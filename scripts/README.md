# Entrega de tarefas validadas

Use `ship` somente ao concluir uma tarefa de implementacao cuja spec foi aprovada e cujos criterios de aceite foram atendidos. O script valida, cria commit em branch de trabalho, publica em `origin` e abre um Pull Request para revisao humana. Ele nunca faz merge nem force push.

## Requisitos

- Python 3.10 ou superior
- Git com remote `origin` configurado
- GitHub CLI instalado e autenticado (`gh auth login`)

## Uso

```powershell
python scripts/ship.py validate
python scripts/ship.py ship feat F1-AUTH "login com JWT"
python scripts/ship.py ship feat F1-AUTH "login com JWT" --draft
```

Tipos aceitos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore` e `ci`. O ID deve referenciar a spec relacionada. O script usa mensagem no formato `feat(F1-AUTH): login com JWT`.

Se a branch atual for `main` ou `master`, uma branch de tarefa sera criada. Em qualquer outra branch, o script continua nela. Alteracoes ja staged sao recusadas para nao sobrescrever selecao manual. Antes de usar, confirme que as alteracoes do worktree pertencem apenas a tarefa que sera enviada, pois arquivos nao staged serao staged juntos.

O comando `validate` e a unica fonte de validacao usada localmente e no CI. Hoje executa compilacao/sintaxe Python e `unittest`; quando outras stacks forem adicionadas, atualize `validation_commands()` em `scripts/ship.py`, este documento e as specs antes de depender do fluxo para essas stacks.

A protecao local de arquivos sensiveis e baseada em nomes/extensoes e nao detecta chaves ou tokens dentro de arquivos comuns. O workflow do GitHub executa Gitleaks como verificacao de conteudo em Pull Requests.

## Limpeza de branches merged

`.github/workflows/cleanup-merged-branches.yml` executa diariamente e apaga branches remotas do mesmo repositorio associadas a PRs para `main` que foram merged ha pelo menos 48 horas. Branches protegidas, `main`, `master`, branches de forks, branches com outro PR aberto e branches cujo SHA mudou desde o merge sao ignorados. Branches locais nunca sao removidas.

O script `scripts/cleanup_merged_branches.py` usa dry-run por padrao. A exclusao exige `--execute`; o workflow agendado passa essa opcao com `contents: write` e `pull-requests: read`. O disparo manual do workflow tambem e dry-run por padrao e so apaga com a entrada explicita `delete_eligible=true`. Para uma simulacao manual local, defina `GITHUB_TOKEN` e `GITHUB_REPOSITORY=owner/repo`, depois execute:

```powershell
python scripts/cleanup_merged_branches.py
```

Uma execucao agendada pode atrasar; 48 horas e o limite minimo, nao um instante garantido.

## Recuperacao

Se o push foi concluido mas a criacao do PR falhou, execute novamente o mesmo comando na branch de tarefa; o script nao cria commit vazio e tenta criar ou localizar o PR existente.

Nao use o comando se o usuario pedir explicitamente para nao commitar ou publicar.
