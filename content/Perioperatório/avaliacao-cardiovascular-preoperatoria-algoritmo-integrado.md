---
title: "Avaliação cardiovascular pré-operatória: algoritmo integrado"
slug: avaliacao-cardiovascular-preoperatoria-algoritmo-integrado
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Rota visual para decidir quando prosseguir para cirurgia, quando pausar para estabilização cardiovascular e quando acrescentar biomarcadores, teste funcional, teste de isquemia ou CCTA."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024. DOI: 10.1161/CIR.0000000000001285."
  - "Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz de Avaliação Cardiovascular Perioperatória da Sociedade Brasileira de Cardiologia – 2024. Arq Bras Cardiol. 2024;121(9):e20240590. PMID: 39442131. DOI: 10.36660/abc.20240590."
  - "Halvorsen S, Mehilli J, Cassese S, et al. 2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery. Eur Heart J. 2022;43(39):3826-3924. PMID: 36017553. DOI: 10.1093/eurheartj/ehac270."
---

# Avaliação cardiovascular pré-operatória — algoritmo integrado

## Princípio

A avaliação pré-operatória deve responder a três perguntas, nesta ordem:

1. **Há condição cardiovascular instável que precisa ser tratada independentemente da cirurgia?**
2. **Qual é o risco combinado do paciente e do procedimento?**
3. **Um exame adicional tem probabilidade real de mudar a decisão, o tratamento ou o planejamento anestésico/cirúrgico?**

A diretriz AHA/ACC 2024 reforça que rastreamento e tratamento cardiovasculares no perioperatório devem obedecer às mesmas indicações utilizadas fora do contexto cirúrgico, evitando investigação excessiva e atraso sem benefício.

## Árvore de decisão principal

```mermaid
flowchart TD
  A["Paciente candidato a cirurgia não cardíaca"] --> B{"Cirurgia de emergência?"}
  B -->|"Sim"| C["Prosseguir com cirurgia + monitorização e manejo perioperatório apropriados"]
  B -->|"Não"| D{"Síndrome coronariana aguda, IC descompensada, arritmia instável ou outra condição cardiovascular ativa/instável?"}
  D -->|"Sim"| E["Pausar cirurgia eletiva/tempo-sensível quando clinicamente possível; diagnosticar e tratar condição"]
  D -->|"Não"| F["Estimar risco por ferramenta validada: RCRI, Gupta MICA ou outra apropriada"]
  F --> G{"Risco global baixo?\nMACE <1% ou equivalente"}
  G -->|"Sim"| H["Prosseguir; não solicitar teste de isquemia de rotina"]
  G -->|"Não"| I["Avaliar capacidade funcional: DASI/METs"]
  I --> J{"Capacidade adequada?\n≥4 METs ou DASI >34"}
  J -->|"Sim, sintomas estáveis"| K["Prosseguir; investigação adicional apenas se houver indicação clínica independente"]
  J -->|"Não / desconhecida"| L["Considerar biomarcadores conforme risco e contexto"]
  L --> M{"Biomarcador normal e nenhuma outra condição de alto risco?"}
  M -->|"Sim"| N["Prosseguir com estratégia de redução de risco e monitorização apropriada"]
  M -->|"Não"| O{"Resultado de teste adicional mudará manejo?"}
  O -->|"Não"| P["Não testar por rotina; proceder com plano perioperatório individualizado"]
  O -->|"Sim"| Q["Considerar teste de estresse ou CCTA conforme perfil clínico e disponibilidade"]
  Q --> R{"Anatomia coronária de alto risco / isquemia relevante?"}
  R -->|"Não"| S["Prosseguir com otimização clínica"]
  R -->|"Sim"| T["Discussão multidisciplinar; tratar DAC conforme indicação independente da cirurgia"]
```

## Pontos de corte operacionais da AHA/ACC 2024

- **Risco elevado:** tradicionalmente RCRI >1 ou risco de MACE calculado >1%.
- **Capacidade funcional pobre:** <4 METs ou **DASI ≤34**.
- Biomarcadores considerados anormais no algoritmo AHA/ACC 2024: **troponina acima do percentil 99 do ensaio**, **BNP >92 ng/L** ou **NT-proBNP ≥300 ng/L**.
- Teste de estresse pode ser considerado em cirurgia de risco elevado quando coexistem capacidade funcional pobre/desconhecida e risco cardiovascular elevado por ferramenta validada.
- Teste de estresse rotineiro não é recomendado em paciente de baixo risco, procedimento de baixo risco ou paciente com capacidade funcional adequada e sintomas estáveis.
- CCTA pode ser considerada em cenário semelhante quando a detecção de anatomia coronária de alto risco puder mudar a conduta.

## Quando solicitar ecocardiograma

```mermaid
flowchart TD
  A["Avaliação pré-operatória"] --> B{"Dispneia nova, sinais de IC ou suspeita de disfunção ventricular nova/pior?"}
  B -->|"Sim"| C["Avaliar função ventricular por ecocardiografia"]
  B -->|"Não"| D{"IC conhecida com mudança do estado clínico?"}
  D -->|"Sim"| C
  D -->|"Não"| E["Paciente assintomático e clinicamente estável"]
  E --> F["Não realizar avaliação rotineira de função ventricular apenas por ser pré-operatório"]
```

## Mensagem para o laudo

O risco deve ser comunicado em **termos absolutos**, quando possível, e não apenas como “baixo/moderado/alto”. A ferramenta de risco é parte da avaliação; não substitui sintomas, estado funcional, fragilidade, urgência da cirurgia, tipo de anestesia e presença de doença cardiovascular ativa.

## Limitações

- As classificações de risco cirúrgico e as recomendações específicas podem variar entre AHA/ACC, ESC e SBC.
- A decisão de adiar cirurgia tempo-sensível deve ser compartilhada com cirurgia, anestesia e equipe clínica responsável.
- Nenhum escore isolado deve determinar teste invasivo ou revascularização.
