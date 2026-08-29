# Verbete novo: MINOCA e dissecção espontânea de artéria coronária (SCAD)

Data: 29/08/2026
Sessão: produção autônoma de conteúdo do Guia de Doenças (Corvia)
Slug: `minoca-e-disseccao-espontanea-arteria-coronaria`
Arquivo: `doencas/fragmentos/minoca-e-disseccao-espontanea-arteria-coronaria.json`

## Por que este verbete foi criado

MINOCA (infarto do miocárdio com artérias coronárias não obstrutivas) e SCAD
(dissecção espontânea de artéria coronária) não tinham ficha própria em
`doencas/metadados.json`, apesar de haver corpus rico já publicado em
`content/`:

- `content/Doença_coronariana/minoca-e-scad-infarto-sem-doenca-coronariana-obstrutiva-e-dissecção-espontânea.md`
- `content/Doença_coronariana/fluxograma-minoca-investigacao-diagnostica.md`
- `content/Doença_coronariana/doenca-isquemica-na-mulher-acuracia-dos-testes-por-sexo-minoca-e-desfechos.md`
- `content/Gravidez/dissecao-coronariana-espontanea-associada-a-gravidez-p-scad.md`
- `content/Gravidez/sindrome-coronariana-aguda-por-scad-na-gestacao-e-puerperio-esc-2025.md`
- `content/Gravidez/fluxograma-sindrome-coronariana-aguda-por-scad-na-gestacao-e-puerperio-esc-2025.md`

As fichas existentes de doença coronariana já cobrem a doença obstrutiva
(`sindrome-coronariana-aguda`, `sindrome-coronariana-cronica`,
`doenca-coronariana-idoso`) e síndrome coronariana aguda na gestação em
geral (`sindrome-coronariana-gravidez`), mas nenhuma trata MINOCA/SCAD como
entidade própria — o registro novo preenche essa lacuna.

## Fontes lidas por completo

Os 7 documentos indicados na missão foram lidos integralmente antes da
redação. Confirmação do slug do primeiro arquivo (nome de arquivo com
caractere especial): o slug real, extraído via `frontmatter.load()`, é
literalmente `minoca-e-scad-infarto-sem-doenca-coronariana-obstrutiva-e-dissecção-espontânea`
(com "ç" e "â" no próprio slug) — reproduzido byte a byte no
`related_document_slugs` do novo registro para garantir resolução correta.

## Decisão sobre o candidato ANOCA/INOCA

`anoca-inoca-angina-e-isquemia-sem-obstrucao-coronariana-esc-2024.md` foi
avaliado com cuidado e **excluído** de `related_document_slugs`. Motivo: o
documento cobre angina/isquemia sem obstrução coronariana em contexto
**crônico/estável** — disfunção microvascular coronariana (CMD) e espasmo
epicárdico/microvascular testados eletivamente fora do cenário de infarto
agudo — enquanto MINOCA é, por definição, um infarto agudo confirmado por
padrão dinâmico de troponina. São entidades clinicamente relacionadas
(ambas envolvem "coronária angiograficamente não obstrutiva") mas
distintas em mecanismo, contexto temporal e conduta. Evidência adicional
dessa distinção: o próprio documento ANOCA/INOCA já lista
`minoca-e-scad-infarto-sem-doenca-coronariana-obstrutiva-e-dissecção-espontânea`
em seu "Tudo com Tudo", mas isso não torna o inverso simetricamente
verdadeiro — ANOCA/INOCA apenas cita a existência do documento de MINOCA/SCAD,
sem discuti-lo centralmente. A ficha `sindrome-coronariana-cronica` (já
existente) é quem lista `anoca-inoca-...` como related_document_slug, o que
confirma que o tema pertence ao domínio crônico/estável. ANOCA/INOCA foi
mantido no corpo do novo verbete apenas como **diferencial** (campo
`differentials`), com nota explícita de que é entidade de contexto
crônico/estável distinta do MINOCA agudo.

## related_document_slugs escolhidos (6, dentro do intervalo 3–7)

