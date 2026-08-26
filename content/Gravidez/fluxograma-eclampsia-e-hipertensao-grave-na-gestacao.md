---
title: "Fluxograma: eclâmpsia e hipertensão grave na gestação ou puerpério"
slug: fluxograma-eclampsia-e-hipertensao-grave-na-gestacao
theme: "Gravidez"
kind: fluxograma
summary: "Conduta imediata diante de convulsão ou hipertensão grave obstétrica: trata qualquer PAS ≥160 ou PAD ≥110 mmHg sustentada, usa magnésio na eclâmpsia e restringe profilaxia sem convulsão às indicações obstétricas, sem atrasar estabilização e planejamento do parto."
review_status: revisado
review_note: "Reescrito em 26/08/2026 contra a diretriz oficial NICE NG133 e o Magpie Trial. Corrigidos três riscos: o limiar passou de 'PA ≥160/110' para PAS ≥160 ou PAD ≥110 mmHg; magnésio deixou de ser automático em toda hipertensão grave sem convulsão; e o esquema secundário 4,5 g + 1,5 g/h foi substituído pelo Collaborative Eclampsia Trial regimen oficial (4 g em 5–15 min, depois 1 g/h). Retiradas doses de anti-hipertensivos copiadas de resumo secundário e metildopa como resgate imediato."
source_refs: ["National Institute for Health and Care Excellence. Hypertension in pregnancy: diagnosis and management. NICE guideline NG133. Publicada em 25/06/2019, atualizada em 17/04/2023. Recomendações 1.8.2–1.8.7 conferidas em 26/08/2026. https://www.nice.org.uk/guidance/ng133/chapter/recommendations", "Altman D, Carroli G, Duley L, Farrell B, Moodley J, et al; Magpie Trial Collaboration Group. Do women with pre-eclampsia, and their babies, benefit from magnesium sulphate? The Magpie Trial: a randomised placebo-controlled trial. Lancet. 2002;359(9321):1877-1890. DOI: 10.1016/S0140-6736(02)08778-0. PMID: 12057549."]
---

# Eclâmpsia e hipertensão grave na gestação ou puerpério

Convulsão durante gestação ou puerpério é eclâmpsia até avaliação rápida de
alternativas, sobretudo quando há hipertensão ou sinais de pré-eclâmpsia.
Hipertensão grave significa **PAS ≥160 mmHg ou PAD ≥110 mmHg** sustentada; não é
necessário que os dois componentes atinjam simultaneamente esses valores.

Acionar obstetrícia, anestesia e cuidado crítico, proteger via aérea, posicionar
com segurança, obter acesso venoso, monitorizar mãe e feto quando aplicável e
colher hemograma/plaquetas, função renal, transaminases e outros exames dirigidos.
Essas ações não devem atrasar magnésio na eclâmpsia nem o tratamento imediato da
pressão grave.

## Árvore de decisão

```mermaid
flowchart TD
  A["Gestante ou puérpera com convulsão<br/>e/ou PAS ≥160 ou PAD ≥110 mmHg sustentada"]
  B["ABCDE + prevenir trauma/aspiração;<br/>acesso IV, monitorização e equipe obstétrica;<br/>avaliar causas neurológicas/metabólicas em paralelo"]
  C{"Convulsão eclâmptica<br/>atual ou prévia?"}
  D["Sulfato de magnésio IV:<br/>4 g em 5–15 min, depois 1 g/h;<br/>continuar por 24 h após a última convulsão"]
  E{"Nova convulsão<br/>apesar do magnésio?"}
  F["Sulfato de magnésio adicional<br/>2–4 g IV em 5–15 min;<br/>reavaliar via aérea e diagnóstico"]
  G{"Sem convulsão: pré-eclâmpsia grave<br/>em cuidado crítico, com parto planejado<br/>nas próximas 24 h e sinais preocupantes?"}
  H["Considerar sulfato de magnésio IV<br/>com a equipe obstétrica; usar o mesmo<br/>esquema e monitorização institucional"]
  I["Não administrar magnésio automaticamente<br/>apenas pelo número da pressão;<br/>vigilância materno-fetal e decisão obstétrica"]
  J{"PAS ≥160 ou PAD ≥110 mmHg<br/>permanece sustentada?"}
  K["Tratar imediatamente com uma opção:<br/>labetalol VO/IV, nifedipino VO ou<br/>hidralazina IV, segundo protocolo e contraindicações"]
  L["Monitorar resposta e efeitos materno-fetais;<br/>modificar tratamento conforme resposta"]
  M["Planejar momento do parto conforme gravidade,<br/>idade gestacional, condição fetal e estabilização;<br/>não atrasar parto por deterioração materna/fetal"]

  A --> B --> C
  C -->|"Sim"| D --> E
  E -->|"Sim"| F --> J
  E -->|"Não"| J
  C -->|"Não"| G
  G -->|"Sim"| H --> J
  G -->|"Não"| I --> J
  J -->|"Sim"| K --> L --> M
  J -->|"Não"| M

  classDef action fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class D,F,H,I,K,L,M action;
```

