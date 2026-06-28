# Auto job-fetcher

Finds new job postings that match your preferences and drops them onto the
board as cards (in the column you choose), on a schedule. Works two ways:

- **Standalone** — a Python script + your OS scheduler. No Claude Cowork needed,
  just an Anthropic API key. This is the path most people will use.
- **Cowork** — run it as a Claude Cowork scheduled task instead. See
  `cowork_task_template.md`.

Generated cards are tagged **AI** (and **startup** when the company is
venture-backed), so you can always tell which roles the agent added.

## What's here

| File | Purpose |
|------|---------|
| `config.example.json` | Template preferences. Your real copy is `config.json` (gitignored). |
| `fetch_roles.py` | The runner: finds roles and writes cards. |
| `install_schedule.py` | Registers a cron job (macOS/Linux) or Task Scheduler task (Windows). |
| `sources/` | Pluggable job-source adapters. Add your own API-backed boards here. |
| `cowork_task_template.md` | Prompt for running it inside Claude Cowork instead. |
| `.env.example` | Where your `ANTHROPIC_API_KEY` goes (copy to `.env`). |

## Setup (standalone)

1. **Install the dependency**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your API key**
   ```bash
   cp .env.example .env      # then edit .env and paste your key
   ```
   Get a key at <https://console.anthropic.com/>.

3. **Set your preferences** — open the board (`JobHunt_Kanban.html`), connect
   your folder, and click **⚙ Agent**. Saving writes `agent/config.json`.
   (Or copy `config.example.json` to `config.json` and edit by hand.) Set
   `enabled: true` to turn it on.

4. **Try it once**
   ```bash
   python fetch_roles.py --dry-run    # shows picks, writes nothing
   python fetch_roles.py              # writes the cards
   ```

5. **Schedule it**
   ```bash
   python install_schedule.py         # preview the schedule
   python install_schedule.py --apply # install it
   ```
   It uses the `schedule` (time + days) from your config. Remove it later with
   `python install_schedule.py --remove`.

## Preferences (`config.json`)

| Field | Meaning |
|-------|---------|
| `enabled` | Master on/off switch. |
| `roles_per_day` | How many new cards to add per run. |
| `schedule.time` / `schedule.days` | When to run (24h local time; weekdays default Mon–Fri). |
| `tracks` | Role types to look for. |
| `salary.min` / `salary.max` | Target band (USD). |
| `location.modes` | Any of `remote`, `hybrid`, `onsite`. |
| `location.base` | City for hybrid/on-site searches. |
| `exclusions` | Things to avoid (e.g. clearance-required roles). |
| `sources.startup_boards` | Boards to prioritize via web search. |
| `sources.pluggable_api_keys` | Credentials for custom `sources/` adapters. |
| `sources.use_cowork_connectors` | Use Cowork job connectors when run inside Cowork. |
| `notes` | Free-text guidance passed to the model. |
| `target_column` | Which board column new cards land in (default `saved`). |

## Adding your own job source

The default source is Claude web search (zero setup). To plug in a board with
its own API, copy `sources/example_source.py`, implement `search()`, register it
in `sources/__init__.py`, and add its credentials under
`sources.pluggable_api_keys` in your config. If a source returns nothing, the
runner tops up the rest with web search automatically.

## Notes

- `config.json`, `.env`, and `agent_run.log` are gitignored — your preferences
  and key never get committed.
- The runner dedupes against everything already in `cards.json`, so it won't
  re-add roles you've already saved, applied to, or rejected.
