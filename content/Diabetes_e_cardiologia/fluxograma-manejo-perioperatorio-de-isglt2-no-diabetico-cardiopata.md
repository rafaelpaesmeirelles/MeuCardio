---
title: "Fluxograma: Manejo Perioperatório de Inibidores de SGLT2 no Diabético Cardiopata"
slug: fluxograma-manejo-perioperatorio-de-isglt2-no-diabetico-cardiopata
theme: "Diabetes e cardiologia"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de fonte nova consultada e verificada nesta produção, buscada e conferida via PubMed E-utilities (esearch/esummary/efetch) e leitura de texto integral no PMC — nenhum PMID, DOI ou número foi inventado. Fonte principal: American Diabetes Association Professional Practice Committee, '16. Diabetes Care in the Hospital: Standards of Care in Diabetes-2024', Diabetes Care 2024;47(Suppl 1):S295-S306, DOI 10.2337/dc24-S016, PMID 38078585 — confirma a suspensão do iSGLT2 3-4 dias antes de cirurgia, com o intervalo de 4 dias específico para ertugliflozina (citando o alerta da FDA), a suspensão de metformina no dia da cirurgia (usada só como contraste no texto, não como ramo da árvore) e o critério de reintrodução hospitalar do iSGLT2 apenas após recuperação da doença aguda e ausência de contraindicação. Segunda fonte, também verificada por texto integral: Levy NA, El-Boghdadly K, Lobo DN, et al., 'Peri-operative management of diabetes mellitus: a multidisciplinary consensus statement from the Association of Anaesthetists and the Joint British Diabetes Societies for Inpatient Care group', Anaesthesia 2026;81(8):1116-1131, DOI 10.1111/anae.70181, PMID 41696887, texto integral conferido via PMC13352544 (pmc.ncbi.nlm.nih.gov) — usada para o ramo de cirurgia urgente/sem antecedência suficiente (monitorização diária de cetonas capilares mesmo com glicemia normal, gatilho de duas glicemias consecutivas acima de 13 mmol/L ou mal-estar para dosar cetonemia) e para a caracterização do iSGLT2 como classe com benefício cardiovascular e renal estabelecido, que justifica a reintrodução precoce assim que segura. Este recorte é distinto dos três fluxogramas já publicados neste tema: 'fluxograma-diabetes-e-doenca-cardiovascular-esc-2023.md' trata do rastreamento inicial e da escolha de terapia crônica orientada por condição predominante (não aborda cirurgia); 'fluxograma-escolha-isglt2-glp1-diabetico-doenca-cardiovascular.md' decide entre iSGLT2 e GLP-1 para tratamento ambulatorial crônico por condição cardiovascular/renal predominante, sem tocar em manejo perioperatório (e cita explicitamente o risco de cetoacidose euglicêmica com iSGLT2 apenas como observação lateral, não desenvolvida); 'fluxograma-investigacao-neuropatia-autonomica-cardiovascular-diabetico.md' é sobre rastreio de neuropatia autonômica cardiovascular, tema não relacionado. Este fluxograma cobre exclusivamente a decisão prática de quando suspender e quando reintroduzir o iSGLT2 ao redor de um procedimento cirúrgico/invasivo no diabético tipo 2 cardiopata, incluindo o cenário de cirurgia urgente sem tempo hábil para suspensão programada — recorte ainda não coberto no tema."
source_refs: ["American Diabetes Association Professional Practice Committee. 16. Diabetes Care in the Hospital: Standards of Care in Diabetes-2024. Diabetes Care. 2024;47(Suppl 1):S295-S306. DOI: 10.2337/dc24-S016. PMID: 38078585.", "Levy NA, El-Boghdadly K, Lobo DN, et al. Peri-operative management of diabetes mellitus: a multidisciplinary consensus statement from the Association of Anaesthetists and the Joint British Diabetes Societies for Inpatient Care group. Anaesthesia. 2026;81(8):1116-1131. DOI: 10.1111/anae.70181. PMID: 41696887.", "Buggy DJ, Columb MO, Hermanides J, et al. Withholding or continuing glucose-lowering drugs for elective surgery in patients with type 2 diabetes mellitus: a secondary analysis of the MOPED international, prospective, observational study. Br J Anaesth. 2026;137(1):99-109. DOI: 10.1016/j.bja.2026.03.068. PMID: 42191528 — usado apenas na seção de limitações, para registrar que os dados observacionais mais recentes ainda não mostram diferença estatisticamente significativa de cetoacidose entre suspender e manter o iSGLT2 no perioperatório, em coortes pequenas."]
---

