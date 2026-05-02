# Imports, exports, and build-configuration coverage

Two complementary layers:

1. **`imports.<ext>` reference files** — per-language catalog of every
   native import/export shape. One file per language, exhaustive inline.
2. **`monorepo_<lang>/` fixture trees** — real multi-package shapes
   that exercise cross-package imports, workspace/build-tool configs,
   and the path-resolution layer the language's LSP depends on.

## Per-language reference (`imports.<ext>`)

| Language   | File                              | Forms covered (inline comment-numbered) |
|------------|-----------------------------------|-----------------------------------------|
| Python     | `python/imports.py`               | whole-module / submodule / aliased / from-import (single, multi, aliased, star) / relative / conditional / `importlib.import_module` / `TYPE_CHECKING`-gated / implicit export / `_private` / `__all__` |
| TypeScript | `typescript/imports.ts`           | named / aliased / namespace `* as` / default / default+named / `import type` / inline type modifier / side-effect / dynamic `import(...)` / triple-slash reference / named export / export list / renamed export / default export / barrel re-export / namespace re-export / wildcard re-export |
| Rust       | `rust/src/imports.rs`             | plain `use` / braced list / renamed / glob / `self` + braced / `super` / `crate::` absolute / `pub use` re-export / `extern crate` (legacy) / inline `mod` / `#[path = "..."]` / `#[cfg(...)]`-gated |
| Go         | `go/imports.go`                   | stdlib plain / grouped / aliased (rename) / blank `_` / dot `.` (shape-only) / intra-project |
| Java       | `java/Imports.java`               | single-type / wildcard / fully-qualified / static member / static wildcard / nested-type |
| C#         | `csharp/Imports.cs`               | `using Ns` / `using static` / namespace alias / type alias / `global using` (cross-file) |
| Kotlin     | `kotlin/Imports.kt`               | single / wildcard / aliased / top-level function / aliased object member |
| Ruby       | `ruby/imports.rb`                 | `require` / `require_relative` / `load` (shape) / `autoload` / Bundler (shape) / constant access |
| PHP        | `php/imports.php`                 | `require_once` / `use Class` / `use Class as Alias` / grouped `use X\{A,B}` / `use function` / `use const` / `require` |
| Solidity   | `solidity/Imports.sol`            | plain file import / named / aliased named / module-level alias `as M` / wildcard `import * as` |
| C          | `c/imports.c`                     | `#include <sys>` / `#include "local"` / `#include_next` (shape) / conditional include / macro-defined include / `extern` symbol |
| Lua        | `lua/imports.lua`                 | `require` / aliased local / dotted path (shape) / `package.loaded` / `dofile`/`loadfile` (shape) / `_G` globals |
| Bash       | `bash/imports.sh`                 | `source` / `.` / PATH-relative (shape) / `export` to env |
| PowerShell | `powershell/Imports.ps1`          | `.` dot-source / `Import-Module` (shape) / `-Prefix` (shape) / `using module` (shape) / `using namespace` / `$env:` |
| ASM        | `asm/imports.asm`                 | `extern` / `global` / `%include` (shape) / `%import` (shape) |

## Monorepo fixtures (`monorepo_<lang>/`)

Each is a self-contained mini-monorepo — apps + shared packages + a
real workspace/build config. Designed to make the LSP and the scan
pipeline resolve cross-package imports the way they'd have to in a
production codebase.

