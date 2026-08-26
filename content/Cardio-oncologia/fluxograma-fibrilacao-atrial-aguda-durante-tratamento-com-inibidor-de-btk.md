---
title: "Fluxograma: FA aguda durante tratamento com inibidor de BTK"
slug: fluxograma-fibrilacao-atrial-aguda-durante-tratamento-com-inibidor-de-btk
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para FA em paciente em ibrutinibe/acalabrutinibe, separando instabilidade, controle de ritmo/frequência e decisão antitrombótica baseada também em sangramento e interações."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al.; ESC Scientific Document Group. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568."]
review_note: "Revisado em 26/08/2026 contra as seções 5.5.6 e 6.4.1 e a Tabela de Recomendação 31 da diretriz ESC 2022 de cardio-oncologia (PMID 36017568). O ramo genérico de controle de frequência/ritmo foi corrigido para priorizar betabloqueador e evitar, quando possível, diltiazem/verapamil por interação e inotropismo negativo. A anticoagulação passou a separar contraindicação temporária por risco hemorrágico muito alto, indicação exclusiva de VKA, fatores que podem favorecer LMWH apenas como estratégia de curto prazo e seleção de NOAC condicionada a interação, função renal, sítio tumoral e absorção. A eficácia de LMWH para prevenir AVC na FA não está estabelecida. Pendente revisão médica independente antes de uso assistencial."
---

# FA aguda durante inibidor de BTK

```mermaid
flowchart TD
  R0["Paciente em inibidor de BTK<br/>+ FA nova/recorrente"]
  D1{"Instabilidade hemodinâmica?<br/>choque, isquemia, edema pulmonar<br/>ou alteração importante da consciência"}
  P1["Cardioversão elétrica sincronizada<br/>conforme protocolo geral de FA"]
  P2["Estável: ECG, eletrólitos, função renal/hepática<br/>+ procurar infecção, anemia, hipóxia, TEP<br/>e outros precipitantes"]
  D2{"Controle de frequência/ritmo<br/>necessário?"}
  P3["Preferir betabloqueador para frequência;<br/>evitar, quando possível, diltiazem/verapamil.<br/>Se estratégia de ritmo: checar QT e interações"]
  D3{"Anticoagulação indicada ou a considerar<br/>após CHA2DS2-VASc + contexto oncológico?"}
  P4["Aplicar TBIP: risco trombótico + sangramento<br/>+ interações + preferência; conferir plaquetas,<br/>sítio tumoral, função renal e absorção"]
  D4{"Risco hemorrágico muito alto?<br/>sangramento maior ativo/recente &lt;1 mês,<br/>lesão intracraniana ou plaquetas &lt;25.000/µL"}
  P5["Não iniciar automaticamente;<br/>corrigir causa e discutir momento/alternativa<br/>com cardio-oncologia + hematologia/oncologia"]
  D4A{"Prótese mecânica ou<br/>estenose mitral moderada/grave?"}
  P6["VKA conforme protocolo específico"]
  D4B{"Tumor GI/GU não operado, toxicidade GI,<br/>CrCl &lt;15, plaquetas &lt;50.000/µL<br/>ou interação maior com NOAC?"}
  P7["Discutir LMWH como opção de curto prazo;<br/>eficácia para prevenção de AVC na FA<br/>não estabelecida"]
  P8["Considerar NOAC conforme protocolo de FA,<br/>função renal e interações"]
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
  D4 -->|"Não"| D4A
  D4A -->|"Sim"| P6
  D4A -->|"Não"| D4B
  D4B -->|"Sim"| P7
  D4B -->|"Não"| P8
  P5 --> D5
  P6 --> D5
  P7 --> D5
  P8 --> D5
  D5 -->|"Sim"| C1
  D5 -->|"Não"| C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

FA em paciente em BTK exige três perguntas simultâneas: **está instável? precisa controle de ritmo/frequência? pode anticoagular com segurança?** O CHA2DS2-VASc pode subestimar o risco trombótico no câncer; por outro lado, plaquetopenia, tumor gastrointestinal/geniturinário, absorção e interações impedem automatizar a escolha do anticoagulante. FA atribuída a fator transitório deve ter a necessidade de anticoagulação reavaliada após três meses. FA ou risco de FA, isoladamente, não contraindicam o tratamento antineoplásico: manutenção, pausa ou troca do BTK dependem de decisão multidisciplinar.
