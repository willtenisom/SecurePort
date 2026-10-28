# Spec-Driven Development

Este diretorio e a fonte versionada dos requisitos e das decisoes do produto. A especificacao inicial foi derivada da proposta do projeto; ela nao afirma que funcionalidades ja estao implementadas.

## Estrutura

- `product/vision.md`: objetivo, usuarios, escopo e invariantes.
- `architecture/overview.md`: limites entre componentes e infraestrutura pretendida.
- `architecture/decisions/`: decisoes arquiteturais (ADRs), incluindo opcoes ainda pendentes.
- `features/local-specs-mcp.md`: servidor MCP local somente-leitura para consulta compacta das especificacoes.
- `features/`: requisitos e criterios de aceite por fase.
- `roadmap.md`: sequencia, dependencias e estado das fases.
- `templates/feature-spec.md`: modelo para novas funcionalidades ou mudancas relevantes.

O servidor MCP das especificacoes e uma ferramenta local de desenvolvimento, fora das seis fases do produto; veja `features/local-specs-mcp.md`.

## Fluxo para cada mudanca

1. **Descobrir:** leia esta pagina, a visao, a arquitetura, a fase afetada e o codigo/testes existentes.
2. **Especificar:** crie ou atualize uma especificacao quando o comportamento, contrato, permissao, dado ou criterio de aceite mudar. Use requisitos com IDs estaveis (`F1-...`) e criterios observaveis.
3. **Resolver:** registre decisoes de arquitetura no ADR pertinente. Pergunte antes de escolher quando uma decisao pendente alterar limites de servico, seguranca, dados ou UX de forma significativa.
4. **Implementar:** faca mudancas coerentes com requisitos e contratos existentes; mantenha isolamento de tenant e autorizacao no servidor.
5. **Verificar:** teste criterios de aceite, casos negativos, permissoes e regressao nos fluxos afetados. Nao declare criterio atendido sem evidencias.
6. **Fechar o ciclo:** atualize especificacao, roadmap e documentacao relacionada; reporte criterios atendidos, testes executados e pendencias.

## Estados

- `Rascunho`: proposta inicial, pode conter decisoes pendentes.
- `Aprovada`: comportamento e criterios acordados; pode ser implementada.
- `Em andamento`: implementacao iniciada.
- `Concluida`: criterios de aceite verificados e documentacao sincronizada.
- `Adiada`: fora do ciclo atual, com motivo registrado.

Uma especificacao nao substitui testes nem autoriza ampliar o escopo. Quando codigo e especificacao divergirem, registre a divergencia e confirme a intencao antes de remover comportamento existente.
