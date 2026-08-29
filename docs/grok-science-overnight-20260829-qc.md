---
title: "QC científico — grok/science-overnight-20260829 (10 documentos atribuídos)"
slug: grok-science-overnight-20260829-qc
---

# QC científico — branch `grok/science-overnight-20260829`

Data: 2026-08-29. Recorte: 10 markdowns científicos novos, `review_status: pendente_revisao`. Leitura apenas; nenhum arquivo de conteúdo foi editado; nada foi promovido a `revisado`.

Corpus cruzado: ~1950 slugs em `content/**/*.md` + slugs de `checklists/metadados.json`. PMIDs âncora conferidos contra PubMed nesta sessão.

## Veredito

Nenhum dos três erros mandatórios está presente. Não há PMID âncora falso. Não há colisão de slug. Não há link órfão para slug inexistente. Há resíduos de verificação humana (tabela ESC 2026 recém-publicada, ISHLT 2016 usada como tabela operacional apesar da sucessora 2024, classes ACS via CardioPractice) e sobreposição deliberada de PMID com cards já existentes. Manter `pendente_revisao`.

| Flag mandatório | Resultado |
|---|---|
| SUMMIT vendido como redução de mortalidade | **PASS** — 8 vs 5 mortes CV, HR 1,58 (IC95% 0,52–4,83); o composto HR 0,62 é explicitamente separado |
| Incretina ESC 2026 vendida como FMT ou classe de mortalidade | **PASS** — AMT, Classe IIa B1, para peso / exercício / QoL; corte FEVE ≥45% e IMC ≥30 |
| Cortes de VO₂ ISHLT invertidos | **PASS** — ≤12 mL/kg/min em BB, ≤14 sem BB (2016 Classe I B); 2024 citada como mantendo os mesmos cortes |

## Arquivos revisados

1. `content/Insuficiência_cardíaca/icfei-historica-e-a-reclassificacao-esc-2026.md`
2. `content/Insuficiência_cardíaca/summit-tirzepatida-icfep-com-obesidade.md`
3. `content/Insuficiência_cardíaca/agonistas-incretina-na-icfep-com-obesidade-step-e-summit.md`
4. `content/Insuficiência_cardíaca/indicacoes-de-transplante-cardiaco-adulto-ishlt-2016.md`
5. `content/Doença_coronariana/angina-vasoespastica-criterios-covadis-diagnostico-e-tratamento.md`
6. `content/Doença_coronariana/comunicacao-interventricular-pos-infarto-diagnostico-e-decisao.md`
7. `content/Doença_coronariana/infarto-tipo-2-versus-lesao-miocardica-nao-isquemica.md`
8. `content/Doença_coronariana/prevencao-secundaria-integrada-apos-sindrome-coronariana-aguda.md`
9. `content/Prevenção_e_lipídios/select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes.md`
10. `content/Geral/dispneia-aguda-de-origem-cardiovascular-abordagem-inicial.md`

---

## 1. PMIDs âncora (spot-check PubMed)

