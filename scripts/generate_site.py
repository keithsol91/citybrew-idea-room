#!/usr/bin/env python3
import json, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'data'/'runs.json').read_text())
def esc(x): return html.escape(str(x))
cards=[]
for r in DATA['runs']:
    status_class = 'review' if 'Review' in r.get('status','') else ('approved' if 'Approved' in r.get('status','') else '')
    selected = ', '.join(r.get('selected') or []) or 'none yet'
    cards.append('<article class="run"><div><span class="pill '+status_class+'">'+esc(r.get('status',''))+'</span><h2>'+esc(r['title'])+'</h2><div class="meta">'+esc(r['date'])+' - '+esc(r.get('concept_count',0))+' concepts - Selected: '+esc(selected)+'</div></div><a class="button" href="'+esc(r['path'].rstrip('/') + '/index.html')+'">Open board</a></article>')
html_doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+esc(DATA['client'])+' — Idea Room Archive</title><link rel="stylesheet" href="assets/css/archive.css"></head><body><main class="wrap"><section class="hero"><div class="eyebrow">SociallyIn Idea Room Archive</div><h1>'+esc(DATA['client'])+'</h1><p class="sub">Permanent AM review-board archive. Public/unlisted for now. Old boards can be hidden from this index without deleting source files.</p></section><section class="runs">'+''.join(cards)+'</section></main></body></html>'
(ROOT/'index.html').write_text(html_doc)
print('generated index.html')
