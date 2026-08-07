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

### Não verificado por falta de tempo nesta rodada
- Conteúdo do texto integral do IDSA 2012 (item a item das recomendações graduadas) — só o
  registro bibliográfico foi conferido, não as recomendações contra o PDF primário (bloqueado
  para download automatizado).
- Texto integral do AHA 2007 (17446442) contra a lista de 4 categorias — aceito por ora, dado que
  o próprio documento já sinaliza `VERIFICAÇÃO HUMANA NECESSÁRIA` para esse ponto específico.
- Commits mais antigos da fila (`1597b71`, `b876fde`, `b88c0ae`, `d43468d`, `3b2084b`, `e499b1b`,
  `051cc7a`, `97d639c`, `a7c275f`) e toda a frente de `casos-clinicos/`+`trilhas/`+`galeria/`+
  `exames/` do segundo agente — ficam para a próxima rodada.

---
