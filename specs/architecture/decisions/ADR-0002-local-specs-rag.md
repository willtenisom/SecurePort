# ADR-0002: RAG local para consulta das especificacoes

- **Estado:** Aprovado
- **Data:** 2026-10-28
- **Contexto:** O agente precisa consultar a fonte versionada de requisitos sem carregar todo o diretorio `specs/` em cada tarefa. A busca deve ser local, simples de operar e economica em contexto.

## Decisao

Implementar um servidor MCP Python por stdio que oferece listagem, leitura direcionada e busca lexical nos arquivos Markdown sob `specs/`. A busca seleciona trechos relevantes e limita tanto a quantidade de resultados quanto o tamanho de cada trecho. O servidor e somente-leitura e nao recebe dados do produto.

## Alternativas consideradas

- **Embeddings/vector store local:** potencialmente melhora busca semantica, mas adiciona dependencias, indexacao/armazenamento e configuracao desnecessarios para o pequeno conjunto atual de specs.
- **Servico remoto ou API de embeddings:** adiciona rede, credenciais e custo, contrariando o objetivo de consulta local economica.
- **Busca lexical com biblioteca adicional:** dispensavel para o corpus pequeno; a implementacao pode usar apenas a biblioteca padrao do Python.

## Consequencias

- Nao ha custo de tokens/API para indexacao; o agente recebe somente os trechos solicitados.
- Consultas por sinonimos ou conceitos sem termos em comum podem nao encontrar o trecho correto; nesse caso, o agente pode listar ou ler uma especificacao diretamente.
- Resultados nao substituem a leitura da especificacao completa quando a tarefa exigir contexto integral.
- O SDK oficial Python do MCP e a unica dependencia runtime; usa-se a API FastMCP da linha 1.x para manter a implementacao simples e estavel.
