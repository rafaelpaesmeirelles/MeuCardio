---
title: "Sessão Grok — produção científica contínua 29/08/2026"
slug: science-continuous-grok-20260829
---

# Sessão Grok — produção científica contínua 29/08/2026

**Status: ENCERRADA NO LOTE 77.** Conteúdo reconciliado e preparado para revisão editorial em 30/08/2026.

Branch: `grok/science-continuous-prevalence-gaps-20260829`
Base: `origin/main` SHA `36a642e` (“ops: disparar deploy emergencial da leitura em português interna”)
Escopo: conteúdo científico original, `review_status: revisado`, `fonte_producao: grok`. Sem merge na `main`, sem deploy, sem frontend, sem CI, sem Docker.

Território: DAC, IC, hipertensão/prevenção, intensiva/emergência, TEV/PE, cardio-oncologia/sistêmico. Sem invadir arritmias, congênitas, pediatria, valvopatias, aorta ou imagem avançada salvo lacuna crítica.

Sessão overnight da mesma data (`docs/grok-science-overnight-20260829.md`) **já importada em main** — não duplicar IC FEi/SUMMIT/ferro, VSA/COVADIS/CMD, tipo 2, Wellens, 0/1 h, DAPT genérico, REDUCE-AMI, SELECT, SGLT2-CKD, Lp(a), colchicina, dispneia, HAS secundária, EAP, pós-ROSC, dor torácica.

PRs/abertos deliberadamente não duplicados (lista overnight + varredura 29/08): #713 emergência hipertensiva, #697 MINOCA/SCAD, #692 cardiorrenal, #684 obesidade, #700 amiloidose AL, #719 sarcoidose, #594 IC avançada, #590 choque, #597 HAS resistente, #570 dislipidemia, #572 diabetes. Busca de PRs por TWILIGHT/HOST-EXAM/DETO2X/REBOOT/bempedoico/hiponatremia: **sem colisão temática**.

## Método de citação

PMID/DOI só depois de esearch/efetch ou Europe PMC. Colisões já observadas em sessões anteriores (PMID 31566344 não é TWILIGHT; 34019809 não é HOST-EXAM) — desta sessão os âncoras foram:

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| TWILIGHT | 31556978 | 10.1056/NEJMoa1908419 | PubMed efetch 29/08/2026 |
| HOST-EXAM | 34010616 | 10.1016/S0140-6736(21)01063-1 | PubMed efetch 29/08/2026 |
| CLEAR Outcomes | 36876740 | 10.1056/NEJMoa2215024 | Europe PMC + abstract |
| REBOOT-CNIC | 40888702 | 10.1056/NEJMoa2504735 | Europe PMC + abstract |
| DETO2X-AMI | 28844200 | 10.1056/NEJMoa1706222 | Europe PMC + abstract |
| AVOID (contexto) | 26002889 | 10.1161/CIRCULATIONAHA.114.014494 | PubMed abstract |

Nada promovido a `revisado`. Nenhum JSON monolítico (`evidencias/metadados.json`, estudos, checklists, material-paciente) tocado. Na preparação final, somente os 332 caminhos inéditos foram importados; 32 caminhos colidentes do bundle histórico foram preservados conforme a `main`.

## Lote 1 — 7 markdown (29/08/2026)

**Doença coronariana**
- `twilight-ticagrelor-monoterapia-apos-3-meses-de-dapt` + `fluxograma-twilight-aspirina-drop-aos-3-meses`
- `reboot-cnic-betabloqueador-pos-iam-feve-maior-que-40` (complementa REDUCE-AMI e as IPD; não as substitui)
- `deto2x-ami-oxigenio-rotineiro-no-iam-sem-hipoxemia` + `fluxograma-oxigenio-no-iam-suspeito`
- `host-exam-clopidogrel-versus-aspirina-monoterapia-manutencao-pos-pci` (complementa SMART-CHOICE 3)

**Prevenção e lipídios**
- `quando-usar-acido-bempedoico-apos-clear-outcomes` (protocolo de decisão; dump do ensaio permanece no combinado IMPROVE-IT/CLEAR/ORION)

## Itens retidos (não inventados)

- % Kaplan-Meier do primário do REBOOT (abstract só traz taxas/1.000 a)
- Componentes isolados do HOST-EXAM (não estão no abstract)
- Critérios operacionais de “alto risco” do TWILIGHT (PDF não relido)
- Classe ESC 2023 de oxigênio (tabela não relida)
- Redução de morte CV / morte total / AVC pelo CLEAR Outcomes (**ausente** no ensaio)
- HOST-EXAM Extended e post hoc 2025–2026
- Subgrupo DETO2X-DPOC
- Hiponatremia na IC (lote seguinte; EVEREST já existe)

## Tudo com Tudo

Arestas clínicas por `document_slug` / menção explícita aos documentos da casa. Sem aresta fictícia. Sem verbete novo em `doencas/metadados.json`.

## Lote 2 — 3 markdown (29/08/2026)

**Insuficiência cardíaca**
- `hiponatremia-na-insuficiencia-cardiaca-abordagem-pratica` + `fluxograma-hiponatremia-na-ic`
  (SALT-1/2 PMID 17105757; TACTICS-HF PMID 27654854; EVEREST já na casa; Spasovski só pela definição Na <135; tabela de bolus 3% NÃO relida)

**Doença coronariana**
- `flower-mi-ffr-versus-angiografia-na-revascularizacao-completa-do-stemi` (PMID 33999545; complementa COMPLETE e DANAMI-3-PRIMULTI)

## PMIDs lote 2

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| SALT-1/SALT-2 | 17105757 | 10.1056/NEJMoa065181 | PubMed efetch |
| TACTICS-HF | 27654854 | 10.1016/j.jacc.2016.09.004 | Europe PMC + esummary (JACC 2017;69(11):1399-1406) |
| FLOWER-MI | 33999545 | 10.1056/NEJMoa2104650 | Europe PMC + esummary (NEJM 2021;385(4):297-308) |
| Spasovski (definição) | 24569496 | 10.1093/ndt/gfu040 | Europe PMC — só definição |

## Itens retidos no lote 2

- Variação em mmol/L do Na no SALT (não está no abstract)
- Bolus de salina a 3% e limites de correção da diretriz europeia (tabela não relida)
- Volume/issue do FLOWER no primeiro rascunho: corrigido para 385(4) via esummary

## Lote 3 — 4 markdown (29/08/2026)

**Doença coronariana**
- `ischemia-ckd-estrategia-invasiva-vs-conservadora-na-drc-avancada` (PMID 32227756; irmão do ISCHEMIA)
- `dapa-mi-dapagliflozina-pos-iam-sem-diabetes-nem-ic` (PMID 38320489; win ratio metabólico, HR 0,95 no composto CV; não misturar com EMPACT-MI)
- `preserve-amacing-profilaxia-de-nefropatia-por-contraste` + `fluxograma-profilaxia-de-nefropatia-por-contraste` (PMID 29130810, 28233565)

## PMIDs lote 3

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ISCHEMIA-CKD | 32227756 | 10.1056/NEJMoa1915925 | Europe PMC + esummary (NEJM 2020;382(17):1608-1618) |
| DAPA-MI | 38320489 | 10.1056/EVIDoa2300286 | Europe PMC + esummary (NEJM Evid 2024;3(2)) |
| PRESERVE | 29130810 | 10.1056/NEJMoa1710933 | Europe PMC + esummary (NEJM 2018;378(7):603-614) |
| AMACING | 28233565 | 10.1016/S0140-6736(17)30057-0 | PubMed efetch (Lancet 2017;389(10076):1312-1322) |

## Itens retidos no lote 3

- TFGe de inclusão do ISCHEMIA-CKD (não está no abstract)
- % isoladas de AVC e diálise no ISCHEMIA-CKD (só HR)
- Classe ESC/KDIGO de profilaxia de contraste
- TICO / STOPDAPT-2 (DAPT já coberto por TWILIGHT/HOST-EXAM/ULTIMATE nesta sessão)

## Lote 4 — 7 markdown (29/08/2026)

**Doença coronariana — escolha de P2Y12 e ancestral da DAC estável**
- `plato-ticagrelor-versus-clopidogrel-na-sca` (PMID 19717846)
- `triton-timi-38-prasugrel-versus-clopidogrel-na-sca-com-pci` (PMID 17982182)
- `isar-react-5-prasugrel-versus-ticagrelor-na-sca` (PMID 31475799; aberto; timing do ataque não relido no PDF)
- `accoast-pretratamento-com-prasugrel-no-nste-acs` (PMID 23991622; % do primário ausente no abstract)
- `themis-ticagrelor-na-dac-estavel-com-diabetes` (PMID 31475798; composto de irreversible harm truncado — não reproduzido)
- `courage-pci-versus-terapia-medica-na-dac-estavel` (PMID 17387127; ancestral do ISCHEMIA)
- `fluxograma-escolha-do-p2y12-na-sca`

Retidos neste lote: DOSE/CARRESS (já em estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada); BOX (já em metas-de-pressao-arterial-e-de-oxigenacao-pos-parada); PEGASUS (só menção no complemento de DAPT — fila); TICO (TWILIGHT cobre o corte de 3 meses).

## PMIDs lote 4

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| PLATO | 19717846 | 10.1056/NEJMoa0904327 | PubMed efetch (NEJM 2009;361(11):1045-57) |
| TRITON-TIMI 38 | 17982182 | 10.1056/NEJMoa0706482 | PubMed efetch (NEJM 2007;357(20):2001-15) |
| ISAR-REACT 5 | 31475799 | 10.1056/NEJMoa1908973 | Europe PMC + esummary (NEJM 2019;381(16):1524-1534) |
| ACCOAST | 23991622 | 10.1056/NEJMoa1308075 | Europe PMC + esummary (NEJM 2013;369(11):999-1010) |
| THEMIS | 31475798 | 10.1056/NEJMoa1908077 | PubMed efetch (NEJM 2019;381(14):1309-1320) |
| COURAGE | 17387127 | 10.1056/NEJMoa070829 | Europe PMC + esummary (NEJM 2007;356(15):1503-16) |

## Lote 5 — 3 markdown (29/08/2026)

- `pegasus-timi-54-ticagrelor-apos-mais-de-um-ano-do-iam` (PMID 25773268) + `fluxograma-ticagrelor-alem-de-12-meses-pegasus-versus-themis`
- `andromeda-shock-enchimento-capilar-versus-lactato-no-choque-septico` (PMID 30772908; primário P=0,06 — **não** redução de mortalidade)

## PMIDs lote 5

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| PEGASUS-TIMI 54 | 25773268 | 10.1056/NEJMoa1500857 | PubMed efetch (NEJM 2015;372(19):1791-800) |
| ANDROMEDA-SHOCK | 30772908 | 10.1001/jama.2019.0071 | Europe PMC + esummary (JAMA 2019;321(7):654-664) |

## Lote 6 — 2 markdown (29/08/2026)

- `years-algoritmo-simplificado-para-excluir-tep-suspeito` (PMID 28549662; coorte, não RCT) + `fluxograma-years-suspeita-de-tep-estavel`
- YEARS da gestação já existe (`diagnostico-de-tep-na-gestante-years-adaptado-e-a-estrategia-do-ct-pe-pregnancy`) — não duplicado

## PMIDs lote 6

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| YEARS | 28549662 | 10.1016/S0140-6736(17)30885-1 | PubMed efetch (Lancet 2017;390(10091):289-297) |

## Lote 7 — 11 markdown (29/08/2026)

**Doença coronariana**
- `atlantic-ticagrelor-pre-hospitalar-no-iamcsst` (PMID 25175921; coprimários sem diferença; percentuais dos coprimários NÃO no abstract; trombose de stent é secundária)
- `talos-ami-desescalonamento-nao-guiado-ticagrelor-para-clopidogrel` (PMID 34627490; Coreia, aberto; primário puxado por sangramento; isquemia P=0,15)
- `heat-ppci-heparina-versus-bivalirudina-na-icp-primaria` (PMID 25002178; centro único; trombose de stent isolada NÃO no abstract)
- `validate-swedeheart-bivalirudina-versus-heparina-monoterapia-no-iam` (PMID 28844201; P=0,54; trombose de stent P=0,09 — não vender)
- `stopdapt-2-dapt-de-1-mes-seguida-de-clopidogrel-monoterapia` (PMID 31237644; Japão; fração SCA NÃO no abstract; autores pedem outras populações)
- `fluxograma-heparina-versus-bivalirudina-na-icp-do-iam`

**Prevenção e lipídios**
- `arrive-aspirina-em-prevencao-primaria-risco-moderado` (PMID 30158069; não confundir com registro AVEIR ARRIVE)
- `fluxograma-aspirina-em-prevencao-primaria-ascend-aspree-arrive`

**Diabetes e cardiologia**
- `canvas-canagliflozina-eventos-cardiovasculares-renais-e-amputacao` (PMID 28605608; renal NÃO significativo na sequência pré-especificada; IC/morte CV isoladas NÃO no abstract)

**Terapia intensiva**
- `classic-restricao-de-fluido-intravenoso-no-choque-septico` (PMID 35709019; P=0,96)
- `65-trial-hipotensao-permissiva-no-idoso-com-choque-vasodilatador` (PMID 32049269; primário P=0,15; OR ajustado NÃO é o primário)

Colisões deliberadamente não duplicadas: MATRIX/HORIZONS (arquivo próprio), ASPREE, ASCEND, EMPA-REG+DECLARE, VERTIS, ANDROMEDA-SHOCK, BOX, SOAP-II, fluxograma de duração da DAPT (desescalonamento guiado), TWILIGHT/HOST-EXAM/MASTER-DAPT/ULTIMATE-DAPT.

## PMIDs lote 7

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ATLANTIC | 25175921 | 10.1056/NEJMoa1407024 | PubMed efetch (NEJM 2014;371(11):1016-27) |
| TALOS-AMI | 34627490 | 10.1016/S0140-6736(21)01445-8 | Europe PMC + esummary (Lancet 2021;398(10308):1305-1316) |
| HEAT-PPCI | 25002178 | 10.1016/S0140-6736(14)60924-7 | PubMed efetch (Lancet 2014;384(9957):1849-1858) |
| VALIDATE-SWEDEHEART | 28844201 | 10.1056/NEJMoa1706443 | PubMed efetch (NEJM 2017;377(12):1132-1142) |
| STOPDAPT-2 | 31237644 | 10.1001/jama.2019.8145 | PubMed efetch + Europe PMC (JAMA 2019;321(24):2414-2427); ArticleId EuroIntervention no XML ignorado |
| ARRIVE | 30158069 | 10.1016/S0140-6736(18)31924-X | Europe PMC + esummary (Lancet 2018;392(10152):1036-1046) |
| CLASSIC | 35709019 | 10.1056/NEJMoa2202707 | PubMed efetch (NEJM 2022;386(26):2459-2470) |
| CANVAS | 28605608 | 10.1056/NEJMoa1611925 | PubMed efetch (NEJM 2017;377(7):644-657) |
| 65-trial | 32049269 | 10.1001/jama.2020.0930 | Europe PMC + esummary (JAMA 2020;323(10):938-949) |

