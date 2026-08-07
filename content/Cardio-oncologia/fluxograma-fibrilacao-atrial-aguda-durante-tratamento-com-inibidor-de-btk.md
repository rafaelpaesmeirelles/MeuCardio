---
title: "Fluxograma: FA aguda durante tratamento com inibidor de BTK"
slug: fluxograma-fibrilacao-atrial-aguda-durante-tratamento-com-inibidor-de-btk
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para FA em paciente em ibrutinibe/acalabrutinibe, separando instabilidade, controle de ritmo/frequência e decisão antitrombótica baseada também em sangramento e interações."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al.; ESC Scientific Document Group. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568."]
---

# FA aguda durante inibidor de BTK

```mermaid
flowchart TD
  R0["Paciente em inibidor de BTK<br/>+ FA nova/recorrente"]
  D1{"Instabilidade hemodinâmica?<br/>choque, isquemia, edema pulmonar<br/>ou alteração importante da consciência"}
  P1["Cardioversão elétrica sincronizada<br/>conforme protocolo geral de FA"]
  P2["Estável: ECG, eletrólitos, função renal/hepática<br/>+ procurar infecção, anemia, hipóxia, TEP<br/>e outros precipitantes"]
  D2{"Controle de frequência/ritmo<br/>necessário?"}
  P3["Escolher estratégia individualizada;<br/>checar QT e interações com terapia oncológica"]
  D3{"Indicação de anticoagulação?"}
  P4["Avaliar risco tromboembólico + sangramento<br/>+ interações + plaquetas + sítio tumoral<br/>+ função renal/hepática"]
  D4{"Sangramento ativo/risco hemorrágico muito alto<br/>ou interação maior?"}
  P5["Discutir estratégia alternativa/adiamento<br/>com cardio-oncologia + hematologia/oncologia"]
  P6["Selecionar anticoagulante e dose<br/>conforme protocolo individual"]
  D5{"TV/QRS largo, síncope inexplicada<br/>ou PCR?"}
  C1(["Migrar para algoritmo de<br/>arritmia ventricular/PCR"])
  C2(["Manter monitorização e decisão<br/>multidisciplinar sobre BTK"])

  R0 --> D1
  D1 -->|"Sim"| P1
  D1 -->|"Não"| P2
  P1 --> D3
  P2 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| D3
  P3 --> D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| D5
  P4 --> D4
  D4 -->|"Sim"| P5
  D4 -->|"Não"| P6
  P5 --> D5
  P6 --> D5
  D5 -->|"Sim"| C1
  D5 -->|"Não"| C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

FA em paciente em BTK exige três perguntas simultâneas: **está instável? precisa controle de ritmo/frequência? pode anticoagular com segurança?** O câncer, a plaquetopenia e as interações impedem automatizar a terceira resposta.