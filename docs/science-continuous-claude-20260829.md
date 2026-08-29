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
- `fenocopias-glicogenicas-da-cardiomiopatia-hipertrofica-danon-e-prkag2` — despachado, ainda em execução (agente a490ae8b455a6fb6b).

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

_(atualizado incrementalmente a cada lote — sem relatório longo, só checkpoint)_
