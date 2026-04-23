"""Type coercion functions for environment variable values.

Each function takes a raw string from an environment variable and converts
it to the expected Python type. If the conversion fails, it returns ``None``
instead of raising. The caller decides what to do.
"""

from __future__ import annotations


# Mapping of truthy and falsy string values for boolean coercion.
_TRUTHY = {"true", "1", "yes", "on"}
_FALSY = {"false", "0", "no", "off"}


def coerce_str(value: str) -> str:
    """Return the value as-is (identity coercion).

    Exists for API consistency - every type has a coercion function,
    so the caller doesn't need special cases.

    Examples:
        >>> coerce_str("hello")
        'hello'
    """
    return value


def coerce_int(value: str) -> int | None:
    """Convert a string to an integer.

    Returns:
        The integer value, or ``None`` if conversion fails.

    Examples:
        >>> coerce_int("42")
        42
        >>> coerce_int("3.14") is None
        True
        >>> coerce_int("abc") is None
        True
    """
    try:
        return int(value)
    except ValueError:
        return None


def coerce_float(value: str) -> float | None:
    """Convert a string to a float.

    Returns:
        The float value, or ``None`` if conversion fails.

    Examples:
        >>> coerce_float("3.14")
        3.14
        >>> coerce_float("42")
        42.0
        >>> coerce_float("abc") is None
        True
    """
    try:
        return float(value)
    except ValueError:
        return None


def coerce_bool(value: str) -> bool | None:
    """Convert a string to a boolean.

    Accepted truthy values: ``true``, ``1``, ``yes``, ``on``.
    Accepted falsy values: ``false``, ``0``, ``no``, ``off``.
    Comparison is case-insensitive.

    Returns:
        The boolean value, or ``None`` if the string is not recognized.

    Examples:
        >>> coerce_bool("true")
        True
        >>> coerce_bool("FALSE")
        False
        >>> coerce_bool("yes")
        True
        >>> coerce_bool("0")
        False
        >>> coerce_bool("maybe") is None
        True
    """
    lower = value.lower()
    if lower in _TRUTHY:
        return True
    if lower in _FALSY:
        return False
    return None


def coerce_list(
    raw: str,
    item_type: str,
    sep: str = ",",
) -> tuple[list, list[tuple[int, str]]]:
    """Split a string on ``sep``, strip whitespace, and coerce each item.

    Rejects empty items, both the whole string being empty and empty
    items between separatores (e.g. ``"a,,b"``).

    Args:
        raw: The full raw string to split.
        item_type: One of ``"str"``, ``"int"``, ``""float"``, ``""bool"``.
            Must be a key in ``COERCIONS``.
        sep: The separator character. Defaults to ``","``.

    Returns:
        A tuple ``(values, failed)``.
        ``values`` is the list of successfully coerced items in order.
        ``failed`` is a list of ``(index, raw_item)`` for items that
        couldn't be coerced (including empty items). If ``failed`` is
        non-empty, the caller should raise ``InvalidEnvVarError`` with
        ``items_info=failed``.

    Examples:
        Happy path:
            coerce_list("1,2,3", "int", ",")
            # ([1, 2, 3], [])

        With failures:
            coerce_list("1,abc,3", "int", ",")
            # ([1, 3], [(1, "abc")])

        Empty items rejected:
            coerce_list("a,,b", "str", ",")
            # (["a", "b"], [(1, "")])
    """
    item_coerce = COERCIONS[item_type]
    items = [x.strip() for x in raw.split(sep)]

    values: list = []
    failed: list[tuple[int, str]] = []

    for idx, item in enumerate(items):
        if item == "":
            failed.append((idx, item))
            continue

        result = item_coerce(item)
        if result is None and item_type != "str":
            failed.append((idx, item))
        else:
            values.append(result)

    return (values, failed)


# Maps type names to their coercion functions.
# Used by core.py to look up the right converter.
COERCIONS: dict[str, callable] = {
    "str": coerce_str,
    "int": coerce_int,
    "float": coerce_float,
    "bool": coerce_bool,
}
