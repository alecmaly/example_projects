# Extractor changes — applied

This complements `EXTRACTOR_CHANGES_PENDING.md`. Patches are applied to a
working copy of the sa-tool scripts that now lives at
`example_projects/sa-tool/`. The copy is volume-mounted *over* the
`alecmaly/sa-tool` Docker image at scan time, so the original 27 GB image
does **not** need to be rebuilt.

## How the override works

`scan_all.sh` now includes:

```bash
SA_TOOL_OVERRIDE="${SA_TOOL_OVERRIDE:-1}"
OVERRIDE_MOUNTS=""
if [ "$SA_TOOL_OVERRIDE" = "1" ] && [ -f "${BASE_DIR}sa-tool/1_extract_w_lsp.py" ]; then
    ...
    OVERRIDE_MOUNTS="$OVERRIDE_MOUNTS -v ${BASE_DIR}sa-tool/$f:/app/$f:ro"
    ...
fi
```

Each `docker run` invocation for steps 1 and 2 of the pipeline now appends
`$OVERRIDE_MOUNTS`, which read-only-mounts:

- `sa-tool/1_extract_w_lsp.py` → `/app/1_extract_w_lsp.py`
- `sa-tool/0_detect_project_roots.py` → `/app/0_detect_project_roots.py`
- `sa-tool/2_build_callstacks.py` → `/app/2_build_callstacks.py`
- `sa-tool/modules/` → `/app/modules/`

To roll back to the image's baked-in extractor:
```bash
SA_TOOL_OVERRIDE=0 ./scan_all.sh
```

To re-sync the working copy with a new upstream image:
```bash
CID=$(docker create alecmaly/sa-tool:latest)
docker cp $CID:/app/1_extract_w_lsp.py         sa-tool/1_extract_w_lsp.py
docker cp $CID:/app/0_detect_project_roots.py  sa-tool/0_detect_project_roots.py
docker cp $CID:/app/2_build_callstacks.py      sa-tool/2_build_callstacks.py
docker cp $CID:/app/modules                    sa-tool/
docker rm $CID
# then re-apply your patches; each one is tagged "PATCH P<x>.<y>" in comments
```

---

## Patches applied to `sa-tool/1_extract_w_lsp.py`

Every patch leaves the pre-patch file reachable via `git diff` against
whatever baseline you extracted, and is annotated in the source with a
`PATCH P<phase>.<num> — <title>` comment so it can be found and reverted
in isolation.

### P2.1 — per-language `VAR_KINDS`

**Symptom:** README listed broken var tracking for Kotlin, Lua, Ruby,
Solidity, Python, PowerShell. Root cause: the hardcoded
`VAR_KINDS = {7, 8, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26}`
was applied to every language, yet each LSP server emits different `kind`
values for "module/class-level variable".

**Change:** `VAR_KINDS` is now a dict keyed by `self.language_id`, with
the original union as the fallback. Added per-language sets for
`solidity`, `ruby`, `python`, `kotlin`, `lua`, `powershell` — the six
languages flagged in the project README. Opt-in debug env
`SA_DUMP_UNKNOWN_KINDS=1` dumps every kind each LSP emitted so future
languages can be added by inspection rather than guessing.

**Risk:** low — the fallback is the original union, so any language not
in the per-language dict gets identical behaviour to before.

### P2.2 — unconditional LocationLink normalisation

**Symptom:** `normalize_location_link()` was gated on
`"ruby-lsp" in self.server_cmd[0]` only, but `gopls`, `rust-analyzer`,
and `clangd` also return `LocationLink` when the client advertises
support for it. They don't today because of a pipeline quirk — but the
gate is brittle.

**Change:** removed the ruby-lsp gate. The function's fast path already
returns the input unchanged when `targetUri` isn't present, so there's
no behaviour change for LSPs that return plain `Location`.

**Risk:** low — preserves the original return-unchanged path.

### P2.4 — Solidity registration (no change needed)

**Intended change:** add Solidity to `lanaguage_defaults_map`.
**Actual state on inspection:** already registered with
`nomicfoundation-solidity-language-server --stdio`. The README's
"Solidity: no vars" was a `VAR_KINDS` symptom (fixed by P2.1), not a
missing-registration one.

### P2.5 — read/write heuristic extended

**Symptom:** `read_write_guess` regex at lines 3646–3660 conflated
reads/writes for several common patterns:
- compound assignments (`x += 1`, `|=`, `<<=`)
- method-invoked mutators (`map.put(...)`, `counter.fetch_add(...)`,
  `atomic.store(...)`, `Registry.Reset()`)

**Change:** added two additive passes after the existing heuristic:
1. If `ref_content` contains any of `+= -= *= /= %= |= &= ^= <<= >>= ??= .=` and the var name appears on the left of `=`, classify as `(w)`.
2. If `ref_content` matches the new `_MUTATOR_METHOD_RE` (a curated list of setter/push/store/compareAndSet/etc. method names attached to the var), classify as `(w*)` — "writeish, via mutator method".

Original classifications (`(w)` direct, `(r*)` plain call, `(r)` otherwise) remain untouched — the new rules only *upgrade* a `(r)` to `(w)` or `(w*)` when evidence warrants it.

**Risk:** low — additive, never downgrades an existing classification.

### P4.2 — C# no-`.sln` csproj-glob fallback

**Symptom:** `csharp_multi_dll/A,B,C` and `_ilspy_dump/CoreLib.dll,Shared.dll` have no shared `.sln`. Old code searched project dir + parent, then told the user to run `0_detect_project_roots.py`.

