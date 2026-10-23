# Visao de arquitetura

**Estado:** Rascunho  
**Versao:** 1

## Componentes e responsabilidades pretendidas

| Componente | Responsabilidade |
|---|---|
| React + TypeScript | Interface administrativa e operacional, autenticacao, cadastros, painel ao vivo e relatorios. O front-end nao e autoridade para permissao ou escopo de tenant. |
| Django + DRF | Nucleo administrativo: organizacoes/unidades, usuarios e papeis, cadastros, autorizacoes, regras de negocio administrativas, ORM, migrations e Django Admin interno. |
| FastAPI | Servicos de ingestao de eventos de acesso, comunicacao WebSocket para atualizacoes ao vivo e endpoints assincronos para webhooks. |
| PostgreSQL | Persistencia relacional pretendida; estrategia de compartilhamento e propriedade dos dados entre Django e FastAPI pendente de ADR. |
| Redis + Celery | Infraestrutura pretendida para tarefas assincronas e processamento de relatorios/alertas; topologia e filas ainda por definir. |
| Nginx | Proxy de entrada pretendido para a implantacao; roteamento e terminacao TLS dependem do ambiente escolhido. |

## Limites e regras

- Django e a autoridade administrativa para identidade, papeis e cadastros enquanto nao houver decisao aprovada em contrario.
- FastAPI nao deve duplicar regras administrativas nem confiar em identidade/tenant fornecidos sem validacao.
- O fluxo de eventos deve permitir associar cada evento a organizacao/unidade, origem, instante, resultado e contexto de auditoria conforme modelo a definir.
- Contratos HTTP, WebSocket e webhook precisam de autenticacao/autorizacao, validacao e documentacao OpenAPI apropriadas.
- O painel ao vivo e uma projecao de eventos aceitos, nao uma fonte de verdade para autorizar acessos.
- Compartilhar o mesmo Postgres nao significa compartilhar tabelas sem propriedade, contratos e estrategia de migrations definidos.

## Decisoes pendentes

- Integracao entre servicos: banco/tabelas compartilhados com propriedade definida ou FastAPI validando tokens emitidos pelo Django (ver ADR-0001).
- Estrategia de isolamento multi-tenant no banco e na aplicacao.
- Modelo de refresh, revogacao e expiracao de JWT.
- Transporte e garantias de entrega dos eventos entre ingestao, processamento, WebSocket e auditoria.
- Politica de retencao, privacidade, backups e recuperacao.
- Ambiente, provedor e estrategia de deploy.

Nenhuma dessas alternativas deve ser tratada como aprovada ate que o ADR relevante seja atualizado.
