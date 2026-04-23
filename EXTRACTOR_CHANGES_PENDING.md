# Extractor changes pending review

Phases 2, 4, 5 of the coverage plan all require edits to
`alecmaly/sa-tool`'s extractor (working copy lives at
`/tmp/1_extract_w_lsp.py` — canonical copy is inside the Docker image).
Because (a) the canonical source is inside a 27 GB image, (b) rebuilding
and re-running the image is costly, and (c) the fixture-only Phase 1/3/7
work is independently valuable, these extractor edits are queued here
rather than applied. All line numbers reference `/tmp/1_extract_w_lsp.py`.

---

## Phase 2 — Fix broken variable tracking

The project README lists broken var-ref handling for **Kotlin, Lua,
Ruby, Solidity, Python, PowerShell**. Root causes likely live in two
places:

### 2.1. Hardcoded `VAR_KINDS` — no per-language override (line 2855)
```
VAR_KINDS = {7, 8, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26}
```
Each LSP emits slightly different symbol `kind` values for what we call
"a variable". Pyright, `ruby-lsp`, `lua-language-server`, and
`kotlin-language-server` disagree on whether module-level bindings come
back as `Variable` (13), `Constant` (14), `Field` (8), or `Property` (7).
Centralised set means wrong-kind symbols are silently dropped.

**Change:** make `VAR_KINDS` a per-language dict keyed by the language
string from `-l`, falling back to the existing union. Add a
`--dump-unknown-symbol-kinds` debug flag so we can quickly see which
kinds an LSP is actually emitting per fixture.

### 2.2. `ruby-lsp` LocationLink vs Location mismatch (line ~782)
The existing `if "ruby-lsp" not in self.server_cmd[0]` branch handles
LocationLink for references, but the downstream `var_ref_map` build at
line 2876 still assumes `Location`. Normalise both into a single
`{uri, range}` shape before storing.

### 2.3. Python line-offset quirk (line ~3173)
Comment in source already says "apply +1 offset for vscode, specific
per language server? this change was made for python". This offset
was applied globally but Pyright has since fixed the off-by-one — vet
against a modern Pyright version and scope the offset to an LSP version
check.

### 2.4. Solidity not in `lanaguage_defaults_map` at all (line 3789)
The README says "Solidity: no vars". That's because Solidity is never
registered. Add an entry for `solc` / `solidity-ls` with extension
`.sol`, and register a language-specific `VAR_KINDS` set since Solidity
emits `stateVariable` as a custom kind via some LSP builds.

### 2.5. Read/write classification is a regex heuristic (lines 3646–3660)
Currently tags `(w)` if the var appears left of `=`. This will miss:
- Compound assignments (`+=`, `-=`, `|=`)
- Method-invoked mutators (`set_x(...)`)
- Python `global x; x = ...` inside a function
- Rust `atomic.store(...)` / `atomic.fetch_add(...)`
- C# auto-property setters
- Go shorthand `:=` doesn't *reassign* so should be (w) new binding
  vs (w) reassignment — the heuristic conflates them.

**Change:** replace the regex with a tree-sitter-based lvalue detector
per language. The tree-sitter grammars for asm, typescript, and c_sharp
are already imported (lines 38–41) but only used for OCaml today.

---

## Phase 4 — Cross-directory / multi-project resolution

The new fixtures `csharp_multi_dll/`, `_ilspy_dump/`, `_jadx_dump/`,
`c_multi_dir/` all deliberately violate the "one project, one build
file" assumption that's baked into the extractor at lines 2989–3023.

### 4.1. Single `rootUri` assumption (line 3019)
`LSPClient.analyze(project_dir)` hardcodes one `workspaceFolders` entry.
Change the entry-point to accept a list of roots (all discovered
`*.csproj`, `*.sln`, `go.mod`, `package.json`, `Cargo.toml`,
`pom.xml`, `build.gradle` under the scan root) and pass them as
`workspaceFolders` per LSP spec. OmniSharp supports this natively;
rust-analyzer, gopls, and pyright do too.

### 4.2. C# `.sln` is searched in parent only (line 4093)
```
for candidate in (project_dir, os.path.dirname(project_dir)):
    for f in os.listdir(candidate):
        if f.endswith('.sln'): ...
```
For `csharp_multi_dll/` there is *no* `.sln` at any level — that's the
whole point of the fixture. Add a branch: if no `.sln` is found, glob
for all `*.csproj` files under scan root and build an in-memory
`*.sln`-equivalent list that OmniSharp's `--loglevel=information` can
consume via `--srcdir` or equivalent. Already partially attempted at
4131–4142 where it tries `dotnet restore`; extend rather than rewrite.

