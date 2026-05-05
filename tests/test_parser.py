"""Tests for envdiff.parser."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file


@pytest.fixture
def tmp_env(tmp_path):
    """Helper to write a temp .env file and return its path."""
    def _write(content: str) -> str:
        env_file = tmp_path / ".env"
        env_file.write_text(content, encoding="utf-8")
        return str(env_file)
    return _write


def test_basic_key_value(tmp_env):
    path = tmp_env("FOO=bar\nBAZ=qux\n")
    result = parse_env_file(path)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_quoted_values(tmp_env):
    path = tmp_env('KEY="hello world"\nOTHER=\'single\'\n')
    result = parse_env_file(path)
    assert result["KEY"] == "hello world"
    assert result["OTHER"] == "single"


def test_empty_value(tmp_env):
    path = tmp_env("EMPTY=\n")
    result = parse_env_file(path)
    assert result["EMPTY"] is None


def test_comments_ignored(tmp_env):
    path = tmp_env("# this is a comment\nFOO=bar\n")
    result = parse_env_file(path)
    assert "#" not in str(result)
    assert result == {"FOO": "bar"}


def test_blank_lines_ignored(tmp_env):
    path = tmp_env("\n\nFOO=bar\n\n")
    result = parse_env_file(path)
    assert result == {"FOO": "bar"}


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/.env")


def test_invalid_line(tmp_env):
    path = tmp_env("NOT VALID LINE\n")
    with pytest.raises(ValueError, match="Invalid line"):
        parse_env_file(path)
