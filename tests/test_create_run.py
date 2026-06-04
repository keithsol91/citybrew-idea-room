import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "create_run.py"


class CreateRunTests(unittest.TestCase):
    def setUp(self):
        self.runs_json = ROOT / "data" / "runs.json"
        self.archive = ROOT / "index.html"
        self.original_runs_json = self.runs_json.read_text()
        self.original_archive = self.archive.read_text()

    def tearDown(self):
        self.runs_json.write_text(self.original_runs_json)
        self.archive.write_text(self.original_archive)
        import shutil
        shutil.rmtree(ROOT / "runs" / "pytest-demo-board", ignore_errors=True)
        shutil.rmtree(ROOT / "runs" / "bad-run", ignore_errors=True)

    def run_cmd(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_create_run_from_json_writes_board_and_updates_archive(self):
        import tempfile
        spec = {
            "client": "City Brew Coffee",
            "slug": "pytest-demo-board",
            "title": "Pytest Demo Board",
            "subtitle": "Generated from structured data.",
            "status": "AM Review",
            "created_at": "2026-06-04",
            "guardrails": "Keep it specific. Direction only.",
            "tags": ["2 concepts", "generated"],
            "ideas": [
                {
                    "id": "01",
                    "title": "Morning Shortcut",
                    "format": "Reel keyframe",
                    "readiness": "READY TO BRIEF",
                    "dependency": "none",
                    "next_action": "Use",
                    "category": "Routine",
                    "summary": "Make the morning stop feel useful.",
                    "visual_direction": "Counter, cup, bag, simple overlay copy.",
                    "on_asset_copy": "Make the stop count.",
                    "caption": "Your morning coffee can do more.",
                    "assets_needed": ["cup photo", "counter angle"],
                    "room_notes": "Moxie kept it specific.",
                    "mockup": "assets/idea-01-mockup.webp",
                },
                {
                    "id": "02",
                    "title": "Cold Order Helper",
                    "format": "Carousel",
                    "readiness": "NEEDS CLIENT INPUT",
                    "dependency": "approved drink",
                    "next_action": "Pick drink",
                    "category": "Product help",
                    "summary": "Solve a common order question.",
                    "visual_direction": "Slide mockup with iced drink and simple decision copy.",
                    "on_asset_copy": "Cold but not too sweet?",
                    "caption": "Ask for this when you want coffee flavor first.",
                    "assets_needed": ["approved drink photo"],
                    "room_notes": "Needs drink confirmation.",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            spec_path = Path(td) / "run.json"
            spec_path.write_text(json.dumps(spec))
            result = self.run_cmd("--input", spec_path, "--no-commit")

        self.assertEqual(result.returncode, 0, result.stderr)
        run_dir = ROOT / "runs" / "pytest-demo-board"
        board = run_dir / "index.html"
        self.assertTrue(board.exists())
        html = board.read_text()
        self.assertIn("Pytest Demo Board", html)
        self.assertIn("Morning Shortcut", html)
        self.assertIn("Cold Order Helper", html)
        self.assertIn("AI visual mockup", html)

        runs = json.loads((ROOT / "data" / "runs.json").read_text())["runs"]
        self.assertTrue(any(r["slug"] == "pytest-demo-board" and r["path"] == "runs/pytest-demo-board/" for r in runs))
        archive = (ROOT / "index.html").read_text()
        self.assertIn("Pytest Demo Board", archive)

    def test_create_run_requires_ideas(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            spec_path = Path(td) / "bad.json"
            spec_path.write_text(json.dumps({"title": "No Ideas", "slug": "bad-run", "ideas": []}))
            result = self.run_cmd("--input", spec_path, "--no-commit")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least one idea", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
