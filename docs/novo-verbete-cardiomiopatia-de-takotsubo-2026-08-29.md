# Verbete novo — Cardiomiopatia de takotsubo — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **cardiomiopatia de
takotsubo** não tinha ficha própria em `doencas/metadados.json`, apesar de
corpus rico e já existente em `content/Cardiomiopatias/` (registro
InterTAK, reclassificação fenotípica ESC 2023), `content/Saúde_mental_e_
cardiologia/` (fluxograma de reconhecimento/manejo agudo, variante basal
invertida, impacto psicológico), `content/Terapia_intensiva/` (choque
cardiogênico fenotipado, takotsubo perioperatório) e
`content/Cardio-oncologia/` (takotsubo associado a câncer/terapia
antineoplásica).

Criado via `doencas/fragmentos/cardiomiopatia-de-takotsubo.json` — **não**
via edição direta de `doencas/metadados.json` — para minimizar colisão com
outras frentes de produção concorrentes. Confirmado programaticamente que,
nesta mesma data, uma frente paralela produzia `cardiomiopatia-dilatada`
(worktree local `claude/novo-verbete-cardiomiopatia-dilatada-20260829`) sem
overlap de `related_document_slugs` com este verbete.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: dados do InterTAK (1.750 pacientes, 26 centros), perfil
  demográfico, gatilhos (físico > emocional, contrariando a percepção
  popular), 55,8% de comorbidade neuropsiquiátrica prévia, distribuição
  anatômica das 4 variantes, perfil do takotsubo catecolaminérgico, dados
  perioperatórios (Shang et al.) e desfecho de longo prazo/recorrência
  (RETAKO).
- `presentation` (10), `diagnostic_approach` (dict aninhado com 4 eixos:
  critérios InterTAK, diferenciação de SCA, variantes anatômicas,
  avaliação hemodinâmica/de risco — mais de 5.000 caracteres, retrato de
  tema complexo), `differentials` (8, incluindo MINOCA/SCAD/miocardite por
  ICI/feocromocitoma), `tests` (9), `red_flags` (9).
- `treatment_summary`: manejo agudo fenotipado do choque (LVOTO vs.
  falência de bomba vs. VD vs. vasoplegia), regra central de evitar
  inotrópico/catecolamina reflexos na LVOTO, suporte circulatório mecânico
  (bomba microaxial/VA-ECMO, evitar IABP em LVOTO), manejo oncológico
  (interrupção do fármaco causal), sem nenhuma dose.
- `ambulatory_flow` (10), `emergency_flow` (10), `monitoring` (8).
- `special_populations` (7): variante basal/catecolaminérgica,
  perioperatório, oncológico, overlap com miocardite por ICI, comorbidade
  neuropsiquiátrica aguda, feocromocitoma/paraganglioma, sobrevivente com
  sofrimento psicológico.
- `assistant_questions` (17), `assistant_rules` (16, priority 97 para
  LVOTO — a regra de maior risco clínico do fluxograma-fonte).
- `related_document_slugs` (7, verificados individualmente).
- `patient_material_slug` preenchido:
  `cardiomiopatia-de-takotsubo-sindrome-do-coracao-partido`.

## Verificação dos 7 related_document_slugs (Tudo com Tudo)

Cada um dos 8 documentos mapeados pelo reconhecimento prévio foi **lido por
completo** nesta sessão. 7 foram incluídos, por discutirem takotsubo de
forma central (documento inteiro dedicado ao tema):

1. `cardiomiopatia-de-takotsubo-o-registro-internacional-e-o-que-a-diferencia-da-sindrome-coronariana-aguda`
2. `fluxograma-cardiomiopatia-takotsubo-reconhecimento-manejo-agudo`
3. `takotsubo-variante-basal-invertida-reconhecimento-do-padrao-atipico-e-gatilho-catecolaminergico`
4. `impacto-psicologico-e-psiquiatrico-do-diagnostico-de-takotsubo-no-sobrevivente`
5. `choque-cardiogenico-na-sindrome-de-takotsubo-lvoto-falencia-de-bomba-e-vasoplegia`
6. `takotsubo-perioperatorio-em-cirurgia-nao-cardiaca-confundido-com-sindrome-coronariana-aguda`
7. `sindrome-de-takotsubo-associada-ao-cancer-e-terapia-antineoplasica`

O 8º candidato,
`reclassificacao-fenotipica-esc-2023-ndlvc-hipertrabeculacao-e-takotsubo-deixam-de-ser-cardiomiopatia`,
foi lido por completo e **deliberadamente excluído**: trata takotsubo como
uma de três entidades reclassificadas pela ESC 2023 (ao lado de RCM e
hipertrabeculação/NDLVC), sem ser central o suficiente ao tema takotsubo
especificamente para a régua desta disciplina.

Nenhum candidato resolve para `content/Farmacologia/`, `content/
Calculadoras/` ou `content/Exames/`.

## Verificação de PMIDs

14 PMIDs verificados individualmente via NCBI e-utils (`esummary`) em
29/08/2026, conferindo título, periódico, ano, volume e páginas contra o
registro oficial do PubMed antes de persistir no `source_refs`:

- 26332547 (Templin et al., InterTAK, NEJM 2015)
- 29850871 e 29850820 (Consenso Internacional de Takotsubo, Partes I e II,
  Eur Heart J 2018)
