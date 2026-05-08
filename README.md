# example_projects

Fixture testbed for static-analysis extractors. Every directory here is
a target the extractor scans. **This is not a buildable product** —
fixtures are written so real language servers can parse and return
semantic info, but the code is never executed in production.

The current production extractor is the tree-sitter pipeline in
[`alecmaly/static-analysis-tooling`](https://github.com/alecmaly/static-analysis-tooling)
(`alecmaly/source-mapper` Docker image). The legacy LSP-based extractor
(`alecmaly/source-mapper` image) can still be run via `scan_all.sh` for diff'ing.

For the project goal, pipeline shape, directory taxonomy, marker
conventions, and debug flags, see **[CLAUDE.md](./CLAUDE.md)**.

## Quick reference

| What                           | Where                                                          |
|--------------------------------|----------------------------------------------------------------|
| Run tree-sitter pipeline       | `docker run --rm -v "$PWD:$PWD" alecmaly/source-mapper scan "$PWD"` (per fixture dir) |
| Run legacy LSP pipeline        | `./scan_all.sh`                                                |
| Dump LSP-reported symbol kinds | `SA_DUMP_UNKNOWN_KINDS=1 ./scan_all.sh`                        |
| Regenerate scope manifest      | `python3 scope_check.py`                                       |
| Full scope spec                | [SCOPE_TEST_SPEC.md](./SCOPE_TEST_SPEC.md)                     |
| Full imports coverage matrix   | [IMPORTS_COVERAGE.md](./IMPORTS_COVERAGE.md)                   |
| Consolidation audit log        | [VERIFICATION.md](./VERIFICATION.md)                           |

## Fixture inventory

- **Flat single-dir fixtures** (kept as flat — monorepo tooling doesn't
  apply): `asm/`, `bash/`, `c/`, `cpp/`, `elixir/`, `groovy/`,
  `haskell/`, `lua/`, `ocaml/`, `powershell/`, `scala/`, `swift/`,
  `zig/`
- **Monorepo fixtures** (replaced former flat dirs for these 10 langs
  during consolidation): `monorepo_csharp/`, `monorepo_go/`,
  `monorepo_java/`, `monorepo_kotlin/`, `monorepo_php/`,
  `monorepo_python/`, `monorepo_ruby/`, `monorepo_rust/`,
  `monorepo_solidity/`, `monorepo_typescript/`
- **Frontend frameworks**: `web/{vanilla,react,vue,angular}/`
- **LSP-stress fixture**: `rust_lsp/` (minimal single-crate shape)
- **Cross-dir / no-build-file**: `csharp_multi_dll/`, `c_multi_dir/`
- **Decompiler outputs**: `_ilspy_dump/`, `_jadx_dump/`, `_vulnserver/`
- **External audit references**: `_solidity-chainlink/`, `_solidity_gte-perps/`
- **Infrastructure**: `sg-rules/` (opt-in Semgrep rules),
  `scope_check.py` (scope harness), `scan_all.sh` (legacy LSP-pipeline
  driver)

## Known LSP flags per language

Historical issues — still valid flags the extractor accepts:

| Language   | Flag                           | Reason                                                      |
|------------|--------------------------------|-------------------------------------------------------------|
| Python     | `--force-callHierarchy`        | Pyright's callHierarchy occasionally unreliable            |
| Rust       | `--disable-outgoing-calls`     | rust-analyzer outgoing calls can spin                      |
| Java       | `--disable-selectionRange`     | JDT returns inconsistent selectionRange for lambdas        |
| ASM        | may need `git init` first      | `asm-lsp` requires a git dir at the project root           |

Var-tracking issues seen in the legacy LSP layout for Kotlin, Lua,
Ruby, Solidity, Python, PowerShell were addressed via patches to the
`alecmaly/source-mapper` extractor. The current tree-sitter pipeline
(`alecmaly/source-mapper`) handles them natively in its per-language
modules under `code-parser/src/ts_modules/`.
