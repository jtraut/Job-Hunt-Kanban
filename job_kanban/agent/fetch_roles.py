#!/usr/bin/env python3
"""Auto job-fetcher for the Job Hunt Tracker.

Reads preferences from job_kanban/links/agent_config.json (set them in the
board's "Agent" settings panel, or copy agent/config.example.json), finds N
matching roles, and writes them as Kanban cards in the configured column.

Job sources, in order:
  1. Any pluggable sources configured in config.sources.pluggable_api_keys
     (see agent/sources/). These typically use your own job-board API keys.
  2. Claude web search — the zero-setup fallback. Always used to top up to
     `roles_per_day` if the pluggable sources don't return enough.

Requires an Anthropic API key in the ANTHROPIC_API_KEY environment variable
(a .env file in agent/ or the repo root is loaded automatically).

Usage:
  python fetch_roles.py            # find roles and write cards
  python fetch_roles.py --dry-run  # print what it would add, write nothing
  python fetch_roles.py --count 5  # override roles_per_day for this run
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import secrets
import sys
from pathlib import Path
from typing import Any

# job_kanban/ — parent of this agent/ directory
AGENT_DIR = Path(__file__).resolve().parent
ROOT = AGENT_DIR.parent  # job_kanban/
CARDS_DIR = ROOT / "cards"
CARDS_JSON = ROOT / "cards.json"
CONFIG_PATH = AGENT_DIR / "config.json"
EXAMPLE_CONFIG = AGENT_DIR / "config.example.json"

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")


# ── tiny .env loader (no dependency) ──────────────────────────────────────
def load_dotenv() -> None:
    for candidate in (AGENT_DIR / ".env", ROOT.parent / ".env"):
        if not candidate.exists():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


# ── config ────────────────────────────────────────────────────────────────
def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"No config found at {CONFIG_PATH}.\n"
            f"Set your preferences in the board's 'Agent' panel, or copy\n"
            f"  {EXAMPLE_CONFIG}\n"
            f"to {CONFIG_PATH} and edit it."
        )
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in cfg.items() if not k.startswith("_")}


# ── existing cards / dedupe ───────────────────────────────────────────────
def load_existing() -> tuple[list[dict[str, Any]], set[str], set[str]]:
    cards: list[dict[str, Any]] = []
    if CARDS_JSON.exists():
        try:
            cards = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cards = []
    ids = {c.get("id") for c in cards}
    keys = {_dedupe_key(c.get("company", ""), c.get("role", "")) for c in cards}
    return cards, ids, keys


def _dedupe_key(company: str, role: str) -> str:
    norm = lambda s: re.sub(r"[^a-z0-9]+", "", (s or "").lower())
    return norm(company) + "|" + norm(role)


# ── salary formatting ─────────────────────────────────────────────────────
def salary_label(cfg: dict[str, Any]) -> str:
    s = cfg.get("salary") or {}
    lo, hi = s.get("min"), s.get("max")
    if lo and hi:
        return f"${lo // 1000}K-${hi // 1000}K"
    return ""


# ── prompt for the Claude web-search pass ─────────────────────────────────
def build_prompt(cfg: dict[str, Any], needed: int, existing: list[dict[str, Any]]) -> str:
    loc = cfg.get("location") or {}
    modes = ", ".join(loc.get("modes") or ["remote"])
    base = loc.get("base") or ""
    tracks = "\n".join(f"  - {t}" for t in (cfg.get("tracks") or []))
    exclusions = "\n".join(f"  - {e}" for e in (cfg.get("exclusions") or [])) or "  - (none)"
    boards = ", ".join((cfg.get("sources") or {}).get("startup_boards") or [])
    # Only send recent company+role pairs to keep the prompt small
    recent = [f"{c.get('company','')} — {c.get('role','')}" for c in existing[-60:]]
    avoid = "\n".join(f"  - {r}" for r in recent) or "  - (none yet)"

    return f"""You are a job-search assistant. Find {needed} NEW job postings that match ALL of these criteria, using web search.

ROLE TRACKS (any one of these qualifies; aim for a spread across them):
{tracks}

