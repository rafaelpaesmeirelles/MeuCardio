# Decisão do responsável: classificação HTTP e tentativas seguras

A instrução explícita original **“Sem novo ci backend”**, registrada anteriormente nesta sessão, permanece vigente para a conclusão do trabalho autorizado de leitura científica e CorVIA Intelligence. A correção focal identificada após o deploy do PR922 não revoga essa instrução. Esta decisão tem escopo independente: não herda nem amplia a autorização registrada no documento do PR922 ou dos PRs anteriores.

O escopo é somente a branch `codex/fix-publication-http-retry-20260910`, originada de `0f341021314669c5fcb8bf81e15ec4f95c7c6934`, o **PR923**, agora selado no manifesto e sua integração exata e confirmada em main. A entrega corrige a classificação de status HTTP em exceções HTTPX e conserva diagnósticos sanitizados e tentativas seguras na biblioteca científica. Não inclui alteração de filas históricas, execução paga, preços, limites, modelos ou guardas de autorização de mudanças clínicas.

O bootstrap com número nulo bloqueia a classificação antes do fallback, sem produzir gate aprovado nem executar suíte. Draft PR também aciona CI; a proteção precede a publicação da branch. Depois de selar o número, a política exige repositório, branch, head SHA atual, ancestralidade da origem e, para main, merge SHA, associação ao PR e igualdade da árvore. Dados ausentes, identidade divergente ou erro de API bloqueiam a classificação; não acionam testes como fallback. Outros PRs ou commits posteriores não herdam a decisão.

Os jobs de backend completo e focal permanecem **skipped**, incluindo etapas de migrations e banco. O artefato informa `backend_ci_executed=false` e `test_certificate=null`, registrando **“backend CI não executado por decisão do responsável”**. Isso não representa aprovação de testes nem reutilização de suíte.

As verificações focais reais serão documentadas em [publication-http-retry-audit-20260910.md](../publication-http-retry-audit-20260910.md). Os contratos existentes de política não serão repetidos opcionalmente apenas para revalidar a mesma estrutura. Corpus, RC2, Visual, frontend e demais gates normais de publicação permanecem obrigatórios.
