# Expansão científica 20k — Claude Code

Branch: `claude/science-scale-20k-20260904`
PR (draft, não mesclar): https://github.com/rafaelpaesmeirelles/MeuCardio/pull/778
SHA base: `754673cc6dc7844eb3e46380e0c5f784dbd4d7ac` (origin/main, 30/08/2026)
Diretiva: meta conjunta de 20.000 itens canônicos até 04/09/2026.
Responsabilidade líquida do Claude: **4.900 itens novos**, sem duplicações:
- 2.400 documentos clínicos originais (content/)
- 900 casos clínicos (casos-clinicos/)
- 600 checklists (checklists/)
- 500 materiais para pacientes (material-paciente/)
- 300 trilhas (trilhas/)
- 200 doenças especializadas (doencas/)

**Fora do escopo do Claude**: `estudos/metadados.json` e `evidencias/metadados.json` pertencem à produção do Grok — nunca tocar.

**Regime de revisão (novo, 30/08/2026)**: dois estágios — um agente produz,
outro agente com contexto independente revisa fontes, números, segurança
clínica e metadados. Só após a segunda revisão confirmada o item recebe
`review_status: revisado`. Sem essa confirmação, permanece
`pendente_revisao` com o motivo listado.

---

## Lote 1 — concluído (commit `24f2a878`, 30/08/2026)

8 checklists hemato-oncológicos com acometimento cardiovascular, cota
"checklists" (427 → 435). Todos `review_status: pendente_revisao` —
ainda **não passaram pelo segundo estágio de revisão independente**
exigido pela nova diretiva (foram produzidos antes dela, na branch
anterior `claude/science-continuous-prevalence-gaps-20260829`, e
migrados para cá como primeira entrega).

| Slug | PMIDs-chave | Origem_secao/tema |
|---|---|---|
| acometimento-cardiovascular-purpura-trombocitopenica-trombotica | 25403270, 28576877, 30625070 | Troponina preditora, mecanismo microangiopático, HERCULES |
| acometimento-cardiaco-sindrome-antifosfolipide-catastrofica | 12892393, 15708888, 38552300 | Critérios Taormina, registro CAPS 2024, MINOCA |
| doenca-arterial-coronariana-hemofilia-manejo-cardiovascular | 23710576, 32744769, 38379212 | DAPT vs. risco hemorrágico, WFH 3ª ed. |
| sindrome-de-hiperviscosidade-acometimento-cardiovascular | 14631546, 37099030, 34550244 | Isquemia baixo fluxo, amiloidose AL |
| hipertensao-pulmonar-neoplasias-mieloproliferativas-mielofibrose | 36017548, 37311222, 38061384 | HP grupo 5 vs. HPTEC, TCTH |
| risco-cardiovascular-trombotico-policitemia-vera | 23216616, 14711910, 18250227 | CYTO-PV, ECLAP, Budd-Chiari |
| risco-cardiovascular-trombotico-trombocitemia-essencial | 23033268, 28205126, 16000354 | IPSET-thrombosis, PT1 |
| doenca-de-von-willebrand-sindrome-de-heyde-cirurgia-cardiaca | — | DVW tipo 2A adquirida/EAo/cirurgia |

**Manifesto**: arquivo alterado `checklists/metadados.json` (única
alteração). PMIDs/DOIs únicos citados: ~90 (ver source_refs de cada
item). Slugs ignorados por duplicação: 0. Erros/avisos: 1 corrigido
(PMID 11921022 ausente de source_refs no item de mielofibrose, adicionado
antes da integração).

**Gates**: `audit_tudo_com_tudo.py` → `broken_references: []`;
`content_inventory.py --strict` → exit 0, 10.197 registros totais, 0
`duplicate_keys`, 0 `invalid`, 0 `missing`.

**Total canônico projetado após Lote 1**: 10.197 (10.189 revisado + 8
pendente_revisao desta branch).

## Lote 2 (em andamento)

Varredura sistemática de lacunas reais (não suposição): dispatch de
agente de inventário para cruzar `doencas/metadados.json` por
`prevalence_rank`/`area` contra cobertura em `content/`,
`casos-clinicos/`, `material-paciente/`, `trilhas/` — vários temas
"prevalentes" testados manualmente (ICFEmr, AHRE, hipertensão
resistente, protocolo 0h/1h, ferro IV em IC, miocardite pós-vacinal)
já estão cobertos em profundidade, confirmando que o corpus está denso;
lacunas reais exigem varredura estruturada, não suposição por tema.

## Lote 2 — concluído (commit `feb3c63c`, 30/08/2026)

7 itens novos: 3 casos clínicos, 2 materiais-paciente, 2 documentos.
Ver mensagem de commit para lista completa e PMIDs-chave.

**Achado crítico de processo**: 3 itens de `doenças especializadas`
planejados (choque-cardiogênico, dislipidemia, cardiomiopatia-chagásica-
crônica) foram descartados após verificação mais profunda — colidiam
com `doencas/fragmentos/*.json` (overlay de composição que o inventário
inicial de lacunas não havia verificado, só `doencas/metadados.json`).
`choque-cardiogenico` e `dislipidemia` são colisão exata de slug com
fragments já "completo"; `cardiomiopatia-chagasica-cronica` é duplicata
semântica de `cardiomiopatia-chagasica` já existente. **Regra adicionada
para todos os lotes futuros de doenças**: checar `doencas/metadados.json`
+ `doencas/fragmentos/` + `doencas/correcoes/` antes de produzir, e o
equivalente para `material-paciente/correcoes/` (verificado limpo neste
lote). `casos-clinicos/`, `checklists/`, `trilhas/` e `content/` não têm
overlay — checagem contra o `metadados.json`/arquivos `.md` é suficiente.

