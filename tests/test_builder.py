from __future__ import annotations

import codecs
import json
import tempfile
import unittest
from pathlib import Path

from message_version_bundle import build_versions, parse_marker_levels, read_levels, write_no_bom_json


class BuilderTests(unittest.TestCase):
    def test_marker_format_parses_levels(self) -> None:
        levels = parse_marker_levels("--- 1 ---\nshort\n--- level 2 ---\nshorter", Path("levels.txt"))
        self.assertEqual(levels, {"1": "short", "2": "shorter"})

    def test_duplicate_marker_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate level marker"):
            parse_marker_levels("--- 1 ---\nfirst\n--- 1 ---\nsecond", Path("levels.txt"))

    def test_json_wrapper_parses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "levels.json"
            path.write_text(json.dumps({"levels": {"1": "short"}}), encoding="utf-8")
            self.assertEqual(read_levels(path), {"1": "short"})

    def test_exact_bundle_has_levels_zero_through_nine(self) -> None:
        levels = {str(i): f"level {i}" for i in range(1, 10)}
        bundle = build_versions("canonical", levels, "error")
        self.assertEqual(set(bundle), {str(i) for i in range(10)})
        self.assertEqual(bundle["0"]["char_count"], 9)

    def test_missing_levels_fail_by_default(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing required levels"):
            build_versions("canonical", {"1": "short"}, "error")

    def test_repeat_last_is_explicit(self) -> None:
        bundle = build_versions("canonical", {"1": "short"}, "repeat-last")
        self.assertEqual(bundle["9"]["message"], "short")

    def test_conflicting_level_zero_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not match"):
            build_versions("canonical", {"0": "different"}, "repeat-last")

    def test_writer_uses_utf8_without_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bundle.json"
            write_no_bom_json(path, {"ok": True})
            self.assertFalse(path.read_bytes().startswith(codecs.BOM_UTF8))

    def test_writer_refuses_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bundle.json"
            write_no_bom_json(path, {"version": 1})
            with self.assertRaises(FileExistsError):
                write_no_bom_json(path, {"version": 2})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["version"], 1)
            write_no_bom_json(path, {"version": 2}, force=True)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["version"], 2)


if __name__ == "__main__":
    unittest.main()
