---
title: "Fluxograma: sinalizadores ambulatoriais de intolerância a estatina — PS vs. reexposição vs. especialista"
slug: fluxograma-sinalizadores-ambulatoriais-intolerancia-estatina
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de SAMS: emergência apenas com rabdomiólise/lesão sistêmica, CK elevada sem emergência, reexposição estruturada e encaminhamento neuromuscular se CK persistir."
review_status: revisado
review_note: "Revisão clínica final 08/09/2026. Corrigidos: CK >10x LSN deixou de ir automaticamente à emergência; gate inicial inclui lesão renal/sistêmica; persistência de CK foi conectada após suspensão nos ramos apropriados; StatinWISE incluído explicitamente nas fontes."
source_refs:
  - "Stroes ES, Thompson PD, Corsini A, et al. EAS Consensus Panel Statement on statin-associated muscle symptoms. Eur Heart J. 2015;36(17):1012-1022. PMID: 25694464"
  - "Mach F, Baigent C, Catapano AL, et al. 2019 ESC/EAS Guidelines for dyslipidaemias. Eur Heart J. 2020;41(1):111-188. PMID: 31504418"
  - "Newman CB, Preiss D, Tobert JA, et al. Statin Safety and Associated Adverse Events. Arterioscler Thromb Vasc Biol. 2019;39(2):e38-e81. PMID: 30580575"
  - "Herrett E, Williamson E, Brack K, et al. StatinWISE Trial Group. Statin treatment and muscle symptoms: series of randomised, placebo controlled n-of-1 trials. BMJ. 2021;372:n135. PMID: 33627334"
---

# Fluxograma: sinalizadores ambulatoriais de intolerância a estatina

```mermaid
flowchart TD
  R0["Sintoma muscular em usuário de estatina"] --> D1{"Sinais de rabdomiólise/gravidade?<br/>fraqueza grave · urina escura · oligúria/anúria<br/>IRA/creatinina subindo · hipercalemia<br/>confusão/desidratação importante"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Suspender estatina<br/>Sem doses neste fluxo"])
  D1 -->|"Não"| D2{"CK disponível?"}

  D2 -->|"Não"| C2(["Solicitar CK; creatinina/eletrólitos se indicados<br/>Educar alarmes<br/>Não rotular intolerante ainda"])
  D2 -->|"Sim"| D3{"CK >10x LSN?"}

  D3 -->|"Sim"| S1["Suspender estatina<br/>Revisar exercício/causas secundárias<br/>Avaliar função renal/urina/eletrólitos"]
  S1 --> D3B{"Há repercussão clínica/renal<br/>ou suspeita de rabdomiólise?"}
  D3B -->|"Sim"| C1
  D3B -->|"Não"| F1["Acompanhar CK e evolução"]

  D3 -->|"Não"| D4{"CK 4–10x LSN?"}
  D4 -->|"Sim"| S2["Conduta conforme risco CV e sintomas<br/>seguir EAS; suspensão/monitorização conforme caso"]
  S2 --> F1

  D4 -->|"Não (CK <4x/normal)"| D5{"SAMS estruturado por dechallenge/rechallenge?"}
  D5 -->|"Ainda não"| C5(["Dechallenge-rechallenge estruturado<br/>Não abandonar a classe"])
  D5 -->|"Sim"| C6(["Máxima terapia tolerada + não-estatínicos<br/>Manter meta de LDL"])

  F1 --> D6{"CK permanece elevada após suspensão<br/>e causas secundárias foram tratadas/excluídas?"}
  D6 -->|"Sim"| C7(["Avaliação neuromuscular<br/>Considerar anti-HMGCR/outra miopatia"])
  D6 -->|"Não / em queda"| C8(["Seguir reavaliação/reexposição<br/>quando clinicamente apropriado"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1 alerta;
  class C2,C5,C6,C7,C8 conduta;
```

## Notas

- CK >10x LSN é um **gate para suspender e investigar**, não um diagnóstico isolado de rabdomiólise.
- Emergência depende de contexto clínico/renal/sistêmico.
- CK persistente após retirada e exclusão de causas secundárias alimenta o ramo neuromuscular.
- StatinWISE apoia reavaliação/reexposição em sintomas sem toxicidade grave; não prova que todo SAMS seja nocebo.
