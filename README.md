# City Brew Idea Room Archive

Static GitHub Pages archive for City Brew Idea Room AM review boards.

Target: public/unlisted GitHub Pages.

## Image-generation workflow

Recommended v1 provider: Higgsfield CLI.

- Product/lifestyle/social board mockups: `higgsfield product-photoshoot create`.
- Use `--enhance-only` to inspect prompt quality without spending generation credits.
- Cost-control rule: generate images only for selected HTML-board ideas, not for every rough idea.
- Default: 1 mockup per idea, reused in Designer Brief unless AM asks for a new visual direction.

Raw model sample costs from the current authenticated Higgsfield account:

- `gpt_image_2`: 7 credits
- `nano_banana_2`: 2 credits
- `image_auto`: 2 credits
- `z_image`: 0.15 credits

Prompt builder:

```bash
python3 scripts/build_higgsfield_prompt.py \
  --idea "Your Usual Should Count" \
  --scene "coffee cup handoff at warm shop counter" \
  --format "Reel or Story" \
  --asset-needs "cup handoff angle, counter texture, receipt/register context"
```

Product-photoshoot prompt enhancement preview:

```bash
higgsfield product-photoshoot create \
  --mode lifestyle_scene \
  --prompt "AI visual-direction mockup for City Brew AM review board: coffee cup handoff at a warm regional coffee shop counter, receipt/register moment, natural light, no fake text or offers" \
  --aspect_ratio 4:5 \
  --count 1 \
  --enhance-only
```

## Notes

- AI mockups are visual direction only, not final production assets.
- External references are optional.
- Visual direction/mockup stays required on the AM board.
- AM feedback happens in Slack; small copy edits should update run data/logs, not force a new board version.