# Fluxograma: Manejo Perioperatório de Inibidores de SGLT2 no Diabético Cardiopata

O inibidor de SGLT2 (iSGLT2) hoje é tratamento de base para o diabético tipo 2
com doença cardiovascular, insuficiência cardíaca ou doença renal crônica — é
exatamente por isso que a pergunta de quando suspendê-lo antes de uma cirurgia,
e quando reintroduzi-lo depois, se tornou frequente em qualquer cardiopata
diabético que vai a um procedimento invasivo. A classe está associada a
cetoacidose diabética euglicêmica no período de jejum, um quadro que cursa com
glicemia normal ou pouco elevada e por isso escapa da suspeita clínica
habitual. Este fluxograma organiza a decisão de suspensão e reintrodução do
iSGLT2 ao redor do procedimento, separando o cenário eletivo (com tempo para
planejar) do urgente/emergente (sem esse tempo), e não repete o conteúdo dos
três fluxogramas já publicados neste tema — nenhum deles trata do período
perioperatório.

## Árvore de decisão

```mermaid
flowchart TD
  R{"Paciente cardiopata com diabetes tipo 2 em uso de inibidor de SGLT2 (dapagliflozina, empagliflozina, canagliflozina ou ertugliflozina) será submetido a cirurgia ou procedimento invasivo com jejum perioperatório?"}

  R -->|"Procedimento eletivo, com pelo menos 4 dias de antecedência para suspender o fármaco"| D1{"Qual inibidor de SGLT2 o paciente utiliza?"}

  R -->|"Procedimento urgente, emergente ou eletivo sem antecedência suficiente para suspensão programada"| P2["Suspender o iSGLT2 assim que a decisão do procedimento for tomada, mesmo sem completar o intervalo pleno; independentemente do tempo de suspensão alcançado, iniciar monitorização diária de cetonas capilares, mesmo com glicemia normal, até a alimentação e a hidratação orais normalizarem (JBDS-IP/Association of Anaesthetists 2026)"]

  D1 -->|"Ertugliflozina"| P1a["Suspender a ertugliflozina 4 dias antes do procedimento — intervalo específico recomendado pela FDA para esta molécula, citado pela ADA Standards of Care in Diabetes-2024; manter monitorização diária de cetonas capilares até a alimentação e a hidratação orais normalizarem"]

  D1 -->|"Dapagliflozina, empagliflozina ou canagliflozina"| P1b["Suspender o iSGLT2 3 dias antes do procedimento (ADA Standards of Care in Diabetes-2024); manter monitorização diária de cetonas capilares até a alimentação e a hidratação orais normalizarem"]

  P1a -->|"Após o intervalo de suspensão perioperatória"| D2a{"No pós-operatório, o paciente já está se alimentando e se hidratando por via oral normalmente, sem doença aguda intercorrente (infecção, injúria renal aguda, cetoacidose) e sem contraindicação ao fármaco?"}

  P1b -->|"Após o intervalo de suspensão perioperatória"| D2b{"No pós-operatório, o paciente já está se alimentando e se hidratando por via oral normalmente, sem doença aguda intercorrente (infecção, injúria renal aguda, cetoacidose) e sem contraindicação ao fármaco?"}

  D2a -->|"Sim"| C1a(["Reintroduzir a ertugliflozina assim que não houver contraindicação e a doença aguda estiver resolvida, retomando o benefício cardiovascular e renal do iSGLT2 (ADA Standards of Care in Diabetes-2024)"])

  D2a -->|"Não"| C1b(["Manter a ertugliflozina suspensa; reavaliar diariamente a condição clínica e reintroduzir somente após recuperação completa, sem contraindicação (ADA Standards of Care in Diabetes-2024)"])

  D2b -->|"Sim"| C2a(["Reintroduzir o iSGLT2 assim que não houver contraindicação e a doença aguda estiver resolvida, retomando o benefício cardiovascular e renal do iSGLT2 (ADA Standards of Care in Diabetes-2024)"])

  D2b -->|"Não"| C2b(["Manter o iSGLT2 suspenso; reavaliar diariamente a condição clínica e reintroduzir somente após recuperação completa, sem contraindicação (ADA Standards of Care in Diabetes-2024)"])

  P2 -->|"Durante a internação e o pós-operatório imediato"| D3{"O paciente apresenta duas ou mais glicemias capilares consecutivas acima de 13 mmol/L (acima de 234 mg/dL) ou mal-estar/sintomas sugestivos, mesmo com glicemia normal?"}

  D3 -->|"Sim"| C3(["Dosar cetonemia capilar; se compatível com cetoacidose euglicêmica associada a iSGLT2, tratar pelo protocolo institucional de cetoacidose diabética, suspender definitivamente o fármaco neste episódio e não reintroduzi-lo até resolução completa e reavaliação especializada (JBDS-IP/Association of Anaesthetists 2026; ADA Standards of Care in Diabetes-2024)"])

  D3 -->|"Não"| C4(["Manter a monitorização diária de cetonas capilares até a alimentação e a hidratação orais normalizarem; manter o iSGLT2 suspenso nesse período e reavaliar a reintrodução após recuperação clínica completa, sem contraindicação (JBDS-IP/Association of Anaesthetists 2026)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1a,C1b,C2a,C2b,C3,C4 conduta;
```

