"""Tests for envgate.core."""

import pytest

from envgate.core import get_env, validate
from envgate.exceptions import InvalidEnvVarError, MissingEnvVarError


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove test env vars before each test.

    The monkeypatch fixture automatically restores the original
    environment after each test, preventing leaks between tests.
    """
    for var in ("TEST_VAR", "HOST", "PORT", "DEBUG"):
        monkeypatch.delenv(var, raising=False)


class TestGetEnv:
    """Tests for get_env."""

    def test_returns_string_by_default(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "hello")
        assert get_env("TEST_VAR") == "hello"

    def test_coerces_to_int(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "42")
        assert get_env("TEST_VAR", type="int") == 42

    def test_coerces_to_float(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "3.14")
        assert get_env("TEST_VAR", type="float") == 3.14

    def test_coerces_to_bool(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "true")
        assert get_env("TEST_VAR", type="bool") is True

    def test_missing_var_raises_error(self):
        with pytest.raises(MissingEnvVarError) as exc_info:
            get_env("TEST_VAR")
        assert exc_info.value.var_name == "TEST_VAR"

    def test_missing_var_with_default(self):
        assert get_env("TEST_VAR", default="fallback") == "fallback"

    def test_missing_var_with_none_default(self):
        assert get_env("TEST_VAR", default=None) is None

    def test_invalid_type_raises_value_error(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "hello")
        with pytest.raises(ValueError, match="Unsupported type"):
            get_env("TEST_VAR", type="list")

    def test_invalid_value_raises_error(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "abc")
        with pytest.raises(InvalidEnvVarError) as exc_info:
            get_env("TEST_VAR", type="int")
        assert exc_info.value.var_name == "TEST_VAR"
        assert exc_info.value.value == "abc"
        assert exc_info.value.expected_type == "int"

    def test_existing_var_ignores_default(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "8080")
        assert get_env("TEST_VAR", type="int", default=3000) == 8080


class TestValidate:
    """Tests for validate."""

    def test_validates_multiple_vars(self, monkeypatch):
        monkeypatch.setenv("HOST", "localhost")
        monkeypatch.setenv("PORT", "5432")
        result = validate(
            {
                "HOST": {"type": "str"},
                "PORT": {"type": "int"},
            }
        )
        assert result == {"HOST": "localhost", "PORT": 5432}

    def test_uses_defaults(self, monkeypatch):
        monkeypatch.setenv("HOST", "localhost")
        result = validate(
            {
                "HOST": {"type": "str"},
                "DEBUG": {"type": "bool", "default": False},
            }
        )
        assert result == {"HOST": "localhost", "DEBUG": False}

    def test_raises_on_missing_required(self):
        with pytest.raises(MissingEnvVarError):
            validate({"HOST": {"type": "str"}})

    def test_raises_on_invalid_value(self, monkeypatch):
        monkeypatch.setenv("PORT", "abc")
        with pytest.raises(InvalidEnvVarError):
            validate({"PORT": {"type": "int"}})

    def test_empty_schema(self):
        assert validate({}) == {}
