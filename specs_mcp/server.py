from mcp.server.fastmcp import FastMCP

from specs_mcp.retrieval import (
    DEFAULT_RESULT_COUNT,
    MAX_READ_CHARS,
    list_spec_paths,
    read_spec as get_spec_content,
    search_specs as find_spec_matches,
)


mcp = FastMCP("secureport-specs")


@mcp.tool()
def list_specs() -> str:
    """Liste os arquivos Markdown de especificacao disponiveis."""
    return "\n".join(list_spec_paths())


@mcp.tool()
def search_specs(query: str, limit: int = DEFAULT_RESULT_COUNT) -> str:
    """Busque trechos relevantes nas specs; retorna no maximo cinco trechos curtos."""
    results = find_spec_matches(query, limit)
    if not results:
        return "Nenhum trecho correspondente encontrado nas especificacoes."

    formatted = []
    for result in results:
        formatted.append(
            f"Fonte: specs/{result.path} | {result.heading}\n{result.text}"
        )
    return "\n\n---\n\n".join(formatted)


@mcp.tool()
def read_spec(path: str) -> str:
    """Leia uma especificacao Markdown por caminho relativo a specs/."""
    content = get_spec_content(path)
    if len(content) > MAX_READ_CHARS:
        return (
            content[:MAX_READ_CHARS]
            + "\n\n[Conteudo truncado no limite de 8.000 caracteres.]"
        )
    return content


if __name__ == "__main__":
    mcp.run(transport="stdio")
