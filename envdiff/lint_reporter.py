"""Format and print LintResult objects."""
from __future__ import annotations

import json
from typing import List

from envdiff.linter import LintResult, LintIssue

_COLORS = {"error": "\033[31m", "warning": "\033[33m", "reset": "\033[0m"}


def _colorize(text: str, severity: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    color = _COLORS.get(severity, "")
    return f"{color}{text}{_COLORS['reset']}"


def format_lint_text(result: LintResult, use_color: bool = True) -> str:
    """Return a human-readable string for a single LintResult."""
    lines: List[str] = []
    lines.append(f"Lint report for: {result.source}")
    if result.is_clean:
        lines.append("  No issues found.")
        return "\n".join(lines)

    for issue in result.issues:
        prefix = f"  line {issue.line_number:>4} [{issue.severity.upper():>7}] {issue.key!r}"
        msg = f"{prefix}: {issue.message}"
        lines.append(_colorize(msg, issue.severity, use_color))

    summary = f"  {len(result.issues)} issue(s) found"
    lines.append(summary)
    return "\n".join(lines)


def format_lint_json(result: LintResult) -> str:
    """Return a JSON string for a single LintResult."""
    payload = {
        "source": result.source,
        "is_clean": result.is_clean,
        "issues": [
            {
                "line": i.line_number,
                "key": i.key,
                "severity": i.severity,
                "message": i.message,
            }
            for i in result.issues
        ],
    }
    return json.dumps(payload, indent=2)


def format_multi_lint_text(results: List[LintResult], use_color: bool = True) -> str:
    """Format multiple LintResults (one per file) into a single report."""
    sections = [format_lint_text(r, use_color=use_color) for r in results]
    divider = "-" * 48
    return ("\n" + divider + "\n").join(sections)


def print_lint_report(result: LintResult, use_color: bool = True) -> None:
    """Print a lint report to stdout."""
    print(format_lint_text(result, use_color=use_color))