**Change:** if no `.sln` is found after the existing search:
1. Recursively glob for every `*.csproj` under `project_dir`.
2. If none exist, scan for directories that contain `.cs` files and drop a minimal `<Project Sdk="Microsoft.NET.Sdk">` csproj in each so ILSpy dumps become loadable.
3. Synthesise `_autogen.sln` at `project_dir` listing every csproj (real + auto-generated) with deterministic GUIDs derived from the relative path.
4. OmniSharp then starts against `_autogen.sln` through the existing `-s <sln>` path.

**Risk:** medium — writes files into the scanned project. Both `_autogen.sln` and `_autogen_<dir>.csproj` are named to be obvious and `.gitignore`-able. If you re-run the scan, they're idempotent (content is deterministic). Delete them to revert.

### P4.4 — `extra_symbol_search_roots` setting

**Change:** after `args.project_dir` is absolutised, read
`<project>/.vscode/ext-static-analysis/settings.json` for
`extra_symbol_search_roots` (list of paths). Paths are resolved
relative to the project dir and stashed in a module-local variable
`extra_symbol_search_roots` for future Phase 4.3 fallback-indexer use.

**Status:** variable is read + logged but is not yet wired into the
file-walker loop (that's the P4.3 work that's still deferred). Useful
today as a no-op-but-visible configuration hook so users can start
adding their extra roots and confirm they're being read.

### P5.1 — synthetic-symbol classifier

**New helpers** at module top (imports section, lines ~30–90):
- `_SYNTHETIC_PATTERNS` — 14 regexes covering Ghidra pseudo-C names
  (`FUN_/SUB_/thunk_FUN_/DAT_/PTR_/UNK_/LAB_/EXT_`), ILSpy compiler-generated
  names (`<>c__DisplayClass`, `<>f__AnonymousType`, `<>c`, `<>9__`,
  `<…>b__`, `<…>d__`, `<PrivateImplementationDetails>`, `$$methodNNN`,
  `<…>j__TPar`), and JADX dumps (`R$…`, `$Lambda$…`, `$N` anon classes,
  `access$N` bridges).
- `classify_synthetic(name)` — returns `'ilspy.display'` / `'ghidra.fn'` /
  etc., or `None`.
- `is_ghidra_decompiled_file(path)` — peeks the first 4 KB of the file (and
  its matching `.h` if given a `.c`) for `typedef unsigned char undefined` +
  `FUN_XXXX`.

**Integration point:** immediately before `g_functions.extend_by_id(functions)` and `g_scopes.extend_by_id(scopes)`, every function/scope gets a `synthetic` tag set if its name matches. Non-destructive — the existing rendering code ignores unknown dict keys.

Validated against every synthetic name in `_ilspy_dump/`, `_jadx_dump/`, and `_vulnserver/`:

```
FUN_00401000                  -> ghidra.fn
DAT_00405000                  -> ghidra.data
LAB_004011c9                  -> ghidra.label
<>c__DisplayClass0_0          -> ilspy.display
<>f__AnonymousType0           -> ilspy.anon
<>c                           -> ilspy.closure
<Process>b__0                 -> ilspy.lambda
<Reset>d__1                   -> ilspy.async
<PrivateImplementationDetails>-> ilspy.priv
$$method0x6000001             -> ilspy.method
R$layout                      -> jadx.r
$Lambda$0                     -> jadx.lambda
access$000                    -> jadx.anon
main                          -> None    ← real code untouched
Widget                        -> None
Registry                      -> None
```

**Risk:** low — purely tagging; no filtering, no mutation of existing
keys.

### P5.3 — Ghidra/IDA-C detection banner

**Change:** when scanning the `c` language, walk the project dir for
`.c`/`.h` files and call `is_ghidra_decompiled_file()` on the first
couple. If any match, print a banner indicating decompilation output
was detected. Downstream folding / filtering is handled by the P5.1
`synthetic` tag.

**Risk:** none — print-only.

---

## Patches DEFERRED (intentionally not applied this pass)

| ID   | Title                           | Reason deferred                                                                   |
|------|---------------------------------|-----------------------------------------------------------------------------------|
| P2.3 | Scope Python +1 line offset     | The +1 is load-bearing for current Pyright; changing it risks silent regressions  |
| P4.1 | Multi-root `workspaceFolders`   | Requires restructuring `init_params` and regression-testing ≥5 LSPs end-to-end    |
| P4.3 | Tree-sitter fallback indexer    | Large new subsystem; deferred to its own change set                               |
| P5.2 | Proactive no-build-file mode    | Largely superseded by P4.2 (C# auto-sln) + existing Java `.project` + OmniSharp→csharp-ls timeout fallback at lines 1203–1218. Remaining gap: pre-triggering csharp-ls before OmniSharp times out, not worth the risk without a timeout-reproducing test fixture. |

---

## How to verify

1. Rerun `scan_all.sh` from a clean state:
   ```bash
   cd example_projects && SA_TOOL_OVERRIDE=1 ./scan_all.sh 2>&1 | tee scan.log
   ```
2. Check that the "sa-tool override active:" banner appears at the top
   and that each language prints `[P2.1] lang=... VAR_KINDS=...` if
   `SA_DUMP_UNKNOWN_KINDS=1` is set.
3. Check that the C# multi-dir fixture logs `[c#][P4.2] no .sln found; synthesised _autogen.sln with N csproj(s)`.
4. Check that `_vulnserver/` logs `[P5.3] Ghidra-style decompilation detected`.
5. Run `python3 scope_check.py --diff` and compare the `extractor_hit`
   pass-rate per case against the pre-patch run.
