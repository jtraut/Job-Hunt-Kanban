# Cowork scheduled-task template — auto job-fetcher

This is the prompt for running the job-fetcher **inside Claude Cowork** as a
scheduled task (an alternative to the standalone `fetch_roles.py` + OS scheduler).
It contains **no personal preferences** — those live in `agent/config.json`,
which the task reads at run time.

## How to use it
In Cowork, ask Claude to create a scheduled task and paste the prompt below.
Set the cron schedule to match the `schedule` in your `agent/config.json`
(e.g. `0 8 * * 1-5` for 08:00 Mon–Fri). Point the task at your local repo path.

---

## Task prompt (copy below this line)

You are a daily job-search agent for the Job Hunt Tracker repo at `<REPO_PATH>`.

1. Read preferences from `<REPO_PATH>/job_kanban/agent/config.json`. If
   `enabled` is false, stop and do nothing. Use these fields: `roles_per_day`,
   `tracks`, `salary` (min/max), `location` (modes + base), `seniority`,
   `exclusions`, `sources.startup_boards`, `sources.use_cowork_connectors`,
   `notes`, and `target_column`.

2. Find `roles_per_day` NEW roles matching ALL preferences:
   - If `sources.use_cowork_connectors` is true, prefer connected job
     connectors (Indeed / Dice / ZipRecruiter `search_jobs`) for direct
     per-posting links and salary data. Search each track separately, once for
     Remote and once for the base city if `hybrid` is in modes.
   - Also use the boards in `sources.startup_boards` via web search
     (`allowed_domains`), preferring specific postings over landing pages.
   - Fall back to general web search, preferring direct ATS links
     (greenhouse.io, lever.co, ashbyhq.com, company careers pages).

3. Dedupe: read `<REPO_PATH>/job_kanban/cards.json` and skip any role whose
   company + similar title already exists in ANY column.

4. Save each new role as a card in BOTH `job_kanban/cards/<id>.json` and the
   `job_kanban/cards.json` array, using a unique 10-char hex id. Schema matches
   `job_kanban/card.example.json`. Set:
   - `date` = today (M/D/YY), `status_label` = the target column's label,
     `column` = `target_column`.
   - `tags`: ALWAYS include `"AI"` (uppercase). Also include `"startup"` for
     venture-backed / early-stage companies. (Stored uppercase "AI" so the
     board renders it "AI", not "Ai".)
   Implement with a single Python script so `cards.json` stays valid JSON.

5. Post a short summary: each role as company — role — salary — location — tags,
   with its link and which track it covers. If fewer than `roles_per_day`
   genuinely fit, say so rather than padding.
