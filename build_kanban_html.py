#!/usr/bin/env python3
"""
Build script for Job Hunt Tracker.

Produces two files:
  JobHunt_Kanban.html  — your personal board, built from job_kanban/cards/*.json (gitignored)
  index.html           — public demo, built from job_kanban/card.example.json only (committed)

Card data lives in job_kanban/cards/*.json (one file per card, gitignored).
Board column config lives in job_kanban/columns.json (committed).

Usage:
  python build_kanban_html.py

To add a card: create a new .json file in job_kanban/cards/ and re-run.
See job_kanban/card.example.json for the expected field format.
"""

import json
import os
import glob

CARDS_DIR    = "job_kanban/cards"
EXAMPLE_CARD = "job_kanban/card.example.json"
COLUMNS_FILE = "job_kanban/columns.json"
HEAD_FILE    = "job_kanban/template_head.html"
TAIL_FILE    = "job_kanban/template_tail.html"
PERSONAL_OUT = "JobHunt_Kanban.html"
DEMO_OUT     = "index.html"


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


def build(output_path, cards, columns, head, tail):
    columns_js = f"const COLUMNS = {json.dumps(columns, ensure_ascii=False)};\n"
    cards_js   = f"const ORIGINAL_CARDS = {json.dumps(cards, ensure_ascii=False)};\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(head + columns_js + cards_js + tail)
    print(f"Built {output_path} ({len(cards)} cards, {len(columns)} columns)")


def main():
    with open(COLUMNS_FILE, encoding="utf-8") as f:
        columns = json.load(f)

    with open(HEAD_FILE, encoding="utf-8") as f:
        head = f.read()

    with open(TAIL_FILE, encoding="utf-8") as f:
        tail = f.read()

    # Personal build — all cards from job_kanban/cards/
    build(PERSONAL_OUT, load_cards(), columns, head, tail)

    # Demo build — example card only, safe to commit
    with open(EXAMPLE_CARD, encoding="utf-8") as f:
        example = json.load(f)
    build(DEMO_OUT, [example], columns, head, tail)


if __name__ == "__main__":
    main()
