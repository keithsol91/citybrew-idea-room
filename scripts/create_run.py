#!/usr/bin/env python3
"""Create a City Brew Idea Room run from structured JSON/YAML.

Usage:
  python3 scripts/create_run.py --input data/example-run.json --no-commit
  python3 scripts/create_run.py --input data/example-run.json --publish --approval APPROVE_PUBLISH_CITYBREW_BOARD
"""
import argparse
import html
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
APPROVAL_PHRASE = "APPROVE_PUBLISH_CITYBREW_BOARD"


def esc(value):
    return html.escape(str(value if value is not None else ""))


def slugify(value):
    value = re.sub(r"[^a-zA-Z0-9]+", "-", str(value).lower()).strip("-")
    return value or "untitled-run"


def load_spec(path):
    path = pathlib.Path(path)
    text = path.read_text()
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except Exception as exc:
            raise SystemExit("YAML input requires PyYAML; use JSON instead") from exc
        return yaml.safe_load(text)
    raise SystemExit("Input must be .json, .yaml, or .yml")


def validate_spec(spec):
    if not isinstance(spec, dict):
        raise ValueError("run spec must be a JSON object")
    ideas = spec.get("ideas") or []
    if not isinstance(ideas, list) or not ideas:
        raise ValueError("run spec must include at least one idea")
    if not spec.get("title"):
        raise ValueError("run spec must include title")
    required = ["title", "format", "readiness", "summary", "visual_direction", "assets_needed"]
    for idx, idea in enumerate(ideas, start=1):
        if not isinstance(idea, dict):
            raise ValueError(f"idea {idx} must be an object")
        missing = [field for field in required if field not in idea or idea.get(field) in (None, "")]
        if missing:
            raise ValueError(f"idea {idx} missing required fields: {', '.join(missing)}")
        if not isinstance(idea.get("assets_needed"), list):
            raise ValueError(f"idea {idx} assets_needed must be a list")


def idea_image_tag(idea):
    mockup = idea.get("mockup")
    if mockup:
        return f'<img src="{esc(mockup)}" alt="Visual direction mockup">'
    label = esc(idea.get("title", "Idea"))
    return (
        '<div class="mockup-fallback" role="img" aria-label="Visual direction placeholder">'
        '<div class="fallback-label">Social mockup needed</div>'
        f'<div class="fallback-title">{label}</div>'
        '</div>'
    )


def render_board(spec, run_dir):
    ideas = spec["ideas"]
    tags = spec.get("tags") or [f"{len(ideas)} concepts", "RICA-light", "designer brief after selection"]
    rows = []
    cards = []
    for idea in ideas:
        title = idea.get("title", "Untitled idea")
        rows.append(
            "<tr>"
            f"<td>{esc(title)}</td>"
            f"<td>{esc(idea.get('format',''))}</td>"
            f"<td>{esc(idea.get('readiness',''))}</td>"
            f"<td>{esc(idea.get('dependency',''))}</td>"
            f"<td>{esc(idea.get('next_action',''))}</td>"
            "</tr>"
        )
        assets = idea.get("assets_needed") or []
        asset_items = "".join(f"<li>{esc(a)}</li>" for a in assets)
        cards.append(
            '<article class="idea-card">'
            '<div class="mockup">'
            f'{idea_image_tag(idea)}'
            '<div class="mockup-caption">AI visual mockup — direction only, not final asset.</div>'
            '</div>'
            '<div class="idea-body">'
            f'<div class="eyebrow">IDEA {esc(idea.get("id", ""))} · {esc(idea.get("format", ""))} · {esc(idea.get("category", ""))}</div>'
            f'<h3>{esc(title)}</h3>'
            f'<p>{esc(idea.get("summary", ""))}</p>'
            '<h4>Visual Direction / Mockup</h4>'
            f'<p>{esc(idea.get("visual_direction", ""))}</p>'
            '<h4>On-Asset Copy</h4>'
            f'<p>{esc(idea.get("on_asset_copy", ""))}</p>'
            '<h4>Caption Sample</h4>'
            f'<p>{esc(idea.get("caption", ""))}</p>'
            '<h4>Assets Needed</h4>'
            f'<ul>{asset_items}</ul>'
            f'<div class="notes">Room notes: {esc(idea.get("room_notes", ""))}</div>'
            '</div>'
            '</article>'
        )
    tag_html = "".join(f'<span class="chip">{esc(t)}</span>' for t in tags)
    html_doc = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(spec.get('client','City Brew Coffee'))} — {esc(spec['title'])}</title>
  <link rel="stylesheet" href="../../assets/css/board.css">
