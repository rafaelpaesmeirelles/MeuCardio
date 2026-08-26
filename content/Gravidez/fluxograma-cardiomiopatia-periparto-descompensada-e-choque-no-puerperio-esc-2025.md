---
title: "Fluxograma: cardiomiopatia periparto descompensada e choque no puerpério — ESC 2025"
slug: fluxograma-cardiomiopatia-periparto-descompensada-e-choque-no-puerperio-esc-2025
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de decisão para dispneia/IC aguda no fim da gestação ou puerpério, com exclusão de diagnósticos concorrentes, avaliação de choque e encaminhamento para suporte avançado."
review_status: revisado
review_note: "Revisão de 26/08/2026 contra as seções 7.3–7.4 e 12.6.2 da ESC 2025. Separadas terapia durante a gestação e terapia pós-parto/lactação; acrescentados inotrópicos e VA-ECMO do ramo de choque sem publicar dose; explicitado que adrenalina deve ser evitada no choque cardiogênico. Bromocriptina deixou de ser pergunta genérica para toda PPCM e passou ao fenótipo moderado/grave, com interrupção da lactação e HBPM ao menos profilática. O ramo de choque agora retorna à confirmação etiológica após estabilização."
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294. Seções 7.3–7.4 e 12.6.2."]
---

# Cardiomiopatia periparto descompensada e choque no puerpério

```mermaid
flowchart TD
  R0["Final da gestação ou puerpério com<br/>dispneia importante, ortopneia, edema pulmonar,<br/>baixo débito, síncope ou arritmia"]
  P1["Monitorização + ECG + oximetria;<br/>eco urgente; biomarcadores;<br/>avaliar TEP, SCAD/SCA, pré-eclâmpsia/eclâmpsia,<br/>sepse, hemorragia e valvopatia aguda"]
  D1{"Há choque/hipoperfusão, hipoxemia refratária<br/>ou arritmia ventricular instável?"}
  C1(["UTI/centro terciário com cirurgia/MCS; definir fenótipo;<br/>se cardiogênico: dobutamina, levosimendana ou milrinona;<br/>evitar adrenalina; considerar VA-ECMO<br/>se choque cardiogênico grave refratário"])
  D2{"Ecocardiograma mostra nova disfunção de VE<br/>compatível com PPCM e sem outra causa evidente?"}
  D4{"Gestação em curso<br/>ou pós-parto?"}
  C2(["Gestação: diurético cauteloso se houver congestão,<br/>beta-1 seletivo, hidralazina/nitrato conforme perfil;<br/>não usar IECA/BRA/ARNI/MRA/ivabradina/iSGLT2/atenolol"])
  C6(["Pós-parto: iniciar terapia completa de IC<br/>ajustada à lactação; se houver amamentação, evitar BRA/iSGLT2;<br/>espironolactona é considerada segura pela ESC"])
  C3(["Direcionar tratamento ao diagnóstico alternativo<br/>identificado — não rotular PPCM por exclusão incompleta"])
  D3{"PPCM moderada/grave e bromocriptina<br/>será considerada como adjuvante?"}
  C4(["Discutir interrupção da lactação e nutrição do lactente;<br/>se bromocriptina, considerar ao menos HBPM profilática;<br/>não substituir a estabilização de IC"])
  C5(["Seguir terapia de IC e reavaliação seriada;<br/>planejar seguimento pós-parto e recuperação ventricular"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  C1 --> D2
  D2 -->|"Não"| C3
  D2 -->|"Sim"| D4
  D4 -->|"Gestação"| C2
  D4 -->|"Pós-parto"| C6
  C2 --> D3
  C6 --> D3
  D3 -->|"Sim"| C4
  D3 -->|"Não"| C5
  C4 --> C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Segurança

O objetivo do fluxograma é reconhecer rapidamente a paciente que precisa de suporte avançado e, ao mesmo tempo, evitar o erro de atribuir toda insuficiência cardíaca do puerpério à PPCM sem excluir TEP, SCAD/SCA, doença hipertensiva grave e sepse.

Na gestação, IECA, BRA, ARNI, antagonista mineralocorticoide, ivabradina e iSGLT2
são contraindicados por risco fetal. No pós-parto, o tratamento pode ser ampliado
de acordo com lactação; a ESC orienta evitar BRA e iSGLT2 quando amamentar for
necessário e considera espironolactona segura. A lista não substitui conferência
individual de compatibilidade do fármaco com lactação.

Em choque cardiogênico, a ESC cita dobutamina e levosimendana, com milrinona como
alternativa quando benefício superar o risco; levosimendana é usada sem bólus.
Adrenalina deve ser evitada. VA-ECMO é o suporte preferido a considerar no choque
grave refratário, em centro com experiência. Se a paciente ainda está gestante,
o choque também exige decisão urgente sobre parto cesáreo pela equipe.

Bromocriptina pode ser considerada como adjuvante, especialmente na PPCM
moderada/grave. Ela interrompe lactação e não demonstrou superioridade clara do
regime prolongado sobre o curto no ensaio citado pela diretriz; por isso este
fluxo não escolhe dose/duração. Ao menos HBPM profilática deve ser considerada
para reduzir risco tromboembólico durante o uso.

## Tudo com Tudo

- [PPCM descompensada e choque — revisão clínica](cardiomiopatia-periparto-descompensada-e-choque-no-puerperio-esc-2025.md)
- [Critérios diagnósticos, recuperação e manejo da PPCM](../Cardiomiopatias/cardiomiopatia-periparto-criterios-diagnosticos-recuperacao-e-manejo.md)
- [Bromocriptina no tratamento da PPCM](bromocriptina-no-tratamento-da-cardiomiopatia-periparto.md)
- [Base genética e variantes truncantes de TTN](base-genetica-da-cardiomiopatia-periparto-variantes-truncantes-de-ttn.md)
- [Gestação subsequente após PPCM](gestacao-subsequente-apos-cardiomiopatia-periparto-risco-por-funcao-ventricular.md)
- [TEP agudo na gestação e puerpério](fluxograma-tromboembolismo-pulmonar-agudo-na-gestacao-e-puerperio-esc-2025.md)
- [Emergência hipertensiva obstétrica](fluxograma-eclampsia-e-hipertensao-grave-na-gestacao.md)
