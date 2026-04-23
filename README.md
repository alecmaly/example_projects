# example_projects

Fixture testbed for the `alecmaly/sa-tool` static-analysis / LSP pipeline.
Every directory here is a target the extractor scans. **This is not a
buildable product** — fixtures are written so real language servers can
parse and return semantic info, but the code is never executed in
production.

For the project goal, pipeline shape, directory taxonomy, marker
conventions, and override flags, see **[CLAUDE.md](./CLAUDE.md)**.

## Quick reference

| What                           | Where                                                          |
|--------------------------------|----------------------------------------------------------------|
| Run everything                 | `./scan_all.sh`                                                |
| Bypass local extractor patches | `SA_TOOL_OVERRIDE=0 ./scan_all.sh`                             |
| Dump LSP-reported symbol kinds | `SA_DUMP_UNKNOWN_KINDS=1 ./scan_all.sh` (debugs Phase 2.1)     |
| Regenerate scope manifest      | `python3 scope_check.py`                                       |
| Full scope spec                | [SCOPE_TEST_SPEC.md](./SCOPE_TEST_SPEC.md)                     |
| Full imports coverage matrix   | [IMPORTS_COVERAGE.md](./IMPORTS_COVERAGE.md)                   |
| Applied extractor patches      | [EXTRACTOR_CHANGES_APPLIED.md](./EXTRACTOR_CHANGES_APPLIED.md) |
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
- **Infrastructure**: `sa-tool/` (volume-mounted extractor patches),
  `sg-rules/` (opt-in Semgrep rules), `scope_check.py` (scope harness),
  `scan_all.sh` (entry point)

## Known LSP flags per language

Historical issues — still valid flags the extractor accepts:

| Language   | Flag                           | Reason                                                      |
|------------|--------------------------------|-------------------------------------------------------------|
| Python     | `--force-callHierarchy`        | Pyright's callHierarchy occasionally unreliable            |
| Rust       | `--disable-outgoing-calls`     | rust-analyzer outgoing calls can spin                      |
| Java       | `--disable-selectionRange`     | JDT returns inconsistent selectionRange for lambdas        |
| ASM        | may need `git init` first      | `asm-lsp` requires a git dir at the project root           |

Var-tracking issues (broken in the old flat layout for Kotlin, Lua,
Ruby, Solidity, Python, PowerShell) are addressed by
**PATCH P2.1** (per-language `VAR_KINDS`) and **PATCH P2.2**
(unconditional `LocationLink` normalisation). See
[EXTRACTOR_CHANGES_APPLIED.md](./EXTRACTOR_CHANGES_APPLIED.md) for the
full list of applied patches and how to roll them back.
