"""Tests for envdiff.annotator."""

import pytest
from envdiff.annotator import annotate_env, Annotation, AnnotateResult


@pytest.fixture
def sample_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "API_KEY": "supersecret",
        "DEBUG": "true",
        "PORT": "8080",
        "EMPTY_VAR": "",
        "APP_NAME": "myapp",
    }


def test_result_has_correct_source(sample_env):
    result = annotate_env(sample_env, source="production.env")
    assert result.source == "production.env"


def test_all_keys_annotated(sample_env):
    result = annotate_env(sample_env)
    annotated_keys = [a.key for a in result.annotations]
    for key in sample_env:
        assert key in annotated_keys


def test_url_key_classified(sample_env):
    result = annotate_env(sample_env)
    ann = result.by_key("DATABASE_URL")
    assert ann is not None
    assert "url" in ann.comment.lower() or "endpoint" in ann.comment.lower()


def test_secret_key_classified(sample_env):
    result = annotate_env(sample_env)
    ann = result.by_key("API_KEY")
    assert ann is not None
    assert "sensitive" in ann.comment.lower() or "secret" in ann.comment.lower()


def test_flag_key_classified(sample_env):
    result = annotate_env(sample_env)
    ann = result.by_key("DEBUG")
    assert ann is not None
    assert "flag" in ann.comment.lower()


def test_numeric_value_classified(sample_env):
    result = annotate_env(sample_env)
    ann = result.by_key("PORT")
    assert ann is not None
    assert "numeric" in ann.comment.lower()


def test_empty_value_classified(sample_env):
    result = annotate_env(sample_env)
    ann = result.by_key("EMPTY_VAR")
    assert ann is not None
    assert "empty" in ann.comment.lower()


def test_generic_string_classified(sample_env):
    result = annotate_env(sample_env)
    ann = result.by_key("APP_NAME")
    assert ann is not None
    assert "string" in ann.comment.lower()


def test_extra_comment_overrides_classification(sample_env):
    extra = {"APP_NAME": "custom override comment"}
    result = annotate_env(sample_env, extra_comments=extra)
    ann = result.by_key("APP_NAME")
    assert ann is not None
    assert ann.comment == "custom override comment"


def test_as_line_format():
    ann = Annotation(key="FOO", value="bar", comment="string value")
    assert ann.as_line() == "FOO=bar  # string value"


def test_as_env_string_contains_all_keys(sample_env):
    result = annotate_env(sample_env)
    output = result.as_env_string()
    for key in sample_env:
        assert key in output


def test_by_key_returns_none_for_missing():
    result = AnnotateResult(source="x")
    assert result.by_key("NONEXISTENT") is None


def test_empty_env_produces_empty_result():
    result = annotate_env({})
    assert result.annotations == []
    assert result.as_env_string() == ""
