# ADR-0001: Integracao de dados e identidade entre Django e FastAPI

- **Estado:** Proposto — decisao pendente
- **Data:** 2026-10-22
- **Contexto:** A plataforma usa Django/DRF como nucleo administrativo e FastAPI para ingestao de eventos, WebSockets e webhooks. Ambos precisam de identidade, escopo de organizacao e dados confiaveis sem criar inconsistencias de autorizacao.

## Opcoes consideradas

### A. PostgreSQL compartilhado

Os servicos acessam o mesmo banco, com propriedade explicita de tabelas, contratos de leitura/escrita e migrations coordenadas.

- Vantagens: acesso direto a dados e menor duplicacao para alguns fluxos.
- Riscos: acoplamento de schema, migrations concorrentes, bypass de regras do ORM e isolamento de tenant inconsistente.

### B. FastAPI valida tokens emitidos pelo Django

Django permanece autoridade de identidade; FastAPI valida tokens e recebe claims suficientes para autorizacao, consultando dados adicionais por uma interface definida quando necessario.

- Vantagens: fronteira de servico mais explicita e menor acoplamento ao schema Django.
- Riscos: exige regras claras de expiracao, revogacao, rotacao de chaves, claims e consistencia dos dados de autorizacao.

## Criterios para decidir

- Isolamento multi-tenant verificavel em todos os caminhos.
- Regras de autorizacao e revogacao coerentes entre os servicos.
- Operacao local e deploy reproduziveis.
- Propriedade de dados e migrations sem ambiguidades.
- Complexidade apropriada para o portfolio e testes que provem os limites.

## Consequencias e proximo passo

Nenhuma opcao esta aprovada. Antes da fase 3, comparar as opcoes com os criterios acima e registrar a decisao, incluindo estrategia de claims/tenant, migrations e testes de integracao. Ate la, especificacoes devem preservar ambas as possibilidades sem assumir acesso direto ao banco ou validacao JWT no FastAPI.
