# Validação de conteúdo — registro adversarial

Este arquivo registra, rodada a rodada, a validação independente do conteúdo científico
publicado pelas duas sessões que escrevem em paralelo em `content/`, `evidencias/`,
`estudos/`, `casos-clinicos/`, `trilhas/`, `galeria/`, `exames/`. Método: adversarial —
tentando ENCONTRAR erro (PMID/DOI errado, número que não bate com a fonte, JSON quebrado,
dado sem `VERIFICAÇÃO HUMANA NECESSÁRIA` onde deveria ter), não confirmar que "parece
plausível". PMIDs conferidos via PubMed E-utilities (esearch/esummary/efetch) e, quando
necessário, DOI conferido via Crossref. Não corrijo os erros encontrados — só documento,
para a sessão orquestradora decidir.

---

## Rodada 1 — 07/08/2026

Estado do repositório: branch `agent/claude-continuacao-corvia` == `origin/main` no commit
`87d2108`. Sem rodada anterior registrada (primeiro arquivo). Validados os 3 commits de
conteúdo mais recentes de uma das duas sessões paralelas (a de `content/`+`evidencias/`+
`estudos/`).

### Commit `ea22393` — Cardiomiopatias (Takotsubo/InterTAK) + Doença coronariana (FFR/iFR, FAME 2 + DEFINE-FLAIR)

Arquivos: 2 documentos novos em `content/Cardiomiopatias/` e `content/Doença_coronariana/`.

**Conferido:**
- PMID 26332547 (Templin et al., InterTAK, NEJM 2015) — título, revista, volume/edição/páginas,
  DOI conferidos no PubMed: **batem**. Todos os números citados no documento (89,8% mulheres,
  idade média 66,8 anos, gatilho emocional 27,7% vs. físico 36,0%, 28,5% sem gatilho, doença
  neuro/psiquiátrica 55,8% vs. 25,7%, FEVE 40,7±11,2% vs. 51,5±12,3%, complicação grave p=0,93,
  MACCE 9,9%/paciente-ano, morte 5,6%/paciente-ano) — **conferidos contra o abstract original,
  batem exatamente**.
- PMID 22924638 (FAME 2, De Bruyne et al., NEJM 2012) — registro e todos os números (1220
  pacientes, 4,3% vs. 12,7%, HR 0,32 [0,19-0,53], urgente 1,6% vs. 11,1%, registro 3,0%) —
  **batem exatamente** com o abstract.
- PMID 29097450 (FAME 2, 3 anos, Fearon et al., Circulation 2018) — registro e números (MACE
  10,1% vs. 22,0%, urgente 4,3% vs. 17,2%, morte/IAM 8,3% vs. 10,4% p=0,28, custo $9.944 vs.
  $4.440 → $16.792 vs. $16.737 p=0,94, ICER $17.300/QALY em 2 anos e $1.600/QALY em 3 anos) —
  **batem exatamente**.
- PMID 28317458 (DEFINE-FLAIR, Davies et al., NEJM 2017) — registro e números (6,8% vs. 7,0%,
  diferença -0,2pp [IC95% -2,3 a 1,8], HR 0,95 [0,68-1,33] p=0,78) — **batem exatamente**.

**Resultado: PASSA integralmente.** Nenhum erro encontrado. Ambos os documentos marcam
`VERIFICAÇÃO HUMANA NECESSÁRIA` de forma apropriada (recomendação formal de diretriz não
verificada, tema "radial vs. femoral" registrado como não coberto).

### Commit `4f877f4` — Pericárdio, Perioperatório, Síncope, Valvopatias (4 documentos)

**Conferido:**
- PMID 10615077 (Sagristà-Sauleda et al., NEJM 1999, derrame pericárdico crônico idiopático) —
  registro e todos os números (1108 avaliados, 461 com derrame de grande volume, 28 incluídos,
  faixa 7-85 anos mediana 61, duração 6m-15a mediana 3a, 13/28 assintomáticos, tamponamento em
  8/29%, pericardiocentese em 24, resolução em 8, recidiva em 11, pericardiectomia em 5 precoce +
  20 no total, pressão intrapericárdica 4,75±3,79 mmHg, pressão transmural 1,0±2,50 mmHg, 10
  óbitos nenhum por causa pericárdica) — **batem exatamente** com o abstract original.
- PMID 27144849 (STICS, Zheng et al., NEJM 2016, rosuvastatina perioperatória) — registro e
  todos os números (1922 pacientes, FA-PO 21,1% vs. 20,5% OR 1,04 p=0,72, lesão miocárdica
  102 vs. 100 ng×h/mL diferença 1% p=0,80, excesso de LRA 5,4±1,9pp p=0,005) — **batem
  exatamente**.
- PMID 36562915 (Gopinathannair et al., marca-passo vs. cardioneuroablação) — registro e
  números (162 pacientes, CNA=61/PM=101, 39 CLS+38 RDR+24 *leadless*, 97% vs. 89%, HR ajustada
  0,27 [0,06-1,24] p=0,09) — **batem exatamente**. Nota: PubMed mostra "PubDate: 2025 Mar" (edição
  impressa) mas o documento cita "2022" — **não é erro**: é o ano do Epub (23/12/2022, confirmado
  no abstract), convenção normal de citação: `J Interv Card Electrophysiol. 2022;68(2):203-210`
  é exatamente como o próprio artigo se autocita no rodapé de copyright ("© 2022").
- PMID 31433493 (da Cunha et al., revisão sistemática CLS vs. RDR) — registro conferido, batem
  volume/edição/páginas/DOI.
- PMID 26718672 (EVEREST II 5 anos, Feldman et al., JACC 2015) — registro e todos os números
  (178:80 randomizados 2:1, desfecho composto 44,2% vs. 64,3% p=0,01, RM recorrente 12,3% vs.
  1,8% p=0,02, cirurgia 27,9% vs. 8,9% p=0,003, 78% das cirurgias em 6 meses, mortalidade 5 anos
  20,8% vs. 26,8% p=0,4) — **batem exatamente**.

**Resultado: PASSA integralmente.** Nenhum erro encontrado nos 4 documentos.

### Commit `384bcfb` — Aorta/DAP, Cardiopatias congênitas, Endocardite, Febre reumática (4 docs) + estudos/metadados.json (MAGPIE, PROGNOSIS, PARROT)

