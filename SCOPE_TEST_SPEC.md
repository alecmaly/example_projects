# Scope test spec

The existing fixtures exercise cross-module reads and writes, but there's no
labeled matrix that lets you diff the extractor's `var_ref_map.gzip` against
an expected result per scope situation. This spec defines 14 canonical scope
cases that every language fixture should exercise (where the language
supports them), with inline labels so the extractor output is mechanically
verifiable.

## Labeling convention

Every scope test case lives in a file named `scopes.<ext>`. Each case is
tagged with a short marker comment at the definition, each reference, and
each mutation. The marker format is language-idiomatic but always contains
the case ID:

```
# S02.outer.def       — the canonical definition
# S02.inner.read      — an expected reference (read)
# S02.inner.write     — an expected reference (write)
# S02.shadow.def      — a competing definition that should NOT be bound to S02
```

Use the language's native comment prefix (`//`, `#`, `--`, `;`, `<!-- -->`).
The extractor output can be regex-scanned for these markers, and the
`var_ref_map` entry at each marker location can be checked against the
spec's expectation.

## The 14 canonical cases

| ID  | Name                            | Definition site                           | Expected references                                    |
|-----|---------------------------------|-------------------------------------------|--------------------------------------------------------|
| S01 | Local var                       | function body                             | reads/writes only within that function                 |
| S02 | Closure — read                  | outer-fn body                             | inner-fn reads bind to outer-fn def                    |
| S03 | Closure — write                 | outer-fn body                             | inner-fn writes bind to outer-fn def (requires nonlocal / use & / &mut) |
| S04 | Module var — same-module read   | module scope                              | every same-module reader resolves to it                |
| S05 | Module var — same-module write  | module scope                              | every same-module writer resolves to it + classified W |
| S06 | Module var — cross-module read  | module A                                  | module B's qualified read resolves to A's def          |
| S07 | Module var — cross-module write | module A                                  | module B's qualified write resolves to A's def + W     |
| S08 | Shadowing                       | outer scope (def A) + inner scope (def B) | inner refs must bind to B, not A                       |
| S09 | Aliased import                  | module A's def                            | importer's alias must resolve back to A's def          |
| S10 | Re-export chain                 | module A's def                            | consumer reads `C.v` → resolves through B's re-export to A |
| S11 | Instance field vs local param   | class with field `x`, method param `x`    | method body's `x` is param; `self.x`/`this.x` is field |
| S12 | Static/class field vs instance  | class with static `s` + instance `i`      | class-qualified reads resolve to static, `self.i` to instance |
| S13 | Inherited field through derived | base class field                          | derived's read via `super`/embed/mixin resolves to base |
| S14 | Namespace-qualified class ref   | class `A.B.Widget`                        | `A.B.Widget(...)` from elsewhere must bind to the class def |

Cases that a given language cannot express (e.g. ASM has no closures,
Solidity has no closures, Lua has no aliased-import syntax) are marked
`N/A` in the fixture's header comment so the diff tooling knows to skip
them.

## Per-language applicability matrix

| Case | Py | Java | C# | Kt | TS | Go | Rs | Rb | PHP | Sol | C | Lua | Bash | PS |
|------|----|------|----|----|----|----|----|----|-----|-----|---|-----|------|----|
| S01  |  Y |   Y  |  Y |  Y |  Y |  Y |  Y |  Y |  Y  |  Y  | Y |  Y  |  Y   |  Y |
| S02  |  Y |   Y  |  Y |  Y |  Y |  Y |  Y |  Y |  Y  |  -  | - |  Y  |  Y   |  Y |
| S03  |  Y |(effectively final) | Y | Y | Y | Y | Y(mut move) | Y | Y(&) | - | - | Y | Y | Y |
| S04  |  Y |   Y  |  Y |  Y |  Y |  Y |  Y |  Y |  Y  |  Y  | Y |  Y  |  Y   |  Y |
| S05  |  Y |   Y  |  Y |  Y |  Y |  Y |  Y |  Y |  Y  |  Y  | Y |  Y  |  Y   |  Y |
| S06  |  Y |   Y  |  Y |  Y |  Y |  Y |  Y |  Y |  Y  |  Y  | Y |  Y  |  Y   |  Y |
| S07  |  Y |   Y  |  Y |  Y |  Y |  Y |Y(atomic)| Y | Y |  Y  | Y |  Y  |  Y   |  Y |
| S08  |  Y |   Y  |  Y |  Y |  Y |  Y |  Y |  Y |  Y  |  -  | Y |  Y  |  Y   |  Y |
| S09  |  Y | (static import) | using alias | Y | Y | Y(pkg alias) | Y(use as) | - | Y(use as) | - | - | - | - | - |
| S10  |  Y |   -  |  Y |  Y |  Y |  - |  Y |  - |  -  |  -  | - |  Y  |  -   |  - |
| S11  |  Y |   Y  |  Y |  Y |  Y |  Y |  Y |  Y |  Y  |  Y  | Y |  Y  |  -   |  Y |
| S12  |  Y |   Y  |  Y |  Y |  Y |  - |  Y |  Y |  Y  |  Y  | - |  -  |  -   |  Y |
| S13  |  Y |   Y  |  Y |  Y |  Y | Y(embed) | Y(trait default) | Y | Y | Y(inherit) | - | Y(meta) | - |  Y |
| S14  |  Y |   Y  |  Y |  Y |  Y |  Y |  Y |  Y |  Y  |  -  | - |  Y  |  -   |  Y |

## Expected extractor behavior

For each marker pair:
1. **Definition-site markers** (`*.def`) should appear exactly once in
   `functions_html.json` / class inheritance output at the labeled line.
2. **Reference markers** (`*.read`, `*.write`) should each produce one
   entry in `var_ref_map` whose `target` is the corresponding `*.def`
   location.
3. The **kind** of each reference (read vs write) should match the
   marker suffix. Today the extractor's read/write heuristic is
   regex-based — some of these cases will likely fail until Phase 2.5
   lands.
4. **Shadowing (S08)** and **aliased import (S09)** are the most
   common regression sites. The `*.shadow.def` marker must NOT appear
   in the refs list of the outer definition.
5. **Re-export (S10)** requires the extractor to follow imports
   transitively — this is usually broken when the intermediate module
   does `from a import v` without re-exporting via `__all__` or
   explicit `export { v }`.

## How to run the spec (future — Phase 2 extractor work)

A companion runner `scope_check.py` (not yet written) walks every
`scopes.*` file, extracts `*.def` / `*.read` / `*.write` markers via
regex, and compares against `.vscode/ext-static-analysis/cache/var_ref_map.gzip`
for each language. The runner emits a pass/fail grid per language per
case. Until it exists, this spec is the contract.
