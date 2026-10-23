# Instrucoes do projeto

## Agente do projeto

- O agente de desenvolvimento utilizado neste projeto e o assistente de IA com Copilot SDK no VS Code.
- Ao executar tarefas neste workspace, siga estas instrucoes e o processo SDD em `specs/README.md`; nao trate a especificacao como opcional nem substitua decisoes pendentes por suposicoes.

## Fonte de verdade

- Antes de propor ou alterar comportamento, leia `specs/README.md` e as especificacoes relevantes em `specs/`.
- As especificacoes descrevem o comportamento esperado; o codigo e a fonte do comportamento implementado. Se divergirem, nao presuma qual esta correta: identifique a divergencia e atualize a especificacao junto com a mudanca acordada.
- Requisitos ainda sem decisao estao marcados como pendentes. Nao os transforme silenciosamente em decisoes de arquitetura.

## Fluxo de desenvolvimento

1. Identifique fase, atores, requisitos e criterios de aceite afetados.
2. Para comportamento novo ou alterado, atualize ou proponha a especificacao antes de implementar. Mudancas pequenas puramente internas podem referenciar uma especificacao existente sem criar outra.
3. Implemente o menor conjunto coerente que satisfaz os criterios, preservando contratos e fluxos existentes.
4. Adicione ou atualize testes que demonstrem os criterios e as protecoes relevantes; execute os comandos disponiveis no projeto.
5. Revise a rastreabilidade requisito -> implementacao -> teste e atualize o estado da fase/documentacao quando aplicavel.
6. Informe o que mudou, validacoes executadas, decisoes pendentes e limitacoes.

## Invariantes do produto

- Toda leitura ou escrita de dados de negocio deve respeitar a organizacao/unidade do usuario autenticado; nunca confiar apenas em um identificador de tenant enviado pelo cliente.
- Permissoes devem ser verificadas no servidor conforme papel e escopo. Ocultar controles no front-end nao substitui autorizacao.
- Autorizacoes de visitantes devem respeitar validade e estado; uma tentativa de validacao nao deve ignorar expiracao ou reutilizacao conforme a regra definida.
- Eventos e acoes relevantes devem manter contexto suficiente para auditoria, sem expor segredos ou dados pessoais desnecessarios em logs.
- Alteracoes de API e eventos devem considerar consumidores existentes, isolamento entre tenants e testes de regressao.

## Arquitetura e qualidade

- Respeite as responsabilidades documentadas em `specs/architecture/overview.md`. Nao mova regras de negocio entre servicos sem atualizar a especificacao e registrar a decisao.
- Nao escolha entre banco compartilhado e validacao de JWT pelo FastAPI ate resolver o ADR correspondente.
- Siga os padroes existentes de linguagem, formatacao, dependencias e testes quando o codigo for criado. Nao invente comandos de build ou teste: verifique os manifests do projeto.
- Documente contratos e comportamento observavel; erros devem ser explicitos e nao convertidos em sucesso aparente.
