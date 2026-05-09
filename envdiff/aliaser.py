"""Key aliasing — map old key names to new ones and detect stale aliases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasResult:
    source: str
    aliases: Dict[str, str]          # old_key -> new_key
    resolved: Dict[str, str]         # new_key -> value (from env)
    stale: List[str]                 # alias targets missing from env
    unknown: List[str]               # alias sources not in mapping

    def has_stale(self) -> bool:
        return bool(self.stale)

    def total_resolved(self) -> int:
        return len(self.resolved)


def apply_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
    source: str = "<env>",
) -> AliasResult:
    """Resolve aliases against *env*.

    For each ``old -> new`` alias pair:
    - If *new* exists in env, record it as resolved.
    - If *new* is absent, record it as stale.
    Keys in *env* that have no alias entry are collected as *unknown*.
    """
    resolved: Dict[str, str] = {}
    stale: List[str] = []

    for old, new in aliases.items():
        if new in env:
            resolved[new] = env[new]
        else:
            stale.append(new)

    aliased_sources = set(aliases.keys())
    unknown = [k for k in env if k not in aliased_sources]

    return AliasResult(
        source=source,
        aliases=aliases,
        resolved=resolved,
        stale=stale,
        unknown=unknown,
    )


def load_aliases(mapping: Dict[str, str]) -> Dict[str, str]:
    """Validate and return an alias mapping (old -> new)."""
    cleaned: Dict[str, str] = {}
    for old, new in mapping.items():
        old, new = old.strip(), new.strip()
        if old and new:
            cleaned[old] = new
    return cleaned
