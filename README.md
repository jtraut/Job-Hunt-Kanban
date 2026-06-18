# Job Hunt Tracker

A kanban-style job application tracker that runs as a single HTML file — no server, no database, no dependencies.

**[Live Demo →](https://jtraut.github.io/Job-Hunt-Kanban/)**

---

## Features

- Drag cards between columns to update status
- Add, edit, and delete cards via a modal form
- **Auto-stale:** applied cards with no response in 3+ months move to Stale automatically
- **Auto-reject:** stale cards older than 6 months move to Rejected automatically
- Search across company, role, notes, salary, and location
- Notes per card (cover letter drafts, recruiter info, interview prep)
- **File-backed storage** (Chrome/Edge): connect your `job_kanban/` folder and cards save as individual JSON files in real time
- **localStorage fallback**: works in any browser without connecting a folder
- Export the full board to JSON at any time

---

## Quick start

```bash
git clone https://github.com/jtraut/Job-Hunt-Kanban.git
cd Job-Hunt-Kanban
open JobHunt_Kanban.html   # or just double-click it
```

That's it — no build step required. Start adding cards with the **+ New** button.

---

## Saving cards as files (optional, Chrome/Edge only)

By default cards are saved in `localStorage`. To save them as individual JSON files instead:

1. Click **Connect folder** in the header
2. Select the `job_kanban/` directory
3. Grant read/write access when prompted

From that point on, every add/edit/delete writes directly to files, organized into subdirectories:

```
job_kanban/
├── cards/        ← one JSON file per role
└── links/
    └── profile.json   ← your LinkedIn and personal site URLs
```

The folder stays connected across browser sessions. Any cards already in localStorage are migrated to files automatically on connect.

> **Why files?** Each card is a plain `.json` file you can read, edit, back up, or version-control independently. Both `cards/` and `links/` are gitignored so your personal data never appears on the public repo.

---

## Columns

| Column | Description |
|---|---|
| Saved | Roles to revisit later |
| Considering | Deciding whether to apply |
| Recruiter contact | Reached out via recruiter |
| Applied | Application submitted, waiting |
| Interview | Phone screen / interview in progress |
| Offer | Received an offer |
| Rejected | No further action |
| **Stale** | No response in 3+ months — auto-rejected after 6 months |
| Withdrawn | You withdrew your application |

Stale and auto-reject are derived from the card's application date with no manual action needed. Dragging a card to any column overrides the auto-placement.

---

## Customizing columns

Edit `job_kanban/columns.json`, then run `python build_kanban_html.py` to rebuild.

---

## Privacy

`job_kanban/cards/*.json` and `job_kanban/links/*.json` are in `.gitignore` and will never be committed. The HTML files committed to this repo contain no personal data — cards and profile links load at runtime from your connected folder or localStorage.