</head>
<body>
<main class="wrap">
  <section class="hero">
    <div class="card">
      <div class="eyebrow">{esc(spec.get('client','City Brew Coffee'))} · AM Review Board</div>
      <h1>{esc(spec['title'])}</h1>
      <p class="sub">{esc(spec.get('subtitle',''))}</p>
      <div class="chips">{tag_html}</div>
      <a class="button" href="../../index.html">Back to archive</a>
    </div>
    <div class="guardrails">Guardrails: {esc(spec.get('guardrails','Use real client assets where possible. AI mockups are direction only.'))}</div>
  </section>

  <section class="summary card">
    <h2>Decision Summary</h2>
    <p>AM chooses: use / revise / kill / build brief</p>
    <table>
      <thead><tr><th>Idea</th><th>Format</th><th>Readiness</th><th>Main Dependency</th><th>AM Next Action</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </section>

  <section class="ideas">
    <div class="section-head"><h2>Idea Cards</h2><p>Visual direction stays; external reference optional.</p></div>
    {''.join(cards)}
  </section>

  <footer class="footer">Feedback shortcuts: use 1 · revise 2 copy warmer · kill 3 · build brief 1 · more local</footer>
</main>
</body>
</html>
'''
    (run_dir / "index.html").write_text(html_doc)


def update_runs_json(spec, slug):
    data_path = ROOT / "data" / "runs.json"
    data = json.loads(data_path.read_text())
    runs = data.setdefault("runs", [])
    entry = {
        "date": spec.get("created_at") or datetime.now().strftime("%Y-%m-%d"),
        "title": spec["title"],
        "slug": slug,
        "status": spec.get("status", "AM Review"),
        "concept_count": len(spec["ideas"]),
        "selected": spec.get("selected", []),
        "path": f"runs/{slug}/",
    }
    runs[:] = [r for r in runs if r.get("slug") != slug]
    runs.insert(0, entry)
    data_path.write_text(json.dumps(data, indent=2) + "\n")


def run(cmd):
    subprocess.run(cmd, cwd=ROOT, check=True)


def git_status_short():
    proc = subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or "git status failed")
    return proc.stdout.strip()


def preexisting_dirty_lines_for_commit(input_arg):
    dirty = git_status_short()
    if not dirty:
        return []
    input_path = pathlib.Path(input_arg)
    allowed_paths = set()
    try:
        allowed_paths.add(str(input_path.relative_to(ROOT)))
    except ValueError:
        pass
    remaining = []
    for line in dirty.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if path in allowed_paths and line[:2] in {"??", " M", "M "}:
            continue
        remaining.append(line)
    return remaining


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--no-commit", action="store_true", help="Generate local files only (safe default; retained for compatibility)")
    parser.add_argument("--commit", action="store_true", help="Commit generated board locally without pushing")
    parser.add_argument("--publish", action="store_true", help="Commit and push; requires --approval phrase")
    parser.add_argument("--approval", default="", help=f"Required exact phrase for --publish: {APPROVAL_PHRASE}")
    args = parser.parse_args(argv)
    if args.publish and args.approval != APPROVAL_PHRASE:
        print(f"publish requires --approval {APPROVAL_PHRASE}", file=sys.stderr)
        return 2
    if args.commit or args.publish:
        dirty_lines = preexisting_dirty_lines_for_commit(args.input)
        if dirty_lines:
            print("commit/publish requires clean working tree except the current input spec", file=sys.stderr)
            print("\n".join(dirty_lines), file=sys.stderr)
            return 2

    try:
        spec = load_spec(args.input)
        validate_spec(spec)
        slug = slugify(spec.get("slug") or spec["title"])
        run_dir = ROOT / "runs" / slug
        (run_dir / "assets").mkdir(parents=True, exist_ok=True)
        render_board(spec, run_dir)
        update_runs_json(spec, slug)
        run([sys.executable, str(ROOT / "scripts" / "generate_site.py")])
        run([sys.executable, str(ROOT / "scripts" / "validate_site.py")])
        should_commit = bool(args.commit or args.publish) and not args.no_commit
        if should_commit:
            input_path = pathlib.Path(args.input)
            add_paths = ["index.html", "data/runs.json", f"runs/{slug}", "assets/css/board.css"]
            try:
                add_paths.append(str(input_path.relative_to(ROOT)))
            except ValueError:
                pass
            run(["git", "add", *add_paths])
            run(["git", "commit", "-m", f"Add Idea Room run: {spec['title']}"])
            if args.publish:
                run(["git", "push", "origin", "main"])
        print(json.dumps({"slug": slug, "board": f"runs/{slug}/index.html"}, indent=2))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
