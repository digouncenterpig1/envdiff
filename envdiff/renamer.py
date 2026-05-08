"""Rename keys across env dicts with optional pattern-based bulk renaming."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class RenameResult:
    renamed: Dict[str, str] = field(default_factory=dict)   # old_key -> new_key
    skipped: List[str] = field(default_factory=list)        # keys not found
    env: Dict[str, str] = field(default_factory=dict)       # updated env


def rename_key(
    env: Dict[str, str],
    old_key: str,
    new_key: str,
) -> RenameResult:
    """Rename a single key in *env*. Returns a new env dict."""
    result = RenameResult(env=dict(env))
    if old_key not in env:
        result.skipped.append(old_key)
        return result
    value = result.env.pop(old_key)
    result.env[new_key] = value
    result.renamed[old_key] = new_key
    return result


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
) -> RenameResult:
    """Rename multiple keys given an old->new *mapping*."""
    result = RenameResult(env=dict(env))
    for old_key, new_key in mapping.items():
        if old_key not in result.env:
            result.skipped.append(old_key)
            continue
        value = result.env.pop(old_key)
        result.env[new_key] = value
        result.renamed[old_key] = new_key
    return result


def rename_by_pattern(
    env: Dict[str, str],
    pattern: str,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    strip_prefix: Optional[str] = None,
) -> RenameResult:
    """Rename all keys matching *pattern* by adding/removing a prefix or suffix.

    At least one of *prefix*, *suffix*, or *strip_prefix* must be provided.
    """
    if not any([prefix, suffix, strip_prefix]):
        raise ValueError("Provide at least one of: prefix, suffix, strip_prefix")

    result = RenameResult(env=dict(env))
    matched_keys = [k for k in env if fnmatch.fnmatch(k, pattern)]

    for old_key in matched_keys:
        new_key = old_key
        if strip_prefix and new_key.startswith(strip_prefix):
            new_key = new_key[len(strip_prefix):]
        if prefix:
            new_key = prefix + new_key
        if suffix:
            new_key = new_key + suffix
        if new_key == old_key:
            continue
        value = result.env.pop(old_key)
        result.env[new_key] = value
        result.renamed[old_key] = new_key

    return result
