# Verbete novo — Insuficiência aórtica — 29/08/2026

## Contexto

Rafael pediu a criação do verbete NOVO **"Insuficiência aórtica"**
(regurgitação aórtica crônica e aguda), slug `insuficiencia-aortica`, que
não tinha ficha própria em `doencas/metadados.json` apesar de corpus já
existente em `content/Valvopatias/` (indicação cirúrgica ESC/EACTS 2021,
fluxograma ESC/EACTS 2025, tratamento transcateter dedicado ALIGN-AR/
Trilogy) e `content/Terapia_intensiva/` (IAo aguda grave na UCO).

Antes de iniciar, o registro `insuficiencia-mitral` (criado no mesmo dia,
branch `claude/novo-verbete-insuficiencia-mitral-20260829`, ainda não
mesclada a `main`) foi lido por completo diretamente do Git (`git show`)
para confirmar que é exclusivamente sobre a valva mitral — aliases,
`related_document_slugs` e todo o conteúdo giram em torno de regurgitação
mitral primária/secundária, sem qualquer menção central a valva aórtica.
Confirmado: nenhum overlap de escopo.

Criado via `doencas/fragmentos/insuficiencia-aortica.json` — **não** via
edição direta de `doencas/metadados.json` — para minimizar colisão com
outras frentes de produção concorrentes.

## Conteúdo produzido (verbete completo, do zero)

- `summary` e `epidemiology`: distinção estrutural crônica vs. aguda,
  critérios ecocardiográficos de gravidade (ESC/EACTS Tabela de
  recomendações), evolução dos cortes cirúrgicos no assintomático entre
  2021 e 2025 (corte indexado de 20→22 mm/m², critério volumétrico novo
  VSFVEi >45 mL/m², reparo IIb→IIa), cortes de aorta/raiz por etiologia
  (geral, Marfan/Loeys-Dietz, bicúspide), dados do ensaio pivotal ALIGN-AR
  (n=700, composto de segurança em 30 dias 24,0%, mortalidade em 1 ano
  7,7%, marca-passo definitivo 21,6%) e da metanálise de dispositivos
  dedicados vs. convencionais (Bacigalupi et al.).