| PMID | Paper citado | Conferência |
|---|---|---|
| 37952131 | SELECT, Lincoff, *NEJM* 2023;389:2221-2232. DOI 10.1056/NEJMoa2307563 | **OK.** N 17.604 (8.803 / 8.801); MACE 6,5% vs 8,0%; HR 0,80 (0,72–0,90); p<0,001; seguimento 39,8±9,4 meses; descontinuação 16,6% vs 8,2%. Componentes isolados **não** estão no abstract — o card não os inventa. Morte CV no texto integral (223 vs 262, HR 0,85, p=0,07) corretamente omitida. |
| 39555826 | SUMMIT, Packer, *NEJM* 2025;392:427-437. DOI 10.1056/NEJMoa2410027 | **OK.** 731 (364 vs 367); composto 9,9% vs 15,3%, HR 0,62, p=0,026; piora da IC 8,0% vs 14,2%, HR 0,54; morte CV **8 vs 5**, HR **1,58** (0,52–4,83); KCCQ +19,5 vs +12,7, Δ 6,9. Nota correta de que “±SD” do abstract tem magnitude de erro-padrão. |
| 26776864 | ISHLT listing 2016, Mehra, *JHLT* 2016;35:1-23 | **OK.** PDF oficial / PubMed batem. |
| 37622654 | ESC 2023 ACS, Byrne, *EHJ* 2023;44:3720-3826. DOI 10.1093/eurheartj/ehad191 | **OK.** |
| 26245334 | COVADIS VSA, Beltrame, *EHJ* 2017;38:2565-2568. DOI 10.1093/eurheartj/ehv351 | **OK.** Consenso (não diretriz). Critérios (nitrato-responsiva; ST ±0,1 mV / U negativa; constrição >90%; definitiva vs suspeita) conferidos contra a página COVADIS. |
| 37622681 | STEP-HFpEF, Kosiborod, *NEJM* 2023;389:1069-1084 | **OK.** n=529; KCCQ +16,6 vs +8,7 (Δ 7,8); peso −13,3% vs −2,6% (Δ −10,7 pp); 6 min +21,5 vs +1,2 m; win ratio 1,72; EAG 13,3% vs 26,7%. |

### Outros PMIDs / DOIs amostrados (não âncora, mas usados como classe ou número)

Todos os abaixo **existem** no PubMed ou no DOI ESC (advance 28/08/2026): 34447992, 37622666, 34449189, 36471037, 36027570, 39225278, 31475794, 39115488, 37549773, 30335870, 39210710, 29031990, 22322081, 39820976, 34126755, 38888906, 40013746 (JACC) / 40014670 (Circulation — publicação dupla ACC/AHA 2025, ambos válidos), 10460813, 10985713, 38587239, 34320090, 40905366, 41294178, 41379178, 40878289, 30165617, 38587241, 38587237, 36018037, 29866583, 18614781, 12124404, 15820160, 31504429, 35363499, 37471501.

DOI 10.1093/eurheartj/ehag100 (ESC 2026 HF), ehag101 (5ª Definição Universal de IAM) e ehag164 (Lorusso 2026, ruptura de parede livre) existem como advance/publicação 2026. Autores Køber / Adamo / Ruwald / Tomasoni da ESC 2026 conferidos na página da ESC.

Nenhum PMID âncora falso. Nenhum DOI inventado nesta amostra.

### Citações incompletas (não falsas)

- ICFEi `source_refs` da SBC 2018 IC omite PMID 30379264 (o documento de dispneia o traz).
- Quinta Definição Universal e ESC 2026 HF ainda sem PMID (advance de 28/08/2026) — declarado.
- Lorusso 2026: DOI citado, PMID explicitamente não conferido.
- V Diretriz SBC IAMCST 2015: classes não reproduzidas porque PMID próprio não foi localizado — honesto.
- `prevencao-secundaria`: PDF ESC 2023 ACS retornou 403 nesta sessão; parte das classes ACS veio de CardioPractice (fonte secundária, declarada).

---

## 2. Classe / nível inventado

Nenhuma classe numerada foi encontrada sem lastro, com três resíduos.

**O que está alinhado**