### 4.3. Cross-artifact symbol resolution needs a fallback indexer
Even with multi-root workspaces, when the LSP can't boot (no build
file at all — `_ilspy_dump`, `_jadx_dump`) we have no cross-dir symbol
table. Add a tree-sitter-based **fallback indexer** that:
1. Walks every file under the scan root
2. Records fully-qualified symbol names (namespace/package/class path)
3. Performs name-match resolution for cross-artifact references
The existing `seen_function_files` logic at line 2853 is the right
insertion point — add a second "fallback symbol map" consulted when the
primary LSP returns no result.

### 4.4. Per-artifact `searchRoots` config
Add a workspace-level `extra_symbol_search_roots: [...]` knob (read
from `.vscode/ext-static-analysis/settings.json`) so the user can
manually point at sibling artifact directories when auto-discovery
fails. For `_ilspy_dump` this would be `["./CoreLib.dll",
"./Shared.dll"]`.

---

## Phase 5 — Decompiler-specific heuristics

`_vulnserver/` (Ghidra), `_ilspy_dump/` (ILSpy), `_jadx_dump/` (JADX)
all contain synthetic symbols that pollute callstacks and scope
summaries. The extractor currently has **zero** filtering for these
(verified via grep — no references to `FUN_`, `DAT_`,
`<>c__DisplayClass`, or `[CompilerGenerated]` in the script).

### 5.1. Synthetic-symbol classifier
Add a `classify_symbol(name, lang)` helper that returns one of
`{normal, synthetic_lambda, synthetic_backing, synthetic_address,
synthetic_resource}` with per-decompiler regex rules:
- Ghidra: `^(FUN|DAT|LAB|SUB|PTR|UNK)_[0-9a-f]+$`
- ILSpy: `^<>[cf]__`, `<PrivateImplementationDetails>`, `$$method`,
  `<...>b__`, `<...>d__`
- JADX: `^access\$`, `^[a-z]$` (fully-obfuscated class names),
  `\$Lambda\$`, `^R\$`, names containing `$[0-9]+`
Tag these in `functions_html.json` so the VS Code extension can fold
them by default.

### 5.2. No-build-file mode
When a language's required build file is absent, don't give up — boot
a smaller-scope indexer:
- C# without `.csproj`/`.sln`: run `csharp-ls` in single-file mode
  (it tolerates this) — the fallback is already there at 1203–1218
  but only triggers *after* an OmniSharp timeout. Make it proactive
  when no build file is found.
- Java without `pom.xml`/`build.gradle`: `.classpath` stub is already
  created at line 4079. Extend to also create a minimal
  `.project` (Eclipse JDT expects one).
- C without Makefile/CMakeLists: current clangd launch is fine but
  add `-I` auto-discovery (walk up from each `.c` file, add any
  sibling `include` directory).

### 5.3. Ghidra/IDA C detection
`_vulnserver/` includes a `.h` with typedef `undefined`/`undefined4`
patterns. Detect that pattern and turn on:
- Stricter synthetic-symbol filtering
- A "no entry point" badge (Ghidra dumps have no `main()` — the
  callstack builder currently assumes one exists)
- Type resolution that ignores the `undefined*` typedefs entirely.

---

## Proposed execution order

1. Phase 2.1 + 2.2 + 2.4 first — these fix existing bugs without new
   features and unblock the "broken vars" entries in the README.
2. Phase 4.1 + 4.2 — make multi-root workspaces real. Test with
   `csharp_multi_dll/`.
3. Phase 4.3 fallback indexer — unblocks `_ilspy_dump` and
   `_jadx_dump` which can never boot an LSP cleanly.
4. Phase 5.1 synthetic-symbol classifier — pure cosmetic but makes the
   decompiler fixtures actually usable.
5. Phase 5.2 no-build-file mode + Phase 5.3 Ghidra detection.
6. Phase 2.5 tree-sitter lvalue detection last — biggest design
   change, easiest to defer.

Each of the above should ship as its own change to `alecmaly/sa-tool`
with a regression run of all fixtures before and after, diffing
`functions_html.json` / `var_ref_map.gzip` / `callstacks.json`.
