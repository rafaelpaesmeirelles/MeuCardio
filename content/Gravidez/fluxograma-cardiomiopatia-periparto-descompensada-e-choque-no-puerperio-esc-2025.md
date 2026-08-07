---
title: "Fluxograma: cardiomiopatia periparto descompensada e choque no puerpério — ESC 2025"
slug: fluxograma-cardiomiopatia-periparto-descompensada-e-choque-no-puerperio-esc-2025
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de decisão para dispneia/IC aguda no fim da gestação ou puerpério, com exclusão de diagnósticos concorrentes, avaliação de choque e encaminhamento para suporte avançado."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025. DOI: 10.1093/eurheartj/ehaf193."]
---

# Cardiomiopatia periparto descompensada e choque no puerpério

```mermaid
flowchart TD
  R0["Final da gestação ou puerpério com<br/>dispneia importante, ortopneia, edema pulmonar,<br/>baixo débito, síncope ou arritmia"]
  P1["Monitorização + ECG + oximetria;<br/>eco urgente; biomarcadores;<br/>avaliar TEP, SCAD/SCA, pré-eclâmpsia/eclâmpsia,<br/>sepse, hemorragia e valvopatia aguda"]
  D1{"Há choque/hipoperfusão, hipoxemia refratária<br/>ou arritmia ventricular instável?"}
  C1(["UTI/centro terciário; tratar IC/choque e arritmia;<br/>acionar Pregnancy Heart Team;<br/>considerar precocemente suporte circulatório mecânico<br/>se refratária, como ponte para recuperação/decisão"])
  D2{"Ecocardiograma mostra nova disfunção de VE<br/>compatível com PPCM e sem outra causa evidente?"}
  C2(["Tratar IC aguda conforme perfil hemodinâmico<br/>e segurança na gestação/lactação;<br/>monitorizar resposta e complicações tromboembólicas"])
  C3(["Direcionar tratamento ao diagnóstico alternativo<br/>identificado — não rotular PPCM por exclusão incompleta"])
  D3{"Bromocriptina será considerada como adjuvante?"}
  C4(["Se bromocriptina: considerar ao menos LMWH profilática;<br/>não usar como substituto da estabilização de IC"])
  C5(["Seguir terapia de IC e reavaliação seriada;<br/>planejar seguimento pós-parto e recuperação ventricular"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| C3
  C2 --> D3
  D3 -->|"Sim"| C4
  D3 -->|"Não"| C5
  C4 --> C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Segurança

O objetivo do fluxograma é reconhecer rapidamente a paciente que precisa de suporte avançado e, ao mesmo tempo, evitar o erro de atribuir toda insuficiência cardíaca do puerpério à PPCM sem excluir TEP, SCAD/SCA, doença hipertensiva grave e sepse.
