---
title: "Fluxograma: sinalizadores ambulatoriais de sangramento em DOAC — PS agora vs. retorno precoce"
slug: fluxograma-sinalizadores-ambulatoriais-doac-sangramento
theme: "Farmacologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: triagem de sangramento maior/crítico vs. menor/nuisance em paciente em DOAC; encaminhamento imediato ao PS ou suporte local com retorno precoce — sem doses de reversão."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar (07/09/2026). EHRA 2021 PMID 33895845; ESC AF 2024 PMID 39210723. Sem antídotos/doses."
source_refs:
  - "Steffel J, Collins R, Antz M, et al. 2021 European Heart Rhythm Association Practical Guide on the Use of Non-Vitamin K Antagonist Oral Anticoagulants in Patients with Atrial Fibrillation. Europace. 2021;23(10):1612-1676. DOI: 10.1093/europace/euab065. PMID: 33895845"
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723"
  - "Corpus MeuCardio: sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar.md; sangramento-menor-doac-no-consultorio-conduta-ambulatorial.md; fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial.md."
---

# Fluxograma: sinalizadores ambulatoriais de sangramento em DOAC

Prosa: [`sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar`](sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar.md). Braço menor: [`sangramento-menor-doac-no-consultorio-conduta-ambulatorial`](sangramento-menor-doac-no-consultorio-conduta-ambulatorial.md). Reversão aguda: [`fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial`](fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial:<br/>paciente em DOAC com sangramento<br/>ou equimose/epistaxe/gengivorragia"] --> D1{"Há sinal de sangramento maior,<br/>sítio crítico ou instabilidade?<br/>(ICH, hipotensão, hematêmese/melena,<br/>trauma craniano sintomático, etc.)"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Não tentar reversão no consultório<br/>Seguir fluxograma de sangramento maior"])

  D1 -->|"Não — parece menor/nuisance"| D2{"Sangramento controlado<br/>com medidas locais?"}

  D2 -->|"Não / persiste / recorrente"| C2(["Limiar baixo para PS<br/>ou observação com suporte;<br/>não liberar sem plano escrito"])

  D2 -->|"Sim"| P1["Medidas locais + educação:<br/>não pular dose sem consulta (EHRA)<br/>revisar AINE/HAS/álcool/interacoes/rim"]
  P1 --> C3(["Retorno ambulatorial precoce<br/>(horas a poucos dias conforme risco)<br/>Orientação escrita dos sinais de alarme"])

  C3 --> D3{"Acesso a retorno e suporte garantidos?<br/>Fragilidade / isolamento?"}
  D3 -->|"Não / alto risco residual"| C4(["Antecipar reavaliação 24–72 h<br/>ou encaminhar se novos alarmes"])
  D3 -->|"Sim"| C5(["Manter plano + retorno precoce<br/>Documentar precipitantes abordados"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2,C4 alerta;
  class C3,C5 conduta;
```

## Notas

- **D1** = gate de segurança (EHRA 2021: tipo de sangramento).
- **D2** = controle local — se falha, não insistir no consultório.
- **D3** = logística/fragilidade muda o prazo do retorno.
- A árvore **não** decide antídoto, CCP, dose ou quantas tomadas pausar.
