import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from specs_mcp.retrieval import (
    MAX_RESULT_CHARS,
    list_spec_paths,
    read_spec,
    resolve_spec_path,
    search_specs,
)


class SpecsRetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "specs"
        self.root.mkdir()
        (self.root / "access.md").write_text(
            "# Acesso\n\nVisitantes usam QR code com validade e autorizacao.\n\n"
            "## Regras\n\nA expiracao impede acesso nao autorizado.",
            encoding="utf-8",
        )
        (self.root / "reports.md").write_text(
            "# Relatorios\n\nExportacao de CSV para administradores.",
            encoding="utf-8",
        )
        (self.root / "ignore.txt").write_text("nao e uma spec", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_lists_only_markdown_specs(self) -> None:
        self.assertEqual(
            list_spec_paths(self.root), ["access.md", "reports.md"]
        )

    def test_search_ranks_matching_spec_and_limits_results(self) -> None:
        results = search_specs("QR code validade visitante", limit=1, root=self.root)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].path, "access.md")
        self.assertLessEqual(len(results[0].text), MAX_RESULT_CHARS)

    def test_search_requires_query_and_valid_limit(self) -> None:
        with self.assertRaises(ValueError):
            search_specs("   ", root=self.root)
        with self.assertRaises(ValueError):
            search_specs("acesso", limit=6, root=self.root)

    def test_search_marks_truncated_excerpts_within_character_limit(self) -> None:
        long_text = "termochave " + ("conteudo longo " * 120)
        (self.root / "long.md").write_text(
            f"# Longo\n\n{long_text}", encoding="utf-8"
        )

        results = search_specs("termochave", limit=1, root=self.root)

        self.assertIn("[trecho truncado]", results[0].text)
        self.assertLessEqual(len(results[0].text), MAX_RESULT_CHARS)

    def test_reads_relative_markdown_path(self) -> None:
        self.assertIn("Visitantes usam QR code", read_spec("access.md", self.root))

    def test_rejects_traversal_absolute_and_non_markdown_paths(self) -> None:
        invalid_paths = [
            "../outside.md",
            str(self.root / "access.md"),
            "ignore.txt",
        ]
        for path in invalid_paths:
            with self.subTest(path=path), self.assertRaises(
                (ValueError, OSError)
            ):
                resolve_spec_path(path, self.root)

    def test_rejects_symlink_outside_specs_root(self) -> None:
        outside = Path(self.temporary_directory.name) / "outside.md"
        outside.write_text("outside", encoding="utf-8")

        original_resolve = Path.resolve

        def resolve_external_link(path, *args, **kwargs):
            if path == self.root / "external.md":
                return outside
            return original_resolve(path, *args, **kwargs)

        with patch.object(Path, "resolve", resolve_external_link):
            with self.assertRaises(ValueError):
                resolve_spec_path("external.md", self.root)


if __name__ == "__main__":
    unittest.main()