- Incretina ESC 2026 Tabela 18: texto literal da diretriz (“should be considered… LVEF ≥45%… BMI ≥30… regardless of diabetes… weight, exercise capacity and QoL”) + **IIa B1, AMT não FMT**. Press release ESC 28/08/2026 confirma IIa em LVEF preservada + obesidade; o corte ≥45% (não ≥50%) está no texto da OUP.
- iSGLT2 I A independente da FEVE e MRA I A independente da FEVE: coerente com ESC 2023 (SGLT2) e com o press release 2026 (MRA I independente da FEVE).
- Dispositivos ESC 2026 **não** acompanham a expansão da ICFEr: CDI/TRC continuam ≤35%. O texto impede a extrapolação.
- Ferro IV 2026 (I B1 sintomas / IIa B1 hospitalização) marcado **VHN** — Tabela 19 não relida.
- COVADIS: consenso, sem Classe I/II/III inventada. CFT ESC 2024 CCS I B conferida contra o documento ANOCA já revisado; classe de CCB / nitrato / betabloqueador **não** inventada.
- CIV: I C reparo emergencial, IIa C IABP na complicação mecânica, III B IABP de rotina no choque de bomba — tabela ESC 2023. ACC/AHA 2025 citada só em linguagem (“is indicated”, “is reasonable”), COR/LOE numéricos não transcritos.
- Tipo 2: a ESC 2023 **não** tem tabela de classe para tipo 2; o protocolo recusa promover narrativa a Classe I/III. MINOCA I C / I B / I B da ESC 2023 está no recorte certo.
- SELECT: SBC/ABESO/SBD/SBEM 2025 R11 = **I B** para semaglutida 2,4 mg em IMC ≥27 sem DM com DCV estabelecida (conferido na diretriz SBD). ESC 2024 CCS = **IIa B** em SCC com IMC >27 sem DM (conferido). Não inflado para I A.
- Dispneia: O2 I C (SpO2 <90% ou PaO2 <60) e VNI IIa B da ESC 2021; NP I A da AHA/ACC/HFSA 2022. ESC 2026 usada só para nomenclatura (“IC descompensada”), tabelas da fase imediata **não** relidas — declarado.

**Resíduos (não inventados, mas ainda não fechados)**

1. **ICFEi — nota de rodapé “e” da Tabela 5 ESC 2026 não lida.** Classe I A de BB e IECA/ARNI na ICFEr recém-expandida (41–49%) pode ser restringida por FEVE, NYHA ou estabilidade. O texto avisa; a promoção humana precisa ler a nota antes de tratar I A como irrestrita nessa faixa. PARADIGM-HF foi ≤40%; PARAGON-HF ≥45% foi neutro (RR 0,87; 0,75–1,01; p=0,06) — isso está escrito.
2. **Molécula de MRA em 41–49%:** sMRA “porque agora é ICFEr” vs finerenona (FINEARTS-HF, FEVE ≥40%, 36% com 40–50%, RR 0,84). Marcado VHN; não convertido silenciosamente.
3. **Prevenção secundária — classes ACS via CardioPractice** (DAPT 12 meses; AAS I B após 12 meses; BB I A após SCA independente de sintoma de IC; influenza I A; teach-back IIa B). Fonte secundária, PDF 403. BB “independente de sintoma de IC” **não** é o mesmo que “independente da FEVE”; o texto em seguida recorta REDUCE-AMI (FEVE ≥50%, n=5.020, HR 0,96, p=0,64). Residual, não invenção.
4. **Nível B1/B2** da ESC 2026 (sistema novo de LoE) é usado de forma consistente nos quatro textos de IC; residual de conferência contra o PDF integral, não de nomenclatura inventada.

---

## 3. Doses

Nenhuma dose errada encontrada.

| Fármaco | O que o texto diz | Checagem |
|---|---|---|
| Tirzepatida SUMMIT | até 15 mg SC 1×/semana | OK |
| Semaglutida STEP / SELECT | 2,4 mg SC 1×/semana | OK. O card SELECT recusa 1,0 mg (FLOW/Ozempic) e a oral. |
| Estatina alta intensidade | atorvastatina 40–80 mg; rosuvastatina 20–40 mg | OK |
| AAS manutenção | 75–100 mg | OK ESC |
| Empagliflozina EMPACT-MI | 10 mg até 14 dias do IAM | OK |
| Polipílula SECURE | AAS 100 + ramipril 2,5/5/10 + atorvastatina 20/40 | OK; o texto avisa que **não** contém BB nem iSGLT2 |

Acetylcolina, diltiazem/verapamil, nitroprussiato, catecolaminas: doses **não** protocoladas (VHN / protocolo local). Correto.

---

## 4. Contraindicações super-absolutizadas

Não há lista inventada de “absoluto”.

