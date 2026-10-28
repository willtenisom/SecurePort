from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
PAGE_SIZE = 100
DEFAULT_GRACE_HOURS = 48
BASE_BRANCHES = {"main", "master"}
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class GitHubApiError(RuntimeError):
    """A GitHub API request failed."""


@dataclass(frozen=True)
class BranchCandidate:
    pull_number: int
    branch: str
    merged_at: datetime
    expected_sha: str


class GitHubApi:
    def __init__(self, token: str) -> None:
        if not token:
            raise GitHubApiError("GITHUB_TOKEN is required.")
        self._token = token

    def request(self, method: str, path: str) -> object | None:
        request = Request(
            f"{API_ROOT}{path}",
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "X-GitHub-Api-Version": API_VERSION,
                "User-Agent": "secureport-merged-branch-cleanup",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
        except HTTPError as error:
            if error.code == 404:
                return None
            raise GitHubApiError(
                f"GitHub API {method} {path} failed with HTTP {error.code}."
            ) from error
        except URLError as error:
            raise GitHubApiError(f"GitHub API request failed: {error.reason}") from error

        if not body:
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise GitHubApiError(f"GitHub API returned invalid JSON for {path}.") from error

    def pull_requests(self, repository: str) -> list[dict[str, object]]:
        pulls: list[dict[str, object]] = []
        page = 1
        while True:
            query = urlencode(
                {
                    "state": "all",
                    "per_page": PAGE_SIZE,
                    "page": page,
                }
            )
            result = self.request(
                "GET", f"/repos/{repository}/pulls?{query}"
            )
            if not isinstance(result, list):
                raise GitHubApiError("GitHub API did not return a pull request list.")
            pulls.extend(item for item in result if isinstance(item, dict))
            if len(result) < PAGE_SIZE:
                return pulls
            page += 1

    def branch(self, repository: str, branch: str) -> dict[str, object] | None:
        path = quote(branch, safe="")
        result = self.request("GET", f"/repos/{repository}/branches/{path}")
        if result is None:
            return None
        if not isinstance(result, dict):
            raise GitHubApiError(f"GitHub API returned invalid branch data for {branch}.")
        return result

    def delete_branch(self, repository: str, branch: str) -> None:
        path = quote(branch, safe="")
        self.request("DELETE", f"/repos/{repository}/git/refs/heads/{path}")


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if timestamp.tzinfo is None:
        return None
    return timestamp.astimezone(timezone.utc)


def eligible_branches(
    pulls: list[dict[str, object]],
    repository: str,
    base: str,
    now: datetime,
    grace_period: timedelta,
) -> list[BranchCandidate]:
    repo_name = repository.casefold()
    candidates: dict[str, BranchCandidate] = {}
    open_branches: set[str] = set()

    for pull in pulls:
        head_data = pull.get("head")
        if not isinstance(head_data, dict):
            continue
        head_repo = head_data.get("repo")
        branch = head_data.get("ref")
        if (
            pull.get("state") == "open"
            and isinstance(head_repo, dict)
            and isinstance(head_repo.get("full_name"), str)
            and head_repo["full_name"].casefold() == repo_name
            and isinstance(branch, str)
        ):
            open_branches.add(branch)

    for pull in pulls:
        base_data = pull.get("base")
        head_data = pull.get("head")
        if not isinstance(base_data, dict) or not isinstance(head_data, dict):
            continue
        if base_data.get("ref") != base:
            continue

        merged_at = parse_timestamp(pull.get("merged_at"))
        if merged_at is None or now - merged_at < grace_period:
            continue

        head_repo = head_data.get("repo")
        if not isinstance(head_repo, dict):
            continue
        full_name = head_repo.get("full_name")
        branch = head_data.get("ref")
        expected_sha = head_data.get("sha")
        number = pull.get("number")
        if (
            not isinstance(full_name, str)
            or full_name.casefold() != repo_name
            or not isinstance(branch, str)
            or not branch
            or branch.casefold() in BASE_BRANCHES
            or branch in open_branches
            or not isinstance(expected_sha, str)
            or not expected_sha
            or not isinstance(number, int)
        ):
            continue

        candidate = BranchCandidate(
            pull_number=number,
            branch=branch,
            merged_at=merged_at,
            expected_sha=expected_sha,
        )
        existing = candidates.get(branch)
        if existing is None or candidate.merged_at > existing.merged_at:
            candidates[branch] = candidate

    return sorted(candidates.values(), key=lambda candidate: candidate.branch)


def cleanup_merged_branches(
    api: GitHubApi,
    repository: str,
    base: str = "main",
    now: datetime | None = None,
    grace_period: timedelta = timedelta(hours=DEFAULT_GRACE_HOURS),
    execute: bool = False,
) -> list[str]:
    if base != "main":
        raise ValueError("Cleanup is restricted to pull requests targeting main.")
    if grace_period < timedelta(hours=DEFAULT_GRACE_HOURS):
        raise ValueError("The cleanup grace period cannot be less than 48 hours.")
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        raise ValueError("now must include a timezone.")

    pulls = api.pull_requests(repository)
    candidates = eligible_branches(pulls, repository, base, current_time, grace_period)
    changed: list[str] = []

    if not candidates:
        print("No merged pull request branches are eligible for cleanup.")
        return changed

    for candidate in candidates:
        branch_data = api.branch(repository, candidate.branch)
        if branch_data is None:
            print(f"Skip {candidate.branch}: branch already absent.")
            continue
        if branch_data.get("name") != candidate.branch:
            raise GitHubApiError(
                f"GitHub returned an unexpected branch name for {candidate.branch}."
            )
        protected = branch_data.get("protected")
        if not isinstance(protected, bool):
            raise GitHubApiError(
                f"GitHub did not report protection status for {candidate.branch}."
            )
        if protected:
            print(f"Skip {candidate.branch}: branch is protected.")
            continue
        commit = branch_data.get("commit")
        current_sha = commit.get("sha") if isinstance(commit, dict) else None
        if not isinstance(current_sha, str) or current_sha != candidate.expected_sha:
            print(f"Skip {candidate.branch}: branch has changed since its merged PR.")
            continue

        if execute:
            latest_data = api.branch(repository, candidate.branch)
            if latest_data is None:
                print(f"Skip {candidate.branch}: branch disappeared before deletion.")
                continue
            if latest_data.get("name") != candidate.branch:
                raise GitHubApiError(
                    f"GitHub returned an unexpected branch name for {candidate.branch}."
                )
            latest_protected = latest_data.get("protected")
            if not isinstance(latest_protected, bool):
                raise GitHubApiError(
                    f"GitHub did not report protection status for {candidate.branch}."
                )
            if latest_protected:
                print(f"Skip {candidate.branch}: branch became protected.")
                continue
            latest_commit = latest_data.get("commit")
            latest_sha = (
                latest_commit.get("sha")
                if isinstance(latest_commit, dict)
                else None
            )
            if latest_sha != candidate.expected_sha:
                print(f"Skip {candidate.branch}: branch changed before deletion.")
                continue
            api.delete_branch(repository, candidate.branch)
            print(
                f"Deleted origin branch {candidate.branch} "
                f"(merged PR #{candidate.pull_number})."
            )
            changed.append(candidate.branch)
        else:
            print(
                f"Dry-run: would delete origin branch {candidate.branch} "
                f"(merged PR #{candidate.pull_number})."
            )

    return changed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean remote branches for pull requests merged at least 48 hours ago."
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="Repository in owner/name form (defaults to GITHUB_REPOSITORY).",
    )
    parser.add_argument("--base", default="main", help="Target branch (default: main).")
    parser.add_argument(
        "--grace-hours",
        type=int,
        default=DEFAULT_GRACE_HOURS,
        help="Minimum age since merge (default: 48 hours).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Delete eligible remote branches. Without this flag, only report them.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.repo or not REPOSITORY_PATTERN.fullmatch(args.repo):
        print("Error: provide --repo owner/name or set GITHUB_REPOSITORY.", file=sys.stderr)
        return 2
    if args.grace_hours < DEFAULT_GRACE_HOURS:
        print("Error: --grace-hours cannot be less than 48.", file=sys.stderr)
        return 2
    if args.base != "main":
        print("Error: cleanup is restricted to PRs targeting main.", file=sys.stderr)
        return 2

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("Error: set GITHUB_TOKEN or GH_TOKEN.", file=sys.stderr)
        return 2

    api = GitHubApi(token)
    try:
        cleanup_merged_branches(
            api,
            args.repo,
            base=args.base,
            execute=args.execute,
        )
    except GitHubApiError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
