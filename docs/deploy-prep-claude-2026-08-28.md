# Preparação de deploy — produção Claude — 28/08/2026

> Documento operacional de staging. Esta branch não contém merges de conteúdo do Claude; ela registra a sequência de integração, os gates observados e os bloqueadores que devem ser resolvidos antes do deploy final.

## Base de produção no início da preparação

- `main`: `49fddbc52ce05bfe90aa16f0484c03d8c14047f6`
- Deploy **não executado** nesta preparação.
- Regra de publicação: registros científicos com `review_status != revisado` não devem ser tratados como publicados. Os PRs de aprofundamento podem permanecer `pendente_revisao` durante preparação/revisão, mas precisam de decisão editorial explícita antes de publicação clínica.

## Produção Claude considerada neste pacote

PRs abertos e independentes identificados até esta preparação:

1. #601 — Arritmias ventriculares e morte súbita cardíaca — hub novo geral.
2. #603 — Doença coronariana no idoso.
3. #604 — Valva aórtica bicúspide pediátrica.
4. #606 — Hipotensão ortostática no idoso.
5. #608 — Sopros na infância.
6. #609 — Hipertensão arterial pediátrica.
7. #610 — Dor torácica pediátrica.
8. #611 — Dislipidemias pediátricas.
9. #612 — Arritmias pediátricas.
10. #613 — Avaliação multidimensional cardiogeriátrica.
11. #615 — Cuidados paliativos cardiovasculares.
12. #616 — Cardiopatia congênita na gravidez.
13. #621 — Hipertensão pulmonar na gravidez.
14. #624 — Cardiotoxicidade por BCR-ABL.
15. #625 — Medicamentos cardiovasculares na gestação/lactação.
16. #626 — Plano de parto na cardiopatia materna.

PRs antigos #580/#590/#594/#596/#597/#599 não entram novamente nesta lista porque sua consolidação/correção está sendo tratada pelo release #605; evitar dupla integração.

## Conteúdo ChatGPT/UCO concluído em paralelo

A expansão de Cardiologia Intensiva/UCO foi salva separadamente e não deve ser misturada automaticamente à integração Claude:

- #617 → lote 1
- #620 → lote 2 empilhado
- #622 → lote 3 empilhado
- #623 → lote 4 empilhado
- #627 → lote 5 empilhado (Shock Team, acesso large-bore e marcapasso transvenoso temporário)

## Estado técnico observado dos PRs Claude

### Verdes nos quatro gates principais na última verificação

- #603
- #606
- #608
- #609
- #610
- #611
- #612
- #613
- #616
- #621
- #624
- #625
- #626

Para esses PRs foram observados `CI`, `RC2 Acceptance`, `Corpus inventory` e `Corpus database reconciliation` concluídos com sucesso no respectivo head SHA.

### #615 — corrigido e em revalidação

Revisão clínica dirigida encontrou cinco bloqueadores e foi aplicada por overlay canônico em `doencas/correcoes/pr615-cuidados-paliativos-cardiovasculares.json`:

- ENABLE CHF-PC: remover afirmação de melhora comprovada de qualidade de vida/humor em 16 semanas;
- AINE sistêmico em insuficiência cardíaca: não apresentar como degrau analgésico usual;
- internações recorrentes: usar como gatilho prognóstico/paliativo, não critério isolado de hospice;
- sintomas refratários + internações + inotrópico: não rotular automaticamente trajetória de fim de vida;
- terapias CIED: distinguir consequências fisiológicas sem criar hierarquia ética/legal entre modalidades.

Teste de regressão adicionado: `backend/tests/test_pr615_cuidados_paliativos_correcoes.py`.

Último estado observado após correção:

- Corpus inventory: verde
- Corpus database reconciliation: verde
- RC2 Acceptance: verde
- CI: ainda em execução no momento da documentação

Não integrar #615 até o CI do head corrigido concluir com sucesso.

### #604 — conteúdo/gates de corpus verdes; branch precisa atualização

Estado observado:

- CI: verde
- Corpus inventory: verde
- Corpus database reconciliation: verde
- RC2 antigo: falhou antes de subir o backend por `502 Bad Gateway` do Docker Hub ao resolver `python:3.12-slim`.
- PR atualmente `mergeable: false` contra a `main` atual, por drift/conflito de branch.