**Conferido:**
- PMID 29132880 (COMPASS, subestudo DAP, Anand et al., Lancet 2018) — registro e todos os
  números (7470 pacientes, riva 2,5mg+AAS vs. AAS: 5% vs. 7% HR 0,72 [0,57-0,90] p=0,0047,
  membro 1% vs. 2% HR 0,54 [0,35-0,82] p=0,0037; riva 5mg isolada: HR 0,86 [0,69-1,08] p=0,19 e
  HR 0,67 [0,45-1,00] p=0,05; sangramento maior 3% vs. 2% HR 1,61 [1,12-2,31] p=0,0089) — **batem
  exatamente**.
- PMID 32222135 (VOYAGER PAD, Bonaca et al., NEJM 2020) — registro e números (6564 pacientes,
  17,3% vs. 19,9% HR 0,85 [0,76-0,96] p=0,009, TIMI 2,65% vs. 1,87% HR 1,43 p=0,07, ISTH 5,94%
  vs. 4,06% HR 1,42 p=0,007) — **batem exatamente**. O subestudo de isquemia aguda de membro
  citado no texto (Hess CN et al., "Circulation 2021") **existe e os números batem** — localizado
  como PMID 34637332 (Circulation. 2021;144(23):1831-1841, DOI
  10.1161/CIRCULATIONAHA.121.055146): redução de 33% HR 0,67 [0,55-0,82] p=0,0001, benefício em
  30 dias HR 0,45 [0,24-0,85], mortalidade associada HR 2,59, amputação HR 24,87 — **todos batem
  exatamente**. Único reparo (menor, não é erro de fato): esse PMID **não está listado em
  `source_refs`** do documento, só citado em prosa sem referência formal — vale completar na
  próxima revisão, mas os números em si estão corretos.
- PMID 17446442 (AHA 2007, profilaxia de endocardite) e PMID 33853363 (AHA 2021, reafirmação) —
  registro de ambos conferido no PubMed, batem. O documento já declara `VERIFICAÇÃO HUMANA
  NECESSÁRIA` porque o texto integral de 17446442 não foi acessado (só resumos secundários
  convergentes) — postura correta, não tentei acessar o PDF pago nesta rodada por tempo, mas a
  lista de 4 categorias descrita bate com o conhecimento médico padrão desta diretriz.
- PMID 27623462 (TAVI, Regueiro et al., JAMA 2016) — registro e **todos** os números do
  documento (47 centros, 250 casos/20.006 pacientes, incidência 1,1%/pessoa-ano, idade mediana
  80, 64% homens, tempo mediano 5,3 meses, idade HR 0,97, sexo masc. HR 1,69, DM HR 1,52, RA
  residual HR 2,05, associada a cuidado de saúde 52,8%, enterococo 24,6%/S. aureus 23,3%,
  mortalidade intra-hospitalar 36%, cirurgia 14,8%, mortalidade 2 anos 66,7%, EuroSCORE OR 1,03,
  IC OR 3,36, LRA OR 2,70) — **batem exatamente**, número por número, com o abstract original.
- PMID 22965026 (IDSA 2012, faringite estreptocócica) — registro conferido, bate. Texto integral
  bloqueado para download (editora não libera XML completo via PMC/E-utilities, só abstract) —
  não consegui conferir as recomendações graduadas item a item contra o texto primário nesta
  rodada; o documento já declara ter feito dupla checagem contra fontes secundárias (não o
  primário), método aceitável mas **não totalmente verificado por mim**.
- **estudos/metadados.json — MAGPIE** (PMID 12057549): registro, DOI (conferido também via
  Crossref) e todos os números do campo `key_findings` (10.141 gestantes, 5071/5070, eclâmpsia
  40/4999 0,8% vs. 96/4993 1,9%, redução 58% IC 40-71, mortalidade RR 0,55 IC 0,26-1,14, óbito do
  bebê 12,7% vs. 12,4% RR 1,02 IC99% 0,92-1,14, descolamento RR 0,67 IC99% 0,45-0,89, efeitos
  colaterais 24% vs. 5%) — **batem exatamente**.
- **estudos/metadados.json — PROGNOSIS** (PMID 26735990): registro, DOI (Crossref confere) e
  todos os números (corte 38, VPN 99,3% IC 97,9-99,9, sensibilidade 80,0% IC 51,9-95,7,
  especificidade 78,3% IC 74,6-81,7, VPP 36,7% IC 28,4-45,7, sensibilidade 66,2%, especificidade
  83,1%) — **batem exatamente**.

**🚨 ERRO REAL ENCONTRADO — estudos/metadados.json, entrada PARROT (slug
`parrot-plgf-revelado-ao-clinico-na-pre-eclampsia-suspeita`):**
O campo `"doi": "10.1016/S0140-6736(19)30490-8"` está **errado**. Esse DOI resolve (conferido
via Crossref) para um artigo completamente diferente e não relacionado: *"Offline: Has global
health lost it?"*, um editorial do Lancet de março de 2019, **não** o artigo do PARROT. O PMID
no mesmo registro (`30948284`) está **correto** e aponta para o artigo certo (Duhig et al.,
Lancet 2019;393(10183):1807-1818) — conferido no PubMed, e o DOI verdadeiro desse artigo é
**`10.1016/S0140-6736(18)33212-4`** (confirmado via PubMed e Crossref). Todos os números do
campo `key_findings` desse mesmo registro (tempo mediano 4,1 vs. 1,9 dias, razão de tempo 0,36
IC95% 0,15-0,87 p=0,027, desfecho materno grave 24/447 5% vs. 22/573 4% OR 0,32 IC95% 0,11-0,96
p=0,043, perinatal 15% vs. 14%, IG 36,6 vs. 36,8 semanas) **batem exatamente** com o artigo
certo (PMID 30948284) — ou seja, o conteúdo textual foi escrito a partir da fonte certa, só o
campo `doi` foi digitado/gerado errado. **Ação recomendada:** corrigir o campo `doi` de
`estudos/metadados.json` no registro `parrot-plgf-revelado-ao-clinico-na-pre-eclampsia-suspeita`
para `10.1016/S0140-6736(18)33212-4`.

