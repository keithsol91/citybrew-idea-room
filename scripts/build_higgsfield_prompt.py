#!/usr/bin/env python3
"""Build tight Higgsfield visual-direction prompts for City Brew AM boards.

Usage:
  python3 scripts/build_higgsfield_prompt.py \
    --idea "Your Usual Should Count" \
    --scene "coffee cup handoff at warm shop counter with receipt/register moment" \
    --format "Reel or Story" \
    --asset-needs "cup handoff b-roll, register/receipt shot" \
    --aspect "4:5"
"""
import argparse
import textwrap

MAX_WORDS = 150

def clamp_words(text: str, max_words: int = MAX_WORDS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(",.;") + "."


def build_prompt(args):
    pieces = [
        "AI visual-direction mockup for an AM review board, not a final production asset.",
        f"Concept: {args.idea}.",
        f"Scene: {args.scene}.",
        "Authentic regional coffee shop environment, warm local feeling, realistic lifestyle photography.",
        f"Social-first {args.aspect} composition for {args.format}, clear focal point, useful negative space if overlay copy is needed.",
        "Natural window light, tactile coffee textures, handheld/social feel, not overproduced, not generic stock photography.",
        f"Production guidance should be obvious: {args.asset_needs}.",
        "No readable fake text, no fake offers, no fake prices, no invented drink names, no fake logos unless approved brand assets are provided.",
    ]
    if args.brand_context:
        pieces.insert(3, f"Brand context: {args.brand_context}.")
    if args.product_context:
        pieces.insert(4, f"Product context: {args.product_context}.")
    return clamp_words(" ".join(pieces))


def main():
    p = argparse.ArgumentParser(description="Build a Higgsfield prompt for City Brew visual-direction mockups.")
    p.add_argument("--idea", required=True)
    p.add_argument("--scene", required=True)
    p.add_argument("--format", default="AM review board idea card")
    p.add_argument("--asset-needs", default="capture angle, object, texture, motion cue, props, and b-roll need")
    p.add_argument("--aspect", default="3:4")
    p.add_argument("--brand-context", default="")
    p.add_argument("--product-context", default="")
    args = p.parse_args()
    print(build_prompt(args))

if __name__ == "__main__":
    main()
