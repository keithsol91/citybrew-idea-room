import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREATE_RUN = ROOT / "scripts" / "create_run.py"
BUILD_BOARD = Path("/Users/taterbot/.hermes/profiles/idea-piper/scripts/idea_room_build_board.py")


def load_build_board():
    spec = importlib.util.spec_from_file_location("idea_room_build_board", BUILD_BOARD)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class V3GuardTests(unittest.TestCase):
    def run_create(self, *args):
        return subprocess.run(
            [sys.executable, str(CREATE_RUN), *map(str, args)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_direct_publish_requires_approval_before_reading_input(self):
        result = self.run_create("--input", "does-not-matter.json", "--publish")
        self.assertEqual(result.returncode, 2)
        self.assertIn("publish requires --approval APPROVE_PUBLISH_CITYBREW_BOARD", result.stderr)

    def test_direct_publish_requires_clean_tree_even_with_approval(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "data") as td:
            path = Path(td) / "ok.json"
            path.write_text(json.dumps({
                "title": "Dirty Publish Test",
                "slug": "dirty-publish-test",
                "ideas": [{
                    "title": "Idea", "format": "Reel", "readiness": "READY TO BRIEF",
                    "summary": "Specific idea", "visual_direction": "Simple frame", "assets_needed": ["asset"]
                }],
            }))
            result = self.run_create("--input", path.relative_to(ROOT), "--publish", "--approval", "APPROVE_PUBLISH_CITYBREW_BOARD")
        self.assertEqual(result.returncode, 2)
        self.assertIn("clean working tree", result.stderr)

    def test_create_run_rejects_incomplete_idea_schema(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text(json.dumps({"title": "Bad", "slug": "bad-schema", "ideas": [{"title": "Missing fields"}]}))
            result = self.run_create("--input", path, "--no-commit")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required fields", result.stderr.lower())

    def test_selected_order_follows_am_request(self):
        mod = load_build_board()
        candidates = [
            {"name": "One", "summary": "A", "format": "Reel"},
            {"name": "Two", "summary": "B", "format": "Carousel"},
            {"name": "Three", "summary": "C", "format": "Story"},
        ]
        matched, missing = mod.normalize_selected(["3", "1"], candidates)
        self.assertEqual(missing, [])
        self.assertEqual([c["name"] for c in matched], ["Three", "One"])

    def test_readiness_not_contaminated_by_global_moxie_kill_gate_text(self):
        mod = load_build_board()
        state = {
            "client": "City Brew Coffee",
            "brief": "Summer drinks",
            "run_id": "pytest-readiness",
            "moxie_pass": "Moxie kill gate: 2) Bad Idea — Kill — generic.",
            "riff_pass": "Riff production pass: approval needed for Bad Idea.",
            "candidates": [
                {"name": "Good Idea", "format": "Reel", "summary": "Morning routine helper", "assets_needed": ["cup"]},
            ],
        }
        spec, err = mod.build_spec(state, [])
        self.assertIsNone(err)
        self.assertEqual(spec["ideas"][0]["readiness"], "READY TO BRIEF")


if __name__ == "__main__":
    unittest.main()
