"""Scope filtering: restrict env keys to a named scope (prefix group)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    source: str
    scope: str
    matched: Dict[str, str] = field(default_factory=dict)
    unmatched: Dict[str, str] = field(default_factory=dict)

    @property
    def match_count(self) -> int:
        return len(self.matched)

    @property
    def unmatched_count(self) -> int:
        return len(self.unmatched)

    @property
    def has_matches(self) -> bool:
        return bool(self.matched)

    def stripped_keys(self, separator: str = "_") -> Dict[str, str]:
        """Return matched keys with the scope prefix (and separator) removed."""
        prefix = self.scope.rstrip(separator) + separator
        return {
            (k[len(prefix):] if k.upper().startswith(prefix.upper()) else k): v
            for k, v in self.matched.items()
        }


def scope_env(
    env: Dict[str, str],
    scope: str,
    source: str = "<env>",
    separator: str = "_",
    case_sensitive: bool = False,
) -> ScopeResult:
    """Split *env* into keys that belong to *scope* and those that don't.

    A key belongs to *scope* when it starts with ``scope + separator``
    (e.g. scope="DB", separator="_" matches "DB_HOST", "DB_PORT").
    """
    prefix = scope.rstrip(separator) + separator
    matched: Dict[str, str] = {}
    unmatched: Dict[str, str] = {}

    for key, value in env.items():
        candidate = key if case_sensitive else key.upper()
        needle = prefix if case_sensitive else prefix.upper()
        if candidate.startswith(needle):
            matched[key] = value
        else:
            unmatched[key] = value

    return ScopeResult(
        source=source,
        scope=scope,
        matched=matched,
        unmatched=unmatched,
    )


def available_scopes(
    env: Dict[str, str],
    separator: str = "_",
) -> List[str]:
    """Return a sorted list of unique top-level prefix scopes found in *env*."""
    scopes: set = set()
    for key in env:
        parts = key.split(separator, 1)
        if len(parts) == 2 and parts[0]:
            scopes.add(parts[0].upper())
    return sorted(scopes)
