"""Profile .env files to summarize key statistics and patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class EnvProfile:
    source: str
    total_keys: int = 0
    empty_values: List[str] = field(default_factory=list)
    prefixes: Dict[str, int] = field(default_factory=dict)
    longest_key: str = ""
    longest_value_key: str = ""
    has_secrets_hint: bool = False

    @property
    def empty_count(self) -> int:
        return len(self.empty_values)

    @property
    def top_prefix(self) -> str | None:
        if not self.prefixes:
            return None
        return max(self.prefixes, key=lambda k: self.prefixes[k])


_SECRET_HINTS = ("secret", "password", "passwd", "token", "key", "api", "auth", "pass")


def _detect_secret_hint(keys: List[str]) -> bool:
    return any(hint in k.lower() for k in keys for hint in _SECRET_HINTS)


def _extract_prefix(key: str) -> str | None:
    if "_" in key:
        return key.split("_")[0]
    return None


def _build_profile(source: str, env: Dict[str, str]) -> EnvProfile:
    profile = EnvProfile(source=source)
    profile.total_keys = len(env)

    prefix_counts: Dict[str, int] = {}
    longest_key = ""
    longest_val_key = ""

    for k, v in env.items():
        if not v:
            profile.empty_values.append(k)
        pfx = _extract_prefix(k)
        if pfx:
            prefix_counts[pfx] = prefix_counts.get(pfx, 0) + 1
        if len(k) > len(longest_key):
            longest_key = k
        if len(v) > len(env.get(longest_val_key, "")):
            longest_val_key = k

    profile.prefixes = prefix_counts
    profile.longest_key = longest_key
    profile.longest_value_key = longest_val_key
    profile.has_secrets_hint = _detect_secret_hint(list(env.keys()))
    return profile


def profile_env_file(path: str) -> EnvProfile:
    env = parse_env_file(path)
    return _build_profile(path, env)


def profile_env_string(content: str, label: str = "<string>") -> EnvProfile:
    env = parse_env_string(content)
    return _build_profile(label, env)
