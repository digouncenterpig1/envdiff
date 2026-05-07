"""Tests for envdiff.scorer and envdiff.score_reporter."""

import json
import pytest

from envdiff.scorer import HealthScore, score_env
from envdiff.linter import LintResult, LintIssue
from envdiff.profiler import EnvProfile
from envdiff.comparator import DiffResult
from envdiff.score_reporter import (
    format_score_text,
    format_score_json,
    format_scores_comparison,
)


# --- helpers ---

def _lint_with_issues(n: int) -> LintResult:
    lr = LintResult(source="test.env")
    for i in range(n):
        lr.add(LintIssue(line=i + 1, key=f"key{i}", message="lowercase key"))
    return lr


def _profile(empty: int = 0, secrets: int = 0) -> EnvProfile:
    return EnvProfile(
        source="test.env",
        total_keys=10,
        empty_count=empty,
        top_prefix="APP",
        prefix_counts={"APP": 5},
        secrets_hint_count=secrets,
    )


def _diff(missing: int = 0, mismatched: int = 0) -> DiffResult:
    return DiffResult(
        missing_in_target={f"KEY{i}" for i in range(missing)},
        missing_in_base=set(),
        mismatched={f"MIS{i}": ("a", "b") for i in range(mismatched)},
    )


# --- scorer tests ---

def test_perfect_score_with_no_inputs():
    hs = score_env("clean.env")
    assert hs.score == 100
    assert hs.grade == "A"


def test_lint_issues_reduce_score():
    hs = score_env("x.env", lint_result=_lint_with_issues(4))
    assert hs.score < 100
    assert "lint_issues" in hs.deductions


def test_empty_values_reduce_score():
    hs = score_env("x.env", profile=_profile(empty=3))
    assert hs.score < 100
    assert "empty_values" in hs.deductions


def test_missing_keys_reduce_score():
    hs = score_env("x.env", diff_result=_diff(missing=3))
    assert "missing_keys" in hs.deductions


def test_mismatched_keys_reduce_score():
    hs = score_env("x.env", diff_result=_diff(mismatched=2))
    assert "mismatched_keys" in hs.deductions


def test_score_never_below_zero():
    hs = score_env(
        "x.env",
        lint_result=_lint_with_issues(20),
        profile=_profile(empty=20),
        diff_result=_diff(missing=10, mismatched=10),
    )
    assert hs.score >= 0


def test_grade_f_for_very_low_score():
    hs = HealthScore(source="bad.env")
    hs.deductions["lint_issues"] = 40
    hs.deductions["empty_values"] = 20
    hs.deductions["missing_keys"] = 20
    hs.deductions["mismatched_keys"] = 20
    assert hs.grade == "F"


# --- reporter tests ---

def test_format_text_contains_score():
    hs = score_env("app.env")
    text = format_score_text(hs)
    assert "100" in text
    assert "app.env" in text


def test_format_json_valid():
    hs = score_env("app.env", lint_result=_lint_with_issues(2))
    data = json.loads(format_score_json(hs))
    assert data["source"] == "app.env"
    assert "score" in data
    assert "grade" in data
    assert "deductions" in data


def test_format_scores_comparison_lists_all():
    scores = [score_env(f"env{i}.env") for i in range(3)]
    text = format_scores_comparison(scores)
    for i in range(3):
        assert f"env{i}.env" in text
