"""Tests for envdiff.linter."""
import textwrap
import pytest
from envdiff.linter import lint_env_string, lint_env_file, LintResult


def test_clean_file_returns_no_issues():
    content = "DB_HOST=localhost\nDB_PORT=5432\n"
    result = lint_env_string(content)
    assert result.is_clean


def test_lowercase_key_flagged():
    result = lint_env_string("db_host=localhost")
    messages = [i.message for i in result.issues]
    assert any("ALL_CAPS" in m for m in messages)


def test_mixed_case_key_flagged():
    result = lint_env_string("DbHost=localhost")
    assert not result.is_clean


def test_unquoted_value_with_spaces():
    result = lint_env_string("GREETING=hello world")
    messages = [i.message for i in result.issues]
    assert any("spaces" in m for m in messages)


def test_quoted_value_with_spaces_ok():
    result = lint_env_string('GREETING="hello world"')
    # only potential ALL_CAPS issue absent here since key is uppercase
    space_issues = [i for i in result.issues if "spaces" in i.message]
    assert len(space_issues) == 0


def test_export_prefix_flagged():
    result = lint_env_string("export MY_VAR=value")
    messages = [i.message for i in result.issues]
    assert any("export" in m for m in messages)


def test_long_value_flagged():
    long_val = "x" * 300
    result = lint_env_string(f"SECRET={long_val}")
    messages = [i.message for i in result.issues]
    assert any("256" in m for m in messages)


def test_comments_and_blanks_ignored():
    content = textwrap.dedent("""
        # this is a comment

        DB_HOST=localhost
    """)
    result = lint_env_string(content)
    assert result.is_clean


def test_line_numbers_are_correct():
    content = "GOOD=ok\nbad_key=value\n"
    result = lint_env_string(content)
    caps_issue = next(i for i in result.issues if "ALL_CAPS" in i.message)
    assert caps_issue.line_number == 2


def test_source_label_stored():
    result = lint_env_string("A=1", source="prod.env")
    assert result.source == "prod.env"


def test_lint_file_missing_path():
    result = lint_env_file("/nonexistent/path/.env")
    assert not result.is_clean
    assert result.errors()


def test_lint_file_reads_correctly(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    result = lint_env_file(str(env_file))
    assert result.is_clean


def test_warnings_and_errors_filtered():
    result = lint_env_string("bad_key=value")
    assert len(result.warnings()) > 0
    assert len(result.errors()) == 0
