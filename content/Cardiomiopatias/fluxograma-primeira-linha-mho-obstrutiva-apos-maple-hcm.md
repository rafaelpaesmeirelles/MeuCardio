---
kind: fluxograma
published: true
review_note: Revisão individual contra SEQUOIA, análise JACC/JAHA, MAPLE, EXPLORER
  e VALOR; resultados, denominadores, moléculas e respostas conferidos. Corrigido
  alívio versus prevalência de sintomas, limites de FEVE e interrupção na dose mínima
  pela FDA 2025, árvores e avaliação esportiva pela AHA/ACC 2024. Resumo didático
  de RC não afirma quatro componentes oficiais. Sem assumir registro brasileiro.
review_status: revisado
slug: fluxograma-primeira-linha-mho-obstrutiva-apos-maple-hcm
source_refs:
- Garcia-Pavia P, Maron MS, Masri A, et al. Aficamten or Metoprolol Monotherapy for
  Obstructive Hypertrophic Cardiomyopathy. N Engl J Med. 2025;393(10):949-960. DOI
  10.1056/NEJMoa2504654. PMID 40888697.
- FDA. MYQORZO (aficamten) prescribing information, 2025, sections 2 and 5. https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/219083s000lbl.pdf
theme: Cardiomiopatias
title: 'Fluxograma: primeira linha na MHO obstrutiva após MAPLE-HCM'
---

# Fluxograma: primeira linha na MHO obstrutiva após MAPLE-HCM

Árvore de **escolha de monoterapia** na MHO obstrutiva sintomática. Não é algoritmo de descontinuação de betabloqueador, nem de indicação de miectomia/ablacão septal. MAPLE-HCM mostrou superioridade do aficamten sobre o metoprolol no VO2 pico em 24 semanas (diferença 2,3 ml/kg/min; IC95% 1,5–3,1; P<0,001). Isso **não** decreta aficamten como primeira linha obrigatória em todas as diretrizes.

Os nós finais estão duplicados de propósito: a árvore não converge.

## Árvore de decisão

```mermaid
flowchart TD
  X0["Paciente com suspeita de MHO obstrutiva sintomática"]
  D0{"Diagnóstico de MHO obstrutiva confirmado — gradiente e sintomas atribuíveis?"}
  C0(["Não iniciar inibidor de miosina: reavaliar fenótipo, gradiente e diagnóstico diferencial"])
  D1{"Há indicação de betabloqueador por outro motivo — FA com necessidade de frequência, angina, FE reduzida?"}
  C1(["Manter ou iniciar betabloqueador pela indicação associada. MAPLE-HCM não testa descontinuação nesse cenário"])
  D2{"FEVE ≥55%, revisão de interações e plano de eco permitem avaliar aficamten? Referência FDA 2025"}
  C2(["Não iniciar aficamten agora: investigar disfunção sistólica, obter eco basal e reavaliar"])
  D3{"Decisão compartilhada: monoterapia aficamten versus monoterapia metoprolol — MAPLE-HCM, 24 semanas"}
  C3A(["Aficamten em monoterapia com monitorização da FEVE: VO2 pico +1,1 vs −1,2 ml/kg/min com metoprolol; diferença 2,3"])
  C3B(["Metoprolol em monoterapia, com reavaliação de sintomas e gradiente. MAPLE não apaga o BB quando o paciente o prefere ou o acesso ao inibidor é inviável"])
  C3C(["Referência a centro de MHO: miectomia, ablação septal ou ensaio — fora do MAPLE-HCM"])

  X0 --> D0
  D0 -->|"Não confirmado"| C0
  D0 -->|"Sim — MHO obstrutiva sintomática"| D1
  D1 -->|"Sim — outra indicação de BB"| C1
  D1 -->|"Não"| D2
  D2 -->|"Não — FEVE ou logística inadequada"| C2
  D2 -->|"Sim — eco de baseline e reavaliação planejados"| D3
  D3 -->|"Prefere aficamten e há acesso e monitorização"| C3A
  D3 -->|"Prefere metoprolol ou inibidor indisponível"| C3B
  D3 -->|"Sintomas refratários a fármaco — discutir invasivo"| C3C

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f
  class C0,C1,C2,C3A,C3B,C3C conduta
```

## Tudo com Tudo

- Cardiomiopatias
- Farmacologia
- Insuficiência cardíaca
- Comunicação clínica
- Cardiologia do Esporte e do Exercício

Referência FDA 2025 (EUA): não iniciar/aumentar aficamten com FEVE <55%. FEVE 40 a <50%: reduzir 5 mg; se já em 5 mg, interromper. FEVE <40%: interromper. Reintrodução, quando cabível, somente após pelo menos sete dias e FEVE ≥55%, em 5 mg. Eco após início/ajuste e avaliação de interações são indispensáveis. Não transpor esses limites para mavacamten nem afirmar aprovação brasileira. A indicação associada de betabloqueador não proíbe automaticamente tratamento adicional: este fluxo limita-se à pergunta de monoterapia do MAPLE.
