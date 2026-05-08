"""Group env keys by prefix, tag, or custom rule."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    source: str
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def total_groups(self) -> int:
        return len(self.groups)

    def key_count(self) -> int:
        return sum(len(v) for v in self.groups.values()) + len(self.ungrouped)


def _extract_prefix(key: str, separator: str = "_") -> Optional[str]:
    """Return the first segment before the separator, or None."""
    if separator in key:
        return key.split(separator)[0]
    return None


def group_by_prefix(
    env: Dict[str, str],
    source: str = "<env>",
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupResult:
    """Group keys by their prefix (segment before the first separator)."""
    buckets: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for key in env:
        prefix = _extract_prefix(key, separator)
        if prefix:
            buckets.setdefault(prefix, []).append(key)
        else:
            ungrouped.append(key)

    groups = {p: sorted(keys) for p, keys in buckets.items() if len(keys) >= min_group_size}

    # keys whose prefix group was too small go to ungrouped
    for prefix, keys in buckets.items():
        if len(keys) < min_group_size:
            ungrouped.extend(keys)

    return GroupResult(source=source, groups=groups, ungrouped=sorted(ungrouped))


def group_by_custom(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
    source: str = "<env>",
) -> GroupResult:
    """Group keys using explicit rules mapping group_name -> list of key prefixes/exact keys."""
    assigned: set = set()
    groups: Dict[str, List[str]] = {}

    for group_name, patterns in rules.items():
        matched = [
            k for k in env
            if any(k == p or k.startswith(p + "_") for p in patterns)
        ]
        if matched:
            groups[group_name] = sorted(matched)
            assigned.update(matched)

    ungrouped = sorted(k for k in env if k not in assigned)
    return GroupResult(source=source, groups=groups, ungrouped=ungrouped)