- `presentation` (10, cobrindo separadamente o fenótipo crônico clássico e
  o fenótipo aguda atípico — inclusive a ressalva de que ausência de pulso
  em martelo d'água NÃO exclui IAo aguda grave).
- `diagnostic_approach` (dict aninhado com 4 eixos: critérios
  ecocardiográficos de gravidade, avaliação do VE/indicação cirúrgica no
  assintomático crônico, avaliação de raiz/aorta ascendente, reconhecimento
  e diagnóstico da IAo aguda — TTE/TEE e por que não atrasar cirurgia por
  exame eletivo).
- `differentials` (6), `tests` (8), `red_flags` (10, incluindo IABP
  contraindicado e bradicardia como red flag específicos da forma aguda).
- `treatment_summary`: cirurgia como padrão na forma crônica (troca padrão,
  reparo Classe IIa 2025, reimplante valve-sparing), tratamento transcateter
  dedicado como alternativa validada só para alto risco cirúrgico com
  anatomia adequada (armadilhas explícitas: não extrapolar para risco
  baixo/intermediário nem para dupla lesão, não usar dispositivo
  convencional off-label), e cirurgia urgente/imediata como tratamento
  definitivo da forma aguda com suporte hemodinâmico apenas como ponte —
  sem nenhuma dose de fármaco em nenhum campo.
- `ambulatory_flow` (10), `emergency_flow` (12 — reproduzindo o
  checklist operacional da fonte de UCO: reconhecimento, TEE sem atraso,
  frequência cardíaca, pós-carga, choque, ventilação/diurese, IABP
  contraindicado, endocardite, dissecção), `monitoring` (7).
- `special_populations` (7): valva aórtica bicúspide, Marfan/Loeys-Dietz,
  endocardite como causa de IAo aguda, dissecção tipo A como causa de IAo
  aguda, população de alto risco cirúrgico do ALIGN-AR, atleta, trauma/
  iatrogenia como causas menos comuns de IAo aguda.
- `assistant_questions` (20) e `assistant_rules` (16, priority 99 para
  IABP contraindicado em IAo aguda — a regra de maior risco clínico
  identificada nas fontes).
- `related_document_slugs` (5, verificados individualmente).
- `patient_material_slug` preenchido:
  `regurgitacao-aortica-quando-a-valvula-vaza-e-quando-operar`.

## Verificação dos 5 related_document_slugs (Tudo com Tudo)

Os 3 candidatos mapeados por Rafael cobrem apenas a forma crônica e o
tratamento transcateter — nenhum cobre a forma AGUDA explicitamente pedida.
Busca ativa em `content/Terapia_intensiva/` (grep por "insuficiencia
aortica aguda"/"regurgitacao aortica aguda") localizou um 4º documento
dedicado, e busca adicional por "regurgitação aórtica"/"insuficiência
aórtica" em todo `content/` (excluindo Farmacologia/Calculadoras/Exames)
localizou um 5º candidato com seção própria e substancial sobre RA. Todos
os 5 foram **lidos por completo**:

1. `regurgitacao-aortica-cronica-e-aguda-indicacao-cirurgica-esceacts-2021`
   — documento inteiro dedicado à indicação cirúrgica na RA crônica/aguda.
2. `regurgitacao-aortica-nativa-grave-tratamento-transcateter-dedicado-align-ar-trilogy`
   — documento inteiro dedicado ao ALIGN-AR/Trilogy.
3. `fluxograma-insuficiencia-aortica-cronica-grave-quando-intervir-esc-eacts-2025`
   — fluxograma inteiro dedicado à IAo crônica grave.
4. `insuficiencia-aortica-aguda-grave-na-uco-endocardite-disseccao-e-choque`
   — documento inteiro dedicado à IAo aguda grave (necessário para cobrir a
   forma aguda pedida explicitamente; não estava nos 3 candidatos mapeados).
5. `doenca-valvar-elegibilidade-esportiva-no-atleta` — seção própria e
   substancial ("Regurgitação aórtica", ~30 linhas, cortes de dimensão de
   VE e classe/nível de recomendação por gravidade), buscado ativamente
   como exigido pela disciplina de 1-2 alternativas extras.

Outros candidatos foram lidos e **deliberadamente excluídos** por não
serem centrais o suficiente:

- `padrao-de-acometimento-valvar-mitral-versus-aortico-na-cardiopatia-reumatica-cronica-remedy`
  — o achado central do documento é o padrão mitral-primeiro/aórtico-depois
  na cardiopatia reumática (registro REMEDY); RA aparece como uma linha de
  tabela de gravidade, não como discussão central.
- `valva-aortica-bicuspide-e-aortopatia-associada-esc-2024` — central é a
  aortopatia associada à valva bicúspide (dilatação de raiz), RA é
  mencionada apenas de passagem (3 ocorrências, sem seção própria).
- `doenca-valvar-cardiaca-diagnostico-e-manejo-esceacts-20212025` — visão
  geral de valvopatia com seções próprias para estenose aórtica,
  regurgitação mitral e tricúspide, mas **sem seção própria** de
  regurgitação aórtica.
- `valvopatia-e-cirurgia-nao-cardiaca-avaliacao-e-manejo-esc-2022` — tem
  seção "Regurgitação aórtica", porém mais curta (2 parágrafos + 1 tabela)
  e menos central que os 5 documentos escolhidos.

Nenhum candidato resolve para `content/Farmacologia/`,
`content/Calculadoras/` ou `content/Exames/`.

**Sobreposição documentada**: os 3 documentos de RA crônica/aguda/
transcateter também aparecem em `related_document_slugs` do hub geral
`valvopatias` (esperado — o hub cita os mesmos documentos centrais de RA).
O documento de elegibilidade esportiva também aparece em
`related_document_slugs` de `valva-aortica-bicuspide-pediatrica` (esperado
— mesmo documento cobre seções dedicadas de RA e de valva bicúspide).
Verificado programaticamente contra todo o catálogo combinado: nenhuma
outra ficha compartilha `related_document_slugs` com este verbete.

## Verificação de PMIDs

7 PMIDs verificados individualmente via NCBI e-utils (`esummary`) em
29/08/2026, conferindo título, periódico, ano, volume e páginas contra o
registro oficial do PubMed antes de persistir no `source_refs` — todos
concordantes com os documentos-fonte, sem divergência a corrigir:

- 34453165 (Vahanian et al., ESC/EACTS 2021 VHD Guidelines, Eur Heart J)
- 40878295 (Praz et al., ESC/EACTS 2025 VHD Guidelines, Eur Heart J)
- 41260228 (Makkar et al., ALIGN-AR pivotal, Lancet 2025)
- 38552656 (Vahl et al., ALIGN-AR relatório inicial, Lancet 2024)
- 41147394 (Bacigalupi et al., metanálise dispositivos dedicados vs.
  convencionais, J Am Heart Assoc 2025)
- 33332150 (Otto et al., ACC/AHA 2020 VHD Guideline — relatório completo,
  Circulation 2021)
- 39735779 (Miller et al., Acute Decompensated Valvular Disease in the
  ICU, JACC Adv 2024)

## Falha esperada e documentada no gate de review_status

`review_status` permanece `"pendente_revisao"` — conteúdo novo não revisado
por humano não se autoaprova. Por isso:

- `backend/tests/test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **FALHA** para `insuficiencia-aortica`. Esperado e correto, não um bug
  introduzido por este commit — mesma lógica documentada na rodada anterior
  (`cardiomiopatia-de-takotsubo`, PR #698): o teste consome todo registro
  com `status == "revisado"` no primeiro `continue`, antes de qualquer
  checagem de allowlist, tornando as checagens seguintes inalcançáveis para
  registro `"pendente_revisao"`.
- A entrada `"insuficiencia-aortica"` foi adicionada a
  `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` no mesmo
  arquivo de teste, seguindo exatamente o padrão/comentário usado na
  branch `claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829`
  (PR #698), porque essa allowlist é **reaproveitada por importação
  direta** em `test_disease_fragments_canonical.py`, onde a checagem
  funciona corretamente para registro pendente.

## Gates executados

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`;
  `SpecialtyDisease.related_document_slugs`: 1098/1098 resolvidos;
  `SpecialtyDisease.patient_material_slug`: 104/104 resolvidos;
  `review_status.pendente_revisao: 1` (só este registro).
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  9.546 registros totais.
- `backend/tests/test_novo_verbete_insuficiencia_aortica.py`: 14 testes, 14
  passando (após corrigir a lista de palavras acentuadas do teste de
  acentuação — o registro usa "cardíaca", não a palavra "coração" — falha
  de teste, não de conteúdo).
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, 3
  passando.
- `backend/tests/test_canonical_content_review_status.py`: 3 testes, 1
  falha esperada/documentada
  (`test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`),
  2 passando.
- `app.main` importa sem erro.
- Execução combinada final (`pytest tests/test_novo_verbete_insuficiencia_aortica.py
  tests/test_disease_fragments_canonical.py
  tests/test_canonical_content_review_status.py`): **19 passaram, 1 falhou**
  (a falha esperada) — resultado final: exatamente 1 falha documentada em
  todo o pipeline, como pedido.
- Verificação direta (fora do pytest): nenhuma dose de fármaco (`mg`,
  `mg/kg`, `mcg`, `J/kg`) em nenhum campo de texto do registro; todas as
  20 `assistant_questions` usam `label`; todas as 16 `assistant_rules` têm
  `op` e chaves de `add` válidos (nenhuma usa `includes` nem `monitoring`),
  `priority` 0-100 e `risk` no enum permitido.
- Overlap de `related_document_slugs` verificado programaticamente contra
  todo o catálogo combinado (119 registros): overlap apenas com o hub
  `valvopatias` (3 documentos) e com `valva-aortica-bicuspide-pediatrica`
  (1 documento), ambos documentados e cobertos por teste dedicado; sem
  overlap com `insuficiencia-mitral` (frente paralela produzida na mesma
  data).
- Drift contra `origin/main` verificado no momento do commit:
  `git log HEAD..origin/main` vazio.

## Branch e PR

Branch `claude/novo-verbete-insuficiencia-aortica-20260829`, baseada em
`origin/main`.
