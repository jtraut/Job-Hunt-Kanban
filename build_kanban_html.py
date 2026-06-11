#!/usr/bin/env python3
"""
Build JobHunt_Kanban.html from templates + card data.

Card data lives in job_kanban/cards/*.json (one file per card).
Board column config lives in job_kanban/columns.json.
These are gitignored so your personal job hunt stays private.

Usage:
  python build_kanban_html.py

To add a card: create a new .json file in job_kanban/cards/ and re-run.
See job_kanban/card.example.json for the expected field format.
"""

import json
import os
import glob

CARDS_DIR   = "job_kanban/cards"
COLUMNS_FILE = "job_kanban/columns.json"
HEAD_FILE   = "job_kanban/template_head.html"
TAIL_FILE   = "job_kanban/template_tail.html"
OUTPUT_FILE = "JobHunt_Kanban.html"


def load_cards():
    paths = sorted(glob.glob(os.path.join(CARDS_DIR, "*.json")))
    if not paths:
        print(f"Warning: no card files found in {CARDS_DIR}/")
        print("  Copy job_kanban/card.example.json to job_kanban/cards/<id>.json to get started.")
        return []
    cards = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            cards.append(json.load(f))
    return cards


def main():
    with open(COLUMNS_FILE, encoding="utf-8") as f:
        columns = json.load(f)

    cards = load_cards()

    with open(HEAD_FILE, encoding="utf-8") as f:
        head = f.read()

    with open(TAIL_FILE, encoding="utf-8") as f:
        tail = f.read()

    columns_js = f"const COLUMNS = {json.dumps(columns, ensure_ascii=False)};\n"
    cards_js   = f"const ORIGINAL_CARDS = {json.dumps(cards, ensure_ascii=False)};\n"

    output = head + columns_js + cards_js + tail

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Built {OUTPUT_FILE} ({len(cards)} cards, {len(columns)} columns)")


if __name__ == "__main__":
    main()
