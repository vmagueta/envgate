"""envgate — Validate environment variables at startup.

A minimal, zero-dependency Python library for validating and
retrieving environment variables with type coercion.

Example:
    >>> import os
    >>> os.environ["PORT"] = "8080"
    >>> from envgate import get_env
    >>> get_env("PORT", type="int")
    8080
"""

from envgate.core import get_env, validate
from envgate.exceptions import (
    EnvGateError,
    InvalidEnvVarError,
    MissingEnvVarError,
    ValidationError,
)


__all__ = [
    "get_env",
    "validate",
    "EnvGateError",
    "InvalidEnvVarError",
    "MissingEnvVarError",
    "ValidationError",
]
