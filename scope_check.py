#!/usr/bin/env python3
"""Scope-test harness for the example-projects fixtures.

Walks every `scopes.*` file under the repo root, extracts the
`S<NN>.<role>[.kind]` markers embedded in comments, and produces a
manifest JSON describing the expected `var_ref_map` entries.

The companion extractor (`alecmaly/source-mapper` / `1_extract_w_lsp.py`)
writes `var_ref_map.gzip` into each language's
`.vscode/ext-static-analysis/cache/` directory. This script can later
be extended to diff the manifest against that output; for now it just
emits `scope_manifest.json` so the contract is machine-readable.

Usage:
    python3 scope_check.py                 # scan + emit manifest
    python3 scope_check.py --diff          # also diff vs extractor output
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys
from pathlib import Path

# Case IDs that the spec reserves.
VALID_CASES = set(f"S{n:02d}" for n in range(1, 15))

# Known marker kinds per role. Captured in the regex below.
VALID_ROLES = {
    "def", "outer", "inner", "param", "instance",
    "static", "base", "derived", "shadow",
    "consumer", "origin", "b",
}
VALID_KINDS = {"def", "read", "write", "import"}

# The marker regex. Matches markers anywhere in a comment. Examples:
#   # S02.outer.def
#   // S08.shadow.read
#   # S09.def
#   # S10.consumer.import
MARKER_RE = re.compile(
    r"""
    (?P<case>S\d{2})
    \.
    (?P<role>[a-zA-Z]+)
    (?:
        \.
        (?P<kind>[a-zA-Z]+)
    )?
    """,
    re.VERBOSE,
)

# Map file extension → language tag used by the extractor.
EXT_TO_LANG = {
    ".py":     "python",
    ".java":   "java",
    ".cs":     "csharp",
    ".kt":     "kotlin",
    ".ts":     "typescript",
    ".tsx":    "typescript",
    ".go":     "go",
    ".rs":     "rust",
    ".rb":     "ruby",
    ".php":    "php",
    ".sol":    "solidity",
    ".c":      "c",
    ".h":      "c",
    ".cpp":    "cpp",
    ".hpp":    "cpp",
    ".lua":    "lua",
    ".sh":     "bash",
    ".ps1":    "powershell",
    ".ex":     "elixir",
    ".exs":    "elixir",
    ".groovy": "groovy",
    ".hs":     "haskell",
    ".ml":     "ocaml",
    ".mli":    "ocaml",
    ".scala":  "scala",
    ".swift":  "swift",
    ".zig":    "zig",
}


def scan_file(path: Path) -> list[dict]:
    """Extract scope markers from a single file."""
    out: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out

    for lineno, line in enumerate(lines, start=1):
        for m in MARKER_RE.finditer(line):
            case = m.group("case")
            role = m.group("role")
            kind = m.group("kind")
            if case not in VALID_CASES:
                continue

            # Two-part markers like "S01.read" have role=read, kind=None.
            # If the single suffix is actually a KIND word, promote it.
            if kind is None and role in VALID_KINDS:
                kind = role
                role = "def" if kind == "def" else "primary"
            # Otherwise role must be a known role word.
            if role not in VALID_ROLES and role != "primary":
                continue
            if kind is not None and kind not in VALID_KINDS:
                continue
            out.append(
                {
                    "file": str(path),
                    "line": lineno,
                    "case": case,
                    "role": role,
                    "kind": kind or "def",
                    "raw": line.strip(),
                }
            )
    return out


def is_scope_fixture(path: Path) -> bool:
    """Scope fixtures are named `scopes.<ext>` or `Scopes.<ext>`."""
    stem = path.stem.lower()
    return stem == "scopes"


def collect(root: Path) -> dict:
    """Walk the tree and produce { lang: [markers…] }."""
    manifest: dict[str, list[dict]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip noise
        if any(seg in dirpath for seg in (".git", ".vscode", "node_modules", "target")):
            continue
        for fn in filenames:
            path = Path(dirpath) / fn
            if not is_scope_fixture(path):
                continue
            lang = EXT_TO_LANG.get(path.suffix.lower())
            if lang is None:
                continue
            markers = scan_file(path)
            if not markers:
                continue
            manifest.setdefault(lang, []).extend(markers)
    return manifest


def summarise(manifest: dict) -> dict:
    """Per-language, per-case counts of def/read/write entries."""
    summary: dict[str, dict[str, dict[str, int]]] = {}
    for lang, entries in manifest.items():
        per_case: dict[str, dict[str, int]] = {}
        for e in entries:
            bucket = per_case.setdefault(e["case"], {"def": 0, "read": 0, "write": 0, "import": 0})
            bucket[e["kind"]] = bucket.get(e["kind"], 0) + 1
        summary[lang] = per_case
    return summary


def load_extractor_var_refs(lang_root: Path) -> dict | None:
    """Best-effort load of the extractor's var_ref_map for a language."""
    candidates = [
        lang_root / ".vscode" / "ext-static-analysis" / "cache" / "var_ref_map.gzip",
        lang_root / ".vscode" / "ext-static-analysis" / "cache" / "var_ref_map.json",
    ]
    for p in candidates:
        if not p.exists():
            continue
        try:
            if p.suffix == ".gzip":
                with gzip.open(p, "rt", encoding="utf-8") as fh:
                    return json.load(fh)
            else:
                return json.loads(p.read_text())
        except Exception as e:
            print(f"warning: could not load {p}: {e}", file=sys.stderr)
    return None


def diff_against_extractor(root: Path, manifest: dict) -> dict:
    """Very light diff: per case, did the extractor's var_ref_map contain
    at least one entry at each marker's (file, line)?

    This is intentionally conservative — the extractor's output shape is
    not fixed and this harness will need to be tightened once Phase 2/4
    of the extractor work lands.
    """
    report: dict[str, list[dict]] = {}
    for lang, entries in manifest.items():
        lang_root = root / lang
        refs = load_extractor_var_refs(lang_root)
        if refs is None:
            report[lang] = [{"status": "skip", "reason": "no var_ref_map"}]
            continue

        flat = {}
        try:
            # var_ref_map is expected to be { var_id: [ {file, line, kind, ...}, ... ] }
            for _, ref_list in (refs.items() if isinstance(refs, dict) else []):
                for r in ref_list or []:
                    key = (r.get("file") or r.get("uri") or "").split("/")[-1], r.get("line")
                    flat.setdefault(key, []).append(r)
        except Exception as e:
            report[lang] = [{"status": "error", "reason": f"bad var_ref_map shape: {e}"}]
            continue

        results = []
        for m in entries:
            key = (Path(m["file"]).name, m["line"])
            hit = key in flat
            results.append({
                "case": m["case"],
                "kind": m["kind"],
                "role": m["role"],
                "file": Path(m["file"]).name,
                "line": m["line"],
                "extractor_hit": hit,
            })
        report[lang] = results
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--manifest", default="scope_manifest.json",
                    help="output manifest file path")
    ap.add_argument("--diff", action="store_true",
                    help="also diff against each language's var_ref_map")
    ap.add_argument("--summary-only", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    manifest = collect(root)
    summary = summarise(manifest)

    if args.summary_only:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    payload = {"summary": summary, "markers": manifest}
    if args.diff:
        payload["diff"] = diff_against_extractor(root, manifest)

    out_path = Path(args.manifest)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"wrote {out_path} "
          f"(langs={len(manifest)}, markers={sum(len(v) for v in manifest.values())})",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
