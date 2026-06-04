# City Brew Idea Room Archive

Static GitHub Pages archive for City Brew Idea Room AM review boards.

Target: public/unlisted GitHub Pages.

Live archive:

- https://keithsol91.github.io/citybrew-idea-room/

## Create/publish a new board

Create a run spec from the template:

```bash
cp templates/run-spec.example.json data/new-run.json
# edit data/new-run.json
```

Generate locally without committing:

```bash
python3 scripts/create_run.py --input data/new-run.json --no-commit
```

Generate, commit, and push live:

```bash
python3 scripts/create_run.py --input data/new-run.json --publish
```

The script will:

- validate the run spec
- create `runs/<slug>/index.html`
- update `data/runs.json`
- regenerate the archive homepage
- run site validation
- optionally commit/push to GitHub Pages

## Image-generation workflow

Recommended v1 provider: Higgsfield CLI.

Current practical routing:

- Photo/lifestyle/product-led board mockups: `image_auto` or `product-photoshoot` if it passes moderation.
- Cheap rough drafts: `z_image`.
- General backup: `nano_banana_2` or `image_auto`.
- Premium direct model: `gpt_image_2`.
- Footage/Reel motion: make static keyframe first; generate video only if motion matters.

Cost-control rule:

- no images for the 15–20 hidden rough ideas
- no images for Slack Concept Menu by default
- 1 mockup per selected HTML-board idea
- reuse same mockup in Designer Brief unless direction changes

Raw model sample costs from current authenticated Higgsfield account:

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

Known Higgsfield notes:

- `product-photoshoot` hit a false NSFW rejection on a handoff/counter prompt.
- Live generation rejected `4:5`; safest defaults are `3:4` for board images and `9:16` for vertical social/video references.
- Avoid prompts with fake logos, readable fake text, invented drink names, offers, prices, or legal-sensitive claims.

## Future visual upgrade: social mockup frames

Current mockups are photo-direction mood images. Good enough for v1, but the better target is:

- Reel keyframe mockup: 9:16 frame with safe overlay-copy zones, hook text, lower-third notes, and motion cue.
- Carousel mockup: 2–4 slide thumbnails showing what goes on each slide.
- Static graphic mockup: product/photo + actual headline placement, not just a pretty image.
- Story mockup: vertical frame with sticker/CTA/copy placement.
- Footage direction: first frame + shot list + motion beats before spending video credits.

For now, encode this in each idea’s `visual_direction` field. Later, add a `mockup_type` field and renderer variants.

## Quality rules

- AI mockups are visual direction only, not final production assets.
- External references are optional.
- Visual direction/mockup stays required on the AM board.
- AM feedback happens in Slack; small copy edits should update run data/logs, not force a new board version.