## Lote 8 — 9 markdown (29/08/2026)

**Doença coronariana**
- `tropical-acs-desescalonamento-guiado-por-funcao-plaquetaria` (PMID 28855078; não inferior; superioridade P=0,12; BARC P=0,23)
- `prague-18-prasugrel-versus-ticagrelor-na-icp-primaria` (PMID 27576777; futilidade; ICs largos; 1 ano NÃO relido)
- `compare-acute-ffr-guiada-revascularizacao-completa-no-stemi` (PMID 28317428; composto puxado por revascularização; regra dos 45 d)
- `prami-pci-preventiva-de-nao-culpada-no-iamcsst` (PMID 23991625; n=465, parado cedo; morte cardíaca IC cruza 1)
- `fluxograma-desescalonamento-dapt-talos-tropical-stopdapt`
- `fluxograma-revascularizacao-completa-no-stemi-prami-compare-complete`

**Diabetes e cardiologia**
- `credence-canagliflozina-na-nefropatia-diabetica` (PMID 30990260; amputação/fratura sem diferença neste abstract — não copiar CANVAS)

**Terapia intensiva**
- `sepsispam-alvo-de-pam-65-versus-80-no-choque-septico` (PMID 24635770; FA e TRS sem percentual no abstract)

**Prevenção e lipídios**
- `hope-3-rosuvastatina-e-pressao-em-risco-intermediario` (PMID 27040132 e 27039945; braço isolado de PA PMID 27041480 NÃO relido; homônimo Duchenne)

## PMIDs lote 8

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| TROPICAL-ACS | 28855078 | 10.1016/S0140-6736(17)32155-4 | Europe PMC + esummary (Lancet 2017;390(10104):1747-1757) |
| PRAGUE-18 | 27576777 | 10.1161/CIRCULATIONAHA.116.024823 | Europe PMC + esummary (Circulation 2016;134(21):1603-1612) |
| SEPSISPAM | 24635770 | 10.1056/NEJMoa1312173 | Europe PMC + esummary (NEJM 2014;370(17):1583-93) |
| CREDENCE | 30990260 | 10.1056/NEJMoa1811744 | PubMed efetch (NEJM 2019;380(24):2295-2306) |
| COMPARE-ACUTE | 28317428 | 10.1056/NEJMoa1701067 | PubMed efetch (NEJM 2017;376(13):1234-1244) |
| PRAMI | 23991625 | 10.1056/NEJMoa1305520 | Europe PMC + esummary (NEJM 2013;369(12):1115-23) |
| HOPE-3 estatina | 27040132 | 10.1056/NEJMoa1600176 | Europe PMC + esummary (NEJM 2016;374(21):2021-31) |
| HOPE-3 combinação | 27039945 | 10.1056/NEJMoa1600177 | Europe PMC + esummary (NEJM 2016;374(21):2032-43) |

## Lote 9 — 8 markdown (29/08/2026)

**Terapia intensiva**
- `clovers-fluido-restritivo-versus-liberal-na-hipotensao-por-sepse` (PMID 36688507; P=0,61)
- `censer-noradrenalina-precoce-no-choque-septico` (PMID 30704260; primário hemodinâmico; morte 28 d P=0,15 — não vender mortalidade)
- `fluxograma-volume-e-vasopressor-na-sepse-classic-clovers-censer`

**Hipertensão**
- `hope-3-braco-de-pressao-candesartana-hctz-no-risco-intermediario` (PMID 27041480; primário neutro; subgrupo PAS >143,5 sem taxas no abstract)

**Doença coronariana**
- `ephesus-eplerenona-apos-iam-com-disfuncao-ventricular` (PMID 12668699; FEVE/janela horária NÃO no abstract)
- `valiant-valsartana-versus-captopril-pos-iam-com-ic` (PMID 14610160; combinação só adiciona AE; doses-alvo NÃO no abstract)
- `topic-troca-de-p2y12-potente-para-clopidogrel-no-mes-1-pos-sca` (PMID 28510646; centro único; isquemia sem % no abstract)
- `beautiful-ivabradina-na-dac-estavel-com-disfuncao-sistolica` (PMID 18757088; primário HR 1,00; secundários de subgrupo FC ≥70)

## PMIDs lote 9

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| CLOVERS | 36688507 | 10.1056/NEJMoa2212663 | Europe PMC + esummary (NEJM 2023;388(6):499-510) |
| HOPE-3 PA | 27041480 | 10.1056/NEJMoa1600175 | Europe PMC + esummary (NEJM 2016;374(21):2009-20) |
| EPHESUS | 12668699 | 10.1056/NEJMoa030207 | Europe PMC + esummary (NEJM 2003;348(14):1309-21) |
| VALIANT | 14610160 | 10.1056/NEJMoa032292 | Europe PMC + esummary (NEJM 2003;349(20):1893-906) |
| TOPIC | 28510646 | 10.1093/eurheartj/ehx175 | Europe PMC + esummary (Eur Heart J 2017;38(41):3070-3078) |
| BEAUTIFUL | 18757088 | 10.1016/S0140-6736(08)61170-8 | Europe PMC + esummary (Lancet 2008;372(9641):807-16) |
| CENSER | 30704260 | 10.1164/rccm.201806-1034OC | Europe PMC + esummary (Am J Respir Crit Care Med 2019;199(9):1097-1105) |

## Lote 10 — 5 markdown (29/08/2026)

**Doença coronariana**
- `albatross-mra-precoce-no-iam-sem-exigir-ic` (PMID 27102506; primário neutro; subgrupo IAMCSST exploratório — não vender)
- `smart-date-dapt-6-versus-12-meses-na-sca` (PMID 29544699; NI cumprida mas mais IAM; autores não concluem segurança; ~80% clopidogrel)
- `euromax-bivalirudina-no-transporte-para-icp-primaria` (PMID 24171490; menos sangramento, mais trombose aguda; morte NS; GPI opcional no controle)
- `cvlprit-revascularizacao-completa-na-internacao-do-stemi` (PMID 25766941; n=296; morte/IAM NS; COMPLETE é o n pedido)

**Prevenção e lipídios**
- `hope-ramipril-em-alto-risco-sem-ic-nem-fe-baixa` (PMID 10639539; não confundir com HOPE-3 nem Duchenne; vitamina E não relida)

CORAL/ASTRAL já cobertos (`estenose-aterosclerotica-de-arteria-renal-o-ensaio-coral-e-o-fim-do-stent-rotineiro`).

## PMIDs lote 10

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ALBATROSS | 27102506 | 10.1016/j.jacc.2016.02.033 | Europe PMC + esummary (JACC 2016;67(16):1917-27) |
| SMART-DATE | 29544699 | 10.1016/S0140-6736(18)30493-8 | PubMed efetch (Lancet 2018;391(10127):1274-1284) |
| EUROMAX | 24171490 | 10.1056/NEJMoa1311096 | Europe PMC + esummary (NEJM 2013;369(23):2207-17) |
| CvLPRIT | 25766941 | 10.1016/j.jacc.2014.12.038 | PubMed efetch (JACC 2015;65(10):963-72) |
| HOPE | 10639539 | 10.1056/NEJM200001203420301 | Europe PMC + esummary (NEJM 2000;342(3):145-53) |

## Lote 11 — 9 markdown (29/08/2026)

**Doença coronariana**
- `taste-total-tromboaspiracao-rotineira-no-iamcsst` (TASTE PMID 23991656; TOTAL PMID 25853743; rotina não reduz eventos; TOTAL aumenta AVC 30 d) + `fluxograma-tromboaspiracao-rotineira-no-iamcsst`
- `cure-clopidogrel-no-nste-acs` (PMID 11519503; chão da DAPT no NSTE; PLATO compara ticagrelor a este clopidogrel)
- `tico-ticagrelor-monoterapia-apos-3-meses-na-sca` (PMID 32543684; só SCA, Coreia; MACCE P=0,09; taxas menores que o esperado)
- `atlas-acs-2-rivaroxabana-apos-sca` (PMID 22077192; morte só na 2,5 mg 2×; ICH sobe; não é COMPASS)
- `danami-2-transferencia-para-icp-versus-fibrinolise` (PMID 12930925; ganho por reinfarto; morte NS; 96% ≤2 h)
- `stream-estrategia-farmacoinvasiva-quando-icp-atrasa` (PMID 23473396; primário NS; ICH 1,0% vs 0,2% antes da emenda)
- `global-leaders-ticagrelor-monoterapia-apos-1-mes` (PMID 30166073; superioridade falhou P=0,073)

**Insuficiência cardíaca**
- `corona-rosuvastatina-na-ic-sistolica-isquemica` (PMID 17984166; primário HR 0,92 P=0,12; morte NS; internação CV secundária)

VISION/MINS já cobertos no perioperatório — não duplicar.

## PMIDs lote 11

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| TASTE | 23991656 | 10.1056/NEJMoa1308789 | Europe PMC + esummary (NEJM 2013;369(17):1587-97) |
| TOTAL | 25853743 | 10.1056/NEJMoa1415098 | Europe PMC + esummary (NEJM 2015;372(15):1389-98) |
| CURE | 11519503 | 10.1056/NEJMoa010746 | Europe PMC + esummary (NEJM 2001;345(7):494-502) |
| TICO | 32543684 | 10.1001/jama.2020.7580 | PubMed efetch (JAMA 2020;323(23):2407-2416) |
| CORONA | 17984166 | 10.1056/NEJMoa0706201 | PubMed efetch (NEJM 2007;357(22):2248-61) |
| ATLAS ACS 2–TIMI 51 | 22077192 | 10.1056/NEJMoa1112277 | PubMed efetch (NEJM 2012;366(1):9-19) |
| DANAMI-2 | 12930925 | 10.1056/NEJMoa025142 | Europe PMC + esummary (NEJM 2003;349(8):733-42) |
| STREAM | 23473396 | 10.1056/NEJMoa1301092 | Europe PMC + esummary (NEJM 2013;368(15):1379-87) |
| GLOBAL LEADERS | 30166073 | 10.1016/S0140-6736(18)31858-0 | Europe PMC + esummary (Lancet 2018;392(10151):940-949) |

## Lote 12 — 6 markdown (29/08/2026)

**Insuficiência cardíaca**
- `gissi-hf-rosuvastatina-na-ic-cronica` (PMID 18757089; morte HR 1,00) + `gissi-hf-omega-3-na-ic-cronica` (PMID 18757090; morte HR 0,91; NNT 56) + `fluxograma-estatina-e-omega-3-na-ic-corona-gissi-hf`

**Doença coronariana**
- `appraise-2-apixabana-apos-sca` (PMID 21780946; interrompido; TIMI maior HR 2,59; isquemia NS)

**Hipertensão**
- `life-losartana-versus-atenolol-na-has-com-hve` (PMID 11937178; composto por AVC; IAM NS)

**Terapia intensiva**
- `tricc-transfusao-restritiva-versus-liberal-no-critico` (PMID 9971864; exceção SCA; MINT é o capítulo do IAM)

PRECISION NSAID já existe (`anti-inflamatorios-nao-esteroidais-e-risco-cardiovascular-o-ensaio-precision`) — não duplicado.

## PMIDs lote 12

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| GISSI-HF rosuvastatina | 18757089 | 10.1016/S0140-6736(08)61240-4 | Europe PMC + esummary (Lancet 2008;372(9645):1231-9) |
| GISSI-HF n-3 PUFA | 18757090 | 10.1016/S0140-6736(08)61239-8 | Europe PMC + esummary (Lancet 2008;372(9645):1223-30) |
| APPRAISE-2 | 21780946 | 10.1056/NEJMoa1105819 | Europe PMC + esummary (NEJM 2011;365(8):699-708) |
| LIFE | 11937178 | 10.1016/S0140-6736(02)08089-3 | Europe PMC + esummary (Lancet 2002;359(9311):995-1003) |
| TRICC | 9971864 | 10.1056/NEJM199902113400601 | Europe PMC + esummary (NEJM 1999;340(6):409-17) |

## Lote 13 — 10 markdown (29/08/2026)

**Doença coronariana — clopidogrel, DAPT longa, fondaparinux**
- `commit-clopidogrel-no-iam-com-supra` (PMID 16271642; sem ataque; morte 7,5% vs 8,1%)
- `current-oasis-7-dose-dupla-de-clopidogrel-e-aas` (PMID 20818903; primário P=0,30; trombose de stent secundária)
- `dapt-estudo-12-versus-30-meses-apos-stent-farmacologico` (PMID 25399658; morte 2,0% vs 1,5% P=0,05 — não esconder)
- `oasis-5-fondaparinux-versus-enoxaparina-na-sca` (PMID 16537663; NI isquêmica; sangramento HR 0,52)
- `oasis-6-fondaparinux-no-iamcsst` (PMID 16537725; sem ganho na ICP primária)
- `fluxograma-fondaparinux-na-sca-oasis-5-e-oasis-6`

**Prevenção e lipídios**
- `prove-it-timi-22-atorvastatina-80-versus-pravastatina-40-pos-sca` (PMID 15007110)
- `tnt-atorvastatina-80-versus-10-na-dac-estavel` (PMID 15755765; mortalidade total igual)
- `fluxograma-intensidade-de-estatina-apos-sca-e-na-dac-estavel`

**Hipertensão**
- `value-valsartana-versus-anlodipino-na-has-de-alto-risco` (PMID 15207952; PA desigual; composto P=0,49)

Colisões evitadas: CURE (lote 11), PEGASUS, TWILIGHT, STOPDAPT-2, ALLHAT/ASCOT-BPLA combinado, 4S/WOSCOPS/CTT, IMPROVE-IT/CLEAR, MATRIX/HORIZONS.

## PMIDs lote 13

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| COMMIT | 16271642 | 10.1016/S0140-6736(05)67660-X | Europe PMC (Lancet 2005;366(9497):1607-1621) |
| CURRENT-OASIS 7 | 20818903 | 10.1056/NEJMoa0909475 | Europe PMC (NEJM 2010;363(10):930-942) |
| DAPT (Mauri) | 25399658 | 10.1056/NEJMoa1409312 | Europe PMC (NEJM 2014;371(23):2155-2166) |
| OASIS-5 | 16537663 | 10.1056/NEJMoa055443 | Europe PMC (NEJM 2006;354(14):1464-1476) |
| OASIS-6 | 16537725 | 10.1001/jama.295.13.joc60038 | PubMed efetch (JAMA 2006;295(13):1519-1530) |
| VALUE | 15207952 | 10.1016/S0140-6736(04)16451-9 | PubMed efetch (Lancet 2004;363(9426):2022-2031) |
| PROVE-IT TIMI 22 | 15007110 | 10.1056/NEJMoa040583 | Europe PMC (NEJM 2004;350(15):1495-1504) |
| TNT | 15755765 | 10.1056/NEJMoa050461 | Europe PMC (NEJM 2005;352(14):1425-1435) |

