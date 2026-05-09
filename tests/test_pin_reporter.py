"""Tests for envdiff.pin_reporter."""

import json
import pytest

from envdiff.pinner import PinResult
from envdiff.pin_reporter import format_pin_text, format_pin_json, print_pin_report


@pytest.fixture
def clean_result():
    return PinResult(source="staging", pinned={"A": "1"})


@pytest.fixture
def drifted_result():
    r = PinResult(source="production", pinned={"A": "old", "B": "gone"})
    r.drifted = ["A"]
    r.new_keys = ["C"]
    r.removed_keys = ["B"]
    return r


def test_text_no_drift_message(clean_result):
    out = format_pin_text(clean_result)
    assert "No drift" in out


def test_text_contains_source(drifted_result):
    out = format_pin_text(drifted_result)
    assert "production" in out


def test_text_shows_drifted_key(drifted_result):
    out = format_pin_text(drifted_result)
    assert "A" in out
    assert "Changed" in out


def test_text_shows_new_key(drifted_result):
    out = format_pin_text(drifted_result)
    assert "C" in out
    assert "New keys" in out


def test_text_shows_removed_key(drifted_result):
    out = format_pin_text(drifted_result)
    assert "B" in out
    assert "Removed" in out


def test_json_structure(drifted_result):
    out = json.loads(format_pin_json(drifted_result))
    assert out["source"] == "production"
    assert out["has_drift"] is True
    assert "A" in out["drifted"]
    assert "C" in out["new_keys"]
    assert "B" in out["removed_keys"]


def test_json_no_drift(clean_result):
    out = json.loads(format_pin_json(clean_result))
    assert out["has_drift"] is False


def test_print_pin_report_text(capsys, clean_result):
    print_pin_report(clean_result, fmt="text")
    captured = capsys.readouterr()
    assert "No drift" in captured.out


def test_print_pin_report_json(capsys, drifted_result):
    print_pin_report(drifted_result, fmt="json")
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["has_drift"] is True
