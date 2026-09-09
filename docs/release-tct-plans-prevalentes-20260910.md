# Release integrada CorVIA — Tudo com Tudo, planos e PR #915

Candidato consolidado em `codex/release-tct-plans-prevalentes-20260910`, baseado em `1c8454d132bfc6ecedec802c731dbb26b4d1e6da`. Preparado por solicitação do proprietário para concluir o trabalho de Tudo com Tudo e IA, acrescentar o PR #915 e aplicar sua segunda rodada antes de publicar.

## Inclusões verificadas

- PR #916: correções de precisão/cobertura da busca, conexões úteis, Holter com vetor nulo, medicamentos, grafo e jornadas de busca. Inclui os relatórios anteriores da avaliação de contribuição/custos da IA e a correção da sentinela (`43a2d858`).
- PR #917: quatro planos mensais (99,90; 119,90; 149,90; 169,90), Mail opcional, carteira financeira, franquia proporcional, reserva e medição das jornadas pagas, recargas e webhooks. Complemento `bbe404fc` conclui orçamento de documentos e contratos de validação.
- PR #915: primeira rodada e handoff `d7f51132d0c1e343e75ff0e85c69211adbf2daa3`, mais patch da segunda rodada efetivamente aplicado em `c1eafa1e674b11ab9946e87a70f098a921e425ce`. Os 43 blobs finais conferem exatamente com o patch. Não houve novo lote científico nem marcação de publicação.

As integrações Git preservaram a main e não apresentaram conflitos. As correções e documentos de cada frente acompanham este candidato; não dependem de reaplicar manualmente o patch #915 depois do merge.

## Verificação consolidada

O inventário canônico final contém **12.210 registros**, sem itens inválidos, arquivos faltantes ou chaves duplicadas. A segunda rodada preserva os catálogos anteriores e valida 24 recursos recíprocos, 14 documentos e oito trilhas com 67 etapas. Quatro sentinelas de busca passaram no candidato integrado.

A migration final foi aplicada por `python -m app.commands.migrate` em PostgreSQL isolado. As cinco tabelas financeiras e as três colunas contratuais correspondem exatamente aos modelos, e as novas rotas foram registradas pela aplicação. Os testes financeiros, de provedores, de Heart Team, de documentos e de interface estão documentados nas entregas; incluem webhook assinado real com transporte simulado, concorrência/reserva, proporcionalidade e teto persistido durante threadpool. TypeScript e contratos de contraste/rotas passaram. Nenhum teste usou banco de produção ou cobrança real.

## Configuração antes do lançamento

`subscriptions_enabled=false` e `ai_credit_topups_enabled=false` continuam como configuração de pré-lançamento. Os preços e a franquia piloto são configuráveis; antes da abertura serão conferidos custos por função/modelo, taxas, câmbio e Mail/WhatsApp. O Tudo com Tudo permanece parte de todos os planos; processamento institucional não consome créditos individuais.

## Bloqueio da publicação

O manifesto integral existente autoriza **11.581 registros**, enquanto este candidato contém **12.210**. O problema não é somente atualizar uma contagem: existem pendências e duplicatas com exclusão expressa de republicação. O relatório `commercial-release-scientific-blockers-20260909.md` documenta o snapshot anterior ao #915: 547 fontes com cobertura exata, 54 fora do inventário incremental e nove pendentes, com sobreposição explicitada.

O handoff #915 exige autorização correspondente ao snapshot final e proíbe fabricar aprovação retroativa de todo o corpus. O publicador incremental existente é vinculado a outro pacote; a pipeline normal continua exigindo gates integrais. Não foram alterados esses gates, manifestos ou estados editoriais para obter aprovação artificial.

**Estado: implementação integrada; produção ainda não atualizada.** Merge/deploy, promoção editorial do #915, reconciliação do grafo/índice em produção e verificação autenticada pós-publicação dependem da liberação correta da release. A avaliação real do provedor semântico permanece limitada pelo `credit_balance_exhausted` já registrado; testes simulados não comprovam a qualidade do provedor em produção.
