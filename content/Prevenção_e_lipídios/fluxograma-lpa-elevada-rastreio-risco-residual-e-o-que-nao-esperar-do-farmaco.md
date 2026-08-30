---
title: "Fluxograma: Lp(a) elevada — rastreio, risco residual e o que não esperar do fármaco"
slug: fluxograma-lpa-elevada-rastreio-risco-residual-e-o-que-nao-esperar-do-farmaco
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: grok
summary: "Árvore do consultório com o resultado de Lp(a) na mão: unidade certa, corte como fator agravante, cascata, intensificar LDL agora, e o ramo que recusa pelacarsena/olpasirana como se já tivessem reduzido MACE. Não substitui o consenso EAS 2022 de quem dosar nem o OCEAN(a)-DOSE."
review_status: revisado
review_note: "Produção científica assistida em 29/08/2026. Árvore estrita (raiz única, um pai por nó, conduta só em folha). Classes: ESC/EAS 2025 Tabela 4 IIa B (fator agravante >50 mg/dL ≈105 nmol/L) lida no PDF/EAS; SBC 2025 GRADE da tabela de Lp(a) lida no PMC. HORIZON sem artigo de desfecho em 29/08/2026 (PubMed + NCT04023552). AAS por Lp(a) isolada: nenhuma tabela lida — ramo de não prescrever, com LIMITE DA EVIDÊNCIA no protocolo irmão."
source_refs:
  - "Mach F, Koskinas KC, Roeters van Lennep JE, et al. 2025 Focused Update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2025;46(42):4359-4378. DOI: 10.1093/eurheartj/ehaf190. PMID: 40878289 — Tabela de Recomendação 4"
  - "Mach F, Baigent C, Catapano AL, et al. 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2020;41(1):111-188. DOI: 10.1093/eurheartj/ehz455. PMID: 31504418"
  - "Rached FH, Miname MH, Rocha VZ, et al. Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose – 2025. Arq Bras Cardiol. 2025;122(9):e20250640. DOI: 10.36660/abc.20250640. PMID: 41379178. PMCID: PMC12674852"
  - "Kronenberg F, Mora S, Stroes ESG, et al. Lipoprotein(a) in atherosclerotic cardiovascular disease and aortic stenosis: a European Atherosclerosis Society consensus statement. Eur Heart J. 2022;43(39):3925-3946. DOI: 10.1093/eurheartj/ehac361. PMID: 36036785"
  - "Blumenthal RS, Morris PB, Gaudino M, et al. 2026 ACC/AHA Guideline on the Management of Dyslipidemia. J Am Coll Cardiol. 2026;87(19):2624-2757. DOI: 10.1016/j.jacc.2025.11.016. PMID: 41824590"
  - "Cho L, Nicholls SJ, Nordestgaard BG, et al. Design and Rationale of Lp(a)HORIZON Trial. Am Heart J. 2025;287:1-9. DOI: 10.1016/j.ahj.2025.03.019. PMID: 40185318"
  - "O'Donoghue ML, Rosenson RS, Gencer B, et al. Small Interfering RNA to Reduce Lipoprotein(a) in Cardiovascular Disease. N Engl J Med. 2022;387(20):1855-1864. PMID: 36342163"
  - "Derivado de lipoproteina-a-conduta-pratica-enquanto-os-desfechos-nao-chegam.md. Liga, não clona, lipoproteina-a-rastreamento-populacional-ao-menos-uma-vez-na-vida-consenso-eas-2022.md e lipoproteina-a-e-olpasirana-o-ensaio-ocean-a-dose.md"
---

# Fluxograma: Lp(a) elevada — rastreio, risco residual e o que não esperar do fármaco

Árvore da **consulta em que o número de Lp(a) decide o que fazer nesta semana**,
não da pergunta "quem dosar na população" (consenso EAS 2022) nem da pergunta
"quanto a olpasirana baixa o biomarcador" (OCEAN(a)-DOSE). As folhas são condutas
de hoje. Nenhuma folha inicia pelacarsena, olpasirana ou AAS "porque a Lp(a) está
alta": Lp(a)HORIZON não tinha MACE publicado em 29/08/2026, e nenhuma tabela lida
nesta revisão editorial recomenda AAS só por esse número.