**Achado à parte, não deste commit (pré-existente) — duplicidade de estudo sob dois slugs:**
`estudos/metadados.json` tem **4 PMIDs duplicados**, cada um representando o mesmo estudo
cadastrado duas vezes com slugs diferentes (nenhum viola unicidade de slug, mas infla a
contagem de itens com conteúdo redundante):
- PMID `9462525` (Ben-Farhat, valvoplastia mitral): slugs
  `ben-farhat-valvoplastia-mitral-por-balao-versus-comissurotomia-cirurgica` (commit `63711a4`) e
  `ben-farhat-valvoplastia-por-balao-versus-comissurotomia-cirurgica-na-estenose-mitral` (commit
  `92fb6fa`).
- PMID `36036525` (INVICTUS): slugs `invictus-rivaroxabana-na-fibrilacao-atrial-da-valvopatia-reumatica`
  (`63711a4`) e `invictus-rivaroxabana-versus-varfarina-na-fa-da-cardiopatia-reumatica` (`92fb6fa`).
- PMID `30883052` (MOMENTUM 3): slugs `momentum-3-dispositivo-de-assistencia-ventricular-centrifugo-vs-axial`
  (`9a96dcd`/`051cc7a`) e `momentum-3-relatorio-final-dav-de-fluxo-centrifugo` (`3e55efe`).
- PMID `15659722` (SCD-HeFT): slugs `scd-heft-amiodarona-ou-cdi-na-insuficiencia-cardiaca`
  (`b0fbe93`/`b88c0ae`) e `scd-heft-cdi-vs-amiodarona-na-icfer` (`3e55efe`).

Nenhum desses 4 pares foi introduzido pelos commits validados nesta rodada — são de commits
anteriores (`63711a4`, `92fb6fa`, `9a96dcd`, `051cc7a`, `3e55efe`, `b0fbe93`, `b88c0ae`), fora do
escopo desta rodada de validação, mas registro aqui porque é um problema de qualidade de dado
real (contagem de itens inflada por duplicata de estudo, não por conteúdo novo) que a sessão
orquestradora deve avaliar — decidir se mantém os dois registros (ângulos de leitura diferentes)
ou consolida em um.

**JSON**: `python3 -c "import json; json.load(open('estudos/metadados.json'))"` — **válido**,
440 itens, 0 slugs duplicados, 4 PMIDs duplicados (ver acima).

---

## Rodada 2 — 07/08/2026 (mesmo dia, ciclo seguinte)

`git pull` trouxe 2 commits de conteúdo novos desde a rodada 1 (mais um commit de código,
`d2dd832`, fora do escopo).

### Commit `cbc9b02` — evidências: +9 recomendações GRADE/clássicas da Diretriz Brasileira de HP 2026 (SBPT)

**Conferido:**
- DOI `10.36416/1806-3756/e20250528` — resolvido via **Crossref**: título e autoria batem
  exatamente com o que o commit descreve (*"Brazilian guidelines for the pharmacological
  treatment of pulmonary hypertension..."*, Sociedade Brasileira de Pneumologia e Tisiologia,
  publicado 2026-06-10, container "Respiratory Research & Clinical Practice" — bate com a
  abreviação "Respir Res Clin Pract" usada no commit). **DOI real e correto.**
- A recomendação de troca para riociguate cita números de um ensaio específico (41% vs. 20%,
  OR 2,78 [1,53-5,06], p=0,007; piora clínica 1% vs. 9%, OR 0,10 [0,01-0,73], p=0,0047).
  Identifiquei a fonte desses números como o **ensaio REPLACE** (Hoeper MM et al., *Switching to
  riociguat versus maintenance therapy with phosphodiesterase-5 inhibitors...*, Lancet Respir Med
  2021;9(6), **PMID 33773120**) — não citado no `source_refs` do item (só a diretriz brasileira é
  citada), mas os números batem com o ensaio original **exceto um**:

**🚨 ERRO REAL ENCONTRADO — evidencias/metadados.json, item `hp-troca-para-riociguate-em-risco-intermediario`:**
O texto do `statement` diz **"p=0,007"** para o desfecho primário (45/111 vs. 23/113, OR 2,78,
IC95% 1,53-5,06). O abstract original do REPLACE (PMID 33773120) diz **"p=0·0007"** — uma ordem
de grandeza menor (mais significativo, não menos). Conferido diretamente no `efetch` do PubMed:
*"odds ratio [OR] 2·78 (95% CI 1·53-5·06; p=0·0007)"*. É erro de transcrição (um zero a menos),
não muda a direção da conclusão (ainda é resultado estatisticamente muito significativo), mas é
um número errado publicado como se fosse exato. O segundo número do mesmo item (piora clínica
1% vs. 9%, OR 0,10, IC95% 0,01-0,73, p=0,0047) **bate exatamente** com o abstract.
**Ação recomendada:** corrigir `p=0,007` para `p=0,0007` no `statement` do slug
`hp-troca-para-riociguate-em-risco-intermediario` em `evidencias/metadados.json`.

- Os demais 8 itens (terapia combinada inicial AMBITION, 3 recomendações negativas do grupo 2 —
  sildenafila/bosentana/macitentana —, e as 4 de terapia tripla/oxigenoterapia em escala
  Classe/Nível) não citam número duro de ensaio no `statement`, só classe/força e nível/qualidade
  — não há valor numérico adicional para conferir contra fonte externa nesta rodada; a
  classificação em si (Forte/Ponderado, Alta/Mod/Baixa/MtBx e Classe/Nível quando aplicável)
  não foi conferida linha a linha contra o texto integral da diretriz (não localizei o texto
  completo em acesso rápido nesta rodada — só o registro do DOI/Crossref).
- JSON: `python3 -c "import json; json.load(open('evidencias/metadados.json'))"` — válido.

### Commit `6d75f90` — trilhas: +10 novas (6 Cardiologia geriátrica, 4 Cardiologia pediátrica)

**Conferido:** JSON válido (483 itens, 0 slugs duplicados). As 10 trilhas novas somam 36 etapas
referenciando itens `documento`/`estudo`. Extraí a lista completa de slugs de `content/**/*.md`
(via front matter) e de `estudos/metadados.json`, e cruzei contra os 36 `item_slug` das 10 trilhas
novas: **0 referências quebradas** — todos os documentos e estudos citados existem no disco com o
slug exato usado na trilha. Não verifiquei separadamente o conteúdo clínico de cada documento
referenciado (seria reverificar dezenas de documentos já publicados por commits anteriores, fora
do escopo desta rodada) — só a integridade referencial da trilha em si, que é o que este tipo de
commit efetivamente adiciona (curadoria, não fato clínico novo).

