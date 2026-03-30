"""Tests for envgate.exceptions."""

from envgate.exceptions import (
    EnvGateError,
    InvalidEnvVarError,
    MissingEnvVarError,
)


class TestEnvGateError:
    """Tests for the base exception."""

    def test_is_exception(self):
        assert issubclass(EnvGateError, Exception)

    def test_message(self):
        error = EnvGateError("boom")
        assert str(error) == "boom"


class TestMissingEnvVarError:
    """Tests for MissingEnvVarError."""

    def test_inherits_from_base(self):
        assert issubclass(MissingEnvVarError, EnvGateError)

    def test_message(self):
        error = MissingEnvVarError("DATABASE_URL")
        assert str(error) == "Environment variable 'DATABASE_URL' is not set."

    def test_var_name_attribute(self):
        error = MissingEnvVarError("SECRET_KEY")
        assert error.var_name == "SECRET_KEY"


class TestInvalidEnvVarError:
    """Tests for InvalidEnvVarError."""

    def test_inherits_from_base(self):
        assert issubclass(InvalidEnvVarError, EnvGateError)

    def test_message(self):
        error = InvalidEnvVarError("PORT", "abc", "int")
        assert str(error) == (
            "Environment variable 'PORT' has invalid value 'abc' (expected int)."
        )

    def test_attributes(self):
        error = InvalidEnvVarError("PORT", "abc", "int")
        assert error.var_name == "PORT"
        assert error.value == "abc"
        assert error.expected_type == "int"

    def test_catchable_by_base(self):
        """Catching EnvGateError should also catch InvalidEnvVarError."""
        with_caught = False
        try:
            raise InvalidEnvVarError("X", "y", "int")
        except EnvGateError:
            with_caught = True
        assert with_caught
