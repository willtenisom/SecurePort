from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
BASE_BRANCH = "main"
COMMIT_TYPES = ("feat", "fix", "docs", "refactor", "test", "chore", "ci")
SPEC_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,39}$")
SENSITIVE_EXTENSIONS = {
    ".key",
    ".keystore",
    ".pem",
    ".p12",
    ".pfx",
    ".ppk",
    ".p7b",
    ".p7c",
}
SENSITIVE_FILENAMES = {
    "credentials.json",
    "id_ed25519",
    "id_rsa",
    "secrets.json",
    "service-account.json",
}
COAUTHOR_TRAILER = (
    "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
)


class ShipError(RuntimeError):
    """An expected precondition or delivery step failed."""


def run(
    command: Sequence[str],
    *,
    capture_output: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            list(command),
            cwd=ROOT,
            text=True,
            capture_output=capture_output,
            check=False,
        )
    except FileNotFoundError as error:
        raise ShipError(f"Executavel nao encontrado: {command[0]}") from error
    if check and result.returncode:
        detail = result.stderr.strip() if capture_output else ""
        message = f"Comando falhou ({result.returncode}): {' '.join(command)}"
        if detail:
            message = f"{message}\n{detail}"
        raise ShipError(message)
    return result


def validate_arguments(change_type: str, spec_id: str, summary: str) -> None:
    if change_type not in COMMIT_TYPES:
        raise ShipError(f"Tipo invalido. Use: {', '.join(COMMIT_TYPES)}.")
    if not SPEC_ID_PATTERN.fullmatch(spec_id):
        raise ShipError("ID da spec invalido; use letras, numeros, ponto, _ ou -.")
    if not summary.strip() or "\n" in summary or "\r" in summary:
        raise ShipError("O resumo deve ser uma linha nao vazia.")
    if len(commit_title(change_type, spec_id, summary)) > 72:
        raise ShipError("O titulo do commit deve ter no maximo 72 caracteres.")


def commit_title(change_type: str, spec_id: str, summary: str) -> str:
    return f"{change_type}({spec_id}): {' '.join(summary.split())}"


def branch_name(change_type: str, spec_id: str, summary: str) -> str:
    normalized = unicodedata.normalize("NFKD", summary)
    ascii_summary = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_summary).strip("-")
    slug = slug[:40].rstrip("-") or "update"
    return f"{change_type}/{spec_id.lower()}-{slug}"


def is_sensitive_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    name = normalized.rsplit("/", 1)[-1].lower()
    if name in SENSITIVE_FILENAMES:
        return True
    if name.startswith(".env") and name not in {".env.example", ".env.sample"}:
        return True
    return Path(name).suffix.lower() in SENSITIVE_EXTENSIONS


def changed_paths() -> list[str]:
    tracked = run(
        ["git", "diff", "--name-only", "-z"], capture_output=True
    ).stdout
    untracked = run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        capture_output=True,
    ).stdout
    return sorted(set(path for path in (tracked + untracked).split("\0") if path))


def has_staged_changes() -> bool:
    result = run(["git", "diff", "--cached", "--quiet"], check=False)
    if result.returncode not in (0, 1):
        raise ShipError("Nao foi possivel verificar arquivos staged.")
    return result.returncode == 1


def working_tree_is_dirty() -> bool:
    return bool(run(["git", "status", "--porcelain"], capture_output=True).stdout)


def validation_commands() -> list[list[str]]:
    return [
        [sys.executable, "-m", "compileall", "-q", "scripts", "specs_mcp", "tests"],
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-v",
        ],
    ]


def validate() -> None:
    for command in validation_commands():
        print(f"> {' '.join(command)}", flush=True)
        run(command)


def current_branch() -> str:
    return run(
        ["git", "branch", "--show-current"], capture_output=True
    ).stdout.strip()


def ensure_gh_ready() -> None:
    if shutil.which("gh") is None:
        raise ShipError(
            "GitHub CLI (gh) nao encontrado. Instale-o e autentique com `gh auth login`."
        )
    run(["gh", "auth", "status"])


def ensure_origin_and_base() -> None:
    run(["git", "remote", "get-url", "origin"])
    run(["git", "fetch", "origin", BASE_BRANCH])
    run(["git", "show-ref", "--verify", f"refs/remotes/origin/{BASE_BRANCH}"])


def ensure_no_staged_changes() -> None:
    if has_staged_changes():
        raise ShipError(
            "Ha alteracoes staged. Desfaca o stage conscientemente antes de usar ship."
        )


def check_sensitive_paths(paths: Sequence[str]) -> None:
    blocked = [path for path in paths if is_sensitive_path(path)]
    if blocked:
        listing = "\n".join(f"- {path}" for path in blocked)
        raise ShipError(
            "Arquivos com nomes/extensoes sensiveis foram bloqueados:\n"
            f"{listing}\n"
            "Essa verificacao nao detecta segredos dentro de outros arquivos."
        )


