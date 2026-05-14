"""Resolve variable interpolation in .env values (e.g. ${VAR} or $VAR)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    source: str
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_refs: Dict[str, List[str]] = field(default_factory=dict)  # key -> missing var names

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved_refs)

    @property
    def unresolved_count(self) -> int:
        return sum(len(v) for v in self.unresolved_refs.values())


def _refs_in(value: str) -> List[str]:
    """Return all variable names referenced in *value*."""
    return [m.group(1) or m.group(2) for m in _REF_RE.finditer(value)]


def _substitute(value: str, env: Dict[str, str]) -> str:
    """Replace all resolvable references; leave unresolvable ones intact."""
    def _replace(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        return env.get(name, m.group(0))

    return _REF_RE.sub(_replace, value)


def interpolate_env(env: Dict[str, str], source: str = "<env>") -> InterpolateResult:
    """Resolve interpolated values within *env*, using the same dict as context.

    Keys are processed in insertion order; forward references may remain
    unresolved on the first pass but are resolved in a second pass.
    """
    result = InterpolateResult(source=source)

    # Two-pass resolution to handle forward references.
    resolved: Dict[str, str] = {}
    for _pass in range(2):
        for key, raw in env.items():
            context = {**env, **resolved}
            resolved[key] = _substitute(raw, context)

    for key, value in resolved.items():
        missing = [r for r in _refs_in(value) if r not in env]
        result.resolved[key] = value
        if missing:
            result.unresolved_refs[key] = missing

    return result
