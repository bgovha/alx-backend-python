#!/usr/bin/env python3
"""A github org client

This module implements a small GithubOrgClient used by the tests to
retrieve organization information and public repositories.
"""
from typing import (
    List,
    Dict,
)

from .utils import (
    get_json,
    access_nested_map,
    memoize,
)


class GithubOrgClient:
    """A Github org client for retrieving organization data.

    The client wraps a small portion of the Github API used in the
    unit and integration tests.
    """
    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        """Initialize the client with the organization name.

        Parameters
        ----------
        org_name: str
            The organization login/name on GitHub
        """
        self._org_name = org_name

    @memoize
    def org(self) -> Dict:
        """Retrieve organization payload from the API.

        This method is memoized by the `memoize` decorator to avoid
        repeated HTTP calls during tests.
        """
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        """Return the public repos URL from the organization payload."""
        return self.org["repos_url"]

    @memoize
    def repos_payload(self) -> Dict:
        """Retrieve the JSON payload of the public repositories."""
        return get_json(self._public_repos_url)

    def public_repos(self, license: str = None) -> List[str]:
        """List public repository names, optionally filtered by license."""
        json_payload = self.repos_payload
        public_repos = [
            repo["name"] for repo in json_payload
            if license is None or self.has_license(repo, license)
        ]

        return public_repos

    @staticmethod
    def has_license(repo: Dict[str, Dict], license_key: str) -> bool:
        """Return True if the repository has the specified license key."""
        assert license_key is not None, "license_key cannot be None"
        try:
            has_license = access_nested_map(repo, ("license", "key")) == license_key
        except KeyError:
            return False
        return has_license
