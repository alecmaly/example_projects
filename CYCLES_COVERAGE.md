# Cyclic-import coverage matrix

Cyclic imports (A↔B) are an LSP stress pattern — a surprising number of
language servers deadlock, infinite-loop, or silently fail when files
reference each other. Each language has a fixture that exercises its
native cycle-handling pattern.

## Per-language shape

| Lang       | Files                                                                                 | Shape used | Notes |
|------------|---------------------------------------------------------------------------------------|-----------|-------|
| Python     | `monorepo_python/.../cycle_a.py` + `cycle_b.py`                                       | `TYPE_CHECKING` gate for type-only ref; runtime import deferred inside method | Canonical cycle-break; pyright must follow both |
| TypeScript | `monorepo_typescript/.../cycle_a.ts` + `cycle_b.ts`                                   | `import type` for circular type ref; dynamic `await import()` for runtime | ES modules load as partial; this avoids the problem |
| Rust       | `monorepo_rust/.../cycle_a.rs` + `cycle_b.rs`                                         | Mutual types via `Box<T>` indirection | Compile-time checked; one side must box |
| Go         | `monorepo_go/apps/web/cycle_a.go` + `cycle_b.go`                                      | Same-package file-level cycle | Cross-PACKAGE cycles forbidden; same-package is fine |
| Java       | `monorepo_java/.../CycleA.java` + `CycleB.java`                                       | Same-package class-class cycle | JDT handles cleanly |
| C#         | `monorepo_csharp/.../CycleA.cs` (both classes in one file, same namespace)           | Namespace-level cross-reference | OmniSharp handles cleanly |
| Kotlin     | `monorepo_kotlin/.../Cycle.kt`                                                        | Same-package class-class | Kotlin-language-server is the weak link historically |
| Ruby       | `monorepo_ruby/apps/web/cycle_{a,b}.rb`                                               | Lazy `require_relative` inside method body | ruby-lsp needs deferred resolution |
| PHP        | `monorepo_php/.../CycleA.php` + `CycleB.php`                                          | PSR-4 autoload cycle | intelephense handles cleanly |
| Scala      | `scala/cycle.scala`                                                                   | Trait↔trait mutual reference + concrete class backing | Metals handles cleanly |
| Haskell    | `haskell/CycleA.hs`                                                                   | Top-level mutual recursion (one file) | Full cross-module cycle would need `.hs-boot` |
| OCaml      | `ocaml/cycle.ml`                                                                      | `type ... and ...` (mutual types), `let rec ... and` (mutual fns), `module rec ... and` (mutual modules) | All three mutual forms exercised |
| Swift      | `swift/cycle.swift`                                                                   | Class cycle with `weak var owner` to break runtime retain cycle | sourcekit-lsp needs both the strong and weak ref-tracking |
| C          | `c/cycle.c` + `cycle_a.h` + `cycle_b.h`                                               | Forward declaration of `struct` before pointer use | clangd handles cleanly |
| C++        | `cpp/cycle.cpp` + `cycle.hpp`                                                         | Forward decl + `std::shared_ptr`/`weak_ptr` to break ownership cycle | Tests clangd's namespace + template + pointer tracking |
| Lua        | `lua/cycle_{a,b}.lua`                                                                 | `package.loaded` partial-load cycle with lazy `require` in method body | lua-language-server's known weak spot |
| Elixir     | `elixir/cycle.ex`                                                                     | Shared `@behaviour` + cross-module calls (both modules in one file) | Compiler forbids real circular deps between files |
| Zig        | `zig/cycle.zig`                                                                       | Single-file mutual types via `*const Other` pointer | `@import` cycles are a compile error across files |

## Wiring

Each monorepo's entry point now also calls the cycle demo (alongside
the existing feature / scope / imports / casts / advanced / chain
invocations). Look for `// Cycle: A ↔ B.` comments in each
`main`/`Main`/`Program`/`run`.

## Not covered

- `asm/` — cross-TU cycles are expressed through `global`/`extern` which
  was already covered by `imports.asm`. Cyclic reference tracking at
  the ASM level is mostly meaningless for LSPs.
- `bash/`, `powershell/`, `groovy/` — cycles are pathological or rarely
  hit in practice for these. Skipped unless a specific bug needs one.

## What the LSP must demonstrate

For each fixture, the extractor's output should:

1. Resolve references FROM cycle_a TO cycle_b AND vice versa (both
   directions — some LSPs only track one).
2. Produce callstacks that terminate (no infinite recursion through
   `Alpha.spawnBravo → Bravo.bounceToAlpha → Alpha.spawnBravo → …`).
3. Attribute the `Alpha` symbol's definition to its own file even when
   cycle_b references it (no "defined in cycle_b.py" hallucinations).
4. Not deadlock during LSP init while parsing the cyclic files.

Phase 4.3 (tree-sitter fallback indexer) would be the backstop for the
cases where the upstream LSP chokes on cycles.
