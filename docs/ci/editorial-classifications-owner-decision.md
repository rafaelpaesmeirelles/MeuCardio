# Decisão do responsável: classificações editoriais e regressões mobile

A instrução explícita **“Sem novo ci backend”**, registrada anteriormente nesta sessão e não revogada pelos pedidos de revisão editorial após o deploy do PR919 e de correção das regressões mobile Home/choice nos temas claro e escuro, continua aplicável. O usuário não repetiu a instrução de não executar backend CI nesses pedidos. Esta decisão tem escopo próprio e não herda a autorização dos PRs 918 ou 919.

O escopo é a branch `codex/fix-editorial-classifications-20260910`, originada de `4c58de6fb7cd64bd8767f062d9ef0ee814870cda`, o **PR920**, agora selado no manifesto, e sua integração exata e confirmada em main. Esta entrega abrange a revisão das classificações editoriais e as correções de visibilidade do wordmark da Home e de overflow da tela choice no mobile, nos temas claro e escuro. O bootstrap com número nulo bloqueia a classificação antes do fallback, sem produzir um gate aprovado. Draft PR também aciona CI; por isso a proteção precede a publicação da branch.

Após selar o número, a política exige repositório, branch, head SHA atual, ancestralidade da origem e, para main, merge SHA, associação ao PR e igualdade da árvore. Identidade divergente, dados ausentes ou erro de API bloqueiam a classificação; não acionam uma suíte como fallback. Outros PRs e commits posteriores não herdam a decisão.

Os jobs de backend completo e focal permanecem **skipped**, incluindo suas etapas de migrations e banco. O artefato informa `backend_ci_executed=false` e `test_certificate=null`, registrando **“backend CI não executado por decisão do responsável”**. Não é certificado de aprovação de testes nem reutilização de suíte.

As verificações locais reais serão registradas em [editorial-classification-audit-20260910.md](../editorial-classification-audit-20260910.md). A política de CI não modifica conteúdo, classificação editorial, autorização de publicação ou critérios científicos. Corpus, RC2, Visual e gates normais de publicação permanecem exigidos.
