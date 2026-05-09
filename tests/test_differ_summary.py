"""Tests for differ_summary.py"""

import pytest
from envdiff.comparator import DiffResult
from envdiff.differ import PairDiff, MultiDiff
from envdiff.differ_summary import summarize_multi_diff, DiffSummary


def _make_result(
    missing_in_target=None,
    missing_in_base=None,
    mismatches=None,
) -> DiffResult:
    return DiffResult(
        missing_in_target=missing_in_target or {},
        missing_in_base=missing_in_base or {},
        mismatches=mismatches or {},
    )


def _make_multi(*pairs) -> MultiDiff:
    return MultiDiff(pairs=list(pairs))


def test_empty_multi_gives_zero_summary():
    multi = _make_multi()
    s = summarize_multi_diff(multi)
    assert s.total_pairs == 0
    assert s.total_issues == 0
    assert s.clean_pairs == 0


def test_single_clean_pair():
    pair = PairDiff(base="a", target="b", result=_make_result())
    s = summarize_multi_diff(_make_multi(pair))
    assert s.total_pairs == 1
    assert s.pairs_with_differences == 0
    assert s.clean_pairs == 1
    assert s.total_issues == 0


def test_counts_missing_in_target():
    r = _make_result(missing_in_target={"FOO": "bar", "BAZ": "qux"})
    pair = PairDiff(base="a", target="b", result=r)
    s = summarize_multi_diff(_make_multi(pair))
    assert s.total_missing_in_target == 2
    assert s.pairs_with_differences == 1


def test_counts_mismatches():
    r = _make_result(mismatches={"KEY": ("v1", "v2")})
    pair = PairDiff(base="a", target="b", result=r)
    s = summarize_multi_diff(_make_multi(pair))
    assert s.total_mismatches == 1


def test_keys_always_missing_across_all_pairs():
    r1 = _make_result(missing_in_target={"FOO": "1"})
    r2 = _make_result(missing_in_target={"FOO": "1", "BAR": "2"})
    p1 = PairDiff(base="a", target="b", result=r1)
    p2 = PairDiff(base="a", target="c", result=r2)
    s = summarize_multi_diff(_make_multi(p1, p2))
    assert "FOO" in s.keys_always_missing
    assert "BAR" not in s.keys_always_missing


def test_keys_always_mismatched_across_all_pairs():
    r1 = _make_result(mismatches={"X": ("a", "b")})
    r2 = _make_result(mismatches={"X": ("a", "c")})
    p1 = PairDiff(base="a", target="b", result=r1)
    p2 = PairDiff(base="a", target="c", result=r2)
    s = summarize_multi_diff(_make_multi(p1, p2))
    assert "X" in s.keys_always_mismatched


def test_as_dict_has_expected_keys():
    s = DiffSummary(total_pairs=2, pairs_with_differences=1)
    d = s.as_dict()
    assert "total_pairs" in d
    assert "clean_pairs" in d
    assert "total_issues" in d
    assert "keys_always_missing" in d
