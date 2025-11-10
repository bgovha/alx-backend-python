#!/usr/bin/env python3
"""Unit tests for the utils module.

This test module verifies the behavior of access_nested_map,
get_json and the memoize decorator.
"""
try:
    from parameterized import parameterized
except Exception:
    # Minimal fallback for parameterized.expand([...]) using unittest.subTest
    class _parameterized:
        @staticmethod
        def expand(params_list):
            def decorator(func):
                def wrapper(self, *args, **kwargs):
                    for params in params_list:
                        with self.subTest(params=params):
                            if isinstance(params, tuple):
                                func(self, *params)
                            else:
                                func(self, params)
                return wrapper
            return decorator
    parameterized = _parameterized
import unittest
from unittest.mock import patch, Mock

from . import utils


class TestAccessNestedMap(unittest.TestCase):
    """Tests for utils.access_nested_map."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """access_nested_map returns the value for a given path."""
        self.assertEqual(utils.access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_msg):
        """access_nested_map raises KeyError with expected message."""
        with self.assertRaises(KeyError) as ctx:
            utils.access_nested_map(nested_map, path)
        self.assertEqual(str(ctx.exception), expected_msg)


class TestGetJson(unittest.TestCase):
    """Tests for utils.get_json using mocked HTTP calls."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """get_json returns the JSON payload from requests.get."""
        mock_resp = Mock()
        mock_resp.json.return_value = test_payload
        with patch('{}.requests.get'.format(utils.__name__), return_value=mock_resp) as mock_get:
            result = utils.get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Tests for the memoize decorator."""

    def test_memoize(self):
        """Ensure memoize caches the result after the first call."""

        class TestClass:
            def a_method(self):
                return 42

            @utils.memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method', return_value=42) as mock_a:
            obj = TestClass()
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)
            mock_a.assert_called_once()
