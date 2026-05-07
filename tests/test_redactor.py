"""Tests for envdiff.redactor."""

import pytest
from envdiff.redactor import (
    REDACTED_PLACEHOLDER,
    redact_dict,
    redact_keys,
    sensitive_keys,
)


@pytest.fixture()
def sample_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "AUTH_TOKEN": "tok_xyz",
        "PORT": "8080",
    }


def test_redact_dict_hides_sensitive_values(sample_env):
    result = redact_dict(sample_env)
    assert result["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result["API_KEY"] == REDACTED_PLACEHOLDER
    assert result["AUTH_TOKEN"] == REDACTED_PLACEHOLDER


def test_redact_dict_preserves_non_sensitive_values(sample_env):
    result = redact_dict(sample_env)
    assert result["APP_NAME"] == "myapp"
    assert result["DEBUG"] == "true"
    assert result["PORT"] == "8080"


def test_redact_dict_custom_placeholder(sample_env):
    result = redact_dict(sample_env, placeholder="<hidden>")
    assert result["DB_PASSWORD"] == "<hidden>"
    assert result["APP_NAME"] == "myapp"


def test_redact_dict_custom_patterns(sample_env):
    result = redact_dict(sample_env, patterns=[r"(?i)debug"])
    assert result["DEBUG"] == REDACTED_PLACEHOLDER
    # default sensitive keys should NOT be redacted with custom pattern
    assert result["DB_PASSWORD"] == "s3cr3t"


def test_redact_dict_empty_env():
    assert redact_dict({}) == {}


def test_redact_keys_explicit(sample_env):
    result = redact_keys(sample_env, keys=["APP_NAME", "PORT"])
    assert result["APP_NAME"] == REDACTED_PLACEHOLDER
    assert result["PORT"] == REDACTED_PLACEHOLDER
    assert result["DEBUG"] == "true"


def test_redact_keys_empty_list(sample_env):
    result = redact_keys(sample_env, keys=[])
    assert result == sample_env


def test_sensitive_keys_returns_matching_keys(sample_env):
    found = sensitive_keys(sample_env)
    assert "DB_PASSWORD" in found
    assert "API_KEY" in found
    assert "AUTH_TOKEN" in found
    assert "APP_NAME" not in found
    assert "PORT" not in found


def test_sensitive_keys_sorted(sample_env):
    found = sensitive_keys(sample_env)
    assert found == sorted(found)


def test_sensitive_keys_custom_patterns(sample_env):
    found = sensitive_keys(sample_env, patterns=[r"(?i)port"])
    assert found == ["PORT"]
