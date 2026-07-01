"""envgate — Validate environment variables at startup.

A minimal, zero-dependency Python library for validating and
retrieving environment variables with type coercion.

Example:
    >>> import os
    >>> os.environ["PORT"] = "8080"
    >>> from envgate import get_env
    >>> get_env("PORT", type="int")
    8080
    >>> del os.environ["PORT"]
"""

from envgate.core import get_env, load_env, validate
from envgate.exceptions import (
    EnvFileError,
    EnvGateError,
    InvalidEnvVarError,
    MissingEnvVarError,
    ValidationError,
)


__all__ = [
    "get_env",
    "load_env",
    "validate",
    "EnvFileError",
    "EnvGateError",
    "InvalidEnvVarError",
    "MissingEnvVarError",
    "ValidationError",
]
