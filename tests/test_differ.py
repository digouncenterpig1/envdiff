"""Tests for envdiff.differ (multi-file diff)."""
import pytest
from envdiff.differ import diff_strings, MultiDiff, PairDiff


BASE = "A=1\nB=2\nC=3\n"
TARGET_OK = "A=1\nB=2\nC=3\n"
TARGET_MISSING = "A=1\nB=2\n"  # missing C
TARGET_EXTRA = "A=1\nB=2\nC=3\nD=4\n"  # D missing in base
TARGET_MISMATCH = "A=1\nB=99\nC=3\n"  # B differs


def _make_multi(*targets):
    return diff_strings("base", BASE, list(targets))


def test_no_differences_when_identical():
    multi = _make_multi(("t1", TARGET_OK))
    assert not multi.any_differences()


def test_missing_in_target_detected():
    multi = _make_multi(("t1", TARGET_MISSING))
    assert multi.any_differences()
    pair = multi.pairs[0]
    assert "C" in pair.result.missing_in_target


def test_missing_in_base_detected():
    multi = _make_multi(("t1", TARGET_EXTRA))
    assert multi.any_differences()
    pair = multi.pairs[0]
    assert "D" in pair.result.missing_in_base


def test_mismatch_detected():
    multi = _make_multi(("t1", TARGET_MISMATCH))
    pair = multi.pairs[0]
    assert "B" in pair.result.mismatches
    assert pair.result.mismatches["B"] == ("2", "99")


def test_multiple_targets():
    multi = _make_multi(("ok", TARGET_OK), ("bad", TARGET_MISSING))
    assert len(multi.pairs) == 2
    summary = multi.summary()
    assert summary["ok"] == 0
    assert summary["bad"] > 0


def test_summary_counts_all_issue_types():
    multi = _make_multi(("t", TARGET_MISMATCH))
    assert multi.summary()["t"] == 1


def test_base_label_preserved():
    multi = _make_multi(("t1", TARGET_OK))
    assert multi.base_label == "base"
    assert multi.pairs[0].base_label == "base"
    assert multi.pairs[0].target_label == "t1"