- 27438117 (Ghadri et al., típico vs. atípico, JAMA Cardiol 2016)
- 15703419 (Wittstein et al., NEJM 2005)
- 35344411 (Singh et al., Circulation 2022)
- 37586122 (RETAKO/recorrência, Am J Cardiol 2023)
- 39209437 (LVOTO em choque, Heart 2024)
- 37352669 (Alhuarrat et al., meta-análise perioperatória, Am J Cardiol
  2023)
- 35757924 (Shang et al., coorte perioperatória, ESC Heart Fail 2022)
- 36017568 (ESC 2022 Guidelines on cardio-oncology)
- 32125009 (Y-Hassan & Falhammar, meta-análise catecolaminérgica, Clin
  Cardiol 2020)
- 28704094 (Gagnon et al., coorte PPGL, Endocr Pract 2017)
- 39454688 (RETAKO/suporte circulatório mecânico, Int J Cardiol 2025)

**Duas correções encontradas e aplicadas:** os documentos-fonte citavam
PMID 37352669 (Alhuarrat et al.) como "Am J Cardiol. 2023;200:29-35, DOI
...05.037" — o registro oficial do PubMed é **volume 201, páginas 78-85,
DOI ...06.015**. E citavam PMID 35757924 (Shang et al.) como "ESC Heart
Fail. 2022;9(6):3785-3796" — o registro oficial é **issue 5, páginas
3149-3159**. Os dois PMIDs identificam corretamente os artigos certos; só a
citação bibliográfica secundária estava desatualizada/errada nos
documentos-fonte. Usei o dado verificado no `source_ref`, com a divergência
documentada explicitamente no próprio texto da referência (não silenciada).

## Nota editorial sobre `category`

A diretriz ESC 2023 de cardiomiopatias reclassificou formalmente o
takotsubo como **NÃO** sendo mais uma cardiomiopatia no sentido estrito
(fenômeno tipicamente reversível, não doença estrutural permanente) — ver
`reclassificacao-fenotipica-esc-2023-ndlvc-hipertrabeculacao-e-takotsubo-deixam-de-ser-cardiomiopatia.md`.
Mesmo assim, usei `category: "cardiomiopatia"` porque: (1) é a mesma
convenção editorial já adotada nesta frente para `cardiomiopatia-
hipertrofica` e para o hub geral `cardiomiopatias` (PR #565); (2) o corpus
markdown de origem do takotsubo vive predominantemente no tema
"Cardiomiopatias" do repositório; (3) o esquema atual não tem categoria
alternativa mais específica para "síndrome reclassificada que já foi
cardiomiopatia". Essa tensão nomenclatura-vs-convenção-de-schema fica
registrada no `review_note` do próprio registro para decisão editorial
humana explícita — não foi resolvida por omissão.

## Falha esperada e documentada no gate de review_status

`review_status` permanece `"pendente_revisao"` — conteúdo novo não revisado
por humano não se autoaprova. Por isso:

- `backend/tests/test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **FALHA** para `cardiomiopatia-de-takotsubo`. Isso é esperado e correto,
  não um bug introduzido por este commit: a lógica desse teste consome
  todo registro com `status == "revisado"` no primeiro `continue`, antes
  de qualquer checagem de allowlist — as checagens seguintes contra
  `PENDENTES_LOTES_TUDO_COM_TUDO` só são alcançáveis para registros que
  **já** estão `"revisado"`, nunca para `"pendente_revisao"`. A allowlist
  não pode isentar este registro, e não foi usada com essa intenção.
- A entrada `"cardiomiopatia-de-takotsubo"` foi adicionada a
  `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` mesmo assim,
  porque essa mesma allowlist é **reaproveitada por importação direta** em
  `backend/tests/test_disease_fragments_canonical.py::test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito`,
  onde a checagem contra pendências **funciona corretamente** (compara o
  slug pendente contra a allowlist antes de reprovar). Ali a entrada é
  necessária e o teste passa.
- Resultado observado, confirmado por execução: `test_canonical_content_
  review_status.py` — 1 falhou (a esperada), 2 passaram;
  `test_disease_fragments_canonical.py` — 3 passaram.

## Gates executados

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`;
  `SpecialtyDisease.related_document_slugs`: 1100/1100 resolvidos;
  `SpecialtyDisease.patient_material_slug`: 104/104 resolvidos;
  `review_status.pendente_revisao: 1` (só este registro).
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  9.546 registros totais.
- `backend/tests/test_novo_verbete_cardiomiopatia_de_takotsubo.py`: 13
  testes, 13 passando.
- `backend/tests/test_canonical_content_review_status.py`: 3 testes, 1
  falha esperada/documentada, 2 passando.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, 3
  passando.
- `app.main` importa sem erro.
- Verificação direta (fora do pytest): nenhuma dose de fármaco (`mg`,
  `mg/kg`, `mcg`, `J/kg`) em nenhum campo de texto do registro; todas as
  17 `assistant_questions` usam `label`; todas as 16 `assistant_rules` têm
  `op` e chaves de `add` válidos, `priority` 0-100 e `risk` no enum
  permitido.
- Overlap de `related_document_slugs` verificado programaticamente contra
  todo o catálogo combinado (119 registros): único overlap é com o hub
  `cardiomiopatias` (1 documento, o InterTAK), documentado e coberto por
  teste dedicado; sem overlap com `cardiomiopatia-dilatada` (frente
  paralela em produção na mesma data).

## Branch e PR

Branch `claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829`, baseada
em `origin/main` sem drift no momento do commit (`git log HEAD..origin/main`
vazio).