A falha RC2 observada não foi uma asserção clínica ou de conteúdo. O job falho foi reexecutado nesta preparação para confirmação, mas o PR ainda precisa ser atualizado/rebaseado para a `main` vigente antes de integração.

### #601 — PR legado anterior ao baseline dinâmico

Os gates antigos falharam porque o workflow de inventário daquela época exigia exatamente `9496` itens. O PR elevou corretamente o corpus a `9497`, e a asserção antiga `assert total_items == 9496` derrubou o gate. A política atual trata o número certificado como baseline mínimo, não como teto.

Além disso, #601 modifica o manifesto monolítico `doencas/metadados.json`; para integração atual, preferir portar o hub novo para `doencas/fragmentos/*.json`, evitando colisão com os numerosos aprofundamentos concorrentes.

Não fazer merge direto do #601 legado sem portar/atualizar e rerodar os gates atuais.

## Colisão estrutural conhecida

Os aprofundamentos Claude foram produzidos em branches paralelas e vários editam simultaneamente:

- `doencas/metadados.json`
- `backend/tests/test_canonical_content_review_status.py`
- `backend/tests/test_disease_fragments_canonical.py`

Nunca resolver conflito desses arquivos com `ours/theirs` em bloco.

A arquitetura canônica atual permite:

- **hub novo** → `doencas/fragmentos/*.json`;
- **alteração pequena/auditável de slug já existente** → `doencas/correcoes/*.json`.

Essa estratégia deve ser preferida ao crescer o pacote integrado.

## Ordem recomendada de integração

Integrar um PR por vez, atualizar o próximo contra o novo `main` e rerodar seus gates. Ordem operacional sugerida:

1. #601 somente após port para fragmento canônico;
2. #603;
3. #604 após atualização/rebase e novo RC2;
4. #606;
5. #608;
6. #609;
7. #610;
8. #611;
9. #612;
10. #613;
11. #615 após CI verde no head corrigido;
12. #616;
13. #621;
14. #624;
15. #625;
16. #626.

A ordem é deliberadamente conservadora para reduzir conflito de branches antigas e preservar a cronologia da produção. Se um PR for portado para fragmento/correção canônica independente, ele pode ser integrado com menos dependência de ordem, mas o SHA final continua exigindo certificação conjunta.

## Decisão editorial antes de publicar

Os PRs de aprofundamento usam `review_status: pendente_revisao` durante revisão. Antes do deploy que pretenda efetivamente publicar esses verbetes:

1. revisar/aprovar nominalmente os registros escolhidos;
2. alterar apenas esses registros para `review_status: revisado` com `review_note` auditável;
3. remover allowlists temporárias que não forem mais necessárias;
4. confirmar que nenhum `pendente_revisao` está marcado `published: true`;
5. executar a reconciliação real e conferir o conjunto que será publicado/despublicado.

Não converter em massa `pendente_revisao` para `revisado` apenas para fazer o CI passar.

## Certificação obrigatória do SHA final

Depois de toda integração e antes do deploy, no **mesmo SHA final que será publicado**, exigir:

- CI completo;
- RC2 Acceptance — Canonical CorVIA;
- Corpus inventory;
- Corpus database reconciliation;
- Visual QA quando o SHA também contiver alterações de frontend/UI;
- build de frontend quando aplicável;
- verificação de referências Tudo com Tudo sem links quebrados;
- testes semânticos específicos adicionados pelos lotes clínicos sensíveis.

Não reutilizar green check de um head antigo para certificar um `main` diferente.

## Deploy

Somente depois dos gates acima no SHA exato de `main`:

1. registrar SHA final;
2. executar o workflow/rotina de deploy de produção;
3. confirmar `/api/version` = SHA esperado;
4. confirmar `/api/health` e `/api/ready`;
5. validar autenticação e uma amostra dos verbetes publicados;
6. conferir que itens `pendente_revisao` não foram expostos como revisados/publicados.

## Estado desta preparação

- Produção Claude identificada e inventariada.
- Lote UCO atual concluído e salvo em #627.
- #615 corrigido cientificamente e protegido por teste de regressão; revalidação em andamento.
- #604 identificado como problema de branch + falha RC2 externa histórica, não falha clínica; rerun solicitado.
- #601 identificado como PR legado com baseline congelado e candidato a port para fragmento.
- Nenhum merge para `main` e nenhum deploy foram feitos por esta preparação.
