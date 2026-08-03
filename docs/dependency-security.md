# Segurança da cadeia de dependências

## Objetivo

A política separa vulnerabilidades presentes no código implantado de problemas
restritos a ferramentas de desenvolvimento, sem ocultar falhas críticas. Toda
mudança de dependência passa por controles reproduzíveis na CI.

## Controles ativos

### Python

`pip-audit` é instalado apenas no ambiente de desenvolvimento e audita
`backend/requirements.txt`, que corresponde ao conjunto instalado na imagem de
produção. A CI falha diante de vulnerabilidades conhecidas ou falhas de
resolução do grafo.

Comando local:

```bash
cd backend
python -m pip install -r requirements-dev.txt
python -m pip_audit -r requirements.txt --progress-spinner=off --strict
```

### Frontend

O script `npm run audit:security` executa dois relatórios:

1. dependências de produção: bloqueia severidade alta ou crítica;
2. grafo completo: bloqueia severidade crítica, inclusive em tooling.

Não existem exceções de advisory. O lockfile atual permanece obrigatório e a CI
continua instalando com `npm ci`.

### Mudanças em pull requests

`actions/dependency-review-action@v5` reprova novas dependências com
vulnerabilidade alta ou crítica antes do merge.

### Atualizações automáticas

O Dependabot verifica semanalmente:

- GitHub Actions;
- dependências Python em `/backend`;
- dependências npm em `/frontend`.

As atualizações continuam sujeitas a build, testes, auditorias e revisão humana.

### Runtime das GitHub Actions

Os workflows usam majors compatíveis com Node 24:

- `actions/checkout@v6`;
- `actions/setup-python@v6`;
- `actions/setup-node@v6`;
- `actions/dependency-review-action@v5`.

`scripts/check_workflow_actions.py` impede regressão silenciosa para majors
anteriores. O Node usado para compilar o frontend permanece explicitamente na
versão 22; isso é independente do runtime interno Node 24 das Actions.

## Relação com o PR #6

O PR #6 foi criado sobre uma base antiga e misturou o gate npm com atualização
de `react-router-dom` e remoção de ferramenta Capacitor, produzindo uma grande
reescrita do lockfile. Este pacote transporta apenas os controles de segurança
para a stack atual, sem alterar dependências funcionais. O PR #6 deve ser
considerado substituído após esta branch passar integralmente pela CI.

## Resposta a falhas

Uma auditoria reprovada não deve ser contornada com `--force`, exclusão genérica
ou redução da severidade. O procedimento é:

1. identificar pacote, cadeia transitiva e advisory;
2. confirmar se o pacote está no runtime de produção ou apenas no tooling;
3. aplicar a menor atualização compatível;
4. regenerar o lockfile pelo gerenciador oficial;
5. repetir auditoria, testes, build e smoke de release;
6. documentar qualquer risco residual com prazo e responsável.