Retidos: trombose de cateter OASIS (não no abstract); componentes isolados VALUE/PROVE-IT; morte CV isolada TNT; braço metoprolol do COMMIT.

## Lote 14 — 13 markdown (29/08/2026)

**Doença coronariana — lise**
- `clarity-timi-28-clopidogrel-com-fibrinolise-no-iamcsst` (PMID 15758000; ≤75 anos, ataque 300 mg)
- `extract-timi-25-enoxaparina-versus-hnf-com-fibrinolise-no-iamcsst` (PMID 16537665; morte P=0,11; líquido P<0,001)
- `fluxograma-antitrombotico-adjunto-a-lise-no-iamcsst`

**Prevenção e lipídios**
- `ideal-atorvastatina-80-versus-sinvastatina-20-apos-iam` (PMID 16287954; primário P=0,07)
- `a-to-z-sinvastatina-precoce-intensa-versus-tardia-apos-sca` (PMID 15337732; primário P=0,14; miopatia 0,4% em 80 mg)
- `cards-atorvastatina-10-na-prevencao-primaria-do-diabetes-tipo-2` (PMID 15325833; morte P=0,059)
- `sparcl-atorvastatina-80-apos-avc-ou-ait-sem-dac` (PMID 16899775; hemorrágico 55 vs 33; morte P=0,98)
- `hps-sinvastatina-40-em-alto-risco-independentemente-do-ldl` (PMID 12114036; morte 12,9% vs 14,7%)
- `ascot-lla-atorvastatina-10-no-hipertenso-com-colesterol-nao-alto` (PMID 12686036; morte P=0,16)

**Insuficiência cardíaca**
- `charm-added-candesartana-sobre-ieca-na-icfer` (PMID 13678869; **não** licença de duplo bloqueio hoje)
- `charm-alternative-candesartana-na-icfer-intolerante-a-ieca` (PMID 13678870)

**Hipertensão / intensiva**
- `hot-alvo-diastolico-e-aas-75-mg-na-has` (PMID 9635947)
- `triss-limiar-7-versus-9-g-dl-no-choque-septico` (PMID 25270275; P=0,44)

Colisões evitadas: JUPITER, 4S/WOSCOPS/CTT, FOURIER/ODYSSEY, REDUCE-IT/STRENGTH, FAME-2, FREEDOM, COMPASS, CHARM-Preserved/TOPCAT, RALES/EMPHASIS, CIBIS-II/MERIT-HF/COPERNICUS, PARADIGM-HF, TRICC, MINT, ASCOT-BPLA combinado, MATRIX/HORIZONS.

## PMIDs lote 14

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| CLARITY-TIMI 28 | 15758000 | 10.1056/NEJMoa050522 | PubMed efetch (NEJM 2005;352(12):1179-1189) |
| ExTRACT-TIMI 25 | 16537665 | 10.1056/NEJMoa060898 | PubMed efetch (NEJM 2006;354(14):1477-1488) |
| IDEAL | 16287954 | 10.1001/jama.294.19.2437 | PubMed efetch (JAMA 2005;294(19):2437-2445) |
| A to Z fase Z | 15337732 | 10.1001/jama.292.11.1307 | PubMed efetch (JAMA 2004;292(11):1307-1316) |
| CARDS | 15325833 | 10.1016/S0140-6736(04)16895-5 | Europe PMC (Lancet 2004;364(9435):685-696) |
| SPARCL | 16899775 | 10.1056/NEJMoa061894 | Europe PMC (NEJM 2006;355(6):549-559) |
| HPS | 12114036 | 10.1016/S0140-6736(02)09327-3 | PubMed/Europe PMC (Lancet 2002;360(9326):7-22) |
| CHARM-Added | 13678869 | 10.1016/S0140-6736(03)14283-3 | PubMed efetch (Lancet 2003;362(9386):767-771) |
| CHARM-Alternative | 13678870 | 10.1016/S0140-6736(03)14284-5 | Europe PMC (Lancet 2003;362(9386):772-776) |
| ASCOT-LLA | 12686036 | 10.1016/S0140-6736(03)12948-0 | Europe PMC (Lancet 2003;361(9364):1149-1158) |
| HOT | 9635947 | 10.1016/S0140-6736(98)04311-6 | PubMed efetch (Lancet 1998;351(9118):1755-1762) |
| TRISS | 25270275 | 10.1056/NEJMoa1406617 | Europe PMC (NEJM 2014;371(15):1381-1391) |

Volume/issue via Crossref quando Europe PMC omitiu revista. PMIDs memorizados errados (CLARITY 16282177 = CANPAP; SPARCL 16880401 = fisiologia) **não** usados.

## Lote 16 — 6 markdown (29/08/2026)

**IECA pós-IAM e DAC estável**
- `save-captopril-na-disfuncao-ventricular-assintomatica-pos-iam` (PMID 1386652; morte 20% vs 25%)
- `aire-ramipril-na-ic-clinica-pos-iam` (PMID 8104270; morte 17% vs 23%; DOI ausente no MEDLINE)
- `trace-trandolapril-na-disfuncao-ventricular-pos-iam` (PMID 7477219; reinfarto NS)
- `europa-perindopril-8-mg-na-dac-estavel-sem-ic` (PMID 13678872)
- `peace-trandolapril-na-dac-estavel-com-fe-preservada` (PMID 15531767; P=0,43)
- `fluxograma-ieca-pos-iam-e-na-dac-estavel-save-aire-trace-europa-peace`

HOPE já na casa. Não misturar PEACE (FE ~58%) com TRACE (FE ≤35%).

## PMIDs lote 16

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| SAVE | 1386652 | 10.1056/NEJM199209033271001 | PubMed efetch (NEJM 1992;327(10):669-677) |
| AIRE | 8104270 | (ausente no MEDLINE) | PubMed efetch (Lancet 1993;342(8875):821-828) |
| TRACE | 7477219 | 10.1056/NEJM199512213332503 | PubMed efetch (NEJM 1995;333(25):1670-1676) |
| EUROPA | 13678872 | 10.1016/S0140-6736(03)14286-9 | PubMed efetch (Lancet 2003;362(9386):782-788) |
| PEACE | 15531767 | 10.1056/NEJMoa042739 | PubMed efetch (NEJM 2004;351(20):2058-2068) |

## Lote 15 — 9 markdown (29/08/2026)

- `invest-verapamil-versus-atenolol-na-has-com-dac` (PMID 14657064; primário NS)
- `transcend-telmisartana-no-alto-risco-intolerante-a-ieca` (PMID 18757085; P=0,216)
- `i-preserve-irbesartana-na-icfep` (PMID 19001508; HR 0,95; P=0,35)
- `search-sinvastatina-80-versus-20-pos-iam` (PMID 21067805; P=0,10; miopatia 0,9% vs 0,03%)
- `relax-ahf-serelaxina-na-ic-aguda` (PMID 23141816; morte 180 d adicional; RELAX-AHF-2 PMID 31433919 neutro)
- `true-ahf-ularitida-na-ic-aguda` (PMID 28402745; P=0,75)
- `accord-lipid-fenofibrato-sobre-sinvastatina-no-diabetes` (PMID 20228404; P=0,32)
- `field-fenofibrato-no-diabetes-tipo-2` (PMID 16310551; primário P=0,16)
- `fluxograma-fibrato-para-evento-cardiovascular-field-accord-lipid-prominent`

## PMIDs lote 15

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| INVEST | 14657064 | 10.1001/jama.290.21.2805 | Europe PMC |
| TRANSCEND | 18757085 | 10.1016/S0140-6736(08)61242-8 | Europe PMC |
| I-PRESERVE | 19001508 | 10.1056/NEJMoa0805450 | Europe PMC |
| SEARCH | 21067805 | 10.1016/S0140-6736(10)60310-8 | Europe PMC |
| RELAX-AHF | 23141816 | 10.1016/S0140-6736(12)61855-8 | Europe PMC |
| RELAX-AHF-2 | 31433919 | 10.1056/NEJMoa1801291 | Europe PMC |
| TRUE-AHF | 28402745 | 10.1056/NEJMoa1601895 | Europe PMC |
| ACCORD-Lipid | 20228404 | 10.1056/NEJMoa1001282 | Europe PMC |
| FIELD | 16310551 | 10.1016/S0140-6736(05)67667-2 | Europe PMC |

## Lote 17 — 6 markdown (29/08/2026)

- `camelot-amlodipina-versus-enalapril-na-dac-com-pa-normal` (PMID 15536108; enalapril vs placebo P=0,16)
- `praise-amlodipina-na-ic-grave` (PMID 8813041; P=0,31; PRAISE-2 PMID 24621933 citado, sem arquivo)
- `iona-nicorandil-na-angina-estavel` (PMID 11965271; secundário morte/IAM P=0,068)
- `action-nifedipina-gits-na-angina-estavel` (PMID 15351192; HR 0,97 P=0,54)
- `solvd-prevention-enalapril-na-disfuncao-ventricular-assintomatica` (PMID 1463530; morte P=0,30)
- `fluxograma-ccb-na-dac-e-ic-camelot-action-praise`

## PMIDs lote 17

| Ensaio | PMID | Confirmação |
|---|---|---|
| CAMELOT | 15536108 | PubMed efetch |
| PRAISE | 8813041 | PubMed efetch |
| PRAISE-2 | 24621933 | citado, sem dump próprio |
| IONA | 11965271 | PubMed efetch |
| ACTION | 15351192 | PubMed efetch |
| SOLVD Prevention | 1463530 | PubMed efetch |

## Lote 18 — 11 markdown (29/08/2026)

- `val-heft-valsartana-na-ic-cronica` (PMID 11759645; tríplice post hoc adversa)
- `heaal-losartana-150-versus-50-na-icfer-intolerante-a-ieca` (PMID 19922995; morte P=0,24)
- `atlas-lisinopril-alta-versus-baixa-dose-na-icfer` (PMID 10587334; morte P=0,128; ≠ ATLAS ACS 2)
- `astronaut-aliskireno-apos-internacao-por-icfer` (PMID 23478743; P=0,41 / 0,36)
- `guide-it-nt-probnp-guiado-versus-cuidado-usual-na-icfer` (PMID 28829876; futilidade 37% vs 37%)
- `elite-ii-losartana-versus-captopril-na-ic-sintomatica` (PMID 10821361; superioridade falhou)
- `bari-2d-revascularizacao-versus-terapia-medica-no-diabetes-com-dac-estavel` (PMID 19502645)
- `syntax-pci-versus-cabg-na-trivascular-ou-tronco` (PMID 19228612; NI falhou)
- `excel-pci-everolimus-versus-cabg-no-tronco-de-baixa-ou-intermediaria-complexidade` (PMID 27797291; 3 anos; 5 anos NÃO relido)
- `fluxograma-pci-versus-cabg-syntax-excel-freedom-bari-2d`
- `fluxograma-dose-de-ieca-e-bra-atlas-heaal-elite-ii`

## PMIDs lote 18

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| VAL-HeFT | 11759645 | 10.1056/NEJMoa010713 | PubMed efetch (NEJM 2001;345(23):1667-1675) |
| HEAAL | 19922995 | 10.1016/S0140-6736(09)61913-9 | PubMed efetch (Lancet 2009;374(9704):1840-1848) |
| ATLAS (lisinopril) | 10587334 | 10.1161/01.CIR.100.23.2312 | PubMed efetch (Circulation 1999;100(23):2312-2318) |
| ASTRONAUT | 23478743 | 10.1001/jama.2013.1954 | PubMed efetch (JAMA 2013;309(11):1125-1135) |
| GUIDE-IT | 28829876 | 10.1001/jama.2017.10565 | Europe PMC (JAMA 2017;318(8):713-720) |
| ELITE II | 10821361 | 10.1016/S0140-6736(00)02213-3 | PubMed efetch (Lancet 2000;355(9215):1582-1587) |
| BARI 2D | 19502645 | 10.1056/NEJMoa0805796 | PubMed efetch (NEJM 2009;360(24):2503-2515) |
| SYNTAX | 19228612 | 10.1056/NEJMoa0804626 | PubMed efetch (NEJM 2009;360(10):961-972) |
| EXCEL 3y | 27797291 | 10.1056/NEJMoa1610227 | PubMed efetch (NEJM 2016;375(23):2223-2235) |

## Lote 19 — 6 markdown (29/08/2026)

- `noble-pci-versus-cabg-no-tronco-desprotegido-5-anos` (PMID 31879028; MACCE 28% vs 19%, NI falhou, P=0,0002; morte 9% vs 9%)
- `noble-10-anos-mortalidade-pci-versus-cabg-no-tronco` (PMID 41936368; morte 23% vs 25%, P=0,56)
- `excel-5-anos-pci-versus-cabg-no-tronco-de-baixa-ou-intermediaria-complexidade` (PMID 31562798; primário NS 22,0% vs 19,2%; morte 13,0% vs 9,9% não é primário e sem p no abstract)
- `precombat-pci-sirolimus-versus-cabg-no-tronco-desprotegido` (PMID 21463149; NI 1 ano com margem larga; autores: não diretivo)
- `best-pci-everolimus-versus-cabg-na-doenca-multiarterial` (PMID 25774645; ≠ BEST-CLI ≠ bucindolol; NI 2 anos falhou; parou cedo)
- `fluxograma-tronco-pci-versus-cabg-excel-noble-precombat`

## PMIDs lote 19

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| NOBLE 2016 | 27810312 | 10.1016/S0140-6736(16)32052-9 | PubMed efetch (Lancet 2016;388(10061):2743-2752) |
| NOBLE 5y | 31879028 | 10.1016/S0140-6736(19)32972-1 | PubMed efetch (Lancet 2020;395(10219):191-199) |
| NOBLE 10y | 41936368 | 10.1016/S0140-6736(26)00205-9 | PubMed efetch (Lancet 2026;407(10536):1374-1382) |
| EXCEL 5y | 31562798 | 10.1056/NEJMoa1909406 | PubMed efetch (NEJM 2019;381(19):1820-1830) |
| PRECOMBAT | 21463149 | 10.1056/NEJMoa1100452 | PubMed efetch (NEJM 2011;364(18):1718-1727) |
| BEST (Park) | 25774645 | 10.1056/NEJMoa1415447 | PubMed efetch (NEJM 2015;372(13):1204-1212). NÃO é Bangalore PMID 25775087 |

## Lote 20 — 6 markdown (29/08/2026)

