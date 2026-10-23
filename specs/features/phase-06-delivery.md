# Fase 6 — Qualidade e demonstracao

- **Estado:** Rascunho
- **Dependencias:** fluxos principais implementados e especificacoes atualizadas.
- **Objetivo:** tornar o produto verificavel, reproduzivel e demonstravel por terceiros.

## Requisitos

- `F6-TESTS`: executar testes do back-end e front-end no CI (pytest e Vitest/Testing Library conforme stack aprovada).
- `F6-CI`: verificar testes e qualidade essencial em GitHub Actions antes de integrar mudancas.
- `F6-OPENAPI`: publicar/documentar OpenAPI dos servicos e manter contratos atualizados.
- `F6-DOCS`: README inclui inicializacao, arquitetura, limites conhecidos e diagrama atualizado.
- `F6-SIMULATOR`: fornecer simulador de eventos sem credenciais privilegiadas embutidas, com dados de demonstracao nao sensiveis.
- `F6-DEPLOY`: publicar ambiente de demonstracao com configuracao e segredos gerenciados fora do codigo-fonte.
- `F6-OBSERVABILITY`: avaliar logs estruturados e Prometheus/Grafana como melhoria opcional, sem expor tokens ou dados pessoais desnecessarios.

## Criterios de aceite

- Um novo desenvolvedor consegue seguir o README para iniciar o projeto e executar verificacoes.
- CI executa verificacoes documentadas e falha quando testes obrigatorios falham.
- O simulador consegue produzir eventos visiveis no painel sem acesso a dados reais ou privilegios administrativos.
- A demonstracao publicada informa como usar o fluxo e nao exige cadastro manual para ver dados demonstrativos.
- Segredos nao estao no repositorio; acesso a ambiente demonstrativo e limitado conforme risco e custo.
- Documentacao reflete arquitetura e comportamento realmente implementados.

## Fora de escopo

Disponibilidade garantida, certificacao de seguranca, ou instrumentacao completa de observabilidade.

## Questoes em aberto

- Provedor, custos, limites, politica de suspensao e manutencao do deploy.
- Dados de demonstracao, reset/seed e protecao contra abuso.
- Gates de cobertura, lint e verificacoes de seguranca que o CI exigira.
