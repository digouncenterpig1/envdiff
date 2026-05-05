"""Tests for envdiff.comparator."""

import pytest
from envdiff.comparator import compare_envs, DiffResult


BASE = {"FOO": "1", "BAR": "hello", "SHARED": "same"}
TARGET = {"BAR": "world", "SHARED": "same", "NEW_KEY": "extra"}


def test_missing_in_target():
    result = compare_envs(BASE, TARGET)
    assert "FOO" in result.missing_in_target


def test_missing_in_base():
    result = compare_envs(BASE, TARGET)
    assert "NEW_KEY" in result.missing_in_base


def test_value_mismatch():
    result = compare_envs(BASE, TARGET)
    assert "BAR" in result.value_mismatches
    assert result.value_mismatches["BAR"] == ("hello", "world")


def test_no_mismatch_for_equal_values():
    result = compare_envs(BASE, TARGET)
    assert "SHARED" not in result.value_mismatches


def test_has_differences_true():
    result = compare_envs(BASE, TARGET)
    assert result.has_differences is True


def test_has_differences_false():
    env = {"A": "1", "B": "2"}
    result = compare_envs(env, env.copy())
    assert result.has_differences is False


def test_ignore_values_skips_mismatch():
    result = compare_envs(BASE, TARGET, ignore_values=True)
    assert result.value_mismatches == {}
    assert "FOO" in result.missing_in_target


def test_labels_stored():
    result = compare_envs(BASE, TARGET, base_name="prod", target_name="staging")
    assert result.base_name == "prod"
    assert result.target_name == "staging"


def test_identical_envs_no_diff():
    env = {"X": "y", "Z": None}
    result = compare_envs(env, env.copy())
    assert not result.missing_in_base
    assert not result.missing_in_target
    assert not result.value_mismatches