- ISHLT 2016: o texto recusa inventar corte único de RVP em Wood como absoluta no adulto; Classe III (substância ativa, não adesão, HCV/HBV com cirrose/HCC, HIV com linfoma SNC / Kaposi visceral) é transcrita como “não transplantar”, que é a linguagem da Classe III. Relativas (IMC ≥35, TFGe <30, HbA1c ≥7,5%, idade >70, tabaco 6 meses) permanecem IIa/IIb.
- SBC 2018 RVP >5 Wood como absoluta é **atribuída à SBC**, contrastada com ISHLT/ESC 2026 (irreversibilidade farmacológica, sem número isolado). Não é silenciada nem generalizada ao ambulatorial.
- Teste de acetilcolina: lista japonesa de contraindicações absolutas **não** é copiada como ESC 2024.
- Tipo 2: DAPT/ICP **não** viram Classe III; o texto diz ausência de recomendação classificada.
- CIV: fibrinólise com suspeita de ruptura — “não lisar” é a ESC 2023 (IIa C só se complicação mecânica **excluída**).
- ESC 2026 Tabela 17: demência / incapacidade de aderir e comorbidade grave irreversível descritas como absolutas da ESC. Residual: conferir se a tabela usa exatamente “absoluta”.

---

## 5. Recomendação desatualizada tratada como vigente

| Item | Gravidade | Nota |
|---|---|---|
| **ISHLT 2016 como tabela operacional de listagem** apesar de Peled 2024 (PMID 39115488) **substituir formalmente** 2006 e 2016 | **Média** | O documento declara a sucessão, afirma que a Tabela 4 de 2024 mantém VO₂ 12/14 e RER >1,05, e marca confronto item a item 2016 vs 2024 como VHN. Mesmo assim o **título, o slug e as Classe III/IIa transcritas** são 2016 (HIV CD4>200, HCV com cirrose, HbA1c ≥7,5%, idade ≤70). Risco de o plantonista ler 2016 como vigente. Não é silêncio: é uso operacional de documento sucessor declarado. |
| ESC 2021 para O2 / VNI / peptídeo na dispneia aguda, com ESC 2026 só na nomenclatura | Baixa | Declarado; tabelas 2026 da fase imediata não relidas. |
| SBC 2018/2021 IC e PCDT 2024 (FEVE <40% / ≤35%) como vigente no Brasil | Nenhuma | Correto: não há SBC IC 2026 localizada; PCDT Portaria SAES/SECTICS nº 10, 13/09/2024, existe; dapagliflozina FEVE <40% conferida. Corte de sacubitril-valsartana ≤35% é residual de conferência no PDF do PCDT. |
| Weintraub AHA 2010 | Nenhuma | Usada só como declaração de objetivos no PS, não como diretriz vigente. |
| Quarta Definição 2018 ao lado da Quinta 2026 | Nenhuma | Vocabulários paralelos, explícitos. SCAD / espasmo / embolia como IAM **primário** 2026 (não mais tipo 2) está alinhado à síntese CorVIA já `revisado` (`quinta-definicao-universal-infarto-miocardio-2026-sintese-corvia`). |

---

## 6. Slugs duplicados vs corpus existente

**Nenhuma colisão de slug.** Sobreposições de PMID / tema (não são o mesmo arquivo):

