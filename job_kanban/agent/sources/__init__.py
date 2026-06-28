"""Source registry. Activates pluggable sources named in
config.sources.pluggable_api_keys; everything else falls back to web search.
"""

from __future__ import annotations

from typing import Any

from .base import JobSource
from .example_source import ExampleSource

# Map a config key -> JobSource subclass. Add your own here.
REGISTRY: dict[str, type[JobSource]] = {
    "example": ExampleSource,
}


def load_sources(config: dict[str, Any]) -> list[JobSource]:
    """Instantiate every configured pluggable source that we have an adapter for."""
    creds_by_name = (config.get("sources") or {}).get("pluggable_api_keys") or {}
    sources: list[JobSource] = []
    for name, creds in creds_by_name.items():
        cls = REGISTRY.get(name)
        if cls is None:
            print(f"[sources] no adapter registered for '{name}' — skipping")
            continue
        sources.append(cls(config, creds))
    return sources
