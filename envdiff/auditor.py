"""Audit trail: record and replay diff operations with timestamps."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class AuditEntry:
    timestamp: str
    operation: str          # e.g. "compare", "merge", "lint"
    sources: List[str]
    summary: str
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "AuditEntry":
        return AuditEntry(
            timestamp=d["timestamp"],
            operation=d["operation"],
            sources=d["sources"],
            summary=d["summary"],
            details=d.get("details", {}),
        )


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def add(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def __len__(self) -> int:
        return len(self.entries)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record(
    log: AuditLog,
    operation: str,
    sources: List[str],
    summary: str,
    details: Optional[dict] = None,
) -> AuditEntry:
    entry = AuditEntry(
        timestamp=_now_iso(),
        operation=operation,
        sources=sources,
        summary=summary,
        details=details or {},
    )
    log.add(entry)
    return entry


def save_audit_log(log: AuditLog, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = [e.to_dict() for e in log.entries]
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_audit_log(path: str) -> AuditLog:
    p = Path(path)
    if not p.exists():
        return AuditLog()
    data = json.loads(p.read_text(encoding="utf-8"))
    return AuditLog(entries=[AuditEntry.from_dict(d) for d in data])


def append_to_audit_file(
    path: str,
    operation: str,
    sources: List[str],
    summary: str,
    details: Optional[dict] = None,
) -> AuditEntry:
    log = load_audit_log(path)
    entry = record(log, operation, sources, summary, details)
    save_audit_log(log, path)
    return entry
