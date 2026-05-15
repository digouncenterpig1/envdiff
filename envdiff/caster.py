"""Type casting inference for .env values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


@dataclass
class CastEntry:
    key: str
    raw: str
    inferred_type: str  # "int", "float", "bool", "empty", "string"
    cast_value: object


@dataclass
class CastResult:
    source: str
    entries: List[CastEntry] = field(default_factory=list)

    def by_type(self, type_name: str) -> List[CastEntry]:
        return [e for e in self.entries if e.inferred_type == type_name]

    def as_dict(self) -> Dict[str, object]:
        return {e.key: e.cast_value for e in self.entries}

    @property
    def type_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self.entries:
            counts[e.inferred_type] = counts.get(e.inferred_type, 0) + 1
        return counts


def _infer(raw: str) -> Tuple[str, object]:
    if raw == "":
        return "empty", None
    low = raw.lower()
    if low in _BOOL_TRUE:
        return "bool", True
    if low in _BOOL_FALSE:
        return "bool", False
    try:
        return "int", int(raw)
    except ValueError:
        pass
    try:
        return "float", float(raw)
    except ValueError:
        pass
    return "string", raw


def cast_env(env: Dict[str, str], source: str = "<env>") -> CastResult:
    """Infer and cast all values in an env dict."""
    result = CastResult(source=source)
    for key, raw in env.items():
        inferred_type, cast_value = _infer(raw)
        result.entries.append(
            CastEntry(key=key, raw=raw, inferred_type=inferred_type, cast_value=cast_value)
        )
    return result
