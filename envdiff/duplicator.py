"""Detect duplicate values across keys in an env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateResult:
    source: str
    # value -> list of keys that share it
    duplicates: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    @property
    def total_groups(self) -> int:
        return len(self.duplicates)

    @property
    def affected_keys(self) -> List[str]:
        keys: List[str] = []
        for ks in self.duplicates.values():
            keys.extend(ks)
        return keys


def find_duplicates(
    env: Dict[str, str],
    source: str = "<env>",
    ignore_empty: bool = True,
) -> DuplicateResult:
    """Return a DuplicateResult mapping shared values to the keys that hold them.

    Args:
        env: Parsed key/value mapping.
        source: Label used in reporting.
        ignore_empty: When True, empty string values are not considered duplicates.
    """
    value_map: Dict[str, List[str]] = {}
    for key, value in env.items():
        if ignore_empty and value == "":
            continue
        value_map.setdefault(value, []).append(key)

    duplicates = {v: ks for v, ks in value_map.items() if len(ks) > 1}
    return DuplicateResult(source=source, duplicates=duplicates)


def find_duplicates_in_file(path: str, ignore_empty: bool = True) -> DuplicateResult:
    """Parse *path* and return duplicate-value groups."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return find_duplicates(env, source=path, ignore_empty=ignore_empty)