Cada um foi verificado por leitura completa, confirmando discussão central
(não tangencial) do tema:

1. `minoca-e-scad-infarto-sem-doenca-coronariana-obstrutiva-e-dissecção-espontânea` — documento central, cobre MINOCA e SCAD desde a definição até a conduta.
2. `fluxograma-minoca-investigacao-diagnostica` — árvore de decisão dedicada ao algoritmo diagnóstico do MINOCA.
3. `doenca-isquemica-na-mulher-acuracia-dos-testes-por-sexo-minoca-e-desfechos` — seção própria e substantiva sobre MINOCA (estudo VIRGO, prevalência 5x maior em mulheres, mortalidade não benigna, SCAD como principal causa de infarto perigestacional).
4. `dissecao-coronariana-espontanea-associada-a-gravidez-p-scad` — registro dedicado de P-SCAD (Mayo Clinic e Kaiser Permanente).
5. `sindrome-coronariana-aguda-por-scad-na-gestacao-e-puerperio-esc-2025` — protocolo de manejo de SCA por SCAD na gestação/puerpério (ESC 2025).
6. `fluxograma-sindrome-coronariana-aguda-por-scad-na-gestacao-e-puerperio-esc-2025` — árvore de decisão correspondente.

Nenhum candidato resolve para `content/Farmacologia/`, `content/Calculadoras/`
ou `content/Exames/`.

### Overlap documentado com outra ficha

Os 3 documentos de Gravidez (itens 4, 5 e 6 acima) também aparecem em
`related_document_slugs` da ficha já existente `sindrome-coronariana-gravidez`.
Esse overlap é **esperado e aceitável**: `sindrome-coronariana-gravidez`
trata SCA na gestação em geral (incluindo causas ateroscleróticas), enquanto
este novo verbete trata MINOCA/SCAD como entidade coronariana própria — as
duas fichas legitimamente apontam para o mesmo material-fonte de SCAD
gestacional sob ângulos diferentes. Documentado em `review_note` do
fragmento e na allowlist de overlap do teste dedicado
(`DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS`).

## PMIDs verificados (8, todos via NCBI E-utilities/esummary em 29/08/2026)

Título, periódico, ano e volume/páginas conferidos byte a byte contra o
retorno da API antes de persistir em `source_refs`:

| PMID | Título (resumido) | Periódico | Ano |
|---|---|---|---|
| 37622654 | 2023 ESC Guidelines for the management of acute coronary syndromes | Eur Heart J | 2023 |
| 29472380 | Spontaneous Coronary Artery Dissection: Current State of the Science (AHA) | Circulation | 2018 |
| 30913893 | Contemporary Diagnosis and Management of MI without Obstructive CAD (AHA/MINOCA) | Circulation | 2019 |
| 30367850 | Reinfarction in Patients with MINOCA | Am J Med | 2019 |
| 28728686 | Spontaneous Coronary Artery Dissection Associated With Pregnancy (Mayo) | J Am Coll Cardiol | 2017 |
| 34001675 | Pregnancy-Associated SCAD: Clinical Characteristics, Outcomes... (Kaiser) | J Invasive Cardiol | 2021 |
| 40878294 | 2025 ESC Guidelines for the management of CVD and pregnancy | Eur Heart J | 2025 |
| 37556656 | Posicionamento Doença Isquêmica do Coração — a Mulher no Centro do Cuidado 2023 (SBC) | Arq Bras Cardiol | 2023 |

## Schema e disciplinas

- `category`: `doenca_coronariana` — categoria **já existente** no sistema
  (confirmada listando as 49 categories em uso via script Python antes do
  uso; não foi necessário criar categoria nova).
- `assistant_questions`: todas usam a chave `label` (nunca `text`).
- `assistant_rules`: 13 regras, ops válidos apenas
  (`eq`, `in`, `truthy`, `falsy`, `lte`, `missing`, `any`), chaves de `add`
  restritas ao conjunto permitido (`risk`, `red_flags`, `supporting`,
  `opposing`, `missing_information`, `suggested_tests`, `differentials`,
  `ambulatory_flow`, `emergency_flow`, `messages`), `risk` sempre em
  `{informativo, rotina, prioritario, urgente, emergencia}`.
