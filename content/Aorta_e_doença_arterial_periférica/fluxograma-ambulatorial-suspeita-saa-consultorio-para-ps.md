---
slug: fluxograma-ambulatorial-suspeita-saa-consultorio-para-ps
title: 'Fluxograma ambulatorial: suspeita de SAA — consultório para PS imediato'
kind: fluxograma
theme: Aorta e doença arterial periférica
summary: 'Árvore de destino no consultório: SAA, AVC agudo, isquemia aguda de membro, AAA sintomático e síncope
  de alto risco recebem destinos emergenciais distintos; ramos crônicos permanecem ambulatoriais.'
tags: []
source_refs:
- 'Mazzolai L, Teixido-Tura G, Lanzi S, et al. 2024 ESC Guidelines for peripheral arterial and aortic diseases.
  PMID: 39210722'
- 'Rogers AM, Hermann LK, Booher AM, et al. Aortic dissection detection risk score. PMID: 21555704'
- 'Nazerian P, Mueller C, Soeiro AM, et al. ADvISED. PMID: 29030346'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: suspeita de SAA — consultório → PS

```mermaid
flowchart TD
  R0["Consulta: dor tórax/dorso/abdome,<br/>síncope ou déficit de perfusão"] --> D1{"Suspeita de SAA?<br/>dor de alto risco e/ou contexto aórtico<br/>ou exame/malperfusão compatíveis"}

  D1 -->|"Sim/dúvida fundamentada"| C1(["PS IMEDIATO<br/>Comunicar suspeita de SAA<br/>Não aguardar D-dímero/TC eletiva"])

  D1 -->|"Não"| D2{"Déficit neurológico focal<br/>súbito ou ainda presente?"}
  D2 -->|"Sim"| C2(["Ativar via AVC AGUDO agora<br/>Avaliação carotídea eletiva só depois"])

  D2 -->|"Não"| D3{"Membro com início súbito:<br/>frio/pálido/sem pulso/dormente/fraco?"}
  D3 -->|"Sim"| C3(["Isquemia AGUDA de membro<br/>emergência vascular"])

  D3 -->|"Não"| D4{"AAA conhecido + nova dor abd/lombar<br/>ou massa pulsátil dolorosa/sensibilidade à palpação?"}
  D4 -->|"Sim"| C4(["PS / emergência vascular<br/>suspeita AAA sintomático/rotura contida"])

  D4 -->|"Não"| D5{"Síncope de alto risco?<br/>esforço/decúbito, palpitação abrupta,<br/>cardiopatia estrutural relevante ou instabilidade?"}
  D5 -->|"Sim"| C5(["Avaliação urgente / PS<br/>seguir fluxo de síncope de alto risco"])

  D5 -->|"Não"| D6{"CLTI crônica sem deterioração aguda?"}
  D6 -->|"Sim"| C6(["Avaliação vascular urgente de CLTI<br/>Não fila eletiva de claudicação"])

  D6 -->|"Não"| D7{"Suspeita de SCA ou angina em instabilização?"}
  D7 -->|"Sim"| C7(["Fluxo SCA / avaliação emergencial<br/>PS imediato"])
  D7 -->|"Não"| C8(["Investigação ambulatorial dirigida<br/>Reabrir gate se surgirem alarmes"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C7 alerta;
  class C6,C8 conduta;
```

## Links canônicos

- [fluxograma-sindrome-aortica-aguda-esc-2024](/biblioteca/fluxograma-sindrome-aortica-aguda-esc-2024)
- [fluxograma-dor-membro-claudicacao-clti-isquemia-aguda](/biblioteca/fluxograma-dor-membro-claudicacao-clti-isquemia-aguda)
- [fluxograma-aneurisma-de-aorta-abdominal-seguimento-e-indicacao-de-reparo](/biblioteca/fluxograma-aneurisma-de-aorta-abdominal-seguimento-e-indicacao-de-reparo)

ADD-RS + D-dímero pertence ao ambiente de emergência; este fluxo só decide **destino**.

SAA pode ocorrer sem predisposição conhecida e, raramente, sem dor: o conjunto clínico prevalece sobre a pontuação. Na suspeita concomitante de dissecção e AVC, comunicar ambos imediatamente à equipe de emergência para avaliação coordenada antes de terapias que possam agravar a dissecção. CLTI requer avaliação vascular urgente mesmo quando crônica; deterioração aguda muda o destino para emergência.

- [AVC agudo](/biblioteca/fluxograma-suspeita-de-avc-agudo-primeira-hora).
