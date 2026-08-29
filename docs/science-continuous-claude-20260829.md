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
