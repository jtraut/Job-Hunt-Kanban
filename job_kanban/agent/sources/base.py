"""Pluggable job-source interface.

Add your own job-board integrations by subclassing JobSource and returning
a list of raw role dicts. The runner normalizes, dedupes, tags, and writes
them as Kanban cards, so a source only has to *find* roles.

A returned role should be a dict with as many of these keys as available:
    company, role, salary, location, link, tags, notes

Anything missing is fine — the runner fills sensible defaults.
"""

from __future__ import annotations

from typing import Any


class JobSource:
    """Base class for a job source. Subclass and implement search()."""

    #: short identifier, also the key used in config.sources.pluggable_api_keys
    name: str = "base"

    def __init__(self, config: dict[str, Any], credentials: dict[str, Any] | None = None):
        self.config = config
        self.credentials = credentials or {}

    def search(self) -> list[dict[str, Any]]:
        """Return a list of raw role dicts matching the user's config.

        Implementations should honor self.config: tracks, salary, location
        (modes + base), seniority, and exclusions. Returning [] is valid —
        the runner falls back to Claude web search to make up the difference.
        """
        raise NotImplementedError