| Fixture                 | Workspace config                  | Packages                                                                   | Cross-package imports exercised |
|-------------------------|-----------------------------------|----------------------------------------------------------------------------|----------------------------------|
| `monorepo_typescript/`  | `pnpm-workspace.yaml` + root `package.json` workspaces + `tsconfig.base.json` paths | `apps/web`, `apps/cli`, `packages/shared`, `packages/utils` | named, default, type-only, namespace, aliased, subpath, side-effect, dynamic, barrel/namespace/wildcard re-export |
| `monorepo_rust/`        | Cargo workspace (`members = [...]`, `workspace.package`) | `crates/app` (bin), `crates/shared` (lib), `crates/utils` (lib) | path deps, `pub use` re-exports, crate-level + glob + aliased `use`, inline `mod` |
| `monorepo_python/`      | Root `pyproject.toml` (`tool.uv.workspace`) + per-pkg `pyproject.toml` with hatchling + `tool.uv.sources` path-deps | `packages/app` (with `mono_app.main` + `mono_app.helper`), `packages/shared` (with barrel `__init__.py`, `__all__`), `packages/utils` | whole module / submodule / aliased / from-import (single, aliased, star) / relative (`from . import`) / dataclass + Enum re-export |
| `monorepo_go/`          | `go.work` multi-module + per-module `go.mod` with `replace` directives | `apps/web`, `apps/cli`, `packages/shared`, `packages/utils` | named, aliased, blank (`_`) side-effect, dot (`.`) import, `init()` execution |
| `monorepo_java/`        | `settings.gradle.kts` with `include(":apps:web", ...)` + per-module `build.gradle.kts` with `project(":packages:shared")` deps | `apps/web`, `apps/cli`, `packages/shared`, `packages/utils` | class import, wildcard, static member, static wildcard |
| `monorepo_csharp/`      | Real `Mono.sln` + per-project `.csproj` with `<ProjectReference>` | `apps/Web`, `apps/Cli`, `packages/Shared`, `packages/Utils` | `using Ns` / `using static` / namespace alias / `global using` (via `GlobalUsings.cs`) |
| `monorepo_php/`         | Root `composer.json` with `path` repositories + per-package `composer.json` with PSR-4 `autoload` + `files` autoload for functions | `apps/web`, `apps/cli`, `packages/shared`, `packages/utils` | `use Class` / `as` / grouped `use X\{A, B as C}` / `use function` / `use const` |
| `monorepo_solidity/`    | `foundry.toml` with `remappings` + `remappings.txt` | `src/App.sol`, `src/Helper.sol`, `lib/shared/src/Token.sol`, `lib/shared/src/IERC20Like.sol`, `lib/utils/src/Math.sol` | remapped `@shared/...` / `@utils/...` / named / aliased / module-level alias / relative-path sibling import |
| `monorepo_kotlin/`      | `settings.gradle.kts` with `include(...)` + per-module `build.gradle.kts` with `project(...)` deps | `apps/web`, `apps/cli`, `packages/shared`, `packages/utils` | class / wildcard / object-member / extension function / aliased import |
| `monorepo_ruby/`        | Root `Gemfile` with `gem ..., path: "packages/.."` + per-package `.gemspec` | `apps/web`, `packages/shared`, `packages/utils` | `require` via Bundler path-deps / `require_relative` / `autoload` / `include ModuleName` |

## How to exercise the coverage

1. **Scope check + imports audit** — run the existing
   `scope_check.py` (it already walks the repo and produces
   `scope_manifest.json`). Once the extractor's tree-sitter/regex
   fallback indexer lands (Phase 4.3), each monorepo fixture will
   produce cross-package `var_ref_map` entries that can be diffed
   against the spec.
2. **Per-language rescan** — `scan_all.sh` will now scan each
   `monorepo_*/` tree with the right LSP (added below). For
   typescript / rust / go / python / java / kotlin / csharp / php /
   solidity the fixtures have build files the LSP can boot from; for
   ruby the Gemfile path-deps are enough for ruby-lsp.
3. **Languages without a monorepo fixture** (bash, lua, powershell,
   asm, c) rely on their `imports.<ext>` reference file alone — none
   of them have a build-tool-driven monorepo story worth modeling.

## What's NOT covered (and why)

- **pnpm / yarn actual install state** — no `node_modules/`, no
  `pnpm-lock.yaml`, no `yarn.lock`. The LSPs don't need these for
  `workspace:*` resolution once `paths` is configured.
- **Nx / Turborepo / Lerna** — adjacent tooling to pnpm workspaces.
  Adding either would mostly exercise *task-graph* config, not import
  resolution. Leave for later if the LSP pipeline ever needs it.
- **Bazel / Buck2** — build-tool monorepos. Static analyzers rarely
  interact with them directly; deferred.
- **`go.work` + private module proxy** — skipping `GOPRIVATE`.
- **Maven multi-module** — we did Gradle; Maven has the same shape
  with `pom.xml` + `<modules>`. Easy follow-up if anyone hits it.

