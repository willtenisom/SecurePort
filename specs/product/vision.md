# Visao do produto

**Estado:** Rascunho  
**Versao:** 1

## Objetivo

Construir uma plataforma multi-tenant de gestao de acesso e ocorrencias para condominios e escolas. O sistema deve apoiar autorizacoes seguras, operacao de portaria, acompanhamento de eventos e consulta auditavel, com uma demonstracao funcional adequada a um portfolio tecnico.

## Usuarios e necessidades

- **Administrador da organizacao:** configura unidades, usuarios, papeis e regras dentro de seu escopo.
- **Morador ou responsavel:** cadastra ou solicita autorizacao de visitantes e acompanha seu estado.
- **Porteiro/operador:** consulta autorizacoes e registra ou valida acessos durante a operacao.
- **Gestor:** acompanha eventos, alertas, escalas e relatorios de sua organizacao.
- **Administrador interno da plataforma:** presta suporte operacional sem confundir seu acesso com o escopo de uma organizacao.

Papeis e permissoes detalhados ainda precisam ser aprovados na especificacao da fundacao.

## Escopo do produto

1. Fundacao administrativa: organizacoes/unidades, usuarios, papeis e autenticacao.
2. Pessoas, veiculos, visitantes e autorizacoes com validade e QR code.
3. Ingestao de eventos de entrada/saida e painel ao vivo.
4. Regras configuraveis de alerta e processamento assincrono.
5. Ponto/escala, auditoria e relatorios.
6. Testes, CI, documentacao, simulador de eventos e demonstracao publicada.

## Invariantes de negocio e seguranca

- Dados de uma organizacao nao podem ser lidos ou alterados por outra organizacao.
- Toda operacao privilegiada exige autenticacao e autorizacao no servidor.
- A unidade e o papel podem limitar o escopo de acesso dentro da organizacao; o modelo exato sera definido na fase 1.
- Uma autorizacao de visitante tem validade verificavel e seu uso deve ser rastreavel.
- Eventos e acoes administrativas relevantes devem permitir identificar ator, escopo, acao e momento, observadas as regras de privacidade e retencao ainda a definir.
- Falhas de validacao ou indisponibilidade nao podem ser representadas como acesso autorizado.

## Fora do escopo inicial

- Integracao com hardware real de catracas/leitores; a fase de demonstracao usa eventos simulados.
- Garantia de conformidade legal ou certificacao de controle de acesso sem analise especifica.
- Observabilidade Prometheus/Grafana como requisito de bloqueio; e opcional no acabamento.
- Definicoes nao aprovadas de retencao de dados, SLA, escalabilidade ou provedor de deploy.

## Medidas de sucesso

- Um fluxo completo de cada fase pode ser demonstrado conforme seus criterios de aceite.
- Testes cobrem isolamento multi-tenant, autorizacao e casos de falha relevantes.
- Um recrutador consegue explorar uma demonstracao sem precisar cadastrar manualmente os dados iniciais.
