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
    
    
    
#!/usr/bin/env python3
"""Unit tests for utils.memoize"""

import unittest
from unittest.mock import patch
from utils import memoize


class TestMemoize(unittest.TestCase):
    """Test cases for memoize decorator"""
    
    def test_memoize(self):
        """Test that memoize caches method results"""
        
        class TestClass:
            """Test class with memoized property"""
            
            def a_method(self):
                """Method that returns a value"""
                return 42
            
            @memoize
            def a_property(self):
                """Memoized property that calls a_method"""
                return self.a_method()
        
        # Create instance
        test_obj = TestClass()
        
        # Patch a_method to track calls
        with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
            # Call a_property twice
            result1 = test_obj.a_property
            result2 = test_obj.a_property
            
            # Both calls should return 42
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            
            # But a_method should only be called once (memoized!)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
    
    
#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class"""
    
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Test that GithubOrgClient.org returns correct value
        
        Args:
            org_name: Name of the organization
            mock_get_json: Mocked get_json function
        """
        # Set up mock return value
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload
        
        # Create client and call org
        client = GithubOrgClient(org_name)
        result = client.org
        
        # Verify get_json was called with correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        
        # Verify result matches expected payload
        self.assertEqual(result, test_payload)


if __name__ == "__main__":
    unittest.main()
    
    
class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class"""
    
    # ... previous tests ...
    
    def test_public_repos_url(self):
        """Test that _public_repos_url returns expected URL"""
        
        # Known payload with repos_url
        known_payload = {
            "login": "google",
            "repos_url": "https://api.github.com/orgs/google/repos"
        }
        
        # Mock the org property to return known_payload
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=lambda: property(lambda self: known_payload)
        ):
            client = GithubOrgClient("google")
            result = client._public_repos_url
            
            # Verify result matches repos_url from payload
            self.assertEqual(result, known_payload["repos_url"])
            
            
class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class"""
    
    # ... previous tests ...
    
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns expected list of repos"""
        
        # Mock payload from get_json
        test_repos_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = test_repos_payload
        
        # Mock _public_repos_url property
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=property,
            return_value="https://api.github.com/orgs/test/repos"
        ) as mock_public_repos_url:
            
            client = GithubOrgClient("test")
            result = client.public_repos()
            
            # Verify result is list of repo names
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            
            # Verify mocked property was accessed
            mock_public_repos_url.assert_called_once()
            
            # Verify get_json was called once
            mock_get_json.assert_called_once()
            
            
class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class"""
    
    # ... previous tests ...
    
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Test that has_license returns correct result
        
        Args:
            repo: Repository dict with license info
            license_key: License key to check
            expected: Expected boolean result
        """
        client = GithubOrgClient("test")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)
        
        
#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch
from parameterized import parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests"""
        
        # Define side_effect function for requests.get
        def get_side_effect(url):
            """Return appropriate payload based on URL"""
            mock_response = unittest.mock.Mock()
            
            if url == cls.org_payload.get("repos_url"):
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = cls.org_payload
            
            return mock_response
        
        # Start patcher
        cls.get_patcher = patch('requests.get', side_effect=get_side_effect)
        cls.get_patcher.start()
    
    @classmethod
    def tearDownClass(cls):
        """Tear down class fixtures after tests complete"""
        cls.get_patcher.stop()
    
    def test_public_repos(self):
        """Test public_repos method returns expected repos"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
    
    def test_public_repos_with_license(self):
        """Test public_repos with license filter"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
    
