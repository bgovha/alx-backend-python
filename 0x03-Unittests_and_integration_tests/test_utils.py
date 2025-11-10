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
        
        #!/usr/bin/env python3
"""Unit tests for utils.get_json"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import get_json


class TestGetJson(unittest.TestCase):
    """Test cases for get_json function"""
    
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """
        Test that get_json returns expected result without making HTTP calls
        
        Args:
            test_url: URL to test
            test_payload: Expected JSON response
            mock_get: Mocked requests.get function (injected by @patch)
        """
        # Configure the mock to return our test payload
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response
        
        # Call the function
        result = get_json(test_url)
        
        # Verify the mock was called once with correct URL
        mock_get.assert_called_once_with(test_url)
        
        # Verify the result matches expected payload
        self.assertEqual(result, test_payload)


if __name__ == "__main__":
    unittest.main()
    
    
    