**Gates**: `audit_tudo_com_tudo.py` → `broken_references: []`;
`content_inventory.py --strict` → exit 0, 10.204 registros totais.

**Total canônico projetado após Lote 2**: 10.204 (10.189 revisado +
15 pendente_revisao desta branch: 8 do Lote 1 + 7 do Lote 2).

## Lote 3 (planejado)

Cota de "doenças especializadas" (200 pedidos, 103 existentes) precisa
de nova varredura que já cruze `fragmentos/`+`correcoes/` desde o início
para não repetir o retrabalho deste lote. Candidatos a reverificar com
o método correto: síndrome aórtica aguda, DAP/claudicação intermitente,
crise hipertensiva (separada da urgência), tako-tsubo, apneia do sono
e coração, obesidade e risco cardiovascular, tabagismo e DCV.

## Lote 3 — concluído (commit `1dd7e359`, 30/08/2026)

2 itens: 1 caso clínico (intolerância a estatina/reexposição, com
efeito nocebo documentado em StatinWISE PMID 33627334 e SAMSON PMID
33196154), 1 material-paciente (hiponatremia na IC). Gates limpos,
10.206 registros totais.

## Achado crítico de CI: gate `test_canonical_content_review_status.py`

O job "Backend tests" do PR #778 falhou (não é bug de conteúdo/código):
`backend/tests/test_canonical_content_review_status.py` garante que
**nenhum item `pendente_revisao` entre em manifesto canônico ou
documento markdown sem uma decisão editorial explícita** registrada em
`editorial-approvals/*.json`. Como todo o conteúdo desta branch é
propositalmente `pendente_revisao` (regime de dois estágios da diretiva
de 30/08), esse teste específico vai continuar vermelho até que o
segundo estágio de revisão aconteça e marque os itens como `revisado`,
ou até que alguém com autoridade editorial (não eu) crie o arquivo de
aprovação explícita.

**Não vou criar esse arquivo de aprovação** — seria efetivamente uma
autoaprovação do meu próprio conteúdo, o que a regra permanente desta
produção proíbe (Claude/Grok geram, ChatGPT revisa e publica).
Reportado como comentário no PR #778 para transparência.

Meus dois gates obrigatórios (`audit_tudo_com_tudo.py`,
`content_inventory.py --strict`) continuam sendo o critério de qualidade
que rodo e reporto a cada lote — esses seguem limpos em todos os lotes
até aqui.

**Total canônico projetado após Lote 3**: 10.206 (10.189 revisado + 17
pendente_revisao desta branch: 8 do Lote 1 + 7 do Lote 2 + 2 do Lote 3).

## Lote 4 — concluído (commit `eda08a49`, 30/08/2026)

3 itens em interseções hemato-cardiológicas (PTT, CAPS, policitemia
vera) — pivô deliberado após confirmar que temas cardiovasculares
"óbvios" já estão quase todos cobertos; esta área teve 0 colisões nas
checagens. Gates limpos, 10.209 registros totais.

**Total canônico projetado após Lote 4**: 10.209 (10.189 revisado + 20
pendente_revisao nesta branch: 8+7+2+3).

## Status consolidado até aqui (4 lotes)

| Tipo | Cota Claude | Entregues (pendente_revisao) | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 2 | 2.398 |
| Casos clínicos | 900 | 5 | 895 |
| Checklists | 600 | 8 | 592 |
| Materiais-paciente | 500 | 4 | 496 |
| Trilhas | 300 | 0 | 300 |
| Doenças especializadas | 200 | 0 (3 descartados por colisão) | 200 |
| **Total** | **4.900** | **19** | **4.881** |

Ritmo real observado: ~2-3 itens por rodada de agentes paralelos
(8-10min cada agente com pesquisa PubMed completa), limitado por
verificação anticolisão cada vez mais difícil (corpus muito denso) e
pelo tempo de pesquisa/verificação por item, não pelo paralelismo em
si. Reportando ritmo real a cada lote em vez de prometer a cota cheia.

## Lote 5 — concluído (commit `94048d49`, 30/08/2026)

2 itens (hemofilia+SCA/stent, trombocitemia essencial). Gates limpos,
10.211 registros totais.

**Total canônico projetado após Lote 5**: 10.211 (10.189 revisado + 22
pendente_revisao nesta branch).

## Lote 6 — concluído (commit ver git log, 30/08/2026)

2 itens (cardiomiopatia acromegálica, Cushing e coração). Gates
limpos, 10.213 registros totais.

**Total canônico projetado após Lote 6**: 10.213 (10.189 revisado + 24
pendente_revisao nesta branch: 8 checklists + 5 casos + 6 material-
paciente + 2 documentos + 3 casos adicionais... ver commits para
contagem exata por tipo).

## Lote 7 — concluído (commit `ecd10b6e`, 30/08/2026)

3 itens (FMF/pericardite, hiperparatireoidismo, cardiomiopatia por
deficiência de carnitina). Gates limpos, 10.216 registros totais.

**Total canônico projetado após Lote 7**: 10.216 (10.189 revisado + 27
pendente_revisao nesta branch).

## Lote 8 — concluído (commit `9d17e656`, 30/08/2026)

3 itens (crise adrenal, miocardite DRESS, FTAAD). Gates limpos, 10.219
registros totais.

**Total canônico projetado após Lote 8**: 10.219 (10.189 revisado + 30
pendente_revisao nesta branch).

## Lote 9 — concluído (commit ver git log, 30/08/2026)

3 itens (GPA, policondrite recidivante, EGPA). Gates limpos, 10.222
registros totais.

