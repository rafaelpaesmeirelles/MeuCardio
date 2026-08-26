---
title: "Fluxograma: Segunda linha hipoglicemiante no diabético tipo 2 cardiopata com doença renal crônica avançada"
slug: fluxograma-segunda-linha-hipoglicemiante-diabetes-drc-avancada
theme: "Diabetes e cardiologia"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir do texto integral, aberto no PMC, do capítulo 11 (Doença Renal Crônica) do ADA Standards of Care in Diabetes-2026 (PMID 41358881, PMCID PMC12690176), lido nesta sessão — as Recomendações 11.6a, 11.7a, 11.7b e o trecho sobre lixisenatida/exenatida foram citados literalmente a partir do texto fetched, não de memória. A diretriz-mãe citada por esse capítulo é o KDIGO 2022 Clinical Practice Guideline for Diabetes Management in Chronic Kidney Disease (PMID 36272764); o texto integral do KDIGO deu 403 em kdigo.org e em kidney-international.org nesta sessão (mesmo bloqueio de Cloudflare já documentado neste repositório para outras diretrizes), então os limiares numéricos de TFGe usados na árvore (30-44, 20-29, <20) vêm do capítulo ADA 2026, que opera e cita a mesma base de evidência do KDIGO (DAPA-CKD, EMPA-KIDNEY, FLOW), já documentada nesta pasta em 'inibidores-de-sglt2-na-doenca-renal-cronica-dapa-ckd-e-empa-kidney.md' e 'flow-semaglutida-drc-diabetes-tipo-2.md'. Antes de escrever, conferido o corpus da pasta: já existe fluxograma geral de escolha iSGLT2 vs. GLP-1 por condição predominante ('fluxograma-escolha-isglt2-glp1-diabetico-doenca-cardiovascular.md', com um único ramo binário de TFGe ≥20/<20), mas nenhum documento cobre especificamente o efeito da própria TFGe avançada sobre a continuidade da metformina nem estratifica a escolha de segunda linha em três faixas de TFGe (30-44, 20-29, <20/diálise) com a cadeia de contraindicação/intolerância iSGLT2→GLP-1RA→outro agente — este é o ângulo novo e o motivo de não duplicar o fluxograma já publicado."
source_refs: ["American Diabetes Association Professional Practice Committee. 11. Chronic Kidney Disease and Risk Management: Standards of Care in Diabetes-2026. Diabetes Care. 2026;49(Suppl 1):S246-S260. DOI: 10.2337/dc26-S011. PMID: 41358881. PMCID: PMC12690176 — texto integral lido nesta sessão, fonte das Recomendações 11.6a, 11.7a, 11.7b e do trecho sobre lixisenatida/exenatida citados na árvore.", "Kidney Disease: Improving Global Outcomes (KDIGO) Diabetes Work Group. KDIGO 2022 Clinical Practice Guideline for Diabetes Management in Chronic Kidney Disease. Kidney Int. 2022;102(5S):S1-S127. DOI: 10.1016/j.kint.2022.06.008. PMID: 36272764 — diretriz de origem dos limiares de TFGe operacionalizados pelo capítulo ADA 2026 citado acima; texto integral bloqueado (403) nesta sessão, não lido diretamente.", "Heerspink HJL, et al. Dapagliflozin in Patients with Chronic Kidney Disease (DAPA-CKD). N Engl J Med. 2020;383(15):1436-1446. PMID: 32970396 — já documentado em 'inibidores-de-sglt2-na-doenca-renal-cronica-dapa-ckd-e-empa-kidney.md' desta pasta, citado aqui só como base de evidência da Recomendação 11.7a.", "Perkovic V, et al. Effects of Semaglutide on Chronic Kidney Disease in Patients with Type 2 Diabetes (FLOW). N Engl J Med. 2024;391:109-121. PMID: 38785209 — já documentado em 'flow-semaglutida-drc-diabetes-tipo-2.md' desta pasta, citado aqui só como base de evidência da Recomendação 11.7b."]
---

# Fluxograma: Segunda linha hipoglicemiante no diabético tipo 2 cardiopata com doença renal crônica avançada

