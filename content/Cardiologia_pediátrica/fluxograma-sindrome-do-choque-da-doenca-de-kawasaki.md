---
title: "Fluxograma: Síndrome do choque da doença de Kawasaki"
slug: fluxograma-sindrome-do-choque-da-doenca-de-kawasaki
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para criança com choque febril e suspeita de Kawasaki, incorporando ecocardiograma com medidas coronarianas, estabilização intensiva e IVIG 2 g/kg quando o diagnóstico é estabelecido."
review_status: revisado
source_refs: ["Jone PN, Tremoulet A, Choueiter N, et al. Update on Diagnosis and Management of Kawasaki Disease: A Scientific Statement From the American Heart Association. Circulation. 2024;150(23):e481-e500. DOI: 10.1161/CIR.0000000000001295. PMID: 39534969. Correction: Circulation. 2025;151(14):e923. DOI: 10.1161/CIR.0000000000001324. PMID: 40163561.", "Gorelik M, Chung SA, Ardalan K, et al. 2021 American College of Rheumatology/Vasculitis Foundation Guideline for the Management of Kawasaki Disease. Arthritis Rheumatol. 2022;74(4):586-596. DOI: 10.1002/art.42041. PMID: 35257501.", "Kanegaye JT, Wilder MS, Molkara D, et al. Recognition of a Kawasaki disease shock syndrome. Pediatrics. 2009;123(5):e783-e789. DOI: 10.1542/peds.2008-1871. PMID: 19403470."]
---

# Síndrome do choque da doença de Kawasaki

```mermaid
flowchart TD
  R0["Criança com febre persistente + hipotensão,<br/>queda sustentada da PA ou sinais de hipoperfusão"]
  P1["ABC + monitorização + acesso vascular;<br/>culturas/antimicrobiano se sepse plausível;<br/>avaliar critérios completos/incompletos de Kawasaki"]
  D1{"Choque permanece sem causa suficientemente explicada?"}
  P2["Sim: obter ecocardiograma urgente com<br/>FUNÇÃO + medidas coronarianas/Z-scores<br/>(recomendação forte ACR/VF)"]
  C1(["Não: tratar causa predominante, mantendo<br/>Kawasaki no diferencial se o curso for incompatível"])
  D2{"Conjunto clínico/laboratorial/eco sustenta Kawasaki?"}
  C2(["Não/incerto: reavaliar sepse, MIS-C, miocardite<br/>e outras causas; repetir eco se suspeita persistir"])
  P3["Sim: IVIG 2 g/kg em dose única +<br/>tratamento anti-inflamatório/antiagregante<br/>conforme protocolo de Kawasaki"]
  D3{"Hipoperfusão/choque persiste?"}
  P4["Sim: UTI pediátrica; volume cuidadosamente titulado<br/>+ vasoativo/inotrópico conforme fenótipo;<br/>reavaliar função ventricular e coronárias"]
  C3(["Não: manter vigilância, ecocardiografia seriada<br/>e seguimento de coronárias"])
  D4{"Alto risco coronariano, resistência ao IVIG,<br/>MAS ou inflamação grave persistente?"}
  C4(["Sim: discutir terapia anti-inflamatória adicional<br/>com cardiologia/reumatologia/infectologia;<br/>não há regime único universal só por haver choque"])
  C5(["Não: seguir protocolo padrão e vigilância coronariana"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| C1
  P2 --> D2
  D2 -->|"Não/incerto"| C2
  D2 -->|"Sim"| P3
  P3 --> D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| C3
  P4 --> D4
  C3 --> D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Ponto-chave

Em choque febril inexplicado, o ecocardiograma precisa incluir **coronárias**, não apenas função ventricular. Se Kawasaki estiver sustentada, IVIG 2 g/kg é tratamento de primeira linha; vasoativo e imunomodulação adicional dependem do fenótipo clínico e do risco.