---

## Transitive re-export chains (T1)

Each language now carries a 3-level transitive chain so the extractor
must follow `consumer → chain_deep → chain_middle → chain_origin` to
resolve a symbol back to its definition. Markers:
`T1.origin.def`, `T1.middle.reexport`, `T1.deep.reexport`,
`T1.consumer.read`.

| Lang       | Chain files (3 levels)                                                                 | Re-export shape per hop |
|------------|----------------------------------------------------------------------------------------|--------------------------|
| Python     | `monorepo_python/.../chain_{origin,middle,deep}.py`                                    | `from X import Y` + `__all__`; aliased on final hop |
| TypeScript | `monorepo_typescript/apps/web/src/chain_{origin,middle,deep}.ts`                       | `export *` wildcard + `export { X as Y }` named+aliased |
| Rust       | `monorepo_rust/crates/shared/src/lib.rs` (`mod chain_{origin,middle,deep}`)            | `pub use super::x::*` wildcard + `pub use … as Y` aliased |
| Go         | `monorepo_go/packages/chain_{origin,middle,deep}/*.go`                                 | Separate modules with `replace` directives; each re-exposes prior as own const |
| Java       | `monorepo_java/packages/shared/src/main/java/mono/chain/{Origin,Middle,Deep}.java`     | `public static final` constants chained (Java has no native re-export) |
| C#         | `monorepo_csharp/packages/Shared/Chain.cs`                                             | Three `static class` constants chaining |
| Kotlin     | `monorepo_kotlin/.../mono/shared/chain/Chain.kt`                                       | Three `object` constants chained + a `typealias` for bonus coverage |
| Ruby       | `monorepo_ruby/apps/web/chain_{origin,middle,deep}.rb`                                 | `require_relative` + module constants chained |
| PHP        | `monorepo_php/packages/shared/src/Chain/{Origin,Middle,Deep}.php`                      | `class` constants with `::` chain (`Deep::VALUE_ALIAS = Middle::MIDDLE_VALUE`) |
| Solidity   | `monorepo_solidity/src/chain/{Origin,Middle,Deep}.sol` + `ChainConsumer.sol`           | Three libraries in a named-import chain |
| Scala      | `scala/chain.scala`                                                                    | Three `object` constants chained |
| Haskell    | `haskell/Chain/{Origin,Middle,Deep}.hs`                                                | `import qualified` + explicit `module X (..)` exports |
| OCaml      | `ocaml/chain.ml`                                                                       | Three nested modules, each exposing a `let` referencing the previous |
| Elixir     | `elixir/chain.ex`                                                                      | `defdelegate` + `defdelegate ..., as:` on final hop |
| Zig        | `zig/chain_{origin,middle,deep}.zig` + `chain.zig` consumer                            | Per-file `@import` + `pub const X = …` chain |
| Lua        | `lua/chain_{origin,middle,deep}.lua`                                                   | Module-return-table pattern; each level `require`s the previous |
| Bash       | `bash/chain_{origin,middle,deep}.sh`                                                   | `source` chaining; each level copies the previous level's var |
| PowerShell | `powershell/Chain{Origin,Middle,Deep}.ps1`                                             | Dot-source `. .\X.ps1` chain; `$script:` scope propagation |
| Groovy     | `groovy/Chain.groovy`                                                                  | Three static classes chained |
| C / C++    | — (already covered by `#include` chains in `imports.c`/`imports.cpp`)                  | — |
| ASM        | — (linker-level `global`/`extern`; no symbol re-export)                                | — |

### What the extractor should demonstrate

For each chain above, the LSP's reference map should produce the same
`target` for:
- The `T1.origin.def` line (where `ORIGIN_VALUE` is defined).
- The `T1.consumer.read` line (where the consumer reads `VALUE_ALIAS`).

If the extractor stops at the first import and doesn't follow re-exports,
the consumer read will resolve to `chain_deep` rather than `chain_origin`.
Extractor Phase 4.3 (tree-sitter fallback indexer) is the planned fix
for the cases where the LSP itself doesn't chain through.
