---
title: "Fluxograma: síndrome de diferenciação por gilteritinibe"
slug: fluxograma-sindrome-de-diferenciacao-por-gilteritinibe
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de emergência para síndrome de diferenciação por gilteritinibe, com dexametasona imediata, monitorização e interrupção do agente se quadro grave persistir."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "XOSPATA (gilteritinib) US Prescribing Information, FDA label 211349s003, Section 5.1."]
---

# Síndrome de diferenciação por gilteritinibe

```mermaid
flowchart TD
  R0["Paciente em gilteritinibe + febre,<br/>dispneia, edema, derrame, hipotensão<br/>ou disfunção renal"]
  P1["Suspeitar síndrome de diferenciação;<br/>investigar sepse/IC/TEP/tamponamento em paralelo"]
  P2["Dexametasona 10 mg IV 12/12 h<br/>+ monitorização hemodinâmica"]
  D1{"Tamponamento ou outra<br/>emergência mecânica?"}
  C1(["Sim: tratar imediatamente<br/>ex.: pericardiocentese"])
  D2{"Manifestações graves persistem<br/>>48 h após corticoide?"}
  P3["Sim: interromper gilteritinibe"]
  P4["Não: manter tratamento e<br/>monitorização; corticoide ≥3 dias"]
  D3{"Melhora para grau 2<br/>ou menor?"}
  C2(["Sim: discutir reinício do gilteritinibe<br/>com onco-hematologia"])
  C3(["Não: manter suporte/intensificar<br/>investigação de diagnósticos concorrentes"])

  R0 --> P1
  P1 --> P2
  P2 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  C1 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| P4
  P3 --> D3
  P4 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

Síndrome de diferenciação pode coexistir com sepse e insuficiência cardíaca. **Trate primeiro o risco:** corticoide precoce, monitorização e investigação paralela.