# Fase 2 — Cadastros e autorizacoes

- **Estado:** Rascunho
- **Dependencias:** fase 1 concluida; modelo de tenant e permissoes acordado.
- **Objetivo:** permitir gerenciar pessoas, veiculos e visitantes e autorizar visitas por QR code com validade.

## Requisitos

- `F2-PEOPLE`: cadastrar e consultar pessoas e veiculos dentro do escopo permitido.
- `F2-VISITOR`: criar autorizacoes de visitante associadas a organizacao/unidade e ao solicitante autorizado.
- `F2-QR`: emitir um QR code que represente uma autorizacao com validade; nao incluir dados pessoais desnecessarios diretamente no codigo.
- `F2-VALIDATE`: permitir que operador autorizado valide a autorizacao e receba um resultado explicito, sem confundir expirado, inexistente, revogado ou valido.
- `F2-AUDIT`: registrar criacao, alteracao, revogacao e tentativa de validacao com ator, escopo e instante.
- `F2-UI`: oferecer telas React para cadastros, criacao e consulta de autorizacoes.

## Criterios de aceite

- Um usuario nao consegue listar, consultar ou alterar pessoas, veiculos ou autorizacoes de outro tenant.
- QR expirado, revogado ou desconhecido nunca resulta em validacao positiva.
- Tentativas repetidas sao tratadas conforme uma regra de uso/reutilizacao aprovada; a regra ainda precisa ser definida antes de fechar o comportamento.
- Operacoes privilegiadas sao autorizadas no servidor e ficam auditadas.
- Testes cobrem validade nos limites temporais, revogacao, tenant incorreto, papel sem permissao e QR invalido.

## Fora de escopo

Integracao com hardware de leitura real e ingestao de eventos em tempo real.

## Questoes em aberto

- QR de uso unico ou reutilizavel; regra de consumo atomico.
- Precisao de fuso horario e regras de horario/validade por organizacao.
- Campos de pessoa/veiculo, consentimento, retencao e minimizacao de dados.
