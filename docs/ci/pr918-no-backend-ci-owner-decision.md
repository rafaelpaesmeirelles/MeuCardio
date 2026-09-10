# PR918 — decisão expressa de não executar novo CI backend

Em 10/09/2026, o responsável determinou: **“Sem novo ci backend”**. Esta instrução substitui a autorização anterior para uma segunda execução focal do backend nesta release.

A política registra `authorized-no-backend-ci` exclusivamente para o PR918 e sua integração exata em `main`. A origem funcional é `266cde7454ec808f37dd4ab0ef6d83415b607c63`, que deve ser ancestral da head do PR. Para integração, também são obrigatórios PR918 mesclado, associação GitHub ao commit, SHA de merge correspondente e árvore idêntica à head. A regra não se transfere a outros PRs ou commits futuros.

Os jobs de backend completo e focal ficam **skipped**. Não executam pytest, migrações, HTTP ou backup em CI. Os unitários da política também não são executados em CI nesse modo; a validação da alteração da política ocorre localmente. O gate registra **“backend CI não executado por decisão do responsável”**. Esse registro não é certificado de sucesso de uma suíte completa ou focal e não reutiliza um certificado de testes.

A evidência anterior permanece com seus resultados reais:

| Execução | Resultado |
| --- | --- |
| Full inicial `34418893616`, job `102689862687`, SHA `eddcb80d3fc99e7c25b330c943637f49691826fa` | Falhou: 84 falhas, 3.038 testes aprovados, 3 ignorados |
| CI `34422978741`, SHA `266cde7454ec808f37dd4ab0ef6d83415b607c63` | Classificação falhou ao baixar o log inicial; motivo HTTP não registrado |
| Jobs backend `102702299040` e focal `102702298687` dessa segunda execução | Ambos skipped; nenhuma segunda suíte backend foi executada |

A consulta de evidência em CI usa somente os metadados do primeiro job e exige seu ID, run, SHA, estado concluído e conclusão `failure` reais. Não baixa novamente logs. Os testes focais locais já concluídos estão documentados nos relatórios versionados abaixo; eles não são apresentados como um CI completo aprovado:

- [Relatório da release](../release-tct-plans-prevalentes-20260910.md)
- [Planos comerciais e carteira de IA](../commercial-plans-ai-wallet-20260909.md)
- [Heart Team e reconciliação delimitada](../heart-team-frontier-and-scoped-reconciliation-20260910.md)
- [Auditoria de configuração da IA](../ai-configuration-audit-20260910.md)
- [Inventário das 84 falhas iniciais](pr918-initial-backend-failures.json)

Os requisitos independentes de Corpus Database, RC2, Visual QA e certificação de publicação/deploy continuam vigentes. Esta decisão não aprova conteúdo científico pendente, altera status editorial ou autoriza a publicação de material em quarentena.
