"""Reporting helpers for EnvTemplate objects."""
from __future__ import annotations

import json
from typing import Optional

from envdiff.templater import EnvTemplate


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_template_text(template: EnvTemplate, color: bool = True) -> str:
    """Render the template as human-readable text with optional color."""
    lines: list[str] = []
    header = f"Template ({len(template.keys)} keys)"
    if template.source:
        header += f" — source: {template.source}"
    lines.append(_c(header, "1") if color else header)
    lines.append("")

    for key in template.keys:
        placeholder = template.placeholders.get(key, "")
        key_part = _c(key, "36") if color else key
        val_part = _c(placeholder if placeholder else "(empty)", "33") if color else (placeholder or "(empty)")
        lines.append(f"  {key_part}={val_part}")

    return "\n".join(lines) + "\n"


def format_template_json(template: EnvTemplate) -> str:
    """Render the template as a JSON string."""
    data = {
        "source": template.source,
        "keys": template.keys,
        "placeholders": template.placeholders,
    }
    return json.dumps(data, indent=2)


def print_template_report(
    template: EnvTemplate,
    fmt: str = "text",
    color: bool = True,
    dest: Optional[object] = None,
) -> None:
    """Print a template report to stdout (or a given file object)."""
    import sys
    out = dest or sys.stdout
    if fmt == "json":
        print(format_template_json(template), file=out)
    else:
        print(format_template_text(template, color=color), file=out)
