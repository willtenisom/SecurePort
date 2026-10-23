# Roadmap por fases

**Estado geral:** Rascunho de planejamento. A especificacao de cada fase define o comportamento e os criterios de aceite.

| Fase | Escopo | Estado | Especificacao |
|---|---|---|---|
| 1 | Fundacao, tenants, papeis, autenticacao e layout React | Nao iniciada | [phase-01-foundation.md](features/phase-01-foundation.md) |
| 2 | Cadastros, visitantes e autorizacoes com QR code | Nao iniciada | [phase-02-authorizations.md](features/phase-02-authorizations.md) |
| 3 | FastAPI, ingestao de eventos e painel ao vivo | Nao iniciada | [phase-03-live-events.md](features/phase-03-live-events.md) |
| 4 | Regras de alertas e tarefas assincronas | Nao iniciada | [phase-04-alerts.md](features/phase-04-alerts.md) |
| 5 | Ponto/escala, auditoria e relatorios | Nao iniciada | [phase-05-operations-and-reports.md](features/phase-05-operations-and-reports.md) |
| 6 | Testes finais, CI, simulador, deploy e documentacao | Nao iniciada | [phase-06-delivery.md](features/phase-06-delivery.md) |

## Regra de progressao

Uma fase so deve ser marcada como concluida quando seus criterios de aceite forem demonstrados por testes ou verificacao documentada. Dependencias de fases anteriores precisam estar atendidas; trabalho posterior pode ocorrer em paralelo somente se nao enfraquecer esses contratos.
