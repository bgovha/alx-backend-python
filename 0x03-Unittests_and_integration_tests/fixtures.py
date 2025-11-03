#!/usr/bin/env python3
"""Fixtures used for GithubOrgClient integration tests.

Contains example payloads for org and repos used by the
TestIntegrationGithubOrgClient test cases.
"""

TEST_PAYLOAD = [
  (
    {"repos_url": "https://api.github.com/orgs/google/repos"},
    [
      {
        "id": 7697149,
        "name": "episodes.dart",
        "license": {"key": "bsd-3-clause"}
      },
      {
        "id": 7968417,
        "name": "dagger",
        "license": {"key": "apache-2.0"}
      }
    ],
    ["episodes.dart", "dagger"],
    ["dagger"],
  )
]
