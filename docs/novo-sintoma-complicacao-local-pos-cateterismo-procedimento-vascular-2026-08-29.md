# Triagem de sintomas nova — Complicação local pós-cateterismo/procedimento vascular — 29/08/2026

## Contexto

A Triagem de Sintomas (`triagem-sintomas/metadados.json`) não tinha fluxo
próprio para dor, hematoma, sangramento ou sinal de má perfusão de membro
após cateterismo cardíaco ou outro procedimento vascular — apesar de corpus
já existente e verificado sobre o tema em `content/Terapia_intensiva/` e
`content/Dispositivos/`. Este registro é diferente do Guia de Doenças
(`doencas/metadados.json`): é um manifesto e schema próprios, orientado a
perguntas objetivas (`questions`) e regras determinísticas (`rules`) de
triagem, não uma ficha de doença.

Registro novo: slug `complicacao-local-pos-cateterismo-procedimento-vascular`,
adicionado ao **final** do array JSON (ver seção "Risco de colisão" abaixo).

## Fontes lidas por completo e verificadas

1. `content/Terapia_intensiva/oclusao-de-arteria-radial-pos-cateterismo-hemostasia-patente-e-tecnica-de-barbeau.md`
   — oclusão de artéria radial (RAO), hemostasia patente, teste de Barbeau.
2. `content/Terapia_intensiva/acesso-vascular-large-bore-em-tmcs-prevencao-de-sangramento-isquemia-e-fechamento.md`
   — seções 7-11: isquemia de membro, sangramento de acesso, sangramento
   retroperitoneal, dissecção/perfuração/oclusão em acesso femoral large-bore.
3. `content/Dispositivos/marcapasso-temporario-transvenoso-indicacao-acesso-e-complicacoes-na-emergencia.md`
   — comparação jugular vs. femoral (sangramento, infecção), magnitude de
   complicações do acesso vascular central.

Busca ativa adicional (conforme instrução da missão) por
`grep -ril "sangramento retroperitoneal\|hematoma.*cateterismo\|isquemia.*membro.*pos.*procedimento\|complicacao.*acesso.*vascular" content/`
encontrou uma quarta fonte corroborante, sem PMID próprio adicional:

4. `content/Terapia_intensiva/complicacoes-da-bomba-microaxial-hemolise-succao-sangramento-isquemia-e-anticoagulacao.md`
   — seções 7 ("Isquemia de membro") e 8 ("Sangramento retroperitoneal"),
   confirmando de forma independente os sinais de alarme (temperatura/cor,
   enchimento capilar, pulsos/Doppler, dor desproporcional em sedado,
   hipotensão inexplicada, queda de hemoglobina, dor lombar/abdominal,
   necessidade crescente de vasopressor) usados nas regras deste registro.

## Verificação de PMIDs

5 PMIDs centrais, todos já citados em documentos `revisado` deste corpus,
foram reconferidos via NCBI E-utilities (`esummary`) em 29/08/2026,
conferindo título e revista contra o registro oficial do PubMed antes de
persistir no `source_refs`:

- 26811162 — Rashid M et al., Radial Artery Occlusion After Transradial
  Interventions: A Systematic Review and Meta-Analysis. J Am Heart Assoc. 2016.
- 18726956 — Pancholy S et al., PROPHET study. Catheter Cardiovasc Interv. 2008.
- 27712733 — Pancholy SB et al., PROPHET-II Randomized Trial. JACC Cardiovasc
  Interv. 2016.
- 30543806 — Metkus TS et al., Complications and Outcomes of Temporary
  Transvenous Pacing (NIS, >360.000 pacientes). Chest. 2019.
- 42132883 — Pereira RA et al., Complications of Temporary Transvenous
  Cardiac Pacing by Access Site. Pacing Clin Electrophysiol. 2026.

Todos confirmados corretos (título, autores, revista, ano) sem divergência.
As referências SCAI/Naidu/Jolly/Ben-Dor citadas no documento de large-bore
não têm PMID (SCAI é documento de sociedade, sem PMID indexado) e foram
reaproveitadas como já publicadas/verificadas no documento de origem.

## Conteúdo produzido

- **14 perguntas** (`questions`), cobrindo as cinco disciplinas exigidas
  pela missão: sítio de acesso (`access_site`: radial/ulnar vs. femoral vs.
  outro), tempo desde o procedimento (`time_since_procedure`, 4 faixas),
  tipo de sinal (hematoma presente/expansivo/pulsátil, sangramento ativo,
  dor desproporcional, palidez/frieza, parestesia/fraqueza motora, pulso
  distal ausente/reduzido, enchimento capilar lentificado, massa pulsátil),
  uso de anticoagulante/antiagregante, e sinais vitais (hipotensão/
  hipoperfusão, dor lombar/abdominal — combinação que sinaliza sangramento
  retroperitoneal em acesso femoral).