| Novo | Já existia | Relação |
|---|---|---|
| `summit-tirzepatida-icfep-com-obesidade` | `tirzepatida-e-icfep-com-obesidade-o-ensaio-summit` (Diabetes e cardiologia, mesmo PMID 39555826) | Near-duplicate deliberado. O novo card é o ensaio de **evento** na pasta IC; o antigo é a molécula no mapa das incretinas. Ambos se apontam. Risco de o leitor achar dois SUMMITs com números diferentes se um for atualizado e o outro não. |
| `select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes` | `cirurgia-metabolica-e-semaglutida-em-obesidade-sem-diabetes-select` (Diabetes; mistura cirurgia + SELECT) | Complementar. O novo é o card dedicado do ensaio; o misto é explicitamente não substituto. |
| `agonistas-incretina-na-icfep-com-obesidade-step-e-summit` | `semaglutida-na-icfep-com-obesidade-o-ensaio-step-hfpef` + SUMMIT (dois temas) | Protocolo de decisão, não clone. |
| `icfei-historica-e-a-reclassificacao-esc-2026` | `esc-2026-insuficiencia-cardiaca-mudancas-chave-e-recomendacoes` + `fluxograma-feve-esc-2021-versus-esc-2026` | Recorte operacional do rótulo 41–49%; o panorâmico 2026 não é reescrito. |
| `infarto-tipo-2-versus-lesao-miocardica-nao-isquemica` | `fluxograma-elevacao-de-troponina-sem-sca-lesao-miocardica-e-infarto-tipo-2` | Camada de conduta sobre árvore já publicada. |
| `comunicacao-interventricular-pos-infarto-diagnostico-e-decisao` | `complicacoes-mecanicas-pos-infarto-na-uco-ruptura-septo-papilar-parede-livre` (UCO) | Beira-leito vs catálogo de UCO. CIV congênita (`comunicacao-interventricular-no-adulto-...`) corretamente separada. |
| `dispneia-aguda-de-origem-cardiovascular-abordagem-inicial` | `fluxograma-dispneia-aguda-cardiogenica-versus-nao-cardiogenica` (mesmo lote) | Irmãos protocolo/fluxograma. |
| `indicacoes-de-transplante-cardiaco-adulto-ishlt-2016` | `teste-cardiopulmonar-...-vo2-pico...` + `transplante-cardiaco-sobrevida-do-enxerto-...` + `fluxograma-encaminhamento-ic-avancada-lvad-transplante` | Não duplica fisiologia do VO₂ nem sobrevida. |
| `prevencao-secundaria-integrada-apos-sindrome-coronariana-aguda` | `fluxograma-alta-apos-sca-os-cinco-pilares-modificaveis` (mesmo lote) + cards REDUCE-AMI, EMPACT-MI, SECURE, DAPT | Playbook que aponta; não reanalisa. |
| `angina-vasoespastica-criterios-covadis-...` | `anoca-inoca-...` + fluxograma VSA do mesmo lote | Endótipo epicárdico; não clona ANOCA, cocaína nem 5-FU. |

---

## 7. Links órfãos

**Nenhum slug apontado que não exista.** Links markdown e backticks dos 10 arquivos resolvem para `content/**/*.md`, com duas exceções que são **checklists** (não conteúdo) e existem em `checklists/metadados.json`:

- `escalonamento-do-hipolipemiante-em-prevencao-secundaria`
- `encaminhamento-para-reabilitacao-cardiaca-em-prevencao-secundaria`

Ambos são chamados de “checklist” no texto. Não órfãos.

Prosa sem slug (não conta como órfão de link): “o documento pediátrico desta biblioteca” (existe `transplante-cardiaco-pediatrico-indicacoes-contraindicacoes-e-desfechos-do-registro-ishlt`); “checklist de início de GLP-1 no diabetes”.

---

## 8. Números-chave conferidos (além dos âncora)

