# Classificação HTTP e retomada financeira segura — PR923

## Escopo e origem

Base publicada: `0f341021314669c5fcb8bf81e15ec4f95c7c6934` (PR922). A área administrativa de aprovação, os Favoritos e os originais foram publicados e verificados nesse release. Esta correção adicional é restrita à classificação de erros HTTP do processamento científico, ao diagnóstico sanitizado e à retomada comprovadamente segura. Não altera modelos, preços, limites, conteúdo clínico ou a exigência de aprovação individual pelo proprietário.

## Evidência de produção, somente leitura

O radar registrou HTTP 429; a implementação anterior não preserva o código que distinguiria cota do fornecedor de limite temporário. A conta editorial estava desbloqueada e com orçamento disponível. A triagem encontrou dez originais armazenados, sem tradução integral pronta e em `cost_unknown`, além de uma falha de aquisição sem original. O histórico disponível não prova a causa individual desses dez casos nem permite afirmar ausência de cobrança apenas por haver zero tokens registrados.

Esses registros históricos não serão reabertos por esta correção. As checagens pós-deploy do PR922 confirmaram a versão pública, autenticação, migração, proprietário e o código dos dois workers; a saúde limitada do radar foi registrada separadamente do sucesso da publicação.

## Limites da correção

Normalizar o status exposto diretamente por SDKs ou em `HTTPX.response.status_code`. Registrar somente classe da exceção, fase, status e código permitido; sem mensagem livre, URL, corpo, credencial ou texto científico/privado. Uma nova tentativa paga exige prova de rejeição HTTP atual do fornecedor e liquidação exata em zero; custo anterior, reserva pendente ou resultado desconhecido continuam bloqueados. Operações anteriores e etapas já concluídas permanecem preservadas.

## Validação

- Nove testes locais da nova política específica do PR923 passaram em 0,125 s. Cobrem identidade, origem, associação da integração, bootstrap bloqueado e não herança por outros PRs. As suítes anteriores não foram repetidas.
- Onze testes focais da classificação/rejeição passaram em 7,20 s; a revisão independente final foi favorável, sem bloqueios. Evidência detalhada abaixo.
- A instrução original de não executar CI backend permanece vigente e registrada especificamente para PR923. Não há novo certificado de testes backend.
- Corpus, RC2, frontend, visual, inventário e gates normais de publicação permanecem obrigatórios. Não houve chamada paga, teste completo de backend, mudança de fila ou modificação de produção nesta correção.

A confirmação final de commit integrado, gates e produção será registrada no PR depois do fluxo normal de publicação.


## Validação focal da classificação e retentativa

Onze casos focais passaram em 7,20 segundos com `pytest --noconftest -q tests/test_scientific_processing_errors.py`. Banco e transportes são simulados: nenhum acesso ao banco de produção, nenhuma conexão de banco para esses testes, nenhuma requisição de rede e nenhuma chamada paga. AST dos cinco arquivos Python desta correção e `git diff --check` passaram. Uma execução inicial encontrou somente fixture sem DOI; a fixture foi completada antes da rodada final aprovada.

Cobertura: HTTPX 429 com `insufficient_quota`, `rate_limit_exceeded` ou sem código; normalização do status de SDK; descarte de códigos livres contendo dados privados; erros locais 403/409 sem autorização de nova tentativa; preservação de operação desconhecida, custo anterior ou tokens anteriores; erro de aquisição com classe segura e backoff de 24 horas; retomada do trecho atual com chave nova sem perder trechos anteriores.

O diagnóstico persiste somente status HTTP, código de fornecedor em lista explícita, classe de exceção em lista explícita, fase, estado financeiro e horário. Nunca persiste mensagem livre, corpo, URL, credencial ou identificação de paciente. Na biblioteca fica em `progress.last_error`; no radar a classificação segura fica no evento de auditoria da execução. Códigos desconhecidos permanecem nulos, sem inferir que 429 é necessariamente cota financeira.

A nova geração de chave exige conjuntamente uma rejeição HTTPX real do endpoint fixo do fornecedor, status de rejeição admitido pela medição existente e o recibo da operação exata liquidado em zero, sem tokens. Erros locais de orçamento não constituem essa prova. A carteira não é modificada por esta classificação. Falha anterior ao envio continua usando a mesma chave; custos, reservas ou resultados incertos continuam bloqueando repetição automática. A trava consultiva global existente permanece abrangendo seleção, geração, persistência e chamada do trabalhador.

Os dez itens históricos em `cost_unknown` continuam fora da seleção de processamento; não houve reset, reconciliação presumida ou nova tentativa desses itens. Nenhum modelo, preço, limite ou saldo foi alterado. Esta correção melhora o diagnóstico de falhas futuras; não recupera causas históricas que não foram registradas.

## Revisão final

A revisão independente confirmou: erros locais 403/409 não autorizam retry; a prova vem da resposta HTTP real do endpoint fixo e do recibo exato liquidado em zero; valores parciais ou pendentes continuam bloqueados; o lock existente protege seleção, chave, persistência e chamada. Diagnósticos têm listas explícitas de valores permitidos. Não há alteração de modelo, preço, limite ou guardas clínicas. O root revisou o diff funcional e aprovou a integração.