O texto que explica unidade, GRADE brasileiro e o status dos CVOTs está em
[`lipoproteina-a-conduta-pratica-enquanto-os-desfechos-nao-chegam`](lipoproteina-a-conduta-pratica-enquanto-os-desfechos-nao-chegam.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto em consultório:<br/>Lp(a) já medida, ou ainda nunca medida"] --> D1{"Já existe uma dosagem<br/>de Lp(a) na vida adulta?"}

  D1 -->|"Não"| C1(["Pedir uma vez, de preferência em nmol/L<br/>com ensaio independente da isoforma.<br/>SBC 2025: Forte / Moderada na população geral;<br/>Forte / Alta se DAC precoce, estenose aórtica,<br/>HF ou história familiar. Não é exame anual"])

  D1 -->|"Sim"| D2{"O laudo está em nmol/L,<br/>ou só em mg/dL?"}

  D2 -->|"Só mg/dL, e a decisão<br/>está perto de 50 mg/dL"| C2(["Não converter com fator fixo.<br/>SBC 2025: fórmulas não são recomendadas<br/>Forte / Alta. Recoletar em nmol/L<br/>no mesmo laboratório se o corte mudar conduta"])

  D2 -->|"nmol/L disponível,<br/>ou mg/dL longe da fronteira"| D3{"Qual é a faixa?"}

  D3 -->|"Abaixo de 75 nmol/L<br/>ou abaixo de 30 mg/dL"| C3(["Lp(a) provavelmente não é o motor.<br/>Tratar o risco restante como de costume;<br/>não repetir a dosagem sem doença renal,<br/>hepática, infecção aguda ou menopausa<br/>com valor prévio limítrofe"])

  D3 -->|"Zona cinzenta EAS 2022:<br/>75 a 125 nmol/L<br/>ou 30 a 50 mg/dL"| C4(["Entra no conjunto de risco,<br/>não reclassifica sozinha.<br/>Não iniciar RNA nem AAS por este número"])

  D3 -->|"Acima de 50 mg/dL<br/>ou cerca de 105 a 125 nmol/L<br/>conforme a diretriz em uso"| D4{"Há doença aterosclerótica<br/>estabelecida?"}

  D4 -->|"Sim"| P1["Fator agravante: ESC/EAS 2025<br/>Tabela 4, Classe IIa, Nível B.<br/>SBC: prediz recorrência"]
  P1 --> D5{"O LDL já está na meta<br/>da categoria deste paciente?"}

  D5 -->|"Não"| C5(["Intensificar HOJE o hipolipemiante<br/>com desfecho já publicado:<br/>estatina de alta intensidade, ezetimiba,<br/>iPCSK9 ou ácido bempedoico.<br/>Não esperar o HORIZON. iPCSK9 é para o LDL,<br/>não 'para Lp(a)'"])

  D5 -->|"Sim"| C6(["Manter a meta de LDL; apertar<br/>pressão, tabaco, diabetes, peso e exercício.<br/>Cascata familiar se ≥50 mg/dL<br/>ou ≥125 nmol/L — SBC 2025 Forte / Alta.<br/>Não iniciar pelacarsena/olpasirana/AAS"])

  D4 -->|"Não"| P2["Reclassificar o risco global:<br/>em moderado ou no limiar de tratar,<br/>Lp(a) alta empurra para cima"]
  P2 --> D6{"Família de 1º grau ainda<br/>não rastreada para Lp(a)?"}

  D6 -->|"Sim, e o caso índice está<br/>≥50 mg/dL ou ≥125 nmol/L"| C7(["Cascata familiar agora.<br/>SBC 2025 Forte / Alta.<br/>No índice: estilo de vida e meta de LDL<br/>da nova categoria, sem RNA e sem AAS<br/>'por Lp(a)'"])

  D6 -->|"Não, ou o valor não atinge<br/>o corte de cascata"| C8(["Tratar os fatores modificáveis<br/>com a intensidade da categoria reclassificada.<br/>Imagem de aterosclerose subclínica só se<br/>ainda houver dúvida de tratar.<br/>Não prescrever o fármaco de Lp(a)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore recusa de propósito

**Pelacarsena e olpasirana não têm folha de "iniciar".** O OCEAN(a)-DOSE (PMID 36342163)
baixa o biomarcador; o Lp(a)HORIZON (PMID 40185318, NCT04023552) é ensaio de desfecho
**ainda sem artigo de MACE na consulta PubMed de 29/08/2026**. OCEAN(a) Outcomes
(NCT05581303) segue em curso. Quem precisa do detalhe de dose vai ao documento
[`lipoproteina-a-e-olpasirana-o-ensaio-ocean-a-dose`](lipoproteina-a-e-olpasirana-o-ensaio-ocean-a-dose.md)
— não se copia aquele ensaio nesta árvore.

**AAS não tem folha de "começar porque a Lp(a) está alta".** Nenhuma tabela lida
nesta revisão editorial dá classe para isso. O protocolo irmão marca **LIMITE DA EVIDÊNCIA**.
AAS continua nas regras de prevenção primária ou secundária que já existem.

**50 mg/dL não é um único nmol/L.** ESC/EAS 2025 Tabela 4 usa ≈105 nmol/L; EAS 2022,
SBC 2025 e ACC/AHA 2026 usam 125 nmol/L para o mesmo 50 mg/dL. A folha C2 existe
para impedir a conta de guardanapo.

**Quem dosar na população** (adulto nunca testado, criança só com AVC ou pai/mãe
com DCVA prematura, ancestralidade como ressalva de corte) continua no consenso
EAS 2022. Esta árvore assume a consulta individual, não o programa de rastreio.

## Cortes que a árvore usa, e de onde vêm

| Faixa | Fonte lida | O que faz na prática |
|---|---|---|
| <30 mg/dL / <75 nmol/L | EAS 2022; SBC 2025 Tabela 3.1 (referência de estratificação, sem meta) | Folha C3 |
| 30–50 mg/dL / 75–125 nmol/L | EAS 2022 zona cinzenta | Folha C4 |
| >50 mg/dL (≈105 nmol/L) | ESC/EAS 2025 Tabela 4, **IIa B** | Entra em D4 |
| ≥50 mg/dL ou ≥125 nmol/L | SBC 2025 cascata, **Forte / Alta** | Folhas C6 e C7 |
| ≥125 nmol/L / 50 mg/dL (~1,4×) e ≥250 nmol/L / 100 mg/dL (~2×) | ACC/AHA 2026, texto; COR/LOE da medição **não lidos** nesta revisão editorial | Intensificador, sem classe americana atribuída aqui |
| >180 mg/dL (equivalência vitalícia com HF heterozigótica) | ESC/EAS 2019 | Extremo; não é o corte da Tabela 4 de 2025 |

Não há meta terapêutica de Lp(a) em nenhuma dessas tabelas.
