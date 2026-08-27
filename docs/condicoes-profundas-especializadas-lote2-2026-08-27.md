# Lote de profundidade — Condições especializadas (27/08/2026)

Empilhado sobre o lote de condições do adulto (PR #539, já mesclado à `main`
em `3bb0f206`). Não toca os quatro verbetes adultos desse lote (`geral`) nem
o verbete de AVC do PR #538, nem a interface.

## Tema e função

Aprofunda oito fichas **já existentes** em `doencas/metadados.json`,
restritas às quatro áreas especializadas do catálogo (`cardiopediatria`,
`cardiogeriatria`, `cardiooncologia`, `gravidez`), escolhidas por auditoria
objetiva do corpus: eram as fichas com `completeness: "basico"` e maior
impacto clínico dentro de cada área — canalopatias hereditárias e
cardiomiopatias na criança, anticoagulação e amiloidose no idoso,
cardiotoxicidade por anti-HER2 e doença pericárdica em oncologia,
hipertensão crônica e valvopatias na gravidez. Nenhum slug novo foi criado
em nenhuma coleção; nenhum contador global mudou (doenças: 92 antes e
depois).

## Conteúdo

- `canalopatias-pediatricas`
- `cardiomiopatias-pediatricas`
- `anticoagulacao-idoso`
- `amiloidose-cardiaca-idoso`
- `cardiotoxicidade-anti-her2`
- `doenca-pericardica-oncologia`
- `hipertensao-cronica-gravidez`
- `valvopatias-na-gravidez`

Cada ficha ganhou, quando sustentado por fonte primária: epidemiologia sem
extrapolação internacional→nacional não marcada como tal; apresentação
típica e atípica; abordagem diagnóstica estruturada; diferenciais; exames
com finalidade e limitação explícitas; red flags; fluxo ambulatorial e de
emergência; princípios terapêuticos completos (dose só quando a bula/estudo
foi aberto nesta sessão, com nota explícita quando não confirmável);
monitorização; populações especiais; e um assistente determinístico seguro
(3–5 perguntas, 4–6 regras, sempre com pelo menos uma regra de prioridade
alta para escalar risco). Nenhum campo usa o nome de um escore clínico
proprietário (`mWHO`, `HFA-ICOS`) dentro de `assistant_questions`/
`assistant_rules` — restrição explícita já protegida por teste do
repositório, ampliada aqui para as oito fichas novas.

Todos os oito registros mudaram de `revisado` (aprovação humana do resumo
básico de 04/08/2026) para `pendente_revisao`, com `fonte_producao: claude`
e `review_note` explicando exatamente que campos foram adicionados e por
quê a revisão anterior não cobre o conteúdo novo.

## Fontes (todas lidas na íntegra nesta sessão, não apenas abstract)

- **Canalopatias pediátricas**: GeneReviews QT longo (NBK1129), CPVT
  (NBK1289) e Brugada (NBK1517); consenso pediátrico holandês de Brugada
  (Peltenburg 2023, PMID 36223066); consenso HRS/EHRA/APHRS/LAHRS de teste
  genético (Wilde 2022, PMID 35373836); consenso de teste farmacológico
  provocativo (Behr/Veltmann 2025, PMID 40165484); J-Wave syndromes
  consensus (Antzelevitch 2016/2017, PMID 27423412). ESC 2022 de arritmias
  ventriculares (PMID 36017572) citada só por estrutura — texto das tabelas
  de classe/nível bloqueado nesta sessão, não usado para número.
- **Cardiomiopatias pediátricas**: AHA Scientific Statements (Lipshultz
  2019 PMID 31132865; Bogle 2023 PMID 37288568); ESC 2023 Cardiomyopathy
  Guidelines (PMID 37622657); Pediatric Cardiomyopathy Registry (Lipshultz
  2003 PMID 12711739; Webber 2012 PMID 22843787; Jefferies 2015 PMID
  26164213); registro europeu EORP (Kaski 2024 PMID 38427064); ensaios
  originais (Shaddy carvedilol 2007 PMID 17848651; PANORAMA-HF 2024 PMID
  39319469; SCOUT-HCM mavacamten 2026 PMID 41910394; HOPE-3 deramiocel 2026
  PMID 42526472).
