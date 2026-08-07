---
title: "Fluxograma: Colapso neonatal por cardiopatia congênita crítica canal-dependente"
slug: fluxograma-colapso-neonatal-por-cardiopatia-congenita-critica-canal-dependente
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de decisão para RN com cianose, choque ou acidose por possível fechamento do canal arterial, incluindo PGE1/alprostadil e transferência para centro de cardiologia pediátrica."
review_status: revisado
source_refs: ["Singh Y. Diagnosis and management of critical congenital heart defects in infants. Paediatr Child Health. 2022;32(9):332-338. DOI: 10.1016/j.paed.2022.07.003.", "Chan B, Singh Y. Prostaglandin E1: Infants With Critical Congenital Heart Defects. Neoreviews. 2024;25(12):e765-e779. DOI: 10.1542/neo.25-12-e765. PMID: 39616144.", "Haughey BS, Elliott MR, Wiggin JY, et al. Standardizing Prostaglandin Initiation in Prenatally Diagnosed Ductal-Dependent Neonates; A Quality Initiative. Pediatr Cardiol. 2023;44(6):1327-1332. DOI: 10.1007/s00246-022-03075-9. PMID: 36538050."]
---

# Colapso neonatal canal-dependente

```mermaid
flowchart TD
  R0["RN nas primeiras horas/dias com<br/>choque, acidose, cianose ou hipoxemia inexplicada"]
  P1["ABC + monitorização + acesso vascular<br/>+ gasometria/lactato + pulsos pré/pós-ductais;<br/>acionar neonatologia/cardiologia pediátrica"]
  D1{"Há forte suspeita de cardiopatia crítica<br/>canal-dependente?"}
  C1(["Não: investigar sepse, doença pulmonar,<br/>distúrbios metabólicos e outras causas;<br/>manter baixa barreira para ecocardiograma"])
  P2["Sim: iniciar PGE1/alprostadil sem aguardar<br/>definição anatômica completa + ecocardiograma urgente"]
  D2{"RN estável / diagnóstico antenatal<br/>e canal provavelmente ainda patente?"}
  C2(["PGE1 0,005–0,01 µg/kg/min IV contínuo;<br/>monitorar perfusão, saturação e efeitos adversos"])
  C3(["RN colapsado/acidótico: PGE1 0,05–0,1 µg/kg/min<br/>IV contínuo pode ser necessária inicialmente;<br/>preparar ventilação/intubação"])
  D3{"Qual padrão fisiológico predomina?"}
  C4(["Fluxo sistêmico dependente:<br/>buscar melhora de pulsos/perfusão,<br/>acidose e lactato"])
  C5(["Fluxo pulmonar dependente:<br/>buscar melhora de saturação/oxigenação"])
  C6(["Mistura inadequada/TGA:<br/>PGE1 pode não ser suficiente;<br/>avaliar comunicação interatrial e necessidade<br/>de septostomia atrial urgente"])
  D4{"Resposta clínica adequada?"}
  P3["Sim: reduzir gradualmente para a menor<br/>taxa eficaz que mantenha estabilidade ductal"]
  P4["Não: reavaliar anatomia/fisiologia,<br/>via aérea, volume, função ventricular e<br/>necessidade de intervenção urgente"]
  C7(["Transferir/manter em centro com cardiologia<br/>pediátrica, hemodinâmica e cirurgia congênita"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P2
  P2 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não / colapso"| C3
  C2 --> D3
  C3 --> D3
  D3 -->|"Sistêmico"| C4
  D3 -->|"Pulmonar"| C5
  D3 -->|"Mistura/TGA"| C6
  C4 --> D4
  C5 --> D4
  C6 --> D4
  D4 -->|"Sim"| P3
  D4 -->|"Não"| P4
  P3 --> C7
  P4 --> C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Segurança

PGE1 pode causar apneia, hipotensão e febre. Doses mais altas são reservadas ao neonato colapsado quando o benefício de reabrir rapidamente o canal supera o risco; após resposta, reduzir para a menor dose eficaz.
