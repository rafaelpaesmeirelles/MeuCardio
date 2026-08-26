---
title: "Fluxograma: Manejo Fenótipo-dirigido da ICFEp (ACC 2026 Expert Consensus Decision Pathway)"
slug: fluxograma-manejo-icfep-fenotipo-dirigido-acc-2026
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído inteiramente a partir de referências já verificadas e publicadas nesta mesma pasta em sessões anteriores, sem PMID/DOI novo. A lógica fenótipo-dirigida (congestão primeiro, iSGLT2 de base para todos independente de diabetes, depois fenótipo de obesidade/incretina, FA, ou antagonista não esteroidal do receptor mineralocorticoide) reproduz diretamente o conteúdo já publicado em 'acc-2026-expert-consensus-icfep-diagnostico-fenotipos-e-tratamento.md' (Kittleson MM et al., J Am Coll Cardiol, DOI 10.1016/j.jacc.2026.06.018, PMID 42494134, texto integral conferido em 13/08/2026), incluindo a ressalva explícita do próprio consenso de que espironolactona (SPIRIT-HF) não replicou o resultado de finerenona (FINEARTS-HF) e não deve ser tratada como equivalente. EMPEROR-Preserved PMID 34449189 e DELIVER PMID 36027570 já verificados em 'inibidores-de-sglt2-na-icfep-empagliflozina-emperor-preserved-e-dapagliflozina-deliver.md'. FINEARTS-HF PMID 39225278 já verificado em 'finerenona-na-icfep-e-icfelr-o-ensaio-finearts-hf.md'. STEP-HFpEF PMID 37622681 já verificado em 'semaglutida-na-icfep-com-obesidade-o-ensaio-step-hfpef.md'. HFA-PEFF PMID 31504452 já verificado em 'hfa-peff-algoritmo-diagnostico-para-icfep-esc-2019.md'. Este documento é sobre TRATAMENTO fenótipo-dirigido, não repete o algoritmo diagnóstico passo a passo do HFA-PEFF, já coberto em profundidade no documento dedicado citado."
source_refs: ["Kittleson MM, Panjrath GS, Bates K, et al. Management of Heart Failure With Preserved Ejection Fraction: 2026 ACC Expert Consensus Decision Pathway. J Am Coll Cardiol. Published online July 23, 2026. DOI: 10.1016/j.jacc.2026.06.018. PMID: 42494134.", "Anker SD, Butler J, Filippatos G, et al; EMPEROR-Preserved Trial Investigators. Empagliflozin in Heart Failure with a Preserved Ejection Fraction. N Engl J Med. 2021;385(16):1451-1461. DOI: 10.1056/NEJMoa2107038. PMID: 34449189", "Solomon SD, McMurray JJV, Claggett B, et al; DELIVER Trial Committees and Investigators. Dapagliflozin in Heart Failure with Mildly Reduced or Preserved Ejection Fraction. N Engl J Med. 2022;387(12):1089-1098. DOI: 10.1056/NEJMoa2206286. PMID: 36027570", "Solomon SD, McMurray JJV, Vaduganathan M, et al; FINEARTS-HF Committees and Investigators. Finerenone in Heart Failure with Mildly Reduced or Preserved Ejection Fraction. N Engl J Med. 2024;391(16):1475-1485. DOI: 10.1056/NEJMoa2407107. PMID: 39225278", "Kosiborod MN, Abildstrøm SZ, Borlaug BA, et al; STEP-HFpEF Trial Committees and Investigators. Semaglutide in Patients with Heart Failure with Preserved Ejection Fraction and Obesity. N Engl J Med. 2023;389(12):1069-1084. DOI: 10.1056/NEJMoa2306963. PMID: 37622681", "Pieske B, Tschöpe C, de Boer RA, et al. How to diagnose heart failure with preserved ejection fraction: the HFA-PEFF diagnostic algorithm. Eur Heart J. 2019;40(40):3297-3317. DOI: 10.1093/eurheartj/ehz641. PMID: 31504452"]
---

# Fluxograma: Manejo Fenótipo-dirigido da ICFEp (ACC 2026 Expert Consensus Decision Pathway)

