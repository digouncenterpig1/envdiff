"""Tests for envdiff.merger."""

import pytest

from envdiff.merger import merge_env_strings, merge_env_files, MergedEnv


# ---------------------------------------------------------------------------
# merge_env_strings
# ---------------------------------------------------------------------------

def test_merge_no_overlap():
    a = "FOO=1\nBAR=2\n"
    b = "BAZ=3\n"
    result = merge_env_strings([a, b], labels=["a", "b"])
    assert result.keys == {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert not result.has_conflicts()


def test_merge_last_strategy_wins():
    a = "FOO=original\n"
    b = "FOO=override\n"
    result = merge_env_strings([a, b], labels=["a", "b"], strategy="last")
    assert result.keys["FOO"] == "override"


def test_merge_first_strategy_wins():
    a = "FOO=original\n"
    b = "FOO=override\n"
    result = merge_env_strings([a, b], labels=["a", "b"], strategy="first")
    assert result.keys["FOO"] == "original"


def test_conflict_recorded_regardless_of_strategy():
    a = "SECRET=abc\n"
    b = "SECRET=xyz\n"
    for strategy in ("first", "last"):
        result = merge_env_strings([a, b], labels=["a", "b"], strategy=strategy)
        assert result.has_conflicts()
        assert "SECRET" in result.conflicts
        assert result.conflicts["SECRET"]["a"] == "abc"
        assert result.conflicts["SECRET"]["b"] == "xyz"


def test_source_tracking():
    a = "FOO=1\nSHARED=yes\n"
    b = "BAR=2\nSHARED=yes\n"
    result = merge_env_strings([a, b], labels=["a", "b"])
    assert result.sources["FOO"] == ["a"]
    assert result.sources["BAR"] == ["b"]
    assert set(result.sources["SHARED"]) == {"a", "b"}


def test_equal_values_not_flagged_as_conflict():
    a = "FOO=same\n"
    b = "FOO=same\n"
    result = merge_env_strings([a, b], labels=["a", "b"])
    assert not result.has_conflicts()


def test_default_labels():
    result = merge_env_strings(["A=1\n", "B=2\n"])
    assert "source_0" in result.sources["A"]
    assert "source_1" in result.sources["B"]


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        merge_env_strings(["A=1\n"], strategy="unknown")


def test_mismatched_labels_raises():
    with pytest.raises(ValueError, match="labels length"):
        merge_env_strings(["A=1\n", "B=2\n"], labels=["only_one"])


# ---------------------------------------------------------------------------
# merge_env_files
# ---------------------------------------------------------------------------

def test_merge_env_files(tmp_path):
    f1 = tmp_path / "dev.env"
    f2 = tmp_path / "prod.env"
    f1.write_text("HOST=localhost\nPORT=5432\n")
    f2.write_text("HOST=db.prod.example.com\nPORT=5432\n")

    result = merge_env_files([str(f1), str(f2)], labels=["dev", "prod"])

    assert result.keys["PORT"] == "5432"
    assert result.has_conflicts()
    assert "HOST" in result.conflicts
    assert result.conflicts["HOST"]["dev"] == "localhost"
    assert result.conflicts["HOST"]["prod"] == "db.prod.example.com"
