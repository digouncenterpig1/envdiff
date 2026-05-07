"""Human-readable reporting for ignored keys."""
from __future__ import annotations

from envdiff.comparator import DiffResult
from envdiff.ignorer import apply_ignore, ignored_keys


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_ignore_summary_text(
    result: DiffResult,
    patterns: list[str],
    *,
    color: bool = True,
) -> str:
    """Return a short text summary of what was ignored and what remains."""
    skipped = ignored_keys(result, patterns)
    filtered = apply_ignore(result, patterns)

    lines: list[str] = []

    if patterns:
        header = "Ignore patterns active:"
        lines.append(_c(header, "1") if color else header)
        for p in patterns:
            lines.append(f"  {_c(p, '33') if color else p}")
    else:
        lines.append("No ignore patterns configured.")

    if skipped:
        label = f"Skipped {len(skipped)} key(s):"
        lines.append(_c(label, "90") if color else label)
        for k in sorted(skipped):
            lines.append(f"  - {k}")
    else:
        lines.append("No keys were ignored.")

    remaining = (
        len(filtered.missing_in_target)
        + len(filtered.missing_in_base)
        + len(filtered.mismatches)
    )
    summary = f"Remaining differences after ignore: {remaining}"
    lines.append(_c(summary, "1") if color else summary)

    return "\n".join(lines)


def print_ignore_summary(
    result: DiffResult,
    patterns: list[str],
    *,
    color: bool = True,
) -> None:
    print(format_ignore_summary_text(result, patterns, color=color))
