# Job Hunt Tracker

A kanban-style job application tracker that runs as a single HTML file — no server, no database, no dependencies.

**[Live Demo →](https://jtraut.github.io/Job-Hunt-Kanban/)**

![Board columns: Saved, Considering, Recruiter, Applied, Interview, Offer, Rejected, Withdrawn](https://img.shields.io/badge/columns-8-blue)

---

## Features

- Drag cards between columns to update status
- Add, edit, and delete cards via a modal form
- Search across company, role, notes, salary, and location
- Notes per card (cover letter drafts, recruiter info, interview prep)
- All state persisted in `localStorage` — no data leaves your browser
- Export the full board to JSON at any time

---

## Using it locally

### 1. Clone the repo

```bash
git clone https://github.com/jtraut/Job-Hunt-Kanban.git
cd Job-Hunt-Kanban
```

### 2. Add your own cards

Each card is a `.json` file in `job_kanban/cards/`. Copy the example to get started:

```bash
cp job_kanban/card.example.json job_kanban/cards/my-first-job.json
```

Edit the file with your job details:

```json
{
  "id": "abc123def4",
  "company": "Acme Corp",
  "role": "Senior Software Engineer",
  "date": "6/1/26",
  "salary": "150-180K",
  "location": "Remote",
  "link": "https://example.com/jobs/12345",
  "notes": "Cover letter sent. Recruiter: Jane Smith.",
  "status_label": "Applied",
  "column": "applied"
}
```

> **`id`** — any unique string; `python -c "import uuid; print(uuid.uuid4().hex[:10])"` generates one.  
> **`column`** — one of: `saved`, `considering`, `recruiter`, `applied`, `interview`, `offer`, `rejected`, `withdrawn`

### 3. Build the HTML

```bash
python build_kanban_html.py
```

This produces two files:
- `JobHunt_Kanban.html` — your personal board with all your cards (gitignored)
- `index.html` — the public demo, rebuilt from `card.example.json` only (committed)

### 4. Open in your browser

```bash
open JobHunt_Kanban.html        # macOS
start JobHunt_Kanban.html       # Windows
xdg-open JobHunt_Kanban.html   # Linux
```

No server needed — open the file directly.

---

## Customizing columns

Edit `job_kanban/columns.json` to rename, recolor, or add columns, then rebuild.

---

## Privacy

Your card files (`job_kanban/cards/*.json`) are listed in `.gitignore` and will never be committed. Only the templates, build script, and columns config are tracked.
