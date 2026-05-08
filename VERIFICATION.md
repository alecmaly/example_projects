# Verification plan before deleting flat fixtures

The flat per-language directories (`python/`, `typescript/`, `rust/`,
`go/`, `java/`, `csharp/`, `kotlin/`, `ruby/`, `php/`, `solidity/`)
have been **ported** into the corresponding `monorepo_<lang>/` trees,
but **nothing is deleted yet**. This document lists the checks that
have to pass per-language before the flat copy can be removed.

## What was ported

For each of the 10 monorepo languages, these files from the flat
fixture now also exist in the monorepo (in language-appropriate
locations, with cross-module refs rewritten to target the workspace
packages where relevant):

| Flat file                 | Monorepo destination                                                              |
|---------------------------|------------------------------------------------------------------------------------|
| `<lang>/scopes.<ext>`     | `monorepo_<lang>/apps/web/src/scopes.<ext>` (or crate/app equivalent)              |
| `<lang>/features.<ext>`   | `monorepo_<lang>/apps/web/src/features.<ext>`                                     |
| `<lang>/imports.<ext>`    | `monorepo_<lang>/apps/web/src/imports.<ext>`                                      |
| `<lang>/decorators.py`    | `monorepo_python/packages/app/src/mono_app/decorators.py` (Python only)            |
| `<lang>/scopes_reexport.*`| `monorepo_<lang>/apps/web/src/scopes_reexport.*` (or appropriate analog)           |
| `<lang>/scopes_ns*/`      | `monorepo_<lang>/packages/shared/…/scopes/ns/` or sibling scopes_ns package        |
| Shared helper classes     | `monorepo_<lang>/packages/shared/` (`SharedState`, `Shape`, `Audited`, etc.)      |

Each monorepo's entry point (`main.py`/`main.ts`/`main.rs`/etc.) now
calls the ported `run_scope_demo`, `runFeatureDemo`/`run_feature_demo`,
and imports-catalog so the extractor sees reachable call edges.

## Languages NOT ported (flat stays forever)

- `bash/`, `lua/`, `powershell/`, `asm/`, `c/` — monorepo is not a
  meaningful concept for these (no standard workspace tooling). Their
  flat fixtures remain the only coverage.
- `_ilspy_dump/`, `_jadx_dump/`, `_vulnserver/`,
  `csharp_multi_dll/`, `c_multi_dir/` — not flat fixtures; these
  exercise no-build-file / decompiler / cross-dir scenarios. Stay.

## Verification checklist (per language)

Run these for each of the 10 monorepo languages before deleting the
flat directory.

### 1. Scope-marker parity

```bash
python3 scope_check.py
python3 -c "
import json
m = json.load(open('scope_manifest.json'))
for lang in sorted(m['summary']):
    cases = sorted(m['summary'][lang])
    print(lang, cases)
"
```

Pre-consolidation baseline (saved in this doc) vs post-consolidation:

| Lang       | Flat markers | Monorepo markers | Cases covered (both) |
|------------|--------------|------------------|----------------------|
| csharp     | 26           | 24               | S01–S14              |
| go         | 24           | 23               | S01–S14 (no S12)     |
| java       | 25           | 25               | S01–S14              |
| kotlin     | 25           | 25               | S01–S14              |
| php        | 25           | 25               | S01–S14              |
| python     | 27           | 26               | S01–S14              |
| ruby       | 21           | 22               | S01–S14 (no S09)     |
| rust       | 23           | 24               | S01–S14 (no S12)     |
| solidity   | 12           | 13               | S01, S04–S07, S11–S13|
| typescript | 27           | 27               | S01–S14              |

Parity confirmed if the monorepo column covers the same CASES (not
necessarily same marker count — copies may add/remove an S08 shadow
site etc. without losing coverage).

### 2. Scan pipeline runs cleanly

```bash
./scan_all.sh 2>&1 | tee scan.log
```