- **Nenhuma dose de fármaco em nenhum campo.** A regra clínica de que SCAD
  tem contraindicação relativa a revascularização/antiagregação agressiva
  padrão de SCA aterosclerótica (manejo conservador preferido) foi capturada
  de forma **qualitativa**, em `treatment_summary` e na regra determinística
  `scad_estavel_conservador` (campo `opposing`), sem doses — coberto por
  teste dedicado (`test_regra_de_manejo_conservador_da_scad_e_qualitativa_sem_dose`).
- `patient_material_slug`: resolvido para o material já existente e
  centralmente sobre o tema —
  `infarto-sem-entupimento-da-arteria-o-que-e-minoca-e-a-dissecacao-espontanea-scad`
  ("Infarto sem entupimento da artéria: o que é MINOCA, e o que é a
  dissecção espontânea (SCAD)").

## Gate de review_status — 1 falha esperada e documentada (política vigente)

**Correção de 29/08/2026:** a primeira versão deste relatório descrevia
"2 falhas esperadas", entendendo que `PENDENTES_LOTES_TUDO_COM_TUDO` era uma
allowlist única que contornava os dois testes ao mesmo tempo — e por isso
deixava-a vazia, deliberadamente, achando que preenchê-la contornaria também
o gate principal. Isso estava incorreto e foi corrigido nesta revisão: são
dois testes com propósitos diferentes, mesmo reaproveitando o mesmo nome de
estrutura.

- `test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  só aceita a exceção quando `review_status == "revisado"` **e** o slug está
  na allowlist (ver código-fonte: a condição exige os dois). Como o registro
  novo é `review_status="pendente_revisao"` — o estado honesto para um
  verbete recém-criado, ainda sem revisão editorial humana — essa condição
  nunca é satisfeita, e o teste **continua falhando de propósito**,
  independente do conteúdo da allowlist. Essa é a única falha esperada desta
  PR; a decisão de promover o registro a `revisado` cabe a Rafael, não a
  este agente. Preencher a allowlist aqui não contorna esse gate.
- `test_disease_fragments_canonical.py::test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito`
  reaproveita a mesma estrutura `PENDENTES_LOTES_TUDO_COM_TUDO` (importada de
  `test_canonical_content_review_status.py`), mas com uma checagem mais
  simples: aceita qualquer registro `pendente_revisao` cujo slug esteja na
  allowlist, sem exigir `review_status == "revisado"`. Esse teste serve só
  para reconhecer registros novos pendentes como legítimos no catálogo
  combinado de doenças — não é o gate de publicação. A allowlist **foi**
  preenchida com `"minoca-e-disseccao-espontanea-arteria-coronaria"` em
  `doencas/metadados.json`, seguindo exatamente o precedente das PRs
  #688–696 desta mesma frente, e esse teste agora passa.

Resultado: **exatamente 1 falha** em toda a suíte relevante — a de
`test_canonical_content_review_status.py`, que é o comportamento correto e
esperado. Nenhum contorno foi aplicado ao gate de publicação.

## Resultado dos gates

| Gate | Resultado |
|---|---|
| `scripts/audit_tudo_com_tudo.py` | OK — `broken_references: []`, `SpecialtyDisease.related_document_slugs` 1099/1099 resolvidos, `SpecialtyDisease.patient_material_slug` 104/104 resolvidos |
| `scripts/content_inventory.py --strict` | OK — `invalid: []`, `missing: []`, 9546 registros totais |
| Teste dedicado (`test_novo_verbete_minoca_e_disseccao_espontanea_arteria_coronaria.py`) | 12/12 passaram |
| `test_disease_fragments_canonical.py` | 3/3 passaram |
| `test_canonical_content_review_status.py` | 2 passaram, 1 falha esperada (ver acima) |
| `import app.main` | OK, sem erro |

## Drift contra origin/main

Nenhum commit novo em `origin/main` desde a criação do branch — sem
necessidade de rebase.