O fluxograma geral já publicado nesta pasta escolhe entre iSGLT2 e GLP-1RA a partir da condição
predominante (insuficiência cardíaca, DRC ou doença aterosclerótica), com um único corte de TFGe
(≥20 ou <20 mL/min/1,73m²) dentro do ramo de DRC. O recorte que falta é o que acontece **dentro**
da DRC avançada: como a própria queda progressiva da TFGe muda tanto o destino da metformina já em
uso quanto a viabilidade de iniciar iSGLT2, e o que fazer quando a primeira escolha de segunda linha
esbarra em contraindicação ou intolerância. Este fluxograma organiza a decisão em três faixas de
TFGe — 30 a 44, 20 a 29, e abaixo de 20 (incluindo diálise) — cada uma com sua própria cadeia de
decisão entre iSGLT2, GLP-1RA e outro agente.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Diabetes tipo 2, cardiopata com doença cardiovascular estabelecida<br/>ou risco cardiovascular alto, em uso de metformina,<br/>com doença renal crônica e TFGe reduzida"] --> D1{"TFGe atual, mL/min/1,73m²?"}
  D1 -->|"30 a 44 (DRC G3b)"| P1["Reavaliar risco-benefício da metformina e reduzir dose;<br/>TFGe ainda permite iniciar iSGLT2"]
  D1 -->|"20 a 29 (DRC G4)"| P2["Suspender metformina, contraindicada abaixo de TFGe 30;<br/>TFGe no limite inferior ainda permite iniciar iSGLT2"]
  D1 -->|"Menor que 20, incluindo diálise (DRC G4 avançada/G5)"| P3["Suspender metformina, contraindicada;<br/>TFGe abaixo do limiar mínimo para iniciar iSGLT2"]
  P1 --> D2a{"Contraindicação ou intolerância a iSGLT2?<br/>(cetoacidose euglicêmica prévia, infecção genital<br/>de repetição, cirurgia programada próxima)"}
  D2a -->|"Não"| C1(["Iniciar iSGLT2 com benefício cardiorrenal comprovado<br/>(dapagliflozina ou empagliflozina) — ADA 2026 Rec. 11.7a"])
  D2a -->|"Sim"| D3a{"Contraindicação ou intolerância a GLP-1RA?<br/>(gastroparesia grave, pancreatite aguda recente,<br/>neoplasia endócrina múltipla tipo 2)"}
  D3a -->|"Não"| C2(["Iniciar GLP-1RA com benefício cardiorrenal comprovado<br/>(semaglutida ou dulaglutida) — ADA 2026 Rec. 11.7b"])
  D3a -->|"Sim"| C3(["Outro agente: insulina basal ajustada ao risco de<br/>hipoglicemia, ou inibidor de DPP-4 compatível<br/>com a função renal, conforme meta individual"])
  P2 --> D2b{"Contraindicação ou intolerância a iSGLT2?"}
  D2b -->|"Não"| C4(["Iniciar iSGLT2 — TFGe igual ou maior que 20 é o<br/>limiar mínimo de início (ADA 2026 Rec. 11.7a),<br/>pode ser mantido até falência renal"])
  D2b -->|"Sim"| D3b{"Contraindicação ou intolerância a GLP-1RA?"}
  D3b -->|"Não"| C5(["Iniciar GLP-1RA com benefício cardiorrenal comprovado"])
  D3b -->|"Sim"| C6(["Outro agente: insulina basal ou inibidor de DPP-4<br/>com ajuste compatível à função renal reduzida"])
  P3 --> D4{"Contraindicação ou intolerância a GLP-1RA?"}
  D4 -->|"Não"| C7(["Iniciar GLP-1RA — classe sem limiar mínimo de TFGe<br/>para início (ressalva: lixisenatida e exenatida têm<br/>dados limitados e exigem cautela com TFGe menor que 30);<br/>preferir semaglutida ou dulaglutida"])
  D4 -->|"Sim"| C8(["Outro agente: insulina, sem restrição por função renal<br/>além do ajuste de dose pelo risco de hipoglicemia"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore não mostra

- **Finerenona não é hipoglicemiante e não entra na árvore.** A Recomendação 11.8 do ADA 2026
  indica antagonista mineralocorticoide não esteroide (finerenona) para reduzir progressão de DRC e
  eventos cardiovasculares quando há albuminúria e TFGe ≥25 mL/min/1,73m² — é aditiva ao iSGLT2 ou
  ao GLP-1RA escolhidos aqui, não uma alternativa a eles. A combinação já está documentada nesta
  pasta em `confidence-combinacao-de-finerenona-e-empagliflozina-na-doenca-renal-cronica-diabetica.md`.
- **A ordem de preferência entre iSGLT2 e GLP-1RA, quando os dois são elegíveis, depende do problema
  predominante — o mesmo critério do fluxograma geral já publicado.** O capítulo ADA 2026 posiciona
  iSGLT2 como primeira escolha para quem tem risco de progressão renal (albuminúria ou queda
  documentada de TFGe) e sugere GLP-1RA quando o risco cardiovascular é o problema predominante. Esta
  árvore assume que, dentro da DRC avançada, a proteção renal já é a prioridade clínica — por isso o
  ramo padrão é iSGLT2 primeiro sempre que a TFGe permitir, reservando GLP-1RA para quando iSGLT2 não
  pode ser usado.
- **A reavaliação da metformina não é binária.** Entre TFGe 30 e 44, a diretriz pede reavaliar
  risco-benefício e considerar redução de dose, não necessariamente suspender de imediato — a decisão
  final depende de tolerância, função renal estável ou em queda, e julgamento clínico. Abaixo de 30, a
  contraindicação é formal.
- **Dentro de "outro agente" (folhas C3, C6 e C8), a escolha entre insulina e inibidor de DPP-4 não é
  detalhada por fármaco específico.** O capítulo da diretriz usado como fonte principal não desenvolve
  o ajuste renal de cada gliptina; a única classe com ressalva renal explícita e citada literalmente
  na fonte é a de dois GLP-1RA específicos (lixisenatida e exenatida, com dados limitados e uso com
  cautela abaixo de TFGe 30) — as demais moléculas de GLP-1RA não têm essa restrição na fonte citada.
- **Efeitos adversos específicos de cada classe não são ramos da árvore** — risco de cetoacidose
  euglicêmica e infecção genital com iSGLT2, efeitos gastrointestinais com GLP-1RA — já documentados
  em itens próprios desta pasta, e entram na avaliação individual de contraindicação/intolerância
  representada nos losangos, não como estrutura própria do algoritmo.
- **A árvore não substitui o julgamento nefrológico em TFGe muito baixa ou diálise.** Nessa faixa, o
  manejo farmacológico costuma ser conduzido em conjunto com nefrologia, e a escolha final considera
  também expectativa de transplante, adesão e capacidade de automonitorização glicêmica do paciente.
