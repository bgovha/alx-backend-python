#!/usr/bin/env python3
"""Unit tests for utils.access_nested_map"""

import unittest
from parameterized import parameterized
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map function"""
    
    @parameterized.expand([
        # (nested_map, path, expected_result)
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns expected results"""
        self.assertEqual(access_nested_map(nested_map, path), expected)


if __name__ == "__main__":
    unittest.main()
    
    
class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map function"""
    
    # ... previous test ...
    
    @parameterized.expand([
        ({}, ("a",), "a"),  # nested_map, path, expected_key_error
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test that KeyError is raised for invalid paths"""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        
        # Check the exception message contains the expected key
        self.assertEqual(str(context.exception), f"'{expected_key}'")
        
        