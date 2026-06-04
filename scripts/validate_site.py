#!/usr/bin/env python3
import pathlib, json, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
errors=[]
for path in [ROOT/'index.html', ROOT/'data'/'runs.json', ROOT/'assets'/'css'/'archive.css', ROOT/'assets'/'css'/'board.css']:
    if not path.exists():
        errors.append(f'missing {path.relative_to(ROOT)}')
try:
    data=json.loads((ROOT/'data'/'runs.json').read_text())
    for r in data.get('runs',[]):
        run_index=ROOT/r['path']/'index.html'
        if not run_index.exists():
            errors.append(f'missing run page {run_index.relative_to(ROOT)}')
        for asset in (ROOT/r['path']/'assets').glob('*') if (ROOT/r['path']/'assets').exists() else []:
            if asset.stat().st_size == 0:
                errors.append(f'empty asset {asset.relative_to(ROOT)}')
except Exception as e:
    errors.append(f'runs.json invalid: {e}')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('site validation passed')
