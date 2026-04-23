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
from envgate.types import COERCIONS, coerce_list

# Sentinel object to distinguish "no default provided" from None.
# Using None as default would be ambiguous — the user might
# intentionally want None as a default value.
_MISSING = object()


def _parse_list_type(type_str: str) -> tuple[bool, str]:
    """Parse a type string and return ``(is_list, item_type)``.

    - ``"list"`` → ``(True, "str")`` (alias for ``"list[str]"``)
    - ``"list[int]"`` → ``(True, "int")``
    - ``"int"`` → ``(False, "int")`` (not a list — passthrough)
    - ``"list[abc]"`` → raises ``ValueError`` (invalid inner type)
    - ``"list[]"`` → raises ``ValueError`` (empty brackets)
    - ``"list[int"`` → raises ``ValueError`` (unclosed brackets)

    Non-list type strings are returned as-is with ``is_list=False``.
    The caller is responsible for validating scalar types against
    ``COERCIONS``.
    """
    if type_str == "list":
        return (True, "str")

    if not type_str.startswith("list["):
        return (False, type_str)

    if not type_str.endswith("]"):
        raise ValueError(f"Invalid list type '{type_str}': missing closing bracket.")

    inner = type_str[len("list[") : -1]
    if inner == "":
        raise ValueError(f"Invalid list type '{type_str}': empty brackets.")

    if inner not in COERCIONS:
        supported = ", ".join(sorted(COERCIONS.keys()))
        raise ValueError(
            f"Invalid list item type '{inner}' in '{type_str}'. "
            f"Must be one of: {supported}."
        )

    return (True, inner)


def get_env(
    var_name: str,
    *,
    type: str = "str",
    default: Any = _MISSING,
    required: bool | None = None,
    sep: Any = _MISSING,
) -> Any:
    """Retrieve and validate a single environment variable.

    Looks up the variable in ``os.environ``, coerces it to the
    requested type, and returns the result. If the variable is
    missing, behavior depends on ``required`` and ``default``.

    Args:
        var_name: The name of the environment variable.
        type: The expected type. One of ``"str"``, ``"int"``,
            ``"float"``, ``"bool"``, or a list type: ``"list"``
            (alias for ``"list[str]"``), ``"list[str]"``,
            ``"list[int]"``, ``"list[float]"``, ``"list[bool]"``.
        default: Value to return if the variable is not set.
            If omitted, the variable is treated as required unless
            ``required=False`` is explicitly set. For list types,
            ``default`` is returned as a copy to prevent mutations
            from leaking into shared schemas.
        required: Whether the variable must be set. If ``None``
            (default), inferred from ``default``: required when no
            default is provided, optional otherwise. Pass ``True``
            or ``False`` to be explicit. Cannot be ``True`` when
            ``default`` is also provided — that combination is
            contradictory and raises ``ValueError``.
        sep: Separator used to split list values. Defaults to ``","``.
            Only applicable when ``type`` is a list type; passing
            ``sep`` with a scalar type raises ``ValueError``.

    Returns:
        The coerced value, the default if the variable is not set,
        or ``None`` if ``required=False`` and no default was given.

    Raises:
        MissingEnvVarError: If the variable is not set, is required,
            and no default is provided.
        InvalidEnvVarError: If the value cannot be coerced to the
            requested type. For list types, aggregates all invalid
            items into a single error via ``items_info``.
        ValueError: If ``type`` is not supported, if ``required=True``
            is combined with a ``default``, or if ``sep`` is passed
            with a non-list ``type``.

    Examples:
        Required variable with type coercion (APP_PORT=8080):
            get_env("APP_PORT", type="int")  # returns 8080

        Optional variable with a fallback:
            get_env("MISSING_VAR", default="fallback")  # returns "fallback"

        Boolean coercion (DEBUG=true):
            get_env("DEBUG", type="bool")  # returns True

        Optional variable absent:
            get_env("MISSING_VAR", required=False)  # returns None

        List of strings (ALLOWED_HOSTS=host1,host2,host3):
            get_env("ALLOWED_HOSTS", type="list")
            # returns ["host1", "host2", "host3"]

        List of integers with custom separator (PATHS=8000:8001:8002):
            get_env("PATHS", type="list[int]", sep=":")
            # returns [8000, 8001, 8002]

        List with Python default (TAGS unset):
            get_env("TAGS", type="list", default=["a", "b"])
            # returns ["a", "b"]
    """
    # Parse the type — detects list[X] forms and validates inner type.
    is_list, item_type = _parse_list_type(type)

    # Validate that the (effective) item type is supported.
    if item_type not in COERCIONS:
        supported = ", ".join(sorted(COERCIONS.keys()))
        raise ValueError(f"Unsupported type '{type}'. Must be one of: {supported}.")

    # sep only applies to list types.
    if sep is not _MISSING and not is_list:
        raise ValueError(f"'sep' is only valid for list types, not '{type}'.")

    # Contradiction: required=True with a default value.
    if required is True and default is not _MISSING:
        raise ValueError(
            f"Cannot combine required=True with a default value for '{var_name}'."
        )
    elif required is None:
        required = default is _MISSING

    effective_sep = sep if sep is not _MISSING else ","

    # Look up the variable in the environment.
    raw_value = os.environ.get(var_name)

    # If the variable is not set, return default or raise.
    if raw_value is None:
        if default is not _MISSING:
            # Copy list defaults to prevent shared-schema mutations.
            if is_list and isinstance(default, list):
                return list(default)
            return default
        elif required is False:
            return None
        else:
            raise MissingEnvVarError(var_name)

    # Coerce the raw string value.
    if is_list:
        values, failed = coerce_list(raw_value, item_type, effective_sep)
        if failed:
            raise InvalidEnvVarError(var_name, raw_value, type, items_info=failed)
        return values

    # Scalar path.
    coerce = COERCIONS[type]
    result = coerce(raw_value)
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
        Validate a schema with mixed required and optional vars.
        Given HOST=localhost and PORT=5432 in the environment:
            result = validate({
                "HOST": {"type": "str"},
                "PORT": {"type": "int"},
                "DEBUG": {"type": "bool", "default": False},
            })
            # result == {"HOST": "localhost", "PORT": 5432, "DEBUG": False}
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