## O que a árvore não mostra

- **A ertugliflozina tem ramo próprio só pela diferença de intervalo, não por
  diferença de conduta.** A ADA Standards of Care in Diabetes-2024 registra que
  a FDA recomenda 3 dias de suspensão para a classe em geral e 4 dias
  especificamente para a ertugliflozina — o restante da decisão (monitorização
  de cetonas, critério de reintrodução) é idêntico entre as moléculas.
- **O gatilho de duas glicemias consecutivas acima de 13 mmol/L para dosar
  cetonemia vem da consenso multidisciplinar britânico (JBDS-IP/Association of
  Anaesthetists 2026), não é um corte da ADA.** Essa mesma fonte recomenda
  monitorização diária de cetonas em todo paciente diabético em uso de iSGLT2
  internado, mesmo com glicemia normal, até a retomada da alimentação e
  hidratação orais — é a base do ramo de cirurgia urgente, no qual não há tempo
  para completar o intervalo de suspensão programado.
- **Não há corte numérico de cetonemia capilar que defina tratamento como
  cetoacidose nesta árvore**, porque as duas fontes verificadas nesta produção
  não especificam esse valor — a decisão de tratar segue o protocolo
  institucional de cetoacidose diabética diante do quadro clínico compatível
  (cetonemia elevada com sintomas ou hiperglicemia persistente), sem que um
  número específico de mmol/L de cetona tenha sido verificado em fonte
  primária para esta árvore.
- **Os dados observacionais mais recentes ainda são pequenos e não mostram
  diferença estatisticamente significativa de cetoacidose entre suspender e
  manter o iSGLT2 no perioperatório.** A análise secundária do estudo MOPED
  (Buggy DJ et al., Br J Anaesth 2026) encontrou taxas semelhantes de
  cetoacidose entre os dois grupos (1,9% suspenso vs. 1,6% mantido), mas os
  próprios autores destacam que as coortes de iSGLT2 eram pequenas demais para
  conclusões firmes — o que reforça, e não contradiz, a prática de seguir a
  suspensão programada recomendada pela ADA e pelo consenso britânico em vez
  de manter o fármaco no perioperatório.
- **Contraindicações específicas do iSGLT2 fora do contexto perioperatório**
  (infecção genital recorrente, TFGe abaixo do limiar de início da classe) não
  são ramos desta árvore — entram na decisão individual de manter o paciente
  na classe a longo prazo, já tratada no fluxograma de escolha entre iSGLT2 e
  GLP-1 desta mesma pasta.
