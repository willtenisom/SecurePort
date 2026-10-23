# Fase 1 — Fundacao

- **Estado:** Rascunho
- **Dependencias:** nenhuma
- **Objetivo:** iniciar a plataforma com isolamento organizacional, identidade e uma interface autenticada executavel localmente.

## Requisitos

- `F1-ORG`: modelar organizacoes e unidades, associando usuarios e dados de negocio a um escopo organizacional.
- `F1-RBAC`: definir papeis e permissoes iniciais para administrador da organizacao, operador e usuario final; separar acesso interno de plataforma do acesso de tenant.
- `F1-AUTH`: oferecer login com JWT e protecao de rotas/API. Ciclo de refresh, revogacao e duracoes ficam pendentes de decisao explicita.
- `F1-ADMIN`: usar Django Admin para operacao interna sem permitir acesso cruzado acidental entre tenants.
- `F1-FRONT`: criar aplicacao React com TypeScript, fluxo de autenticacao e layout base.
- `F1-LOCAL`: fornecer Docker Compose com PostgreSQL e Redis para desenvolvimento local, mais instrucoes de inicializacao.

## Criterios de aceite

- Uma instalacao local documentada inicia os servicos da fase e permite executar migrations.
- Um usuario autenticado consegue acessar apenas funcionalidades permitidas por seu papel.
- Usuarios de organizacoes distintas nao conseguem consultar nem alterar dados um do outro, inclusive manipulando IDs na requisicao.
- Requisicoes sem autenticacao ou sem permissao recebem resposta de falha apropriada; o front-end nao e o unico controle.
- O front-end apresenta estados de autenticado, nao autenticado e erro de autenticacao sem expor tokens em logs.
- Existem testes para autenticacao, RBAC, isolamento entre dois tenants e comportamento de falha.

## Fora de escopo

Cadastros de visitantes, autorizacoes/QR, eventos de acesso e painel ao vivo pertencem as fases seguintes.

## Questoes em aberto

- Matriz exata de permissoes e escopo por unidade.
- Politica de refresh, revogacao, expiracao e armazenamento de tokens.
- Estrategia de isolamento no banco e abordagem de integracao entre Django e FastAPI.
