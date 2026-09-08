---
title: "Fluxograma: sinalizadores ambulatoriais de PVC frequente — PS agora vs. EP/ablação vs. vigilância"
slug: fluxograma-sinalizadores-ambulatoriais-pvc-frequente
theme: "Arritmias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de PVC frequente: canalopatia/emergência primeiro; depois sintomas, causalidade provável e função ventricular para decidir EP, sem usar 24% como requisito."
review_status: revisado
review_note: "Revisão clínica final 08/09/2026. Canalopatias adicionadas ao gate de urgência; removido >24% como pré-requisito de ablação; pacientes sintomáticos mantidos na via EP; monomorfismo não é indicação isolada; seguimento <10% não recebe classe IIa indevida."
source_refs:
  - "Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC VA/SCD Guidelines. PMID: 36017572"
  - "Cronin EM, Bogun FM, Maury P, et al. 2019 HRS/EHRA/APHRS/LAHRS consensus. PMID: 32071620"
  - "Baman TS, Lange DC, Ilg KJ, et al. PVC burden and LV function. PMID: 20348027"
---

# Fluxograma: sinalizadores ambulatoriais de PVC frequente

```mermaid
flowchart TD
  R0["PVC frequente em ECG/Holter"] --> D1{"Emergência/canalopatia de alto risco?<br/>síncope arrítmica · TV sustentada/polimórfica<br/>instabilidade · SCA/IC aguda<br/>Brugada sintomático · QT longo/curto com arritmia"}
  D1 -->|"Sim"| C1(["PS / emergência AGORA"])

  D1 -->|"Não"| D2{"FEVE reduzida/dilatação<br/>sem outra causa mais provável?"}
  D2 -->|"Sim"| D3{"PVC frequente é causal/contribuinte plausível?<br/>morfologia predominantemente monomórfica<br/>+ relação temporal/carga relevante"}
  D3 -->|"Sim"| C2(["EP eletiva<br/>Discutir ablação conforme HRS/ESC<br/>sem exigir carga >24%"])
  D3 -->|"Não/dúvida"| C3(["Investigar outras causas estruturais<br/>RM/EP conforme contexto"])

  D2 -->|"Não"| D4{"Sintomas limitantes/QoL afetada<br/>atribuíveis aos PVCs?"}
  D4 -->|"Sim"| C4(["EP eletiva para estratégia terapêutica<br/>independentemente de não atingir 24%"])

  D4 -->|"Não"| D5{"Carga aproximadamente >=10%?"}
  D5 -->|"Sim"| C5(["Vigilância de carga e função ventricular<br/>Ablação não automática"])
  D5 -->|"Não"| C6(["Seguimento clínico individualizado<br/>Sem atribuir IIa automática ao <10%"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1 alerta;
  class C2,C3,C4,C5,C6 conduta;
```

## Notas
- Baman >24% é discriminador de coorte, não requisito para ablação.
- Sintomas relevantes podem justificar EP mesmo com VE preservado e carga 10–24%.
- Monomorfismo é modificador de causalidade/viabilidade da ablação, não gatilho isolado.
