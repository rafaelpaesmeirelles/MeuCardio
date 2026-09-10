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

## Autorização do snapshot e quarentena

O manifesto integral anterior permanece intacto: sua autorização de 11.581 registros não é reaproveitada para aprovar conteúdo diferente. O novo manifesto de escopo exato `editorial-approvals/scoped-corpus-release-20260910.json` e suas evidências vinculam **12.154 registros autorizados** e **56 em quarentena** ao inventário final de 12.210.

A proveniência verificada corresponde a 11.230 identidades imutáveis da baseline autorizada, 545 do pacote de 09/09, 75 das duas rodadas do PR #915 e 304 fichas cuja única alteração é a normalização técnica de `theme` do Tudo com Tudo no commit `800a159e09c87176c9c5bc0f53978495dd5a8de9`. Essa normalização foi expressamente incluída na autorização técnica da sessão; não representa nova revisão clínica. Nenhum campo clínico foi ignorado na comparação.

A quarentena reúne 47 fontes sem cobertura exata de autorização, sete pendentes de revisão e duas duplicatas expressamente excluídas que ainda possuem arquivos canônicos. Os estados editoriais dos arquivos e as exclusões anteriores foram preservados. Sidecars, mídias e relações explícitas também possuem prova de origem e hashes. Das 3.159 relações explícitas, 3.054 foram preservadas e 105 correspondem exatamente às adições do #915. O relatório `scoped-corpus-release-provenance-20260910.md` descreve a reconstrução reproduzível.

A validação de schema 2 exige partição exata, hashes por identidade e evidências acessíveis, e compara os slugs efetivamente publicados no banco. O reconciliador importa uma cópia validada das fontes e relações, com publicação canônica congelada durante a carga; apenas o conjunto autorizado pode ser promovido ao final. Referências necessárias ao validador são montadas somente leitura no backend. Detalhes e hidratação RAG não podem expor fontes despublicadas.

## Verificação e operação da release

A validação local do frontend passou nas 17 etapas do CI. O precache final contém 146 arquivos e 3.122.244 bytes, abaixo do teto de 3.135.488. Quatro páginas que dependem de conexão foram retiradas somente do precache; a política de cache das APIs foi preservada. O contrato de login acompanha o componente `LoginGalaxy`, sem alteração do layout aprovado.

O `deploy.sh` volta ao fluxo normal certificado, preservando o caminho específico de recuperação RDC: build antes da indisponibilidade, trava de concorrência, checkout imutável, parada dos escritores, backup consistente, rollback armado antes das migrations, reconciliação do corpus, workers da mesma versão e readiness antes de abrir o proxy. Foi removida a chamada genérica de republicação após o reconciliador, pois ela poderia contrariar a quarentena. A verificação do deploy não faz chamada paga ao fornecedor. Na validação focal operacional, 30 testes passaram inicialmente; a única expectativa obsoleta de canário pago foi corrigida e os dois contratos afetados passaram. A verificação adicional dos mounts confirmou que todas as evidências transitivas estão disponíveis somente leitura.

O primeiro CI completo do backend do candidato `eddcb80d` terminou com **3.038 aprovados, 84 falhas e três ignorados**, em 1.821,92 segundos. Esse resultado não constitui aprovação integral. Conforme instrução explícita do proprietário para não repetir a suíte completa, o acompanhamento executa os módulos que falharam, os impactados pelas mudanças e regressões financeiras obrigatórias; caminhos sem mapeamento bloqueiam. O certificado de acompanhamento é distinto e restrito ao PR #918 e à sua integração exata na main. Migrations, idempotência, HTTP, backup e os demais gates operacionais permanecem exigidos.

O assistente pessoal com OpenAI agora dispõe de transporte de ferramentas em resposta normal e streaming: preserva o executor autenticado, reserva até seis rodadas, limita uma chamada de ferramenta por rodada e impede nova ação na rodada final. Doze testes com transporte e carteira simulados passaram, incluindo contagem de todas as etapas, cancelamento, argumentos fragmentados, falta de saldo e repetição de identificador. Nenhuma mensagem real foi enviada.

A reconciliação do corpus real passou em banco isolado (nove testes, 352,45 segundos), além de 12 testes focais de autorização/carga e um teste de mídia. As falhas do primeiro CI foram tratadas e revalidadas nos módulos correspondentes; os registros detalhados acompanham `docs/ci/pr918-initial-backend-failures.json`. A auditoria adicional de configuração OpenAI/Anthropic está em `ai-configuration-audit-20260910.md`; a medição de cache/transcrição passou em 45 testes.

Por solicitação expressa do proprietário, o Heart Team passará a usar GPT-5.6 Sol dedicado em suas análises e síntese, com raciocínio `medium`, orçamento antes da execução e configuração separada do chat geral. A validação da configuração dedicada passou em 94 testes e revisão independente. O limite da extração visual foi alinhado à saída de 8.192 tokens e passou em uma conferência focal separada. O contrato final está em `heart-team-frontier-and-scoped-reconciliation-20260910.md`. As quatro variáveis dedicadas não possuem override no `.env` de produção; o novo código fornecerá os defaults aprovados sem alteração de credenciais. **Produção ainda não atualizada; commit final, CI do acompanhamento e deploy pendentes.** A avaliação real do provedor semântico permanece limitada pelo `credit_balance_exhausted` já registrado; testes simulados não comprovam qualidade de respostas em produção.
