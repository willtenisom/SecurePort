import unittest
from datetime import datetime, timedelta, timezone

from scripts.cleanup_merged_branches import cleanup_merged_branches


NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
REPOSITORY = "willtenisom/SecurePort"
OLD_SHA = "a" * 40


def pull_request(
    number: int,
    branch: str,
    *,
    merged_at: str | None,
    sha: str = OLD_SHA,
    state: str = "closed",
    head_repository: str = REPOSITORY,
    base: str = "main",
) -> dict[str, object]:
    return {
        "number": number,
        "state": state,
        "merged_at": merged_at,
        "base": {"ref": base},
        "head": {
            "ref": branch,
            "sha": sha,
            "repo": {"full_name": head_repository},
        },
    }


class FakeGitHubApi:
    def __init__(
        self,
        pulls: list[dict[str, object]],
        branches: dict[str, dict[str, object]],
    ) -> None:
        self.pulls = pulls
        self.branches = branches
        self.deleted: list[str] = []

    def pull_requests(self, repository: str) -> list[dict[str, object]]:
        return self.pulls

    def branch(
        self, repository: str, branch: str
    ) -> dict[str, object] | None:
        return self.branches.get(branch)

    def delete_branch(self, repository: str, branch: str) -> None:
        self.deleted.append(branch)


class CleanupMergedBranchesTests(unittest.TestCase):
    def test_dry_run_only_reports_old_merged_same_repo_branch(self) -> None:
        pulls = [
            pull_request(1, "feat/old", merged_at="2026-10-26T11:59:59Z"),
            pull_request(2, "feat/recent", merged_at="2026-10-26T12:00:01Z"),
            pull_request(3, "feat/closed", merged_at=None),
            pull_request(
                7,
                "feat/wrong-base",
                merged_at="2026-10-25T00:00:00Z",
                base="release",
            ),
            pull_request(
                4,
                "feat/fork",
                merged_at="2026-10-26T11:00:00Z",
                head_repository="contributor/SecurePort",
            ),
            pull_request(
                5,
                "main",
                merged_at="2026-10-25T00:00:00Z",
            ),
        ]
        api = FakeGitHubApi(
            pulls,
            {
                "feat/old": {
                    "name": "feat/old",
                    "protected": False,
                    "commit": {"sha": OLD_SHA},
                }
            },
        )

        deleted = cleanup_merged_branches(api, REPOSITORY, now=NOW)

        self.assertEqual(deleted, [])
        self.assertEqual(api.deleted, [])

    def test_execute_deletes_only_unprotected_unchanged_eligible_branch(self) -> None:
        pulls = [
            pull_request(1, "feat/delete", merged_at="2026-10-26T11:00:00Z"),
            pull_request(2, "feat/protected", merged_at="2026-10-25T00:00:00Z"),
            pull_request(3, "feat/advanced", merged_at="2026-10-25T00:00:00Z"),
            pull_request(4, "feat/active", merged_at="2026-10-25T00:00:00Z"),
            pull_request(5, "feat/active", merged_at=None, state="open"),
            pull_request(
                6,
                "feat/active-other-base",
                merged_at=None,
                state="open",
                base="release",
            ),
        ]
        api = FakeGitHubApi(
            pulls,
            {
                "feat/delete": {
                    "name": "feat/delete",
                    "protected": False,
                    "commit": {"sha": OLD_SHA},
                },
                "feat/protected": {
                    "name": "feat/protected",
                    "protected": True,
                    "commit": {"sha": OLD_SHA},
                },
                "feat/advanced": {
                    "name": "feat/advanced",
                    "protected": False,
                    "commit": {"sha": "b" * 40},
                },
                "feat/active-other-base": {
                    "name": "feat/active-other-base",
                    "protected": False,
                    "commit": {"sha": OLD_SHA},
                },
            },
        )

        deleted = cleanup_merged_branches(
            api,
            REPOSITORY,
            now=NOW,
            grace_period=timedelta(hours=48),
            execute=True,
        )

        self.assertEqual(deleted, ["feat/delete"])
        self.assertEqual(api.deleted, ["feat/delete"])

    def test_missing_timezone_is_rejected(self) -> None:
        api = FakeGitHubApi([], {})
        with self.assertRaisesRegex(ValueError, "timezone"):
            cleanup_merged_branches(
                api,
                REPOSITORY,
                now=datetime(2026, 10, 28, 12, 0),
            )

    def test_cleanup_rejects_shorter_grace_period_and_other_base(self) -> None:
        api = FakeGitHubApi([], {})
        with self.assertRaisesRegex(ValueError, "48 hours"):
            cleanup_merged_branches(
                api,
                REPOSITORY,
                grace_period=timedelta(hours=24),
            )
        with self.assertRaisesRegex(ValueError, "main"):
            cleanup_merged_branches(api, REPOSITORY, base="release")


if __name__ == "__main__":
    unittest.main()
