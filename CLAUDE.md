# CLAUDE.md — project goal and working notes

## What this repo is

A fixture testbed for static-analysis extractors. Every directory under
this repo is a target the extractor scans; the outputs live under
`.vscode/ext-static-analysis/` per project and drive a VS Code extension
that renders call graphs, variable references, scope summaries, and
detector hits.

The current production extractor is the tree-sitter pipeline in the
[`alecmaly/static-analysis-tooling`](https://github.com/alecmaly/static-analysis-tooling)
repo (run with `docker run --rm -v "$PWD:$PWD" alecmaly/source-mapper
scan "$PWD"`). The retired LSP-based predecessor (`alecmaly/sa-tool`
image) can still be run via `scan_all.sh` for users who want a side-by-
side diff.

**This is not a buildable product.** Fixtures are written so that real
language servers can parse and return semantic info, but the code is
never executed in production. Syntactic correctness and shape coverage
matter more than runtime correctness.

## The pipeline (legacy LSP path — `scan_all.sh`)

For each folder in `language_folders`:

1. **Extraction** — `docker run alecmaly/sa-tool python3 /app/1_extract_w_lsp.py -d <dir> -l <lang>`
   Boots the language's LSP, fetches document symbols, references, and
   call hierarchies. Output: `*/var_ref_map.gzip`, `function_calls.json`,
   `seen_files.json`, `class_inheritance.json`.
2. **Callstack build** — `2_build_callstacks.py` stitches references
   into callstacks and scope summaries. Output: `callstacks.json`,
   `scope_summaries_html.json`, `functions_html.json`,
   `decorations.json`, `inheritance_graph.json`.
3. **Detectors** — `semgrep scan` → `semgrep-to-detector-results.py`,
   `grep-to-detector-results.py` for if / loop detectors. Output:
   `detector-results.json` under `.vscode/ext-detectors/`.

`scan_all.sh` ends with `code .` per project so VS Code re-opens
against fresh outputs.

For the **current** tree-sitter pipeline, use `alecmaly/source-mapper`
directly — it scans the same fixture dirs and emits the same
`functions_html.json`/`function_calls.json` schema (plus
`var_ref_map.json` instead of `.gzip`).

## Directory taxonomy

| Path                           | Purpose                                                                                    |
|--------------------------------|---------------------------------------------------------------------------------------------|
| `asm/`, `bash/`, `c/`, `lua/`, `powershell/` | Flat per-language fixtures — **retained**; monorepo tooling doesn't fit these languages. |
| `cpp/`, `elixir/`, `groovy/`, `haskell/`, `ocaml/`, `scala/`, `swift/`, `zig/` | Single-dir fixtures for the extractor's secondary-LSP languages. Each covers features / imports / scopes (where the feature applies).  |
| `rust_lsp/`                    | Rust LSP-stress fixture with its own `Cargo.toml` — distinct from `monorepo_rust/`; exercises the LSP boot / ref-map path on a minimal single-crate shape.  |
| `web/`                         | Frontend framework coverage: `vanilla/`, `react/`, `vue/`, `angular/`. Counter-style sample + advanced (hooks/class components, composables, services/pipes/directives, EventTarget/fetch/async).  |
| `monorepo_<lang>/`             | Multi-package workspace with real build config + cross-package imports. Covers: typescript, rust, python, go, java, csharp, php, solidity, kotlin, ruby. **Replaced the old flat per-language dirs** after parity audit — see `VERIFICATION.md`. |
| `csharp_multi_dll/`            | 3 C# dirs (A/B/C) with **no** shared `.sln`/`.csproj` — cross-dir resolution                |
| `_ilspy_dump/`, `_jadx_dump/`, `_vulnserver/` | Decompiler output fixtures (ILSpy, JADX, Ghidra). No build files; synthetic-symbol-heavy   |
| `c_multi_dir/`                 | C fixture split across `lib/include`, `lib/src`, `app/` with no Makefile                    |
| `sg-rules/`                    | Opt-in custom Semgrep rules (toggle via `--config ../sg-rules` in scan_all.sh)              |
| `scope_check.py`               | Walks every `scopes.*` file, extracts S01–S14 markers, emits `scope_manifest.json`.         |

## Key docs

- `README.md` — terse list of known broken behaviors per language
- `SCOPE_TEST_SPEC.md` — 14 canonical scope test cases (S01..S14) with per-language applicability matrix
- `IMPORTS_COVERAGE.md` — matrix of import/export/build-config forms per language
- `VERIFICATION.md` — how to verify per-language parity before deleting flat fixtures

## Conventions

### Marker convention for scope fixtures
Each canonical scope case is labeled inline:
- `S<NN>.def` / `S<NN>.<role>.def` — definition site
- `S<NN>.read` / `S<NN>.<role>.read` — reference read
- `S<NN>.write` / `S<NN>.<role>.write` — reference write
- `S<NN>.shadow.def` — competing definition that must NOT bind to the outer def

`scope_check.py` regex-extracts these markers and produces
`scope_manifest.json`. Use `--diff` to compare against the extractor's
`var_ref_map.gzip`.

### LSP debug flag
- `SA_DUMP_UNKNOWN_KINDS=1` — per-file dump of every LSP symbol kind encountered (debug aid for the legacy `alecmaly/sa-tool` extractor's `VAR_KINDS` mapping)

## What NOT to do

- **Do not re-introduce flat `<lang>/` fixtures for languages that have monorepos** — the consolidation pass moved all coverage into `monorepo_<lang>/`. Adding content back to the flat layout for the 10 consolidated languages would split coverage again. (The 5 flat fixtures that remain — asm/bash/c/lua/powershell — are intentional because monorepo tooling doesn't fit those languages.)
- **Do not commit `*.json` scan outputs under `.vscode/ext-static-analysis/cache/`.** They are regenerated on every scan and bloat diffs.
- **Do not bypass hooks / skip signing** when committing.
- **Do not modify `_vulnserver/*.json` or `_solidity-chainlink/*` or `_solidity_gte-perps/*`** — they are excluded from the cleanup step of `scan_all.sh` on purpose.

## Open work

- **Monorepo consolidation** — completed. Flat `<lang>/` dirs fully removed for the 10 consolidated languages (python, typescript, rust, go, java, csharp, php, solidity, kotlin, ruby).
- **Expansion round** — completed. `cpp/`, `elixir/`, `groovy/`, `haskell/`, `ocaml/`, `scala/`, `swift/`, `zig/`, `web/`, `rust_lsp/` now carry features / imports / scopes coverage (see `VERIFICATION.md` round 4).
- Maven multi-module fixture (Gradle already covered).
