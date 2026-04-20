"""Tests for envgate.core."""

import pytest

from envgate.core import get_env, validate
from envgate.exceptions import InvalidEnvVarError, MissingEnvVarError, ValidationError


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
        with pytest.raises(ValidationError) as exc_info:
            validate({"HOST": {"type": "str"}})
        assert len(exc_info.value.errors) == 1
        assert isinstance(exc_info.value.errors[0], MissingEnvVarError)

    def test_raises_on_invalid_value(self, monkeypatch):
        monkeypatch.setenv("PORT", "abc")
        with pytest.raises(ValidationError) as exc_info:
            validate({"PORT": {"type": "int"}})
        assert len(exc_info.value.errors) == 1
        assert isinstance(exc_info.value.errors[0], InvalidEnvVarError)

    def test_empty_schema(self):
        assert validate({}) == {}


class TestValidationCollectsAllErrors:
    """Tests for issue #3 — validate() reports all errors at once."""

    def test_multiple_missing(self):
        schema = {
            "DB_URL": {"type": "str"},
            "REDIS_URL": {"type": "str"},
            "SECRET_KEY": {"type": "str"},
        }
        with pytest.raises(ValidationError) as exc_info:
            validate(schema)

        assert len(exc_info.value.errors) == 3
        assert all(isinstance(e, MissingEnvVarError) for e in exc_info.value.errors)

    def test_multiple_invalid(self, monkeypatch):
        monkeypatch.setenv("PORT", "abc")
        monkeypatch.setenv("TIMEOUT", "xyz")

        schema = {
            "PORT": {"type": "int"},
            "TIMEOUT": {"type": "float"},
        }
        with pytest.raises(ValidationError) as exc_info:
            validate(schema)

        assert len(exc_info.value.errors) == 2
        assert all(isinstance(e, InvalidEnvVarError) for e in exc_info.value.errors)

    def test_mixed_missing_and_invalid(self, monkeypatch):
        monkeypatch.setenv("PORT", "not_a_number")

        schema = {
            "DB_URL": {"type": "str"},
            "PORT": {"type": "int"},
        }
        with pytest.raises(ValidationError) as exc_info:
            validate(schema)

        errors = exc_info.value.errors
        assert len(errors) == 2
        assert isinstance(errors[0], MissingEnvVarError)
        assert isinstance(errors[1], InvalidEnvVarError)

    def test_error_message_lists_all(self, monkeypatch):
        monkeypatch.setenv("PORT", "abc")

        schema = {
            "DB_URL": {"type": "str"},
            "PORT": {"type": "int"},
        }
        with pytest.raises(ValidationError, match="Environment validation failed"):
            validate(schema)

    def test_no_errors_returns_normally(self, monkeypatch):
        monkeypatch.setenv("HOST", "localhost")
        monkeypatch.setenv("PORT", "5432")

        result = validate(
            {
                "HOST": {"type": "str"},
                "PORT": {"type": "int"},
            }
        )
        assert result == {"HOST": "localhost", "PORT": 5432}


class TestRequiredFlag:
    """Tests for issue #4 — explicit required flag."""

    def test_required_true_raises_when_missing(self):
        with pytest.raises(MissingEnvVarError) as exc_info:
            get_env("TEST_VAR", required=True)
        assert exc_info.value.var_name == "TEST_VAR"

    def test_required_true_with_default_raises_value_error(self):
        with pytest.raises(ValueError, match="Cannot combine required"):
            get_env("TEST_VAR", required=True, default="X")

    def test_required_true_with_default_raises_even_when_var_is_set(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "abc")
        with pytest.raises(ValueError, match="Cannot combine required"):
            get_env("TEST_VAR", required=True, default="abc")

    def test_required_false_without_default_returns_none(self):
        assert get_env("TEST_VAR", required=False) is None

    def test_required_false_with_default_returns_default(self):
        assert get_env("TEST_VAR", required=False, default="fallback") == "fallback"

    def test_value_error_message_mentions_var_name(self):
        with pytest.raises(ValueError, match=r"'CUSTOM_VAR'"):
            get_env("CUSTOM_VAR", required=True, default="X")
