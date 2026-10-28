from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath


SPECS_ROOT = Path(__file__).resolve().parent.parent / "specs"
MAX_RESULT_CHARS = 900
MAX_READ_CHARS = 8000
DEFAULT_RESULT_COUNT = 3
MAX_RESULT_COUNT = 5
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


@dataclass(frozen=True)
class SpecChunk:
    path: str
    heading: str
    text: str


@dataclass(frozen=True)
class SearchResult:
    path: str
    heading: str
    text: str
    score: float


def _tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return _TOKEN_PATTERN.findall(ascii_text)


def list_spec_paths(root: Path = SPECS_ROOT) -> list[str]:
    resolved_root = root.resolve(strict=True)
    paths = []
    for path in resolved_root.rglob("*.md"):
        if path.is_file():
            resolved_path = path.resolve(strict=True)
            try:
                resolved_path.relative_to(resolved_root)
            except ValueError:
                raise ValueError("A arvore specs/ contem um link fora da raiz.") from None
            paths.append(path.relative_to(resolved_root).as_posix())
    return sorted(paths)


def resolve_spec_path(path: str, root: Path = SPECS_ROOT) -> Path:
    if not path:
        raise ValueError("O caminho da especificacao nao pode ser vazio.")

    posix_path = PurePosixPath(path)
    windows_path = PureWindowsPath(path)
    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or ".." in posix_path.parts
        or ".." in windows_path.parts
    ):
        raise ValueError("Informe um caminho relativo dentro de specs/.")

    resolved_root = root.resolve(strict=True)
    resolved_path = (resolved_root / Path(path)).resolve(strict=True)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        raise ValueError("O caminho precisa permanecer dentro de specs/.") from None
    if not resolved_path.is_file() or resolved_path.suffix.lower() != ".md":
        raise ValueError("Somente arquivos Markdown dentro de specs/ podem ser lidos.")
    return resolved_path


def read_spec(path: str, root: Path = SPECS_ROOT) -> str:
    return resolve_spec_path(path, root).read_text(encoding="utf-8")


def _split_long_text(text: str, max_chars: int = 1200) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        while len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            split_at = paragraph.rfind(" ", 0, max_chars + 1)
            if split_at <= 0:
                split_at = max_chars
            chunks.append(paragraph[:split_at].strip())
            paragraph = paragraph[split_at:].strip()

        if not paragraph:
            continue
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()

    if current:
        chunks.append(current)
    return chunks


def _document_chunks(path: str, text: str) -> list[SpecChunk]:
    chunks: list[SpecChunk] = []
    heading = "Documento"
    section_lines: list[str] = []

    def flush_section() -> None:
        content = "\n".join(section_lines).strip()
        for part in _split_long_text(content):
            chunks.append(SpecChunk(path=path, heading=heading, text=part))

    for line in text.splitlines():
        match = _HEADING_PATTERN.match(line)
        if match:
            flush_section()
            heading = match.group(2).strip()
            section_lines.clear()
        else:
            section_lines.append(line)
    flush_section()
    return chunks


def _bm25_score(
    query_tokens: list[str],
    chunk_tokens: list[str],
    document_frequencies: dict[str, int],
    document_count: int,
    average_length: float,
) -> float:
    frequencies: dict[str, int] = {}
    for token in chunk_tokens:
        frequencies[token] = frequencies.get(token, 0) + 1

    score = 0.0
    length = len(chunk_tokens)
    for token in set(query_tokens):
        term_frequency = frequencies.get(token, 0)
        if not term_frequency:
            continue
        frequency = document_frequencies[token]
        inverse_frequency = math.log(
            1 + (document_count - frequency + 0.5) / (frequency + 0.5)
        )
        denominator = term_frequency + 1.5 * (
            1 - 0.75 + 0.75 * length / average_length
        )
        score += inverse_frequency * term_frequency * 2.5 / denominator
    return score


def _bounded_excerpt(text: str) -> str:
    if len(text) <= MAX_RESULT_CHARS:
        return text
    marker = "[trecho truncado]"
    end = MAX_RESULT_CHARS - len(marker) - 1
    boundary = text.rfind(" ", 0, end)
    if boundary > 0:
        end = boundary
    return f"{text[:end].rstrip()} {marker}"


def search_specs(
    query: str, limit: int = DEFAULT_RESULT_COUNT, root: Path = SPECS_ROOT
) -> list[SearchResult]:
    if not query.strip():
        raise ValueError("Informe termos para buscar nas especificacoes.")
    if not 1 <= limit <= MAX_RESULT_COUNT:
        raise ValueError(f"O limite deve estar entre 1 e {MAX_RESULT_COUNT}.")

    query_tokens = _tokens(query)
    if not query_tokens:
        raise ValueError("A consulta precisa conter ao menos uma palavra ou numero.")

    chunks = []
    for path in list_spec_paths(root):
        chunks.extend(_document_chunks(path, read_spec(path, root)))

    tokenized_chunks = [
        _tokens(f"{chunk.heading} {chunk.text}") for chunk in chunks
    ]
    document_frequencies: dict[str, int] = {}
    for tokens in tokenized_chunks:
        for token in set(tokens):
            document_frequencies[token] = document_frequencies.get(token, 0) + 1

    if not chunks:
        return []

    average_length = max(
        sum(map(len, tokenized_chunks)) / len(tokenized_chunks), 1.0
    )
    results = []
    for chunk, tokens in zip(chunks, tokenized_chunks):
        score = _bm25_score(
            query_tokens,
            tokens,
            document_frequencies,
            len(chunks),
            average_length,
        )
        if score > 0:
            results.append(
                SearchResult(
                    path=chunk.path,
                    heading=chunk.heading,
                    text=_bounded_excerpt(chunk.text),
                    score=score,
                )
            )

    return sorted(
        results, key=lambda result: (-result.score, result.path, result.heading)
    )[:limit]
