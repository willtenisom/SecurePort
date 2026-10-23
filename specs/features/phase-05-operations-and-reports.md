# Fase 5 — Operacao, auditoria e relatorios

- **Estado:** Rascunho
- **Dependencias:** fases 1 a 4 conforme os dados usados nos relatorios.
- **Objetivo:** apoiar controle de ponto/escala e consulta auditavel de operacoes e fluxo.

## Requisitos

- `F5-SHIFT`: registrar escalas de funcionarios com escopo, papel e regras de acesso definidos.
- `F5-TIME`: registrar eventos de ponto necessarios ao relatorio, distinguindo dado original de correcao administrativa.
- `F5-AUDIT`: manter trilha auditavel de quem fez o que, quando e em qual escopo; correcoes devem ser adicionais e rastreaveis, nao apagar silenciosamente o historico.
- `F5-REPORT`: oferecer consultas e dashboards de fluxo por horario e ocorrencias, respeitando tenant e permissao.
- `F5-EXPORT`: exportar dados permitidos em CSV e PDF, com validacao de escopo e filtros explicitos.

## Criterios de aceite

- Usuarios autorizados consultam somente dados do proprio escopo; exportacoes aplicam as mesmas regras.
- Auditoria registra ator, acao, instante e contexto suficiente sem armazenar segredos.
- Correcao de registro preserva evidencia do valor anterior e do responsavel pela alteracao.
- Relatorios apresentam intervalo e fuso horario claramente, e filtros nao ampliam o escopo do usuario.
- Testes cobrem permissao, exportacao, isolamento, correcao e consistencia de agregacoes.

## Fora de escopo

Integracao com folha de pagamento ou afirmacao de conformidade legal trabalhista.

## Questoes em aberto

- Regras de jornada, arredondamento, aprovacao e correcao de ponto.
- Retencao e acesso a trilha de auditoria.
- Limites e formato de exportacao para grandes volumes.