def ensure_branch(change_type: str, spec_id: str, summary: str) -> str:
    branch = current_branch()
    if branch.lower() in {BASE_BRANCH, "master"}:
        new_branch = branch_name(change_type, spec_id, summary)
        exists = run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{new_branch}"],
            check=False,
        )
        if exists.returncode == 0:
            raise ShipError(
                f"A branch {new_branch} ja existe; mude para ela antes de continuar."
            )
        if exists.returncode != 1:
            raise ShipError("Nao foi possivel verificar a branch de trabalho.")
        run(["git", "switch", "-c", new_branch])
        branch = new_branch
    if not branch:
        raise ShipError("Nao foi possivel determinar a branch atual.")
    return branch


def commit_changes(change_type: str, spec_id: str, summary: str) -> str:
    if not working_tree_is_dirty():
        return run(
            ["git", "log", "-1", "--format=%s"], capture_output=True
        ).stdout.strip()

    run(["git", "add", "-A"])
    run(["git", "diff", "--cached", "--check"])
    title = commit_title(change_type, spec_id, summary)
    run(
        [
            "git",
            "commit",
            "-m",
            title,
            "-m",
            COAUTHOR_TRAILER,
        ]
    )
    if working_tree_is_dirty():
        raise ShipError(
            "O commit gerou ou deixou alteracoes adicionais; valide-as antes do push."
        )
    return title


def ensure_commits_to_publish() -> None:
    count = run(
        ["git", "rev-list", "--count", f"origin/{BASE_BRANCH}..HEAD"],
        capture_output=True,
    ).stdout.strip()
    if not count.isdigit() or int(count) == 0:
        raise ShipError(f"Nao ha commits para publicar em {BASE_BRANCH}.")


def pull_request_body(spec_id: str) -> str:
    diff_stat = run(
        [
            "git",
            "diff",
            "--stat",
            f"origin/{BASE_BRANCH}...HEAD",
        ],
        capture_output=True,
    ).stdout.strip()
    if not diff_stat:
        diff_stat = "Sem diff de arquivos em relacao a branch base."
    return (
        f"## Spec\n`{spec_id}`\n\n"
        f"## Alteracoes\n```text\n{diff_stat}\n```\n\n"
        "## Revisao\n"
        "- [ ] Criterios de aceite da spec conferidos\n"
        "- [ ] Testes e validacoes conferidos\n"
        "- [ ] Seguranca e compatibilidade revisadas\n\n"
        "Este PR foi criado pela automacao local; o merge continua manual."
    )


def publish_pull_request(
    branch: str, title: str, spec_id: str, draft: bool
) -> str:
    existing = run(
        [
            "gh",
            "pr",
            "list",
            "--head",
            branch,
            "--json",
            "url",
            "--jq",
            ".[0].url // empty",
        ],
        capture_output=True,
    ).stdout.strip()
    if existing:
        print(f"PR existente atualizado pelo push: {existing}")
        return existing

    command = [
        "gh",
        "pr",
        "create",
        "--base",
        BASE_BRANCH,
        "--head",
        branch,
        "--title",
        title,
        "--body",
        pull_request_body(spec_id),
    ]
    if draft:
        command.append("--draft")
    url = run(command, capture_output=True).stdout.strip()
    if not url:
        raise ShipError("O GitHub CLI nao retornou a URL do Pull Request.")
    print(f"Pull Request criado: {url}")
    return url


def ship(
    change_type: str, spec_id: str, summary: str, *, draft: bool = False
) -> None:
    validate_arguments(change_type, spec_id, summary)
    ensure_gh_ready()
    ensure_origin_and_base()
    ensure_no_staged_changes()

    paths = changed_paths()
    check_sensitive_paths(paths)

    validate()
    branch = current_branch()
    if branch.lower() in {BASE_BRANCH, "master"} and not working_tree_is_dirty():
        raise ShipError(
            "Nenhuma alteracao local para enviar. A branch base nunca e publicada."
        )

    branch = ensure_branch(change_type, spec_id, summary)
    title = commit_changes(change_type, spec_id, summary)
    ensure_commits_to_publish()
    run(["git", "push", "-u", "origin", "HEAD"])
    publish_pull_request(branch, title, spec_id, draft)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida, commita, publica e abre um Pull Request revisavel."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Executa as validacoes locais configuradas.")

    ship_parser = subparsers.add_parser(
        "ship", help="Valida e publica uma tarefa concluida em um Pull Request."
    )
    ship_parser.add_argument("type", choices=COMMIT_TYPES)
    ship_parser.add_argument("spec_id")
    ship_parser.add_argument("summary")
    ship_parser.add_argument(
        "--draft", action="store_true", help="Cria o Pull Request como draft."
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            validate()
        else:
            ship(args.type, args.spec_id, args.summary, draft=args.draft)
    except ShipError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