**Total canônico projetado após Lote 9**: 10.222 (10.189 revisado + 33
pendente_revisao nesta branch).

## Lote 10 — concluído (commit ver git log, 30/08/2026)

2 itens (PRKAG2, Naxos/Carvajal). Gates limpos, 10.224 registros
totais.

**Total canônico projetado após Lote 10**: 10.224 (10.189 revisado +
35 pendente_revisao nesta branch).

## Status consolidado após 10 lotes

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 4 | 2.396 |
| Casos clínicos | 900 | 14 | 886 |
| Checklists | 600 | 8 | 592 |
| Materiais-paciente | 500 | 9 | 491 |
| Trilhas | 300 | 0 | 300 |
| Doenças especializadas | 200 | 0 (3 descartados por colisão) | 200 |
| **Total** | **4.900** | **35** | **4.865** |

## Lote 11 — concluído (commit `63c51051`, 30/08/2026)

2 itens (esclerose sistêmica, trilha básica de FA — primeira trilha
desta expansão). Gates limpos, 10.226 registros totais.

**Total canônico projetado após Lote 11**: 10.226 (10.189 revisado +
37 pendente_revisao nesta branch).

## Lote 12 — concluído (commit ver git log, 30/08/2026)

2 itens (sarcoidose cardíaca/CDI, amiloidose AL/hipotensão). Gates
limpos, 10.228 registros totais.

**Total canônico projetado após Lote 12**: 10.228 (10.189 revisado +
39 pendente_revisao nesta branch).

## Lote 13 — concluído (commit ver git log, 30/08/2026)

2 itens (síndrome de Timothy, Jervell-Lange-Nielsen). Gates limpos,
10.230 registros totais.

**Total canônico projetado após Lote 13**: 10.230 (10.189 revisado +
41 pendente_revisao nesta branch).

## Lote 14 — concluído (commit ver git log, 30/08/2026)

3 itens (distrofia miotônica tipo 1, síndrome de Alström, Emery-
Dreifuss). Gates limpos, 10.233 registros totais.

**Total canônico projetado após Lote 14**: 10.233 (10.189 revisado +
44 pendente_revisao nesta branch).

## Lote 15 — concluído (commit ver git log, 30/08/2026)

2 itens (NF1 vasculopatia/HAS, progeria). Gates limpos, 10.235
registros totais.

**Total canônico projetado após Lote 15**: 10.235 (10.189 revisado +
46 pendente_revisao nesta branch).

## Status consolidado após 15 lotes

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 4 | 2.396 |
| Casos clínicos | 900 | 20 | 880 |
| Checklists | 600 | 8 | 592 |
| Materiais-paciente | 500 | 13 | 487 |
| Trilhas | 300 | 1 | 299 |
| Doenças especializadas | 200 | 0 (3 descartados por colisão) | 200 |
| **Total** | **4.900** | **46** | **4.854** |

## Lote 16 — concluído (commit ver git log, 30/08/2026)

2 itens (ataxia de Friedreich, Duchenne). Gates limpos, 10.237
registros totais.

**Total canônico projetado após Lote 16**: 10.237 (10.189 revisado +
48 pendente_revisao nesta branch).

## Lote 17 — concluído (commit ver git log, 30/08/2026)

2 itens (ataxia-telangiectasia, síndrome de Wolfram). Gates limpos,
10.239 registros totais.

**Total canônico projetado após Lote 17**: 10.239 (10.189 revisado +
50 pendente_revisao nesta branch).

## Lote 18 — concluído (commit ver git log, 30/08/2026)

2 itens (Löffler/hipereosinofílica, hemocromatose). Gates limpos,
10.241 registros totais.

**Total canônico projetado após Lote 18**: 10.241 (10.189 revisado +
52 pendente_revisao nesta branch).

## Lote 19 — concluído (commit ver git log, 30/08/2026)

2 itens (SCA por cocaína, cardiomiopatia arritmogênica). Gates
limpos, 10.243 registros totais.

**Total canônico projetado após Lote 19**: 10.243 (10.189 revisado +
54 pendente_revisao nesta branch).

## Status consolidado após 19 lotes

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 4 | 2.396 |
| Casos clínicos | 900 | 24 | 876 |
| Checklists | 600 | 8 | 592 |
| Materiais-paciente | 500 | 17 | 483 |
| Trilhas | 300 | 1 | 299 |
| Doenças especializadas | 200 | 0 (3 descartados por colisão) | 200 |
| **Total** | **4.900** | **54** | **4.846** |

## Lote 20 — concluído (commit c5d649af)

