"""Tests for envdiff.deduplicator."""

import pytest

from envdiff.deduplicator import (
    DeduplicateResult,
    deduplicate_env,
    deduplicate_pairs,
)


# ---------------------------------------------------------------------------
# deduplicate_env (dict input — always clean)
# ---------------------------------------------------------------------------

def test_deduplicate_env_no_duplicates():
    env = {"A": "1", "B": "2"}
    result = deduplicate_env(env, source="test.env")
    assert result.kept == env
    assert result.has_removals() is False
    assert result.removal_count() == 0


def test_deduplicate_env_preserves_source_label():
    result = deduplicate_env({}, source="prod.env")
    assert result.source == "prod.env"


# ---------------------------------------------------------------------------
# deduplicate_pairs — first strategy
# ---------------------------------------------------------------------------

def test_first_strategy_keeps_first_value():
    pairs = [("KEY", "original"), ("KEY", "duplicate")]
    result = deduplicate_pairs(pairs, strategy="first")
    assert result.kept["KEY"] == "original"


def test_first_strategy_records_removed_pair():
    pairs = [("KEY", "original"), ("KEY", "duplicate")]
    result = deduplicate_pairs(pairs, strategy="first")
    assert ("KEY", "duplicate") in result.removed


def test_first_strategy_removal_count():
    pairs = [("X", "a"), ("X", "b"), ("X", "c")]
    result = deduplicate_pairs(pairs, strategy="first")
    assert result.removal_count() == 2


# ---------------------------------------------------------------------------
# deduplicate_pairs — last strategy
# ---------------------------------------------------------------------------

def test_last_strategy_keeps_last_value():
    pairs = [("KEY", "first"), ("KEY", "second")]
    result = deduplicate_pairs(pairs, strategy="last")
    assert result.kept["KEY"] == "second"


def test_last_strategy_records_removed_pair():
    pairs = [("KEY", "first"), ("KEY", "second")]
    result = deduplicate_pairs(pairs, strategy="last")
    assert ("KEY", "first") in result.removed


# ---------------------------------------------------------------------------
# as_env_string
# ---------------------------------------------------------------------------

def test_as_env_string_format():
    pairs = [("A", "1"), ("B", "2"), ("A", "99")]
    result = deduplicate_pairs(pairs, strategy="first")
    env_str = result.as_env_string()
    assert "A=1" in env_str
    assert "B=2" in env_str
    assert "A=99" not in env_str


# ---------------------------------------------------------------------------
# no duplicates at all
# ---------------------------------------------------------------------------

def test_no_duplicates_has_no_removals():
    pairs = [("FOO", "bar"), ("BAZ", "qux")]
    result = deduplicate_pairs(pairs)
    assert result.has_removals() is False
    assert result.kept == {"FOO": "bar", "BAZ": "qux"}