### Commits mais antigos, também conferidos nesta janela de trabalho (antes do fim da rodada 1)

- **`b876fde` (galeria: +3 imagens — ECG hipercalemia, ECG HVE, US TVP)**: as 3 imagens foram
  abertas e inspecionadas visualmente. As 3 URLs de origem no Wikimedia Commons (`Hyperkalemia_ECG.jpg`,
  `E307_(CardioNetworks_ECGpedia).jpg`, `Ultrasonography_of_deep_vein_thrombosis_of_the_femoral_vein.jpg`)
  respondem 200 e **os metadados batem exatamente**: dimensões do arquivo de HVE (2015×1307)
  conferem com `data-file-width`/`data-file-height` da página do Commons; tamanho em bytes do
  arquivo de TVP (74.609 bytes) confere com o `contentSize` do JSON-LD da página; texto da licença
  e atribuição (CC BY 4.0/Agbayani-Gonzales, CC BY-SA 3.0/Rosengarten, CC0/Häggström) conferem
  com o texto da página de cada arquivo. O achado clínico descrito no `findings` de cada imagem é
  consistente com o que se vê na imagem (ondas T apiculadas difusas; QRS de alta voltagem
  precordial com padrão de strain; veia femoral superficial sem sinal de cor entre artéria
  (vermelho) e veia femoral profunda (azul) com fluxo). **PASSA.**
- **`d43468d` + `3b2084b` + `e499b1b` (evidências ESC 2021 prevenção CV — Saúde mental/tabagismo/
  reabilitação, PMID 34458905)**: registro do PMID conferido no PubMed — título, revista,
  volume/edição/páginas e DOI batem exatamente (`Eur Heart J. 2021;42(34):3227-3337`, DOI
  `10.1093/eurheartj/ehab484`). O único número duro citado num desses itens — o ensaio **SUPRIM**
  (redução de 41% no desfecho composto de DCVA, HR 0,59) — foi conferido contra o abstract
  original (Gulliksson et al., PMID 21263103, Arch Intern Med 2011): **41% e HR 0,59 [IC95%
  0,42-0,83] batem exatamente**. Não consegui acessar o texto integral da diretriz ESC 2021 (Oxford
  Academic bloqueia por 403, sem PMC direto — limitação já registrada váras vezes no CLAUDE.md
  deste projeto) para conferir linha a linha as demais 14 recomendações desses três commits contra
  a tabela original; as classes/níveis citados (I-A para cessação de tabagismo, IIa-A para reposição
  de nicotina/vareniclina/bupropiona, I-C/I-B/IIa-B para as de saúde mental) são plausíveis e
  consistentes com o que é de conhecimento médico padrão dessa diretriz, mas **não foram
  verificadas contra o texto primário nesta rodada** — registro como parcialmente verificado.

### Não verificado por falta de tempo nesta rodada
- Conteúdo do texto integral do IDSA 2012 (item a item das recomendações graduadas) — só o
  registro bibliográfico foi conferido, não as recomendações contra o PDF primário (bloqueado
  para download automatizado).
- Texto integral do AHA 2007 (17446442) contra a lista de 4 categorias — aceito por ora, dado que
  o próprio documento já sinaliza `VERIFICAÇÃO HUMANA NECESSÁRIA` para esse ponto específico.
- Texto integral da ESC 2021 de prevenção cardiovascular (34458905) contra as 15 recomendações dos
  commits `d43468d`/`3b2084b`/`e499b1b` — só o PMID/registro e um número (SUPRIM) foram conferidos.
- As 8 recomendações restantes de `cbc9b02` (HP 2026 SBPT) não tiveram a classificação
  Forte/Ponderado ou Classe/Nível conferida contra o texto integral da diretriz.
- Commit `051cc7a`, `97d639c`, `a7c275f`, `b88c0ae` (mais antigos) e toda a frente de
  `galeria/`+`exames/` mais antiga do segundo agente — ficam para a próxima rodada.

---

## Rodada 3 — 07/08/2026 (mesmo dia, ciclo seguinte)

`git fetch`/`merge` trouxe mais 2 commits de conteúdo desde a rodada 2 (mais mudanças locais
não commitadas de outra sessão em `frontend/src/pages/Agenda.tsx`, `Sincronizacao.tsx` e
`frontend/src/styles/shell.css` — código de outra sessão, deixado intocado, não é conteúdo e não
é minha frente).

### Commit `309cac7` — estudos: +6 ensaios pivotais de Diabetes e cardiologia (FLOW, DEVOTE, ORIGIN, REWIND, PROACTIVE, FREEDOM)

**Conferido — os 6 PMIDs batem exatamente** (título, revista, volume/edição/páginas, DOI, todos
conferidos no PubMed): FLOW 38785209, DEVOTE 28605603, ORIGIN 22686416, REWIND 31189511,
PROACTIVE 16214598, FREEDOM 23121323.

**Números conferidos linha a linha contra o abstract original, todos batendo exatamente:**
- **FLOW**: 331 vs. 410 eventos, HR 0,76 [0,66-0,88] p=0,0003; declínio de TFGe 1,16 mL/min/1,73m²
  p<0,001; morte CV HR 0,71 [0,56-0,89].
- **DEVOTE**: 325 (8,5%) vs. 356 (9,3%), HR 0,91 [0,78-1,06]; HbA1c 7,5±1,2% nos dois grupos;
  glicemia de jejum 128±56 vs. 136±57 mg/dL p<0,001; hipoglicemia grave 187 (4,9%) vs. 252 (6,6%).
- **REWIND**: 594 (12,0%) vs. 663 (13,4%), HR 0,88 [0,79-0,99] p=0,026; mortalidade 536 (10,8%) vs.
  592 (12,0%) HR 0,90 [0,80-1,01] p=0,067; evento GI 47,4% vs. 34,1% p<0,0001.
- **MINT** (citado em outro commit, ver abaixo) — não aplicável aqui.

