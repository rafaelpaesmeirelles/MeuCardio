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
