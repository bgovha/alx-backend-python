#!/usr/bin/env python3
"""Unit and integration tests for client.GithubOrgClient."""
from parameterized import parameterized, parameterized_class
import unittest
from unittest.mock import patch, Mock

from .client import GithubOrgClient
from . import fixtures


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient methods."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('0x03_Unittests_and_integration_tests.client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct payload."""
        mock_get_json.return_value = {"login": org_name}
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"login": org_name})
        mock_get_json.assert_called_once()

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the repos_url from org."""
        client = GithubOrgClient('test')
        with patch.object(GithubOrgClient, 'org', return_value={"repos_url": "http://api.github.com/test/repos"}):
            self.assertEqual(client._public_repos_url, "http://api.github.com/test/repos")

    @patch('0x03_Unittests_and_integration_tests.client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns names filtered by license when provided."""
        mock_get_json.return_value = fixtures.TEST_PAYLOAD[0][1]
        client = GithubOrgClient('test')
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=Mock) as mock_url:
            mock_url.return_value = "http://api.github.com/test/repos"
            repos = client.public_repos()
            self.assertEqual(repos, [r['name'] for r in fixtures.TEST_PAYLOAD[0][1]])
            mock_get_json.assert_called()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns expected boolean for repo/license."""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


@parameterized_class(fixtures.TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos using fixtures."""

    @classmethod
    def setUpClass(cls):
        """Start patcher for requests.get to return fixture payloads."""
        cls.get_patcher = patch('0x03_Unittests_and_integration_tests.client.get_json')
        cls.mock_get = cls.get_patcher.start()
        # First call for org
        cls.mock_get.side_effect = [cls.org_payload, cls.repos_payload]

    @classmethod
    def tearDownClass(cls):
        """Stop the requests.get patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test the integration of public_repos returns expected repos."""
        client = GithubOrgClient(self.org_payload.get('repos_url', ''))
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test for public_repos with license filtering."""
        client = GithubOrgClient(self.org_payload.get('repos_url', ''))
        self.assertEqual(client.public_repos(license='apache-2.0'), self.apache2_repos)
