---
title: "Fluxograma: Prolongamento de QT por ribociclibe e risco de torsades"
slug: fluxograma-prolongamento-qt-por-ribociclibe-e-risco-de-torsades
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de emergência para paciente oncológico em ribociclibe com QTcF prolongado, síncope ou arritmia ventricular, incorporando interrupção do fármaco, correção de fatores reversíveis e transição imediata para protocolo de torsades quando presente."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al.; ESC Scientific Document Group. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "U.S. National Library of Medicine. DailyMed: KISQALI (ribociclib) Prescribing Information, Table 4 — Dose Modification and Management for QT Prolongation. SPL version 28, effective 2026-07-01. Set ID aaeaef94-f3f5-4367-8ea2-b181d7be2da8.", "Hortobagyi GN, Stemmer SM, Burris HA, et al. Ribociclib as First-Line Therapy for HR-Positive, Advanced Breast Cancer. N Engl J Med. 2016;375(18):1738-1748. DOI: 10.1056/NEJMoa1609709. PMID: 27717303."]
review_note: "Revisado em 26/08/2026 contra a Tabela 4 da rotulagem regulatória DailyMed de KISQALI, SPL versão 28, efetiva em 01/07/2026, e a diretriz ESC 2022 de cardio-oncologia (PMID 36017568). Corrigido o ramo QTcF >480 e <=500 ms, antes genérico: após a primeira ocorrência, doença inicial permite retomada na mesma dose, enquanto doença avançada/metastática exige o próximo nível inferior; recorrência >480 ms exige interrupção e retomada no próximo nível inferior em ambas. Mantidos os critérios distintos de recorrência >500 ms e de descontinuação permanente associada a torsades, TV polimórfica, síncope ou arritmia grave. Pendente revisão médica independente antes de uso assistencial."
---

# QT prolongado por ribociclibe — emergência

```mermaid
flowchart TD
  R0["Paciente em ribociclibe com QTcF prolongado,<br/>palpitação, síncope, pré-síncope ou arritmia"]
  P1["ECG imediato com QTcF (Fridericia) +<br/>K/Mg/Ca + função renal/hepática +<br/>revisão de outros fármacos que prolongam QT"]
  D1{"TdP, TV polimórfica, instabilidade<br/>ou parada cardíaca?"}
  C1(["Sim: interromper ribociclibe imediatamente<br/>e seguir protocolo de torsades/TV/PCR;<br/>corrigir eletrólitos e retirar co-agressores"])
  D2{"QTcF >500 ms?"}
  P2["Sim: interromper KISQALI até QTcF ≤480 ms;<br/>se recuperar, rotulagem prevê retomada em dose menor;<br/>se >500 ms recidivar, descontinuar"]
  D3{"QTcF >480 e ≤500 ms?"}
  P3["Interromper até QTcF ≤480 ms.<br/>1º evento: doença inicial retoma mesma dose;<br/>avançada/metastática retoma nível inferior.<br/>Se recorrente: nível inferior em ambas"]
  C2(["QTcF ≤480 ms sem arritmia grave:<br/>procurar causa alternativa dos sintomas e<br/>seguir monitorização oncológica/cardiológica"])
  D4{"QTcF >500 ms OU aumento >60 ms do basal<br/>E houve TdP, TV polimórfica, síncope ou<br/>sinal/sintoma de arritmia grave?"}
  C3(["Sim: descontinuar KISQALI permanentemente<br/>conforme rotulagem FDA"])
  C4(["Não: aplicar retomada/redução de P2/P3;<br/>ECG mais frequente após o evento"])
  C5(["Após estabilização: cardio-oncologia + oncologia;<br/>evitar combinação com novos fármacos QT-prolongadores<br/>e corrigir eletrólitos antes da reexposição"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| P3
  D3 -->|"Não"| C2
  C1 --> D4
  P2 --> D4
  P3 --> D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| C4
  C2 --> C5
  C3 --> C5
  C4 --> C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Regras regulatórias verificadas

- **QTcF >480 e ≤500 ms:** interromper ribociclibe até QTcF ≤480 ms. Na primeira ocorrência, retomar na mesma dose se doença inicial e no próximo nível inferior se doença avançada/metastática. Se >480 ms recorrer, interromper novamente e retomar no próximo nível inferior em ambas as indicações.
- **QTcF >500 ms:** interromper até QTcF ≤480 ms e, quando a retomada for permitida, reduzir para o próximo nível de dose; se QTcF >500 ms recidivar, descontinuar.
- **Descontinuação permanente:** QTcF >500 ms ou aumento >60 ms do basal associado a torsades de pointes, TV polimórfica, síncope ou sinais/sintomas de arritmia grave.
- **Monitorização regulatória:** ECG antes de iniciar, aproximadamente no dia 14 do primeiro ciclo e conforme indicação clínica; após qualquer prolongamento do QTcF, aumentar a frequência dos ECGs.

## Segurança

A emergência elétrica tem prioridade sobre a decisão oncológica de dose. Se houver torsades/TV polimórfica, o paciente migra imediatamente para o protocolo específico de **torsades de pointes e QT longo adquirido** já existente no Modo Emergência.
