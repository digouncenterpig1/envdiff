"""Tests for envdiff.differ_stats."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ import PairDiff, MultiDiff
from envdiff.differ_stats import compute_stats, DiffStats


def _make_result(
    missing_in_target=None,
    missing_in_base=None,
    mismatches=None,
) -> DiffResult:
    return DiffResult(
        missing_in_target=list(missing_in_target or []),
        missing_in_base=list(missing_in_base or []),
        mismatches=dict(mismatches or {}),
    )


def _make_multi(*pairs) -> MultiDiff:
    pair_list = [
        PairDiff(base=b, target=t, result=r)
        for b, t, r in pairs
    ]
    return MultiDiff(pairs=pair_list)


def test_empty_multi_returns_zero_stats():
    multi = MultiDiff(pairs=[])
    stats = compute_stats(multi, source="test")
    assert stats.total_pairs == 0
    assert stats.clean_pairs == 0
    assert stats.dirty_pairs == 0
    assert stats.health_ratio == 1.0
    assert stats.most_affected_key is None


def test_all_clean_pairs():
    multi = _make_multi(
        ("a.env", "b.env", _make_result()),
        ("c.env", "d.env", _make_result()),
    )
    stats = compute_stats(multi, source="prod")
    assert stats.total_pairs == 2
    assert stats.clean_pairs == 2
    assert stats.dirty_pairs == 0
    assert stats.health_ratio == 1.0


def test_missing_in_target_counted():
    multi = _make_multi(
        ("a.env", "b.env", _make_result(missing_in_target=["KEY_A", "KEY_B"])),
    )
    stats = compute_stats(multi)
    assert stats.total_missing_in_target == 2
    assert stats.pairs_with_missing_in_target == 1
    assert stats.clean_pairs == 0


def test_missing_in_base_counted():
    multi = _make_multi(
        ("a.env", "b.env", _make_result(missing_in_base=["EXTRA"])),
    )
    stats = compute_stats(multi)
    assert stats.total_missing_in_base == 1
    assert stats.pairs_with_missing_in_base == 1


def test_mismatches_counted():
    multi = _make_multi(
        ("a.env", "b.env", _make_result(mismatches={"DB_URL": ("x", "y")})),
    )
    stats = compute_stats(multi)
    assert stats.total_mismatches == 1
    assert stats.pairs_with_mismatches == 1


def test_most_affected_key_identified():
    multi = _make_multi(
        ("a.env", "b.env", _make_result(missing_in_target=["SHARED_KEY"])),
        ("c.env", "d.env", _make_result(missing_in_target=["SHARED_KEY", "OTHER"])),
    )
    stats = compute_stats(multi)
    assert stats.most_affected_key == "SHARED_KEY"


def test_health_ratio_partial():
    multi = _make_multi(
        ("a.env", "b.env", _make_result()),
        ("c.env", "d.env", _make_result(missing_in_target=["X"])),
        ("e.env", "f.env", _make_result(missing_in_target=["Y"])),
        ("g.env", "h.env", _make_result()),
    )
    stats = compute_stats(multi)
    assert stats.clean_pairs == 2
    assert stats.dirty_pairs == 2
    assert stats.health_ratio == 0.5


def test_as_dict_contains_expected_keys():
    multi = _make_multi(
        ("a.env", "b.env", _make_result(mismatches={"PORT": ("80", "443")})),
    )
    stats = compute_stats(multi, source="staging")
    d = stats.as_dict()
    assert d["source"] == "staging"
    assert "health_ratio" in d
    assert "most_affected_key" in d
    assert d["total_mismatches"] == 1
