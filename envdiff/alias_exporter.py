"""Export AliasResult to disk."""
from __future__ import annotations

import json
from pathlib import Path

from .aliaser import AliasResult
from .alias_reporter import format_alias_text


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def export_alias_text(result: AliasResult, path: Path) -> None:
    _ensure_parent(path)
    path.write_text(format_alias_text(result), encoding="utf-8")


def export_alias_json(result: AliasResult, path: Path) -> None:
    _ensure_parent(path)
    data = {
        "source": result.source,
        "aliases": result.aliases,
        "resolved": result.resolved,
        "stale": result.stale,
        "unknown": result.unknown,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_alias(result: AliasResult, path: Path, fmt: str = "text") -> None:
    if fmt == "json":
        export_alias_json(result, path)
    else:
        export_alias_text(result, path)
