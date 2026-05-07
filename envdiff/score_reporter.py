"""Formats HealthScore results for display."""

import json
from envdiff.scorer import HealthScore

_COLORS = {
    "A": "\033[92m",  # green
    "B": "\033[96m",  # cyan
    "C": "\033[93m",  # yellow
    "D": "\033[91m",  # red
    "F": "\033[91m",  # red
    "reset": "\033[0m",
}


def _c(grade: str, text: str) -> str:
    color = _COLORS.get(grade, "")
    return f"{color}{text}{_COLORS['reset']}"


def format_score_text(hs: HealthScore) -> str:
    lines = [
        f"Health Score: {hs.source}",
        "-" * 40,
        f"  Score : {_c(hs.grade, str(hs.score))} / {hs.total}",
        f"  Grade : {_c(hs.grade, hs.grade)}",
    ]
    if hs.deductions:
        lines.append("  Deductions:")
        for key, val in hs.deductions.items():
            lines.append(f"    - {key}: -{val}")
    if hs.notes:
        lines.append("  Notes:")
        for note in hs.notes:
            lines.append(f"    * {note}")
    return "\n".join(lines)


def format_score_json(hs: HealthScore) -> str:
    return json.dumps(
        {
            "source": hs.source,
            "score": hs.score,
            "total": hs.total,
            "grade": hs.grade,
            "deductions": hs.deductions,
            "notes": hs.notes,
        },
        indent=2,
    )


def format_scores_comparison(scores: list[HealthScore]) -> str:
    lines = ["Environment Health Comparison", "=" * 40]
    for hs in scores:
        lines.append(
            f"  {hs.source:<30} score={_c(hs.grade, str(hs.score)):>3}  grade={_c(hs.grade, hs.grade)}"
        )
    return "\n".join(lines)


def print_score_report(hs: HealthScore, fmt: str = "text") -> None:
    if fmt == "json":
        print(format_score_json(hs))
    else:
        print(format_score_text(hs))