LOCATION: {modes}{(' — base city ' + base) if base else ''}
SALARY: roughly {salary_label(cfg) or 'open'} (if a posting lists no salary, it's still acceptable when the rest fits — leave salary blank)
SENIORITY: {cfg.get('seniority', 'senior')} individual-contributor level (not management, not entry/mid)

EXCLUDE:
{exclusions}

PREFER these startup boards and direct ATS links (greenhouse.io, lever.co, ashbyhq.com, company careers pages) over aggregator landing pages:
  {boards}

DO NOT return any of these already-tracked roles:
{avoid}

Extra preferences: {cfg.get('notes', '')}

Search the web, then output ONLY a JSON array of exactly {needed} objects (no prose before or after), each:
{{
  "company": "Company Name",
  "role": "Exact posting title",
  "salary": "150-190K or empty string",
  "location": "Remote / Denver hybrid / etc.",
  "link": "https://direct-posting-url",
  "tags": ["startup"],   // include "startup" only for venture-backed/early-stage companies; else []
  "notes": "Which track it fits + one line on why."
}}
Wrap the array in a ```json code fence."""


# ── Claude web-search source ──────────────────────────────────────────────
def claude_web_search(cfg: dict[str, Any], needed: int, existing: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        import anthropic
    except ImportError:
        sys.exit("The 'anthropic' package is required. Run: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY is not set. Put it in agent/.env or your environment.")

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=4096,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
        messages=[{"role": "user", "content": build_prompt(cfg, needed, existing)}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return parse_cards(text)


def parse_cards(text: str) -> list[dict[str, Any]]:
    m = re.search(r"```json\s*(.*?)```", text, re.S) or re.search(r"(\[.*\])", text, re.S)
    if not m:
        print("[warn] could not find a JSON array in the model response")
        return []
    try:
        data = json.loads(m.group(1).strip())
    except json.JSONDecodeError as e:
        print(f"[warn] JSON parse failed: {e}")
        return []
    return data if isinstance(data, list) else []


# ── normalize + write ─────────────────────────────────────────────────────
def make_card(raw: dict[str, Any], cfg: dict[str, Any], existing_ids: set[str]) -> dict[str, Any]:
    while True:
        cid = secrets.token_hex(5)
        if cid not in existing_ids:
            existing_ids.add(cid)
            break
    today = dt.date.today()
    date_str = f"{today.month}/{today.day}/{today.strftime('%y')}"
    column = cfg.get("target_column", "saved")
    label = {"saved": "Saved", "considering": "Considering", "applied": "Applied"}.get(column, column.title())
    tags = raw.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    # Every agent-generated card is marked with an "AI" tag (stored uppercase so
    # the board's capitalize styling renders it "AI", not "Ai").
    if "ai" not in [t.lower() for t in tags]:
        tags = tags + ["AI"]
    return {
        "id": cid,
        "company": (raw.get("company") or "").strip(),
        "role": (raw.get("role") or "").strip(),
        "date": date_str,
        "salary": (raw.get("salary") or "").strip(),
        "location": (raw.get("location") or "").strip(),
        "link": (raw.get("link") or "").strip(),
        "tags": tags,
        "notes": (raw.get("notes") or "").strip(),
        "status_label": label,
        "column": column,
    }


def write_cards(new_cards: list[dict[str, Any]], all_cards: list[dict[str, Any]]) -> None:
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    for c in new_cards:
        (CARDS_DIR / f"{c['id']}.json").write_text(
            json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    all_cards.extend(new_cards)
    CARDS_JSON.write_text(json.dumps(all_cards, indent=2, ensure_ascii=False), encoding="utf-8")


# ── main ──────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description="Find new roles and add them as Kanban cards.")
    ap.add_argument("--dry-run", action="store_true", help="print results without writing")
    ap.add_argument("--count", type=int, help="override roles_per_day for this run")
    args = ap.parse_args()

    load_dotenv()
    cfg = load_config()
    if not cfg.get("enabled", False):
        print("Agent is disabled (set enabled: true in the config to run). Exiting.")
        return

    needed = args.count or int(cfg.get("roles_per_day", 3))
    existing, existing_ids, existing_keys = load_existing()

    # 1) pluggable sources
    from sources import load_sources

    gathered: list[dict[str, Any]] = []
    for src in load_sources(cfg):
        try:
            found = src.search() or []
            print(f"[source:{src.name}] returned {len(found)} roles")
            gathered.extend(found)
        except Exception as e:  # a bad source must not kill the run
            print(f"[source:{src.name}] error: {e}")

    # 2) web-search fallback to top up
    remaining = needed - len(gathered)
    if remaining > 0:
        gathered.extend(claude_web_search(cfg, remaining, existing))

    # normalize + dedupe (against board AND within this batch)
    new_cards: list[dict[str, Any]] = []
    for raw in gathered:
        if not (raw.get("company") and raw.get("role")):
            continue
        key = _dedupe_key(raw.get("company", ""), raw.get("role", ""))
        if key in existing_keys:
            continue
        existing_keys.add(key)
        new_cards.append(make_card(raw, cfg, existing_ids))
        if len(new_cards) >= needed:
            break

    if not new_cards:
        print("No new matching roles found today.")
        return

    print(f"\nFound {len(new_cards)} new role(s):")
    for c in new_cards:
        tag = f" [{', '.join(c['tags'])}]" if c["tags"] else ""
        print(f"  • {c['company']} — {c['role']} — {c['salary'] or 'salary n/a'} — {c['location']}{tag}")
        print(f"    {c['link']}")

    if args.dry_run:
        print("\n(--dry-run: nothing written)")
        return

    write_cards(new_cards, existing)
    print(f"\nWrote {len(new_cards)} card(s) to {CARDS_DIR} and updated {CARDS_JSON.name}.")


if __name__ == "__main__":
    main()