- **12 regras** (`rules`), priority 20-100, cobrindo explicitamente as
  quatro exigidas pela missão:
  - `isquemia-aguda-membro-palidez-frieza-pulso-ausente` (priority 100,
    `emergencia`) — palidez/frieza + pulso distal ausente/reduzido.
  - `isquemia-aguda-deficit-neurologico-com-pulso-ausente` (priority 100,
    `emergencia`) — déficit sensitivo/motor + pulso ausente.
  - `hematoma-expansivo-ou-sangramento-ativo-nao-controlado` (priority 90,
    `urgente`) — hematoma expansivo/pulsátil OU sangramento ativo que não
    cede a compressão.
  - `sangramento-retroperitoneal-suspeito` (priority 100, `emergencia`) —
    acesso femoral + dor lombar/abdominal nova + hipotensão/hipoperfusão.
  - `equimose-leve-estavel-sem-outros-sinais` (priority 20, `rotina`) —
    hematoma presente sem expansão, sangramento ativo, dor desproporcional,
    palidez/frieza ou pulso ausente.
  - Mais 7 regras de suporte: pulso distal ausente isolado, dor
    desproporcional isolada, hipotensão isolada, enchimento capilar
    lentificado, suspeita de pseudoaneurisma (massa pulsátil/sopro), uso de
    anticoagulante/antiagregante (sem indicação de suspensão automática) e
    detecção tardia de possível RAO assintomática em acesso radial (>24h,
    pulso ausente sem palidez).
- `ambulatory_flow` (6 itens) e `emergency_flow` (5 itens), ambos
  não-vazios.
- `default_tests` (6), `differentials` (9), `red_flags` (6 no nível
  superior do registro).
- Nenhuma dose de fármaco em nenhum campo (verificado por regex dedicado no
  teste, além de leitura manual).

## Risco de colisão — outras frentes escrevendo o mesmo arquivo

A missão sinalizou explicitamente que outros agentes podiam estar
adicionando registros ao mesmo `triagem-sintomas/metadados.json` em
branches paralelas simultâneas. Por isso:

- O registro foi adicionado ao **final** do array JSON via script Python
  que carrega, faz `append` e serializa de novo (não edição manual de
  texto), reduzindo risco de erro de sintaxe por edição concorrente.
- Ao rodar o loader (`carregar_triagem_sintomas.carregar`) contra o banco
  de teste compartilhado (`corvia-test-pg`), a primeira tentativa
  encontrou `psycopg.errors.DeadlockDetected` — consistente com outra
  frente escrevendo na mesma tabela ao mesmo tempo. Uma segunda tentativa
  teve sucesso (`{'novos': 19, 'atualizados': 0}`), confirmando que os 19
  registros do manifesto (18 preexistentes + este) validam e persistem
  sem erro de schema.
- Esse é um sinal de **concorrência de infraestrutura de teste**, não de
  conflito de conteúdo — o merge deste PR pode ainda assim colidir em
  `git merge` com outra branch que também tenha feito `append` no mesmo
  arquivo; isso é sinalizado no corpo do PR para revisão humana antes do
  merge.

## Falha esperada e documentada no gate de review_status

`review_status` permanece `"pendente_revisao"` — conteúdo novo não se
autoaprova. Por isso:

- `backend/tests/test_canonical_content_review_status.py::
  test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **FALHA** para `complicacao-local-pos-cateterismo-procedimento-vascular`.
  Isso é esperado e correto, não um bug introduzido por este commit: a
  lógica desse teste consome todo registro com `status == "revisado"` no
  primeiro `continue`, antes de qualquer checagem de allowlist — as
  checagens seguintes contra `PENDENTES_LOTES_TUDO_COM_TUDO` só são
  alcançáveis para registros que **já** estão `"revisado"`, nunca para
  `"pendente_revisao"`.
- Diferente do padrão usado no PR #698 (verbete de doença
  `cardiomiopatia-de-takotsubo`), onde o slug era adicionado à allowlist
  mesmo assim porque ela é **reaproveitada por import direto** em
  `test_disease_fragments_canonical.py`, aqui essa allowlist **não** é
  importada por nenhum outro teste de `triagem-sintomas/metadados.json` —
  não existe um `test_symptom_triage_fragments_canonical.py` equivalente.
  Por isso o slug **não** foi adicionado à allowlist: não teria efeito
  prático e criaria uma entrada morta.
- Resultado observado, confirmado por execução: ver seção "Gates" abaixo.

## Gates executados

- Teste dedicado: 14/14 passou (executado, 33min por contenção de banco compartilhado):
  `backend/tests/test_novo_sintoma_complicacao_local_pos_cateterismo_procedimento_vascular.py`.
- `backend/tests/test_specialty_guides.py` — 11/11 passou: manifesto
  continua com ≥15 registros (agora 19), slugs únicos, `questions`/`rules`/
  `ambulatory_flow`/`emergency_flow`/`source_refs` não-vazios em todos os
  registros, URLs válidas.
- `backend/tests/test_canonical_content_review_status.py` — 2/3 passou,
  1 falha esperada e documentada (ver seção acima):
  `test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  falha citando exatamente
  `triagem-sintomas/metadados.json:complicacao-local-pos-cateterismo-procedimento-vascular:pendente_revisao`;
  `test_manifesto_nao_marca_como_publicado_um_registro_pendente` e
  `test_todos_os_documentos_markdown_estao_revisados` passaram.
- `import app.main` sem erro.
- Loader `carregar_triagem_sintomas.carregar()` contra
  `postgresql+psycopg://meucardio_test:test@localhost:5432/meucardio_test`
  (container `corvia-test-pg`) — `{'novos': 19, 'atualizados': 0}` na
  segunda tentativa (primeira teve deadlock por concorrência com outra
  frente, não relacionado ao conteúdo deste registro).

## Não incluído neste PR

Merge e deploy — aguardando revisão humana.