**🔍 Achado positivo, não um erro — o item PROACTIVE flagra corretamente uma inconsistência real
do próprio abstract do PubMed.** O campo `limitations` diz que o abstract indexado registra
internação por IC como "6% (149 de 2.065)" no grupo pioglitazona, mas o mesmo resumo define esse
grupo com 2.605 pacientes — **conferido diretamente no `efetch`: a inconsistência existe de fato no
abstract original** ("6% (149 of 2065) and 4% (108 of 2633)... pioglitazone and placebo groups"),
não foi inventada pelo redator. O item marca isso com `VERIFICAÇÃO HUMANA NECESSÁRIA` em vez de
"corrigir" silenciosamente ou escolher um denominador — postura correta. Os demais números do
PROACTIVE (514/2605 vs. 572/2633, HR 0,90 [0,80-1,02] p=0,095; secundário 301 vs. 358, HR 0,84
[0,72-0,98] p=0,027) **batem exatamente** com o abstract.

**Resultado: PASSA integralmente**, com destaque positivo pela honestidade do PROACTIVE.

### Commit `3557cbc` — casos-clinicos: +7 novos (IC x2, Terapia intensiva x3, Hipertensão pulmonar x2)

**Conferido — os 9 PMIDs citados nos 7 casos batem exatamente** no registro do PubMed: HFA-PEFF
31504452, amiloidose ATTR (Ruberg & Berk) 22949539, MINT 37952133, REALITY 33560322, VANCS
27841822, POCUS choque (meta-análise) 37231510, POCUS derrame pericárdico 33538920, esquistossomose
HAP Brasil 31720370, e o PMCID 11932222 (revisão sistemática de HAP esquistossomótica, sem PMID
próprio — conferido via `esummary db=pmc`, título bate exatamente).

**Números conferidos contra os abstracts originais:**
- **MINT**: 295/1749 (16,9%) vs. 255/1755 (14,5%), RR 1,15 [0,99-1,34] p=0,07 — a explicação do
  caso ("intervalo de confiança tangenciando a significância... sem cruzar de forma inequívoca")
  descreve corretamente esse resultado limítrofe.
- **VANCS**: 330 randomizados, 300 infundidos (149 vasopressina/151 noradrenalina) — bate
  exatamente. O desfecho composto do abstract (32% vs. 49%, HR 0,55 [0,38-0,80] p=0,0014) é mais
  forte do que o texto do caso sugere ("menor taxa", sem citar a magnitude) — não é erro, é
  descrição qualitativa compatível, só não reproduz o número exato do HR no corpo do caso (o
  case não afirma nenhum valor numérico falso, então não conta como erro, só como detalhe
  omitido).
- **HFA-PEFF**: descrição do algoritmo (Etapa P/E/F1/F2, faixas de pontuação 0-1/2-4/≥5) consistente
  com o que é publicamente conhecido da diretriz; não confrontei linha a linha contra o texto
  integral nesta rodada (Oxford Academic, mesmo bloqueio de 403 já registrado no projeto).

**Resultado: PASSA.** Nenhum erro de PMID, DOI ou número encontrado nos 7 casos.

### Não verificado por falta de tempo nesta rodada (rodada 3)
- HFA-PEFF: descrição do algoritmo não conferida linha a linha contra o texto integral (bloqueio
  de acesso conhecido do projeto a `academic.oup.com`).
- Descrição fisiopatológica do caso de amiloidose (triagem hematológica antes de PYP) e do caso de
  POCUS (achados ecocardiográficos/pulmonares) — são afirmações de conhecimento médico geral
  amplamente replicado na literatura, não checadas frase a frase contra a fonte primária citada.
- Commits mais antigos ainda não revisados (`051cc7a`, `97d639c`, `a7c275f`, `b88c0ae`) e toda a
  frente mais antiga de `galeria/`/`exames/` do segundo agente — seguem para a próxima rodada.

---

## Rodada 4 — 07/08/2026 (mesmo dia, ciclo seguinte)

### Commit `0cd86cb` — evidências: +6 recomendações Classe/Nível (ESC) para o tema Calculadoras (HCM Risk-SCD + STS-PROM/EuroSCORE II)

**Conferido:**
- PMID 37622657 (ESC 2023 Guidelines for the management of cardiomyopathies) — registro
  (título/revista/volume/edição/páginas/DOI) confere exatamente no PubMed. **Sem PMC** disponível
  (`elink` não devolve `pubmed_pmc`) — não consegui conferir as 4 recomendações de HCM Risk-SCD
  linha a linha contra o texto integral nesta rodada (mesmo bloqueio de `academic.oup.com` já
  registrado no projeto).
- PMID 34453165 (ESC/EACTS 2021 valvopatias) — o commit cita a fonte como PMCID 9725093, sem PMID
  próprio no texto; localizei o PMID correspondente (34453165, Eur Heart J. 2022;43(7):561-632) e
  confirmei que **título/revista/volume/edição/páginas batem exatamente** com a citação do commit.
  **Texto integral acessado** via PMC (aberto), permitindo conferência real, não só de registro.

**🚨 ERRO REAL ENCONTRADO — evidencias/metadados.json, item
`estenose-aortica-tavi-recomendada-em-idoso-ou-alto-risco-sts-prom`:**
O item grava `"evidence_level": "B"` para a recomendação *"TAVI is recommended in older patients
(≥75 years), or in those who are high risk (STS-PROM/EuroSCORE II >8%) or unsuitable for
surgery"*. **Conferido no HTML da tabela original do PMC** (célula de nível de evidência com cor
de fundo distinta, lida da estrutura `<tr><td>...recomendação...</td><td>I</td><td>A</td></tr>`):
a diretriz atribui a essa recomendação **Classe I, Nível A** — não Nível B. O nível correto é
**A**, não B. (A recomendação irmã de SAVR, no mesmo item de tabela — *"SAVR is recommended in
younger patients who are low risk for surgery (<75 years and STS-PROM/EuroSCORE II <4%)..."* —
está corretamente gravada como Classe I/Nível B no item `estenose-aortica-savr-recomendada-em-jovem-baixo-risco-cirurgico-sts-prom`, conferido contra a mesma tabela: bate.)
**Ação recomendada:** corrigir `evidence_level` de `"B"` para `"A"` no slug
`estenose-aortica-tavi-recomendada-em-idoso-ou-alto-risco-sts-prom` em `evidencias/metadados.json`.

**As 4 recomendações de HCM Risk-SCD (alto risco IIa/B, intermediário IIb/B, baixo risco com LGE
extenso IIb/B, prevenção secundária I/B) não foram conferidas contra o texto integral** — sem
acesso ao PMC/PDF da diretriz ESC 2023 nesta rodada. Ficam como não verificadas, não como
confirmadas.

