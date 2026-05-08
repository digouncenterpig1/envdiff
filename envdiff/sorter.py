"""Sort .env keys by various strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal

SortStrategy = Literal["alpha", "alpha_desc", "by_prefix", "by_length"]


@dataclass
class SortResult:
    source: str
    original: List[str]
    sorted_keys: List[str]
    strategy: SortStrategy
    env: Dict[str, str] = field(default_factory=dict)

    def as_env_string(self) -> str:
        """Render sorted env back to KEY=VALUE lines."""
        lines = []
        for key in self.sorted_keys:
            value = self.env.get(key, "")
            lines.append(f"{key}={value}")
        return "\n".join(lines)


def _extract_prefix(key: str) -> str:
    """Return the prefix portion of a key (up to first underscore)."""
    if "_" in key:
        return key.split("_")[0]
    return key


def sort_env(
    env: Dict[str, str],
    source: str = "<input>",
    strategy: SortStrategy = "alpha",
) -> SortResult:
    """Sort the keys of *env* using the given strategy."""
    keys = list(env.keys())

    if strategy == "alpha":
        sorted_keys = sorted(keys)
    elif strategy == "alpha_desc":
        sorted_keys = sorted(keys, reverse=True)
    elif strategy == "by_prefix":
        sorted_keys = sorted(keys, key=lambda k: (_extract_prefix(k), k))
    elif strategy == "by_length":
        sorted_keys = sorted(keys, key=lambda k: (len(k), k))
    else:
        raise ValueError(f"Unknown sort strategy: {strategy!r}")

    return SortResult(
        source=source,
        original=keys,
        sorted_keys=sorted_keys,
        strategy=strategy,
        env=dict(env),
    )


def sort_env_file(
    path: str,
    strategy: SortStrategy = "alpha",
) -> SortResult:
    """Parse *path* and return a SortResult."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return sort_env(env, source=path, strategy=strategy)