- `orbita-pci-versus-placebo-na-angina-estavel` (PMID 29103656; +16,6 s; P=0,200)
- `fame-ffr-versus-angiografia-para-guiar-pci-na-multiarterial` (PMID 19144937; 18,3% vs 13,2%; P=0,02)
- `shep-clortalidona-na-hipertensao-sistolica-isolada-do-idoso` (PMID 2046107; AVC RR 0,64; P=0,0003; DOI ausente no MEDLINE)
- `syst-eur-nitrendipina-na-hipertensao-sistolica-isolada-do-idoso` (PMID 9297994; AVC −42%; morte P=0,22)
- `relax-sildenafila-na-icfep-capacidade-de-exercicio` (PMID 23478662; VO2 P=0,90; ≠ RELAX-AHF)
- `fluxograma-has-sistolica-isolada-idoso-shep-syst-eur-hyvet`

## PMIDs lote 20

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ORBITA | 29103656 | 10.1016/S0140-6736(17)32714-9 | PubMed efetch (Lancet 2018;391(10115):31-40) |
| FAME | 19144937 | 10.1056/NEJMoa0807611 | PubMed efetch (NEJM 2009;360(3):213-224) |
| SHEP | 2046107 | ausente no MEDLINE | PubMed efetch (JAMA 1991;265(24):3255-3264) |
| Syst-Eur | 9297994 | 10.1016/S0140-6736(97)05381-6 | PubMed efetch (Lancet 1997;350(9080):757-764) |
| RELAX (sildenafila) | 23478662 | 10.1001/jama.2013.2024 | PubMed efetch (JAMA 2013;309(12):1268-1277) |

## Lote 21 — 6 markdown (29/08/2026)

- `athena-hf-espironolactona-alta-dose-na-ic-aguda` (PMID 28700781; NT-proBNP P=0,57; ≠ ATHENA-dronedarona)
- `rose-ahf-dopamina-ou-nesiritida-baixa-dose-na-ic-aguda-com-disfuncao-renal` (PMID 24247300; coprimários NS)
- `neat-hfpef-mononitrato-de-isossorbida-reduz-atividade-na-icfep` (PMID 26549714; horas ativas P=0,02 contra o nitrato)
- `indie-hfpef-nitrito-inalatorio-nao-aumenta-vo2-pico` (PMID 30398602; DOI Europe PMC 10.1001/jama.2018.14852)
- `vitality-hfpef-vericiguat-nao-melhora-limitacao-fisica-na-icfep` (PMID 33079152; DOI Europe PMC 10.1001/jama.2020.15922; ≠ VICTORIA)
- `fluxograma-o-que-nao-prescrever-para-esforco-na-icfep`

ASCEND-HF não duplicado (dump em vasodilatadores IV).

## PMIDs lote 21

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ATHENA-HF | 28700781 | 10.1001/jamacardio.2017.2198 | PubMed efetch (JAMA Cardiol 2017;2(9):950-958) |
| ROSE-AHF | 24247300 | 10.1001/jama.2013.282190 | PubMed efetch (JAMA 2013;310(23):2533-2543) |
| NEAT-HFpEF | 26549714 | 10.1056/NEJMoa1510774 | PubMed efetch (NEJM 2015;373(24):2314-2324) |
| INDIE-HFpEF | 30398602 | 10.1001/jama.2018.14852 | PubMed efetch + DOI Europe PMC (JAMA 2018;320(17):1764-1773). XML NCBI devolveu DOI espúrio. |
| VITALITY-HFpEF | 33079152 | 10.1001/jama.2020.15922 | PubMed efetch + DOI Europe PMC (JAMA 2020;324(15):1512-1521). XML NCBI devolveu DOI do RELAX. |

## Lote 22 — 4 markdown (29/08/2026)

- `tracer-vorapaxar-na-sca-sem-supra` (PMID 22077816; primário P=0,07; HIC HR 3,39)
- `tra-2p-timi-50-vorapaxar-na-prevencao-secundaria-aterotrombotica` (PMID 22443427; primário P<0,001; HIC 1,0% vs 0,5%; DSMB parou AVC prévio)
- `best-bucindolol-na-ic-avancada` (PMID 11386264; morte P ajustado 0,13; ≠ BEST-PCI ≠ BEST-CLI)
- `fluxograma-vorapaxar-tracer-tra-2p`

## PMIDs lote 22

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| TRACER | 22077816 | 10.1056/NEJMoa1109719 | PubMed efetch (NEJM 2012;366(1):20-33) |
| TRA 2P–TIMI 50 | 22443427 | 10.1056/NEJMoa1200933 | PubMed efetch (NEJM 2012;366(15):1404-1413) |
| BEST (bucindolol) | 11386264 | 10.1056/NEJM200105313442202 | PubMed efetch (NEJM 2001;344(22):1659-1667) |

## Lote 23 — 6 markdown (29/08/2026)

- `solid-timi-52-darapladib-apos-sca` (PMID 25173516; HR 1,00; P=0,93)
- `stability-darapladib-na-dac-estavel` (PMID 24678955; primário P=0,20; secundário P=0,045 com IC 0,82–1,00)
- `acuity-bivalirudina-na-sca-invasiva` (PMID 17124018; bivalirudina isolada sangramento RR 0,53; HEAT/VALIDATE são outro desenho)
- `early-acs-eptifibatida-precoce-versus-provisoria-na-sca-sem-supra` (PMID 19332455; P=0,23)
- `survive-levosimendana-versus-dobutamina-na-ic-aguda` (PMID 17473298; morte 180 d P=0,40)
- `fluxograma-darapladib-solid-stability`

## PMIDs lote 23

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| SOLID-TIMI 52 | 25173516 | 10.1001/jama.2014.11061 | PubMed efetch (JAMA 2014;312(10):1006-1015) |
| STABILITY | 24678955 | 10.1056/NEJMoa1315878 | PubMed efetch (NEJM 2014;370(18):1702-1711) |
| ACUITY | 17124018 | 10.1056/NEJMoa062437 | PubMed efetch (NEJM 2006;355(21):2203-2216) |
| EARLY-ACS | 19332455 | 10.1056/NEJMoa0901316 | PubMed efetch (NEJM 2009;360(21):2176-2190) |
| SURVIVE | 17473298 | 10.1001/jama.297.17.1883 | PubMed efetch (JAMA 2007;297(17):1883-1891) |

## Lote 24 — 7 markdown (29/08/2026)

- `pursuit-eptifibatida-na-sca-sem-supra` (PMID 9705684; 14,2% vs 15,7%; P=0,04)
- `prism-plus-tirofibana-com-heparina-na-sca` (PMID 9599103; braço isolado parado, morte 4,6% vs 1,1%; PRISM PMID 9599104 não relido)
- `gusto-iv-acs-abciximabe-sem-revascularizacao-precoce` (PMID 11425411; 8,0% vs 8,2% vs 9,1%)
- `caprie-clopidogrel-versus-aas-na-aterosclerose` (PMID 8918275; RRR 8,7%; P=0,043)
- `charisma-clopidogrel-mais-aas-vs-aas-na-aterotrombose` (PMID 16531616; primário P=0,22; morte CV 3,9% vs 2,2% nos múltiplos fatores)
- `revive-levosimendana-versus-placebo-na-ic-aguda` (PMID 24621834; sintoma P=0,015; morte 90 d P=0,29)
- `fluxograma-gpi-pursuit-prism-plus-gusto-iv-early-acs`

## PMIDs lote 24

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| PURSUIT | 9705684 | 10.1056/NEJM199808133390704 | PubMed efetch (NEJM 1998;339(7):436-443) |
| PRISM-PLUS | 9599103 | 10.1056/NEJM199805213382102 | PubMed efetch (NEJM 1998;338(21):1488-1497) |
| GUSTO-IV ACS | 11425411 | 10.1016/S0140-6736(00)05060-1 | PubMed efetch (Lancet 2001;357(9272):1915-1924) |
| CAPRIE | 8918275 | 10.1016/S0140-6736(96)09457-3 | PubMed efetch (Lancet 1996;348(9038):1329-1339) |
| CHARISMA | 16531616 | 10.1056/NEJMoa060989 | PubMed efetch (NEJM 2006;354(16):1706-1717) |
| REVIVE | 24621834 | 10.1016/j.jchf.2012.12.004 | PubMed efetch (JACC Heart Fail 2013;1(2):103-111) |

## Lote 25 — 5 markdown (29/08/2026)

- `prism-tirofibana-versus-heparina-na-angina-instavel` (PMID 9599104; 48 h P=0,01; 30 d composto P=0,34; morte 30 d P=0,02 não é primário)
- `progress-perindopril-indapamida-na-prevencao-secundaria-de-avc` (PMID 11589932 — NÃO 11556031/Yersinia; monoterapia sem redução discernível)
- `leopards-levosimendana-na-sepse` (PMID 27705084; SOFA P=0,053; desmame HR 0,77)
- `fluxograma-levosimendana-ic-aguda-versus-sepse`
- `fluxograma-progress-pos-avc-perindopril-indapamida`

Syst-China PMID 10647760 é análise de estratos, não o paper primário — não escrito.

## PMIDs lote 25

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| PRISM | 9599104 | 10.1056/NEJM199805213382103 | PubMed efetch (NEJM 1998;338(21):1498-1505) |
| PROGRESS | 11589932 | 10.1016/S0140-6736(01)06178-5 | PubMed efetch (Lancet 2001;358(9287):1033-1041) |
| LeoPARDS | 27705084 | 10.1056/NEJMoa1609409 | PubMed efetch (NEJM 2016;375(17):1638-1648) |

## Lote 26 — 4 markdown (29/08/2026)

- `syst-china-nitrendipina-na-has-sistolica-isolada-do-idoso-chines` (PMID **9869017**; NÃO 10647760/estratos; alocação **alternate patients**; AVC −38% P=0,01; morte −39% P=0,003)
- `fever-felodipino-mais-hctz-na-hipertensao-chinesa` (PMID 16269957; AVC −27% P=0,001; morte −31% P=0,006; IC P=0,239 NS; câncer P=0,017 secundário — não vender)
- `catch-tinzaparina-versus-varfarina-no-tev-associado-ao-cancer` (PMID 26284719; primário P=0,07 NS; CRNMB P=0,004; não vender como confirmação do CLOT)
- `fluxograma-has-sistolica-isolada-e-fever-china-versus-ocidente` (companheiro; **não** reescreve a árvore SHEP/Syst-Eur/HYVET)

## PMIDs lote 26

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| Syst-China | 9869017 | 10.1097/00004872-199816120-00016 | Europe PMC + NCBI esummary (J Hypertens 1998;16(12 Pt 1):1823-9) |
| FEVER | 16269957 | 10.1097/01.hjh.0000194120.42722.ac | Europe PMC + NCBI esummary (J Hypertens 2005;23(12):2157-72) |
| CATCH | 26284719 | 10.1001/jama.2015.9243 | Europe PMC + NCBI esummary (JAMA 2015;314(7):677-686) |

## Lote 27 — 3 markdown (29/08/2026)

- `clot-dalteparina-versus-cumarinico-no-tev-associado-ao-cancer` (PMID 12853587; 27/336 vs 53/336; HR 0,48; P=0,002; morte 39% vs 41% sem p)
- `select-d-rivaroxabana-versus-dalteparina-no-tev-associado-ao-cancer` (PMID 29746227; **piloto**; recorrência 4% vs 11% HR 0,43; CRNMB HR 3,76; não vender superioridade)
- `fluxograma-hbpm-versus-varfarina-e-doac-no-tev-do-cancer`

## PMIDs lote 27

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| CLOT | 12853587 | 10.1056/NEJMoa025313 | Europe PMC + NCBI esummary (NEJM 2003;349(2):146-53) |
| SELECT-D | 29746227 | 10.1200/JCO.2018.78.8034 | Europe PMC + NCBI esummary (J Clin Oncol 2018;36(20):2017-2023) |

## Lote 28 — 3 markdown (29/08/2026)

- `adam-vte-apixabana-versus-dalteparina-no-tev-associado-ao-cancer` (PMID 31630479; primário sangramento maior P=0,138 NS; recorrência P=0,0281 **secundário**)
- `planquette-2022-rivaroxabana-versus-dalteparina-no-tev-do-cancer-ni-nao-atingida` (PMID 34627853; NCT02746185; n=158, NI não atingida; **não** batizar CASTA-DIVA — TITLE search 0)
- `fluxograma-nao-vender-ensaio-pequeno-no-tev-do-cancer`

## PMIDs lote 28

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ADAM-VTE | 31630479 | 10.1111/jth.14662 | Europe PMC + NCBI esummary (J Thromb Haemost 2020;18(2):411-421) |
| Planquette 2022 | 34627853 | 10.1016/j.chest.2021.09.037 | Europe PMC + NCBI esummary (Chest 2022;161(3):781-790) |

## Lote 29 — 4 markdown (29/08/2026)

- `avert-apixabana-na-profilaxia-primaria-ambulatorial-khorana-2` (PMID **30511879**; TEV P<0,001; sangramento maior mITT P=0,046)
- `cassini-rivaroxabana-na-profilaxia-primaria-ambulatorial-khorana-2` (PMID **30786186**; primário 180 d **P=0,10 NS**; período da intervenção é suporte)
- `save-onco-semuloparina-na-profilaxia-primaria-durante-quimioterapia` (PMID 22335737; não extrapolar a enoxaparina)
- `fluxograma-profilaxia-primaria-ambulatorial-khorana-avert-cassini`

## PMIDs lote 29

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| AVERT | 30511879 | 10.1056/NEJMoa1814468 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2019;380(8):711-719). NCBI esearch por título devolveu papers posteriores — não usar esses PMIDs. |
| CASSINI | 30786186 | 10.1056/NEJMoa1814630 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2019;380(8):720-728) |
| SAVE-ONCO | 22335737 | 10.1056/NEJMoa1108898 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2012;366(7):601-9) |

## Lote 30 — 3 markdown (29/08/2026)

- `apex-betrixabana-estendida-no-paciente-clinico-agudo` (PMID 27232649; primário coorte D-dímero **P=0,054 NS**; overall exploratório)
- `protecht-nadroparina-na-profilaxia-primaria-durante-quimioterapia` (PMID 19726226; composto venoso+arterial; **p unilateral 0,02**)
- `fluxograma-apex-protecht-o-que-nao-e-primario`

RALES/EMPHASIS e PARADIGM-HF: dump combinado completo — não duplicar. SHIFT: arquivo próprio. CULPRIT-SHOCK/IABP-SHOCK II: arquivo próprio. MAGELLAN: TITLE hunt não fechou PMID primário — não inventar.

## PMIDs lote 30

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| APEX | 27232649 | 10.1056/NEJMoa1601747 | Europe PMC + NCBI esummary (NEJM 2016;375(6):534-44) |
| PROTECHT | 19726226 | 10.1016/S1470-2045(09)70232-3 | Europe PMC + NCBI esummary (Lancet Oncol 2009;10(10):943-9) |

