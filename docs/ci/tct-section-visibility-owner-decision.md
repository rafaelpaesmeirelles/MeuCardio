# Decisão do responsável: correção das seções do Tudo com Tudo

A instrução explícita **“Sem novo ci backend”**, mantida pelo responsável ao solicitar a correção geral das pesquisas, aplica-se a esta entrega. A decisão é própria desta correção; a dispensa do PR918 não é reutilizada como autorização.

O escopo é a branch `codex/fix-tct-section-visibility-20260910`, originada de `02ad2d6a38301667a82eb60444b531d1e1fcd4e1`, o número de PR posteriormente selado no manifesto e sua integração exata e confirmada em main. O manifesto em bootstrap, com número nulo, bloqueia a classificação antes do fallback e não produz um gate aprovado. Abrir draft PR não suprime CI automaticamente.

Após selar o número, são verificados repositório, branch, head SHA atual, ancestralidade da origem e, no push em main, merge SHA, associação ao PR e igualdade da árvore. Dados ausentes, erros de API ou identidade divergente bloqueiam a classificação; não autorizam uma execução de backend como fallback. Outros PRs e commits posteriores não herdam a decisão.

Os jobs de testes completos e focais permanecem **skipped**, incluindo suas etapas de migrations e preparação do banco. O artefato informa `backend_ci_executed=false` e `test_certificate=null`, com o registro **“backend CI não executado por decisão do responsável”**. Não é certificado de testes aprovados nem reutilização de suíte.

As verificações locais efetivamente concluídas serão documentadas em [tct-section-visibility-20260910.md](../tct-section-visibility-20260910.md). Esta decisão não afirma que uma nova suíte de backend passou. Os gates independentes Corpus, RC2, Visual e de publicação permanecem exigidos e conservam suas próprias verificações.
