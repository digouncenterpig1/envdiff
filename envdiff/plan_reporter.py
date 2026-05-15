"""Format and print MigrationPlan results."""
from __future__ import annotations

import json

from envdiff.planner import MigrationPlan

_COLORS = {"add": "\033[32m", "remove": "\033[31m", "update": "\033[33m", "reset": "\033[0m"}
_ICONS = {"add": "+", "remove": "-", "update": "~"}


def _c(text: str, action: str, *, color: bool = True) -> str:
    if not color:
        return text
    code = _COLORS.get(action, "")
    return f"{code}{text}{_COLORS['reset']}"


def format_plan_text(plan: MigrationPlan, *, color: bool = True) -> str:
    lines = [f"Migration plan: {plan.source!r} → {plan.target!r}"]
    if not plan.has_steps:
        lines.append("  No changes needed.")
        return "\n".join(lines)

    for action in ("add", "remove", "update"):
        group = plan.by_action(action)
        if not group:
            continue
        label = {"add": "Add", "remove": "Remove", "update": "Update"}[action]
        lines.append(f"\n  {label} ({len(group)}):")
        for step in group:
            icon = _ICONS[action]
            if action == "update":
                detail = f"{step.current_value!r} → {step.target_value!r}"
                lines.append("    " + _c(f"{icon} {step.key}: {detail}", action, color=color))
            else:
                lines.append("    " + _c(f"{icon} {step.key}", action, color=color))

    lines.append(f"\n  Total steps: {plan.step_count}")
    return "\n".join(lines)


def format_plan_json(plan: MigrationPlan) -> str:
    return json.dumps(plan.as_dict(), indent=2)


def print_plan_report(plan: MigrationPlan, *, color: bool = True) -> None:
    print(format_plan_text(plan, color=color))
