"""Tests for envdiff.auditor and envdiff.audit_reporter."""

import json
import os
from pathlib import Path

import pytest

from envdiff.auditor import (
    AuditEntry,
    AuditLog,
    record,
    save_audit_log,
    load_audit_log,
    append_to_audit_file,
)
from envdiff.audit_reporter import (
    format_audit_text,
    format_audit_json,
    format_audit_summary,
)


# ---------------------------------------------------------------------------
# auditor core
# ---------------------------------------------------------------------------

def test_record_adds_entry():
    log = AuditLog()
    entry = record(log, "compare", ["a.env", "b.env"], "1 mismatch")
    assert len(log) == 1
    assert entry.operation == "compare"
    assert entry.sources == ["a.env", "b.env"]
    assert entry.summary == "1 mismatch"


def test_record_timestamp_is_set():
    log = AuditLog()
    entry = record(log, "lint", ["x.env"], "clean")
    assert entry.timestamp  # non-empty
    assert "T" in entry.timestamp  # ISO format


def test_record_details_stored():
    log = AuditLog()
    entry = record(log, "merge", [], "merged", details={"strategy": "last"})
    assert entry.details["strategy"] == "last"


def test_save_and_load_round_trip(tmp_path):
    log = AuditLog()
    record(log, "compare", ["a.env"], "ok")
    record(log, "lint", ["b.env"], "2 issues")
    path = str(tmp_path / "audit.json")
    save_audit_log(log, path)
    loaded = load_audit_log(path)
    assert len(loaded) == 2
    assert loaded.entries[0].operation == "compare"
    assert loaded.entries[1].operation == "lint"


def test_load_missing_file_returns_empty(tmp_path):
    log = load_audit_log(str(tmp_path / "nonexistent.json"))
    assert len(log) == 0


def test_append_to_audit_file_accumulates(tmp_path):
    path = str(tmp_path / "audit.json")
    append_to_audit_file(path, "compare", ["a.env"], "first")
    append_to_audit_file(path, "lint", ["a.env"], "second")
    log = load_audit_log(path)
    assert len(log) == 2


def test_audit_entry_from_dict_round_trip():
    entry = AuditEntry(
        timestamp="2024-01-01T00:00:00+00:00",
        operation="compare",
        sources=["x.env"],
        summary="all good",
        details={"keys": 10},
    )
    restored = AuditEntry.from_dict(entry.to_dict())
    assert restored.operation == entry.operation
    assert restored.details == entry.details


# ---------------------------------------------------------------------------
# audit_reporter
# ---------------------------------------------------------------------------

def _sample_log() -> AuditLog:
    log = AuditLog()
    record(log, "compare", ["dev.env", "prod.env"], "3 differences")
    record(log, "lint", ["dev.env"], "clean", details={"issues": 0})
    return log


def test_format_text_contains_operation():
    text = format_audit_text(_sample_log())
    assert "COMPARE" in text
    assert "LINT" in text


def test_format_text_contains_sources():
    text = format_audit_text(_sample_log())
    assert "dev.env" in text


def test_format_text_empty_log():
    text = format_audit_text(AuditLog())
    assert "No audit entries" in text


def test_format_json_valid(tmp_path):
    data = json.loads(format_audit_json(_sample_log()))
    assert isinstance(data, list)
    assert data[0]["operation"] == "compare"


def test_format_summary():
    summary = format_audit_summary(_sample_log())
    assert "compare=1" in summary
    assert "lint=1" in summary


def test_format_summary_empty():
    assert "no entries" in format_audit_summary(AuditLog())