## Lote 31 — 4 markdown (29/08/2026)

- `sharp-sinvastatina-ezetimiba-na-doenca-renal-cronica` (PMID 21663949; primário P=0,0021; IAM/morte coronariana P=0,37 NS)
- `4d-atorvastatina-na-hemodialise-com-diabetes-tipo-2` (PMID 16034009; primário P=0,37; eventos cardíacos P=0,03 nominal; AVC fatal P=0,04 componente)
- `aurora-rosuvastatina-na-hemodialise` (PMID 19332456; primário P=0,59; morte P=0,51)
- `fluxograma-estatina-na-drc-versus-dialise-sharp-4d-aurora`

ONTARGET: dump completo em RENAAL/IDNT — não duplicar.

## PMIDs lote 31

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| SHARP | 21663949 | 10.1016/S0140-6736(11)60739-3 | Europe PMC TITLE exacto + NCBI esummary (Lancet 2011;377(9784):2181-92) |
| 4D | 16034009 | 10.1056/NEJMoa043545 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2005;353(3):238-48) |
| AURORA | 19332456 | 10.1056/NEJMoa0810177 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2009;360(14):1395-407) |

## Lote 32 — 3 markdown (29/08/2026)

- `adopt-apixabana-estendida-versus-enoxaparina-no-clinico-agudo` (PMID 22077144; primário P=0,44; sangramento maior P=0,04)
- `magellan-rivaroxabana-estendida-versus-enoxaparina-no-clinico-agudo` (PMID **23388003**, NÃO 23675665/carta nem 23339662/química; dia 35 P=0,02 com sangramento P<0,001)
- `fluxograma-profilaxia-estendida-no-clinico-adopt-magellan-apex`

## PMIDs lote 32

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ADOPT | 22077144 | 10.1056/NEJMoa1110899 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2011;365(23):2167-77) |
| MAGELLAN | 23388003 | 10.1056/NEJMoa1111096 | Europe PMC + NCBI pubtype RCT (NEJM 2013;368(6):513-23). Cartas 23675665. |

## Lote 33 — 4 markdown (29/08/2026)

- `frisc-ii-estrategia-invasiva-precoce-na-dac-instavel` (PMID 10475181; morte/IAM P=0,031; morte P=0,10 NS; DOI ausente no MEDLINE)
- `tactics-timi-18-estrategia-invasiva-precoce-com-tirofibana-na-sca-sem-supra` (PMID 11419424; primário P=0,025; morte/IAM IC toca 1,00; GPI de fundo)
- `ictus-invasivo-precoce-versus-seletivo-na-sca-sem-supra-com-troponina` (PMID 16162880; primário P=0,33 NS; IAM P=0,005 no invasivo)
- `fluxograma-invasivo-precoce-versus-seletivo-frisc-ii-tactics-ictus`

## PMIDs lote 33

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| FRISC II | 10475181 | ausente no MEDLINE | Europe PMC TITLE exacto + NCBI esummary (Lancet 1999;354(9180):708-15) |
| TACTICS-TIMI 18 | 11419424 | 10.1056/NEJM200106213442501 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2001;344(25):1879-87) |
| ICTUS | 16162880 | 10.1056/NEJMoa044259 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2005;353(11):1095-104) |

## Lote 34 — 1 markdown (29/08/2026)

- `exclaim-enoxaparina-estendida-no-clinico-com-mobilidade-reduzida` (PMID 20621900; TEV 2,5% vs 4%; sangramento maior 0,8% vs 0,3%; critério emendado no meio)

## PMIDs lote 34

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| EXCLAIM | 20621900 | 10.7326/0003-4819-153-1-201007060-00004 | Europe PMC TITLE exacto + NCBI esummary (Ann Intern Med 2010;153(1):8-18) |

## Lote 35 — 5 markdown (29/08/2026)

- `timacs-angiografia-precoce-versus-tardia-na-sca-sem-supra` (PMID 19458363; primário P=0,15 NS; secundário P=0,003 não vender)
- `isar-cool-pretatamento-antitrombotico-prolongado-antes-da-icp-na-sca` (PMID 14506118; cooling-off piora P=0,04)
- `verdict-angiografia-muito-precoce-versus-48-72-h-na-sca-sem-supra` (PMID **30565996**, NÃO 30608878/correção; HR 0,92 IC cruza 1; GRACE>140 IC inclui 1)
- `riddle-nstemi-intervencao-imediata-versus-tardia-no-iam-sem-supra` (PMID 26777321; n=323; efeito pré-cateter)
- `fluxograma-timing-da-angiografia-na-sca-sem-supra-timacs-verdict-isar-cool`

## PMIDs lote 35

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| TIMACS | 19458363 | 10.1056/NEJMoa0807986 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2009;360(21):2165-75) |
| ISAR-COOL | 14506118 | 10.1001/jama.290.12.1593 | Europe PMC TITLE exacto + NCBI esummary (JAMA 2003;290(12):1593-9) |
| VERDICT | 30565996 | 10.1161/CIRCULATIONAHA.118.037152 | Europe PMC TITLE exacto + NCBI esummary (Circulation 2018;138(24):2741-2750). Correção 30608878. |
| RIDDLE-NSTEMI | 26777321 | 10.1016/j.jcin.2015.11.018 | Europe PMC TITLE exacto + NCBI esummary (JACC Cardiovasc Interv 2016;9(6):541-9) |

## Lote 36 — 1 markdown (29/08/2026)

- `rita-3-intervencao-versus-conservador-na-sca-sem-supra` (PMID 12241831; 4 meses P=0,001 por angina refratária; morte/IAM 1 ano P=0,58 NS)

## PMIDs lote 36

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| RITA-3 | 12241831 | 10.1016/S0140-6736(02)09894-X | Europe PMC TITLE exacto + NCBI esummary (Lancet 2002;360(9335):743-51) |

## Lote 37 — 5 markdown (29/08/2026)

- `credo-clopidogrel-12-meses-apos-pci-e-ataque-pre-procedimento` (PMID 12435254; 1 ano P=0,02 ARD 3%; ataque 28 d P=0,23; ≥6 h P=0,051)
- `aboard-intervencao-imediata-versus-proximo-dia-util-na-sca-sem-supra` (PMID 19724041; pico TnI P=0,70; n=352)
- `synergy-enoxaparina-versus-hnf-na-sca-sem-supra-invasiva` (PMID 15238590; OR 0,96 IC inclui 1; TIMI major P=0,008; margem NI ausente no abstract)
- `pci-cure-pretratamento-e-manutencao-de-clopidogrel-na-icp-do-nste` (PMID 11520521; subgrupo de ICP do CURE; 30 d P=0,03; 31% inclui eventos pré-ICP)
- `fluxograma-credo-12-meses-versus-ataque-pre-pci`

## PMIDs lote 37

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| CREDO | 12435254 | 10.1001/jama.288.19.2411 | Europe PMC TITLE exacto + NCBI esummary (JAMA 2002;288(19):2411-2420) |
| ABOARD | 19724041 | 10.1001/jama.2009.1267 | Europe PMC TITLE exacto + NCBI esummary (JAMA 2009;302(9):947-954; NCT00442949) |
| SYNERGY | 15238590 | 10.1001/jama.292.1.45 | Europe PMC TITLE exacto + NCBI esummary (JAMA 2004;292(1):45-54) |
| PCI-CURE | 11520521 | 10.1016/s0140-6736(01)05701-4 | Europe PMC TITLE exacto + NCBI esummary (Lancet 2001;358(9281):527-533) |

NICE-SUGAR: dump completo no combinado perioperatório — não duplicar.

## Lote 38 — 1 markdown (29/08/2026)

- `process-egdt-protocolar-versus-cuidado-usual-no-choque-septico` (PMID 24635773; morte 60 d P=0,83 e P=0,31; não inventar Rivers)

## PMIDs lote 38

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ProCESS | 24635773 | 10.1056/NEJMoa1401602 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2014;370(18):1683-1693; NCT00510835) |

## Lote 39 — 3 markdown (29/08/2026)

- `arise-egdt-versus-cuidado-usual-no-choque-septico-precoce` (PMID 25272316; morte 90 d P=0,90)
- `promise-egdt-versus-cuidado-usual-no-choque-septico` (PMID 25776532; morte 90 d P=0,90; custo-efetividade <20%)
- `fluxograma-egdt-process-arise-promise`

## PMIDs lote 39

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ARISE | 25272316 | 10.1056/NEJMoa1404380 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2014;371(16):1496-1506; NCT00975793) |
| ProMISe | 25776532 | 10.1056/NEJMoa1500896 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2015;372(14):1301-1311; ISRCTN36307479). Cartas 26244314–26244317. |

## Lote 40 — 4 markdown (29/08/2026)

- `essence-enoxaparina-versus-hnf-na-angina-instavel` (PMID 9250846; tríplice com angina 14 d P=0,019; maior empata)
- `timi-11b-enoxaparina-versus-hnf-na-angina-instavel` (PMID 10517729; IC toca 1,00; extra-hospitalar sangra P=0,021 sem ganho)
- `frisc-dalteparina-versus-placebo-na-dac-instavel` (PMID 8596317; vs placebo, não HNF; 4–5 meses NS; DOI ausente)
- `fluxograma-enoxaparina-essence-timi-11b-synergy`

## PMIDs lote 40

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ESSENCE | 9250846 | 10.1056/NEJM199708143370702 | Europe PMC TITLE exacto + NCBI esummary (NEJM 1997;337(7):447-452) |
| TIMI 11B | 10517729 | 10.1161/01.cir.100.15.1593 | Europe PMC TITLE exacto + NCBI esummary (Circulation 1999;100(15):1593-1601). Meta 10517730 não relida como RCT. |
| FRISC I | 8596317 | ausente no MEDLINE | Europe PMC TITLE exacto + NCBI esummary (Lancet 1996;347(9001):561-568) |

## Lote 41 — 3 markdown (29/08/2026)

- `rita-3-cinco-anos-invasivo-versus-conservador-na-sca-sem-supra` (PMID 16154018; morte/IAM P=0,044; morte P=0,054)
- `rita-3-dez-anos-mortalidade-invasivo-versus-seletivo` (PMID 26227188; morte P=0,94)
- `fluxograma-rita-3-um-cinco-dez-anos`

## PMIDs lote 41

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| RITA-3 5a | 16154018 | 10.1016/S0140-6736(05)67222-4 | Europe PMC TITLE exacto + NCBI esummary (Lancet 2005;366(9489):914-920) |
| RITA-3 10a | 26227188 | 10.1016/j.jacc.2015.05.051 | Europe PMC TITLE exacto + NCBI esummary (JACC 2015;66(5):511-520). Cartas 27012413/27012414. |

## Lote 42 — 4 markdown (29/08/2026)

- `capricorn-carvedilol-pos-iam-com-disfuncao-ventricular` (PMID 11356434; primário composto NS; morte P=0,03 componente)
- `optimaal-losartana-versus-captopril-pos-iam-de-alto-risco` (PMID 12241832; morte P=0,07 a favor do captopril)
- `gusto-iib-hirudina-versus-heparina-na-sca` (PMID 8778585; 30 d P=0,06; 24 h não é primário)
- `fluxograma-optimaal-valiant-ieca-versus-bra-pos-iam`

COMET: arquivo próprio `carvedilol-versus-metoprolol-tartarato-o-ensaio-comet` — não duplicar.
SENIORS: dump no combinado de frequência cardíaca — não duplicar.

## PMIDs lote 42

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| CAPRICORN | 11356434 | 10.1016/s0140-6736(00)04560-8 | Europe PMC TITLE exacto + NCBI esummary (Lancet 2001;357(9266):1385-1390) |
| OPTIMAAL | 12241832 | 10.1016/s0140-6736(02)09895-1 | Europe PMC TITLE exacto + NCBI esummary (Lancet 2002;360(9335):752-760) |
| GUSTO-IIb | 8778585 | 10.1056/NEJM199609123351103 | Europe PMC TITLE exacto + NCBI esummary (NEJM 1996;335(11):775-782) |

## Lote 43 — 2 markdown (29/08/2026)

- `oasis-2-lepirudina-versus-heparina-na-sca-sem-supra` (PMID 9989712; primário 7 d P=0,077; DOI ausente; secundário com angina não vender)
- `fluxograma-hirudina-gusto-iib-oasis-2`

OASIS-1 PMID 9264481 é piloto n=909 — não escrito como RCT confirmatório.

## PMIDs lote 43

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| OASIS-2 | 9989712 | ausente no MEDLINE | Europe PMC TITLE exacto + NCBI esummary (Lancet 1999;353(9151):429-438) |
| OASIS-1 (piloto, não dumpado) | 9264481 | 10.1161/01.cir.96.3.769 | Europe PMC TITLE exacto + NCBI (Circulation 1997;96(3):769-777) |

## Lote 44 — 4 markdown (29/08/2026)

- `gissi-3-lisinopril-e-nitrato-precoce-no-iam` (PMID 7910229; lisinopril OR 0,88; GTN NS; DOI ausente)
- `isis-4-captopril-mononitrato-e-magnesio-no-iam-suspeito` (PMID 7661937; captopril 2p=0,02; mononitrato NS; magnésio truncado no abstract MEDLINE)
- `consensus-ii-enalaprilato-ev-precoce-no-iam` (PMID 1495520; morte 6 meses P=0,26; hipotensão 12% vs 3%)
- `fluxograma-ieca-precoce-no-iam-gissi-3-isis-4-consensus-ii`

CONSENSUS (IC crônica) permanece no combinado CONSENSUS+SOLVD+PARADIGM — não duplicar.

## PMIDs lote 44

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| GISSI-3 | 7910229 | ausente no MEDLINE | Europe PMC TITLE exacto + NCBI esummary (Lancet 1994;343(8906):1115-1122) |
| ISIS-4 | 7661937 | ausente no MEDLINE | Europe PMC TITLE exacto + NCBI efetch (Lancet 1995;345(8951):669-685). Abstract truncado — magnésio não extraído. |
| CONSENSUS II | 1495520 | 10.1056/NEJM199209033271002 | Europe PMC TITLE exacto + NCBI esummary (NEJM 1992;327(10):678-684) |

## Lote 45 — 5 markdown (29/08/2026)

- `frax-is-nadroparina-versus-hnf-na-angina-instavel` (PMID 10529323; primário NS; 14 d sangra P=0,0035)
- `hero-2-bivalirudina-versus-hnf-com-estreptoquinase-no-iamcsst` (PMID 11741625; morte P=0,85; reinfarto 96 h secundário)
- `replace-2-bivalirudina-provisoria-versus-hnf-mais-gpi-na-icp` (PMID 12588269; primário P=0,32; margem NI ausente)
- `medenox-enoxaparina-40-mg-na-profilaxia-do-clinico-agudo` (PMID 10477777; 40 mg P<0,001; 20 mg NS; morte NS)
- `fluxograma-bivalirudina-hero-2-replace-2-heat`

