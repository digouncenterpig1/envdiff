"""Tests for envdiff.masker."""
import pytest

from envdiff.masker import MaskResult, _is_sensitive, mask_env, mask_env_file


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "PORT": "8080",
        "AUTH_TOKEN": "tok_xyz",
        "LOG_LEVEL": "info",
    }


def test_sensitive_key_detected():
    assert _is_sensitive("DB_PASSWORD", ["password"]) is True


def test_non_sensitive_key_not_detected():
    assert _is_sensitive("APP_NAME", ["password", "secret"]) is False


def test_mask_count(sample_env):
    result = mask_env(sample_env, source="test")
    # DB_PASSWORD, API_KEY, AUTH_TOKEN all match default patterns
    assert result.mask_count >= 3


def test_non_sensitive_value_preserved(sample_env):
    result = mask_env(sample_env, source="test")
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["PORT"] == "8080"


def test_sensitive_value_replaced(sample_env):
    result = mask_env(sample_env, source="test")
    assert result.masked["DB_PASSWORD"] == "***"
    assert result.masked["API_KEY"] == "***"
    assert result.masked["AUTH_TOKEN"] == "***"


def test_original_unchanged(sample_env):
    result = mask_env(sample_env, source="test")
    assert result.original["DB_PASSWORD"] == "s3cr3t"


def test_custom_placeholder(sample_env):
    result = mask_env(sample_env, source="test", placeholder="[REDACTED]")
    assert result.masked["DB_PASSWORD"] == "[REDACTED]"


def test_custom_patterns():
    env = {"MY_CUSTOM_FIELD": "value", "SAFE": "ok"}
    result = mask_env(env, source="test", patterns=["custom"])
    assert result.masked["MY_CUSTOM_FIELD"] == "***"
    assert result.masked["SAFE"] == "ok"


def test_has_masked_true(sample_env):
    result = mask_env(sample_env, source="test")
    assert result.has_masked is True


def test_has_masked_false():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = mask_env(env, source="test")
    assert result.has_masked is False


def test_masked_keys_sorted(sample_env):
    result = mask_env(sample_env, source="test")
    assert result.masked_keys == sorted(result.masked_keys)


def test_as_env_string(sample_env):
    result = mask_env(sample_env, source="test")
    output = result.as_env_string()
    assert "APP_NAME=myapp" in output
    assert "DB_PASSWORD=***" in output


def test_mask_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP=hello\nSECRET_KEY=topsecret\nPORT=3000\n")
    result = mask_env_file(str(p))
    assert result.source == str(p)
    assert result.masked["APP"] == "hello"
    assert result.masked["SECRET_KEY"] == "***"
    assert result.masked["PORT"] == "3000"
