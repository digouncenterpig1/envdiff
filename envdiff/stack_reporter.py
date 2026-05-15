"""Reporter for StackResult — shows resolved env and override conflicts."""
from __future__ import annotations

import json
from typing import Optional

from envdiff.stacker import StackResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_stack_text(result: StackResult, color: bool = True) -> str:
    lines: list[str] = []
    header = f"Stack: {result.source}"
    lines.append(_c(header, "1;34") if color else header)
    lines.append(f"  Resolved keys : {len(result.resolved)}")
    lines.append(f"  Override keys : {result.override_count()}")
    lines.append("")

    if result.overrides:
        label = "Overrides (key redefined across layers):"
        lines.append(_c(label, "1;33") if color else label)
        for key, history in sorted(result.overrides.items()):
            lines.append(f"  {key}")
            for src, val in history:
                marker = "  ->" if (src, val) == history[-1] else "    "
                entry = f"{marker} [{src}] {val}"
                if color and marker == "  ->":
                    entry = _c(entry, "32")
                lines.append(entry)
        lines.append("")

    label2 = "Resolved env:"
    lines.append(_c(label2, "1") if color else label2)
    for k, v in sorted(result.resolved.items()):
        lines.append(f"  {k}={v}")

    return "\n".join(lines) + "\n"


def format_stack_json(result: StackResult) -> str:
    payload = {
        "source": result.source,
        "resolved": result.resolved,
        "overrides": {
            k: [{"source": s, "value": v} for s, v in hist]
            for k, hist in result.overrides.items()
        },
    }
    return json.dumps(payload, indent=2)


def print_stack_report(
    result: StackResult,
    fmt: str = "text",
    color: bool = True,
    out: Optional[object] = None,
) -> None:
    import sys

    dest = out or sys.stdout
    if fmt == "json":
        dest.write(format_stack_json(result) + "\n")
    else:
        dest.write(format_stack_text(result, color=color))