- JSON: `python3 -c "import json; json.load(open('evidencias/metadados.json'))"` — válido.

### Não verificado por falta de tempo nesta rodada (rodada 4)
- As 4 recomendações de HCM Risk-SCD do commit `0cd86cb`, contra o texto integral da ESC 2023 de
  cardiomiopatias (sem PMC aberto, acesso bloqueado nesta rodada).
- Commits mais antigos ainda não revisados (`051cc7a`, `97d639c`, `a7c275f`, `b88c0ae`) e toda a
  frente mais antiga de `galeria/`/`exames/` do segundo agente.

---

## Rodada 5 — 07/08/2026 (mesmo dia, ciclo seguinte)

### Commit `cc4d367` — estudos: +6 ensaios/estudos de Comunicação clínica

**Conferido: os 7 PMIDs citados (incluindo a réplica de Schwartz, PMID 10413743) batem exatamente**
no registro do PubMed (título/revista/volume/edição/páginas/DOI). Números conferidos linha a linha
contra os abstracts originais, **todos batendo exatamente**: Jabre (211/266 79% vs. 131/304 43%,
OR ajustada 1,7 [1,2-2,5] p=0,004; OR 1,6 [1,1-2,5] p=0,02), REACT (mediana basal 140 min, -4,7%/ano
vs. -6,8%/ano p=0,54; efeito líquido de uso de EMS 20% [7-34%] p<0,005), Schulman 1999 (64,1% vs.
69,2% p<0,001; OR 0,60 [0,4-0,9] p=0,02 para sexo e raça; OR 0,4 [0,2-0,7] p=0,004 para interação
raça×sexo). **PASSA integralmente.**

### Commit `392a365` — evidências: +4 recomendações Classe/Nível de Comunicação clínica (ESC 2023 SCA + ESC 2020 esporte)

**Conferido:** PMID 32860412 (ESC 2020 esporte) e o DOI `10.1093/eurheartj/ehad191` (ESC 2023 SCA,
conferido via Crossref) batem exatamente com as citações do commit. **As 4 classificações
Classe/Nível (I/C, IIa/C ×3) não foram conferidas contra o texto integral** — as duas diretrizes
estão atrás do bloqueio de 403 do Oxford Academic já registrado no projeto, e não localizei PMC
aberto para nenhuma das duas nesta rodada.

### Commit `ec5481d` — casos-clinicos: +8 novos (Cardio-oncologia, Gravidez, Hipertensão, Arritmias)

**Conferido: 15 dos 16 PMIDs citados nos 8 casos batem exatamente** no registro do PubMed
(título/revista/volume/edição/páginas/DOI): 5-FU vasoespasmo (33817666, 29977352), tríade
miocardite-miosite-miastenia (30089619, 29567210, 36017568), SCAD gestacional (28728686, 34001675),
cesárea perimortem/Katz (15970850), alcaçuz/pseudo-hiperaldosteronismo (31379750, 34362360),
PRESCRIPT/feocromocitoma (31714582 — número de pacientes, 134, conferido exatamente; 24893135),
cardite de Lyme (30765038, 2644885), RIVA (6849238; 32119407 é referência StatPearls sem DOI, só
PMID, e o PMID confere no registro do PubMed apesar de não ter metadados de revista/página —
comportamento esperado de verbete StatPearls).

**🚨 ERRO REAL ENCONTRADO — casos-clinicos/metadados.json, caso
`bloqueio-atrioventricular-total-em-jovem-com-artralgia-migratoria-cardite-de-lyme`:**
O `source_refs` cita *"Besant G, Wan D, Yeung C, et al. Suspicious index in Lyme carditis...
Clin Cardiol. 2018;41(12):1611-1616. **DOI: 10.1002/clc.23112**. PMID: 30350436"*. **O PMID está
correto** (confere no PubMed, título/revista/páginas batem). **O DOI está errado**: o registro do
PubMed para o PMID 30350436 mostra DOI **`10.1002/clc.23102`** (não 23112), confirmado também via
Crossref — `10.1002/clc.23102` resolve para o artigo certo de Lyme carditis, enquanto
`10.1002/clc.23112` (o DOI usado no commit) resolve, via Crossref, para um artigo **completamente
diferente e não relacionado**: *"Design of the randomized, placebo-controlled evolocumab for early
reduction of LDL-cholesterol levels... (EVOPACS) trial"*, também publicado em Clinical Cardiology
— mesmo padrão de erro do DOI do PARROT encontrado na Rodada 1 (dígito transposto num DOI da mesma
revista). **Ação recomendada:** corrigir o campo DOI de `10.1002/clc.23112` para `10.1002/clc.23102`
no `source_refs` do caso `bloqueio-atrioventricular-total-em-jovem-com-artralgia-migratoria-cardite-de-lyme`
em `casos-clinicos/metadados.json`.

**Resultado geral do commit: passa quanto a PMIDs e conteúdo clínico; 1 DOI incorreto encontrado
(reportado acima).**

### Não verificado por falta de tempo nesta rodada (rodada 5)
- As 4 classificações Classe/Nível do commit `392a365` contra o texto integral das duas diretrizes
  (bloqueio de acesso).
- Descrições fisiopatológicas dos casos de vasoespasmo por 5-FU, tríade autoimune por checkpoint,
  SCAD gestacional, pseudo-hiperaldosteronismo por alcaçuz e RIVA — checadas quanto a PMID/DOI, não
  frase a frase contra o texto integral de cada fonte.
- Commits mais antigos ainda não revisados (`051cc7a`, `97d639c`, `a7c275f`, `b88c0ae`) e toda a
  frente mais antiga de `galeria/`/`exames/` do segundo agente.

---

## Rodada 6 — 07/08/2026 (backlog mais antigo, sem commits novos no momento do ciclo)

Sem commits de conteúdo novos desde a rodada 5 neste ciclo — usei a janela de espera para revisar
parte do backlog mais antigo sinalizado nas rodadas anteriores.

### Commit `b88c0ae` — sincroniza 183 itens JSON e 42 documentos de content (commit grande, 8.206 inserções)

**Verificação parcial, por amostragem** — commit grande demais para adversarial completo linha a
linha no tempo desta rodada. Dois documentos de `content/Doença_coronariana/` foram escolhidos por
densidade numérica (mais fácil de errar) e verificados **linha a linha contra os abstracts
originais**:

