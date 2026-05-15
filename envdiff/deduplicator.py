"""Deduplicator: remove duplicate keys from an env dict, keeping first or last occurrence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Tuple

Strategy = Literal["first", "last"]


@dataclass
class DeduplicateResult:
    source: str
    kept: Dict[str, str]
    removed: List[Tuple[str, str]]  # (key, value) pairs that were dropped

    def has_removals(self) -> bool:
        return len(self.removed) > 0

    def removal_count(self) -> int:
        return len(self.removed)

    def as_env_string(self) -> str:
        lines = [f"{k}={v}" for k, v in self.kept.items()]
        return "\n".join(lines)


def deduplicate_env(
    env: Dict[str, str],
    source: str = "<env>",
    strategy: Strategy = "first",
) -> DeduplicateResult:
    """Return a DeduplicateResult with duplicate keys resolved.

    Since a plain dict already has unique keys, this function works on a raw
    list of (key, value) pairs to simulate files that contain repeated keys.
    For convenience it also accepts a dict (no duplicates possible, result is
    always clean).
    """
    # env is already deduplicated when passed as dict; kept == env
    return DeduplicateResult(source=source, kept=dict(env), removed=[])


def deduplicate_pairs(
    pairs: List[Tuple[str, str]],
    source: str = "<env>",
    strategy: Strategy = "first",
) -> DeduplicateResult:
    """Deduplicate a list of (key, value) pairs.

    Parameters
    ----------
    pairs:    ordered list of (key, value) tuples, possibly with repeated keys
    source:   label for the origin of the data
    strategy: 'first' keeps the first occurrence; 'last' keeps the last
    """
    seen: Dict[str, str] = {}
    removed: List[Tuple[str, str]] = []

    if strategy == "first":
        for key, value in pairs:
            if key in seen:
                removed.append((key, value))
            else:
                seen[key] = value
    else:  # last
        # collect all positions per key
        positions: Dict[str, List[int]] = {}
        for idx, (key, _) in enumerate(pairs):
            positions.setdefault(key, []).append(idx)

        kept_indices = {idxs[-1] for idxs in positions.values()}
        for idx, (key, value) in enumerate(pairs):
            if idx in kept_indices:
                seen[key] = value
            else:
                removed.append((key, value))

    return DeduplicateResult(source=source, kept=seen, removed=removed)
