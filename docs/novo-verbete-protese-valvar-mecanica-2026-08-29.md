# Verbete novo — Prótese valvar mecânica: escolha, anticoagulação e trombose — 29/08/2026

## Contexto

Não existia ficha própria de doença/entidade clínica para **prótese valvar
mecânica** em `doencas/metadados.json`, apesar de corpus extenso já
publicado em `content/Valvopatias/` (escolha mecânica vs. biológica e alvo
de INR, trombose aguda e ambos os fluxogramas ESC/EACTS 2021 e 2025) e em
`content/Tromboembolismo/` (RE-ALIGN sobre a contraindicação de DOAC, e a
revisão histórica PRO-TEE/Roudaut/Karthikeyan sobre trombólise vs.
cirurgia).

Criado via `doencas/fragmentos/protese-valvar-mecanica.json` — **não** via
edição direta de `doencas/metadados.json` — para minimizar colisão com
outras frentes de produção concorrentes (nesta mesma data, dezenas de
outras frentes produziam verbetes em paralelo, confirmado pela contenção de
lock observada no banco de teste compartilhado durante a execução dos
gates).

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: taxa de trombose sem anticoagulação (12%/ano aórtica,
  22%/ano mitral, primeira geração), coorte histórica de Roudaut et al.
  (263 episódios), registro PRO-TEE (107 pacientes, corte de 0,8 cm²),
  metanálise de Karthikeyan et al. 2013 (690 episódios), o primeiro ensaio
  randomizado SAFE-PVT (79 pacientes, 2025) e o ensaio RE-ALIGN (252
  pacientes, interrompido precocemente).
- `presentation` (10), `diagnostic_approach` (dict aninhado com 4 eixos:
  confirmação da trombose valvar, obstrutiva vs. não obstrutiva, avaliação
  para escolha entre fibrinólise e cirurgia, escolha de prótese na
  indicação inicial — mais de 3.700 caracteres), `differentials` (8,
  incluindo pannus, trombose de bioprótese, endocardite protética,
  discordância paciente-prótese), `tests` (8), `red_flags` (8).
- `treatment_summary` (~3.800 caracteres): anticoagulação crônica
  obrigatória com AVK e alvo de INR individualizado tratado como
  informação de classificação de risco (não esquema posológico),
  contraindicação formal de DOAC/dupla antiagregação (RE-ALIGN), decisão
  aguda entre fibrinólise em baixa dose/infusão lenta e cirurgia via Heart
  Team (ESC/EACTS 2025), manejo de trombo não obstrutivo, escolha inicial
  de tipo de prótese — sem nenhuma dose de fármaco.
- `ambulatory_flow` (10), `emergency_flow` (9), `monitoring` (7).
- `special_populations` (7): gestante (remetida à ficha própria já
  publicada), idoso, prótese em posição direita, contraindicação relativa a
  anticoagulação, fator pró-trombótico adicional, múltiplas próteses
  mecânicas, indicação concomitante de anticoagulação por outro motivo.
- `assistant_questions` (19), `assistant_rules` (18, priority 97 para
  trombose obstrutiva com IC aguda NYHA III-IV — a regra de maior risco
  clínico do fluxograma-fonte).
- `related_document_slugs` (7, verificados individualmente).
- `patient_material_slug` preenchido:
  `vivendo-com-uma-valvula-mecanica-anticoagulacao-e-cuidados-no-dia-a-dia`.

## Verificação dos 7 related_document_slugs (Tudo com Tudo)

Cada um dos documentos mapeados foi **lido por completo** nesta sessão,
confirmando discussão CENTRAL (não tangencial) do tema prótese valvar
mecânica:

1. `trombose-de-protese-valvar-mecanica-diagnostico-e-decisao-entre-fibrinolise-e-cirurgia`
2. `fluxograma-trombose-de-protese-valvar-mecanica-fibrinolise-vs-cirurgia-esc-eacts-2021`
3. `fluxograma-trombose-de-protese-valvar-mecanica-fibrinolise-vs-cirurgia-esc-eacts-2025`
4. `protese-valvar-escolha-mecanica-vs-biologica-e-alvo-de-inr-esc-eacts-2025`
5. `fluxograma-escolha-de-protese-valvar-mecanica-vs-biologica-esc-eacts-2025`
6. `anticoagulante-oral-direto-em-protese-valvar-mecanica-por-que-e-contraindicado-re-align`
7. `trombose-de-protese-valvar-mecanica-trombolise-versus-cirurgia-de-urgencia`

O candidato mapeado inicialmente para exclusão,
`antitrombotico-nos-primeiros-3-meses-apos-biopotese-valvar-esc-eacts-2021`,
foi confirmado como fora de escopo — trata de **bioprótese** (valva
biológica), não de prótese mecânica, conforme instrução explícita da
tarefa. Também foram avaliados e descartados por menor centralidade:
`trombose-obstrutiva-de-protese-valvar-na-uco-cirurgia-fibrinolise-e-heart-team.md`
(cobre mecânica **e** biológica, redundante com as fontes ESC/EACTS 2025 já
centrais desta ficha) e `endocardite-protetica-precoce-versus-tardia-esc-2023.md`
(tema central é endocardite, não escolha/anticoagulação/trombose).

Nenhum candidato resolve para `content/Farmacologia/`,
`content/Calculadoras/` ou `content/Exames/`.

## Verificação de PMIDs

9 PMIDs verificados individualmente via NCBI e-utils (`esummary`) em
29/08/2026, conferindo título, periódico, ano, volume e páginas contra o
registro oficial do PubMed antes de persistir no `source_refs` — nenhuma
correção necessária (todos batem com a citação já usada nos
documentos-fonte publicados):