## Quando considerar magnésio sem convulsão

Na pré-eclâmpsia grave em cuidado crítico, o NICE recomenda **considerar**
magnésio quando o parto está planejado nas próximas 24 horas. A decisão ganha
peso diante de cefaleia grave recorrente, escotomas, náuseas/vômitos, dor
epigástrica, oligúria com hipertensão grave ou deterioração progressiva de
creatinina, transaminases ou plaquetas. Isso não equivale a prescrever magnésio
para toda pessoa que apresenta isoladamente um valor pressórico grave.

O Magpie Trial sustenta o benefício preventivo do magnésio na pré-eclâmpsia,
mas não define sozinho qual paciente contemporânea deve receber o fármaco; a
seleção e o regime operacional vêm da diretriz. Diazepam, fenitoína e outros
anticonvulsivantes **não substituem** sulfato de magnésio na eclâmpsia.

## Segurança do sulfato de magnésio

Monitorizar frequência respiratória, reflexos, diurese, estado neurológico e
função renal segundo protocolo. O risco de acúmulo aumenta na disfunção renal;
ajustes, suspensão e manejo de toxicidade devem seguir prescrição obstétrica e
farmácia clínica. A dose adicional de 2–4 g vale para recorrência de convulsão,
não para repetição automática por persistência da hipertensão.

## Tratamento da pressão e parto

Na hipertensão grave em cuidado crítico durante gestação ou após o parto, o
NICE indica tratamento imediato com **labetalol oral ou IV, nifedipino oral ou
hidralazina IV**. A escolha considera acesso, contraindicações, frequência,
função cardíaca e protocolo obstétrico; nifedipino não deve ser administrado por
via sublingual. Este fluxo não reproduz escalonamentos de dose divergentes entre
protocolos.

Controlar a pressão e a convulsão estabiliza a mãe, mas não elimina a doença
placentária. Momento e via do parto dependem de idade gestacional, condição
materna/fetal e resposta; deterioração não deve ser mascarada por uma medida de
pressão temporariamente melhor.

## Tudo com Tudo

- [Doença cardiovascular e gravidez — ESC 2025](fluxograma-doenca-cardiovascular-e-gravidez-esc-2025.md)
- [Emergência hipertensiva](../Hipertensão/fluxograma-emergencia-hipertensiva.md)
- [Cardiomiopatia periparto descompensada e choque](fluxograma-cardiomiopatia-periparto-descompensada-e-choque-no-puerperio-esc-2025.md)
- [Síndrome coronariana aguda na gestação e puerpério](fluxograma-sindrome-coronariana-aguda-na-gestacao-e-puerperio.md)
- [Síndrome aórtica aguda na gestação e puerpério](fluxograma-sindrome-aortica-aguda-na-gestacao-e-puerperio.md)
- [Sulfato de magnésio em cardiologia](../Farmacologia/sulfato-de-magnesio-em-cardiologia-torsades-de-pointes-e-adjuvante-no-controle-de-frequencia-da-fa.md)
