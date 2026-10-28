# Ferramenta MCP local para as especificacoes

- **Estado:** Concluida
- **Tipo:** Ferramenta de desenvolvimento; fora do roadmap de runtime do produto
- **Atores:** Assistente Copilot no VS Code e desenvolvedor local
- **Dependencias:** Python 3.10 ou superior; dependencias declaradas no projeto

## Problema e objetivo

Permitir ao agente consultar requisitos relevantes sem inserir todo o corpus de especificacoes no contexto de cada tarefa. O servidor executa localmente, comunica-se por MCP stdio e nao usa servicos externos.

## Requisitos

- `MCP-SPECS-LIST`: listar caminhos relativos de arquivos Markdown sob `specs/`.
- `MCP-SPECS-SEARCH`: recuperar trechos relevantes por busca lexical local; sem embeddings, LLM adicional, rede ou telemetria.
- `MCP-SPECS-READ`: ler uma especificacao Markdown especifica usando caminho relativo dentro de `specs/`.
- `MCP-SPECS-BOUNDS`: limitar a busca a no maximo cinco resultados, com tres por padrao e no maximo 900 caracteres por trecho.
- `MCP-SPECS-SAFETY`: rejeitar caminho absoluto, traversal, arquivos fora de `specs/`, links que escapem do diretorio e arquivos que nao sejam Markdown.
- `MCP-SPECS-RO`: expor apenas operacoes de leitura; nao escrever, criar ou remover arquivos.
- `MCP-SPECS-VSCODE`: disponibilizar configuracao local para iniciar o servidor no VS Code com o Python do projeto.

## Criterios de aceite

- Uma consulta por termos presentes em uma especificacao retorna primeiro trechos que contenham esses termos, com o caminho de origem.
- A busca devolve ate tres trechos por padrao, permite no maximo cinco e limita cada trecho a 900 caracteres.
- Consultas sem correspondencias retornam uma resposta explicita de nenhum resultado.
- A ferramenta de leitura retorna o conteudo da especificacao solicitada, com limite de 8.000 caracteres e aviso quando truncado.
- Listagem, busca e leitura nao alteram nenhum arquivo.
- Caminhos absolutos, `..`, caminhos fora da raiz, links escapando da raiz e extensoes diferentes de `.md` sao recusados.
- O servidor MCP inicializa por stdio sem escrever logs/progresso em stdout.
- Testes automatizados cobrem ranking, limites, caminho permitido, traversal e ausencia de alteracao.

## Fora de escopo

- Indexacao vetorial, embeddings, modelos de linguagem, servicos externos, banco de dados ou daemon HTTP.
- Busca semantica perfeita; consultas devem usar palavras relacionadas ao conteudo documentado.
- Consulta de codigo-fonte ou de arquivos fora de `specs/`.

## Verificacao

Testes unitarios da recuperacao e validacao dos caminhos; teste manual/protocolo de inicializacao MCP usando a configuracao de VS Code.
