---
title: "Fluxograma: síndrome de diferenciação por gilteritinibe"
slug: fluxograma-sindrome-de-diferenciacao-por-gilteritinibe
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de emergência para síndrome de diferenciação por gilteritinibe, com dexametasona imediata, monitorização e interrupção do agente se quadro grave persistir."
review_status: revisado
review_note: "Revisado em 26/08/2026 contra a seção 5.1 da bula regulatória FDA de XOSPATA (gilteritinibe) e a diretriz ESC 2022 de cardio-oncologia (PMID 36017568). Corrigido o ramo que mandava 'reiniciar' gilteritinibe mesmo quando ele nunca havia sido interrompido. A interrupção ficou restrita a manifestações graves persistentes por mais de 48 horas após início de corticoide, e o reinício passou a ocorrer quando os sinais e sintomas deixam de ser graves, conforme a redação regulatória, sem inventar graduação formal. Dexametasona deve durar pelo menos três dias e só ser reduzida após resolução. Pendente revisão médica independente antes de uso assistencial."
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
  C4(["Não: manter gilteritinibe e monitorização;<br/>dexametasona por pelo menos 3 dias e<br/>reduzir apenas após resolução dos sintomas"])
  D3{"Após a interrupção, os sinais e<br/>sintomas deixaram de ser graves?"}
  C2(["Sim: reiniciar gilteritinibe após discussão<br/>com onco-hematologia; manter monitorização<br/>e completar o tratamento corticosteroide"])
  C3(["Não: manter gilteritinibe interrompido,<br/>suporte intensivo e investigação de<br/>diagnósticos concorrentes"])

  R0 --> P1
  P1 --> P2
  P2 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  C1 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| C4
  P3 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Regra prática

Síndrome de diferenciação pode coexistir com sepse e insuficiência cardíaca. **Trate primeiro o risco:** corticoide precoce, monitorização e investigação paralela.

O prazo de 48 horas não é uma espera para iniciar tratamento: dexametasona e
monitorização começam assim que a síndrome é suspeitada. Ele define quando a
persistência de manifestações graves passa a exigir a interrupção temporária do
gilteritinibe. Tamponamento, choque, hipoxemia e insuficiência renal recebem suporte
específico em paralelo ao corticoide.
