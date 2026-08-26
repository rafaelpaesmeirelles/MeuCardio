---
title: "Fluxograma: síndrome coronariana aguda na gestação e puerpério"
slug: fluxograma-sindrome-coronariana-aguda-na-gestacao-e-puerperio
theme: "Gravidez"
kind: fluxograma
summary: "Atendimento da SCA na gestante ou puérpera: preserva angiografia/PCI conforme risco, posiciona fibrinólise apenas antes da angiografia quando PCI oportuna não existe e encaminha SCAD para estratégia própria."
review_status: revisado
review_note: "Reescrito em 26/08/2026 contra as seções 5.2.2 e 12.2 da ESC 2025. Corrigida incoerência temporal: fibrinólise deixou de aparecer depois de angiografia/decisão de stent e passou a ser alternativa antes da angiografia, somente quando reperfusão é urgente e PCI oportuna não está disponível. Acrescentada a alta prevalência de SCAD como motivo para avaliação especializada antes de trombólise, ticagrelor contraindicado por embriotoxicidade e intervalo mínimo de 5 dias sem clopidogrel antes de anestesia neuraxial."
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294. Seções 5.2.2 e 12.2."]
---

# SCA na gestação ou puerpério

Gestação não reduz a indicação de reperfusão. ECG, troponina e ecocardiograma
seguem a lógica habitual; elevação de troponina representa lesão miocárdica e
supradesnivelamento de ST não é alteração fisiológica da gravidez. Em paralelo,
considerar TEP, síndrome aórtica, cardiomiopatia periparto e pré-eclâmpsia.

## Árvore de decisão

```mermaid
flowchart TD
  A["Gestante/puérpera com dor torácica,<br/>dispneia, instabilidade ou suspeita de SCA"]
  B["ECG + troponina + TTE conforme apresentação;<br/>monitorização e Pregnancy Heart Team;<br/>não atribuir alteração isquêmica à gestação"]
  C{"STEMI, instabilidade, isquemia<br/>ativa/recorrente ou SCA de alto/muito alto risco?"}
  D{"PCI pode ser realizada<br/>em tempo adequado?"}
  E["Angiografia imediata + PCI se indicada;<br/>minimizar radiação pelo princípio ALARA"]
  F{"PCI oportuna indisponível e<br/>reperfusão sistêmica ainda é necessária?"}
  G["Trombólise sistêmica pode ser alternativa;<br/>avaliar hemorragia obstétrica e possibilidade de SCAD<br/>com equipe experiente antes da decisão"]
  H["Transferência urgente para centro de PCI;<br/>não atrasar suporte nem administrar fibrinolítico<br/>automaticamente quando SCAD é provável"]
  I["Sem alto risco imediato: avaliação seriada;<br/>na NSTE-SCA confirmada/diagnóstico de trabalho<br/>com alta suspeita de angina instável, estratégia invasiva precoce"]
  J{"Angiografia realizada:<br/>há SCAD?"}
  K["Migrar para fluxo específico de SCAD;<br/>estável sem isquemia favorece manejo conservador"]
  L{"PCI com stent e<br/>DAPT indicada?"}
  M["AAS + clopidogrel pelo menor tempo apropriado;<br/>ticagrelor é contraindicado na gestação;<br/>planejar parto e anestesia neuraxial"]
  N["Tratamento conforme etiologia e risco;<br/>planejar parto/puerpério e prevenção secundária"]

  A --> B --> C
  C -->|"Sim"| D
  C -->|"Não"| I --> J
  D -->|"Sim"| E --> J
  D -->|"Não"| F
  F -->|"Sim, após avaliação"| G --> N
  F -->|"Não / SCAD provável"| H --> N
  J -->|"Sim"| K
  J -->|"Não"| L
  J -->|"Não realizada ainda"| N
  L -->|"Sim"| M --> N
  L -->|"Não"| N

  classDef action fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class E,G,H,I,K,M,N action;
```

## Reperfusão e SCAD

Indicações de angiografia e PCI são comparáveis às da paciente não gestante.
Em SCA de alto ou muito alto risco, a ESC recomenda angiografia imediata e PCI
quando indicada; a exposição deve ser reduzida pelo princípio ALARA, sem reter
um procedimento necessário.

Fibrinólise sistêmica pode ser alternativa quando PCI oportuna não está
disponível. Ela não atravessa a placenta em quantidade relevante, mas pode
causar sangramento, inclusive subplacentário. Como SCAD é a causa mais frequente
de SCA associada à gestação/puerpério e trombólise pode agravar dissecção ou
hematoma, essa alternativa exige avaliação do mecanismo e risco hemorrágico —
não um reflexo após “falha” de uma angiografia que já ocorreu.

## Antiagregação, parto e anestesia

Aspirina e clopidogrel são as bases quando DAPT é necessária; a ESC considera
clopidogrel seguro pelo menor tempo possível e contraindica ticagrelor na
gestação por embriotoxicidade. Prasugrel fica reservado a situações especiais,
como metabolização deficiente de clopidogrel, após decisão especializada.

O parto é planejado conforme condição materna e obstétrica. **Clopidogrel deve
ser suspenso por pelo menos 5 dias antes de anestesia neuraxial** para reduzir
risco de hematoma epidural. Isso não autoriza interromper precocemente DAPT após
stent sem comparar risco de trombose; cardiologia, obstetrícia e anestesia devem
definir o calendário em conjunto.

## Tudo com Tudo

- [SCA por SCAD na gestação e puerpério](fluxograma-sindrome-coronariana-aguda-por-scad-na-gestacao-e-puerperio-esc-2025.md)
- [Síndrome coronariana aguda — ESC 2023](../Doença_coronariana/fluxograma-sindrome-coronariana-aguda-esc-2023.md)
- [TEP agudo na gestação e puerpério](fluxograma-tromboembolismo-pulmonar-agudo-na-gestacao-e-puerperio-esc-2025.md)
- [Síndrome aórtica aguda na gestação e puerpério](fluxograma-sindrome-aortica-aguda-na-gestacao-e-puerperio.md)
- [Cardiomiopatia periparto descompensada](fluxograma-cardiomiopatia-periparto-descompensada-e-choque-no-puerperio-esc-2025.md)
- [Eclâmpsia e hipertensão grave](fluxograma-eclampsia-e-hipertensao-grave-na-gestacao.md)
