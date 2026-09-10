---
slug: fluxograma-sinalizadores-ambulatoriais-intolerancia-estatina
title: 'Fluxograma: sinalizadores ambulatoriais de intolerância a estatina — PS vs. reexposição vs. especialista'
kind: fluxograma
theme: Prevenção e lipídios
summary: 'Árvore ambulatorial de SAMS: emergência apenas com rabdomiólise/lesão sistêmica, CK elevada sem emergência,
  reexposição estruturada e encaminhamento neuromuscular se CK persistir.'
tags: []
source_refs:
- 'Cheeley MK, et al. NLA scientific statement on statin intolerance. J Clin Lipidol. 2022. DOI: 10.1016/j.jacl.2022.05.068'
- '2025 Focused Update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2025;46:4359–4378.
  DOI: 10.1093/eurheartj/ehaf190. PMID: 40878289'
- 'Stroes ES, Thompson PD, Corsini A, et al. EAS Consensus Panel Statement on statin-associated muscle symptoms.
  Eur Heart J. 2015;36(17):1012-1022. PMID: 25694464'
- 'Mach F, Baigent C, Catapano AL, et al. 2019 ESC/EAS Guidelines for dyslipidaemias. Eur Heart J. 2020;41(1):111-188.
  PMID: 31504418'
- 'Newman CB, Preiss D, Tobert JA, et al. Statin Safety and Associated Adverse Events. Arterioscler Thromb Vasc
  Biol. 2019;39(2):e38-e81. PMID: 30580575'
- 'Herrett E, Williamson E, Brack K, et al. StatinWISE Trial Group. Statin treatment and muscle symptoms: series
  of randomised, placebo controlled n-of-1 trials. BMJ. 2021;372:n135. PMID: 33627334'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma: sinalizadores ambulatoriais de intolerância a estatina

```mermaid
flowchart TD
  R0["Sintoma muscular em usuário de estatina"] --> D1{"Sinais de rabdomiólise/gravidade?<br/>fraqueza aguda grave/piora rápida · urina escura · oligúria/anúria<br/>IRA/creatinina subindo · hipercalemia<br/>confusão/desidratação importante"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Suspender estatina<br/>Sem doses neste fluxo"])
  D1 -->|"Não"| D2{"CK disponível?"}

  D2 -->|"Não"| C2(["Solicitar CK; creatinina/eletrólitos se indicados<br/>Educar alarmes<br/>Aguardar CK antes de reexposição"])
  D2 -->|"Sim"| D3{"CK ≥10x LSN?"}

  D3 -->|"Sim"| S1["Suspender estatina<br/>Revisar exercício/causas secundárias<br/>Avaliar função renal/urina/eletrólitos"]
  S1 --> D3B{"Há repercussão clínica/renal<br/>ou suspeita de rabdomiólise?"}
  D3B -->|"Sim"| C1
  D3B -->|"Não"| F1["Acompanhar CK e evolução"]

  D3 -->|"Não"| D4{"CK 4 a <10x LSN?"}
  D4 -->|"Sim"| S2["Individualizar por sintomas, tendência da CK,<br/>função renal, causas secundárias e risco CV<br/>Suspender se piora ou CK ≥10x"]
  S2 --> F1

  D4 -->|"Não (CK <4x/normal)"| D5{"SAMS estruturado por dechallenge/rechallenge?"}
  D5 -->|"Ainda não"| C5(["Dechallenge-rechallenge estruturado<br/>Não abandonar a classe"])
  D5 -->|"Sim"| C6(["Máxima terapia tolerada + não-estatínicos<br/>Manter meta de LDL"])

  F1 --> D6{"CK permanece elevada após suspensão<br/>e causas secundárias foram tratadas/excluídas?"}
  D6 -->|"Sim"| C7(["Avaliação neuromuscular<br/>Considerar anti-HMGCR/outra miopatia<br/>Sem reexposição até esclarecimento"])
  D6 -->|"Não: normalizou e sintomas resolveram"| D7{"Rabdomiólise ou miopatia imune suspeita?"}
  D7 -->|"Sim"| C7
  D7 -->|"Não"| C8(["Reavaliar reexposição supervisionada"])
  D6 -->|"CK em queda, ainda elevada"| F1

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1 alerta;
  class C2,C5,C6,C7,C8 conduta;
```

## Notas

- CK ≥10x LSN é um **gate para suspender e investigar**, não um diagnóstico isolado de rabdomiólise.
- Emergência depende de contexto clínico/renal/sistêmico.
- CK persistente após retirada e exclusão de causas secundárias alimenta o ramo neuromuscular.
- StatinWISE apoia reavaliação/reexposição em sintomas sem toxicidade grave; não prova que todo SAMS seja nocebo.

## Segurança da reexposição e prevenção

CK ≥10x LSN impede reexposição enquanto ativa. Após esse episódio, considerar nova tentativa apenas quando CK normalizar, sintomas resolverem e causas secundárias forem corrigidas, com supervisão e monitorização. CK apenas em queda não libera nova tentativa. Suspeita de rabdomiólise impede reintrodução; suspeita de miopatia necrosante imunomediada requer avaliação especializada, mantendo a estatina suspensa. Se a investigação rápida não estiver disponível ou ocorrer deterioração, encaminhar à urgência.

Com CK entre 4 e <10x LSN, a decisão considera sintomas, tendência da CK, função renal, causas secundárias e risco cardiovascular. Continuação em alto risco só com monitorização próxima e sem toxicidade progressiva; suspender se houver piora ou CK atingir 10x LSN.

A NLA 2022 distingue intolerância parcial de completa e exige tentativa de pelo menos duas estatinas, uma na menor dose diária aprovada, quando seguro; esse critério não obriga reexposição após toxicidade grave. A atualização ESC/EAS 2025 recomenda alternativas não estatínicas com benefício cardiovascular comprovado quando estatinas não puderem ser usadas.

[Protocolo canônico de reexposição](/biblioteca/intolerancia-a-estatina-definicao-operacional-e-protocolo-de-reexposicao-eas-2015).
