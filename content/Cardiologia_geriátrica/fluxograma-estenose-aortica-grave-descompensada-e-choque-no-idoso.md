---
title: "Fluxograma: Estenose aórtica grave descompensada e choque no idoso"
slug: fluxograma-estenose-aortica-grave-descompensada-e-choque-no-idoso
theme: "Cardiologia geriátrica"
kind: fluxograma
summary: "Árvore de emergência para idoso com EAo grave e IC aguda/choque, com estabilização, identificação de gatilho e acionamento precoce do Heart Team para TAVI/SAVR ou BAV como ponte em casos selecionados."
review_status: revisado
source_refs: ["Praz F, Borger MA, Lanz J, et al.; ESC/EACTS Scientific Document Group. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4736. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295."]
---

# EAo grave descompensada/choque no idoso

```mermaid
flowchart TD
  R0["Idoso com EAo grave conhecida/suspeita<br/>+ IC aguda, edema pulmonar, hipotensão ou choque"]
  P1["ABC + monitorização + ECG + eco urgente;<br/>identificar isquemia, arritmia, infecção, anemia<br/>ou outro gatilho reversível; acionar Heart Team"]
  D1{"EAo grave é componente dominante<br/>da deterioração hemodinâmica?"}
  C1(["Não: tratar causa predominante e reavaliar<br/>contribuição da valvopatia"])
  P2["Sim: estabilização cuidadosa da pré-carga/pressão;<br/>diurese titulada se congesto; suporte vasoativo/inotrópico<br/>individualizado; corrigir arritmia/gatilho"]
  D2{"Há choque ou falência orgânica progressiva<br/>apesar do suporte inicial?"}
  P3["Sim: intervenção valvar deve ser considerada cedo;<br/>não prolongar suporte isolado se obstrução é a causa"]
  D3{"TAVI urgente é anatomicamente e logisticamente viável<br/>e há expectativa razoável de benefício?"}
  C2(["Sim: proceder para TAVI urgente/emergencial<br/>em centro valvar experiente"])
  D4{"TAVI/SAVR definitiva não pode ser feita agora,<br/>mas há potencial de ponte para tratamento definitivo?"}
  C3(["Sim: BAV pode ser raramente considerada como ponte,<br/>reconhecendo risco de insuficiência aórtica aguda"])
  C4(["Não: discutir SAVR/outro suporte conforme anatomia<br/>ou objetivos de cuidado se intervenção for fútil"])
  D5{"Sem choque, mas descompensação persistente?"}
  C5(["Avaliação acelerada do Heart Team para intervenção;<br/>tratamento clínico é ponte, não solução definitiva"])
  C6(["Após estabilização/intervenção: reavaliar função,<br/>fragilidade, cognição e plano de reabilitação"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P2
  P2 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| D5
  P3 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| C4
  D5 -->|"Sim"| C5
  D5 -->|"Não/resolveu gatilho"| C6
  C2 --> C6
  C3 --> C6
  C4 --> C6
  C5 --> C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Regra prática

Quando a EAo grave é a causa mecânica do choque, **o suporte clínico ganha tempo, mas não remove a obstrução**. A ESC/EACTS 2025 favorece avaliação intervencionista precoce; BAV é hoje principalmente uma ponte rara em casos selecionados.
