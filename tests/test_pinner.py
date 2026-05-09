"""Tests for envdiff.pinner."""

import json
import pytest
from pathlib import Path

from envdiff.pinner import (
    save_pin,
    load_pin,
    pin_exists,
    diff_with_pin,
    PinResult,
)


@pytest.fixture
def pin_file(tmp_path):
    return tmp_path / "baseline.pin.json"


def test_save_and_load_round_trip(pin_file):
    env = {"HOST": "localhost", "PORT": "5432"}
    save_pin(env, pin_file, source="test")
    loaded = load_pin(pin_file)
    assert loaded == env


def test_load_missing_returns_empty(pin_file):
    assert load_pin(pin_file) == {}


def test_pin_exists_true(pin_file):
    save_pin({}, pin_file)
    assert pin_exists(pin_file) is True


def test_pin_exists_false(pin_file):
    assert pin_exists(pin_file) is False


def test_no_drift_when_identical(pin_file):
    env = {"A": "1", "B": "2"}
    save_pin(env, pin_file)
    result = diff_with_pin(env, pin_file, source="test")
    assert not result.has_drift()
    assert result.drifted == []
    assert result.new_keys == []
    assert result.removed_keys == []


def test_drifted_key_detected(pin_file):
    save_pin({"A": "old"}, pin_file)
    result = diff_with_pin({"A": "new"}, pin_file)
    assert "A" in result.drifted
    assert result.has_drift()


def test_new_key_detected(pin_file):
    save_pin({"A": "1"}, pin_file)
    result = diff_with_pin({"A": "1", "B": "2"}, pin_file)
    assert "B" in result.new_keys


def test_removed_key_detected(pin_file):
    save_pin({"A": "1", "B": "2"}, pin_file)
    result = diff_with_pin({"A": "1"}, pin_file)
    assert "B" in result.removed_keys


def test_save_creates_parent_dirs(tmp_path):
    deep = tmp_path / "a" / "b" / "pin.json"
    save_pin({"X": "y"}, deep)
    assert deep.exists()


def test_source_stored_in_file(pin_file):
    save_pin({"K": "v"}, pin_file, source="production")
    raw = json.loads(pin_file.read_text())
    assert raw["source"] == "production"
