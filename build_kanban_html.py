#!/usr/bin/env python3
"""
Build script for Job Hunt Tracker.

Produces two files:
  index.html           — public demo, built from job_kanban/demo/*.json (committed)
  JobHunt_Kanban.html  — always built with ORIGINAL_CARDS=[] (committed, safe to share)
                         Cards are loaded at runtime via the File System Access API
                         or localStorage — no personal data baked in.

Run this script when you change templates, columns, or demo cards.
For day-to-day personal use, just open JobHunt_Kanban.html and use "Connect folder".
"""

import json
import os
import glob

CARDS_DIR    = "job_kanban/cards"
DEMO_DIR     = "job_kanban/demo"
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

    # Personal build — always empty ORIGINAL_CARDS; cards load at runtime via UI
    build(PERSONAL_OUT, [], columns, head, tail)

    # Demo build — demo cards only, safe to commit
    demo_paths = sorted(glob.glob(os.path.join(DEMO_DIR, "*.json")))
    demo_cards = []
    for p in demo_paths:
        with open(p, encoding="utf-8") as f:
            demo_cards.append(json.load(f))
    build(DEMO_OUT, demo_cards, columns, head, tail)


if __name__ == "__main__":
    main()
