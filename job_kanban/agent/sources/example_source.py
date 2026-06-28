"""Example pluggable source — copy this to build your own.

To enable a custom source:
  1. Copy this file (e.g. to `indeed_source.py`) and implement search().
  2. Register it in REGISTRY below (or in sources/__init__.py).
  3. Add an entry under config.sources.pluggable_api_keys, e.g.
       "pluggable_api_keys": { "example": { "api_key": "..." } }
     The matching key name selects which sources are active.

If no pluggable source is configured or a source returns nothing, the runner
falls back to Claude web search automatically.
"""

from __future__ import annotations

from typing import Any

from .base import JobSource


class ExampleSource(JobSource):
    name = "example"

    def search(self) -> list[dict[str, Any]]:
        # Replace this with a real API call using self.credentials["api_key"]
        # and filters drawn from self.config. Returning [] is a valid no-op.
        return []