O ACC 2026 abandona formalmente a visão da ICFEp como "FEVE normal +
diurético" e organiza o tratamento em torno do fenótipo dominante — obesidade,
fibrilação atrial, ou nenhum fenótipo isolado além da síndrome cardiometabólica
de base. O inibidor de SGLT2 é pilar farmacológico para **todos**,
independente de diabetes; o que muda por fenótipo é o que se soma a ele.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Diagnóstico confirmado de ICFEp<br/>(FEVE ≥ 50%, sintomas/sinais de IC,<br/>evidência objetiva por HFA-PEFF,<br/>H2FPEF ou HFpEF-ABA)"]
  D1{"Paciente está congesto agora<br/>(sinais/sintomas de sobrecarga de<br/>volume)?"}
  C1(["Tratar a congestão com diurético de<br/>alça até euvolemia — diurético trata o<br/>sintoma, não é terapia modificadora de<br/>prognóstico por si só (ACC 2026 ECDP);<br/>reavaliar o fenótipo predominante após<br/>a descongestão"])
  P1["Iniciar inibidor de SGLT2 como pilar<br/>farmacológico de base, independente de<br/>diabetes (ACC 2026 ECDP,<br/>EMPEROR-Preserved, DELIVER)"]
  D2{"Fenótipo predominante identificado<br/>além da síndrome cardiometabólica de<br/>base?"}
  D3{"Diabetes tipo 2 ou IMC compatível com<br/>indicação de terapia incretínica, sem<br/>contraindicação?"}
  C2(["Associar terapia incretínica (ex.<br/>semaglutida em obesidade — STEP-HFpEF)<br/>ao iSGLT2, junto a intervenção<br/>estruturada de perda ponderal e<br/>exercício"])
  C3(["Priorizar perda ponderal por dieta e<br/>exercício associada ao iSGLT2;<br/>reavaliar a terapia incretínica se a<br/>elegibilidade mudar"])
  C4(["Tratar a fibrilação atrial como<br/>componente do fenótipo — anticoagulação<br/>conforme risco tromboembólico, controle<br/>de frequência e avaliação de controle de<br/>ritmo quando apropriado, junto ao iSGLT2<br/>de base"])
  D4{"Potássio e TFGe permitem associar<br/>antagonista não esteroidal do receptor<br/>mineralocorticoide (finerenona)?"}
  C5(["Associar finerenona ao iSGLT2<br/>(FINEARTS-HF) — não extrapolar<br/>automaticamente este benefício para<br/>espironolactona, que não replicou o<br/>resultado (SPIRIT-HF, citado no ACC 2026<br/>ECDP)"])
  C6(["Manter iSGLT2 como pilar de base, com<br/>controle rigoroso de pressão arterial e<br/>das demais comorbidades (DAC, DRC,<br/>apneia do sono); reavaliar elegibilidade<br/>a antagonista mineralocorticoide na<br/>evolução"])

  R0 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| P1
  P1 --> D2
  D2 -->|"Obesidade/fenótipo metabólico<br/>predominante"| D3
  D2 -->|"Fibrilação atrial predominante"| C4
  D2 -->|"Nenhum fenótipo dominante isolado"| D4
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  D4 -->|"Sim"| C5
  D4 -->|"Não"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**O algoritmo diagnóstico completo (HFA-PEFF, H2FPEF, HFpEF-ABA)** — a
probabilidade pré-teste, os domínios ecocardiográficos e o teste funcional para
casos indeterminados — não é repetido aqui; a árvore assume diagnóstico já
confirmado. Ver `hfa-peff-algoritmo-diagnostico-para-icfep-esc-2019.md`.

**Fenótipos concomitantes** (ex. obesidade **e** fibrilação atrial no mesmo
paciente) não são resolvidos por um único ramo — a árvore trata cada fenótipo
isoladamente; na prática, condutas de mais de um ramo costumam ser combinadas,
sempre com o iSGLT2 de base comum aos dois.

**ARNI e BRA na ICFEp** são posicionados pelo próprio ACC 2026 ECDP como
terapia individualizada, dependente de pressão arterial, função renal,
potássio e congestão — não como terapia universal com benefício homogêneo, e
por isso não aparecem como ramo próprio desta árvore, que segue a hierarquia
de prioridade explícita do consenso (iSGLT2 primeiro, depois fenótipo).

**Investigação de imitadores cardíacos e não cardíacos de ICFEp** (amiloidose
cardíaca, doença pericárdica, obesidade sem ICFEp verdadeira) é etapa
diagnóstica prévia a esta árvore, não coberta aqui — ver o documento de
diferenciação de amiloidose nesta pasta quando a suspeita existir.