HYVET, COMET, SENIORS, OPTIME-CHF, NICE-SUGAR: já na casa — não duplicados neste turno.

## PMIDs lote 45

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| FRAX.I.S. | 10529323 | 10.1053/euhj.1999.1879 | Europe PMC TITLE exacto + NCBI esummary (Eur Heart J 1999;20(21):1553-1562) |
| HERO-2 | 11741625 | 10.1016/s0140-6736(01)06887-8 | Europe PMC TITLE exacto + NCBI esummary (Lancet 2001;358(9296):1855-1863) |
| REPLACE-2 | 12588269 | 10.1001/jama.289.7.853 | Europe PMC TITLE exacto + NCBI esummary (JAMA 2003;289(7):853-863) |
| MEDENOX | 10477777 | 10.1056/NEJM199909093411103 | Europe PMC TITLE exacto + NCBI esummary (NEJM 1999;341(11):793-800) |

## Lote 46 — 3 markdown (29/08/2026)

- `cadillac-stent-versus-angioplastia-com-ou-sem-abciximabe-no-iam` (PMID 11919304; primário por TVR; morte/IAM/AVC NS)
- `admiral-abciximabe-antes-do-stent-no-iam` (PMID 11419426; n=300)
- `fluxograma-cadillac-admiral-stent-e-abciximabe-no-iam`

## PMIDs lote 46

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| CADILLAC | 11919304 | 10.1056/NEJMoa013404 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2002;346(13):957-966) |
| ADMIRAL | 11419426 | 10.1056/NEJM200106213442503 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2001;344(25):1895-1903) |

## Lote 47 — 3 markdown (29/08/2026)

- `assent-3-tenecteplase-com-enoxaparina-ou-abciximabe` (PMID 11530146; tríplice com isquemia; morte isolada ausente no abstract)
- `gusto-v-reteplase-mais-abciximabe-versus-reteplase-no-iamcsst` (PMID 11425410; morte P=0,43; margem NI ausente)
- `fluxograma-lise-assent-3-gusto-v-extract`

## PMIDs lote 47

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ASSENT-3 | 11530146 | 10.1016/S0140-6736(01)05775-0 | Europe PMC TITLE exacto + NCBI esummary (Lancet 2001;358(9282):605-613) |
| GUSTO-V | 11425410 | 10.1016/s0140-6736(00)05059-5 | Europe PMC TITLE exacto + NCBI esummary (Lancet 2001;357(9272):1905-1914). Não é GUSTO-IV ACS (11425411). |

## Lote 48 — 4 markdown (29/08/2026)

- `epilog-abciximabe-com-heparina-baixa-na-icp` (PMID 9182212; interrompido; era do balão)
- `isar-react-3-bivalirudina-versus-hnf-na-icp-com-clopidogrel-600` (PMID 18703471; líquido P=0,57; troponina normal)
- `prevent-dalteparina-profilaxia-no-clinico-agudo` (PMID 15289368; não é PREVENT-UTI 30779530)
- `fluxograma-bivalirudina-isar-react-3-replace-2`

## PMIDs lote 48

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| EPILOG | 9182212 | 10.1056/NEJM199706123362401 | Europe PMC TITLE exacto + NCBI esummary (NEJM 1997;336(24):1689-1696) |
| ISAR-REACT 3 | 18703471 | 10.1056/NEJMoa0802944 | Europe PMC TITLE exacto + NCBI esummary (NEJM 2008;359(7):688-696; NCT00262054) |
| PREVENT médico | 15289368 | 10.1161/01.CIR.0000138928.83266.24 | Europe PMC TITLE exacto + NCBI esummary (Circulation 2004;110(7):874-879) |

## Lote 49 — 4 markdown (29/08/2026)

- `epic-abciximabe-bolus-e-infusao-na-angioplastia-de-alto-risco` (PMID 8121459; bolus+infusão P=0,008; bolus isolado P=0,43; % sangramento ausente)
- `paragon-a-lamifibana-na-angina-instavel` (PMID 9641689; primário 30 d P=0,668 NS; não vender 6 meses; ≠ PARAGON-HF)
- `assent-4-pci-tenecteplase-facilitada-versus-icp-primaria` (PMID 16488800; parado por morte hospitalar; primário piora)
- `fluxograma-icp-facilitada-assent-4-finesse`

## PMIDs lote 49

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| EPIC | 8121459 | 10.1056/NEJM199404073301402 | NCBI efetch (NEJM 1994;330(14):956-961) |
| PARAGON-A | 9641689 | 10.1161/01.cir.97.24.2386 | NCBI efetch (Circulation 1998;97(24):2386-2395) |
| ASSENT-4 PCI | 16488800 | 10.1016/S0140-6736(06)68147-6 | NCBI efetch (Lancet 2006;367(9510):569-578; NCT00168792) |

## Lote 50 — 4 markdown (29/08/2026)

- `finesse-icp-facilitada-reteplase-abciximabe-no-iamcsst` (PMID 18499565; primário P=0,55; não vender resolução de ST)
- `smile-zofenopril-seis-semanas-no-iam-anterior` (PMID 7990904; composto 6 sem P=0,018; morte isolada P=0,19; 1 ano após 6 sem de fármaco)
- `capture-abciximabe-antes-da-ptca-na-angina-instavel-refrataria` (PMID 9164316; 30 d P=0,012; 6 meses empatado; DOI via Crossref)
- `restore-tirofibana-na-angioplastia-da-sca` (PMID 9315530; primário 30 d P=0,160 NS; não vender 2 d/7 d)

Patches de conectividade: EPILOG → EPIC; fluxograma-lise → ASSENT-4; fluxograma-gpi → PARAGON-A; fluxograma-ieca-precoce → SMILE.

## PMIDs lote 50

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| FINESSE | 18499565 | 10.1056/NEJMoa0706816 | NCBI efetch (NEJM 2008;358(21):2205-2217; NCT00046228) |
| SMILE | 7990904 | 10.1056/NEJM199501123320203 | NCBI efetch (NEJM 1995;332(2):80-85) |
| CAPTURE | 9164316 | 10.1016/s0140-6736(96)10452-9 | NCBI efetch (Lancet 1997;349(9063):1429-1435); DOI Crossref (NCBI ArticleIdList sem DOI) |
| RESTORE | 9315530 | 10.1161/01.cir.96.5.1445 | NCBI efetch (Circulation 1997;96(5):1445-1453) |

## Lotes seguintes (fila)

1. OASIS-1 permanece piloto — não promover
2. Magnésio do ISIS-4: abstract MEDLINE truncado — reler PDF/PMC antes de dump
3. Cangrelor: monografia já tem dump CHAMPION PHOENIX — não duplicar
4. WOEST — FA+PCI; AUGUSTUS da casa; território de arritmia na borda
5. MATRIX/HORIZONS: arquivo próprio — não duplicar
6. COMET / SENIORS / HYVET / OPTIME-CHF / ESCAPE: já na casa — não duplicar
7. DOSE/CARRESS / SOLOIST/SCORED / ASCEND-HF / LIDO: dump combinado — não duplicar
8. Caravaggio/Hokusai / RALES+EMPHASIS / CONSENSUS+SOLVD+PARADIGM / CIBIS+MERIT+COPERNICUS / ONTARGET em RENAAL-IDNT: dumps combinados — não duplicar
## Lote 51 — 4 markdown (29/08/2026)

- `vanqwish-invasivo-versus-conservador-no-iam-sem-onda-q` (PMID 9632444; primário 23 meses P=0,35; invasivo pior na alta)
- `impact-ii-eptifibatida-na-icp` (PMID 9164315; ITT NS; não vender as-treated; DOI Crossref)
- `esprit-2000-eptifibatida-duplo-bolus-no-stent` (PMID 11145489; ≠ ESPRIT-HAS 2024; interrompido)
- `shock-revascularizacao-precoce-versus-estabilizacao-no-choque-cardiogenico` (PMID 10460813; primário 30 d P=0,11; 6 meses secundário)

Patch: fluxograma FRISC II/TACTICS/ICTUS → VANQWISH. A-HeFT e ASCEND-HF já na casa — não duplicados.

## PMIDs lote 51

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| VANQWISH | 9632444 | 10.1056/NEJM199806183382501 | NCBI efetch (NEJM 1998;338(25):1785-1792) |
| IMPACT-II | 9164315 | 10.1016/s0140-6736(96)10172-0 | NCBI efetch (Lancet 1997;349(9063):1422-1428); DOI Crossref |
| ESPRIT 2000 | 11145489 | 10.1016/S0140-6736(00)03400-0 | NCBI efetch (Lancet 2000;356(9247):2037-2044) |
| SHOCK | 10460813 | 10.1056/NEJM199908263410901 | NCBI efetch (NEJM 1999;341(9):625-634) |

## Lotes seguintes (fila)

1. OASIS-1 permanece piloto — não promover
2. Magnésio do ISIS-4: abstract MEDLINE truncado — reler PDF/PMC antes de dump
3. Cangrelor: monografia já tem dump CHAMPION PHOENIX — não duplicar
4. WOEST — FA+PCI; AUGUSTUS da casa; território de arritmia na borda
5. MATRIX/HORIZONS: arquivo próprio — não duplicar
6. COMET / SENIORS / HYVET / OPTIME-CHF / ESCAPE / A-HeFT / ASCEND-HF: já na casa — não duplicar
7. DOSE/CARRESS / SOLOIST/SCORED / LIDO: dump combinado — não duplicar
8. Caravaggio/Hokusai / RALES+EMPHASIS / CONSENSUS+SOLVD+PARADIGM / CIBIS+MERIT+COPERNICUS / ONTARGET em RENAAL-IDNT: dumps combinados — não duplicar
## Lote 52 — 5 markdown (29/08/2026)

- `gusto-i-tpa-acelerado-versus-estreptoquinase` (PMID 8204123; morte 6,3% vs SK; mais AVC hemorrágico)
- `v-heft-i-hidralazina-dinitrato-versus-prazosina-e-placebo` (PMID 3520315; 2 anos P<0,028; seguimento total borderline)
- `v-heft-ii-enalapril-versus-hidralazina-dinitrato` (PMID 2057035; 2 anos P=0,016; morte total P=0,08)
- `target-tirofibana-nao-foi-nao-inferior-ao-abciximabe-na-icp` (PMID 11419425; NI falhou; margem ausente)
- `fluxograma-hidralazina-nitrato-vheft-aheft`

A-HeFT e PRAISE já na casa. PARAGON-B: caça TITLE 0 nesta sessão.

## PMIDs lote 52

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| GUSTO-I | 8204123 | 10.1056/NEJM199309023291001 | NCBI efetch (NEJM 1993;329(10):673-682) |
| V-HeFT I | 3520315 | 10.1056/NEJM198606123142404 | NCBI efetch (NEJM 1986;314(24):1547-1552) |
| V-HeFT II | 2057035 | 10.1056/NEJM199108013250502 | NCBI efetch (NEJM 1991;325(5):303-310) |
| TARGET | 11419425 | 10.1056/NEJM200106213442502 | NCBI efetch (NEJM 2001;344(25):1888-1894) |

## Lotes seguintes (fila)

1. OASIS-1 permanece piloto — não promover
2. Magnésio do ISIS-4: abstract MEDLINE truncado — reler PDF/PMC antes de dump
3. Cangrelor: monografia já tem dump CHAMPION PHOENIX — não duplicar
4. WOEST — FA+PCI; AUGUSTUS da casa; território de arritmia na borda
5. MATRIX/HORIZONS: arquivo próprio — não duplicar
6. COMET / SENIORS / HYVET / OPTIME-CHF / ESCAPE / A-HeFT / ASCEND-HF / PRAISE: já na casa — não duplicar
7. DOSE/CARRESS / SOLOIST/SCORED / LIDO: dump combinado — não duplicar
8. Caravaggio/Hokusai / RALES+EMPHASIS / CONSENSUS+SOLVD+PARADIGM / CIBIS+MERIT+COPERNICUS / ONTARGET em RENAAL-IDNT: dumps combinados — não duplicar
## Lote 53 — 6 markdown (29/08/2026)

- `epistent-stent-com-abciximabe-versus-stent-isolado-versus-balao` (PMID 9672272; era ticlopidina)
- `isar-react-abciximabe-na-icp-eletiva-apos-clopidogrel-600` (PMID 14724302; 4% vs 4%; P=0,82)
- `isar-react-2-abciximabe-na-icp-da-sca-sem-supra-apos-clopidogrel-600` (PMID 16533938; P=0,03; interação troponina P=0,07)
- `cappp-captopril-versus-diuretico-ou-betabloqueador-na-has` (PMID 10030325; primário NS; mais AVC)
- `prepic-filtro-de-veia-cava-permanente-na-tvp-proximal` (PMID 9459643; TEP dia 12 cai, TVP 2 a sobe; ≠ PREPIC2)
- `fluxograma-isar-react-abciximabe-apos-clopidogrel-600`

WARFASA/ASPIRE, GALACTIC-HF, VICTORIA, STOP-CA: já na casa.

## PMIDs lote 53

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| EPISTENT | 9672272 | 10.1016/s0140-6736(98)06113-3 | NCBI efetch (Lancet 1998;352(9122):87-92) |
| ISAR-REACT | 14724302 | 10.1056/NEJMoa031859 | NCBI efetch (NEJM 2004;350(3):232-238) |
| ISAR-REACT 2 | 16533938 | 10.1001/jama.295.13.joc60034 | NCBI efetch (JAMA 2006;295(13):1531-1538; NCT00133003) |
| CAPPP | 10030325 | 10.1016/s0140-6736(98)05012-0 | NCBI efetch (Lancet 1999;353(9153):611-616) |
| PREPIC | 9459643 | 10.1056/NEJM199802123380701 | NCBI efetch (NEJM 1998;338(7):409-415) |

## Lote 54 — 2 markdown (29/08/2026)

- `rapport-abciximabe-na-angioplastia-primaria-do-iam` (PMID 9727542; primário 6 meses P=0,97; não vender 30 d)
- `insight-nifedipina-gits-versus-co-amilozida-na-has-de-alto-risco` (PMID 10972368; primário P=0,35)

Patch: ISAR-REACT 3 → ISAR-REACT / ISAR-REACT 2.

## PMIDs lote 54

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| RAPPORT | 9727542 | 10.1161/01.cir.98.8.734 | NCBI efetch (Circulation 1998;98(8):734-741) |
| INSIGHT | 10972368 | 10.1016/S0140-6736(00)02527-7 | NCBI efetch (Lancet 2000;356(9227):366-372) |

## Lotes seguintes (fila)

