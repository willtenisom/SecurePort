# Fase 4 — Regras e alertas

- **Estado:** Rascunho
- **Dependencias:** fase 3 concluida; estrategia de processamento assincrono acordada.
- **Objetivo:** avaliar eventos segundo regras configuraveis e notificar usuarios autorizados.

## Requisitos

- `F4-RULES`: permitir configurar regras por organizacao, com parametros e estado habilitado/desabilitado.
- `F4-THRESHOLD`: suportar uma regra de referencia: alertar apos tres tentativas de acesso nao autorizado em dez minutos.
- `F4-SCHEDULE`: suportar regra de referencia para acesso fora do horario configurado, apos definicao de fuso e calendario.
- `F4-ASYNC`: processar tarefas assincronas usando Celery/Redis, com tratamento observavel de erro e retentativas limitadas conforme politica definida.
- `F4-NOTIFY`: apresentar alertas a usuarios com permissao e escopo adequados; evitar vazamento entre tenants.

## Criterios de aceite

- Alterar uma regra em uma organizacao nao muda o comportamento de outra.
- A regra de tres tentativas produz o alerta de acordo com a janela temporal especificada, sem contar eventos de tenant diferente.
- Eventos duplicados nao geram contagens/alertas duplicados indevidos.
- Indisponibilidade ou falha de tarefa nao e reportada como processamento concluido; falhas sao observaveis e recuperaveis conforme politica.
- Testes cobrem limites da janela, fuso horario, desativacao da regra, idempotencia e isolamento.

## Fora de escopo

Modelos de machine learning, notificacoes externas e canais SMS/e-mail, salvo aprovacao posterior.

## Questoes em aberto

- Definicao de horario, calendario, feriados e fuso por organizacao.
- Agrupamento, deduplicacao, severidade, silenciamento e ciclo de vida de alertas.
- Politica de retry, dead-letter e monitoramento de tarefas.
