"""Tests for envdiff.diff_reporter."""
import json
import pytest
from envdiff.differ import diff_strings
from envdiff.diff_reporter import format_multi_diff_text, format_multi_diff_json


BASE = "A=1\nB=2\nC=3\n"


def _multi(targets):
    return diff_strings("base", BASE, targets)


def test_text_no_differences_shows_ok():
    multi = _multi([("t1", BASE)])
    out = format_multi_diff_text(multi)
    assert "No differences found" in out


def test_text_shows_missing_in_target():
    multi = _multi([("t1", "A=1\nB=2\n")])
    out = format_multi_diff_text(multi)
    assert "MISSING IN TARGET" in out
    assert "C" in out


def test_text_shows_missing_in_base():
    multi = _multi([("t1", BASE + "D=4\n")])
    out = format_multi_diff_text(multi)
    assert "MISSING IN BASE" in out
    assert "D" in out


def test_text_shows_mismatch():
    multi = _multi([("t1", "A=1\nB=99\nC=3\n")])
    out = format_multi_diff_text(multi)
    assert "MISMATCH" in out
    assert "B" in out


def test_text_summary_section_present():
    multi = _multi([("t1", BASE)])
    out = format_multi_diff_text(multi)
    assert "Summary" in out
    assert "t1" in out


def test_json_valid_structure():
    multi = _multi([("t1", "A=1\nB=2\n")])
    data = json.loads(format_multi_diff_json(multi))
    assert data["base"] == "base"
    assert len(data["comparisons"]) == 1
    comp = data["comparisons"][0]
    assert "C" in comp["missing_in_target"]
    assert comp["missing_in_base"] == []
    assert comp["mismatches"] == {}


def test_json_mismatch_structure():
    multi = _multi([("t1", "A=1\nB=99\nC=3\n")])
    data = json.loads(format_multi_diff_json(multi))
    mismatch = data["comparisons"][0]["mismatches"]
    assert "B" in mismatch
    assert mismatch["B"] == {"base": "2", "target": "99"}


def test_text_with_color_does_not_crash():
    multi = _multi([("t1", "A=1\nB=2\n")])
    out = format_multi_diff_text(multi, use_color=True)
    assert "C" in out


def test_json_multiple_targets():
    """Ensure comparisons list has one entry per target when multiple are given."""
    targets = [("t1", "A=1\nB=2\n"), ("t2", BASE + "D=4\n"), ("t3", BASE)]
    multi = _multi(targets)
    data = json.loads(format_multi_diff_json(multi))
    assert len(data["comparisons"]) == 3
    names = [c["target"] for c in data["comparisons"]]
    assert names == ["t1", "t2", "t3"]
    # t3 is identical to base — all diff lists should be empty
    t3 = data["comparisons"][2]
    assert t3["missing_in_target"] == []
    assert t3["missing_in_base"] == []
    assert t3["mismatches"] == {}