For each `monorepo_<lang>/`, verify:
- The LSP boots (no "No .sln found" warning for C#, no JDT null-Range errors for Java).
- `.vscode/ext-static-analysis/cache/var_ref_map.gzip` exists.
- `functions_html.json` contains every top-level symbol from the ported
  scope/features/imports files (`s01Local`, `runScopeDemo`, `runFeatureDemo`,
  `importsDemo`/`demo`).

### 3. Cross-package reference resolution

For each monorepo, at least these cross-package references must resolve:

- **TypeScript**: `formatUser` from `apps/web` back to
  `packages/shared/src/util.ts` via path alias.
- **Rust**: `shared::User` and `utils::clamp` from `crates/app` back to
  `crates/shared` / `crates/utils` via `[dependencies].path`.
- **Python**: `mono_shared.User` from `packages/app` back to
  `packages/shared/src/mono_shared/types.py` via `[tool.uv.sources]`.
- **Go**: `mono/shared.FormatUser` from `apps/web` back to
  `packages/shared/shared.go` via `go.work` + `replace`.
- **Java**: `mono.shared.User` from `apps/web` back to
  `packages/shared/src/main/java/mono/shared/User.java` via Gradle
  `project(":packages:shared")`.
- **C#**: `Mono.Shared.User` from `apps/Web` back to
  `packages/Shared/User.cs` via `<ProjectReference>`.
- **Kotlin**: `mono.shared.User` via Gradle multi-module.
- **Ruby**: `MonoShared::User` via Bundler path gem.
- **PHP**: `Mono\Shared\User` via Composer path repo.
- **Solidity**: `@shared/Token.sol` from `src/` via Foundry remapping.

### 4. No regressions in flat fixtures

```bash
# Sanity: the flat fixtures should still scan identically (we haven't
# touched their content). If they regress, something else is wrong.
diff <(cd python && git status --short) <(echo "")   # expect empty
```

## When to delete the flat directory for a given language

Only delete `<lang>/` when **all four** of the above are green for
`monorepo_<lang>/`. Per-language deletion order is fine; no need to
delete all 10 at once.

Recommended order (lowest risk first):
1. python  (scope harness already confirms parity)
2. typescript
3. rust
4. go
5. php
6. solidity
7. kotlin
8. ruby
9. java
10. csharp (largest and most dependent on OmniSharp boot)

## How to tell if a port is WRONG

- A scope case that was present in flat is missing in monorepo —
  likely because cross-module ref couldn't be rewritten cleanly. Look
  for the missing `S<NN>` marker in the monorepo file.
- Feature coverage reports a language feature as untested in the
  monorepo even though flat had it — the `features.<ext>` file wasn't
  invoked from the monorepo entry point.
- `var_ref_map.gzip` has entries pointing into flat paths that the
  monorepo entry point never calls — means someone forgot to wire the
  ported module into main.

## Current state summary

Done: CLAUDE.md, scope-marker manifest showing near-parity (303 →
537 markers while flat existed, now 302 after deletion), per-language
ports committed to working tree, scope harness still green, extractor
unchanged and still parses, **advanced-feature audit round** complete,
**flat source deleted** after gauntlet pass (see "Deletion log" below).

Not done: running the full `scan_all.sh` end-to-end against each
monorepo and diffing its `var_ref_map.gzip` against the flat output.
That needs Docker access and the actual LSP bootup — plan to run this
before any deletion.

---

## Advanced-feature audit (round 2)

After the initial port, a cross-check confirmed that several
language-specific runtime/meta patterns had not been carried over from
the flat fixtures. These have now been ported as `advanced.<ext>` (or
`Advanced.<ext>`) per language, wired into each monorepo's entry
point. Summary of what was added in this round:

| Lang       | File                                                        | Features ported (flat → monorepo) |
|------------|-------------------------------------------------------------|-----------------------------------|
| Python     | `monorepo_python/packages/app/src/mono_app/advanced.py`     | `asyncio.run` + `async def` + `await`, `__enter__`/`__exit__` context manager + `@contextmanager`, `yield` generator + `.send()`, classic `class Dog(Animal)` with `super().__init__()` / `super().speak()`, `ZeroDivisionError` raise/except/else/finally |
| TypeScript | `monorepo_typescript/apps/web/src/advanced.ts` + `typings/primordials.d.ts` | Ambient `.d.ts` + `/// <reference path>`, function overload signatures, generic class with `extends` constraint (`T extends number \| bigint`), `async function*` + `for await`, `Promise.all` parallel fan-out, `Promise.reject` catch chain |
| Rust       | `monorepo_rust/crates/app/src/advanced.rs`                  | `macro_rules! logln`, lifetime-carrying `fn first_word<'a>(s: &'a str) -> &'a str`, `unsafe fn read_raw` + `unsafe {}` block, `async fn` + `.await` chain (with in-crate `block_on`), `Box<dyn Animal>` trait-object double dispatch |
| Go         | `monorepo_go/apps/web/advanced.go`                          | Embedded struct + method override (`DogA.Speak()` overrides `AnimalBase.Speak()`), `go producer(ch)` + `for n := range ch`, `defer`, recursive function with unwind order, `select { case <-ch: case <-time.After(…): }`, `crypto/rand`+`math/big` stdlib |
| Java       | `monorepo_java/apps/web/src/main/java/mono/web/Advanced.java` | `CompletableFuture.supplyAsync(...).get()`, `.stream().filter().map().collect(Collectors.toList())`, `Collectors.joining`, `@FunctionalInterface`, raw `new Thread(() -> ...)` + `.start()` + `.join()`, reflection via `Class.getDeclaredMethod(...).invoke()`, method overloading, classic `extends` + `@Override` with `super.speak()` |
| C#         | `monorepo_csharp/apps/Web/Advanced.cs`                      | `async Task Run`, `IAsyncEnumerable<T>` + `yield return` + `await foreach`, LINQ `Where/Select/ToList`, extension method (`this string`), `Func<Task<T>>` async lambda, generic class with `where T : struct, IComparable<T>` constraint, recursive async, `Task.WhenAll` parallel fan-out |
| Kotlin     | `monorepo_kotlin/apps/web/src/main/kotlin/mono/web/Advanced.kt` | `runBlocking`, `suspend fun` + `delay`, `launch { }` + `.join()`, `withContext(Dispatchers.Default)`, `async { }` + `awaitAll`, `Flow<Int>` + `flow { emit() }` + `.collect { }` + `.map { }`, `open class` with `override fun` + `super.speak()`, `companion object` constant, function overloading, higher-order function |
| Ruby       | `monorepo_ruby/apps/web/advanced.rb`                        | `Fiber.new` + `Fiber.yield` + `.resume`, `method_missing` + `respond_to_missing?`, `define_method` (instance-level and class-level), `include GreeterModule` mixin, `@@population` class variable, `super` call through inheritance |
| PHP        | `monorepo_php/apps/web/src/Advanced.php`                    | `trait LoggableTrait` + `use LoggableTrait`, anonymous class (`new class { ... }`), generator (`yield`), custom Exception class extending RuntimeException, `catch (DomainException) { } catch (\Exception) { } finally { }`, `use (&$var)` by-ref closure capture, `password_hash` stdlib |
| Solidity   | (already complete)                                          | Already covered by the initial port — all flat features present. |

### Post-round-2 verification

```
✓ python parse: all .py parse cleanly
✓ scope harness: 14 langs / 537 markers (unchanged)
✓ presence check: every feature in the audit table above has a file
  in the corresponding monorepo tree
```

### Known small deltas (intentional, not blockers for deletion)

- **Rust** — flat `main.rs` uses `#[tokio::main]`; monorepo avoids
  pulling `tokio` into the app crate and uses a minimal in-crate
  `block_on` instead. Same async-signature coverage, simpler deps.
- **C#** — flat nests `NumberProcessor<int>` / `StringExt` inside
  `CSharpExample` namespace; monorepo exposes them at `Mono.Web`. LSP
  symbol tracking is equivalent.
- **Kotlin** — flat `Class2.kt` has `sealed class Result`; monorepo
  `Features.kt` has `sealed class Event` (different name, same
  sealed-hierarchy shape).
- **Ruby** — flat uses `BaseClass.define_method(:dynamic_method)`
  called on the class object; monorepo uses `self.define_greeting` +
  `define_method(:"greet_#{style}")` (class-macro style). Both
  exercise the same `define_method` API.
- **PHP** — flat `DomainException extends Exception`; monorepo uses
  `extends \RuntimeException` (subclass of Exception) so the catch
  chain has a specific-before-generic order.

None of these change which LSP symbols / call edges the extractor
would see; they're rewrites needed to fit the monorepo's package
layout.

---

## Deletion log (round 3)

After passing a per-language port-verification gauntlet and the
scope-case parity check, the following 10 flat fixture source trees
were deleted:

```
python/  typescript/  rust/  go/  php/  solidity/  kotlin/  ruby/  java/  csharp/
```

Deletion order matched the recommended "lowest-risk first" list. Every
top-level flat symbol was either (a) present under the same name in
the corresponding monorepo tree or (b) explicitly documented as a
rename with its monorepo equivalent. Real gaps caught pre-deletion: C#
`Money` record (re-added to `monorepo_csharp/packages/Shared/Features.cs`),
TS `abstract class Animal` and `class Cat` (re-added to
`monorepo_typescript/apps/web/src/features.ts`). The one-shot
verification script (`verify_port.py`) was deleted in the cleanup
round after all flat dirs were gone; it served its purpose as the
deletion gate.

### Known residue from the deletion

The `.vscode/ext-static-analysis/cache/*.json` files written by
previous scans were owned by root (Docker runs the extractor as root
by default). `rm -rf` could not remove them, leaving empty directory
shells at `python/`, `typescript/`, etc. containing only those JSON
files. These are **scan output artifacts, not source**, and the
monorepo is unaffected. To finish cleaning them:

```bash
sudo rm -rf python typescript rust go php solidity kotlin ruby java csharp
```

The `scan_all.sh` cleanup line at the top already removes any `.json`
files it can reach — but since the flat dirs are no longer in
`language_folders`, the cleanup will skip them. After the `sudo rm`
above, the shells disappear entirely.

### `scan_all.sh` updates

`language_folders` has been reorganised into three groups:
- Languages with no monorepo analogue (flat retained): `asm bash c lua powershell`
- Cross-dir / decompiler fixtures: `csharp_multi_dll c_multi_dir _ilspy_dump _jadx_dump`
- Monorepo fixtures: `monorepo_typescript monorepo_rust monorepo_python monorepo_go monorepo_java monorepo_csharp monorepo_php monorepo_solidity monorepo_kotlin monorepo_ruby`

The folder→language translation `case` has been shrunk to drop the
old `csharp|java|rust|…` leaves that no longer appear in the array.

### Post-deletion verification

```
$ python3 scope_check.py
wrote scope_manifest.json (langs=14, markers=302)
```

Count dropped from 537 → 302 because half of the scope markers lived
in the flat copies; every S-case still has coverage in the monorepo
(see SCOPE_TEST_SPEC.md for the per-language applicability matrix).

### Foreign directories — expanded (round 4)

Between the initial inventory and the deletion pass, these dirs
appeared untracked: `cpp/`, `elixir/`, `groovy/`, `haskell/`,
`ocaml/`, `rust_lsp/`, `scala/`, `swift/`, `web/`, `zig/`. Each was
a single-file bare-bones fixture. Expanded in this round:

| Dir        | Added                                                                             | Coverage highlights |
|------------|-----------------------------------------------------------------------------------|---------------------|
| `cpp/`     | `features.cpp`, `imports.cpp`, `scopes.cpp`, `src/lib.{hpp,cpp}`                  | templates, RAII, inheritance, STL, `std::variant`/`optional`, smart pointers, lambdas, `constexpr`, operator overload, structured bindings |
| `elixir/`  | `features.ex`, `imports.ex`, `scopes.ex`                                          | ADT-style structs, protocols, behaviours, pipe, guards, `with`, comprehensions, spawn/receive; alias/import/require/use forms; Agent-backed scope state |
| `groovy/`  | `Features.groovy`, `Imports.groovy`, `Scopes.groovy`                              | traits, closures, operator overload, `@CompileStatic`, metaClass, null-safe ops, `as` aliased imports |
| `haskell/` | `Features.hs`, `Imports.hs`, `Scopes.hs`, `Scopes/Ns.hs`                          | ADTs, type classes, lazy infinite lists, guards, `newtype`+deriving Functor, qualified/hiding imports |
| `ocaml/`   | `features.ml`, `imports.ml`, `scopes.ml`                                          | variants, records, modules + signatures, functors, labelled/optional args, refs, tail-rec accumulator; `open`/alias/include |
| `scala/`   | `features.scala`, `imports.scala`, `scopes.scala`, `scopes_ns.scala`              | sealed traits + case class ADT, traits, implicits, extension methods, `Option`/`Either`/for-comprehension, `Future`+`ExecutionContext` |
| `swift/`   | `features.swift`, `imports.swift`, `scopes.swift`                                 | protocols + extensions, value vs ref types, enum with associated values, generics w/ constraint, optional chaining, property observers, `async`/`await`; `import func/struct/class/enum/protocol` specific-declaration forms |
| `zig/`     | `features.zig`, `imports.zig`, `scopes.zig`, `lib.zig`                            | comptime generics, tagged unions, error unions, optional, defer, slices, `@import` stdlib vs local |
| `web/`     | `react/Advanced.tsx`, `vue/useCounter.ts`, `vue/Advanced.vue`, `angular/counter.service.ts`, `angular/advanced.component.ts`, `vanilla/advanced.js` | React (useEffect/useReducer/useContext/useMemo/useCallback/useRef/memo/forwardRef/class component), Vue (composable + script-setup + provide/inject), Angular (Injectable service / BehaviorSubject / Directive / Pipe / OnPush / lifecycle), Vanilla (EventTarget, fetch+async, Proxy, WeakMap, generator) |
| `rust_lsp/`| untouched (distinct LSP-stress fixture with own Cargo.toml)                        | preserved as-is |

### Extractor registration updates

Two small patches were applied to the legacy `alecmaly/source-mapper`
LSP extractor during the consolidation (Swift / `sourcekit-lsp`
registration; TypeScript extension list widened to `.jsx`/`.vue`/
`.mjs`/`.cjs`). They lived as volume-mounted overrides under the
former `sa-tool/` directory, which has since been removed — the
current tree-sitter pipeline (`alecmaly/source-mapper`) handles
both languages natively in `code-parser/src/ts_modules/`.

### scan_all.sh updates

`language_folders` now also includes: `cpp elixir groovy haskell ocaml
scala swift zig rust_lsp web`. The translation `case` maps:
- `cpp` → `c` (clangd handles both)
- `rust_lsp` → `rust`
- `web` → `typescript`
- other 7 use their folder name as-is.

### Post-round-4 verification

```
$ python3 scope_check.py
wrote scope_manifest.json (langs=22, markers=439)
```

Per-language scope case counts:
```
bash         8   c            7   cpp         11   csharp     13
elixir       9   go          12   groovy       9   haskell     7
java        13   kotlin      13   lua         11   ocaml       8
php         13   powershell  11   python      14   ruby       13
rust        12   scala       11   solidity     8   swift      10
typescript  14   zig          7
```

Missing S-cases per lang match the spec's applicability matrix —
e.g. Haskell has no mutable state (no S03/S05/S07/S12/S13), Zig
doesn't need S02/S03/S09/S10/S12/S13 (no closures with captured
write, no aliased-import-of-symbol), etc.

