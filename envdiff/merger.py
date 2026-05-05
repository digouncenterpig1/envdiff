"""Merge multiple .env files into a unified key set with source tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class MergedEnv:
    """Result of merging multiple env sources."""

    keys: Dict[str, str] = field(default_factory=dict)
    # maps key -> list of source labels that defined it
    sources: Dict[str, List[str]] = field(default_factory=dict)
    # keys that had conflicting values across sources
    conflicts: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)


def merge_env_files(
    paths: List[str],
    labels: Optional[List[str]] = None,
    strategy: str = "last",
) -> MergedEnv:
    """Merge env files from *paths*.

    Args:
        paths: Ordered list of file paths to merge.
        labels: Human-readable label for each path (defaults to the path itself).
        strategy: ``'last'`` keeps the last-seen value; ``'first'`` keeps the
                  first-seen value.  Conflicts are always recorded regardless.

    Returns:
        A :class:`MergedEnv` describing the merged result.
    """
    if labels is None:
        labels = list(paths)
    if len(labels) != len(paths):
        raise ValueError("labels length must match paths length")
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown strategy {strategy!r}; use 'first' or 'last'")

    merged = MergedEnv()

    for path, label in zip(paths, labels):
        env = parse_env_file(path)
        _apply(merged, env, label, strategy)

    return merged


def merge_env_strings(
    contents: List[str],
    labels: Optional[List[str]] = None,
    strategy: str = "last",
) -> MergedEnv:
    """Same as :func:`merge_env_files` but accepts raw env strings."""
    if labels is None:
        labels = [f"source_{i}" for i in range(len(contents))]
    if len(labels) != len(contents):
        raise ValueError("labels length must match contents length")
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown strategy {strategy!r}; use 'first' or 'last'")

    merged = MergedEnv()

    for content, label in zip(contents, labels):
        env = parse_env_string(content)
        _apply(merged, env, label, strategy)

    return merged


def _apply(
    merged: MergedEnv,
    env: Dict[str, str],
    label: str,
    strategy: str,
) -> None:
    for key, value in env.items():
        merged.sources.setdefault(key, [])
        merged.sources[key].append(label)

        if key in merged.keys and merged.keys[key] != value:
            merged.conflicts.setdefault(key, {merged.sources[key][0]: merged.keys[key]})
            merged.conflicts[key][label] = value

        if key not in merged.keys or strategy == "last":
            merged.keys[key] = value