- **`revascularizacao-completa-versus-somente-lesao-culpada-no-iam-multiarterial-o-ensaio-complete.md`**
  (ensaio COMPLETE, PMID 31475795): registro bate exatamente; números do desfecho coprimário 1
  (7,8% vs. 10,5%, p=0,004) e 2 (8,9% vs. 16,7%, p<0,001) batem exatamente com o abstract. **Os
  números de HR por momento de revascularização (0,77 [0,59-1,00] durante a internação; 0,69
  [0,49-0,97] após a alta) também batem exatamente** — mas contra um **artigo complementar** (Wood
  DA et al., JACC 2019, PMID 31779786) **não listado no `source_refs`** do documento (só a NEJM
  principal é citada). Não é fabricação (os números batem com a fonte real), é lacuna de citação —
  quem checar `source_refs` sozinho não vai achar a fonte desse detalhe específico.
- **`choque-cardiogenico-na-sindrome-coronariana-aguda-culprit-shock-e-iabp-shock-ii.md`**
  (CULPRIT-SHOCK PMID 29083953 + seguimento 1 ano PMID 30145971 + IABP-SHOCK II PMID 22920912 +
  Lancet 12 meses PMID 24011548): **todos os 4 PMIDs batem exatamente** no registro do PubMed, e
  **todos os números conferidos batem exatamente** com os abstracts: CULPRIT-SHOCK 45,9%/158/344
  vs. 55,4%/189/341 RR 0,83 [0,71-0,96] p=0,01; morte RR 0,84 [0,72-0,98] p=0,03; 1 ano 50,0% vs.
  56,9% RR 0,88 [0,76-1,01]; revascularização repetida 32,3% vs. 9,4% RR 3,44; reinternação por IC
  5,2% vs. 1,2% RR 4,46; IABP-SHOCK II 39,7%/119/300 vs. 41,3%/123/298 RR 0,96 [0,79-1,17] p=0,69,
  e todos os desfechos secundários (sangramento, isquemia periférica, sepse, AVC). **Boa prática
  observada**: o documento marca `VERIFICAÇÃO HUMANA NECESSÁRIA` explicitamente para os
  percentuais exatos de 12 meses do Lancet 2013, que não foram extraídos diretamente — em vez de
  inventar ou aproximar. **PASSA integralmente**, com destaque positivo.

**Resultado da amostra: PASSA**, com uma lacuna de citação menor (não erro de fato) no documento do
COMPLETE. As 40 demais entradas de `content/` e as ~140 entradas das frentes JSON deste commit
**não foram verificadas** nesta rodada — fica pendente para quem continuar.

### Commit `051cc7a` — estudos: +13 ensaios pivotais em temas mais rasos

**Conferido: os 13 PMIDs batem exatamente** no registro do PubMed (DELIVER 36027570, ENGAGE
AF-TIMI 48 24251359, LEADER 27295427, PATENT-1 23883378, MOMENTUM 3 30883052, PADIS-PE 26151264,
ProCESS 24635773, POG 9404 26700126, Statin Choice 17533211, validação Pooled Cohort Equations
24682252, PARTITA 35369700, PURE 31492503, UPBEAT 22858387).

**Números da entrada MOMENTUM 3 (slug `momentum-3-dispositivo-de-assistencia-ventricular-centrifugo-vs-axial`)
conferidos contra o abstract original: batem exatamente** (76,9% vs. 64,8% RR 0,84 [0,78-0,91]
p<0,001; substituição de bomba 2,3% vs. 11,3% RR 0,21 [0,11-0,38] p<0,001).

**🔁 Confirma e localiza a origem de uma das 4 duplicatas de PMID já registradas na Rodada 1**: esta
entrada (`momentum-3-dispositivo-de-assistencia-ventricular-centrifugo-vs-axial`, introduzida neste
commit `051cc7a`) e a entrada `momentum-3-relatorio-final-dav-de-fluxo-centrifugo` (introduzida
antes, no commit `3e55efe`) citam **o mesmo PMID/DOI** (30883052 /
`10.1056/NEJMoa1900486`) — são o mesmo artigo ("A Fully Magnetically Levitated Left Ventricular
Assist Device - Final Report", NEJM 2019) cadastrado duas vezes sob títulos ligeiramente diferentes
("...versus axial" vs. "(relatório final)..."). Não é erro de fato (os números da nova entrada
batem com a fonte real) — é duplicata de conteúdo, já registrada como achado da Rodada 1 e agora
confirmada como tendo entrado por este commit específico.

**Resultado: PASSA quanto a exatidão de PMID/número; confirma duplicata já registrada.** Os outros
9 estudos deste commit (exceto MOMENTUM 3) não tiveram os números do `key_findings` conferidos
linha a linha nesta rodada, só o registro do PMID.

### Commits `97d639c` e `a7c275f` — material-paciente e checklists (7 itens, derivados de documento já publicado)

Ambos os commits declaram explicitamente que os itens **não introduzem fonte nova** — são
reformulações de documentos já verificados e publicados em `content/`, para os formatos de
material do paciente e checklist de alta. **JSON válido** nos dois
(`python3 -c "import json; json.load(open('material-paciente/metadados.json'))"` e o mesmo para
`checklists/metadados.json`). Não conferi se os `documento_slug`/`documento_origem` referenciados
realmente existem e estão publicados (checagem de integridade referencial, não de fato clínico) —
fica para a próxima rodada.

### Não verificado por falta de tempo nesta rodada (rodada 6)
- 40 dos 42 documentos de `content/` e a maior parte das ~140 entradas JSON do commit `b88c0ae`
  (só 2 documentos verificados por amostragem).
- 9 dos 13 estudos do commit `051cc7a` (só MOMENTUM 3 teve os números conferidos).
- Integridade referencial dos 7 itens de `97d639c`/`a7c275f` contra os documentos de origem.

---

## Rodada 7 — 07/08/2026

### Commit `9f03e46` — Gravidez: +8 evidências (ACC/AHA 2022 doença aórtica, gestação/aortopatia) + 3 estudos

**Destaque de qualidade nesta rodada.** PMID 36322642 (2022 ACC/AHA Guideline for the Diagnosis and
Management of Aortic Disease) confere exatamente no PubMed, e **o PMC9876736 citado é real e foi
acessado por completo** (texto integral aberto). **As 8 recomendações Classe/Nível foram conferidas
PALAVRA POR PALAVRA contra a tabela original da diretriz — todas batem exatamente**, inclusive
classe, nível de evidência e os cortes numéricos em cm:
- *"In pregnant patients with a history of chronic aortic dissection, cesarean delivery is
  recommended"* — I/C-EO ✓
- *"...aortic diameter of <4.0 cm, vaginal delivery... is recommended"* — I/C-EO ✓
- *"...≥4.5 cm, cesarean delivery is reasonable"* — IIa/C-EO ✓
- *"...4.0 cm to 4.5 cm, vaginal delivery with regional anesthesia, expedited second stage, and
  assisted delivery may be reasonable"* — IIb/C-EO ✓
- *"...syndromic and nsHTAD, and a diameter... of 4.0 cm to 4.5 cm, cesarean delivery may be
  considered"* — IIb/C-EO ✓
- *"Marfan syndrome and an aortic root diameter of >4.5 cm, aortic surgery before pregnancy is
  recommended"* — I/C-LD ✓
- *"...4.0 cm to 4.5 cm, aortic surgery before pregnancy may be considered, especially... rapid
  aortic growth of ≥0.3 cm/y or a family history of aortic dissection"* — IIb/C-LD ✓ (limiar de
  crescimento e histórico familiar batem literalmente)