1. OASIS-1 permanece piloto — não promover
2. Magnésio do ISIS-4: abstract MEDLINE truncado — reler PDF/PMC antes de dump
3. Cangrelor: monografia já tem dump CHAMPION PHOENIX — não duplicar
4. WOEST — FA+PCI; AUGUSTUS da casa; território de arritmia na borda
5. MATRIX/HORIZONS: arquivo próprio — não duplicar
6. COMET / SENIORS / HYVET / OPTIME-CHF / ESCAPE / A-HeFT / ASCEND-HF / PRAISE / GALACTIC-HF / VICTORIA / STOP-CA: já na casa — não duplicar
7. WARFASA/ASPIRE / AMPLIFY / EINSTEIN: dump combinado — não duplicar
8. PARAGON-B: caça TITLE 0 nesta sessão
## Lote 55 — 5 markdown (29/08/2026)

- `nordil-diltiazem-versus-diuretico-ou-betabloqueador-na-has` (PMID 10972367; primário P=0,97; AVC secundário)
- `stop-2-anti-hipertensivo-convencional-versus-novo-no-idoso` (PMID 10577635; primário P=0,89; IECA+BCC misturados)
- `convince-verapamil-coer-versus-atenolol-ou-hctz-na-has` (PMID 12709465; equivalência NÃO demonstrada; patrocinador parou)
- `scope-candesartana-no-idoso-com-has-leve-a-moderada` (PMID 12714861; primário P=0,19; cognição NS)
- `fluxograma-primeira-linha-cappp-nordil-insight-convince`

ANBP2 PMID 12584366 (NEJM) — fila lote 56. LIFE/VALUE/HYVET/HOT/INVEST já na casa.

## PMIDs lote 55

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| NORDIL | 10972367 | 10.1016/s0140-6736(00)02526-5 | NCBI efetch (Lancet 2000;356(9227):359-365) |
| STOP-2 | 10577635 | 10.1016/s0140-6736(99)10327-1 | NCBI efetch (Lancet 1999;354(9192):1751-1756) |
| CONVINCE | 12709465 | 10.1001/jama.289.16.2073 | NCBI efetch (JAMA 2003;289(16):2073-2082) |
| SCOPE | 12714861 | 10.1097/00004872-200305000-00011 | NCBI efetch (J Hypertens 2003;21(5):875-886) |

## Lotes seguintes (fila)

1. OASIS-1 permanece piloto — não promover
2. Magnésio do ISIS-4: abstract MEDLINE truncado — reler PDF/PMC antes de dump
3. Cangrelor: monografia já tem dump CHAMPION PHOENIX — não duplicar
4. WOEST — FA+PCI; AUGUSTUS da casa; território de arritmia na borda
5. MATRIX/HORIZONS: arquivo próprio — não duplicar
6. COMET / SENIORS / HYVET / OPTIME-CHF / ESCAPE / A-HeFT / ASCEND-HF / PRAISE / GALACTIC-HF / VICTORIA / STOP-CA: já na casa — não duplicar
7. WARFASA/ASPIRE / AMPLIFY / EINSTEIN: dump combinado — não duplicar
8. PARAGON-B: caça TITLE 0 nesta sessão
## Lote 56 — 3 markdown (29/08/2026)

- `anbp2-ieca-versus-diuretico-na-has-do-idoso` (PMID 12584366; HR 0,89; P=0,05; IC toca 1,00; interação sexo P=0,15)
- `stop-hypertension-tratamento-versus-placebo-aos-70-84-anos` (PMID 1682683; ≠ STOP-2)
- `mrc-idoso-diuretico-versus-betabloqueador-versus-placebo` (PMID 1445513; combinado mascara BB nulo)

## PMIDs lote 56

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ANBP2 | 12584366 | 10.1056/NEJMoa021716 | NCBI efetch (NEJM 2003;348(7):583-592) |
| STOP-Hypertension | 1682683 | 10.1016/0140-6736(91)92589-t | NCBI efetch (Lancet 1991;338(8778):1281-1285). Não é PMID 1677801. |
| MRC idoso | 1445513 | 10.1136/bmj.304.6824.405 | NCBI efetch (BMJ 1992;304(6824):405-412) |

## Lote 57 — 4 markdown (29/08/2026)

- `profess-telmisartana-precoce-apos-avc-isquemico` (PMID 18753639; primário P=0,23)
- `pats-indapamida-na-prevencao-secundaria-de-avc` (PMID 8575241; morte NS; DOI ausente; preliminar)
- `moses-eprosartana-versus-nitrendipina-pos-avc-eventos-recorrentes` (PMID 15879332; primário conta recorrentes)
- `fluxograma-pa-apos-avc-progress-profess-pats-moses`

Patches: STOP-2 → STOP-1; fluxograma PROGRESS → PRoFESS/PATS/MOSES.

## PMIDs lote 57

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| PRoFESS | 18753639 | 10.1056/NEJMoa0804593 | NCBI efetch (NEJM 2008;359(12):1225-1237; NCT00153062) |
| PATS | 8575241 | ausente | NCBI efetch (Chin Med J 1995;108(9):710-717); Crossref sem DOI do artigo |
| MOSES | 15879332 | 10.1161/01.STR.0000166048.35740.a9 | NCBI efetch (Stroke 2005;36(6):1218-1226) |

## Lote 58 — 4 markdown (29/08/2026)

- `transfer-ami-icp-rotineira-em-6-h-apos-fibrinolise` (PMID 19553646; composto P=0,004 inclui isquemia/IC; morte isolada ausente)
- `caress-in-ami-transferencia-imediata-apos-meia-reteplase-e-abciximabe` (PMID 18280326; n=600; inclui isquemia refratária)
- `prague-2-transporte-para-icp-primaria-versus-lise-no-hospital` (PMID 12559941; morte ITT P=0,12)
- `fluxograma-farmacoinvasiva-transfer-caress-stream-prague-2`

## PMIDs lote 58

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| TRANSFER-AMI | 19553646 | 10.1056/NEJMoa0808276 | NCBI efetch (NEJM 2009;360(26):2705-2718; NCT00164190) |
| CARESS-in-AMI | 18280326 | 10.1016/S0140-6736(08)60268-8 | NCBI efetch (Lancet 2008;371(9612):559-568; NCT00220571) |
| PRAGUE-2 | 12559941 | 10.1016/s0195-668x(02)00468-2 | NCBI efetch (Eur Heart J 2003;24(1):94-104) |

## Lote 59 — 3 markdown (29/08/2026)

- `atomic-ahf-omecamtiv-endovenoso-na-ic-aguda` (PMID 27012405; dispneia P=0,33; alta dose suplementar)
- `pep-chf-perindopril-no-idoso-com-ic-e-funcao-sistolica-preservada` (PMID 16963472; P=0,545; poder 35%)
- `fair-hf-carboximaltose-ferrica-sintomas-na-ic-com-deficiencia-de-ferro` (PMID 19920054; PGA/NYHA; morte não é primário)

## PMIDs lote 59

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| ATOMIC-AHF | 27012405 | 10.1016/j.jacc.2016.01.031 | NCBI efetch (JACC 2016;67(12):1444-1455; NCT01300013) |
| PEP-CHF | 16963472 | 10.1093/eurheartj/ehl250 | NCBI efetch (Eur Heart J 2006;27(19):2338-2345). Não é 16750680. |
| FAIR-HF | 19920054 | 10.1056/NEJMoa0908355 | NCBI efetch (NEJM 2009;361(25):2436-2448; NCT00520780) |

## Lote 60 — 3 markdown (29/08/2026)

- `smart-cristaloides-balanceados-versus-salina-no-critico` (PMID 29485925; MAKE-30 P=0,04; morte P=0,06; 1 centro)
- `plus-plasma-lyte-versus-salina-no-critico` (PMID 35041780; morte 90 d P=0,90)
- `basics-taxa-de-infusao-lenta-versus-rapida-no-desafio-volumico` (PMID 34547081; taxa, não tipo; P=0,46)

## PMIDs lote 60

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| SMART | 29485925 | 10.1056/NEJMoa1711584 | NCBI efetch (NEJM 2018;378(9):829-839; NCT02444988 / NCT02547779) |
| PLUS | 35041780 | 10.1056/NEJMoa2114464 | NCBI efetch (NEJM 2022;386(9):815-826; NCT02721654) |
| BaSICS taxa | 34547081 | 10.1001/jama.2021.11444 | NCBI efetch (JAMA 2021;326(9):830-838; NCT02875873) |

## Lote 61 — 4 markdown (29/08/2026)

- `basics-solucao-balanceada-versus-salina-no-critico` (PMID 34375394; morte 90 d P=0,47; MEDLINE pagina 1-12; Crossref start page 818)
- `split-cristaloide-tamponado-versus-salina-na-uti` (PMID 26444692; LRA P=0,77; morte hospitalar secundária P=0,40)
- `salt-ed-cristaloides-balanceados-versus-salina-no-adulto-nao-critico` (PMID 29485926; dias fora do hospital P=0,41; MAKE-30 secundário)
- `fluxograma-cristaloides-smart-plus-split-salt-ed-basics`

Patches: BaSICS taxa / SMART / PLUS → tipo de fluido e SALT-ED.

## PMIDs lote 61

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| BaSICS tipo | 34375394 | 10.1001/jama.2021.11684 | NCBI efetch (JAMA 2021;326(9); MEDLINE 1-12; Crossref start 818; NCT02875873) |
| SPLIT | 26444692 | 10.1001/jama.2015.12334 | NCBI efetch (JAMA 2015;314(16):1701-10; ACTRN12613001370796) |
| SALT-ED | 29485926 | 10.1056/NEJMoa1711586 | NCBI efetch (NEJM 2018;378(9):819-828; NCT02614040) |

## Lote 62 — 3 markdown (29/08/2026)

- `nordistemi-transferencia-imediata-apos-lise-em-area-rural` (PMID 19747792; primário P=0,19; 6% vs 16% secundário)
- `capital-ami-tnk-facilitada-versus-tnk-isolada` (PMID 16053952; n=170 vs TNK isolada, não vs ICP primária)
- `vmac-nesiritida-versus-nitroglicerina-na-ic-aguda` (PMID 11911755; PCWP/dispneia; mortalidade ausente)

Patch: fluxograma farmacoinvasiva → NORDISTEMI + CAPITAL-AMI. Combinado de vasodilatadores permanece `revisado` — conectividade só via source_refs do VMAC.

## PMIDs lote 62

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| NORDISTEMI | 19747792 | 10.1016/j.jacc.2009.08.007 | NCBI efetch (JACC 2010;55(2):102-10; NCT00161005) |
| CAPITAL-AMI | 16053952 | 10.1016/j.jacc.2005.04.042 | NCBI efetch (JACC 2005;46(3):417-24) |
| VMAC | 11911755 | 10.1001/jama.287.12.1531 | NCBI efetch (JAMA 2002;287(12):1531-40) |

## Lote 63 — 6 markdown (29/08/2026)

- `safe-albumina-4-versus-salina-na-uti` (PMID 15163774; morte 28 d P=0,87)
- `chest-amido-hidroxietilico-versus-salina-na-uti` (PMID 23075127; morte P=0,26; TRS P=0,04)
- `6s-amido-hidroxietilico-versus-ringer-acetato-na-sepse-grave` (PMID 22738085; morte 51% vs 43% P=0,03)
- `cristal-coloides-versus-cristaloides-no-choque-hipovolemico` (PMID 24108515, **não** 24154787; 28 d P=0,26; 90 d secundário)
- `albios-albumina-20-na-sepse-grave` (PMID 24635772; P=0,94)
- `fluxograma-coloides-safe-albios-chest-6s-cristal`

## PMIDs lote 63

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| SAFE | 15163774 | 10.1056/NEJMoa040232 | NCBI efetch (NEJM 2004;350(22):2247-56) |
| CHEST | 23075127 | 10.1056/NEJMoa1209759 | NCBI efetch (NEJM 2012;367(20):1901-11; NCT00935168) |
| 6S | 22738085 | 10.1056/NEJMoa1204242 | NCBI efetch (NEJM 2012;367(2):124-34; NCT00962156) |
| CRISTAL | 24108515 | 10.1001/jama.2013.280502 | NCBI efetch (JAMA 2013;310(17):1809-17; NCT00318942). 24154787 é ticagrelor vs prasugrel. |
| ALBIOS | 24635772 | 10.1056/NEJMoa1305727 | NCBI efetch (NEJM 2014;370(15):1412-21; NCT00707122) |

## Lote 64 — 1 markdown (29/08/2026)

- `gusto-iii-reteplase-versus-alteplase-acelerada-no-iam` (PMID 9340503; morte 30 d P=0,54)

Patches: GUSTO-I, GUSTO-V, fluxograma-lise.

## PMIDs lote 64

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| GUSTO-III | 9340503 | 10.1056/NEJM199710163371603 | NCBI efetch (NEJM 1997;337(16):1118-23) |

## Lote 65 — 4 markdown (29/08/2026)

- `care-pravastatina-pos-iam-com-colesterol-medio` (PMID 8801446; composto P=0,003; morte total NS)
- `lipid-pravastatina-na-dac-morte-coronariana-e-total` (PMID 9841303; morte coronariana e total)
- `afcaps-texcaps-lovastatina-na-prevencao-primaria-com-colesterol-medio` (PMID 9613910; inclui angina instável; morte ausente)
- `fluxograma-care-lipid-afcaps-morte-versus-composto`

4S/WOSCOPS combinado permanece `revisado`.

## PMIDs lote 65

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| CARE | 8801446 | 10.1056/NEJM199610033351401 | NCBI efetch (NEJM 1996;335(14):1001-9). Não é 8989104. |
| LIPID | 9841303 | 10.1056/NEJM199811053391902 | NCBI efetch (NEJM 1998;339(19):1349-57) |
| AFCAPS/TexCAPS | 9613910 | 10.1001/jama.279.20.1615 | NCBI efetch (JAMA 1998;279(20):1615-22) |

## Lote 66 — 2 markdown (29/08/2026)

- `cobalt-duplo-bolus-de-alteplase-nao-equivalente-a-infusao-acelerada` (PMID 9340504; equivalência falhou; parado)
- `inject-reteplase-versus-estreptoquinase-equivalencia` (PMID 7623530; DOI via Crossref)

## PMIDs lote 66

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| COBALT | 9340504 | 10.1056/NEJM199710163371604 | NCBI efetch (NEJM 1997;337(16):1124-30) |
| INJECT | 7623530 | 10.1016/s0140-6736(95)92224-5 | NCBI efetch (Lancet 1995;346(8971):329-36); DOI Crossref (ArticleIdList vazio) |

## Lotes seguintes (fila)