- 40878295 (ESC/EACTS 2025, valvopatias)
- 34453165 (ESC/EACTS 2021, valvopatias)
- 40574603 (SAFE-PVT, Karthikeyan et al., Eur Heart J 2025)
- 19427604 (Roudaut et al., coorte histórica, Arch Cardiovasc Dis 2009)
- 23991661 (RE-ALIGN, Eikelboom et al., NEJM 2013)
- 14715187 (PRO-TEE, Tong et al., JACC 2004)
- 23329151 (Karthikeyan et al., metanálise, Eur Heart J 2013)
- 17170355 (Roudaut et al., revisão, Heart 2007)
- 42412081 (Raj Mantoo et al., revisão, Expert Rev Cardiovasc Ther 2026)

## Nota editorial sobre `category`

`category: "valvopatia_e_anticoagulacao"` reutiliza a única convenção já
existente no sistema para esse cruzamento temático — confirmada por
listagem programática de todas as categorias em `doencas/metadados.json` e
`doencas/fragmentos/*.json` nesta sessão, encontrando um único uso prévio
em `protese-mecanica-na-gravidez`. Preferida a `valvopatia` simples (usada
em `valvopatias`, `estenose-aortica-tavi-idoso`, `valvopatias-na-gravidez`)
porque esta ficha é tão sobre anticoagulação obrigatória quanto sobre a
prótese em si. `subtype: "protese_mecanica"` também replica a convenção já
usada em `protese-mecanica-na-gravidez`.

## Sobreposição de related_document_slugs documentada

Ao contrário do padrão "um hub só" usado em `cardiomiopatia-de-takotsubo`,
este verbete compartilha `related_document_slugs` com **três** registros já
existentes no catálogo combinado:

- `valvopatias` (hub geral): 5 dos 7 slugs — os dois fluxogramas de
  trombose 2021/2025, o documento de trombose ESC/EACTS 2025, o documento
  de escolha mecânica-vs-biológica/INR e o fluxograma de escolha.
- `protese-mecanica-na-gravidez`: 2 slugs — RE-ALIGN e o documento de
  escolha/INR.
- `anticoagulacao-idoso`: 1 slug — o documento de escolha/INR.

Essa sobreposição é esperada e aceitável: este verbete é a ficha específica
sobre a entidade "prótese valvar mecânica" dentro do hub geral
`valvopatias` (mesmo padrão já usado para `cardiomiopatia-de-takotsubo`
dentro do hub `cardiomiopatias`), e os outros dois registros são recortes
por população (gestação) ou por faixa etária (idoso) do mesmo corpo de
evidência sobre INR-alvo e contraindicação de DOAC — não fichas
concorrentes sobre o mesmo escopo. Verificado programaticamente contra todo
o catálogo combinado: nenhuma sobreposição não documentada com qualquer
outro registro.

## Falha esperada e documentada no gate de review_status

`review_status` permanece `"pendente_revisao"` — conteúdo novo não revisado
por humano não se autoaprova. Por isso:

- `backend/tests/test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **FALHA** para `protese-valvar-mecanica`. Esperado e correto, mesmo
  comportamento estrutural já documentado para `cardiomiopatia-de-takotsubo`:
  a lógica desse teste consome todo registro com `status == "revisado"` no
  primeiro `continue`, antes de qualquer checagem de allowlist — as
  checagens seguintes contra `PENDENTES_LOTES_TUDO_COM_TUDO` só são
  alcançáveis para registros que **já** estão `"revisado"`, nunca para
  `"pendente_revisao"`.
- A entrada `"protese-valvar-mecanica"` foi adicionada a
  `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` mesmo assim,
  porque essa mesma allowlist é reaproveitada por importação direta em
  `backend/tests/test_disease_fragments_canonical.py`, onde a checagem
  contra pendências funciona corretamente.
- Resultado esperado: `test_disease_fragments_canonical.py` passa;
  `test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  falha (esperado, documentado, não contornado) — **exatamente 1 falha**.

## Gates executados

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`;
  `SpecialtyDisease.related_document_slugs`: 1100/1100 resolvidos;
  `SpecialtyDisease.patient_material_slug`: 104/104 resolvidos;
  `review_status.pendente_revisao: 1` (só este registro, no worktree
  isolado desta branch).
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  9.546 registros totais.
- `backend/tests/test_novo_verbete_protese_valvar_mecanica.py`: 17 testes.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada/documentada, 2 passando.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.
- Verificação direta (fora do pytest): nenhuma dose de fármaco (`mg`,
  `mg/kg`, `mcg`, `J/kg`) em nenhum campo de texto do registro — inclusive a
  menção ao RE-ALIGN evita reproduzir os esquemas posológicos de
  dabigatrana/varfarina do documento-fonte, só o resultado clínico do
  ensaio; as faixas de alvo de INR foram tratadas como informação de
  classificação de risco, mesma lógica já usada no documento-fonte
  ESC/EACTS 2025 publicado nesta pasta. Todas as 19 `assistant_questions`
  usam `label`; todas as 18 `assistant_rules` têm `op` e chaves de `add`
  válidos, `priority` 0-100 e `risk` no enum permitido — validado
  programaticamente contra `app.services.clinical_rule_engine`.
- Overlap de `related_document_slugs` verificado programaticamente contra
  todo o catálogo combinado: apenas os três overlaps documentados acima
  (`valvopatias`, `protese-mecanica-na-gravidez`, `anticoagulacao-idoso`).

## Branch e PR

Branch `claude/novo-verbete-protese-valvar-mecanica-20260829`, baseada em
`origin/main` sem drift no momento do commit (`git log HEAD..origin/main`
vazio).
