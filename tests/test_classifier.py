"""Tests for envdiff.classifier."""

import pytest
from envdiff.classifier import classify_env, ClassifyEntry, ClassifyResult


@pytest.fixture
def sample_env():
    return {
        "DATABASE_PASSWORD": "s3cr3t",
        "API_URL": "https://api.example.com",
        "SERVER_PORT": "8080",
        "ENABLE_FEATURE_X": "true",
        "LOG_DIR": "/var/log/app",
        "SUPPORT_EMAIL": "support@example.com",
        "REQUEST_TIMEOUT": "30",
        "MAX_RETRIES": "5",
        "APP_NAME": "myapp",
    }


def test_secret_key_classified(sample_env):
    result = classify_env(sample_env)
    secrets = result.keys_in("secret")
    assert "DATABASE_PASSWORD" in secrets


def test_url_key_classified(sample_env):
    result = classify_env(sample_env)
    assert "API_URL" in result.keys_in("url")


def test_port_key_classified(sample_env):
    result = classify_env(sample_env)
    assert "SERVER_PORT" in result.keys_in("port")


def test_flag_key_classified(sample_env):
    result = classify_env(sample_env)
    assert "ENABLE_FEATURE_X" in result.keys_in("flag")


def test_path_key_classified(sample_env):
    result = classify_env(sample_env)
    assert "LOG_DIR" in result.keys_in("path")


def test_email_key_classified(sample_env):
    result = classify_env(sample_env)
    assert "SUPPORT_EMAIL" in result.keys_in("email")


def test_timeout_key_classified(sample_env):
    result = classify_env(sample_env)
    assert "REQUEST_TIMEOUT" in result.keys_in("timeout")


def test_numeric_fallback_via_value(sample_env):
    result = classify_env(sample_env)
    # MAX_RETRIES has no pattern match, value "5" is numeric
    assert "MAX_RETRIES" in result.keys_in("numeric")


def test_unknown_fallback(sample_env):
    result = classify_env(sample_env)
    assert "APP_NAME" in result.keys_in("unknown")


def test_category_counts_sums_to_total(sample_env):
    result = classify_env(sample_env)
    total = sum(result.category_counts().values())
    assert total == len(sample_env)


def test_source_stored():
    result = classify_env({}, source="production")
    assert result.source == "production"


def test_empty_env_returns_empty_result():
    result = classify_env({})
    assert result.entries == []
    assert result.by_category() == {}


def test_url_value_fallback():
    env = {"SOME_KEY": "https://example.com"}
    result = classify_env(env)
    assert "SOME_KEY" in result.keys_in("url")


def test_email_value_fallback():
    env = {"CONTACT": "admin@example.org"}
    result = classify_env(env)
    assert "CONTACT" in result.keys_in("email")
