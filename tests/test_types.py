"""Tests for envgate.types."""

import pytest

from envgate.types import (
    COERCIONS,
    coerce_bool,
    coerce_float,
    coerce_int,
    coerce_list,
    coerce_str,
)


class TestCoerceStr:
    """Tests for coerce_str."""

    def test_returns_value_as_is(self):
        assert coerce_str("hello") == "hello"

    def test_empty_string(self):
        assert coerce_str("") == ""


class TestCoerceInt:
    """Tests for coerce_int."""

    def test_valid_int(self):
        assert coerce_int("42") == 42

    def test_negative_int(self):
        assert coerce_int("-7") == -7

    def test_zero(self):
        assert coerce_int("0") == 0

    def test_float_string_returns_none(self):
        assert coerce_int("3.14") is None

    def test_invalid_string_returns_none(self):
        assert coerce_int("abc") is None

    def test_empty_string_returns_none(self):
        assert coerce_int("") is None


class TestCoerceFloat:
    """Tests for coerce_float."""

    def test_valid_float(self):
        assert coerce_float("3.14") == 3.14

    def test_integer_string(self):
        assert coerce_float("42") == 42.0

    def test_negative_float(self):
        assert coerce_float("-2.5") == -2.5

    def test_zero(self):
        assert coerce_float("0") == 0.0

    def test_invalid_string_returns_none(self):
        assert coerce_float("abc") is None

    def test_empty_string_returns_none(self):
        assert coerce_float("") is None


class TestCoerceBool:
    """Tests for coerce_bool."""

    @pytest.mark.parametrize("value", ["true", "1", "yes", "on"])
    def test_truthy_values(self, value):
        assert coerce_bool(value) is True

    @pytest.mark.parametrize("value", ["false", "0", "no", "off"])
    def test_falsy_values(self, value):
        assert coerce_bool(value) is False

    @pytest.mark.parametrize("value", ["TRUE", "True", "YES", "Yes", "ON", "On"])
    def test_case_insensitive(self, value):
        assert coerce_bool(value) is True

    def test_invalid_string_returns_none(self):
        assert coerce_bool("maybe") is None

    def test_empty_string_returns_none(self):
        assert coerce_bool("") is None


class TestCoercionsDict:
    """Tests for the COERCIONS mapping."""

    def test_has_all_types(self):
        assert set(COERCIONS.keys()) == {"str", "int", "float", "bool"}

    def test_maps_to_correct_functions(self):
        assert COERCIONS["str"] is coerce_str
        assert COERCIONS["int"] is coerce_int
        assert COERCIONS["float"] is coerce_float
        assert COERCIONS["bool"] is coerce_bool


class TestCoerceList:
    """Tests for coerce_list (issue #5)."""

    def test_simple_string_list(self):
        values, failed = coerce_list("a,b,c", "str", ",")
        assert values == ["a", "b", "c"]
        assert failed == []

    def test_int_list(self):
        values, failed = coerce_list("1,2,3", "int", ",")
        assert values == [1, 2, 3]
        assert failed == []

    def test_float_list(self):
        values, failed = coerce_list("1.5,2.5,3.5", "float", ",")
        assert values == [1.5, 2.5, 3.5]
        assert failed == []

    def test_bool_list(self):
        values, failed = coerce_list("true,false,yes,no", "bool", ",")
        assert values == [True, False, True, False]
        assert failed == []

    def test_custom_separator(self):
        values, failed = coerce_list("a:b:c", "str", ":")
        assert values == ["a", "b", "c"]
        assert failed == []

    def test_strip_whitespace_around_items(self):
        values, failed = coerce_list(" a , b , c ", "str", ",")
        assert values == ["a", "b", "c"]
        assert failed == []

    def test_failed_items_collected_with_indices(self):
        values, failed = coerce_list("1,abc,3,xyz,5", "int", ",")
        assert values == [1, 3, 5]
        assert failed == [(1, "abc"), (3, "xyz")]

    def test_empty_string_rejected(self):
        values, failed = coerce_list("", "int", ",")
        assert values == []
        assert failed == [(0, "")]

    def test_empty_item_in_middle_rejected(self):
        values, failed = coerce_list("a,,b", "str", ",")
        assert values == ["a", "b"]
        assert failed == [(1, "")]

    def test_trailing_empty_rejected(self):
        values, failed = coerce_list("a,b,", "str", ",")
        assert values == ["a", "b"]
        assert failed == [(2, "")]

    def test_leading_empty_rejected(self):
        values, failed = coerce_list(",a,b", "str", ",")
        assert values == ["a", "b"]
        assert failed == [(0, "")]

    def test_all_invalid_coercion(self):
        values, failed = coerce_list("a,b,c", "int", ",")
        assert values == []
        assert failed == [(0, "a"), (1, "b"), (2, "c")]
