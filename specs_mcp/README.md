# MCP local para consultar as specs

Servidor MCP somente-leitura para o agente consultar as especificacoes sem carregar o diretorio inteiro no contexto. A recuperacao e lexical (BM25), local e sem embeddings, API externa ou telemetria. Requer Python 3.10 ou superior.

## Preparar no Windows

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-mcp.txt
```

Abra ou recarregue o workspace no VS Code e inicie `secureport-specs` em **MCP: List Servers**. A configuracao em `.vscode/mcp.json` usa o Python do ambiente virtual do projeto.

## Ferramentas MCP

- `list_specs`: lista apenas caminhos relativos de arquivos Markdown em `specs/`.
- `search_specs`: busca por termos e devolve tres trechos por padrao, no maximo cinco; cada trecho tem ate 900 caracteres.
- `read_spec`: le um arquivo solicitado por caminho relativo e limita o retorno a 8.000 caracteres.

Todos os caminhos sao confinados a `specs/`; caminhos absolutos, traversal e arquivos fora do formato Markdown sao recusados. O servidor usa stdio, nao escreve na arvore de specs e deve ser usado por um cliente MCP, nao iniciado em um terminal interativo.

## Testes

```powershell
python -m unittest discover -s tests
```