| Número | Fonte no texto | Checagem |
|---|---|---|
| EMPEROR-Preserved 5.988; 13,8% vs 17,1%; HR 0,79 | ICFEi | OK |
| Subgrupo 41–49% HR 0,71 (0,57–0,88); p interação 0,27; 995 vs 988 | ICFEi, PMID 36471037 | OK (4.005 com FEVE ≥50% ⇒ 1.983 na faixa; 995+988=1.983) |
| DELIVER 6.263; 16,4% vs 19,5%; HR 0,82 | ICFEi | OK. HR pontual ≤49% **não** citado (VHN). |
| FINEARTS-HF 6.001; FEVE ≥40%; 36% com 40–50%; RR 0,84; morte CV HR 0,93 ns | ICFEi | OK (ACC: EF 40–50% = 36%) |
| PARAGON-HF RR 0,87; 0,75–1,01; p=0,06 | ICFEi | OK |
| SHOCK 302; 30 d 46,7% vs 56,0% p=0,11; 6 m 50,3% vs 63,1% p=0,027 | CIV | OK |
| Registro SHOCK CIV 55; mortalidade 87% vs 61%; cirurgia 25/31; clínico 1/24 sobreviveu; IABP 75%; PAS 81→102 | CIV | Coerente com Menon JACC 2000 |
| DanGer-Shock 45,8% vs 58,5%; HR 0,74; exclusão explícita de ruptura | CIV | OK. Não extrapolado para CIV. |
| ACOVA 304 → 144 (47%) <20% → 124 ACh → 62% espasmo (35 epicárdico ≥75%, 42 micro) | VSA | OK. Distinção ≥75% pré-COVADIS vs >90% 2017 está correta. |
| Breathing Not Properly acurácia 83,4% no corte BNP 100 | Dispneia | OK |
| SHoC-ED n=273, sem ganho de sobrevida; subestudo VE spec 94% / sens 62,5% | Dispneia | OK (Keefer) |
| REDUCE-AMI 5.020; HR 0,96 (0,79–1,16); p=0,64 | Prevenção 2ª | OK |
| EMPACT-MI 6.522; HR 0,90 (0,76–1,06); p=0,21 | Prevenção 2ª | OK. Primário = hospitalização por IC **ou morte por qualquer causa**. O texto diz “morte” sem “por qualquer causa” — imprecisão menor, não troca por morte CV. |
| SECURE 2.499; 9,5% vs 12,7%; HR 0,76 p=0,02 | Prevenção 2ª | OK |
| SBC 2025 dislipidemias LDL-c <50 / não-HDL <80 no muito alto risco (Forte, Alta); <40 no extremo | Prevenção 2ª | OK (PMC 12674852) |
| PRIDE exclusão NT-proBNP <300 (VPN 99%); inclusão 450/900 | Dispneia | OK no corte de exclusão. A menção 450/900/**1.800** “do PRIDE e do subestudo geriátrico” mistura PRIDE com ICON — imprecisão menor, marcada como VHN no próprio texto. |

---

## 9. Por arquivo — o que passa e o que sobra

### `icfei-historica-e-a-reclassificacao-esc-2026`

Passa: separa relógio diagnóstico 2026 (ICFEr <50%) do relógio de ensaio; não abre CDI/TRC; ivabradina/digoxina/hidralazina ficam ≤40%; vericiguat só <45%; incretina só ≥45% + obesidade; PCDT/SBC não são “atualizados” pela ESC; trajetória HFimpEF vs estável vs queda. Números EMPEROR/DELIVER/FINEARTS/PARAGON conferidos.

Sobra: nota de rodapé “e” da Tabela 5; molécula de MRA; HR isolado DELIVER ≤49% e FINEARTS 40–50%; ferro Tabela 19; Classe I A de BB/IECA/ARNI na faixa 41–49% é **reclassificação, não RCT novo** (já dito; ainda precisa da nota e).

### `summit-tirzepatida-icfep-com-obesidade` e `agonistas-incretina-na-icfep-com-obesidade-step-e-summit`

Passa o teste de mortalidade e o de FMT. STEP e SUMMIT não são misturados. Peso/6 min do SUMMIT **não** são inventados a partir do abstract. FEVE 45–49% é da diretriz, não do SUMMIT (≥50%). iSGLT2 não é retirado. Near-duplicate do card de Diabetes (mesmo PMID).

### `indicacoes-de-transplante-cardiaco-adulto-ishlt-2016`

VO₂ 12/14 corretos; “não listar só com VO₂ / só com escore” Classe III C; SHFM <80% ≠ mortalidade observada >40% da ESC; RVP absoluta não inventada. **Resíduo principal do lote:** 2016 operacional com 2024 sucessora formal. HIV/HCV/HbA1c/idade podem ter mudado em 2024 — o próprio texto pede confronto de 98 páginas.

### `angina-vasoespastica-criterios-covadis-diagnostico-e-tratamento`

Critérios COVADIS e o corte 90% vs ACOVA 75% corretos. Não atribui Classe I A a CCB. Não trata cocaína/5-FU como VSA primária. Fluxograma irmão do mesmo lote existe.

### `comunicacao-interventricular-pos-infarto-diagnostico-e-decisao`

DanGer-Shock **não** é extrapolado (critério de exclusão explícito). IABP IIa C na mecânica vs III B no choque de bomba. Timing “esperar cicatrizar” não vira regra. Lorusso 2026 citado só como existência.

### `infarto-tipo-2-versus-lesao-miocardica-nao-isquemica`

Alinhado à 5ª Definição 2026 já revisada no acervo. DAPT/ICP de rotina recusados. Delphi 2025 (PMID 40905366) tratado como opinião. Sem incidência inventada.

### `prevencao-secundaria-integrada-apos-sindrome-coronariana-aguda`

Cinco pilares; REDUCE-AMI e EMPACT-MI como freio; SELECT não vira Classe I inventada; metas LDL ESC 55 vs SBC 50 **não** misturadas; SECURE como implementação. Classes ACS parcialmente via CardioPractice (PDF 403). Checklists apontados existem.

### `select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes`

Números do abstract corretos; prevenção primária recusada; 2,4 mg ≠ 1,0 mg; componentes do MACE não declarados significativos. I B brasileiro e IIa B ESC 2024 conferidos.

### `dispneia-aguda-de-origem-cardiovascular-abordagem-inicial`

O2 só se hipoxemia; ECG 10 min como equivalente; cortes agudos 300/100 vs ambulatoriais 125/35; SHoC-ED honesto (sem ganho de sobrevida; não extrapola para dispneia sem hipotensão). ESC 2026 não relida nas tabelas da 1ª hora.

---

## 10. Itens que exigem verificação humana antes de promover

Prioridade alta

1. Nota de rodapé “e” da Recommendation Table 5 ESC 2026 (BB e IECA/ARNI na ICFEr expandida).
2. Confronto ISHLT 2016 vs 2024 linha a linha (além de VO₂ 12/14 e ausência de INTERMACS). Decidir se o título/slug devem permanecer “2016” ou passar a “ISHLT 2024 com memória de 2016”.
3. Reler Tabela 18 ESC 2026 no PDF (IIa B1, AMT, peso/exercício/QoL, FEVE ≥45%) — o texto avançado da OUP bate, mas é advance de 28/08/2026.
4. Classes ACS da prevenção secundária (influenza I A, teach-back IIa B, BB I A independente de sintoma, DAPT 12 meses I) contra o PDF ESC 2023, não só CardioPractice.

Prioridade média

5. Molécula de MRA em 41–49% (sMRA vs finerenona).
6. Ferro IV Tabela 19 ESC 2026.
7. Classe/nível de CCB e nitrato no endótipo VSA da ESC 2024 CCS.
8. Manter os dois cards SUMMIT sincronizados se um for atualizado com o texto integral (peso, 6 min, fração com diabetes).
9. PCDT 2024: confirmar no PDF o corte de sacubitril-valsartana ≤35%.
10. ESC 2026 Tabela 17: linguagem exata de “contraindicação absoluta”.

Prioridade baixa

11. PRIDE vs ICON no corte 1.800 de NT-proBNP.
12. EMPACT-MI: explicitar “morte por qualquer causa”.
13. Completar PMID 30379264 na SBC 2018 do ICFEi.
14. `fonte_producao: grok` ausente em `agonistas-incretina-...` e `select-...` (processo, não ciência).

---

## 11. O que este QC não faz

Não altera `review_status`. Não edita conteúdo. Não cobre os outros arquivos do mesmo lote (CMD, HAS secundária, EAP inicial, SGLT2-DRC, exercício primário, fluxogramas irmãos) salvo quando um dos 10 aponta para eles. Não substitui leitura do PDF integral da ESC 2026 HF (advance 28/08/2026).
