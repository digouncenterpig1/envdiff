"""masker.py – mask env values for safe display or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_PATTERNS = [
    "secret", "password", "passwd", "token", "api_key", "apikey",
    "auth", "private", "credential", "cert", "key", "pwd",
]

_MASK = "***"


@dataclass
class MaskResult:
    source: str
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    @property
    def mask_count(self) -> int:
        return len(self.masked_keys)

    @property
    def has_masked(self) -> bool:
        return self.mask_count > 0

    def as_env_string(self) -> str:
        lines = []
        for k, v in self.masked.items():
            lines.append(f"{k}={v}")
        return "\n".join(lines)


def _is_sensitive(key: str, patterns: List[str]) -> bool:
    lower = key.lower()
    return any(p in lower for p in patterns)


def mask_env(
    env: Dict[str, str],
    source: str = "<env>",
    patterns: Optional[List[str]] = None,
    placeholder: str = _MASK,
) -> MaskResult:
    """Return a MaskResult with sensitive values replaced by *placeholder*."""
    active = patterns if patterns is not None else _DEFAULT_PATTERNS
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for k, v in env.items():
        if _is_sensitive(k, active):
            masked[k] = placeholder
            masked_keys.append(k)
        else:
            masked[k] = v

    return MaskResult(
        source=source,
        original=dict(env),
        masked=masked,
        masked_keys=sorted(masked_keys),
    )


def mask_env_file(
    path: str,
    patterns: Optional[List[str]] = None,
    placeholder: str = _MASK,
) -> MaskResult:
    """Parse *path* and mask sensitive values."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return mask_env(env, source=path, patterns=patterns, placeholder=placeholder)
