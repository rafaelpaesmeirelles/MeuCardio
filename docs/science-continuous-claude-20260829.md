# Produção científica contínua — Claude (29/08/2026 em diante)

Branch: `claude/science-continuous-prevalence-gaps-20260829`
Base: `origin/main` @ `36a642e398a36051ea6ecd3ba18d9481e0a61d85`

## Auditoria quantitativa inicial (base main)

| Coleção | Registros |
|---|---|
| doenças (base + fragmentos) | 150 |
| exames | 410 |
| evidências | 2827 |
| estudos | 1648 |
| medicamentos | 206 |
| checklists | 385 |
| trilhas | 531 |
| material-paciente | 408 |
| emergência | 77 |
| casos clínicos | 854 |
| galeria | 281 |
| triagem-sintomas | 23 |
| documentos markdown (content/) | 1962 |
| calculadoras | 63 |

## Cobertura já existente no território (checagem rápida por grep antes de produzir)

- Valvopatias: estenose/insuficiência aórtica, estenose/insuficiência mitral, insuficiência tricúspide, atresia tricúspide, valva bicúspide pediátrica — **faltam**: estenose tricúspide, valvopatia pulmonar do adulto.
- Congênitas: Fallot (+fetal), TGA (+fetal), CIA, CIV, atresia pulmonar/tricúspide, coarctação (+fetal), PCA, Ebstein, VE hipoplásico (fetal), fisiologia de ventrículo único, canalopatias pediátricas — boa cobertura.
- Arritmias/EP: FA (+idoso), flutter fetal, TSV (+fetal), disfunção do nó sinusal (Codex, 29/08 — recente), BAV (+fetal), canalopatias hereditárias, TV/morte súbita, torsades, QT longo oncológico, PCR/morte súbita abortada.
- Dispositivos: hub `dispositivos-cardiacos-implantaveis` existe.
- Endocardite: `endocardite-infecciosa` e `endocardite-pediatrica` existem.
- Aorta/vascular: hub `doenca-da-aorta`, `doenca-arterial-periferica-de-membros`, `hipertensao-renovascular-e-estenose-de-arteria-renal` (⚠️ já existe — não duplicar tema de renovascular).
- Cardiomiopatias: hipertrófica, dilatada, arritmogênica, Takotsubo, Chagas, periparto, hub pediátrico.

## Lote 1 — auditoria concluída

