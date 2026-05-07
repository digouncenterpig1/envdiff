"""Key ignore rules: load ignore patterns from a file or list and filter diff results."""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterable

from envdiff.comparator import DiffResult


def load_ignore_patterns(path: str | Path) -> list[str]:
    """Read ignore patterns from a file (one pattern per line, # = comment)."""
    patterns: list[str] = []
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def _matches_any(key: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(key, p) for p in patterns)


def apply_ignore(result: DiffResult, patterns: Iterable[str]) -> DiffResult:
    """Return a new DiffResult with ignored keys removed from all buckets."""
    pats = list(patterns)
    if not pats:
        return result

    missing_in_target = {
        k: v for k, v in result.missing_in_target.items() if not _matches_any(k, pats)
    }
    missing_in_base = {
        k: v for k, v in result.missing_in_base.items() if not _matches_any(k, pats)
    }
    mismatches = {
        k: v for k, v in result.mismatches.items() if not _matches_any(k, pats)
    }

    return DiffResult(
        missing_in_target=missing_in_target,
        missing_in_base=missing_in_base,
        mismatches=mismatches,
    )


def ignored_keys(result: DiffResult, patterns: Iterable[str]) -> set[str]:
    """Return the set of keys that *would* be removed by the given patterns."""
    pats = list(patterns)
    all_keys = (
        set(result.missing_in_target)
        | set(result.missing_in_base)
        | set(result.mismatches)
    )
    return {k for k in all_keys if _matches_any(k, pats)}
