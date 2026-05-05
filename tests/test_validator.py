"""Tests for envdiff.validator."""

import pytest
from envdiff.validator import validate_env_string, validate_env_file


def test_valid_content_returns_no_issues():
    content = "KEY=value\nDEBUG=true\n# a comment\n\nFOO=bar"
    result = validate_env_string(content)
    assert result.is_valid
    assert result.issues == []


def test_missing_equals_separator():
    result = validate_env_string("BADLINE")
    assert not result.is_valid
    assert any("missing '='" in i.message for i in result.issues)


def test_empty_key_flagged():
    result = validate_env_string("=value")
    assert not result.is_valid
    assert any("empty key" in i.message for i in result.issues)


def test_key_with_whitespace_flagged():
    result = validate_env_string("MY KEY=value")
    assert not result.is_valid
    assert any("whitespace" in i.message for i in result.issues)


def test_key_starting_with_digit_flagged():
    result = validate_env_string("1KEY=value")
    assert not result.is_valid
    assert any("letter or underscore" in i.message for i in result.issues)


def test_key_starting_with_underscore_is_valid():
    result = validate_env_string("_PRIVATE=secret")
    assert result.is_valid


def test_unmatched_double_quote_flagged():
    result = validate_env_string('KEY="unmatched')
    assert not result.is_valid
    assert any("unmatched quote" in i.message for i in result.issues)


def test_matched_quotes_are_valid():
    result = validate_env_string('KEY="hello world"')
    assert result.is_valid


def test_comments_and_blanks_ignored():
    content = "# comment\n\n   \n# another"
    result = validate_env_string(content)
    assert result.is_valid


def test_issue_str_representation():
    result = validate_env_string("BADLINE")
    issue_str = str(result.issues[0])
    assert "Line 1" in issue_str


def test_validate_env_file_missing_file():
    result = validate_env_file("/nonexistent/path/.env")
    assert not result.is_valid
    assert any("cannot read file" in i.message for i in result.issues)


def test_validate_env_file_reads_valid_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("HOST=localhost\nPORT=5432\n")
    result = validate_env_file(str(env_file))
    assert result.is_valid
