"""Core validation logic for envgate.

Provides functions to validate and retrieve environment variables
with type coercion and optional defaults.
"""

from __future__ import annotations

import os
from typing import Any

from envgate.exceptions import (
    EnvGateError,
    InvalidEnvVarError,
    MissingEnvVarError,
    ValidationError,
)
from envgate.types import COERCIONS

# Sentinel object to distinguish "no default provided" from None.
# Using None as default would be ambiguous — the user might
# intentionally want None as a default value.
_MISSING = object()


def get_env(
    var_name: str,
    *,
    type: str = "str",
    default: Any = _MISSING,
    required: bool | None = None,
) -> Any:
    """Retrieve and validate a single environment variable.

    Looks up the variable in ``os.environ``, coerces it to the
    requested type, and returns the result. If the variable is
    missing, behavior depends on ``required`` and ``default``.

    Args:
        var_name: The name of the environment variable.
        type: The expected type. One of ``"str"``, ``"int"``,
            ``"float"``, or ``"bool"``.
        default: Value to return if the variable is not set.
            If omitted, the variable is treated as required unless
            ``required=False`` is explicitly set.
        required: Whether the variable must be set. If ``None``
            (default), inferred from ``default``: required when no
            default is provided, optional otherwise. Pass ``True``
            or ``False`` to be explicit. Cannot be ``True`` when
            ``default`` is also provided — that combination is
            contradictory and raises ``ValueError``.

    Returns:
        The coerced value, the default if the variable is not set,
        or ``None`` if ``required=False`` and no default was given.

    Raises:
        MissingEnvVarError: If the variable is not set, is required,
            and no default is provided.
        InvalidEnvVarError: If the value cannot be coerced to the
            requested type.
        ValueError: If ``type`` is not supported, or if
            ``required=True`` is combined with a ``default``.

    Examples:
        >>> import os
        >>> os.environ["APP_PORT"] = "8080"
        >>> get_env("APP_PORT", type="int")
        8080

        >>> get_env("MISSING_VAR", default="fallback")
        'fallback'

        >>> os.environ["DEBUG"] = "true"
        >>> get_env("DEBUG", type="bool")
        True

        >>> get_env("MISSING_VAR", required=False) is None
        True
    """
    # Validate that the requested type is supported.
    if type not in COERCIONS:
        supported = ", ".join(sorted(COERCIONS.keys()))
        raise ValueError(f"Unsupported type '{type}'. Must be one of: {supported}.")

    # Confirms if required and default were passed, it's a schema error
    if required is True and default is not _MISSING:
        raise ValueError(
            f"Cannot combine required=True with a default value for '{var_name}'."
        )
    elif required is None:
        required = default is _MISSING

    # Look up the variable in the environment.
    raw_value = os.environ.get(var_name)

    # If the variable is not set, return default or raise.
    if raw_value is None:
        if default is not _MISSING:
            return default
        elif required is False:
            return None
        else:
            raise MissingEnvVarError(var_name)

    # Coerce the raw string value to the requested type.
    coerce = COERCIONS[type]
    result = coerce(raw_value)

    # If coercion returned None, the value is invalid for the type.
    if result is None:
        raise InvalidEnvVarError(var_name, raw_value, type)

    return result


def validate(schema: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Validate multiple environment variables at once.

    Takes a schema dictionary where each key is a variable name
    and each value is a dict of options passed to :func:`get_env`.

    Args:
        schema: A mapping of variable names to their validation
            options (``type``, ``default``, ``required``).

    Returns:
        A dictionary of variable names to their validated values.

    Raises:
        ValidationError: If any required variable is not set
            or if any value fails type coercion.

    Examples:
        >>> import os
        >>> os.environ["HOST"] = "localhost"
        >>> os.environ["PORT"] = "5432"
        >>> _ = os.environ.pop("DEBUG", None)
        >>> result = validate({
        ...     "HOST": {"type": "str"},
        ...     "PORT": {"type": "int"},
        ...     "DEBUG": {"type": "bool", "default": False},
        ... })
        >>> result == {"HOST": "localhost", "PORT": 5432, "DEBUG": False}
        True
    """
    result: dict[str, Any] = {}
    errors: list[EnvGateError] = []

    for var_name, options in schema.items():
        try:
            result[var_name] = get_env(var_name, **options)
        except (MissingEnvVarError, InvalidEnvVarError) as e:
            errors.append(e)

    if errors:
        raise ValidationError(errors)

    return result
