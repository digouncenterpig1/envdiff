"""Trim unused or redundant keys from an env dict based on a reference set."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class TrimResult:
    source: str
    original: Dict[str, str]
    trimmed: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)

    @property
    def has_removals(self) -> bool:
        return len(self.removed_keys) > 0

    @property
    def removal_count(self) -> int:
        return len(self.removed_keys)

    def as_env_string(self) -> str:
        lines = [f"{k}={v}" for k, v in self.trimmed.items()]
        return "\n".join(lines)


def trim_to_reference(
    env: Dict[str, str],
    reference: Dict[str, str],
    source: str = "<env>",
) -> TrimResult:
    """Remove keys from *env* that are not present in *reference*."""
    ref_keys: Set[str] = set(reference.keys())
    trimmed: Dict[str, str] = {}
    removed: List[str] = []

    for key, value in env.items():
        if key in ref_keys:
            trimmed[key] = value
        else:
            removed.append(key)

    return TrimResult(
        source=source,
        original=dict(env),
        trimmed=trimmed,
        removed_keys=sorted(removed),
    )


def trim_keys(
    env: Dict[str, str],
    keys_to_remove: List[str],
    source: str = "<env>",
) -> TrimResult:
    """Explicitly remove a list of keys from *env*."""
    remove_set: Set[str] = set(keys_to_remove)
    trimmed: Dict[str, str] = {}
    removed: List[str] = []

    for key, value in env.items():
        if key in remove_set:
            removed.append(key)
        else:
            trimmed[key] = value

    return TrimResult(
        source=source,
        original=dict(env),
        trimmed=trimmed,
        removed_keys=sorted(removed),
    )