- Vigilância ecocardiográfica "a cada trimestre" — confirmado no corpo do texto da diretriz.

**Os 3 estudos** (REBECGA PMID null/DOI `10.36660/abc.20240807i`, Pillarisetti 2014 PMID 24814494,
Hosseinpour 2022 PMID 35883253) — **todos os PMIDs/DOI batem exatamente**. Números do Pillarisetti
conferidos linha a linha: **batem exatamente** (100 pacientes, 55%/39%/6% por raça, idade 30±6,
FEVE 28±9%, 42% melhora, HR 3,0 p=0,01 pós-parto, HR 2,2 p=0,01 raça, mortalidade 15% vs. 5%
p=0,1, ICD em 12% dos sem melhora). **Boa prática destacada**: para o REBECGA, sem PMID indexado no
PubMed, o campo foi gravado como `"pmid": null` em vez de omitido ou inventado, com o DOI
confirmado de forma independente no Crossref (conferido aqui também: resolve para o artigo certo,
"REBECGA: Brazilian Registry of Heart Disease and Pregnancy...", Arq Bras Cardiol 2025).

**Resultado: PASSA integralmente, com destaque positivo pela exatidão literal das 8 recomendações
Classe/Nível.**

### Commit `a093e2a` — estudos: +5 estudos de Saúde mental e cardiologia (INTERHEART, Mostofsky, Kivimäki, SUPRIM, Roest)

**Conferido: os 5 PMIDs batem exatamente** no registro do PubMed (INTERHEART 15364185, Mostofsky
2012 22230481, Kivimäki 2012 22981903, SUPRIM 21263103, Roest 2010 20620715). **Números conferidos
linha a linha contra os abstracts, todos batendo exatamente**: Mostofsky (270/1985 13,6%, 19 em 1
dia, incidência elevada 21,1× [13,1-34,1], risco absoluto 1/1394 vs. 1/320), Kivimäki (197.473
participantes, 30.214/15% job strain, 2358 eventos, HR 1,23 [1,10-1,37], publicados 1,43 vs. não
publicados 1,16, exclusão 3 anos 1,31 e 5 anos 1,30, PAR 3,4%) — **um número do Kivimäki não pôde
ser conferido contra o abstract** (HR ajustado multivariável completo 1,17 [1,05-1,31], que a
entrada cita mas não aparece no resumo indexado, só o HR ajustado por idade/sexo de 1,23 aparece —
não é contraditório, só não verificável só pelo abstract, provavelmente do corpo do artigo).

**🔁 Novo caso de duplicata de PMID, mesmo padrão dos 4 já registrados na Rodada 1 e o MOMENTUM 3 da
Rodada 6**: PMID 15364185 (INTERHEART) agora aparece **duas vezes** em `estudos/metadados.json`,
sob slugs diferentes — `interheart-fatores-de-risco-modificaveis-para-infarto-no-mundo` (já
existente, sincronizada por `b88c0ae`/`b0fbe93`) e `interheart-fator-psicossocial-risco-de-infarto`
(nova, introduzida por este commit `a093e2a`). São o mesmo estudo (mesmo PMID/DOI) cadastrado duas
vezes com ângulos de leitura diferentes (fatores de risco em geral vs. recorte psicossocial
específico) — não é erro de fato (os números da nova entrada batem com a fonte real), é o mesmo
padrão de duplicação de conteúdo já sinalizado à sessão orquestradora. `estudos/metadados.json`
passou de 4 para **5 PMIDs duplicados** com este commit.

**Resultado: PASSA quanto a exatidão de PMID/números; acrescenta uma 5ª duplicata de estudo à lista
já registrada.**

### Commit `311ffce` — casos-clinicos: +10 novos (Comunicação clínica, Farmacologia, Geral, Saúde mental, Calculadoras)

**Verificação leve, por falta de tempo**: os 18 PMIDs citados nos 10 casos foram checados **apenas
quanto a existência/registro** (não os números do corpo do caso) — todos resolvem a registros reais
no PubMed, incluindo dois PMIDs de 8 dígitos incomuns (41277145, 42471187) que **conferem como
publicações reais de 2026** ("Systematic Review and Meta-Analysis of Mortality in Patients With
Anorexia Nervosa", Int J Eat Disord 2026; "Association of lithium treatment with incident
cardiovascular disease...", J Affect Disord 2026) — não são PMID inventado, é só o número de
identificação já ter avançado bastante em 2026. **Números do corpo de cada caso não foram
conferidos nesta rodada.**

### JSON válido (confirmado após as 3 rodadas de commits)
`python3 -c "import json; json.load(open('estudos/metadados.json'))"` e o mesmo para
`evidencias/metadados.json` e `casos-clinicos/metadados.json` — todos válidos.

### Não verificado por falta de tempo nesta rodada (rodada 7)
- Números do corpo dos 10 casos clínicos do commit `311ffce` contra as fontes citadas.
- O restante do backlog mais antigo (40 documentos de `b88c0ae`, 9 estudos de `051cc7a`).

---
