"""Format and display audit log entries."""

from __future__ import annotations

import json
from typing import List

from envdiff.auditor import AuditEntry, AuditLog

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_DIM = "\033[2m"


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}"


def format_audit_text(log: AuditLog) -> str:
    if not log.entries:
        return "No audit entries found."

    lines: List[str] = [_c(_BOLD, f"Audit Log  ({len(log.entries)} entries)"), ""]
    for i, entry in enumerate(log.entries, 1):
        lines.append(
            f"  {_c(_CYAN, str(i))}. [{_c(_DIM, entry.timestamp)}] "
            f"{_c(_YELLOW, entry.operation.upper())}"
        )
        lines.append(f"     sources : {', '.join(entry.sources) or '—'}")
        lines.append(f"     summary : {entry.summary}")
        if entry.details:
            for k, v in entry.details.items():
                lines.append(f"     {k:10s}: {v}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_audit_json(log: AuditLog) -> str:
    return json.dumps([e.to_dict() for e in log.entries], indent=2)


def format_audit_summary(log: AuditLog) -> str:
    """One-line summary per operation type."""
    counts: dict = {}
    for entry in log.entries:
        counts[entry.operation] = counts.get(entry.operation, 0) + 1
    if not counts:
        return "audit: no entries"
    parts = [f"{op}={n}" for op, n in sorted(counts.items())]
    return "audit summary — " + ", ".join(parts)


def print_audit_report(log: AuditLog, fmt: str = "text") -> None:
    if fmt == "json":
        print(format_audit_json(log))
    else:
        print(format_audit_text(log))