- **Anticoagulação no idoso**: ESC 2024 FA (PMID 39210723); EHRA 2021
  Practical Guide (PMID 33895845); ACC 2026 Scientific Statement on DOACs
  (DOI 10.1016/j.jacc.2026.05.033 — título/DOI corrigidos frente à citação
  incompleta da ficha original); ELDERCARE-AF (PMID 32865374); ARISTOTLE
  (PMID 21870978); Man-Son-Hing 1999 (PMID 10218746) e Grymonprez 2023
  (PMID 37252193) sobre queda e anticoagulação; STOPP/START v3 (PMID
  37256475); Beers 2023 (PMID 37139824); ESC/EACTS 2025 valvopatias (PMID
  40878295); bulas DailyMed de apixabana, dabigatrana, rivaroxabana.
- **Amiloidose cardíaca no idoso**: ACC ECDP 2023 (PMID 36697326 — título
  corrigido, faltava "Comprehensive Multidisciplinary Care for the Patient
  With"); ESC 2023 Cardiomyopathy (PMID 37622657); posicionamento ESC 2021
  (PMID 33825853); Gillmore 2016 não-biópsia (PMID 27143678); ATTR-ACT
  (PMID 30145929) e extensão de longo prazo (PMID 34923848); Ruberg & Berk
  2012 (PMID 22949539); Mohammed 2014 (PMID 24720917); rótulo FDA
  VYNDAQEL/VYNDAMAX aberto nesta sessão via DailyMed/labeling.pfizer.com.
- **Cardiotoxicidade anti-HER2**: ESC 2022 Cardio-Oncology (PMID 36017568);
  Slamon 2001 (PMID 11248153); Romond 2005 (PMID 16236738); Chavez-MacGregor
  2013/2015 (PMID 24127446/25964256); SAFE-HEaRt (PMID 30852761 + extensão);
  MANTICORE 101 (PMID 27893331); DESTINY-Breast03/04 (PMID 35320644/35665782);
  rótulos FDA DailyMed de trastuzumabe, pertuzumabe e trastuzumabe-deruxtecana.
- **Doença pericárdica em oncologia**: ESC 2022 Cardio-Oncology (PMID
  36017568), seções 6.10.1/6.10.2 e Tabelas 38/45; ESC 2015 doença
  pericárdica (PMID 26320112), princípios gerais referenciados pela de 2022.
- **Hipertensão crônica na gravidez**: ESC 2025 CVD e gravidez (PMID
  40878294), Tabela 14, Figuras 12A-C, Recommendation Table 13; ESC 2024
  hipertensão (PMID 39210715), seção 9.2; CHAP (PMID 35363951); rótulo FDA
  labetalol via DailyMed; bulas ADALAT/ALDOMET já verificadas no acervo.
- **Valvopatias na gravidez**: ESC 2025 CVD e gravidez (PMID 40878294);
  ESC/EACTS 2025 valvopatias (PMID 40878295); ESC 2018 gravidez (PMID
  30165544, usada só onde a 2025 geral reafirma sem contradição); ROPAC III
  (PMID 40237423); Lau 2025 (PMID 41048030). Texto integral da ESC 2025
  bloqueado por paywall nesta sessão para os dois documentos de 2025 — todo
  número específico usado já havia sido conferido linha a linha em sessão
  anterior do próprio acervo, registrado nos `evidencias`/documentos citados.

## Relações Tudo com Tudo

### Vínculo clínico direto (reaproveitando apenas slugs existentes)

- `doença.related_document_slugs` → documentos `content/**/*.md` já
  publicados, um por mecanismo/mesmo recorte da ficha (nunca genérico
  demais nem redundante com outro já listado).
- `doença.patient_material_slug` → no máximo um material ao paciente por
  ficha, o mais direto — quando nenhum candidato era genuinamente
  específico (hipertensão crônica na gravidez), o campo foi deixado vazio e
  a lacuna, declarada, não preenchida por aproximação.

### Proximidade temática registrada como NÃO relação (não promovida)

- **Anticoagulação no idoso**: escore HAS-BLED, calculadora de fragilidade
  de Rockwood e as páginas de referência dos próprios anticoagulantes
  (apixabana, dabigatrana, rivaroxabana, edoxabana, varfarina) foram
  descartados de `related_document_slugs` — são calculadora/medicamento,
  fora do campo que só resolve contra documento narrativo, e a regra do
  lote veda vínculo com medicamento/calculadora mesmo quando o slug existe
  como página de conteúdo.
- **Amiloidose cardíaca no idoso**: documento de amiloidose AL (cadeia
  leve, cardio-oncologia) e calculadora AL-ISS citados só como diferencial
  em prosa, não como vínculo direto — são doença e ferramenta hematológica
  distintas, não a ATTR do idoso.
- **Cardiotoxicidade anti-HER2**: documento genérico de prevenção/manejo de
  toxicidade cardiovascular relacionada ao câncer (cobre todas as classes)
  não promovido — genérico demais para vínculo direto de uma ficha
  específica de anti-HER2.
- **Doença pericárdica em oncologia**: fluxogramas-espelho dos três
  protocolos já linkados (tamponamento neoplásico, actínica, ICI) e
  documento técnico de cateter de demora vs. janela pericárdica (fonte
  citada é revisão narrativa, vedada pela regra de fonte) não promovidos.
- **Hipertensão crônica na gravidez**: material de risco cardiovascular
  pós-parto de longo prazo (população/momento diferente — pós-parto, não
  gestação em curso) não usado como `patient_material_slug`; nenhum
  material específico melhor foi encontrado — lacuna declarada.
- **Valvopatias na gravidez**: tabela de alvo de INR por tipo/posição de
  prótese e escore de Wilkins (já em documentos irmãos publicados) não
  duplicados aqui; checklists e trilhas relacionadas listadas como
  candidatas para quem monta trilha, não promovidas nesta ficha.

## Riscos e limitações

- Todos os oito registros continuam `pendente_revisao`; nenhum é publicado
  pela reconciliação enquanto pendente.
- Doses e critérios numéricos vêm só de fonte primária aberta nesta sessão
  (diretriz, bula regulatória DailyMed, estudo original); onde a fonte não
  permitiu confirmar um número, o campo evita o valor em vez de estimá-lo.
- Duas correções de citação identificadas e aplicadas: título/DOI do ACC
  2026 sobre DOACs (estava incompleto na ficha original) e título completo
  do ACC ECDP 2023 de amiloidose (faltava um trecho do subtítulo).
- ESC 2025 (gravidez e valvopatias) ficou atrás de paywall nesta sessão
  para leitura linha a linha nova — os números usados vieram de verificação
  já registrada em sessões anteriores do próprio acervo, não inventados
  agora; sinalizado explicitamente no relatório do agente responsável.
- Revisão clínica humana continua obrigatória, especialmente doses,
  critérios de reversibilidade/interrupção terapêutica e limiares de
  intervenção — nenhuma das oito fichas deve virar `revisado` sem essa
  revisão.

## Gates

- `python scripts/audit_tudo_com_tudo.py`: total_items **9.467** (idêntico
  ao baseline do PR #539 — nenhum item novo, nenhum removido), zero
  referência quebrada.
- `python scripts/content_inventory.py --minimum-records 9467
  --minimum-files 2187 --strict`: `invalid=[]`, `missing=[]`.
- `validate_question_definitions`/`validate_rule_definitions` (motor de
  regras determinístico): OK nas 8 fichas, 39 perguntas e 40 regras no
  total.
- `pytest backend/tests/test_condicoes_profundas_especializadas_lote2.py
  backend/tests/test_canonical_content_review_status.py
  backend/tests/test_specialty_guides.py
  backend/tests/test_library_catalog_integrity.py`: novo teste de
  profundidade real (impede regressão a ficha-resumo) + suítes de
  integridade do catálogo, todos verdes, rodados contra Postgres real
  (`alembic upgrade head` no banco de teste).
- `from app.main import app`: importa sem erro.
- Nenhum contador global mudou: `reconcile_content.py`, `library.py` e
  `.github/workflows/corpus-inventory.yml` **não foram tocados** neste
  lote — a instrução explícita foi não alterar contagens do corpus, e como
  nenhum registro novo foi criado, nenhum mínimo precisou mudar.

## Dependência do PR #539

Este lote pressupõe #539 já mesclado (confirmado: `main` está em
`3bb0f206`, que é exatamente o commit de `#539`). Os quatro verbetes
adultos (`geral`) desse lote e o verbete de AVC do #538 não foram tocados —
verificado por teste dedicado
(`test_lote_nao_alterou_os_quatro_verbetes_adultos_do_pr539_nem_o_avc_do_pr538`).

Sem merge, sem deploy.
