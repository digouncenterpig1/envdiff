"""Human-readable and JSON reporters for AliasResult."""
from __future__ import annotations

import json
from typing import List

from .aliaser import AliasResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_alias_text(result: AliasResult) -> str:
    lines: List[str] = []
    lines.append(_c(f"Alias report — {result.source}", "1;34"))
    lines.append(f"  Aliases defined : {len(result.aliases)}")
    lines.append(f"  Resolved        : {result.total_resolved()}")
    lines.append(f"  Stale targets   : {len(result.stale)}")

    if result.resolved:
        lines.append(_c("\nResolved aliases:", "32"))
        for new_key, value in result.resolved.items():
            lines.append(f"  {new_key} = {value}")

    if result.stale:
        lines.append(_c("\nStale alias targets (missing from env):", "33"))
        for key in result.stale:
            lines.append(f"  {_c(key, '33')}")

    if result.unknown:
        lines.append(_c("\nUnaliased keys:", "90"))
        for key in result.unknown:
            lines.append(f"  {key}")

    return "\n".join(lines)


def format_alias_json(result: AliasResult) -> str:
    return json.dumps(
        {
            "source": result.source,
            "aliases": result.aliases,
            "resolved": result.resolved,
            "stale": result.stale,
            "unknown": result.unknown,
        },
        indent=2,
    )


def print_alias_report(result: AliasResult, fmt: str = "text") -> None:
    if fmt == "json":
        print(format_alias_json(result))
    else:
        print(format_alias_text(result))