Achados-chave (agente de auditoria):
- **Cancelado**: dispositivos-cardiacos-implantaveis (colisão ativa PR #599, #711 abertos).
- **Adiado**: fibrilação atrial (Codex trabalhando agora, PR #725 draft hoje).
- `estenose-tricuspide`: doença sem Guia de Doenças, mas HÁ narrativa em content/Valvopatias/estenose-tricuspide-reumatica-diagnostico-e-manejo.md — mantido como aprofundamento/integração (não duplicação), conforme prioridade #5 da missão.
- `valvopatia-pulmonar-do-adulto...`: lacuna real confirmada, sem colisão.
- Top-15 baixa conectividade e top-10 baixa profundidade identificados (ver detalhe no relatório do agente, não replicado aqui).

## Lote 2 (em andamento, 6 agentes simultâneos)

1. `valvopatia-pulmonar-do-adulto-estenose-e-insuficiencia` — verbete novo
2. `estenose-tricuspide` — verbete novo, integrado ao doc narrativo já existente
3. `doenca-de-kawasaki` — aprofundamento (diagnostic_approach vazio, treatment_summary raso) — correção aditiva, review_status volta a pendente_revisao
4. `miocardite-pediatrica` — idem
5. `avaliacao-cardiovascular-pre-concepcional` — Tudo com Tudo (related_document_slugs vazio → 3-7 links)
6. `sarcoidose-cardiaca` — checklist + caso clínico novos (verbete já completo, faltava conectividade a esses tipos)

## Lote 2 — concluído (5 commits, SHA e2d5cd90)

- `valvopatia-pulmonar-do-adulto-estenose-e-insuficiencia` — verbete novo
- `estenose-tricuspide` — verbete novo, integrado ao doc narrativo já existente
- `doenca-de-kawasaki` — aprofundado (diagnostic_approach + treatment_summary)
- `miocardite-pediatrica` — aprofundado (idem)
- `avaliacao-cardiovascular-pre-concepcional` — +1 related_document_slug
- `sarcoidose-cardiaca` — +1 checklist, +1 caso clínico

## Lote 3 (em andamento, 4 agentes)

1. `tronco-arterial-comum` — aprofundamento (diag/treat vazios)
2. `extrassistoles-fetais` — aprofundamento (idem)
3. `tumores-cardiacos-fetais` — aprofundamento (idem)
4. `defeito-septo-atrioventricular` — Tudo com Tudo (related=1 → mais links)

## Lote 3 — concluído (4 commits, SHA cc0fa412)

- `defeito-septo-atrioventricular` — +2 related_document_slugs
- `extrassistoles-fetais` — aprofundado (diag/treat)
- `tronco-arterial-comum` — aprofundado (diag/treat, Van Praagh, 22q11.2)
- `tumores-cardiacos-fetais` — aprofundado (rabdomioma/teratoma/fibroma)

## Lote 4 (em andamento, 4 agentes)

1. `hipertensao-gestacional` — aprofundamento (diag vazio, treat raso)
2. Cardiologia do Esporte — scouting + verbete novo (tema a definir pelo agente, evitando overlap com science-overnight)
3. Endocardite — auditoria de profundidade + aprofundamento ou subtema novo
4. Imagem cardiovascular — scouting + exame novo

## Lote 4 — concluído (4 commits, SHA cce611ec)

- `hipertensao-gestacional` — aprofundado (CHIPS vs. CHAP, HYPITAT, risco pós-parto)
- `endocardite-de-protese-valvar` — verbete novo (desbloqueia 11 evidências SBC 2019)
- `valvopatia-elegibilidade-esportiva-atleta` — verbete novo (maior bloco pendente do tema esporte, 29/54)
- exame `ecocardiograma-com-contraste...` — novo

Nota: main drift confirmado sem conflito (mudanças em infra/frontend/API de guideline_updates, nenhum arquivo de conteúdo tocado).
Território verificado antes do lote: PR #599 (dispositivos) e #725 (FA/Codex) ainda abertos — continuar evitando. `disfuncao-do-no-sinusal` tocado por Codex HOJE (correção zzzzz-codex-20260829, removeu links órfãos) — evitado.

## Lote 5 (em andamento, 3 agentes)

1. `tronco-arterial-comum` — Tudo com Tudo (rel=1)
2. `extrassistoles-fetais` + `tumores-cardiacos-fetais` — Tudo com Tudo (rel=1 cada)
3. Aorta torácica descendente — scouting + verbete/correção (evitar duplicar HIM/PAU/renovascular/aortopatias-genéticas já feitos na branch science-overnight)

## Lote 5 — concluído (2 commits, SHA 4ce777ea) — total 15 commits na branch

- Tudo com Tudo para trio fetal/pediátrico (tronco arterial comum +4, extrassístoles fetais +5, tumores cardíacos fetais +3)
- `dissecao-aortica-tipo-b` — verbete novo (ADSORB/INSTEAD-XL, tricotomia complicada/alto-risco/sem-alto-risco)

## Resumo cumulativo até aqui (15 commits)
Verbetes novos: valvopatia-pulmonar-do-adulto, estenose-tricuspide, endocardite-de-protese-valvar, valvopatia-elegibilidade-esportiva-atleta, dissecao-aortica-tipo-b (5)
Aprofundamentos: doenca-de-kawasaki, miocardite-pediatrica, tronco-arterial-comum, extrassistoles-fetais, tumores-cardiacos-fetais, hipertensao-gestacional (6)
Tudo-com-Tudo (só links): avaliacao-cardiovascular-pre-concepcional, defeito-septo-atrioventricular, + trio fetal do lote 5 (5 correções)
Novo tipo de conteúdo: checklist+caso para sarcoidose-cardiaca, exame ecocardiograma-com-contraste (3)

## Lote 6 — concluído (2 commits, SHA 66a516d3) — total 18 commits na branch

- `arritmia-atrial-na-circulacao-de-fontan` — verbete novo (complementa fisiologia-ventriculo-unico)
- exame `caracterizacao-de-placa-de-alto-risco-por-angiotomografia-coronariana` — novo

Território já bem coberto, confirmado sem lacuna: métodos gráficos (129 exames), DAP (rel=24), canalopatias, cardiomiopatias principais (mas backlog de evidências ainda alto — ver lote 7).

## Lote 7 — concluído (2 commits, SHA 75940ae8) — total 20 commits na branch

- `cardiomiopatia-restritiva-nao-amiloide` — verbete novo (fibrose endomiocárdica/SHE, sinal do "duplo V"; não sobrepõe amiloidose nem não-compactação/hipertrabeculação ESC 2023)
- `manejo-perioperatorio-de-dispositivo-cardiaco-implantavel` — verbete novo (magneto vs. reprogramação, dependência de estimulação, monopolar/bipolar)

Nota de correção de gate: os related_document_slugs originalmente propostos pelo
agente do item 2 eram 6 slugs de *doença* (dispositivos-cardiacos-implantaveis,
bloqueio-atrioventricular, arritmias-ventriculares-e-morte-subita-cardiaca,
sincope, insuficiencia-cardiaca, parada-cardiorrespiratoria-e-morte-subita-abortada)
— nenhum resolve contra related_document_slugs, que só aceita documento/fluxograma.
audit_tudo_com_tudo.py pegou os 6 broken_references antes do commit. Corrigido
para 5 documentos/fluxogramas reais e clinicamente pertinentes (verificados por
busca em content/), incl. o doc que já cobre manejo perioperatório de CIED
(fonte AHA compartilhada) e o análogo de EMI em radioterapia oncológica.
Gates re-executados limpos (broken_references: [], content_inventory --strict OK)
antes do commit final.

## Lote 8 (em andamento, 4 agentes despachados, 3 já integrados) — total 24 commits na branch

- `esclerose-sistemica-com-acometimento-cardiaco` — verbete novo (SHA 2e31a566). Escopo restrito a miocárdio/pericárdio/condução; HP-ESc e crise renal ficam de fora (diferenciais, linkados aos 2 docs DETECT já existentes). 12 PMIDs (EUSTAR consensus/coorte, RM T1 mapping, disfunção microvascular, arritmia/condução, tamponamento). Correção: 2 perguntas com options em string simples → formato {value,label}.
- checklist `ecocardiograma-seriado-no-tratamento-da-endocardite-infecciosa-quando-repetir` — 14 itens (SHA 750c12e4). Fonte: Posicionamento SBC 2019 de ecocardiografia em adultos (Tabelas 29/31, seção 3.4), classes/níveis transcritos literalmente do full-text PMC. documento_origem=null (nenhum match direto real).
- `cardiomiopatia-por-sobrecarga-de-ferro` — verbete novo (SHA 2e9d3020). Hemocromatose (flebotomia) vs. sobrecarga transfusional/talassemia (quelação, sem posologia por falta de fonte). Eixo: RM T2* (cortes 20/10ms, RR de IC=160 e RR arritmia=4,6, Kirk 2009). 10 PMIDs, incl. confirmação por full-text de que o posicionamento SBC 2026 tem seção dedicada. Correções: entidades HTML → caracteres reais, options de pergunta → {value,label}, 4 related_document_slugs reais preenchidos.
- `fenocopias-glicogenicas-da-cardiomiopatia-hipertrofica-danon-e-prkag2` — verbete novo (SHA c8dc5c27). Danon (LAMP2) vs. PRKAG2, pré-excitação ventricular como pista compartilhada, Fabry tratada só como diferencial (ficha própria já existe). 8 PMIDs. 5 related_document_slugs reais.

Todos os 3 já integrados passaram pelos 3 gates (field/enum/question/rule,
audit_tudo_com_tudo broken_references:[], content_inventory --strict) limpos
antes do commit. Nenhum arquivo perdido no checkout compartilhado.

Candidato descartado por já ter host: `cmh-avaliacao-perioperatoria-eco-biomarcadores-e-betabloqueador`
(evidência pendente) — já existe `content/Perioperatório/cmh-lvoto-cirurgia-nao-cardiaca-arvore-aha-acc-2024.md`;
é lacuna de conectividade, não de conteúdo novo — candidato para lote de
Tudo-com-Tudo puro, não para verbete novo.

Pendência não acionada: possível quase-duplicata entre
`doenca-renovascular-e-displasia-fibromuscular` (branch science-overnight) e
`hipertensao-renovascular-e-estenose-de-arteria-renal` (já em main) — a
reconciliar quando as branches forem revisadas/mescladas.

## Lote 9 (em andamento, 2 itens) — total 27 commits na branch

Reaudição confirmou PR #599 (dispositivos) e #725 (FA) ainda abertos — mantido
afastamento. Backlog Valvopatias (77 itens) escaneado: cluster eco-estresse
(~10 itens) já tem exame-host (`ecocardiografia-de-estresse-na-doenca-valvar`,
pré-existente) — descartado como candidato a conteúdo novo, é lacuna de
conectividade, não de conteúdo. Cluster geriátrico (~10 itens: TAVI vs.
cirurgia por idade/risco, HAS na EAo do idoso, estatina não freia progressão,
valvoplastia por balão como ponte) mapeado a uma lacuna real e explícita: o
verbete geral `estenose-aortica` já cita textualmente "ver ficha específica de
estenose aórtica e TAVI no idoso" — ficha que nunca foi criada. Despachada.

- exame `teste-ergometrico-na-estenose-aortica-pediatrica-e-na-valva-aortica-bicuspide`
  — novo (SHA 6d7a5468). Complementar ao Bruce modificado pediátrico genérico
  já existente. 9 PMIDs (Task Forces AHA/ACC de elegibilidade esportiva,
  EAPC/ESC/AEPC, TCPE em CHD). Sem corte numérico único validado — declarado.
- `estenose-aortica-no-idoso-fragilidade-tavi-e-futilidade` — verbete novo
  (SHA 6fc9965a), area=cardiogeriatria. 14 PMIDs (FRAILTY-AVR, futilidade,
  SEAS/ASTRONOMER estatina, BAV ponte/paliação). Correção: 7 assistant_rules
  referenciavam ids de pergunta inexistentes — remapeados; 2 perguntas novas
  adicionadas; 4 related_document_slugs reais preenchidos.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 10 (em andamento, 1 agente) — lote 9 fechado, total 28 commits

Lote 9 fechado — 2/2 integrados (exame ergométrico EAo pediátrica + verbete
geriátrico de EAo/TAVI/futilidade). Cluster restante do backlog de
Valvopatias mapeado: angiotomografia com 4 papéis expandidos no TAVI
(coronária pré-TAVI, valve-in-valve, escore de cálcio para dirimir gravidade
discordante ao eco, trombose de folheto pós-TAVI) — complementar ao exame
básico de planejamento (anel/vias de acesso) já existente. Despachado
(agente a9fce3dda4bfdf359).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_
## Lote 10 — concluído (1 commit, SHA 36bbab23) — total 29 commits

- exame `angiotomografia-coronariana-e-cardiaca-em-papeis-expandidos-no-tavi...`
  — novo, complementar ao exame básico de planejamento pré-TAVI. 4 cenários
  (coronária pré-TAVI, valve-in-valve/VTC, escore de cálcio na discordância
  eco, trombose de folheto/HALT — controvérsia GALILEO vs. GALILEO-4D
  preservada). 15 PMIDs. Correção: indications/interpretation/limitations
  vieram como lista no rascunho — LabTest usa Text, não ARRAY; convertidas
  para string antes de gravar.

Aprendizado do lote: boa parte do restante do backlog de Valvopatias
(comissurotomia mitral, DOAC vs. AVK em valvopatia não-mitral, cirurgia de
tricúspide combinada) já tem host real (verbetes/documentos existentes) —
são lacunas de CONECTIVIDADE, não de conteúdo novo. Não acionado nesta
rodada (fora do padrão de produção deste agente, que gera conteúdo).

## Lote 11 (em andamento, 1 agente)

Backlog de Cardiologia pediátrica (61 itens) escaneado: cluster JCS 2020
Kawasaki (6 itens) sobre farmacoterapia de longo prazo estratificada por
tamanho de aneurisma coronariano (AAS dose baixa vs. dupla antiagregação vs.
varfarina+AAS em aneurisma grande, estatina, IECA/BRA) — confirmado como
lacuna real no aprofundamento já feito no lote 2 (que cobriu só AHA 2017,
sem a estratificação JCS 2020 por tamanho). Despachada correção aditiva
(agente ad3fdc574c880d8da).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 11 — concluído (1 commit, SHA 9311ef5d) — total 30 commits

- correção `doenca-de-kawasaki` — farmacoterapia de longo prazo por tamanho
  de aneurisma (JCS/JSCS 2020, PMID 32641591): AAS dose baixa em aneurisma
  persistente, dupla antiagregação em médio/grande, varfarina+AAS em
  gigante, estatina e IECA/BRA (evidência preliminar, declarado). Arquivo
  zzzzzzz-jcs2020- ordenado corretamente após a correção anterior;
  review_status confirmado pendente_revisao via load_disease_records().

## Lote 12 (em andamento, 1 agente)

Backlog pediátrico: cluster erg-ped/ergped2024 restante (QT longo, Brugada,
BAVT congênito) — CPVT já tem 2 exames-host, não incluído. Despachado exame
complementar (agente a25dd7a5b2c95d2e9).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 12 — concluído (1 commit, SHA 94a57a1f) — total 32 commits

- exame `teste-ergometrico-na-sindrome-do-qt-longo-sindrome-de-brugada-e-no-bavt-congenito-pediatrico`
  — novo, complementar ao exame já existente de CPVT. 3 cenários (QTc de
  recuperação em SQTL/LQT1, desmascaramento limitado de Brugada, capacidade
  funcional/incompetência cronotrópica em BAVT congênito para decisão de
  marca-passo). 11 PMIDs. Sem corte numérico de consenso em nenhum dos 3 —
  declarado.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 13 (em andamento, 1 agente)

Cluster "eco-*" do backlog pediátrico (~16-19 itens): indicações de
ecocardiograma pediátrico por cenário clínico (RN cianótico/choque, RN
assimetria de pulsos, RN suspeita PCA, palpitação+HF arritmia/morte súbita,
HAS, síncope de esforço, endocardite, Kawasaki fase aguda/seguimento/
eco-estresse tardio, cardio-oncologia, pós-transplante+eco-estresse
vasculopatia tardia, ETE por janela ruim, ETE em UTI pós-operatória, ECMO).
Exame técnico existente (`ecocardiograma-transtoracico-pediatrico-com-escore-z`)
cobre só medição por escore Z, não indicações — confirmado gap real.
Despachado como checklist (agente a192914cbfd4ed3f2).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 13 — concluído (1 commit, SHA 209db3e7) — total 34 commits

- checklist `indicacoes-de-ecocardiograma-em-cardiologia-pediatrica-cenarios-clinicos-especificos`
  — 20 itens, 9 categorias, maior impacto de backlog em um único lote desta
  fase (~19-20 itens evidencias/metadados.json potencialmente desbloqueados).
  11 fontes verificadas (AHA Kawasaki/endocardite/oximetria, ASE TEE/
  quantificação pediátrica, HRS/EHRA/APHRS, AAP hipertensão, IGHG
  cardio-oncologia, ISHLT transplante, ELSO ECMO). Nenhuma diretriz SBC
  específica localizada — declarado.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 14 (em andamento, 1 agente) — maior cluster identificado nesta fase

Backlog pediátrico: cluster "paces2021-*" (21 itens!) — indicações de CDI/
marca-passo/monitor implantável em pediatria (BAVT congênito, CPVT, QT
longo, Brugada, CMH, cardiomiopatia arritmogênica, Chagas pediátrico, DNS,
síncope, RM em portador de dispositivo). Complementar ao hub geral de
dispositivos (adulto, ainda sob PR #599 — não mexido), sem host pediátrico
específico no corpus. Despachado como checklist com as 21 classes de
recomendação (agente a3eeb9f8e1df81fae).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 14 — concluído (1 commit, SHA 71cb516e) — total 36 commits

- checklist `indicacoes-de-dispositivo-cardiaco-eletronico-implantavel-em-pediatria-paces-2021`
  — 21 itens, maior cluster desbloqueado nesta fase. Todas as classes de
  recomendação (I/IIa/IIb/III) extraídas literalmente da diretriz PACES
  2021 (PMID 34363988), incl. nota explícita de que um padrão de risco
  recebe classes diferentes conforme a cardiomiopatia (não inventada uma
  tabela consolidada inexistente).

## Resumo cumulativo desta janela (lotes 7-14, 22 commits, ~19 itens de conteúdo novo/aprofundado)

Verbetes novos: cardiomiopatia-restritiva-nao-amiloide, manejo-perioperatorio-cied,
esclerose-sistemica-cardiaca, cardiomiopatia-por-sobrecarga-de-ferro,
fenocopias-glicogenicas-danon-prkag2, estenose-aortica-no-idoso-fragilidade-tavi (6)
Exames novos: teste-ergometrico-ea-pediatrica-vab, angiotomografia-tavi-expandida,
teste-ergometrico-canalopatias-bavt-pediatrico (3)
Checklists novos: eco-endocardite-seriado, indicacoes-eco-pediatrico (20 itens),
paces2021-dispositivos-pediatricos (21 itens) (3)
Correções: kawasaki JCS 2020 farmacoterapia por tamanho de aneurisma (1)
Território: Cardiomiopatias, Perioperatório/Dispositivos, Valvopatias/Cardiogeriatria,
Cardiologia pediátrica — todos dentro do território designado do Claude.
Nenhuma colisão: PR #599 e #725 seguem abertos e evitados em todas as rodadas
(reconferidos a cada lote via git fetch + gh pr view).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 15 (em andamento, 1 agente)

`aortopatias-geneticas-do-adulto` já existe (branch science-overnight,
confirmado via git log --all — Marfan/Loeys-Dietz/bicúspide, limiares em
mm de adulto). Gap real: verbete PEDIÁTRICO complementar — escore Z (não
mm absoluto) para vigilância seriada de raiz aórtica em criança, limiares
cirúrgicos pediátricos, técnica valve-sparing conforme crescimento
residual, diferenciação de agressividade entre Marfan/Loeys-Dietz/EDS
vascular em criança. Documento narrativo já existente no corpus usado
como contexto, verbete estruturado ainda não existia. Despachado (agente
a9fd2a92b9f72117f).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 15 — concluído (1 commit, SHA faba1d15) — total 38 commits

- `aortopatia-genetica-pediatrica-marfan-loeys-dietz-e-ehlers-danlos-vascular-vigilancia-e-limiares-cirurgicos`
  — verbete novo, area=cardiopediatria. Escore Z vs. diâmetro absoluto,
  técnica valve-sparing com crescimento residual, diferenciação de
  agressividade entre as 3 síndromes, restrição esportiva. 14 PMIDs.
  Complementar (não duplicado) ao verbete de adulto da outra branch.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 16 (em andamento, 1 agente) — retorno ao território primário (Arritmias)

Backlog de Arritmias (42 itens) escaneado: cluster "jcs-2022" muito grande
(~32 itens da diretriz JCS/JHRS 2022 de manejo não farmacológico de
arritmias) — dividido em sub-lotes. Primeiro sub-lote despachado: seleção
de método diagnóstico/monitorização (ECG, Holter, gravadores de eventos,
smartphone/smartwatch, IA, monitor implantável/looper, mapeamento
eletroanatômico) — 16 itens (agente ae582afc63f5011a8). CDI prevenção
primária/secundária (2 itens) já tem host (fluxogramas CDI ESC 2022 já
existentes) — não acionado. Restante do cluster JCS 2022 (risco pós-IAM,
teste genético em canalopatias, restrição de exercício por condição) fica
para próximos lotes.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 16 — concluído (1 commit, SHA f158b807) — total 40 commits

- checklist `selecao-do-metodo-diagnostico-e-monitorizacao-de-arritmia-jcs-2022`
  — 16 itens. Rigor exemplar: agente identificou que a diretriz correta é
  o documento-base JCS/JHRS 2019 (PMID 34386109), não a atualização focada
  2021/2022 popularmente chamada "JCS 2022"; declarou explicitamente que 4
  itens do briefing (HRV/turbulência, câmera smartphone, smartwatch, IA
  para FA) NÃO constam na diretriz pesquisada, em vez de inventar — mantidos
  como lacunas assinaladas. ICM: 4 indicações com COR/LOE exatos da
  Tabela 44.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 17 (em andamento, 1 agente) — sub-lote 2/3 do cluster JCS 2019/2021

Segundo sub-lote: teste genético em canalopatias (LQTS, CPVT, Brugada +
cascata familiar) e estratificação de risco pós-IAM/cardiomiopatia
(FEVE, TVNS, EPS+TVNS, índices de despolarização/repolarização) +
restrição/liberação de exercício (pós-CDI, FA, CPVT, CAVD, LQT1, resposta
pressórica na CMH, teste ergométrico em CPVT/QTL) — 16 itens. Mesmo padrão
de rigor do lote 16 (declarar explicitamente quando recomendação formal
não for confirmada). Despachado (agente a8c914f2ae48e97d2).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 17 — concluído (1 commit, SHA b1f2043f) — total 42 commits

- checklist `teste-genetico-em-canalopatias-e-risco-pos-iam-e-restricao-de-exercicio-em-arritmia-jcs`
  — 16 itens, sub-lote 2/3 do cluster JCS/JHRS 2019. 8/16 itens declarados
  explicitamente como não confirmados na diretriz (incl. correção de uma
  hipótese do meu próprio briefing sobre testes ergométricos em CPVT/QTL).

## Varredura final de encerramento do ciclo ativo desta janela

Verificado antes de continuar: AVNRT (2 itens restantes do cluster
Arritmias) e LQTS betabloqueador/mexiletina já têm host narrativo completo
(`taquicardia-por-reentrada-nodal-avnrt-ablacao-versus-farmacos...`,
`canalopatias-sindrome-do-qt-longo-e-sindrome-de-brugada-diagnostico-e-manejo`)
— lacuna de conectividade, não de conteúdo. Cluster `aortopatia-gestante-*`
(7 itens, cortes de diâmetro para via de parto) já coberto por
`sindrome-de-marfan-na-gestacao-risco-de-dissecao-aortica-e-limiares-de-manejo-pelo-diametro`
(confirmado: menciona cesárea, parto vaginal E os cortes de 4cm/40mm
citados no backlog). Cluster `gravidez-esc-2018-*` (~30 itens): mWHO 2.0
já coberto por `classificacao-de-risco-mwho-2-0-na-gravidez-esc-2025` —
versão MAIS RECENTE (ESC 2025) já presente no corpus; produzir conteúdo
novo citando a diretriz 2018 desatualizada quando o corpus já tem a
atualização de 2025 seria contraproducente.

**Conclusão desta rodada**: os clusters de maior valor marginal genuíno
(cardiomiopatias, dispositivos periop/pediátricos, valvopatias geriátricas,
aortopatia pediátrica, arritmias/canalopatias JCS) foram identificados e
produzidos. Os clusters remanescentes auditados nesta última varredura são,
de forma consistente, lacunas de CONECTIVIDADE (Tudo-com-Tudo) sobre
conteúdo já existente, não lacunas de conteúdo novo — produzir verbete/
checklist novo ali duplicaria material já presente. Registrado aqui como
sinal para a próxima rodada: um lote de Tudo-com-Tudo puro (sem produção de
conteúdo novo, só related_document_slugs) nesses clusters teria alto valor.

## Resumo cumulativo final desta janela (lotes 7-17, 35 commits)
Verbetes novos (8): cardiomiopatia-restritiva-nao-amiloide, manejo-perioperatorio-cied,
esclerose-sistemica-cardiaca, cardiomiopatia-por-sobrecarga-de-ferro,
fenocopias-glicogenicas-danon-prkag2, estenose-aortica-idoso-fragilidade-tavi,
aortopatia-genetica-pediatrica-marfan-loeys-dietz-eds-vascular
Exames novos (3): teste-ergometrico-ea-pediatrica-vab, angiotomografia-tavi-expandida,
teste-ergometrico-canalopatias-bavt-pediatrico
Checklists novos (5): eco-endocardite-seriado, indicacoes-eco-pediatrico (20 itens),
paces2021-dispositivos-pediatricos (21 itens), selecao-metodo-diagnostico-arritmia-jcs (16 itens),
teste-genetico-canalopatias-exercicio-jcs (16 itens)
Correções (1): kawasaki JCS 2020 farmacoterapia por tamanho de aneurisma
Território: Cardiomiopatias, Dispositivos/Perioperatório, Valvopatias/Cardiogeriatria,
Cardiologia pediátrica, Arritmias/Canalopatias — todos no território designado.
Colisões evitadas em todas as rodadas: PR #599, #725 (reconferidos a cada lote).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 18 (em andamento, 1 agente)

Backlog Cardiologia geriátrica (69 itens) escaneado: cluster "sbc2019-*"
(~17 itens da I Diretriz Brasileira de Cardiogeriatria, SBC/Arq Bras
Cardiol 2019) — fonte brasileira prioritária conforme hierarquia da missão,
sem host no corpus. Primeiro sub-lote despachado: prevenção/estilo de vida
(exercício, tabagismo/método 4As), valvopatia (regurgitação aórtica),
arritmia/monitorização (ETE pré-cardioversão, ECG/Holter — incl. uso
apropriado vs. inadequado), estatina (não freia progressão de EAo vs.
PROSPER reduz eventos), meta pressórica <120mmHg em DAC crônica — 13 itens
(agente a6d3b07ccc21502d0).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 18 — concluído (1 commit, SHA 91935ab4) — total 44 commits

- checklist `diretriz-brasileira-de-cardiogeriatria-sbc-2019-avaliacao-e-manejo-cardiovascular-no-idoso`
  — 13 itens, fonte SBC. Achados de rigor: diretriz é na verdade a 3ª
  edição da série (não "I Diretriz"); meta de PAS <120mmHg do backlog NÃO
  é posição própria da diretriz (é só descrição do braço SPRINT) — meta
  real é ≤130mmHg/<140mmHg, divergência documentada explicitamente.

Verificado antes do próximo lote: cluster `aas/prasugrel/DAPT idoso pós-SCA`
já tem host (`terapia-antiplaquetaria-dupla-no-muito-idoso...`, 8 menções
a prasugrel/AAS) — conectividade, não conteúdo novo, não acionado.

## Lote 19 (em andamento, 1 agente) — território Aorta/vascular

Backlog "Aorta e doença arterial periférica" (72 itens): cluster
`carotidas-*` (15 itens, critérios de Doppler de carótidas — VPS,
avaliação multiparamétrica, definição de placa/oclusão, armadilhas de
suboclusão, extensão do exame, complementação por angio-TC/RM) confirmado
sem host (só existe item separado de CIMT, tema distinto). Despachado
como checklist (agente a98c4566a2775830d).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 19 — concluído (1 commit, SHA 7f4af4fa) — total 45 commits

- checklist `criterios-diagnosticos-do-doppler-de-carotidas-avaliacao-multiparametrica-da-estenose`
  — 13 itens. Fonte primária SRU 2003 (PMID 14500855). Rigor exemplar:
  agente declarou explicitamente quando não conseguiu confirmar um valor
  numérico (razão ACI/ACC) ou fonte primária de um sinal de propedêutica
  consolidada, em vez de inventar. Marcadores DTC: microembolização com
  evidência prospectiva robusta (ACES) vs. reserva vasomotora sem
  significância no mesmo estudo — diferença de robustez preservada.

## Lote 20 (em andamento, 1 agente) — correção pequena, fecha o sub-tema ITB SBC 2024

Cluster `itb-pos-esforco-*` SBC 2024 (3 itens): confirmado que o exame
já existente `itb-pos-exercicio-em-esteira-na-claudicacao-intermitente`
não cobre os 3 cenários específicos (ITB repouso normal com sintomas, ITB
alterado em diabético assintomático, TcPO2 complementar). Despachada
correção aditiva (agente ac51429cd14737ef9).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 20 — concluído (1 commit, SHA f2bdf4fe) — total 46 commits

- correção `itb-pos-exercicio-em-esteira-na-claudicacao-intermitente` — 3
  cenários SBC 2024/SBACV (Erzinger et al., PMID 39493832): sintomático com
  ITB repouso normal, diabético assintomático com ITB alterado por
  calcificação, TcPO2 complementar (WIfI ≥60/​<30mmHg). review_status
  revertido de revisado para pendente_revisao; source_refs 2→5.

## Lote 21 (em andamento, 1 agente)

Backlog Aorta: cluster de limiares cirúrgicos de aneurisma por etiologia
(8 itens: ascendente esporádico 5,5cm, Marfan 5,0cm, Loeys-Dietz por gene,
bicúspide isolado vs. com troca valvar concomitante 4,5cm, aorta
descendente, AAA por sexo) — confirmado sem host (doc geral PAAD ESC 2024
existente não detalha por etiologia, 0 menções aos limiares numéricos).
Despachado (agente a60b82fe6e884144e).

## Panorama consolidado desta janela estendida (lotes 7-21, ~46 commits)
21 lotes completados nesta sessão contínua. Território coberto: Cardiomiopatias
(restritiva, sobrecarga de ferro, fenocópias glicogênicas, esclerose sistêmica),
Dispositivos (periop CIED, PACES 2021 pediátrico), Valvopatias (estenose
aórtica geriátrica/TAVI/futilidade), Cardiologia pediátrica (eco indicações,
teste ergométrico QTL/Brugada/BAVT, Kawasaki JCS 2020, aortopatia genética
pediátrica), Arritmias (seleção diagnóstica JCS 2019, teste genético/exercício
JCS 2019), Cardiologia geriátrica (SBC 2019 cardiogeriatria), Aorta/vascular
(TAVI angiotomografia expandida, Doppler de carótidas SRU 2003, ITB SBC 2024).
Padrão de rigor consistente: múltiplos agentes corrigiram premissas do próprio
briefing do orquestrador ao não encontrar confirmação na fonte primária, e
declararam isso explicitamente em vez de inventar — sinal de que o processo de
verificação está funcionando como pretendido.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 21 — concluído (1 commit, SHA 16cebe8d) — total 47 commits

- checklist `limiares-cirurgicos-de-aneurisma-de-aorta-por-etiologia-marfan-loeys-dietz-bicuspide-esporadico`
  — 8 itens, fonte ACC/AHA 2022 (PMID 36322642) verificada por texto
  integral. Declaração explícita de ausência de corte único por gene em
  Loeys-Dietz; contraponto de debate em andamento sobre limiar por sexo em
  AAA (Talvitie 2024, PMID 37963191) preservado, não omitido.

## Lote 22 (em andamento, 1 agente)

Item pequeno e focado: vigilância de TODA a aorta (não só segmento
sintomático) e timing de intervenção eletiva apenas em remissão na
aortite inflamatória (Takayasu/arterite de células gigantes) — documento
narrativo já existente no corpus não cobre esses 2 pontos práticos.
Despachado como exame (agente a889586a272ee92f8).

## Checkpoint final desta janela estendida (lotes 7-22, 47+ commits)

22 lotes completados nesta sessão de produção contínua. Cobertura por
território (todos dentro do escopo designado do Claude): Cardiomiopatias
(4 verbetes novos), Dispositivos/Perioperatório (2), Valvopatias/
Cardiogeriatria (2), Cardiologia pediátrica (5: eco indicações, teste
ergométrico, Kawasaki, PACES 2021, aortopatia genética), Arritmias (2
checklists JCS 2019, ~32 itens), Cardiologia geriátrica (1, SBC 2019),
Aorta/vascular (4: TAVI angiotomografia, Doppler carótidas, ITB SBC 2024,
limiares de aneurisma). Total aproximado: 9 verbetes novos, 3 exames
novos, 8 checklists novos (>150 itens de checklist ao todo), 2 correções.

Padrão de qualidade mantido em todas as rodadas: PMIDs verificados via
NCBI e-utils (nunca inventados), declarações explícitas de incerteza
quando a fonte não confirma um valor/recomendação (múltiplas ocorrências
por lote nas rodadas finais), gates de validação (field/enum/question/rule,
Tudo-com-Tudo, content_inventory --strict) limpos antes de cada commit,
zero colisão com PR #599/#725 (reconferidos a cada lote), zero arquivo
perdido no checkout compartilhado. Sinal de encerramento natural: as
últimas varreduras de backlog mostram predominância de lacunas de
CONECTIVIDADE (conteúdo já existente sem link) sobre lacunas de conteúdo
genuinamente novo — registrado como direção para a próxima fase de
trabalho, seja pelo Claude nesta mesma branch ou por outro agente.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 23 (em andamento, despachado em paralelo ao lote 22)

Retorno ao backlog de Endocardite (23 itens): cluster "profilaxia
antibiotica-*" (8 itens) — completamente distinto do checklist de timing
de eco já produzido no lote 8, sem host no corpus. Cobre procedimento
odontológico de alto risco, endocardite prévia, VAD, prótese transcateter,
implante de CIED, baixo risco (não indicado), procedimento não-odontológico
de alto risco (opcional), descolonização sem rastreio (não indicado).
Despachado (agente a2d4aaf7d8a7de498).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 22 — concluído (1 commit, SHA 84129a44) — total 48 commits

- exame `vigilancia-por-imagem-de-toda-a-aorta-e-timing-de-intervencao-na-aortite-inflamatoria-em-remissao`
  — novo, complementar ao documento narrativo de Takayasu/ACG. 7 PMIDs
  verificados (Espitia 2021 PMID 33413605, ACR/VF 2021 PMID 34235884,
  Zheng 2019 PMID 29313449). Declarado explicitamente: a própria diretriz
  reconhece ausência de indicador de atividade validado; nenhum corte
  numérico de remissão foi inventado.

Lote 23 (profilaxia antibiótica de endocardite, 8 itens) segue em
execução em paralelo — despachado antes deste checkpoint.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 23 — concluído (1 commit, SHA 26250d8a) — total 49 commits

- checklist `profilaxia-antibiotica-para-prevencao-de-endocardite-infecciosa-indicacoes-por-cenario`
  — 8 itens. 6 fontes (AHA 2007/2021, ESC 2023, AHA CIED 2024, PADIT
  Trial, SHEA/IDSA). Distinção clara entre indicações fortes e
  extrapolação/opinião de especialista (VAD, procedimento não-odontológico).

Nota: cluster Dispositivos "esc-2021-*"/CDI por canalopatia (~30 itens,
maior parcela do backlog não coberto) verificado como colidindo com o
hub geral ainda sob PR #599 (confirmado aberto) — não acionado, correto
manter distância. Pequeno gap de radioterapia+CIED (2 itens) parcialmente
coberto por doc existente, não priorizado.

## Lote 24 (em andamento, 1 agente) — fecha tema Endocardite nesta janela

Último item pequeno do backlog de Endocardite: seleção de modalidade de
imagem na avaliação DIAGNÓSTICA inicial (ETT primeira linha, ETE
obrigatório com prótese/dispositivo intracardíaco, RM não recomendada
para vegetação) — distinto do checklist de timing de repetição (lote 8).
Despachado (agente a827eb7ee6ccb2c32).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 24 — concluído (1 commit, SHA d217c1d7) — total 50 commits (marco)

- exame `selecao-de-modalidade-de-imagem-na-avaliacao-diagnostica-inicial-da-endocardite-infecciosa`
  — novo. Mesma fonte primária SBC 2019 do checklist de timing (Tabela 31),
  5 PMIDs verificados. Fecha a cobertura do tema Endocardite nesta janela.

## Lote 25 (em andamento, 1 agente) — retorno a Cardiomiopatias (maior backlog, 118 itens)

Cluster "cmh-*" identificado como o maior remanescente (34+ itens) — hub
`cardiomiopatia-hipertrofica` já tem boa profundidade geral (mavacamten,
aneurisma apical, esporte já cobertos), mas cluster "te-*"/SBC 2024
(6 itens: protocolo atenuado, TCPE, liberação pós-miocardite 3-6 meses,
reavaliação 2 anos pós-miocardite, TE seriado para ajuste de exercício e
para resposta pressórica) confirmado sem host — fonte brasileira
priorizada. Despachado (agente ad379774df47bfcc2).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 25 — concluído (1 commit, SHA b2925991) — total 51 commits

- checklist `teste-ergometrico-e-tcpe-seriado-na-cardiomiopatia-hipertrofica-e-apos-miocardite-sbc-2024`
  — 6 itens, fonte Diretriz Brasileira de Ergometria 2024 (PMID 38896581).
  Rigor exemplar no item 6: agente declarou explicitamente não ter
  conseguido acessar texto integral da diretriz internacional de CMH
  (paywall) para verificar elo com decisão de redução septal — tratado
  como inferência não verificada, não recomendação formal.

## Lote 26 (em andamento, 1 agente)

Cluster "amiloidose-*" (16 itens): verbetes de amiloidose já têm boa
profundidade geral (tafamidis, estadiamento), mas faltam pontos específicos
do algoritmo diagnóstico (escore de Perugini, razão H/CL, falsos-positivos
da cintilografia, biópsia quando cintilografia não resolve, tipagem/
sequenciamento, "não usar os 4 pilares da ICFEr" na amiloidose). Despachado
como checklist de 10 itens (agente aee932a13ee2f31a9).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 26 — concluído (1 commit, SHA 7d254034) — total 52 commits

- checklist `algoritmo-diagnostico-da-amiloidose-cardiaca-cintilografia-escore-de-perugini-e-biopsia`
  — 10 itens, 12 fontes. Gillmore 2016 (PMID 27143678, VPP 100%), Bokhari
  2013 (PMID 23400849, H/CL). Rigor: 2 lacunas declaradas explicitamente
  (descrição de graus 1/2 de Perugini, formulação mecanística sem citação
  literal de guideline).

## Lote 27 (em andamento, 1 agente)

Cluster Chagas em Cardiomiopatias (9 itens): verbete geral já cobre forma
indeterminada/Holter, mas RM cardíaca (fibrose/edema/trombo), periodicidade
de ECG e anticoagulação em trombo mural confirmados sem host — fonte
brasileira priorizada (doença endêmica no Brasil). Despachado (agente
a6f8173cbd84a6f3f).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 27 — concluído (1 commit, SHA bd39ef47) — total 53 commits

- checklist `investigacao-por-imagem-e-ecg-na-cardiomiopatia-chagasica-do-rastreio-a-estratificacao-de-risco`
  — 9 itens, fonte brasileira priorizada, 13 fontes verificadas.
  ECG define transição indeterminada→cardíaca; RMC com RTG em 71,4% da
  coorte USP associado a morte CV/TVS; trombo medeia 63,3% do risco
  embólico do aneurisma apical (coorte UFMG 2026). 3 lacunas declaradas
  explicitamente (periodicidade de ECG, corte de RTG, duração de
  anticoagulação).

## Lote 28 (em andamento, 1 agente)

Cluster Fabry (4 itens): nenhum host no corpus (só documento narrativo
sem detalhamento de vigilância por imagem) — eco anual primeira linha,
eco em triagem familiar sem teste genético, strain reduzido basal
inferolateral (achado precoce característico), T1 nativo REDUZIDO na RMC
(diferenciador — a maioria das outras causas de hipertrofia/infiltração
mostra T1 aumentado). Despachado como exame (agente accb1cd58669b414e).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 28 — concluído (1 commit, SHA 0c6fa017) — total 54 commits

- exame `vigilancia-por-imagem-cardiovascular-na-doenca-de-fabry-eco-anual-strain-e-t1-nativo`
  — novo, primeiro host de imagem estruturado para Fabry no corpus. 8
  fontes verificadas (Lu 2022 PMID 34687538, Kozor 2016 PMID 26729695,
  Pica/Sado 2014 PMID 25475749). Rigor: nenhum corte segmentar/T1 universal
  apresentado como padrão — declarado dependência de plataforma/sequência.

## Lote 29 (em andamento, 1 agente) — correção cirúrgica pequena

Verificado ANTES de dispatchar: verbete sarcoidose-cardiaca já tem
subseção pet_fdg_e_cintilografia_papel_e_limitacoes que DECLARA
explicitamente "a padronização exata do preparo dietético não está
detalhada... não deve ser reproduzida de memória" — confirma gap real
e genuíno (não falso-positivo do meu grep anterior). monitoring já
menciona "PET-FDG seriado" mas falta strain como ferramenta de rastreio.
Despachada correção (agente a7eed9f8e80401158); integração planejada como
MERGE cirúrgico (nova subseção + item de monitoring adicionado), não
substituição do dict diagnostic_approach existente.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 29 — concluído (1 commit, SHA cac190fe) — total 55 commits

- Correção `sarcoidose-cardiaca`: merge cirúrgico (não substituição) —
  protocolo de preparo do PET-FDG (dieta hiperlipídica/hipoglicídica +
  jejum, Christopoulos 2021 PMID 31111450) preencheu lacuna que o próprio
  verbete declarava explicitamente não ter conseguido detalhar; strain
  como rastreio adicionado ao monitoring (corte ~-17,3%, 80% sens.).
  Achado importante: item já estava "revisado" por correção anterior
  (zzz-auditoria-703) — nova correção zzzzzzz- reverteu para
  pendente_revisao, ordenação de arquivo verificada antes do commit.

## Checkpoint consolidado desta continuação ("prossiga", lotes 22-29, 13 commits)

8 lotes adicionais desde o checkpoint anterior: 2 exames novos (aortite
Takayasu/ACG, imagem diagnóstica em EI, vigilância Fabry), 1 verbete
complementar pediátrico já contabilizado no checkpoint anterior, 5
checklists novos (profilaxia EI, TE/TCPE em CMH, algoritmo diagnóstico da
amiloidose, imagem na cardiomiopatia chagásica) e 2 correções cirúrgicas
(ITB pós-esforço SBC 2024, sarcoidose PET-FDG+strain). Padrão de rigor
mantido em toda a extensão: PMIDs sempre verificados via NCBI e-utils,
lacunas declaradas explicitamente em vez de inventadas (múltiplas por
lote), merges cirúrgicos preservando estrutura existente em vez de
substituição destrutiva, correção de review_status quando conteúdo novo
é adicionado a item já aprovado.

Total geral da branch: 55 commits, 17+ verbetes/exames/checklists novos
substanciais desde o início desta fase (lote 7), cobrindo consistentemente
o território designado do Claude sem nenhuma colisão registrada.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 30 (em andamento, 1 agente)

Cluster "depositos-de-glicogenio-*" (4 itens): verbete Danon/PRKAG2 (lote
15) confirmado sem cobertura de protocolo de imagem — eco primeira linha,
manobras provocativas, T1 nativo reduzido no PRKAG2 (mapeamento), TEE em
evento neurológico. Despachado como exame (agente ae1d6fb8b354d0b26).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lote 30 — concluído (1 commit, SHA f0587af0) — total 57 commits

- exame `imagem-cardiovascular-nas-fenocopias-glicogenicas-danon-e-prkag2-eco-manobras-e-t1-mapping`
  — novo, complementar ao verbete Danon/PRKAG2 (lote 15). 6 fontes
  (Pöyhönen 2015 PMID 26496977, Bukhari 2026 PMID 42530173, Fang 2021
  PMID 34362124). Rigor exemplar: agente buscou o termo "mapa polar"
  pedido no briefing e declarou explicitamente NÃO tê-lo encontrado nas
  fontes — não reproduzido como achado confirmado.

## Fim desta continuação ("prossiga") — total 24 commits desde o checkpoint anterior (lotes 22-30)

9 lotes adicionais: 4 exames novos (aortite Takayasu/ACG, imagem
diagnóstica em EI, vigilância Fabry, imagem em fenocópias glicogênicas),
5 checklists novos (profilaxia antibiótica de EI, TE/TCPE em CMH pós-
miocardite, algoritmo diagnóstico da amiloidose, imagem na cardiomiopatia
chagásica) e 2 correções cirúrgicas com merge preservando estrutura
existente (ITB pós-esforço SBC 2024, sarcoidose PET-FDG+strain — incl.
reversão de review_status quando necessário). Zero colisão, zero gate
falho, zero PMID inventado em toda a extensão. Fila mantida cheia o tempo
todo conforme instruído; nenhum pedido de confirmação entre lotes.

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lotes 31-32 (em andamento, 2 agentes em paralelo) — nova continuação ("prossiga")

Backlog Cardiopatias congênitas (57 itens) escaneado: grandes clusters
"cc-adulto-*" (eco, 8 itens) + "cc-transesofagico-*" (ETE, 6 itens) +
"erg-ped-*" (teste ergométrico em ACHD, 6 itens) confirmados sem host —
nenhum checklist de indicações de imagem em ACHD existe no corpus.
Despachados dois agentes em paralelo: lote 31 = indicações de ETT em
ACHD (9 itens, agente aa1698398cc976c97), lote 32 = indicações de ETE em
ACHD (6 itens, agente a1dac83182823407a).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_

## Lotes 31-32 — concluídos (1 commit, SHA 8afd6e64) — total 59 commits

- checklist `indicacoes-de-ecocardiograma-transtoracico-na-cardiopatia-congenita-do-adulto`
  — 9 itens (ETT).
- checklist `indicacoes-de-ecocardiograma-transesofagico-na-cardiopatia-congenita-do-adulto`
  — 6 itens (ETE).
Produzidos em paralelo, 15 fontes verificadas no total. Ambos os agentes
declararam explicitamente quando não confirmaram classe/nível de
evidência por falta de acesso a texto integral — nunca inventaram
gradação.

## Lote 33 — concluído (SHA 63b18e45) — total 60 commits

- checklist `teste-ergometrico-e-tcpe-na-cardiopatia-congenita-do-adulto-fontan-fallot-tga-e-descompensacao`
  — 6 itens: VO2 pico prognóstico em Fontan (ressalva: sem corte único
  validado, só trajetória de declínio); contraindicação em
  descompensação (referência geral AHA, sem lista ACHD-específica);
  cianótica corrigida — incompetência cronotrópica (caveat: estudo-base
  é pediátrico); IC compensada pós-intervenção; Fallot reparada —
  dispersão QTc/JTc e MTWA induzidos por esforço, relevantes para
  decisão de troca valvar pulmonar; TGA corrigida (switch atrial/ccTGA)
  — 4 achados (incompetência cronotrópica, VE/VCO2 e VO2% preditores,
  segurança de treino aeróbico, GLS do VD sistêmico).
15 fontes via NCBI e-utils. Nenhuma diretriz SBC específica localizada —
declarado. **Fecha o cluster ACHD ETT/ETE/TCPE desta janela.**

Nota: origin/main avançou para 97899cf6 ("recovery emergencial
certificado", fora do escopo desta branch) — sem colisão nos diretórios
de conteúdo; branch segue sem rebase.

## Lote 34 — concluído (SHA e493eb7c) — total 61 commits

- checklist `recomendacoes-granulares-esc2020-ahaacc2018-ebstein-eisenmenger-cia-civ-fontan-tga-switch`
  — 5 itens complementando o hub geral `cardiopatia-congenita-do-adulto`
  (confirmado por grep como transversal, sem este nível de detalhe):
  reparo em cone vs. ablação de via acessória em Ebstein; bosentana em
  Eisenmenger (série BREATHE-5 completa, com limitação de desfecho
  substituto declarada); critérios de fechamento de CIA/CIV — lacuna
  EXPLÍCITA dos cortes numéricos Qp/Qs e RVSP (sem acesso ao texto
  integral da diretriz, não inventados); anticoagulação e vigilância
  hepática em Fontan (RCT Monagle 2011 — sem diferença varfarina vs.
  AAS); manejo de IART pós-switch atrial (ausência de RCT farmaco vs.
  ablação declarada). 13 fontes via NCBI e-utils. Nenhuma diretriz SBC
  específica localizada — declarado. **Fecha o cluster ACHD/achd2018
  desta janela.**

## Lote 35 — concluído (SHA 27304ce6) — total 62 commits

- checklist `manejo-terapeutico-escalonado-da-taquicardia-ventricular-polimorfica-catecolaminergica-cpvt`
  — 5 itens: betabloqueador não seletivo (nadolol preferencial);
  flecainida adjuvante via RyR2 (76% resposta em refratários);
  LCSD/simpatectomia para refratários; CDI com nuance específica de
  tempestade elétrica autoperpetuada pelo próprio choque; restrição de
  esporte competitivo mesmo em assintomático controlado. Gap confirmado
  por grep: hub geral de canalopatias cobria diagnóstico mas nada além
  de "betabloqueador primeira linha". 11 fontes via NCBI e-utils, toda
  evidência observacional/coorte (doença rara, sem RCT) — declarado.
  Nenhuma diretriz SBC específica localizada.

Auditoria pré-lote-36 nesta janela (grep + gh pr list) confirmou bem
cobertos e SEM gap acionável: gestação/cardiopatia (11 checklists),
esporte/pré-participação (17 checklists + 8 exames), perioperatório
(10 checklists), bloqueio AV/distúrbio de condução (fragmento completo,
inclui HV/bifascicular), MAD/prolapso mitral arritmogênico, cardiogenética
(13 painéis genéticos + 4 checklists). Evitados por colisão com PR aberto:
dispositivos cardíacos (PR #599), cardiomiopatia arritmogênica (PR #723).

## Lotes 36-37 — concluídos (2 commits, SHA fe051491 e 08112cb6) — total 64 commits

Auditoria confirmou escore de calcio/angio-TC/SPECT já muito bem
cobertos e idoso frágil/DRC já com fragmentos dedicados — sem gap
acionável ali. Dois gaps genuínos de medicina/imagem nuclear e RM
encontrados e despachados em paralelo:

- exame `ressonancia-magnetica-cardiaca-de-estresse-com-perfusao-por-vasodilatador-adenosina-ou-regadenosona`
  (lote 36) — mecanismo, indicações (RCT MR-INFORM), interpretação
  (CE-MARC vs. SPECT), ausência de corte quantitativo único declarada,
  artefato "dark rim", segurança de regadenosona em coorte de 5.780
  pacientes. 8 fontes via NCBI e-utils.
- exame `cintilografia-cardiaca-com-123i-mibg-avaliacao-da-inervacao-simpatica`
  (lote 37) — mecanismo (H/M ratio, washout), prognóstico em IC via
  ADMIRE-HF/ADMIRE-HFX (corte H/M ≥1,60), diferenciação de
  parkinsonismos, reanálise de interferência medicamentosa (só
  neuropsiquiátricos de alta potência afetam H/M, ao contrário do
  presumido). 8 fontes via NCBI e-utils.

Nenhuma diretriz SBC específica localizada em nenhum dos dois — declarado
em ambos. **Fecha o gap de medicina nuclear/RM de estresse desta janela.**

## Lote 38 — concluído (SHA 14e9e711) — total 65 commits

- checklist `vigilancia-e-manejo-pos-transplante-cardiaco-rejeicao-e-vasculopatia-do-enxerto`
  — 5 itens: biópsia de vigilância com classificação ISHLT 0R-3R
  (cronograma numérico exato declarado como não confirmado por texto
  integral); manejo escalonado da rejeição celular; rejeição humoral
  (AMR) via working formulation pAMR0-3, com nuance de assintomaticidade
  e DSA nem sempre detectável; vasculopatia do enxerto (CAV) com ênfase
  em que a denervação torna a angina silenciosa — rastreio não pode ser
  guiado por sintomas; imunossupressão de manutenção e vigilância de
  efeitos adversos. Gap de alto impacto: corpus cobria IC avançada/
  indicação de transplante mas nada da vigilância pós-transplante
  propriamente dita (zero menção a rejeição celular/humoral ou CAV antes
  desta adição). 8 fontes ISHLT via NCBI e-utils. Checagem de LVAD
  confirmou já bem coberto (7 itens dedicados) — evitada duplicação.

Auditoria pré-lote-39: confirmado sem gap acionável em LVAD (já coberto).

## Lote 39 — concluído (SHA baa7f231) — total 66 commits

- checklist `avaliacao-cardiovascular-pre-operatoria-para-cirurgia-bariatrica`
  — 5 itens: estratificação de risco (limitação do RCRI em obesidade
  grave declarada como extrapolação, não achado validado; escore
  OS-MRS; prevalência de DAC de 31,7% em candidatos com síndrome
  metabólica); AOS via STOP-BANG (remissão pós-cirúrgica de só 65% —
  não presumir resolução automática); cardiomiopatia da obesidade (eco
  de rotina NÃO preditivo de eventos, priorizar história dirigida);
  ajuste de medicação crônica com farmacocinética quantificada
  pós-bypass; profilaxia de TEV estratificada por risco. Gap de alta
  prevalência: cirurgia bariátrica é um dos procedimentos eletivos mais
  comuns hoje e tinha zero cobertura cardiovascular específica. 16
  fontes via NCBI e-utils. Confirmado que DAP/claudicação (exercício +
  cilostazol + revascularização já num checklist de 9 itens) e rastreio
  de AAA já estavam bem cobertos — evitada duplicação.

## Lote 40 — concluído (SHA d1c8b1b0) — total 67 commits

- checklist `manejo-de-longo-prazo-de-aneurisma-coronariano-de-kawasaki-da-infancia-a-vida-adulta`
  — 5 itens: classificação de risco por escore Z (AHA 2017); antitrombótico
  escalonado por tamanho (trombose intra-aneurismática documentada mesmo
  sob profilaxia); vigilância por imagem migrando de eco para angio-TC/RM
  com crescimento somático; avaliação funcional de isquemia; transição
  para o adulto (casos de Kawasaki não diagnosticado se apresentando como
  IAM em jovens; remodelamento residual mesmo após regressão aparente).
  10 fontes via NCBI e-utils, incluindo diretriz JCS/JSCS 2020 como
  complemento à AHA 2017. Periodicidade numérica exata declarada como
  não confirmada (acesso só a metadados) — não inventada.

**Nota de auditoria desta janela**: varredura extensa pré-lote-40
confirmou que Brugada (tempestade elétrica, ablação epicárdica,
quinidina), LQT1/2/3 por genótipo, limiares cirúrgicos de aneurisma de
aorta (inclusive degenerativo/esporádico), IMH/PAU, febre reumática (4
checklists, 50 itens), cardiotoxicidade por antraciclina/dexrazoxano e
DAP/claudicação já estão bem cobertos nesta base — os gaps
"fáceis"/óbvios do território de Claude estão substancialmente
exauridos nesta janela. Continuar exigirá auditorias progressivamente
mais estreitas/profundas por sub-tema.

## Lote 41 — concluído (SHA 79f6716a) — total 68 commits

- exame `pet-de-perfusao-miocardica-com-rubidio-82-ou-amonia-n-13-e-reserva-de-fluxo-coronariano`
  — único método com quantificação absoluta de fluxo/CFR, ausente do
  corpus apesar de SPECT e PET-FDG já cobertos. Especificidade superior
  ao SPECT em obesidade (84% vs. 64%); indicação central em doença
  microvascular e isquemia balanceada triarterial; valor prognóstico
  robusto do CFR (HR 5,6x no tercil mais baixo); ausência de corte
  numérico único validado por consenso declarada explicitamente (dois
  limiares distintos citados de estudos diferentes, sem apresentar como
  consenso). 8 fontes via NCBI e-utils, incluindo posicionamento
  conjunto SNMMI/ASNC. **Fecha o gap de medicina nuclear cardiovascular
  desta janela (SPECT + PET-FDG + PET-perfusão + MIBG agora cobertos).**

## Lote 42 — concluído (SHA 0cd0457a) — total 69 commits

- checklist `seguranca-cardiovascular-do-exercicio-fisico-e-esporte-na-gestacao-sem-cardiopatia`
  — 5 itens na interseção de gestação+cardiopatia e cardiologia do
  esporte (territórios cobertos separadamente, mas nunca combinados):
  recomendação geral ACOG (RPE/talk-test em vez de zona de FC-alvo,
  ausência declarada); contraindicações absolutas/relativas com
  reavaliação de "quase-contraindicações" tradicionais sem evidência de
  dano; sinais de alarme para suspensão imediata; síndrome de hipotensão
  supina com nuance de revisão 2022 questionando magnitude clássica;
  atleta competitiva grávida — desaceleração de FC fetal acima de ~90%
  da FC materna máxima em 2 estudos independentes, ausência de protocolo
  padronizado de triagem pré-participação declarada. 12 fontes via NCBI
  e-utils.

## Lote 43 (em andamento, 1 agente)

Tentativa de conectividade: cogitei setar `documento_origem` de 8
checklists desta janela (CPVT→canalopatias, ACHD×4→cardiopatia-congenita-
do-adulto, CMH, Chagas, transplante→IC avançada) diretamente para o
slug do hub de doença. `audit_tudo_com_tudo.py` **rejeitou as 8** —
`documento_origem` só aceita referência a item tipo `documento`/
`fluxograma`, não a `SpecialtyDisease` diretamente (mecanismo distinto
de `related_document_slugs`, que é campo de doença, não de checklist).
Revertido via `git checkout` antes de qualquer commit — nenhum dano.
Lição registrada: os `documento_origem: null` desta janela eram
corretos por ausência de fluxograma/documento dedicado ao subtema, não
por descuido.

Gap novo encontrado: origem anômala de artéria coronária (AAOCA) —
2ª causa mais comum de morte súbita em atletas jovens em séries de
necropsia, sem hub dedicado (só menção tangencial dentro do checklist de
ETT-ACHD do lote 31). Interseção de congênita/esporte/morte súbita.

## Lote 43 — concluído (SHA 025fdd23) — total 70 commits

- checklist `origem-anomala-de-arteria-coronaria-aaoca-caracterizacao-anatomica-cirurgia-e-elegibilidade-esportiva`
  — 5 itens: anatomia de risco (trajeto intramural como mecanismo de
  compressão dinâmica, não fixa; ausência de corte numérico declarada);
  angio-TC como modalidade de escolha; indicação cirúrgica escalonada
  por sintoma+anatomia+subtipo (AAOLCA sempre mais grave); elegibilidade
  esportiva via Task Force 4 AHA/ACC; limitação crítica do teste de
  esforço isolado — sensibilidade de apenas 19% para isquemia (sobe a
  58% com CPET), não deve ser critério único de liberação. 10 fontes via
  NCBI e-utils, incluindo nomenclatura padronizada ICAAC 2026.

## Lote 44 — concluído (SHA cb456a2a) — total 71 commits

- checklist `vigilancia-arterial-extra-aortica-visceral-em-sindrome-de-loeys-dietz-e-ehlers-danlos-vascular`
  — 5 itens complementando o fragmento existente de aortopatia genética
  pediátrica (que cobre só raiz/aorta torácica): distribuição real de
  leitos extra-aórticos acometidos (mesentérica 31,7% em EDS vascular);
  protocolo cabeça-a-pelve com intervalo de ~2 anos em LDS estável
  (atribuído a comunicação pessoal dos autores, não estudo controlado —
  distinção explícita); manejo de aneurisma visceral (4 óbitos
  intraoperatórios em 21 reparos abertos vs. zero em 18 embolizações,
  reforçando preferência endovascular); ruptura espontânea de órgão SEM
  aneurisma prévio (47% dos casos esplênicos, 17% diagnóstico
  post-mortem); risco gestacional quantificado (5,3% óbito materno).
  11 fontes via NCBI e-utils, com leitura de **texto integral via PMC**
  quando disponível (não apenas abstract) — nível de rigor mais alto
  que o padrão desta janela.

**Descoberta evitada por colisão de escopo**: "bloqueio de ramo esquerdo
novo" descartado do planejamento — investigação dessa condição se
sobrepõe fortemente a critérios de Sgarbossa/SCA, fora do território de
Claude (coberto por outras branches/Codex).

## Lote 45 — concluído (SHA 4d24da30) — total 72 commits

- checklist `acometimento-cardiovascular-na-doenca-falciforme-hipertensao-pulmonar-e-cardiomiopatia`
  — 5 itens: hipertensão pulmonar via TRV (RR 10,1, com nuance de que é
  rastreio, não diagnóstico); cardiomiopatia/disfunção diastólica por
  alto débito (RR 3,5, combinado com HP eleva a RR 12,0); NT-proBNP
  ≥160 pg/mL validado em 2 coortes independentes; manejo específico
  (cautela com diuréticos declarada como prática aceita SEM estudo
  controlado dedicado — não inventado; achado verificado de que
  hidroxiureia NÃO reduziu HP nessa coorte); morte súbita via registro
  piloto DREPACOEUR (arritmia ventricular em 22%, GLS promissor mas não
  validado). Gap de alta prevalência no Brasil — só havia menção
  tangencial dentro de cardiomiopatia por sobrecarga de ferro. 8 fontes
  via NCBI e-utils, incluindo diretriz ASH 2019.

## ⚠️ CORREÇÃO CRÍTICA (30/08/2026) — falha de processo em waves 22-45

Ao investigar o lote 46 (CIV perimembranosa/muscular na criança),
descobri que o alvo já estava coberto em
`content/Cardiologia_pediátrica/civ-e-cia-na-crianca-historia-natural-e-
criterios-de-fechamento.md` — arquivo em uma pasta que eu nunca havia
buscado nesta janela. Investigação revelou uma falha de processo
sistêmica: **todo o procedimento de checagem de colisão usado nas waves
22-45 buscava apenas em `doencas/fragmentos/*.json`,
`checklists/metadados.json` e `exames/metadados.json` — nunca em
`content/**/*.md`**, corpus de 1.962 arquivos markdown organizados por
pasta de especialidade, que é a base de conteúdo primária de outras
trilhas de produção (ChatGPT/Codex, sessões noturnas anteriores de
Claude). Isso violou a regra obrigatória de colisão do briefing.

Auditoria retroativa (SHA 919b3b86) encontrou 3 duplicatas quase totais
— removidas: AAOCA (lote 43, duplicava documento já revisado e
autorizado em 27/08), CPVT (lote 35, duplicava documento com MAIS rigor
de 25/08), algoritmo de amiloidose (lote 26, duplicava fluxograma
existente de Perugini). 2 checklists com sobreposição PARCIAL mantidos
com nota de revisão apontando o documento a cotejar: ACHD granular
(lote 34, 2 dos 5 itens sobrepostos) e vigilância pós-transplante
(lote 38, seção de biópsia sobreposta). Demais 19 waves verificados
sem colisão confirmada. Nada publicado foi afetado — tudo estava
`pendente_revisao`.

**Procedimento corrigido a partir de agora**: toda checagem de colisão
inclui `grep` explícito em `content/**/*.md`, além dos JSONs já
verificados.

## Lote 46 — concluído (SHA 80691b0f) — total 74 commits

Primeiro lote desde a correção crítica, verificado com o procedimento
corrigido (JSONs + `content/**/*.md` + `gh pr list`).

- checklist `interpretacao-do-ecg-em-atletas-negros-variantes-normais-versus-achados-de-alarme`
  — 5 itens: inversão de onda T anterior V1-V4 como variante normal
  quando isolada (22,8% vs. 3,7% em brancos); voltagem isolada de HVE
  como adaptação ao treino, variando por origem geográfica — não
  generalizar; achados de alarme (100% dos casos com cardiomiopatia
  confirmada tinham inversão LATERAL, não isolada anterior); fluxo de
  investigação eco+RM, com nuance de que teste genético isolado agregou
  só 2,5% de diagnóstico quando avaliação clínica já normal; desfecho —
  especificidade de 97-99% em ambas as raças, tranquilização vem DEPOIS
  da triagem, nunca no lugar dela. 8 fontes via NCBI e-utils. Nenhum
  corte numérico (mm/mV) inventado — regra qualitativa usada por falta
  de confirmação exata nas fontes.

## Lote 47 — concluído (SHA d96c623a) — total 75 commits

- checklist `avaliacao-cardiovascular-do-candidato-a-transplante-hepatico-cardiomiopatia-cirrotica-e-rastreio-coronariano`
  — 5 itens: cardiomiopatia cirrótica (FE de repouso normal mascara
  reserva contrátil comprometida, critérios revisados 2019/2020
  substituindo Montreal 2005); eco de estresse com dobutamina (18% de
  exames inadequados nessa população); rastreio coronariano via escore
  CAD-LT (97% de acerto), com nuance de que testes funcionais têm
  acurácia limitada segundo AHA 2022; hipertensão porto-pulmonar (eco
  como rastreio, SEMPRE exige confirmação por cateterismo antes de
  contraindicar transplante); manejo perioperatório (reperfusão
  desmascara reserva comprometida no momento de maior risco). 11 fontes
  via NCBI e-utils. Ausência de PMID isolado para consenso Montreal 2005
  declarada explicitamente (via revisão posterior, não inventado).

## Lote 48 — concluído (SHA 71ac0639) — total 76 commits

- checklist `avaliacao-cardiovascular-do-candidato-a-transplante-renal-rastreio-coronariano-e-doenca-mineral-ossea`
  — 5 itens: rastreio coronariano (AHA 2022 — rastreio sistemático em
  assintomáticos "não demonstrou melhorar desfechos"; CARSK citado com
  nota explícita de que a busca não encontrou resultados primários
  publicados, só protocolo — não inventado); calcificação vascular
  (escore de cálcio preditor independente de mortalidade); hipertrofia
  ventricular progressiva mesmo sem doença sintomática; doença valvar
  calcificada progressiva (coorte brasileira); manejo perioperatório da
  diálise (coorte Medicare de 1,1 milhão de procedimentos, associação
  dose-dependente intervalo-mortalidade, com ressalva de ser
  observacional). 11 fontes via NCBI e-utils. Cluster de avaliação
  cardiovascular pré-transplante de órgão sólido (hepático + renal)
  encerrado nesta janela.

## Lote 49 — concluído (SHA dad1d5e0) — total 77 commits

- checklist `doenca-cardiovascular-no-paciente-com-hiv-risco-inflamatorio-interacoes-e-prevencao`
  — 5 itens: risco inflamatório persistente mesmo com supressão viral
  (HR 1,48 para IAM ajustado); estratificação de risco — equações
  tradicionais subestimam risco em HIV, ensaio REPRIEVE como 1º RCT de
  prevenção primária específico (interrompido por eficácia, HR 0,65);
  interações medicamentosas (PI/cobicistat como inibidores potentes de
  CYP3A4 — contraindicação de sinvastatina/lovastatina, DOAC, BCC);
  cardiomiopatia/miocardite (transição pré-TARV/TARV, prevalência de
  miocardite na era moderna declarada como lacuna — não inventado);
  doença coronariana (fenótipo de placa não calcificada/inflamatória,
  escore de cálcio zero pode subestimar). 13 fontes via NCBI e-utils.

## Lote 50 — concluído (SHA f0196578) — total 78 commits — MARCO

- checklist `sindrome-de-taquicardia-postural-pots-e-disautonomia-desencadeada-pela-covid-19`
  — 5 itens: epidemiologia/mecanismo (33% de nova POTS em coorte
  sintomática autosselecionada, viés declarado; aumento populacional em
  base TriNetX, associação temporal não causal); diagnóstico
  diferencial (só 13% de fadiga pós-COVID tinha POTS objetiva
  confirmada); teste de inclinação; manejo não farmacológico (RCT
  mostrando boa tolerância a HIIT/MICT, contrapondo preocupação teórica
  de mal-estar pós-esforço); manejo farmacológico (ivabradina com RCT
  em POTS GERAL, nota de rigor explícita de que nenhum fármaco tem RCT
  dedicado a POTS pós-COVID — extrapolação declarada). 11 fontes via
  NCBI e-utils.

**Resumo da janela até aqui**: 50 lotes despachados desde o início
desta continuação (22-50), 3 removidos por duplicata na correção
crítica de 30/08 (item anterior), restando 28 itens novos líquidos
integrados + 1 correção. Cluster imagem cardiovascular (SPECT/PET-FDG/
stress-CMR/PET-perfusão/MIBG), cluster ACHD, cluster transplante de
órgão sólido (hepático+renal) e cluster populações especiais (falciforme,
HIV, pós-COVID) fechados nesta janela.

## Lote 51 — concluído (SHA 0e59d9c4) — total 79 commits

- checklist `reabilitacao-cardiaca-e-prescricao-de-exercicio-pos-transplante-cardiaco-coracao-denervado`
  — 5 itens complementando o checklist de vigilância de rejeição/CAV
  já existente: fisiologia denervada (resposta cronotrópica
  catecolamina-dependente, reinervação parcial tardia e incompleta);
  TCPE (reserva cronotrópica correlacionada a sobrevida, nota explícita
  de que VE/VCO2 não tem validação transplante-específica); benefícios
  da reabilitação (Cochrane +2,49 mL/kg/min, HIIT superior mas ganho
  não se mantém em 5 anos sem manutenção); prescrição (FC-alvo e Borg
  ambos com limitações documentadas, nuance preservada); segurança
  (evidência construída em pacientes já estáveis, não na fase hospitalar
  imediata). 20 fontes via NCBI e-utils. Auditoria prévia confirmou
  CAR-T, Buerger/Raynaud, critérios de Padua/ALVC e calculadora de
  risco de ACM já bem cobertos — evitada duplicação.

## Lote 52 — concluído (SHA e20cf0f0) — total 80 commits

- checklist `insuficiencia-de-ventriculo-direito-apos-implante-de-lvad-risco-reconhecimento-e-manejo`
  — 5 itens complementando o checklist geral de acompanhamento pós-LVAD:
  fisiopatologia (desvio septal, interdependência ventricular);
  estratificação de risco com 3 escores validados (Kormos, CRITT,
  EUROMACS-RHF — risco de 11% a 43,1%); reconhecimento clínico-
  hemodinâmico; manejo médico (vasodilatador pulmonar, redução de
  velocidade do LVAD); suporte mecânico temporário (Impella RP, ECMO,
  RVAD). 7 fontes via NCBI e-utils, incluindo consenso ISHLT 2013.
  Todos os cortes numéricos extraídos diretamente dos abstracts, nenhum
  inventado.

## PARADA — ordem do Rafael (30/08/2026)

Ordem recebida: "Interromper produção, finalize o que está fazendo,
salve, e prepare para publicação." Produção interrompida imediatamente.

Um agente de pesquisa do lote 53 (trombose subclínica de folheto em
biopróteses/HALT-HAT) estava em andamento no momento da ordem — seu
resultado NÃO foi integrado ao corpus; a pesquisa pode ter concluído
em background de forma independente, mas nenhum conteúdo dela entrou
em `checklists/metadados.json` ou em qualquer arquivo do repositório.

**Estado final desta janela contínua (lotes 22-52, 30/08/2026, SHA
5e8c99cc)**: árvore de trabalho limpa, sem alterações pendentes;
`audit_tudo_com_tudo.py` com `broken_references: []`;
`content_inventory.py --strict` com 0 erros, 9.812 registros totais;
`/opt/meucardio` sem arquivos órfãos. 126 commits à frente de
`origin/main` (branch nunca rebaseada, nunca mesclada, conforme
instrução original).

**Resumo do que foi produzido nesta janela** (lotes 22-52, 31 lotes
efetivos após a correção crítica que removeu 3 duplicatas): cluster
imagem cardiovascular (aortite/Takayasu, endocardite×2, PET-FDG
sarcoidose, Fabry, Danon/PRKAG2, stress-CMR, PET-perfusão/Rb-82,
MIBG); cluster ACHD (ETT, ETE, TCPE, recomendações granulares
ESC2020/AHA2018); cluster canalopatias (CPVT — removido por duplicata,
ver correção); cluster transplante de órgão sólido (hepático, renal,
vigilância de rejeição/CAV cardíaco, reabilitação pós-transplante
cardíaco); cluster populações especiais (doença falciforme, HIV,
avaliação pré-bariátrica, exercício na gestação, POTS pós-COVID);
AAOCA; Kawasaki no adulto; vigilância extra-aórtica em Loeys-Dietz/EDS
vascular; ECG em atletas negros; insuficiência de VD pós-LVAD.

**Correção crítica registrada em 30/08/2026** (ver acima): 3 itens
duplicados removidos (AAOCA, CPVT, algoritmo de amiloidose), 2
parcialmente sobrepostos flagados com nota de revisão (ACHD granular,
vigilância pós-transplante). Procedimento de colisão corrigido
permanentemente para incluir `content/**/*.md` em toda checagem futura
nesta branch.

**Status editorial**: todo conteúdo desta janela está com
`review_status: pendente_revisao` — nada foi aprovado editorialmente
por Claude, conforme regra do briefing original. Pronto para revisão
humana e decisão de publicação pelo Rafael.

_(fim da produção contínua desta janela — aguardando nova instrução)_

## RETOMADA — ordem do Rafael (30/08/2026)

Ordem recebida: "prossiga com a produção". Produção retomada.

## Lote 53 — concluído (SHA f2b455f8) — total 81 commits

- checklist `trombose-subclinica-de-folheto-em-bioproteses-halt-deteccao-por-4d-ct-e-manejo`
  — item já pesquisado integralmente pelo agente antes da pausa;
  integrado normalmente na retomada (sem redespachar). Slug corrigido
  (removido caractere acentuado "biopróteses"→"bioproteses" para manter
  convenção ASCII). 5 itens: definição HALT vs. HAT; angio-TC 4D como
  método de escolha; prevalência 12% geral/4% cirúrgica vs. 13% TAVI
  (RESOLVE/SAVORY) e 10%→24% em 1 ano (PARTNER 3 CT substudy);
  significado clínico com controvérsia preservada (associação com
  AIT/AVC combinado, não com AVC isolado); manejo — achado central do
  GALILEO-4D: rivaroxabana resolveu HALT mas o ensaio principal mostrou
  PIOR desfecho clínico em quem não tinha indicação prévia de
  anticoagulação. 9 fontes via NCBI e-utils, leitura de abstract
  completo via efetch.

## Lote 54 — concluído (SHA a644487f) — total 82 commits

- checklist `acometimento-cardiaco-na-doenca-de-pompe-cardiomiopatia-infantil-e-terapia-de-reposicao-enzimatica`
  — 5 itens complementando as fenocópias glicogênicas Danon/PRKAG2 já
  cobertas, com mecanismo lisossômico distinto (GAA): fisiopatologia
  (IOPD vs. LOPD, cardiomiopatia obrigatória por definição na forma
  infantil); achados de imagem/ECG (PR curto e voltagem elevada como
  marcadores de gravidade/resposta); rastreio neonatal (piloto de
  Taiwan); TRE com alglucosidase alfa (reversão documentada, mas ganho
  menor quanto mais tardio o início); seguimento de longo prazo (WPW em
  8/113 mesmo com melhora funcional; 6% de parada cardiopulmonar na
  indução anestésica — propofol/sevoflurano contraindicados). 13 fontes
  via NCBI e-utils. Endocardite protética, Takayasu/tocilizumabe, ATTR
  (tafamidis/acoramidis) e TEER tricúspide já confirmados bem cobertos
  — evitada duplicação.

## Lote 55 — concluído (SHA b8e465c6) — total 83 commits

- checklist `acometimento-cardiaco-nas-mucopolissacaridoses-valvopatia-cardiomiopatia-e-doenca-coronariana`
  — 5 itens complementando as menções breves já existentes em docs de
  diagnóstico diferencial: fisiopatologia por subtipo (MPS I/II/VI mais
  graves); valvopatia progressiva (regurgitação mitral em 58-74%,
  relativamente refratária a TRE já estabelecida); doença coronariana
  por depósito de GAG — mecanismo distinto de aterosclerose clássica,
  documentado mesmo pós-TCTH; imagem/monitorização com 2 lacunas de
  evidência declaradas explicitamente; TRE/TCTH com efeito diferencial
  por componente cardíaco e via aérea difícil perioperatória (1,06% vs.
  25,6% de complicação com protocolo padronizado). 10 fontes via NCBI
  e-utils. Cluster de cardiomiopatias de depósito lisossômico (Fabry,
  Pompe, Danon/PRKAG2, MPS) encerrado nesta janela.

## Lote 56 — concluído (SHA 838dc722) — total 84 commits

- checklist `disautonomia-e-pots-na-sindrome-de-ehlers-danlos-hipermovel-triagem-triade-clinica-e-manejo`
  — 5 itens distintos tanto do POTS pós-COVID (gatilho viral) quanto da
  EDS vascular (risco arterial estrutural): associação epidemiológica
  (78% vs. 10%, coorte pequena não extrapolada); triagem por Beighton +
  Critérios 2017, com nota de que hEDS é diagnóstico clínico sem teste
  confirmatório; tríade hipermobilidade-POTS-MCAS (OR 32,46, faixas de
  2-87% conforme critério, sem número único apresentado como
  definitivo); manejo — fisioterapia de fortalecimento antes de
  exercício cardiovascular; diagnóstico diferencial com red flags que
  reclassificam para vEDS/Loeys-Dietz. 12 fontes via NCBI e-utils.
  Confirmado que hemocromatose hereditária, reativação de Chagas
  pós-transplante, SCAD, Löffler e beriberi já estavam bem cobertos —
  evitada duplicação.

## Lote 57 — concluído (SHA 15ae85fe) — total 85 commits

- exame `vetorcardiograma-fonocardiograma-e-apexcardiograma-metodos-graficos-classicos-papel-historico-e-uso-atual`
  — último território confirmado com zero cobertura ao longo de toda a
  janela (Métodos gráficos e funcionais). Redigido com rigor
  deliberadamente honesto: instrução explícita para não inflar
  relevância clínica atual, dado que os 3 métodos foram amplamente
  substituídos por ECG 12 derivações e ecocardiograma. Nichos de uso
  ATUAL genuinamente verificados (não inventados): QRS area derivado
  matematicamente do ECG digital como preditor de resposta a TRC;
  fonocardiograma digital com IA em pesquisa pediátrica translacional,
  ainda sem adoção assistencial; apexcardiograma quase exclusivamente
  histórico. 10 fontes via NCBI e-utils. Nesta auditoria extensa (waves
  56-57) confirmado saturação quase completa: acromegalia,
  feocromocitoma, cor pulmonale, Wellens, TAVI-LBBB, Turner, Brugada
  storm, QT por antipsicóticos — todos já bem cobertos.

**Nota de saturação desta janela**: após 36 lotes efetivos desde a
retomada (waves 22-57, líquido de remoções), o território de Claude
está substancialmente exaurido nos gaps facilmente descobríveis.
Continuar exigirá auditorias progressivamente mais estreitas ou
aprofundamento pontual de hubs existentes.

## Lote 58 — concluído (SHA 12517a83) — total 86 commits

- checklist `avaliacao-cardiovascular-do-doador-cardiaco-criterios-de-aceitacao-do-enxerto`
  — 5 itens do lado do DOADOR, complementando toda a cobertura já
  construída do lado do receptor: critérios do doador (ausência de
  corte etário único confirmado, declarado); ecocardiograma do doador
  (disfunção sistólica inicial NÃO é contraindicação automática —
  "tempestade catecolaminérgica" da morte encefálica é reversível,
  recuperação de FE de 48% para 59% em protocolo ativo); ECG e morte
  encefálica (QTc longo NÃO se associou a recusa após ajuste, mas HVE
  foi preditor forte); rastreio coronariano seletivo; otimização
  hemodinâmica (pacote combinado com respaldo retrospectivo sólido,
  mas RCT de T4 isolado NÃO mostrou melhora significativa — distinção
  preservada com honestidade). 11 fontes via NCBI e-utils. Confirmado
  extensa saturação nesta auditoria: SGLT2i em CMH, PFA, leadless
  pacemaker, clozapina, sarcopenia — já cobertos.

## Lote 59 — concluído (SHA e119589a) — total 87 commits

- checklist `cuidado-cardiovascular-no-adulto-com-sindrome-de-down-espectro-congenito-e-valvopatia-adquirida`
  — achado de ALTA prevalência: síndrome de Down é a causa cromossômica
  mais comum de CHD (~50% vs. ~1%), zero cobertura apesar da extensa
  ACHD já construída. 5 itens: espectro congênito (AVSD mais frequente,
  eco neonatal mesmo sem sopro); hipertensão pulmonar ("janela segura"
  clássica não se aplica — DVPO fixa em 10/81 antes de 1 ano vs. 0/40
  sem Down); valvopatia adquirida (MVP em até 57%/RA em 11% mesmo sem
  CHD ao nascimento, progressão adolescência→adulto documentada);
  considerações perioperatórias (instabilidade atlantoaxial, estridor
  pós-extubação em 24%); rastreio vitalício sem periodicidade numérica
  especificada — lacuna declarada. Nota de rigor: uma citação inline
  não respaldada por `source_refs` foi removida antes de integrar. 9
  fontes via NCBI e-utils. Evitada colisão com PR #599 (dispositivos)
  ao descartar tópico de complicações de CSP — hub geral de 21k linhas
  já em revisão.

## Lote 60 — concluído (SHA 786c304b) — total 88 commits — MARCO

- checklist `cardiopatia-congenita-associada-a-sindrome-de-alagille-vacterl-e-charge-espectro-e-manejo`
  — fecha o subcluster de síndromes genéticas com CHD (Down, DiGeorge/
  22q11, Williams, Noonan já confirmados). 3 condições bundladas:
  Alagille (94% de acometimento CV, estenose de ramos pulmonares
  DIFUSA/multifocal em 76%, reestenose intra-stent de 24% nesse
  subgrupo); VACTERL (explicitamente NÃO é síndrome genética única,
  critério ≥3 componentes); CHARGE (cardiopatia em 74% dos CHD7+,
  anomalias de arco associadas a outro defeito em 81% dos casos);
  aconselhamento genético com padrões de herança distintos entre as
  três. 11 fontes via NCBI e-utils, incluindo GeneReviews.

**Resumo do marco 60 lotes**: desde o início desta janela contínua
(lote 22), 39 itens novos líquidos integrados (3 removidos por
duplicata na correção crítica), 1 correção crítica de procedimento
documentada e resolvida, PR #760 aberto e atualizado automaticamente a
cada push. Territórios agora extensivamente cobertos: imagem
cardiovascular (todas as modalidades), ACHD completo, síndromes
genéticas com CHD, cardiomiopatias de depósito lisossômico, transplante
de órgão sólido bilateral (doador+receptor, cardíaco/hepático/renal),
populações especiais (falciforme, HIV, pós-COVID, hEDS), canalopatias,
métodos gráficos.

## Lote 61 — concluído (SHA 59cc61f2) — total 89 commits

- checklist `atresia-tricuspide-classificacao-edwards-burchell-e-via-cirurgica-estagiada-ao-fontan`
  — gap genuíno: a atresia tricúspide como entidade anatômica primária
  nunca havia sido coberta, apesar da base extensa já construída sobre
  Fontan/cianose neonatal/triagem oximétrica (menções existentes em
  `content/**/*.md` tratam a lesão apenas de passagem). PR #710
  (insuficiência tricúspide) é valvopatia, sem sobreposição. 5 itens:
  classificação de Edwards-Burchell (1949) — tipos I-III por relação
  ventrículo-arterial × subtipos a/b/c por fluxo pulmonar;
  apresentação neonatal (shunt D-E obrigatório via CIA, dependência
  ductal por subtipo); manejo inicial (PGE1, Rashkind, shunt BT vs.
  banding); via estagiada ao Fontan (Glenn ~6 meses, Fontan ~1-2 anos
  depois, fenestração 4-6mm — nota de rigor sobre variação de idade
  entre centros); particularidades univentriculares — metanálise de
  27 estudos/9.373 pacientes (Ponzoni 2022, PMID 36367236): sobrevida
  em 20 anos 86% (ventrículo dominante esquerdo, caso da atresia
  tricúspide) vs. 69% (dominante direito). 8 fontes via NCBI e-utils,
  incluindo a classificação original (PMID 18145655) e ESC 2020/
  AHA-ACC 2018 ACHD. Nenhuma diretriz SBC específica localizada —
  declarado. Gates limpos. Total: 422 checklists.

## Lote 62 — concluído (SHA 424505dd) — total 90 commits

- checklist `sindrome-heterotaxia-isomerismo-atrial-direito-esquerdo`
  — gap genuíno: heterotaxia/isomerismo atrial nunca teve entrada
  dedicada (apenas 6 menções de passagem em `content/**/*.md` e 1 menção
  textual sem slug em `doencas/metadados.json`). Nenhum PR aberto sobre
  o tema. 6 itens: classificação IAD (asplenia) vs. IAE (polisplenia)
  por morfologia de apêndice atrial, com discordância subtipo↔status
  esplênico documentada em até ~28% dos casos; espectro de cardiopatias
  associadas (DSAV 72,9% IAD vs. 59,3% IAE, metanálise com IC amplos
  declarados); sistema de condução — base anatômica explicando maior
  bradiarritmia/BAVT no IAE (87% vs. 29%); achados extracardíacos e
  risco infeccioso por asplenia, variabilidade de prática documentada
  por ausência de diretriz unificada; abordagem diagnóstica; manejo
  cirúrgico/prognóstico — dados diretamente discordantes entre séries
  sobre qual subtipo é pior, declarado em vez de resolvido
  artificialmente. Correção de integridade: 2 citações inline sem
  lastro em `source_refs` (Rao 1982, Pastakia 1979) removidas antes de
  integrar, em vez de adicionadas sem verificação própria. 19 fontes
  via NCBI e-utils. Nenhuma diretriz SBC/AHA-ACC dedicada localizada —
  declarado. Gates limpos. Total: 423 checklists.

## Lote 63 — concluído (SHA 4eefa8de) — total 91 commits

- checklist `fistula-arterial-coronariana-congenita` — gap genuíno:
  zero menção no corpus sob qualquer grafia. Nenhum PR aberto (PR #697
  é MINOCA/SCAD, entidade adquirida distinta). 6 itens: classificação
  de Sakakibara (1966) com ressalva de que só título/resumo foi
  verificado, não texto integral; diferenciação formal frente a AAOCA
  (terminação distal anômala vs. origem/curso proximal anômalo);
  epidemiologia — 0,18% em série angiográfica de 126.595 pacientes,
  fechamento espontâneo em 30,3% de crianças pequenas, com
  inconsistência aritmética sinalizada explicitamente numa cifra
  publicada em Arq Bras Cardiol; apresentação clínica estratificada por
  idade (79% assintomática em crianças vs. 71% sintomática em adultos);
  abordagem diagnóstica; indicações de fechamento — declarado que a
  diretriz AHA/ACC 2018 não pôde ser verificada quanto a COR/LOE
  específico (paywall, sem cópia PMC) e nenhuma diretriz SBC localizada;
  desfechos do fechamento percutâneo vs. cirúrgico. 15 fontes via NCBI
  e-utils. Correção de processo: o subagente inicialmente removeu toda
  acentuação do texto corrido (mal-entendido da instrução "ASCII", que
  deveria valer só para slug/id) — reenviado ao mesmo agente para
  correção antes de integrar, sem re-pesquisar. Gates limpos. Total:
  424 checklists.

## Lote 64 — concluído (SHA 7740a631) — total 92 commits

- checklist `aneis-vasculares-congenitos` — gap genuíno: anomalias de
  arco com compressão traqueoesofágica só tinham menções de passagem
  (22q11.2, Turner). PR #580 (doença da aorta geral) é sobre patologia
  aórtica do adulto, sem sobreposição. 6 itens: classificação anatômica
  (duplo arco vs. arco direito com ligamento esquerdo/"loose ring"),
  nenhuma diretriz SBC localizada (único registro nacional é relato de
  caso de 1985); sling de artéria pulmonar, diferenciado explicitamente
  de um "anel" verdadeiro; divertículo de Kommerell, com ressalva
  explícita contra extrapolar história natural de adultos para
  seguimento pediátrico assintomático; apresentação clínica por idade,
  impacto do diagnóstico pré-natal (99% assintomáticos aos 30 meses);
  investigação diagnóstica (RM com sensibilidade equivalente à TC, sem
  radiação); tratamento cirúrgico — mortalidade baixa mas liberdade de
  sintomas residuais caindo de 97% (1 ano) a 86,2% (10 anos) por
  traqueomalácia residual. 16 fontes via NCBI e-utils. Correção de
  processo repetida: agente novamente removeu acentuação na primeira
  entrega (mesmo padrão do lote 63) — reenviado com instrução mais
  explícita, corrigido sem re-pesquisar. Gates limpos. Total: 425
  checklists.

## Lote 65 — concluído (SHA 500c4306) — total 93 commits

- checklist `cardiomiopatia-sobrecarga-de-ferro` — gap genuíno: zero
  menção a hemocromatose, sobrecarga de ferro, talassemia, quelação ou
  T2* em todo o corpus, apesar da extensa cobertura de anemia
  falciforme já construída nesta janela. Nenhum PR aberto. 6 itens:
  fisiopatologia (HFE vs. secundária/transfusional, com ressalva contra
  generalizar dados de talassemia para outras anemias); espectro
  clínico (arritmia RR 4,6x com T2*<20ms); triagem laboratorial
  (ferritina NÃO substitui avaliação direta de ferro miocárdico, AUC
  0,629 vs. 0,948); RM cardíaca T2* como padrão-ouro (RR de IC de 160x
  com T2*<10ms, com ressalva de que os cortes foram validados em
  talassemia maior, extrapolação razoável mas não formalmente validada
  para outras etiologias); tratamento (flebotomia vs. quelação,
  deferiprona com remoção cardíaca superior); seguimento com T2*
  seriado, sem taxa de reversibilidade numérica inventada. 12 fontes
  via NCBI e-utils (consenso AHA 2013 talassemia + EASL 2022
  hemocromatose). Nenhuma diretriz SBC localizada — declarado. Gates
  limpos. Total: 426 checklists.

## RETOMADA (30/08/2026) — nova meta do Rafael: 10.000 → 20.000 documentos científicos publicados em uma semana

Divisão de trabalho confirmada pelo Rafael: Claude (esta sessão) e Grok
geram conteúdo — sempre `pendente_revisao`, nunca autoaprovado; o
ChatGPT revisa e publica. Nenhuma mudança no regime de aprovação desta
sessão: continuo sem autoridade para marcar `revisado`/publicado.

Pedido direto: "máximo de agentes possível pra acelerar a produção" —
9 agentes paralelos dispatchados de uma vez (recorde desta janela,
antes o máximo era ~1-2 simultâneos por rodada).

## Lote 67 — concluído (SHA 3903650d) — total 94 commits

- checklist `sindrome-de-barth` — cardiomiopatia ligada ao X (gene
  TAZ/tafazina, remodelação de cardiolipina). Tétrade clássica
  (cardiomiopatia dilatada/LVNC + neutropenia + miopatia + atraso de
  crescimento), risco de morte súbita mesmo com disfunção leve
  (Spencer 2005). 11 fontes via NCBI e-utils. Total: 428 checklists.

## Lote 68 — concluído (SHA 4eb6ff0c) — total 95 commits — MÁXIMO PARALELO (9 agentes)

Rodada de máxima escala: 9 agentes de pesquisa dispatchados
simultaneamente sobre 9 gaps genuínos confirmados (canalopatias
raras, RASopatias, cardiomiopatias hereditárias raras). Todos os 9
retornaram JSON completo, verificado via NCBI e-utils, integrado em
lote único após validação individual.

- `sindrome-do-qt-curto-congenito` — SQT1/2/3, registro europeu de 53
  pacientes, CDI + quinidina (único fármaco eficaz em EEF).
- `sindrome-e-padrao-de-repolarizacao-precoce` — padrão (5,8% da
  população) vs. síndrome (31% em sobreviventes de FVI, Haissaguerre
  2008 NEJM); CDI só após evento documentado.
- `fibrilacao-ventricular-idiopatica` — diagnóstico de exclusão,
  rendimento diagnóstico de 43% com investigação completa (revisão
  sistemática de 21 estudos); algoritmo escalonado por rendimento.
- `cardiomiopatia-mitocondrial` — Kearns-Sayre (BAV progressivo,
  marca-passo profilático) e MELAS/m.3243A>G; barreiras documentadas
  ao transplante por doença sistêmica (zero de 10 candidatos
  transplantados numa série).
- `sindrome-de-costello-envolvimento-cardiovascular` — HRAS, CMH em
  ~60%, taquicardia atrial multifocal independente da CMH, protocolo
  de rastreio oncológico.
- `sindrome-noonan-multiplos-lentigos-leopard` — PTPN11 com mecanismo
  de PERDA de função fosfatase, distinto da Noonan clássica.
- `acometimento-cardiovascular-sindrome-de-cantu` — canal KATP
  (ABCC9/KCNJ8), cardiomegalia 64%/PCA 58%/derrame pericárdico 25%.
- `sindrome-de-kabuki-acometimento-cardiovascular` — KMT2D/KDM6A,
  predomínio de lesões obstrutivas esquerdas, diferenciação formal
  frente a Turner/Down/Noonan.

Nenhuma diretriz SBC/ESC/AHA específica localizada para nenhum dos 8
temas — declarado explicitamente em cada resumo. Gates (tudo-com-
tudo: broken_references=[]; content_inventory --strict: exit 0)
limpos. Total: 436 checklists.

## Lote 69 — concluído (SHA a770349a) — total 446 checklists — MÁXIMO PARALELO (10 agentes)

Segunda rodada de "máximo de agentes possível". 10 itens: 8
canalopatias/laminopatias/distrofias musculares hereditárias + 1
lacuna de rastreio (CTEPH pós-TEP agudo) + 1 cardiomiopatia
neuromuscular:

- `sindrome-de-jervell-e-lange-nielsen` — LQTS bialélica
  (KCNQ1/KCNE1) com surdez neurossensorial obrigatória, gravidade
  cardíaca maior que Romano-Ward; registro Schwartz 2006 (n=186).
- `cardiomiopatia-ataxia-friedreich` — CMH concêntrica na FRDA
  (expansão GAA em FXN); coorte EFACTS 2024.
- `acometimento-cardiovascular-neurofibromatose-tipo-1` —
  vasculopatia própria da NF1, hipertensão secundária
  (renovascular/feocromocitoma), diferenciação molecular do
  fenótipo NF1-Noonan/Watson (variante em NF1, não em genes
  Ras-MAPK clássicos).
- `sindrome-de-timothy` — LQT8 (CACNA1C/Cav1.2), bloqueio AV
  funcional 2:1, registro internacional 2024 com mortalidade de 45%.
- `rastreio-cteph-pos-tep-agudo` — lacuna de rastreio na janela de
  3-6 meses pós-TEP agudo, distinta do verbete geral de CTEPH já
  em tramitação no PR #714 (operabilidade/endarterectomia); ~25%
  dos casos de CTEPH não têm TEP agudo prévio reconhecido — limite
  estrutural declarado explicitamente.
- `sindrome-de-alstrom-acometimento-cardiovascular` — ciliopatia
  ultrarrara (ALMS1), padrão bimodal de cardiomiopatia dilatada
  (infância precoce e adolescência/adulto).
- `cardiomiopatia-duchenne-becker-vigilancia-manejo` — rastreio e
  manejo farmacológico padrão (IECA precoce, eplerenona,
  corticoterapia), escopo explicitamente separado do artigo
  existente sobre deramiocel/HOPE-2/HOPE-3.
- `acometimento-cardiaco-distrofia-emery-dreifuss` — laminopatia
  (EMD/LMNA), doença de condução e risco de morte súbita mesmo com
  FEVE preservada (Classe IIa/C para CDI em mutação LMNA, ESC 2021).
- `acometimento-cardiaco-distrofia-miotonica-tipo-1` — doença de
  condução desproporcional à função sistólica na DM1; segunda
  causa de morte após insuficiência respiratória (Groh 2008, Wahbi
  2012).
- `doenca-de-danon` — deficiência de LAMP2 (defeito
  autofágico-lisossômico estrutural, não enzimático), assimetria
  de gravidade ligada ao sexo, pré-excitação WPW por via
  fascículo-ventricular (fenocópia de HCM).

Nenhuma diretriz SBC/ESC/AHA específica localizada para nenhum dos
10 temas — declarado explicitamente em cada resumo. Gates (tudo-
com-tudo: broken_references=[]; content_inventory --strict: exit 0)
limpos. Total: 446 checklists.

Trabalho lateral concluído nesta janela (branch própria, PR aberto,
não bloqueia esta produção): correção de 3 anomalias de tema fora
do vocabulário canônico do motor "Tudo com Tudo" — PR #709.

## Lote 70 (planejado)

Continuando no ritmo máximo de paralelismo, em tempo indeterminado,
até ordem de pausa do Rafael. Meta compartilhada: 20.000 documentos
científicos publicados até 06/09/2026 (Claude+Grok geram
pendente_revisao; ChatGPT revisa e publica — divisão de trabalho
confirmada em 30/08). Auditoria de próximos gaps com o procedimento
padrão (JSONs + `content/**/*.md` + `gh pr list` + verificação de
que main não avançou com conteúdo de outras faixas desde o último
fetch).

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_
