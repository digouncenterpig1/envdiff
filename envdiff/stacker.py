"""Layer multiple .env files into a resolved flat env, tracking overrides."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class StackLayer:
    source: str
    env: Dict[str, str]


@dataclass
class StackResult:
    source: str
    resolved: Dict[str, str]
    # key -> list of (source, value) in layer order (last wins)
    overrides: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    def has_overrides(self) -> bool:
        return bool(self.overrides)

    def override_count(self) -> int:
        return len(self.overrides)

    def as_env_string(self) -> str:
        lines = [f"# stacked from: {self.source}"]
        for k, v in sorted(self.resolved.items()):
            lines.append(f"{k}={v}")
        return "\n".join(lines) + "\n"


def stack_envs(layers: List[StackLayer], source: str = "<stacked>") -> StackResult:
    """Merge layers in order; later layers override earlier ones."""
    resolved: Dict[str, str] = {}
    history: Dict[str, List[Tuple[str, str]]] = {}

    for layer in layers:
        for key, value in layer.env.items():
            history.setdefault(key, [])
            history[key].append((layer.source, value))
            resolved[key] = value

    overrides = {k: v for k, v in history.items() if len(v) > 1}
    return StackResult(source=source, resolved=resolved, overrides=overrides)


def stack_env_files(paths: List[str]) -> StackResult:
    """Build a StackResult from a list of file paths."""
    layers = [StackLayer(source=p, env=parse_env_file(p)) for p in paths]
    source = " > ".join(paths)
    return stack_envs(layers, source=source)


def stack_env_strings(
    named_strings: List[Tuple[str, str]]
) -> StackResult:
    """Build a StackResult from (name, raw_string) pairs."""
    layers = [
        StackLayer(source=name, env=parse_env_string(raw))
        for name, raw in named_strings
    ]
    source = " > ".join(n for n, _ in named_strings)
    return stack_envs(layers, source=source)
