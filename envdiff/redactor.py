"""Redact sensitive values from env dicts before display or export."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Optional

# Keys matching these patterns are considered sensitive
_DEFAULT_PATTERNS: list[str] = [
    r"(?i)(secret|password|passwd|token|api[_-]?key|private[_-]?key|auth|credential|cert|seed|salt)"
]

REDACTED_PLACEHOLDER = "***REDACTED***"


def _is_sensitive(key: str, patterns: list[str]) -> bool:
    """Return True if *key* matches any of the given regex patterns."""
    return any(re.search(p, key) for p in patterns)


def redact_dict(
    env: Dict[str, str],
    patterns: Optional[list[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by *placeholder*."""
    active = patterns if patterns is not None else _DEFAULT_PATTERNS
    return {
        k: (placeholder if _is_sensitive(k, active) else v)
        for k, v in env.items()
    }


def redact_keys(
    env: Dict[str, str],
    keys: Iterable[str],
    placeholder: str = REDACTED_PLACEHOLDER,
) -> Dict[str, str]:
    """Return a copy of *env* with explicit *keys* redacted."""
    sensitive = set(keys)
    return {k: (placeholder if k in sensitive else v) for k, v in env.items()}


def sensitive_keys(
    env: Dict[str, str],
    patterns: Optional[list[str]] = None,
) -> list[str]:
    """Return a sorted list of keys in *env* that are considered sensitive."""
    active = patterns if patterns is not None else _DEFAULT_PATTERNS
    return sorted(k for k in env if _is_sensitive(k, active))