- **casos-clinicos**: +1 — `erdheim-chester-aorta-em-bainha-braf` (histiocitose não-Langerhans, "aorta em bainha", BRAF V600E, tema Populações especiais).
- **content/**: +1 — `doenca-relacionada-a-igg4-e-a-aorta-periaortite-e-aneurisma-inflamatorio` (Aorta e doença arterial periférica) — periaortite/aneurisma inflamatório por IgG4-RD, diferencial direto com o caso do Erdheim-Chester deste mesmo lote.
- **Correção de dívida "Tudo com Tudo"**: 4 documentos de lotes anteriores (17–19 e um mais antigo) estavam sem a seção `## Tudo com Tudo` — achado ao validar manualmente os 7 links que o agente do documento de IgG4 havia proposto (todos fabricados, nenhum slug existia no corpus). Refeitos com links reais, cada slug conferido individualmente contra o corpus antes do commit:
  - `complicacoes-vasculares-acesso-cateterismo-hematoma-pseudoaneurisma-fistula-av.md`
  - `hipotireoidismo-sistema-cardiovascular-bradicardia-dislipidemia.md`
  - `cardiomiopatia-deficiencia-primaria-carnitina.md`
  - `aneurisma-aortico-toracico-familiar-nao-sindromico-documento.md`
  - `doenca-relacionada-a-igg4-e-a-aorta-periaortite-e-aneurisma-inflamatorio.md` (novo, com 5 links)

  **Lição registrada**: `audit_tudo_com_tudo.py` só valida referências estruturadas (`documento_slug`, `related_document_slugs`, etc.) — **não** valida os links markdown dentro da seção `## Tudo com Tudo` de `content/*.md`. Um subagente pode alucinar slugs plausíveis nessa seção sem que o gate `--strict` detecte. **Regra nova**: todo slug citado em `## Tudo com Tudo` de um documento novo precisa ser conferido manualmente (grep pelo `slug:` exato no front-matter) antes do commit — não confiar apenas nos gates automatizados para essa seção.

- **PMIDs novos**: 4 (Erdheim-Chester: PMID 15525849, 15505288, 22879539, 23258922) + 28 do documento de IgG4 (ver front-matter) — nenhum PMID duplicado dentro do corpus verificado nesta rodada.
- **Slugs pulados por duplicação**: nenhum.
- **Gates**: `audit_tudo_com_tudo.py` → `broken_references: []`; `content_inventory.py --strict` → exit 0, `invalid: []`, `missing: []`.
- **Total canônico projetado**: 10.245 (10.189 revisado + 56 pendente_revisao desta frente).
- **PR #709** (correção de anomalias de tema): OPEN, mergeable, checks 100% verdes (Backend tests, Frontend build) — aguardando decisão de merge do Rafael, não mexido.
- **PR #778** (frente principal desta expansão): permanece com "Backend tests" vermelho por desenho (gate de aprovação editorial, sem segunda revisão independente ainda realizada em nenhum item) — sem mudança de status.

### Status consolidado (após Lote 20)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 5 | 2.395 |
| Casos clínicos | 900 | 25 | 875 |
| Checklists | 600 | 8 | 592 |
| Materiais-paciente | 500 | 17 | 483 |
| Trilhas | 300 | 1 | 299 |
| Doenças especializadas | 200 | 0 (3 descartados por colisão) | 200 |
| **Total** | **4.900** | **56** | **4.844** |

## Lote 21 — concluído (commit 8b98cf19)

- **doencas**: +1 — `erdheim-chester-disease-acometimento-cardiovascular` — primeiro item entregue na frente "doenças especializadas" (0/200 até este lote). Cuidado extra no schema desta vez: `related_document_slugs` e `patient_material_slug` só preenchidos quando confirmados, evitando repetir a colisão de fragmento de lotes anteriores.
- **checklists**: +1 — `indicacao-e-preparo-para-biopsia-endomiocardica-na-suspeita-de-miocardite-de-celulas-gigantes-ou-sarcoidose-cardiaca` — pareado com o documento de miocardite de células gigantes já publicado; preenche lacuna operacional entre os 2 checklists diagnósticos já existentes sobre o mesmo tema.
- **casos-clinicos**: +1 — `sindrome-poems-hipertensao-pulmonar-derrame-pericardico` — tema Hipertensão pulmonar, diferencial com amiloidose AL.
- **PMIDs novos**: Erdheim-Chester acrescentou PMID 22300602, 29188284, 32187362, 25738753, 30569522 (além dos 4 já citados no caso do lote 20); POEMS: PMID 37732822, 31012139, 22983590, 28894560; checklist reaproveitou referências já citadas no documento-origem (Naseeb 2023, Kandolin 2013) mais a Diretriz SBC 2022 (PMID 35830116). Nenhum PMID inventado, nenhuma duplicação de fingerprint detectada.
- **Slugs pulados por duplicação**: nenhum.
- **Gates**: `audit_tudo_com_tudo.py` → `broken_references: []`; `content_inventory.py --strict` → exit 0, `invalid: []`, `missing: []`.
- **Total canônico**: 10.248 (10.189 revisado + 59 pendente_revisao desta frente).

### Status consolidado (após Lote 21)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 5 | 2.395 |
| Casos clínicos | 900 | 26 | 874 |
| Checklists | 600 | 9 | 591 |
| Materiais-paciente | 500 | 17 | 483 |
| Trilhas | 300 | 1 | 299 |
| Doenças especializadas | 200 | 1 (3 descartados por colisão) | 199 |
| **Total** | **4.900** | **59** | **4.841** |

## Lote 22 — concluído (commit 62065c00)

- **content/Cardiomiopatias**: +1 — `fibroelastoma-papilar-cardiaco-diagnostico-ecocardiografico-risco-embolico-e-indicacao-cirurgica`.
- **content/Aorta_e_doença_arterial_periférica**: +1 — `doenca-de-behcet-e-envolvimento-cardiovascular-aneurismas-trombose-e-sindrome-de-hughes-stovin`.
- **material-paciente**: +1 — `aneurisma-inflamatorio-da-aorta-doenca-relacionada-a-igg4` (pareado com o documento do lote 20).
- **ACHADO DE SCHEMA (dívida aberta)**: `material-paciente/metadados.json` tem 3 campos reais além dos documentados — `sinais_de_alerta`, `perguntas`, `fontes` — presentes em 408/425 registros pré-existentes. Os 17 materiais-paciente entregues por esta frente nos lotes 2-19 **não têm** esses 3 campos (confirmado por diff de chaves contra o schema real). Remediação dispatchada a seguir como lote dedicado.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.251 (10.189 revisado + 62 pendente_revisao).

### Status consolidado (após Lote 22)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 7 | 2.393 |
| Casos clínicos | 900 | 26 | 874 |
| Checklists | 600 | 9 | 591 |
| Materiais-paciente | 500 | 18 | 482 |
| Trilhas | 300 | 1 | 299 |
| Doenças especializadas | 200 | 1 (3 descartados por colisão) | 199 |
| **Total** | **4.900** | **62** | **4.838** |

## Remediação de schema — concluída (commit c49847e8)

Dívida aberta no checkpoint do Lote 22 fechada: os 17 materiais-
paciente entregues nos lotes 2-19 agora têm os 3 campos reais do
schema (`sinais_de_alerta`, `perguntas`, `fontes`), preenchidos por
4 agentes paralelos com fontes individualmente verificadas via
PubMed/Europe PMC/GeneReviews — nenhuma referência inventada; um caso
descartou uma citação não localizável e usou a fonte real mais
próxima do mesmo achado. `sinais_de_alerta`/`perguntas` derivados
apenas do conteúdo clínico já presente em cada registro.

Verificado: os 426 registros de `material-paciente/metadados.json`
têm agora os 3 campos (0 faltando). Nenhum item novo — só correção.

Gates: `broken_references: []`; `content_inventory.py --strict` exit 0.

**Lição geral reforçada**: sempre confirmar o schema real (chaves de
um item existente do manifesto) antes de produzir um novo tipo de
conteúdo — meus dois achados de dívida nesta frente (revisao como
objeto vs. string; e agora estes 3 campos ausentes) vieram de nunca
ter conferido um item completo e real antes da primeira produção
daquele tipo.

## Lote 23 — concluído (commit 31ff546b)

- **doencas**: +1 — `doenca-de-behcet`.
- **checklists**: +1 — `anticoagulacao-em-trombose-venosa-ou-trombo-intracardiaco-na-doenca-de-behcet`.
- **trilhas**: +1 — `trilha-aorta-mimetizadores-raros-igg4-erdheim-chester-behcet` (5 etapas: síndrome aórtica aguda → Takayasu/células gigantes → IgG4-RD → caso Erdheim-Chester → Behçet). Verificado contra `trilha-aorta-vasculites-e-doenca-renovascular` pré-existente para confirmar ausência de sobreposição (foco distinto: aneurisma/mimetizador inflamatório vs. doença oclusiva).
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.254 (10.189 revisado + 65 pendente_revisao).

### Status consolidado (após Lote 23)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 7 | 2.393 |
| Casos clínicos | 900 | 26 | 874 |
| Checklists | 600 | 11 | 589 |
| Materiais-paciente | 500 | 18 | 482 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 2 (3 descartados por colisão) | 198 |
| **Total** | **4.900** | **66** | **4.834** |

## Lote 24 — concluído (commit cdae6db8)

- **content/Cardiologia_geriátrica**: +1 — `estenose-aortica-e-amiloidose-cardiaca-por-transtirretina-overlap-no-idoso` (11-16% de coexistência EA/ATTR em 5 coortes; evidência de que tratar as duas doenças — TAVI + tafamidis — dá o melhor prognóstico, Nitsche et al. 2025 PMID 40452225).
- **casos-clinicos**: +1 — `beriberi-cardiaco-pos-cirurgia-bariatrica-ic-alto-debito-reversivel-com-tiamina`.
- **material-paciente**: +1 — `doenca-de-behcet-e-o-coracao-por-que-ela-causa-trombose-e-aneurismas-ao-mesmo-tempo`.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.257 (10.189 revisado + 68 pendente_revisao).

### Status consolidado (após Lote 24)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 8 | 2.392 |
| Casos clínicos | 900 | 27 | 873 |
| Checklists | 600 | 11 | 589 |
| Materiais-paciente | 500 | 20 | 480 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 2 (3 descartados por colisão) | 198 |
| **Total** | **4.900** | **69** | **4.831** |

## Lote 25 — concluído (commit 0159c802)

- **content/Cardiomiopatias**: +1 — `reativacao-da-doenca-de-chagas-apos-transplante-cardiaco`. Sobreposição parcial registrada com subseção curta pré-existente em `miocardite-chagasica-aguda-e-miocardites-tropicais-sbc-2022.md` — aprofundamento dedicado, não duplicata; decisão de eventual consolidação fica com o Rafael.
- **casos-clinicos**: +1 — `miocardite-de-celulas-gigantes-choque-cardiogenico-bloqueio-av-refratario-imunossupressao-combinada` (pareado com doc+checklist do lote 21).
- **material-paciente**: +1 — `estenose-aortica-e-amiloidose-ao-mesmo-tempo-o-que-significa-para-o-tavi` (pareado com o documento do lote 24).
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.260 (10.189 revisado + 71 pendente_revisao).
- **PR #709**: OPEN, mergeable, checks verdes — sem mudança, aguardando Rafael.
- **PR #778**: OPEN, draft — sem mudança de status (gate editorial permanece vermelho por desenho).

### Status consolidado (após Lote 25)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 9 | 2.391 |
| Casos clínicos | 900 | 28 | 872 |
| Checklists | 600 | 11 | 589 |
| Materiais-paciente | 500 | 21 | 479 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 2 (3 descartados por colisão) | 198 |
| **Total** | **4.900** | **71** | **4.829** |

## Lote 26 — concluído (commit 706b1136)

- **doencas**: +2 — `fibroelastoma-papilar-cardiaco` (pareado com lote 22), `sindrome-poems` (pareado com lote 21).
- **checklists**: +1 — `vigilancia-de-reativacao-da-doenca-de-chagas-pos-transplante-cardiaco` (pareado com lote 25).
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.263 (10.189 revisado + 74 pendente_revisao).

### Status consolidado (após Lote 26)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 9 | 2.391 |
| Casos clínicos | 900 | 28 | 872 |
| Checklists | 600 | 12 | 588 |
| Materiais-paciente | 500 | 21 | 479 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 4 (3 descartados por colisão) | 196 |
| **Total** | **4.900** | **76** | **4.824** |

## Lote 27 — concluído (commit b9d8c683)

- **content/Cardiomiopatias**: +1 — `granulomatose-eosinofilica-com-poliangiite-egpa-e-envolvimento-cardiovascular`. Pareado retroativamente com o material-paciente `egpa-granulomatose-eosinofilica-e-o-coracao` (documento_slug atualizado).
- **casos-clinicos**: +1 — `amiloidose-atrial-isolada-vs-amiloidose-sistemica-achado-incidental`.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.265 (10.189 revisado + 76 pendente_revisao).

### Status consolidado (após Lote 27)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 10 | 2.390 |
| Casos clínicos | 900 | 29 | 871 |
| Checklists | 600 | 12 | 588 |
| Materiais-paciente | 500 | 21 | 479 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 4 (3 descartados por colisão) | 196 |
| **Total** | **4.900** | **78** | **4.822** |

## Lote 28 — concluído (commit 530f455c)

- **content/Cardiomiopatias**: +1 — `tumores-cardiacos-malignos-primarios-angiossarcoma-e-linfoma-cardiaco-primario`.
- **casos-clinicos**: +1 — `derrame-pericardico-hemorragico-recorrente-angiossarcoma-atrio-direito`.
- **Achado de verificação**: 1 falso alarme no processo de checagem de links — `grep -rl "^slug: $slug$"` não casa quando o front-matter usa `slug: "valor"` (com aspas); o arquivo existia. Ajustar checagens futuras para `grep -rlE "^slug: \"?$slug\"?$"`.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.267 (10.189 revisado + 78 pendente_revisao).

### Status consolidado (após Lote 28)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 11 | 2.389 |
| Casos clínicos | 900 | 30 | 870 |
| Checklists | 600 | 12 | 588 |
| Materiais-paciente | 500 | 21 | 479 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 4 (3 descartados por colisão) | 196 |
| **Total** | **4.900** | **80** | **4.820** |

## Lote 29 — concluído (commit 9c7334d6)

- **doencas**: +1 — `tumores-cardiacos-malignos-primarios` (pareado com lote 28).
- **material-paciente**: +1 — `achado-de-massa-no-coracao-entendendo-a-investigacao` (tom cuidadoso, momento de incerteza diagnóstica, sem presumir prognóstico).
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.269 (10.189 revisado + 80 pendente_revisao).

### Status consolidado (após Lote 29)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 11 | 2.389 |
| Casos clínicos | 900 | 30 | 870 |
| Checklists | 600 | 12 | 588 |
| Materiais-paciente | 500 | 22 | 478 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 5 (3 descartados por colisão) | 195 |
| **Total** | **4.900** | **82** | **4.818** |

## Lote 30 — concluído (commit 8260bbb7)

- **checklists**: +2 — `fibroelastoma-papilar-cardiaco-decisao-ressecao-vs-vigilancia` (lote 22), `rastreio-de-amiloidose-cardiaca-por-transtirretina-em-idoso-encaminhado-para-tavi` (lote 24).
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.271 (10.189 revisado + 82 pendente_revisao).

### Status consolidado (após Lote 30) — marco: 30 lotes, 84 itens entregues

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 11 | 2.389 |
| Casos clínicos | 900 | 30 | 870 |
| Checklists | 600 | 14 | 586 |
| Materiais-paciente | 500 | 22 | 478 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 5 (3 descartados por colisão) | 195 |
| **Total** | **4.900** | **84** | **4.816** |

**Nota de ritmo**: 84 itens em 30 lotes ao longo desta sessão contínua.
No ritmo atual, a cota completa exigiria muitas sessões adicionais —
consistente com a natureza indefinida da diretiva (prazo 04/09,
trabalho contínuo até ordem explícita do Rafael para pausar). Padrões
consolidados que seguem sendo reaplicados: mineração em interseções
raras cardiovasculares (alta taxa de acerto, ~0 colisões nos últimos
15 lotes), verificação manual de cada link "Tudo com Tudo" antes do
commit (pegou 1 alucinação real no lote 20, 1 falso-positivo por
aspas no lote 28), e pareamento retroativo de documento_slug quando
um documento novo cobre um material-paciente pré-existente.

## Lote 31 — concluído (commit 98dcb0f0)

- **content/Insuficiência_cardíaca**: +1 — `cardiomiopatia-por-deficiencia-de-selenio-doenca-de-keshan-e-formas-adquiridas`.
- **casos-clinicos**: +1 — `cardiomiopatia-dilatada-por-deficiencia-de-selenio-em-npt-prolongada`.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.273 (10.189 revisado + 84 pendente_revisao).

### Status consolidado (após Lote 31)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 12 | 2.388 |
| Casos clínicos | 900 | 31 | 869 |
| Checklists | 600 | 14 | 586 |
| Materiais-paciente | 500 | 22 | 478 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 5 (3 descartados por colisão) | 195 |
| **Total** | **4.900** | **86** | **4.814** |

## Lote 32 — concluído (commit a32e220a)

- **doencas**: +1 — `cardiomiopatia-por-deficiencia-de-selenio` (pareado com lote 31).
- **material-paciente**: +1 — `falta-de-selenio-pode-enfraquecer-o-coracao-o-que-saber`.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.275 (10.189 revisado + 86 pendente_revisao).

### Status consolidado (após Lote 32)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 12 | 2.388 |
| Casos clínicos | 900 | 31 | 869 |
| Checklists | 600 | 14 | 586 |
| Materiais-paciente | 500 | 23 | 477 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 6 (3 descartados por colisão) | 194 |
| **Total** | **4.900** | **88** | **4.812** |

## Lote 33 — concluído (commit 449da2a9)

- **checklists**: +2 — `cardiomiopatia-deficiencia-primaria-carnitina` (lote 1), `reconhecimento-e-conduta-inicial-complicacoes-vasculares-acesso-cateterismo` (lote 1).
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.277 (10.189 revisado + 88 pendente_revisao).

### Status consolidado (após Lote 33)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 12 | 2.388 |
| Casos clínicos | 900 | 31 | 869 |
| Checklists | 600 | 16 | 584 |
| Materiais-paciente | 500 | 23 | 477 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 6 (3 descartados por colisão) | 194 |
| **Total** | **4.900** | **90** | **4.810** |

## Lote 34 — concluído (commit ea3c3dac)

- **content/Insuficiência_cardíaca**: +1 — `cardiomiopatia-dilatada-reversivel-por-hipocalcemia-grave`.
- **casos-clinicos**: +1 — `cardiomiopatia-dilatada-hipocalcemia-hipoparatireoidismo-pos-tireoidectomia`.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.279 (10.189 revisado + 90 pendente_revisao).

### Status consolidado (após Lote 34)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 13 | 2.387 |
| Casos clínicos | 900 | 32 | 868 |
| Checklists | 600 | 16 | 584 |
| Materiais-paciente | 500 | 23 | 477 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 6 (3 descartados por colisão) | 194 |
| **Total** | **4.900** | **92** | **4.808** |

## Lote 35 — concluído (commit ea2d439a)

- **doencas**: +1 — `cardiomiopatia-dilatada-por-hipocalcemia-grave` (pareado com lote 34).
- **checklists**: +1 — `investigacao-de-cardiomiopatia-dilatada-com-suspeita-de-hipocalcemia-grave`.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.281 (10.189 revisado + 92 pendente_revisao).
- **PR #709/#778**: sem mudança de status, verificados neste ciclo.

### Status consolidado (após Lote 35)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 13 | 2.387 |
| Casos clínicos | 900 | 32 | 868 |
| Checklists | 600 | 17 | 583 |
| Materiais-paciente | 500 | 23 | 477 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 7 (3 descartados por colisão) | 193 |
| **Total** | **4.900** | **94** | **4.806** |

## Marco: primeira revisão editorial independente (commit 6afe6673, 30/08)

Rafael, com revisão independente do Codex, executou pela primeira vez o segundo
estágio do regime de revisão em dois estágios: promoveu 79 registros e 13
documentos de `pendente_revisao` para `revisado`, adicionando `fonte_producao:
"claude"` e `review_note` com a data e o escopo da revisão (estrutura, fontes
declaradas, consistência interna, segurança clínica, vínculos canônicos). O
commit também **removeu posologia acionável de materiais leigos** (ex.:
"aspirina em dose baixa, em geral 100 mg por dia" → "aspirina em baixa dose, na
posologia individualmente prescrita") — padrão de segurança que passo a aplicar
proativamente em todo material-paciente novo: nunca declarar dose numérica
acionável a público leigo. Novo diretório `editorial-approvals/` criado com os
artefatos de certificação do lançamento de 29/08.

Push do Lote 36 exigiu rebase (`git rebase origin/claude/science-scale-20k-20260904`)
por conflito de seam em `material-paciente/metadados.json` entre o fechamento do
commit de revisão e meu item recém-anexado — resolvido preservando ambos os
lados, gates reverificados, push concluído sem perda de trabalho de nenhuma
parte. Regra "nunca autopromover `review_status`" permanece integralmente em
vigor — apenas o artefato de certificação passou a existir de fato.

## Lote 36 — concluído (commit 79b585d0)

- **content/Cardiomiopatias**: +1 — `cardiomiopatia-acromegalica-historia-natural-mecanismos-e-reversibilidade`.
- **material-paciente**: +1 — material de apoio para hipocalcemia grave (pareado com lote 34).
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0 (pós-rebase).
- **Total canônico**: 10.283 (10.281 revisado + 2 pendente_revisao).

### Status consolidado (após Lote 36)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 14 | 2.386 |
| Casos clínicos | 900 | 32 | 868 |
| Checklists | 600 | 17 | 583 |
| Materiais-paciente | 500 | 24 | 476 |
| Trilhas | 300 | 2 | 298 |
| Doenças especializadas | 200 | 7 (3 descartados por colisão) | 193 |
| **Total** | **4.900** | **96** | **4.804** |

## Lote 37 — concluído (commit 82cb3323)

Ritmo acelerado a pedido explícito do Rafael ("maximo de agentes, acelere") —
8 agentes dispatchados em paralelo nesta rodada (recorde da sessão, ante o
padrão de 1-3 agentes/lote usado até o Lote 36).

- **content/Cardiomiopatias**: +2 — `cardiomiopatia-dilatada-por-deficiencia-de-cobre-causas-adquiridas-doenca-de-menkes-e-reversibilidade`, `amiloidose-relacionada-a-dialise-beta2-microglobulina-e-acometimento-cardiovascular`.
- **doencas**: +2 — `cardiomiopatia-acromegalica`, `granulomatose-eosinofilica-com-poliangiite-egpa` (ambas pareadas com documentos já existentes).
- **checklists**: +2 — `avaliacao-cardiovascular-inicial-e-seguimento-na-acromegalia`, `rastreio-cardiovascular-ativo-na-egpa-recem-diagnosticada`.
- **casos-clinicos**: +2 — `picada-bothrops-jararaca-coagulopatia-choque-procedimento-invasivo`, `avc-embolico-endocardite-libman-sacks-lupus-e-sindrome-antifosfolipide`.
- **trilhas**: +1 — `trilha-cardiomiopatias-metabolicas-reversiveis-do-adulto` (montada diretamente por mim, sem despacho de agente, unificando o cluster selênio/cobre/beribéri/hipocalcemia/acromegalia/alcoólica dos lotes 31-37 sob um único padrão clínico).
- **Verificação**: todos os slugs de colisão e todos os links "Tudo com Tudo" reconferidos manualmente contra o worktree antes da integração (2 agentes propuseram links para selênio/hipocalcemia que julgaram inexistentes por checarem `/opt/meucardio` — que segue `origin/main`, não minha branch — corrigido na integração).
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.292 (10.281 revisado + 11 pendente_revisao).

### Status consolidado (após Lote 37)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 16 | 2.384 |
| Casos clínicos | 900 | 34 | 866 |
| Checklists | 600 | 19 | 581 |
| Materiais-paciente | 500 | 24 | 476 |
| Trilhas | 300 | 3 | 297 |
| Doenças especializadas | 200 | 9 (3 descartados por colisão) | 191 |
| **Total** | **4.900** | **105** | **4.795** |

## Lote 38 — concluído (commit 5d3aed3a)

- **content/Cardiomiopatias**: +1 — `doenca-de-wilson-acometimento-cardiovascular-fisiopatologia-manifestacoes-e-terapia-quelante` (par de contraste mecanístico do documento de deficiência de cobre do lote 37: mesmo elemento, direção metabólica oposta).
- **content/Terapia_intensiva**: +1 — `sindrome-de-realimentacao-e-cardiotoxicidade-por-hipofosfatemia-grave`.
- **doencas**: +2 — `cardiomiopatia-dilatada-por-deficiencia-de-cobre`, `amiloidose-relacionada-a-dialise-beta2-microglobulina` (pareadas com os dois documentos do lote 37).
- **checklists**: +2 — investigação/manejo da cardiomiopatia por deficiência de cobre; rastreio de amiloidose relacionada à diálise.
- **casos-clinicos**: +1 — `escorpionismo-grave-tempestade-catecolaminergica-crianca` (Tityus serrulatus, tempestade catecolaminérgica, armadilha do edema pulmonar tratado como anafilaxia).
- **material-paciente**: +1 — `deficiencia-de-cobre-e-o-coracao`, sem nenhuma dose numérica acionável (política de segurança pós-revisão de 29/08 aplicada proativamente).
- **Correção de schema durante integração**: um agente propôs o mesmo slug para a doença de amiloidose-diálise e para seu documento técnico irmão — nenhum precedente no corpus tem doença e documento compartilhando slug idêntico (risco de colisão de rota `/biblioteca/<slug>`); renomeado para um slug mais curto e distinto antes de integrar, seguindo o padrão já usado em EGPA/acromegalia.
- **Verificação**: 2 agentes reportaram não conseguir confirmar a existência dos documentos de deficiência de cobre e diálise-amiloidose (criados no lote 37) por checarem apenas `/opt/meucardio` — comportamento esperado e já documentado; confirmado manualmente contra o worktree antes de integrar, e o link ao documento de cobre foi adicionado ao "Tudo com Tudo" do documento de Wilson.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.300 (10.281 revisado + 19 pendente_revisao).

### Status consolidado (após Lote 38)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 18 | 2.382 |
| Casos clínicos | 900 | 35 | 865 |
| Checklists | 600 | 21 | 579 |
| Materiais-paciente | 500 | 25 | 475 |
| Trilhas | 300 | 3 | 297 |
| Doenças especializadas | 200 | 11 (3 descartados por colisão) | 189 |
| **Total** | **4.900** | **113** | **4.787** |

## Lote 39 — concluído (commit ddd50714)

- **content/Cardiologia_geriátrica**: +1 — `hipertireoidismo-apatico-no-idoso-fenotipo-atipico-fibrilacao-atrial-e-insuficiencia-cardiaca`.
- **content/Cardiomiopatias**: +1 — `sindrome-de-cushing-e-risco-cardiovascular-mecanismos-cardiomiopatia-e-risco-residual`.
- **doencas**: +1 — `doenca-de-wilson-cardiovascular` (pareada com documento do lote 38).
- **checklists**: +2 — rastreio cardiovascular na doença de Wilson; prevenção/manejo da síndrome de realimentação.
- **casos-clinicos**: +2 — loxoscelismo cutâneo-visceral (hemólise/CIVD/LRA); toxoplasmose reativada pós-transplante cardíaco (miocardite vs. rejeição).
- **material-paciente**: +1 — síndrome de realimentação, tom não estigmatizante para contexto de transtorno alimentar, sem dose/meta calórica numérica.
- **Correções durante integração**: `prevalence_rank: null` de um agente corrigido para valor inteiro coerente (padrão do manifesto); entidades HTML (`&lt;`) corrigidas em dois documentos.
- **Gates**: `broken_references: []`; `content_inventory.py --strict` exit 0.
- **Total canônico**: 10.308 (10.281 revisado + 27 pendente_revisao).

### Status consolidado (após Lote 39)

| Tipo | Cota Claude | Entregues | Restante |
|---|---:|---:|---:|
| Documentos (content/) | 2.400 | 20 | 2.380 |
| Casos clínicos | 900 | 37 | 863 |
| Checklists | 600 | 23 | 577 |
| Materiais-paciente | 500 | 26 | 474 |
| Trilhas | 300 | 3 | 297 |
| Doenças especializadas | 200 | 12 (3 descartados por colisão) | 188 |
| **Total** | **4.900** | **121** | **4.779** |
