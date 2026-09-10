# Decisão do responsável: Meus Favoritos universal

A instrução explícita **“Sem novo ci backend”**, registrada anteriormente nesta sessão, permanece vigente. O pedido posterior ao deploy do PR921 amplia Meus Favoritos para qualquer conteúdo autorizado do site, reunindo os acessos a original, resumo em português e tradução quando aplicáveis. O usuário não revogou nem repetiu a instrução de CI neste pedido. Esta decisão é independente e não reutiliza nem amplia as autorizações dos PRs 918, 919, 920 ou 921.

O escopo é somente a branch `codex/universal-favorites-20260910`, originada de `97270582d93cac6327c9d843395fa704be831373`, o PR independente a selar no manifesto, e sua integração exata e confirmada em main. A entrega preserva a compatibilidade e a privacidade dos favoritos e os controles existentes de acesso e publicação científica. Abrir conteúdo ou favoritar nunca executa IA paga. Esta decisão de CI não concede autorização de publicação científica, processamento massivo ou acesso adicional a conteúdo privado.

O bootstrap com número nulo bloqueia a classificação antes do fallback, sem produzir gate aprovado nem executar suíte. Draft PR também aciona CI; a proteção precede a publicação da branch. Após selar o número, a política exige repositório, branch, head SHA atual, ancestralidade da origem e, para main, merge SHA, associação ao PR e igualdade da árvore. Dados ausentes, identidade divergente ou erro de API bloqueiam a classificação; não acionam testes como fallback. Outros PRs ou commits posteriores não herdam a decisão.

Os jobs de backend completo e focal permanecem **skipped**, incluindo suas etapas de migrations e banco. O artefato informa `backend_ci_executed=false` e `test_certificate=null`, registrando **“backend CI não executado por decisão do responsável”**. Não é certificado de aprovação de testes nem reutilização de suíte.

As verificações locais reais serão registradas em [universal-favorites-audit-20260910.md](../universal-favorites-audit-20260910.md). Corpus, RC2, Visual, build do frontend, cobertura de rotas e gates normais de publicação permanecem exigidos.
