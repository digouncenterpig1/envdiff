"""Normalize .env file contents for consistent comparison.

Handles common inconsistencies like trailing whitespace, mixed line endings,
redundant quotes, and key casing so diffs reflect real differences only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NormalizeResult:
    """Holds the normalized env dict and a log of changes made."""

    source: str
    normalized: Dict[str, str]
    changes: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    def change_count(self) -> int:
        return len(self.changes)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_REDUNDANT_QUOTE_RE = re.compile(r'^(['"])(.*?)\1$', re.DOTALL)


def _strip_redundant_quotes(value: str) -> str:
    """Remove surrounding single or double quotes when they are balanced."""
    m = _REDUNDANT_QUOTE_RE.match(value)
    return m.group(2) if m else value


def _normalize_value(value: str) -> str:
    """Apply all value-level normalizations."""
    # Strip leading/trailing whitespace first
    value = value.strip()
    # Remove redundant enclosing quotes
    value = _strip_redundant_quotes(value)
    # Strip again in case quotes were hiding inner whitespace
    value = value.strip()
    return value


def _normalize_key(key: str, uppercase: bool = True) -> str:
    """Normalize a key: strip whitespace and optionally uppercase."""
    key = key.strip()
    if uppercase:
        key = key.upper()
    return key


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalize_env(
    env: Dict[str, str],
    source: str = "<dict>",
    *,
    uppercase_keys: bool = True,
    strip_values: bool = True,
    remove_quotes: bool = True,
) -> NormalizeResult:
    """Normalize an already-parsed env dictionary.

    Parameters
    ----------
    env:
        Raw key/value pairs as returned by the parser.
    source:
        Label used in the result (e.g. filename).
    uppercase_keys:
        When *True*, keys are uppercased so ``db_host`` and ``DB_HOST``
        are treated as the same key.
    strip_values:
        Strip leading/trailing whitespace from values.
    remove_quotes:
        Remove balanced surrounding quotes from values.

    Returns
    -------
    NormalizeResult
    """
    normalized: Dict[str, str] = {}
    changes: List[str] = []

    for raw_key, raw_value in env.items():
        key = _normalize_key(raw_key, uppercase=uppercase_keys)
        if key != raw_key:
            changes.append(f"key renamed: {raw_key!r} -> {key!r}")

        value = raw_value
        if strip_values or remove_quotes:
            new_value = _normalize_value(value) if remove_quotes else value.strip()
            if new_value != value:
                changes.append(f"{key}: value changed {value!r} -> {new_value!r}")
            value = new_value

        normalized[key] = value

    return NormalizeResult(source=source, normalized=normalized, changes=changes)


def normalize_env_string(
    text: str,
    source: str = "<string>",
    **kwargs,
) -> NormalizeResult:
    """Parse *text* as an .env file and normalize the result.

    Accepts the same keyword arguments as :func:`normalize_env`.
    """
    from envdiff.parser import parse_env_string  # local import avoids circularity

    raw = parse_env_string(text)
    return normalize_env(raw, source=source, **kwargs)


def normalize_env_file(
    path: str,
    **kwargs,
) -> NormalizeResult:
    """Read *path* from disk, parse it, and normalize the result.

    Accepts the same keyword arguments as :func:`normalize_env`.
    """
    from envdiff.parser import parse_env_file  # local import avoids circularity

    raw = parse_env_file(path)
    return normalize_env(raw, source=path, **kwargs)
