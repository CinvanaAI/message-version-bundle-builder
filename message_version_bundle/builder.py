#!/usr/bin/env python3
"""Build a chatroom message-version bundle from a canonical message file.

The backend update command expects a JSON object keyed by version level 0-9.
This helper copies level 0 from the canonical hidden message file, accepts
Codex-prepared semantic levels from a small input file, recomputes char_count
values, and writes UTF-8 JSON without a BOM.
"""

from __future__ import annotations

import argparse
import codecs
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


MIN_LEVEL = 0
MAX_LEVEL = 9
LEVEL_MARKER = re.compile(r"^---\s*(?:level\s*)?([0-9])\s*---\s*$", re.IGNORECASE)


def text_char_count(value: object) -> int:
    return len(str(value or ""))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_message(path: Path) -> str:
    parsed = read_json(path)
    if not isinstance(parsed, dict):
        raise ValueError(f"message file must contain a JSON object: {path}")
    if "message" not in parsed:
        raise ValueError(f"message file is missing canonical message text: {path}")
    return str(parsed.get("message", "") or "")


def parse_marker_levels(text: str, path: Path) -> dict[str, str]:
    levels: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    saw_marker = False

    def flush() -> None:
        nonlocal current_key, current_lines
        if current_key is not None:
            if current_key in levels:
                raise ValueError(f"duplicate level marker {current_key} in {path}")
            levels[current_key] = "\n".join(current_lines).strip()
        current_key = None
        current_lines = []

    for raw_line in text.splitlines():
        match = LEVEL_MARKER.match(raw_line.strip())
        if match:
            saw_marker = True
            flush()
            current_key = match.group(1)
            continue
        if current_key is not None:
            current_lines.append(raw_line)
        elif raw_line.strip():
            raise ValueError(
                f"unexpected text before first level marker in {path}; "
                "use JSON or markers like '--- 1 ---'"
            )

    flush()
    if not saw_marker:
        raise ValueError(f"levels file is neither JSON nor marker format: {path}")
    return levels


def normalize_levels(raw: Any) -> dict[str, str]:
    if isinstance(raw, dict) and "versions" in raw:
        raw = raw["versions"]
    elif isinstance(raw, dict) and "levels" in raw:
        raw = raw["levels"]

    if not isinstance(raw, dict):
        raise ValueError("levels file must be a JSON object, or contain 'levels'/'versions'")

    levels: dict[str, str] = {}
    for key, value in raw.items():
        level_key = str(key)
        if not level_key.isdigit():
            continue
        level = int(level_key)
        if level < MIN_LEVEL or level > MAX_LEVEL:
            continue
        if isinstance(value, dict):
            levels[level_key] = str(value.get("message", "") or "")
        else:
            levels[level_key] = str(value or "")
    return levels


def _unique_json_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member in levels file: {key}")
        result[key] = value
    return result


def read_levels(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        return normalize_levels(json.loads(text, object_pairs_hook=_unique_json_members))
    return parse_marker_levels(text, path)


def build_versions(canonical: str, levels: dict[str, str], fill_missing: str) -> dict[str, dict[str, Any]]:
    if "0" in levels and levels["0"] != canonical:
        raise ValueError("provided level 0 does not match canonical message text")

    versions: dict[str, dict[str, Any]] = {
        "0": {"message": canonical, "char_count": text_char_count(canonical)}
    }
    last_text = canonical
    missing: list[str] = []

    for level in range(1, MAX_LEVEL + 1):
        key = str(level)
        if key in levels:
            text = levels[key]
        elif fill_missing == "repeat-last":
            text = last_text
        else:
            missing.append(key)
            continue
        versions[key] = {"message": text, "char_count": text_char_count(text)}
        last_text = text

    if missing:
        raise ValueError(f"levels file missing required levels: {', '.join(missing)}")
    if set(versions.keys()) != {str(level) for level in range(MIN_LEVEL, MAX_LEVEL + 1)}:
        raise ValueError("versions object does not contain exactly levels 0-9")
    return versions


def write_no_bom_json(path: Path, value: Any, *, force: bool = False) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"output exists; pass --force only after reviewing it: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    handle_number, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle_number, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if temporary.read_bytes().startswith(codecs.BOM_UTF8):
            raise ValueError(f"UTF-8 BOM detected after write: {path}")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message-file", required=True, type=Path)
    parser.add_argument("--levels-file", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true", help="Replace an existing output after explicit review")
    parser.add_argument(
        "--fill-missing",
        default="error",
        choices=["error", "repeat-last"],
        help="Repeat the prior level only when Codex has intentionally decided it is safe.",
    )
    args = parser.parse_args(argv)

    canonical = read_message(args.message_file)
    levels = read_levels(args.levels_file)
    versions = build_versions(canonical, levels, args.fill_missing)
    write_no_bom_json(args.output, versions, force=args.force)

    summary = {
        "output": str(args.output),
        "level_count": len(versions),
        "level_0_char_count": versions["0"]["char_count"],
        "counts": {key: record["char_count"] for key, record in versions.items()},
        "bom": False,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"build_version_bundle.py: {exc}", file=sys.stderr)
        raise SystemExit(1)
