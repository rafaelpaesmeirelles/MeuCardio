---
slug: fluxograma-sinalizadores-ambulatoriais-varfarina
title: 'Fluxograma: sinalizadores ambulatoriais de varfarina — PS agora vs. retorno precoce'
kind: fluxograma
theme: Farmacologia
summary: 'Árvore ambulatorial: triagem de sangramento maior/crítico vs. menor/nuisance e ramo de INR elevado sem
  sangramento em paciente em AVK; encaminhamento imediato ao PS ou manejo ambulatorial com retorno precoce — sem
  doses de varfarina/vitamina K.'
tags: []
source_refs:
- 'Witt DM, Nieuwlaat R, Clark NP, et al. American Society of Hematology 2018 guidelines for management of venous
  thromboembolism: optimal management of anticoagulation therapy. Blood Adv. 2018;2(22):3257-3291. DOI: 10.1182/bloodadvances.2018024893.
  PMID: 30482765'
- 'Holbrook A, Schulman S, Witt DM, et al. Evidence-based management of anticoagulant therapy: Antithrombotic Therapy
  and Prevention of Thrombosis, 9th ed: American College of Chest Physicians Evidence-Based Clinical Practice Guidelines.
  Chest. 2012;141(2 Suppl):e152S-e184S. DOI: 10.1378/chest.11-2295. PMID: 22315259'
- 'Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed
  in collaboration with EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723'
- 'NICE NG232, Head injury: assessment and early management. Recomendações 1.2.4 e 1.5.13. https://www.nice.org.uk/guidance/ng232/chapter/recommendations'
- 'Corpus MeuCardio: sinalizadores-ambulatoriais-varfarina-inr-sangramento-quando-encaminhar.md; inr-elevado-sem-sangramento-no-consultorio-conduta-ambulatorial.md;
  fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial.md.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma: sinalizadores ambulatoriais de varfarina

Prosa: [sinalizadores-ambulatoriais-varfarina-inr-sangramento-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-varfarina-inr-sangramento-quando-encaminhar). Braço INR sem sangramento: [inr-elevado-sem-sangramento-no-consultorio-conduta-ambulatorial](/biblioteca/inr-elevado-sem-sangramento-no-consultorio-conduta-ambulatorial). Reversão aguda: [fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial](/biblioteca/fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial:<br/>paciente em AVK/varfarina com<br/>sangramento e/ou INR fora da faixa"] --> D1{"Há sinal de sangramento maior,<br/>sítio crítico ou instabilidade?<br/>(ICH, hipotensão, hematêmese/melena,<br/>trauma craniano recente, etc.)"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Não tentar reversão no consultório<br/>Seguir fluxograma de sangramento maior"])

  D1 -->|"Não"| D2{"Qual é o problema principal?"}

  D2 -->|"Sangramento trivial/nuisance<br/>(controlável localmente)"| P1["Medidas locais + educação<br/>Revisar precipitantes<br/>(antibiótico, amiodarona, AINE,<br/>álcool, dieta, adesão)"]
  P1 --> C2(["Retorno ambulatorial precoce<br/>Não inventar pausa longa sem prescritor<br/>Orientação escrita dos alarmes"])

  D2 -->|"Persistente ou clinicamente relevante, sem maior"| CR["Avaliar presencialmente no mesmo dia;<br/>controle local, INR e hemograma conforme quadro;<br/>hospital se controle ou acesso inviável"]

  D2 -->|"INR elevado sem sangramento<br/>clinicamente relevante"| P2["Ver protocolo de INR por faixa:<br/>não extrapolar pausa a qualquer elevação;<br/>INR acima de 10 exige decisão no mesmo dia"]
  P2 --> D3{"INR acima de 10, fragilidade,<br/>sem reavaliação laboratorial em horas,<br/>ou alto risco trombótico + dúvida?"}
  D3 -->|"Sim"| C3(["Limiar baixo para PS / observação<br/>com suporte; contato com prescritor"])
  D3 -->|"Não — acesso a re-INR garantido"| C4(["Re-INR precoce + retorno<br/>Retomada só com o prescritor<br/>Documentar precipitantes"])

  C2 --> D4{"Acesso e suporte adequados?<br/>Fragilidade/isolamento contemplados no plano?"}
  D4 -->|"Não / suporte insuficiente"| C5(["Garantir avaliação no mesmo dia<br/>ou PS se novos alarmes"])
  D4 -->|"Sim"| C6(["Manter plano + retorno precoce"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C3,C5 alerta;
  class C2,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (ASH 2018: reversão agressiva para sangramento ameaçador à vida).
- **D2** = separa sangramento menor de INR outlier assintomático — condutas diferentes.
- **D3** = logística/fragilidade/extremidade do INR muda o destino.
- A árvore **não** decide miligramas de varfarina, vitamina K, CCP nem meta de INR por indicação.
