"""Filter diff results by key patterns or diff types."""

from __future__ import annotations

import fnmatch
from typing import List, Optional

from envdiff.comparator import DiffResult


def filter_by_pattern(result: DiffResult, pattern: str) -> DiffResult:
    """Return a new DiffResult containing only keys matching the glob pattern."""
    def _match(key: str) -> bool:
        return fnmatch.fnmatch(key, pattern)

    return DiffResult(
        missing_in_target={k: v for k, v in result.missing_in_target.items() if _match(k)},
        missing_in_base={k: v for k, v in result.missing_in_base.items() if _match(k)},
        mismatches={
            k: v for k, v in result.mismatches.items() if _match(k)
        },
    )


def filter_by_type(
    result: DiffResult,
    include_missing_in_target: bool = True,
    include_missing_in_base: bool = True,
    include_mismatches: bool = True,
) -> DiffResult:
    """Return a new DiffResult with selected diff types included."""
    return DiffResult(
        missing_in_target=result.missing_in_target if include_missing_in_target else {},
        missing_in_base=result.missing_in_base if include_missing_in_base else {},
        mismatches=result.mismatches if include_mismatches else {},
    )


def filter_keys(result: DiffResult, keys: List[str]) -> DiffResult:
    """Return a new DiffResult containing only the specified keys."""
    key_set = set(keys)
    return DiffResult(
        missing_in_target={k: v for k, v in result.missing_in_target.items() if k in key_set},
        missing_in_base={k: v for k, v in result.missing_in_base.items() if k in key_set},
        mismatches={k: v for k, v in result.mismatches.items() if k in key_set},
    )


def exclude_keys(result: DiffResult, keys: List[str]) -> DiffResult:
    """Return a new DiffResult with the specified keys removed."""
    key_set = set(keys)
    return DiffResult(
        missing_in_target={k: v for k, v in result.missing_in_target.items() if k not in key_set},
        missing_in_base={k: v for k, v in result.missing_in_base.items() if k not in key_set},
        mismatches={k: v for k, v in result.mismatches.items() if k not in key_set},
    )
