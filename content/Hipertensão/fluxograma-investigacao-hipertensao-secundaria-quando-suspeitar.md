---
title: "Fluxograma: Investigação de Hipertensão Secundária — Quando Suspeitar e Por Onde Começar"
slug: fluxograma-investigacao-hipertensao-secundaria-quando-suspeitar
theme: "Hipertensão"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Nenhum dos 4 fluxogramas já publicados nesta pasta (crise adrenérgica do feocromocitoma, emergência hipertensiva por síndrome-alvo, caminho ESC 2024 de diagnóstico/alvo, hipertensão resistente/quarta droga) cobre o momento anterior a todos eles: quando, diante de um hipertenso, vale a pena suspeitar de causa secundária e por qual pista clínica começar a investigação. Este documento fecha essa lacuna. Fonte estrutural principal — Charles L, Triscott J, Dobbs B. Secondary Hypertension: Discovering the Underlying Cause. Am Fam Physician. 2017;96(7):453-461. PMID: 29094913 — verificada nesta sessão via PubMed esummary (título, periódico, data, autores, volume/fascículo/páginas conferidos linha a linha, todos batendo). O DOI da 2024 ESC Guidelines for the management of elevated blood pressure and hypertension (Eur Heart J. 2024) foi conferido nesta sessão via Crossref (10.1093/eurheartj/ehae178, título e data de publicação batendo) — citada aqui só como contexto de diretriz vigente sobre a mesma população, sem extração de texto integral (bloqueado por 403 no Oxford Academic, mesma barreira já documentada exaustivamente neste repositório). O terceiro PMID (41069544, Acta Endocrinol (Bucur) 2024, perspectiva do cardiologista sobre estenose de artéria renal e hiperaldosteronismo primário como causas mais comuns em jovens) foi verificado por esummary e efetch de abstract nesta sessão e usado só para corroborar o ramo de doença renovascular. Os cortes/exames confirmatórios específicos de hiperaldosteronismo primário e feocromocitoma NÃO foram reescritos aqui — o documento aponta para os dois protocolos já publicados e revisados nesta mesma pasta (`aldosteronismo-primario-e-feocromocitoma-testes-confirmatorios-endocrine-society.md` e `emergencia-hipertensiva-e-triagem-de-hipertensao-secundaria.md`), para não duplicar conteúdo já verificado."
source_refs: ["Charles L, Triscott J, Dobbs B. Secondary Hypertension: Discovering the Underlying Cause. Am Fam Physician. 2017;96(7):453-461. PMID: 29094913 — revisão que organiza os indicadores de alarme (idade de início, gravidade, resistência ao tratamento) e a tabela de pistas clínicas por causa secundária (hipopotassemia/hiperaldosteronismo, apneia do sono, feocromocitoma, coartação de aorta, síndrome de Cushing, disfunção tireoidiana, estenose de artéria renal) usada como esqueleto desta árvore de decisão", "2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178 — diretriz vigente sobre a mesma população hipertensa, citada como contexto; DOI conferido nesta sessão via Crossref (título e data batendo), sem extração de texto integral por bloqueio de acesso (Oxford Academic, 403)", "Darabont RO. Current insights in the screening of secondary hypertension: a cardiologist's perspective. Acta Endocrinol (Bucur). 2024;20(4):[online]. PMID: 41069544 — revisão que reforça a estenose de artéria renal e o hiperaldosteronismo primário como as causas secundárias mais comuns em adultos jovens, usada para corroborar o ramo de doença renovascular"]
---

# Fluxograma: Investigação de Hipertensão Secundária — Quando Suspeitar e Por Onde Começar

