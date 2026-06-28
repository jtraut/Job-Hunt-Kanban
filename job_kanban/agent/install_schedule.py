#!/usr/bin/env python3
"""Register the auto job-fetcher with your OS scheduler, using the time and
days from agent_config.json.

  - macOS / Linux  -> a crontab line
  - Windows        -> a Task Scheduler (schtasks) task

By default this PRINTS the command so you can review it. Add --apply to
actually install it.

  python install_schedule.py            # show what would be scheduled
  python install_schedule.py --apply    # actually schedule it
  python install_schedule.py --remove   # remove the scheduled job
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent
ROOT = AGENT_DIR.parent
CONFIG_PATH = AGENT_DIR / "config.json"
RUNNER = AGENT_DIR / "fetch_roles.py"
TASK_NAME = "JobHuntFetcher"

CRON_DAY = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}
WIN_DAY = {"mon": "MON", "tue": "TUE", "wed": "WED", "thu": "THU", "fri": "FRI", "sat": "SAT", "sun": "SUN"}


def load_schedule() -> tuple[int, int, list[str]]:
    if not CONFIG_PATH.exists():
        sys.exit(f"No config at {CONFIG_PATH}. Set your preferences first.")
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    sched = cfg.get("schedule") or {}
    hh, mm = (sched.get("time") or "08:00").split(":")
    days = [d.lower()[:3] for d in (sched.get("days") or ["mon", "tue", "wed", "thu", "fri"])]
    return int(hh), int(mm), days


def python_exe() -> str:
    return sys.executable or "python3"


# ── unix ──────────────────────────────────────────────────────────────────
def cron_line(hh: int, mm: int, days: list[str]) -> str:
    dow = ",".join(str(CRON_DAY[d]) for d in days)
    return f"{mm} {hh} * * {dow} cd {AGENT_DIR} && {python_exe()} {RUNNER} >> {AGENT_DIR / 'agent_run.log'} 2>&1 # {TASK_NAME}"


def unix_apply(line: str, remove: bool) -> None:
    try:
        current = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    except FileNotFoundError:
        sys.exit("crontab not found on this system.")
    kept = [ln for ln in current.splitlines() if TASK_NAME not in ln]
    if not remove:
        kept.append(line)
    new = "\n".join(kept) + "\n"
    subprocess.run(["crontab", "-"], input=new, text=True, check=True)
    print("Removed." if remove else "Installed cron job:\n  " + line)


# ── windows ────────────────────────────────────────────────────────────────
def win_apply(hh: int, mm: int, days: list[str], remove: bool) -> None:
    if remove:
        subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], check=False)
        print("Removed (if it existed).")
        return
    dows = ",".join(WIN_DAY[d] for d in days)
    cmd = [
        "schtasks", "/Create", "/F", "/TN", TASK_NAME,
        "/SC", "WEEKLY", "/D", dows,
        "/ST", f"{hh:02d}:{mm:02d}",
        "/TR", f'cmd /c cd /d "{AGENT_DIR}" && "{python_exe()}" "{RUNNER}" >> "{AGENT_DIR / "agent_run.log"}" 2>&1',
    ]
    subprocess.run(cmd, check=True)
    print(f"Installed Task Scheduler task '{TASK_NAME}'.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually install the schedule")
    ap.add_argument("--remove", action="store_true", help="remove the scheduled job")
    args = ap.parse_args()

    hh, mm, days = load_schedule()
    system = platform.system()
    print(f"Schedule: {hh:02d}:{mm:02d} on {', '.join(days)}  (detected OS: {system})\n")

    if system == "Windows":
        if args.apply or args.remove:
            win_apply(hh, mm, days, args.remove)
        else:
            dows = ",".join(WIN_DAY[d] for d in days)
            print("Would run (use --apply to install):")
            print(f'  schtasks /Create /F /TN {TASK_NAME} /SC WEEKLY /D {dows} '
                  f'/ST {hh:02d}:{mm:02d} /TR "...fetch_roles.py"')
    else:
        line = cron_line(hh, mm, days)
        if args.apply or args.remove:
            unix_apply(line, args.remove)
        else:
            print("Would add this crontab line (use --apply to install):")
            print("  " + line)


if __name__ == "__main__":
    main()
