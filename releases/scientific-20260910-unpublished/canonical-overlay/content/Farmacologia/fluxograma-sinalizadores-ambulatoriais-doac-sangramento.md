---
slug: fluxograma-sinalizadores-ambulatoriais-doac-sangramento
title: 'Fluxograma: sinalizadores ambulatoriais de sangramento em DOAC — PS agora vs. retorno precoce'
kind: fluxograma
theme: Farmacologia
summary: 'Árvore ambulatorial: triagem de sangramento maior/crítico vs. menor/nuisance em paciente em DOAC; encaminhamento
  imediato ao PS ou suporte local com retorno precoce — sem doses de reversão.'
tags: []
source_refs:
- 'Tomaselli GF et al. 2020 ACC Expert Consensus Decision Pathway on Management of Bleeding in Patients on Oral
  Anticoagulants. JACC. DOI: 10.1016/j.jacc.2020.04.053.'
- 'NICE NG232. Head injury: assessment and early management. 2023. https://www.nice.org.uk/guidance/ng232/chapter/recommendations'
- 'Steffel J, Collins R, Antz M, et al. 2021 European Heart Rhythm Association Practical Guide on the Use of Non-Vitamin
  K Antagonist Oral Anticoagulants in Patients with Atrial Fibrillation. Europace. 2021;23(10):1612-1676. DOI: 10.1093/europace/euab065.
  PMID: 33895845'
- 'Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed
  in collaboration with EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723'
- 'Corpus MeuCardio: sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar.md; sangramento-menor-doac-no-consultorio-conduta-ambulatorial.md;
  fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial.md.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma: sinalizadores ambulatoriais de sangramento em DOAC

Prosa: [`sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar`](/biblioteca/sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar). Braço menor: [`sangramento-menor-doac-no-consultorio-conduta-ambulatorial`](/biblioteca/sangramento-menor-doac-no-consultorio-conduta-ambulatorial). Reversão aguda: [`fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial`](/biblioteca/fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial:<br/>paciente em DOAC com sangramento<br/>ou equimose/epistaxe/gengivorragia"] --> D1{"Há sinal de sangramento maior,<br/>sítio crítico ou instabilidade?<br/>(ICH, hipotensão, hematêmese/melena,<br/>trauma craniano recente mesmo sem sintomas, etc.)"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Não tentar reversão no consultório<br/>Seguir fluxograma de sangramento maior"])

  D1 -->|"Sem critérios de maior"| D2{"Sangramento controlado<br/>com medidas locais?"}

  D2 -->|"Não / relevante ou recorrente"| C2(["Avaliar CRNM: fonte, hemograma e exposição<br/>Decisão clínica individual sobre pausa<br/>Urgência se maior ou acesso inseguro"])

  D2 -->|"Sim"| P1["Medidas locais + educação:<br/>conferir fármaco, esquema e última dose<br/>hemograma e função renal/hepática se indicados"]
  P1 --> C3(["Retorno ambulatorial precoce<br/>(horas a poucos dias conforme risco)<br/>Orientação escrita dos sinais de alarme"])

  C3 --> D3{"Acesso a retorno e suporte garantidos?<br/>Fragilidade / isolamento?"}
  D3 -->|"Não / alto risco residual"| C4(["Garantir avaliação em prazo seguro<br/>Urgência se acesso insuficiente ou novos alarmes"])
  D3 -->|"Sim"| C5(["Manter plano + retorno precoce<br/>Documentar precipitantes abordados"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2,C4 alerta;
  class C3,C5 conduta;
```

## Notas

Sangramento maior inclui sítio crítico, instabilidade, queda de Hb ≥2 g/dL ou transfusão ≥2 unidades. Nuisance controlado e CRNM não recebem a mesma decisão de continuidade. Trauma craniano em anticoagulado requer avaliação urgente mesmo sem sintomas; indicação de imagem segue NG232 e contexto clínico.


- **D1** = gate de segurança (EHRA 2021: tipo de sangramento).
- **D2** = controle local — se falha, não insistir no consultório.
- **D3** = logística/fragilidade muda o prazo do retorno.
- A árvore **não** decide antídoto, CCP, dose ou quantas tomadas pausar.
