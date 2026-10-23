# Fase 3 — Eventos e painel ao vivo

- **Estado:** Rascunho
- **Dependencias:** fase 1 concluida; fase 2 recomendada para validar autorizacoes; ADR-0001 decidido.
- **Objetivo:** aceitar eventos de entrada/saida e apresentá-los em tempo real para operadores autorizados.

## Requisitos

- `F3-INGEST`: FastAPI recebe eventos simulados de entrada/saida com identificador, organizacao/unidade, origem, instante e resultado validado.
- `F3-AUTH`: autenticar e autorizar produtores de eventos; nunca aceitar tenant ou resultado de autorizacao sem validacao adequada.
- `F3-IDEMPOTENCY`: definir e aplicar comportamento para repeticao de um mesmo evento, evitando duplicacao indevida no feed e nos registros.
- `F3-WS`: publicar eventos aceitos via WebSocket apenas para clientes autenticados e autorizados no tenant correspondente.
- `F3-DASH`: React apresenta feed atualizado e estado de conexao; falha ou reconexao nao deve sugerir que o feed esta atualizado quando nao esta.
- `F3-OPENAPI`: documentar contratos HTTP e payloads; documentar o protocolo WebSocket para consumidores.

## Criterios de aceite

- Um evento valido aparece no feed de clientes autorizados do escopo correspondente.
- Clientes de outro tenant nao recebem eventos, inclusive apos reconexao.
- Payload malformado, produtor nao autenticado e tenant sem permissao sao rejeitados e nao publicados.
- A repeticao de evento segue regra idempotente especificada e testada.
- Falhas de conexao sao visiveis; ao reconectar, o cliente recupera estado de forma definida ou informa explicitamente a limitacao.
- Testes cobrem autorizacao, isolamento, validacao, duplicidade e publicacao.

## Fora de escopo

Conexao a catracas/leitores fisicos e garantia de entrega exatamente uma vez, salvo decisao posterior.

## Questoes em aberto

- Schema e versionamento de evento, autenticacao dos simuladores e garantia de entrega.
- Fonte de verdade e estrategia de recuperacao do feed apos desconexao.
- Resiliencia, limites de taxa e retencao dos eventos.