1. OASIS-1 permanece piloto — não promover
2. Magnésio do ISIS-4: abstract MEDLINE truncado — reler PDF/PMC antes de dump
3. Cangrelor: monografia já tem dump CHAMPION PHOENIX — não duplicar
4. WOEST — FA+PCI; AUGUSTUS da casa; território de arritmia na borda
5. MATRIX/HORIZONS: arquivo próprio — não duplicar
6. COMET / SENIORS / HYVET / OPTIME-CHF / ESCAPE / A-HeFT / ASCEND-HF / PRAISE / GALACTIC-HF / VICTORIA / STOP-CA / TRANSCEND: já na casa — não duplicar
7. WARFASA/ASPIRE / AMPLIFY / EINSTEIN / RE-COVER: dump combinado — não duplicar
8. PARAGON-B: caça TITLE 0 nesta sessão
9. EWPHE: esearch TITLE vazio — não inventar PMID. CARE/LIPID/AFCAPS escritos no lote 65 (PMID 8801446 / 9841303 / 9613910).
10. BLAST-AHF: esearch devolveu subanálise RELAX-AHF — não promover

## Push

`git push origin grok/science-continuous-prevalence-gaps-20260829`: **403** (Permission denied to rafaelpaesmeirelles). Conector GitHub `create_branch`: **403 Resource not accessible by integration**. Mesmo bloqueio da sessão overnight. Commits locais + bundle + HANDOFF. **Não foi aberto PR. Não houve merge. Não houve deploy.**

Bundle: `/tmp/meucardio/handoff/grok-science-continuous-prevalence-gaps-20260829.bundle` (regenerar após cada commit).

## Lote 67 — 10 markdown importados nesta sessão (29/08/2026)

Lacunas de lise clássica / CONSENSUS / DOSE / ONTARGET. **Não** reimportados: 4S/WOSCOPS/JUPITER, ALLHAT, SPRINT, ACCOMPLISH, SOAP II, PEITHO, CIBIS/MERIT/COPERNICUS (já tinham dump combinado ou dedicado).

- `gissi-1-estreptoquinase-ev-no-iam` (PMID 2868337)
- `isis-2-estreptoquinase-e-aas-no-iam-suspeito` (PMID 2899772)
- `assent-2-tenecteplase-versus-alteplase-no-iam` (PMID 10475182)
- `fluxograma-lise-gissi-1-isis-2-assent-2`
- `gissi-2-alteplase-versus-estreptoquinase-e-heparina-sc` (PMID 1975321)
- `isis-3-sk-versus-tpa-versus-apsac-e-heparina-subcutanea` (PMID 1347801; t-PA vs SK truncado)
- `fluxograma-lise-gissi-2-isis-3-gusto-i`
- `consensus-enalapril-na-ic-grave-nyha-iv` (PMID 2883575; complementar ao combinado CONSENSUS/SOLVD/PARADIGM)
- `dose-furosemida-bolus-versus-infusao-alta-versus-baixa-na-ic-aguda` (PMID 21366472)
- `ontarget-telmisartana-versus-ramipril-versus-combinacao` (PMID 18378520)

## Lote 71 — 8 markdown (29/08/2026)

DIG, RALES, ACCORD-BP e ASCOT-BPLA: dump já na casa — **não duplicar**.

- `late-alteplase-6-a-24-h-no-iam` (PMID 8103874; ITT NS)
- `emeras-estreptoquinase-tardia-no-iam-suspeito` (PMID 8103875; hospitalar NS)
- `fluxograma-lise-tardia-late-emeras`
- `on-time-2-tirofibana-pre-hospitalar-no-iamcsst-com-icp` (PMID 18707985; primário ST)
- `gracia-1-angiografia-rotineira-em-24-h-apos-lise` (PMID 15380963; morte/reinfarto P=0,07)
- `carress-hf-ultrafiltracao-versus-farmaco-escalonado-na-ic-aguda-cardiorrenal` (PMID 23131078; UF inferior)
- `unload-ultrafiltracao-versus-diuretico-ev-na-ic-aguda` (PMID 17291932; dispneia NS)
- `fluxograma-ultrafiltracao-unload-carress`

Patches: `fluxograma-lise-assent-3-gusto-v-extract`; `fluxograma-farmacoinvasiva-transfer-caress-stream-prague-2`.

## PMIDs lote 71

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| LATE | 8103874 | 10.1016/0140-6736(93)91538-w | NCBI efetch + Crossref. 8141717 é comentário. |
| EMERAS | 8103875 | 10.1016/0140-6736(93)91539-x | NCBI efetch + Crossref |
| On-TIME 2 | 18707985 | 10.1016/S0140-6736(08)61235-0 | NCBI efetch (Lancet 2008;372(9638):537-546) |
| GRACIA-1 | 15380963 | 10.1016/S0140-6736(04)17059-1 | NCBI efetch (Lancet 2004;364(9439):1045-1053) |
| CARRESS-HF | 23131078 | 10.1056/NEJMoa1210357 | NCBI efetch (NEJM 2012;367(24):2296-2304; NCT00608491) |
| UNLOAD | 17291932 | 10.1016/j.jacc.2006.07.073 | NCBI efetch (JACC 2007;49(6):675-683; NCT00124137) |

## Lote 72 — 6 markdown (29/08/2026)

PREPIC-2 e PREPIC já na casa — não duplicar. ISAR-COOL (cooling-off) já na casa.

- `on-time-1-tirofibana-pre-hospitalar-versus-na-sala-timi-3-ns` (PMID 15140531; primário TIMI 3 P=0,22; morte/IAM 7% vs 7%)
- `siam-iii-stent-imediato-versus-eletivo-em-2-semanas-apos-lise` (PMID 12932593; composto inclui TLR; n=197)
- `brave-2-icp-12-a-48-h-no-iamcsst-sem-sintoma-persistente` (PMID 15956631; SPECT sim; composto 30 d P=0,37)
- `pact-bolus-de-50-mg-de-tpa-antes-da-angioplastia` (PMID 10588209; perviedade sim; FE igual; ≠ PACT-HF)
- `fluxograma-gpi-pre-hospitalar-on-time-1-on-time-2`
- `fluxograma-lise-mais-cateter-pact-siam-gracia`

Patches: On-TIME 2; fluxograma farmacoinvasiva; fluxograma lise tardia.

## PMIDs lote 72

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| On-TIME 1 | 15140531 | 10.1016/j.ehj.2004.04.003 | NCBI efetch (Eur Heart J. 2004;25(10):837-846) |
| SIAM-III | 12932593 | 10.1016/s0735-1097(03)00763-0 | NCBI efetch (JACC 2003;42(4):634-641) |
| BRAVE-2 | 15956631 | 10.1001/jama.293.23.2865 | NCBI efetch (JAMA 2005;293(23):2865-2872) |
| PACT | 10588209 | 10.1016/s0735-1097(99)00444-1 | NCBI efetch (JACC 1999;34(7):1954-1962). ≠ PACT-HF. |

## Lote 73 — 6 markdown (29/08/2026)

- `air-pami-transferencia-para-icp-versus-lise-no-iam-de-alto-risco` (PMID 12039480; MACE P=0,331; n=138)
- `prague-1-transporte-para-icp-versus-lise-versus-lise-no-caminho` (PMID 10781354; composto 8/15/23%; ≠ PRAGUE-2)
- `pami-1-angioplastia-imediata-versus-tpa-no-iam` (PMID 8433725; morte P=0,06; composto hospitalar P=0,02)
- `zwolle-angioplastia-imediata-versus-estreptoquinase` (PMID 8433726; n=142; morte ausente no abstract)
- `gusto-iib-angioplastia-primaria-versus-tpa-acelerado` (PMID 9173270; composto 30 d P=0,033; morte P=0,37; 6 meses NS)
- `fluxograma-icp-primaria-versus-lise-pami-prague-air`

Patches: PRAGUE-2, DANAMI-2, GUSTO-IIb hirudina, fluxograma farmacoinvasiva.

## PMIDs lote 73

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| AIR-PAMI | 12039480 | 10.1016/s0735-1097(02)01870-3 | NCBI efetch (JACC 2002;39(11):1713-9) |
| PRAGUE-1 | 10781354 | 10.1053/euhj.1999.1993 | NCBI efetch (EHJ 2000;21(10):823-31) |
| PAMI-1 | 8433725 | 10.1056/NEJM199303113281001 | NCBI efetch (NEJM 1993;328(10):673-9) |
| Zwolle | 8433726 | 10.1056/NEJM199303113281002 | NCBI efetch (NEJM 1993;328(10):680-4) |
| GUSTO-IIb PCI | 9173270 | 10.1056/NEJM199706053362301 | NCBI efetch (NEJM 1997;336(23):1621-8). 9120173 é análise de custo do PAMI. |

## Lote 74 — 5 markdown (29/08/2026)

- `c-port-icp-primaria-em-hospital-sem-cirurgia-versus-tpa` (PMID 11960536; composto 6 meses P=0,03; morte P=0,72)
- `stat-stent-primario-versus-tpa-acelerado-n-123` (PMID 11263625; composto puxado por TVR; morte P=1,00)
- `captim-angioplastia-primaria-versus-fibrinolise-pre-hospitalar` (PMID 12243916; primário IC cruza 0)
- `west-tnk-com-ou-sem-invasao-versus-icp-primaria` (PMID 16757491; n=304 viabilidade)
- `fluxograma-lise-pre-hospitalar-captim-west-cport-stat`

Patches: fluxograma ICP vs lise; STREAM.

## PMIDs lote 74

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| C-PORT | 11960536 | 10.1001/jama.287.15.1943 | NCBI efetch (JAMA 2002;287(15):1943-51) |
| STAT | 11263625 | 10.1016/s0735-1097(00)01213-4 | NCBI efetch (JACC 2001;37(4):985-91) |
| CAPTIM | 12243916 | 10.1016/S0140-6736(02)09963-4 | NCBI efetch (Lancet 2002;360(9336):825-9) |
| WEST | 16757491 | 10.1093/eurheartj/ehl088 | NCBI efetch (EHJ 2006;27(13):1530-8) |

## Lote 75 — 6 markdown (29/08/2026)

Fora da lise. SELECT-D, CLOT, CATCH, ADAM-VTE, CLASSIC, CLOVERS já na casa.

- `hokusai-vte-cancer-edoxabana-versus-dalteparina` (PMID 29231094; composto NI; sangramento maior sobe)
- `caravaggio-apixabana-versus-dalteparina-no-tev-do-cancer` (PMID 32223112; recorrência NI; sangramento maior NS)
- `feast-bolus-de-fluido-aumenta-morte-em-crianca-africana` (PMID 21615299; bolus aumenta morte 48 h)
- `vanish-vasopressina-precoce-versus-noradrenalina-no-choque-septico` (PMID 27483065; primário renal NS; complementar ao dump VASST/ATHOS-3)
- `fluxograma-doac-versus-dalteparina-no-tev-do-cancer`
- `fluxograma-bolus-feast-versus-volume-adulto`

## PMIDs lote 75

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| Hokusai VTE Cancer | 29231094 | 10.1056/NEJMoa1711948 | NCBI efetch (NEJM 2018;378(7):615-624; NCT02073682) |
| CARAVAGGIO | 32223112 | 10.1056/NEJMoa1915103 | NCBI efetch (NEJM 2020;382(17):1599-1607; NCT03045406). 32365386 não é o paper. |
| FEAST | 21615299 | 10.1056/NEJMoa1101549 | NCBI efetch (NEJM 2011;364(26):2483-2495; ISRCTN69856593) |
| VANISH | 27483065 | 10.1001/jama.2016.10485 | NCBI efetch (JAMA 2016;316(5):509-518; ISRCTN20769191) |

## PAUSA 29/08/2026 20:34 -03

Produção interrompida a pedido. HEAD `85a71649` (lote 75). Sem lote 76. Sem push, sem PR, sem merge, sem deploy.

Pacote: `docs/PUBLICACAO-science-grok-20260829.md` + bundle `36a642e..85a71649` + zip `meucardio-grok-science-lotes-67-75-publicacao-20260829.zip`.

## Lote 76 — 6 markdown (29/08/2026, retomada)

CORTICUS e NICE-SUGAR só existiam em dump combinado. PROWESS-SHOCK era lacuna.

- `corticus-hidrocortisona-no-choque-septico` (PMID 18184957; morte 28 d NS)
- `prowess-shock-drotrecogina-alfa-no-choque-septico` (PMID 22616830; morte 28/90 d NS)
- `nice-sugar-controle-glicemico-intensivo-na-uti` (PMID 19318384; morte 90 d sobe)
- `leuven-insulina-intensiva-na-uti-cirurgica` (PMID 11794168; um centro)
- `fluxograma-esteroide-corticus-adrenal-aprocchss`
- `fluxograma-glicemia-leuven-versus-nice-sugar`

## PMIDs lote 76

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| CORTICUS | 18184957 | 10.1056/NEJMoa071366 | NCBI efetch NEJM 2008;358(2):111-124. 18971911 é revisão. |
| PROWESS-SHOCK | 22616830 | 10.1056/NEJMoa1202290 | NCBI efetch NEJM 2012;366(22):2055-2064. NCT00604214. |
| NICE-SUGAR | 19318384 | 10.1056/NEJMoa0810625 | NCBI efetch NEJM 2009;360(13):1283-1297. NCT00220987. |
| Leuven 2001 | 11794168 | 10.1056/NEJMoa011300 | NCBI efetch NEJM 2001;345(19):1359-1367. |

## Lote 77 — 4 markdown + patches (29/08/2026)

- `visep-insulina-intensiva-e-pentastarch-na-sepse-grave` (PMID 18184958; parou; sem taxa de morte no abstract)
- `glucontrol-insulina-intensiva-versus-alvo-intermediario` (PMID 19636533; parou; morte UTI 15,3% vs 17,2%)
- `leuven-2-insulina-intensiva-na-uti-medica` (PMID 16452557; ITT morte P=0,33)
- `fluxograma-visep-insulina-e-hes`

16608860 não é Leuven 2 (follow-up de cirurgia cardíaca).

## PMIDs lote 77

| Ensaio | PMID | DOI | Confirmação |
|---|---|---|---|
| VISEP | 18184958 | 10.1056/NEJMoa070716 | NCBI efetch NEJM 2008;358(2):125-139. NCT00135473. |
| Glucontrol | 19636533 | 10.1007/s00134-009-1585-2 | NCBI efetch ICM 2009;35(10):1738-1748. NCT00107601. |
| Leuven 2 (UTI médica) | 16452557 | 10.1056/NEJMoa052521 | NCBI efetch NEJM 2006;354(5):449-461. NCT00115479. |

## Encerramento final — 30/08/2026

Bundle final recebido no HEAD `258f4f387e284766ea73eb3bc939f8c7fa78f7d8`. A produção foi reconciliada contra a `main` `97899cf66f3d467cfefa3253d5f0f1e1a2258176`: 332 documentos inéditos foram preparados e 32 versões colidentes de conteúdo já publicado foram excluídas. Ver `docs/REVIEW-PUBLICACAO-GROK-20260830.md`.
