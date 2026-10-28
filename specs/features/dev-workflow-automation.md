# Automacao local de validacao e Pull Request

- **Estado:** Concluida
- **Tipo:** Ferramenta de desenvolvimento; fora do roadmap de runtime do produto
- **Atores:** Assistente Copilot no VS Code e desenvolvedor local
- **Dependencias:** Python 3.10+, Git, GitHub CLI (`gh`) autenticado e remote `origin`

## Problema e objetivo

Reduzir operacoes repetitivas do agente e manter mudancas importantes revisaveis: ao concluir uma tarefa de implementacao com criterios de aceite atendidos, validar, criar commit em branch de trabalho, publicar e abrir um Pull Request para aprovacao humana.

## Requisitos

- `SHIP-TRIGGER`: considerar importante uma tarefa de implementacao aprovada/concluida com criterios verificaveis; nao disparar em edicoes parciais, rascunhos, tarefas de explicacao ou quando o usuario pedir para nao commitar/publicar.
- `SHIP-VALIDATE`: executar o comando de validacao configurado no repositorio antes de criar commit; qualquer falha bloqueia stage, commit, push e PR.
- `SHIP-BRANCH`: nunca criar commit na branch base (`main`); quando estiver nela, criar branch de trabalho rastreavel pelo tipo de mudanca e ID da spec.
- `SHIP-SECRET-NAMES`: bloquear arquivos sensiveis conhecidos pelo nome/extensao; a verificacao local por nome nao substitui scanner de conteudo.
- `SHIP-COMMIT`: gerar mensagem sem IA no formato `<tipo>(<id-da-spec>): <resumo>` e incluir trailer de coautoria Copilot.
- `SHIP-PUBLISH`: publicar a branch em `origin` sem force push e criar PR direcionado a `main`.
- `SHIP-IDEMPOTENT`: ao repetir o fluxo em branch com commit valido ja existente, publicar/republicar e criar o PR se necessario, sem duplicar commit.
- `SHIP-HUMAN-REVIEW`: nunca fazer merge; revisao e merge permanecem sob controle humano.
- `SHIP-CI`: GitHub Actions executa a mesma validacao do script em Pull Requests e em pushes para `main`, e executa verificacao de segredos no CI.
- `SHIP-CLEANUP`: um workflow agendado remove apenas branches remotas do mesmo repositorio ligadas a PRs para `main` que estejam merged ha pelo menos 48 horas; PR fechado sem merge, branch de fork, branch protegida, branch usada por outro PR aberto, branch cujo SHA mudou desde o merge, `main` e `master` nunca sao removidos.
- `SHIP-CLEANUP-SAFETY`: a rotina tem modo dry-run por padrao, workflow manual so apaga com opt-in explicito, a agenda usa permissao minima `contents: write` e `pull-requests: read`, e nenhuma branch local e alterada.
- `SHIP-COPILOT`: as instrucoes do workspace dizem ao agente quando e como usar o fluxo, sem adicionar `CLAUDE.md` ou automatizar em hook de pausa/fim de sessao.
- `SHIP-LOW-CONTEXT`: titulo e corpo do PR sao gerados deterministicamente a partir de argumentos, spec ID e resumo do diff; nao usar modelo ou servico externo.

## Criterios de aceite

- O subcomando `validate` roda os testes existentes do projeto e retorna falha ao primeiro erro.
- O subcomando `ship` falha explicitamente sem argumentos validos, remote `origin`, GitHub CLI autenticado ou alteracoes/commits publicaveis.
- Se a validacao falhar, nenhum arquivo e staged e nenhum commit, push ou PR e criado.
- Tentativa de publicar a partir de `main` cria uma branch de trabalho e o commit nunca e feito na branch base.
- Arquivos sensiveis conhecidos sao bloqueados antes do stage.
- Uma mudanca validada produz no maximo um commit com titulo no padrao definido e trailer Copilot; retries nao criam commit vazio.
- Push usa `git push -u origin HEAD` sem opcoes de force.
- Um PR para `main` e aberto, ou a URL do PR existente da mesma branch e retornada; nenhum caminho executa merge.
- O workflow do GitHub usa o mesmo comando de validacao e verifica segredos em PRs.
- A limpeza agendada considera somente PRs merged para `main` ha 48 horas ou mais e branches do proprio repositorio.
- Dry-run lista branches elegiveis sem apagar; modo execute apaga somente branches elegiveis nao protegidas e sem outro PR aberto, se o SHA ainda corresponder ao PR merged, nunca branches base/protegidas ou branches locais.
- A limpeza automatizada usa permissao GitHub minima para consultar PR/branch e apagar refs, e possui testes para idade, PR nao merged, forks, branches protegidas e dry-run.
- Instrucoes do Copilot so chamam `ship` quando uma tarefa de implementacao esta concluida e validada, respeitando pedido explicito para nao publicar.
- Testes cobrem validacao dos argumentos, protecao de nomes sensiveis, criacao de titulo/branch e caminho de validacao.

## Fora de escopo

- Merge ou aprovacao de PR, force push, rebase automatico ou descarte de alteracoes.
- Exclusao de branches locais, branches de PRs fechados sem merge ou branches pertencentes a forks.
- Hooks que disparam em pausas/fim de sessao sem confirmacao dos criterios.
- Lint/testes de Django, FastAPI ou React antes de tais manifests e comandos existirem; o comando de validacao deve evoluir junto com a stack.
- Deteccao local completa de segredos por conteudo; o CI executa Gitleaks.

## Validacao atual

O repositorio atualmente tem testes Python `unittest`; o script e o CI executam `python scripts/ship.py validate`. Quando novas stacks ou suites forem adicionadas, atualizar o comando e este contrato antes de depender da automacao para elas.

Validacao de aceite anterior: 15 testes locais passaram; o fluxo criou e atualizou o PR #1 sem duplicar commit; os checks hospedados `Tests` e `Secret scan` passaram. O primeiro check do Gitleaks identificou falta de permissao `pull-requests: read`; a permissao minima foi adicionada e o re-run passou.

## Retencao de branches remotas

Uma execucao diaria verifica PRs com `merged_at` pelo menos 48 horas no passado. A limpeza cobre apenas branches head do proprio repositorio para PRs com base `main`; forks, PRs sem merge, branches protegidas, branches usadas por outro PR aberto, branches cujo SHA divergiu desde o merge e `main`/`master` sao ignorados. Dry-run e o comportamento padrao local e no disparo manual do workflow; somente a agenda ou uma confirmacao manual explicita envia o opt-in de exclusao. O GitHub pode atrasar execucoes agendadas, portanto 48 horas e o tempo minimo, nao um horario exato de exclusao. Branches locais nao sao removidas.

Validacao desta alteracao: 19 testes locais passaram, ambos os workflows foram parseados como YAML e o dry-run autenticado contra a API do repositorio nao encontrou branches elegiveis. O modo de exclusao foi exercitado com API simulada; nenhuma branch real foi apagada. No PR #2, os checks hospedados `Tests` e `Secret scan` passaram.