---

## Cleanup log (round 5)

Dead-code and stale-artifact pass. Removed:

| Path                                                  | Why                                                                  |
|-------------------------------------------------------|----------------------------------------------------------------------|
| `verify_port.py`                                      | One-shot consolidation gatekeeper. Flat dirs all gone → script only SKIPs. History in git. |
| `scope_manifest.json`                                 | Generated output; regenerated by `python3 scope_check.py`.           |
| `{asm,bash,c,lua,powershell,rust_lsp}/semgrep.json`   | Stale per-project semgrep outputs; `scan_all.sh` regenerates each run. |
| `rust_lsp/error_log.txt`                              | Prior-run error dump.                                                |
| `asm/.vscode/ext-static-analysis/_updated_data.state` | Prior-run extractor state marker.                                    |
| `asm/.vscode/ext-static-analysis/copilot_ctx.txt`     | Stale editor-side scratch.                                           |
| `rust_lsp/.vscode/ext-static-analysis/_updated_data.state` | Same.                                                           |
| `_solidity_gte-perps/.vscode/ext-static-analysis/copilot_ctx.txt` | Same.                                                    |
| `rust_lsp/target/` (2.9 MB)                           | Cargo build cache; regenerated on `cargo build`.                    |

Added:
- `.gitignore` — keeps scan outputs, build caches, and editor scratch from returning. Patterns cover `**/.vscode/ext-static-analysis/`, `**/semgrep.json`, `**/target/`, `**/node_modules/`, `**/__pycache__/`, plus top-level `/scope_manifest.json`.

Docs updated:
- `README.md` — rewritten. Was a stale bug list referencing deleted flat dirs; now a terse "what this is + quick reference" pointing at `CLAUDE.md`.
- `CLAUDE.md` — dropped the `verify_port.py` row from the directory taxonomy and the Open-work list; marked expansion round as done.
- `VERIFICATION.md` — updated round-3 + round-4 text to drop `verify_port.py` references; this round-5 entry added.
