---
title: "Fluxograma: CHA₂DS₂-VA e a Decisão de Anticoagular na Fibrilação Atrial"
slug: fluxograma-cha2ds2-va-decisao-de-anticoagulacao
theme: "Calculadoras"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723"
  - "Lip GYH, Nieuwlaat R, Pisters R, Lane DA, Crijns HJGM. Refining clinical risk stratification for predicting stroke and thromboembolism in atrial fibrillation using a novel risk factor-based approach: the Euro Heart Survey on Atrial Fibrillation. Chest. 2010;137(2):263-272. DOI: 10.1378/chest.09-1584. PMID: 19762550"
  - "Pisters R, Lane DA, Nieuwlaat R, de Vos CB, Crijns HJGM, Lip GYH. A novel user-friendly score (HAS-BLED) to assess 1-year risk of major bleeding in patients with atrial fibrillation: the Euro Heart Survey. Chest. 2010;138(5):1093-1100. DOI: 10.1378/chest.10-0134. PMID: 20299623"
---

# Fluxograma: CHA₂DS₂-VA e a Decisão de Anticoagular na Fibrilação Atrial

Este fluxograma deriva dos documentos já publicados `cha2ds2-va.md` e `has-bled.md` (tema Calculadoras). O CHA₂DS₂-VA (diretriz ESC 2024, que substitui o CHA₂DS₂-VASc removendo o sexo feminino como fator isolado) decide a indicação de anticoagular; o HAS-BLED é complementar, nunca gatekeeper dessa decisão.

## As sete variáveis do CHA₂DS₂-VA (entrada de cálculo, fora da árvore)

| letra | variável | pontos |
|---|---|---|
| C | Insuficiência cardíaca congestiva / disfunção de VE | 1 |
| H | Hipertensão | 1 |
| A₂ | Idade ≥75 anos | 2 |
| D | Diabetes mellitus | 1 |
| S₂ | AVC/AIT/tromboembolismo prévio | 2 |
| V | Doença vascular (DAC, DAP, placa aórtica) | 1 |
| A | Idade 65–74 anos | 1 |

Escore máximo: 9 pontos.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente com fibrilação atrial: calcular o escore CHA₂DS₂-VA"]
    A --> D{"Escore CHA₂DS₂-VA?"}
    D -->|"0 ponto"| C1(["Anticoagulação geralmente não indicada"])
    D -->|"1 ponto"| C2(["Avaliação individualizada — considerar anticoagulação oral conforme fatores de risco adicionais"])
    D -->|"2 ou mais pontos"| C3(["Anticoagulação oral recomendada"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3 conduta;
```

## O papel do HAS-BLED — complementar, não excludente

O HAS-BLED (Pisters R et al., Chest. 2010;138(5):1093-1100, PMID 20299623) estima risco de sangramento maior em 1 ano em quem já usa ou vai usar anticoagulação oral. Escore ≥3 indica risco aumentado de sangramento — mas isso pede monitorização mais frequente e correção de fatores modificáveis (hipertensão não controlada, álcool, AINE, INR lábil), **nunca** suspensão ou não indicação da anticoagulação em quem tem indicação clara pelo CHA₂DS₂-VA.

A diretriz ESC 2024 de fibrilação atrial afirma explicitamente que a decisão de anticoagular não deve ser condicionada a escore de sangramento — por isso o HAS-BLED não aparece como ramo de decisão nesta árvore. Ele se encaixa na etapa de reavaliação periódica (E — Evaluation) do caminho AF-CARE da ESC 2024, calibrando a frequência de acompanhamento de quem já está anticoagulado, não decidindo se deve estar.

## Armadilhas clínicas (herdadas dos documentos de origem)

- Usar HAS-BLED alto como critério de exclusão da anticoagulação — inverte o propósito do escore.
- Aplicar o corte de anticoagulação sem considerar que o escore 1 exige avaliação individualizada, não uma regra automática de "sim" ou "não".
- Confundir CHA₂DS₂-VA (sem o ponto de sexo feminino, ESC 2024) com o CHA₂DS₂-VASc anterior — os dois têm escore máximo diferente (9 vs. 9, mas composição distinta) e não são intercambiáveis sem checar qual diretriz está em uso.
