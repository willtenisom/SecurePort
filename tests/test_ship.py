import unittest
from subprocess import CompletedProcess
from unittest.mock import patch

from scripts.ship import (
    ShipError,
    branch_name,
    commit_title,
    ensure_branch,
    ensure_gh_ready,
    is_sensitive_path,
    ship,
    validate_arguments,
)


class ShipHelpersTests(unittest.TestCase):
    def test_builds_conventional_commit_title(self) -> None:
        self.assertEqual(
            commit_title("feat", "F1-AUTH", "login   com JWT"),
            "feat(F1-AUTH): login com JWT",
        )

    def test_builds_cross_platform_branch_slug(self) -> None:
        self.assertEqual(
            branch_name("feat", "F1-AUTH", "autorização de visitante"),
            "feat/f1-auth-autorizacao-de-visitante",
        )

    def test_rejects_invalid_type_spec_and_multiline_summary(self) -> None:
        with self.assertRaises(ShipError):
            validate_arguments("feature", "F1", "Login")
        with self.assertRaises(ShipError):
            validate_arguments("feat", "../F1", "Login")
        with self.assertRaises(ShipError):
            validate_arguments("feat", "F1", "Login\nsegundo commit")

    def test_rejects_commit_titles_over_72_characters(self) -> None:
        with self.assertRaises(ShipError):
            validate_arguments("feat", "F1", "x" * 64)

    def test_blocks_common_secret_file_names_but_allows_templates(self) -> None:
        for path in (".env", "config/.env.prod", "certs/server.pem", "id_rsa"):
            with self.subTest(path=path):
                self.assertTrue(is_sensitive_path(path))
        self.assertFalse(is_sensitive_path(".env.example"))
        self.assertFalse(is_sensitive_path("src/settings.py"))

    def test_missing_github_cli_fails_with_setup_instructions(self) -> None:
        with patch("scripts.ship.shutil.which", return_value=None):
            with self.assertRaisesRegex(ShipError, "gh auth login"):
                ensure_gh_ready()

    def test_creates_a_task_branch_instead_of_committing_on_main(self) -> None:
        completed = CompletedProcess([], 0, stdout="", stderr="")
        missing_branch = CompletedProcess([], 1, stdout="", stderr="")
        with (
            patch("scripts.ship.current_branch", return_value="main"),
            patch(
                "scripts.ship.run",
                side_effect=[missing_branch, completed],
            ) as run_command,
        ):
            result = ensure_branch("feat", "F1-AUTH", "login")

        self.assertEqual(result, "feat/f1-auth-login")
        self.assertEqual(
            run_command.call_args_list[1].args[0],
            ["git", "switch", "-c", "feat/f1-auth-login"],
        )

    def test_validation_failure_stops_before_branch_or_commit(self) -> None:
        with (
            patch("scripts.ship.ensure_gh_ready"),
            patch("scripts.ship.ensure_origin_and_base"),
            patch("scripts.ship.ensure_no_staged_changes"),
            patch("scripts.ship.changed_paths", return_value=["src/app.py"]),
            patch("scripts.ship.validate", side_effect=ShipError("test failed")),
            patch("scripts.ship.ensure_branch") as ensure_branch,
            patch("scripts.ship.commit_changes") as commit_changes,
        ):
            with self.assertRaisesRegex(ShipError, "test failed"):
                ship("feat", "F1-AUTH", "login")

        ensure_branch.assert_not_called()
        commit_changes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