Nem todo hipertenso precisa investigar causa secundária, e a diferença não está no valor da pressão isoladamente — está em um pequeno conjunto de indicadores de alarme (idade de início, velocidade de instalação, gravidade e resposta ao tratamento). Uma vez presente pelo menos um desses indicadores, o passo seguinte não é pedir "todos os exames": é deixar a anamnese e o exame físico apontarem qual causa é mais provável, porque cada pista clínica leva a um exame de triagem diferente. Este fluxograma organiza essa primeira bifurcação — que este acervo ainda não tinha em formato de árvore de decisão — e entrega, no fim de cada ramo, o exame inicial certo para aquela suspeita, sem repetir os protocolos de teste confirmatório que já estão publicados nesta mesma pasta para hiperaldosteronismo primário e feocromocitoma.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com diagnóstico de hipertensão arterial,<br/>em avaliação inicial ou em seguimento"] --> P1["Avaliar clinicamente a presença de indicadores<br/>de alarme para causa secundária"]

  P1 --> D1{"Presente pelo menos um destes indicadores?<br/>Início antes da puberdade · idade menor que 30 anos,<br/>sem obesidade, sem história familiar de hipertensão<br/>e não afrodescendente · elevação abrupta da PA em<br/>paciente previamente estável e controlado · hipertensão<br/>maligna/acelerada com lesão aguda de órgão-alvo ·<br/>PAS maior que 180 ou PAD maior que 120mmHg ·<br/>hipertensão resistente (PA não controlada com 3<br/>fármacos em dose adequada, incluindo diurético)"}

  D1 -->|"Nenhum indicador presente"| C1(["Hipertensão primária (essencial) provável:<br/>não investigar causa secundária de rotina;<br/>seguir diagnóstico e meta pressórica da diretriz<br/>vigente (ESC 2024/SBC), com reavaliação periódica"])

  D1 -->|"Pelo menos um indicador presente"| P2["Anamnese e exame físico dirigidos à pesquisa de<br/>sinais e sintomas de causa secundária específica"]

  P2 --> D2{"Qual achado clínico predomina<br/>na anamnese/exame?"}

  D2 -->|"Hipopotassemia espontânea<br/>ou induzida por diurético"| P3["Solicitar relação aldosterona-renina, coletada pela<br/>manhã, com o paciente em pé há pelo menos 2 horas"]
  P3 --> C2(["Suspeita de hiperaldosteronismo primário:<br/>prosseguir com teste confirmatório (infusão salina,<br/>fludrocortisona, captopril ou sobrecarga oral de<br/>sódio) conforme o protocolo já publicado nesta<br/>biblioteca (testes confirmatórios, Endocrine Society)"])

  D2 -->|"Sonolência diurna, ronco alto<br/>ou apneias testemunhadas"| P4["Solicitar polissonografia, ou triagem inicial por<br/>oximetria/escala clínica validada"]
  P4 --> C3(["Suspeita de apneia obstrutiva do sono:<br/>confirmar por polissonografia e tratar com CPAP<br/>antes de escalonar o esquema anti-hipertensivo"])

  D2 -->|"Flushing, cefaleia episódica,<br/>palpitação, sudorese ou síncope"| P5["Solicitar metanefrinas fracionadas — plasmáticas<br/>livres ou urinárias de 24 horas"]
  P5 --> C4(["Suspeita de feocromocitoma/paraganglioma:<br/>prosseguir com teste confirmatório específico já<br/>publicado nesta biblioteca (Endocrine Society) antes<br/>de qualquer manipulação do tumor ou cirurgia"])

  D2 -->|"Diferença de PA braço-perna maior que<br/>20mmHg, ou pulsos femorais diminuídos/ausentes"| P6["Solicitar ecocardiograma transtorácico (se criança/<br/>adolescente) ou angioTC/angioRM de aorta (adulto)"]
  P6 --> C5(["Suspeita de coartação de aorta: confirmar<br/>por exame de imagem e encaminhar para<br/>avaliação de correção (percutânea ou cirúrgica)"])

  D2 -->|"Hábito cushingoide: fácies em lua,<br/>estrias violáceas, obesidade central, giba dorsal"| P7["Solicitar cortisol urinário livre de 24 horas,<br/>supressão com dexametasona em dose baixa,<br/>ou cortisol salivar noturno"]
  P7 --> C6(["Suspeita de síndrome de Cushing:<br/>prosseguir com investigação endocrinológica<br/>dedicada para confirmar e localizar a causa"])

  D2 -->|"Bradicardia/taquicardia, intolerância ao<br/>calor/frio, obstipação/diarreia ou outro sinal<br/>sugestivo de disfunção tireoidiana"| P8["Solicitar TSH"]
  P8 --> C7(["Disfunção tireoidiana como causa contribuinte<br/>da hipertensão: tratar a disfunção de base<br/>e reavaliar a pressão arterial depois"])

  D2 -->|"Aumento de creatinina 50% ou mais após início<br/>de IECA/BRA, sopro abdominal, ou hipertensão<br/>resistente/de início súbito em mulher jovem"| P9["Solicitar ultrassonografia com Doppler,<br/>angioTC ou angioRM de artérias renais"]
  P9 --> C8(["Suspeita de estenose de artéria renal<br/>(aterosclerótica ou displasia fibromuscular):<br/>confirmar por imagem e decidir revascularização<br/>conforme etiologia, idade e comorbidades"])

  D2 -->|"Nenhuma pista clínica específica identificada,<br/>apesar do indicador de alarme presente"| C9(["Investigação inicial ampla sem alvo clínico definido:<br/>função renal, eletrólitos, TSH, relação aldosterona-<br/>renina e exame de imagem renal; encaminhar a centro<br/>de referência em hipertensão se tudo vier negativo<br/>e o indicador de alarme persistir"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## Por que a triagem começa pela pista clínica, não por um painel de exames

Pedir aldosterona/renina, metanefrinas, cortisol, TSH e imagem renal para todo hipertenso com um indicador de alarme multiplica falso-positivo sem aumentar o rendimento diagnóstico — cada teste tem melhor desempenho quando pedido a partir de uma probabilidade pré-teste real, construída pela clínica. É esse o papel da anamnese e do exame físico dirigidos (nó `P2`): eles não substituem o exame confirmatório, mas decidem qual exame de triagem pedir primeiro.

## O que este fluxograma não substitui

Os testes confirmatórios de hiperaldosteronismo primário (relação aldosterona-renina anormal) e de feocromocitoma (metanefrinas elevadas) — cortes exatos, condições de coleta e algoritmo de confirmação — estão no documento `aldosteronismo-primario-e-feocromocitoma-testes-confirmatorios-endocrine-society.md`, já publicado nesta pasta. A prevalência de cada causa secundária por faixa etária e a comparação entre nicardipina e labetalol na emergência hipertensiva estão em `emergencia-hipertensiva-e-triagem-de-hipertensao-secundaria.md`. Este fluxograma é o elo que faltava entre os dois: o momento de decisão, em consultório, de que pista seguir primeiro.
