---
idioma: pt-BR
kind: documento
published: true
review_note: Revisão integral do recorte ESC 2025, tabelas visuais 12/13/20, Figura
  22 e AHA 2025/CHAP. Confirmado AAS prevenção I A e dose distinta de SCA. Fluxos
  sem convergência e sem estádio intermediário; choque inclui pré-viabilidade e suporte
  em paralelo. SCAD estável não implica ICP, BP alvo não aplicado ao choque, gestante
  138/88 sem HAS não inicia fármaco automaticamente.
review_status: revisado
slug: choque-cardiogenico-na-gestante-esc-2025
source_refs:
- De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management
  of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI
  10.1093/eurheartj/ehaf193. PMID 40878294.
- ESC. Essential Messages from the 2025 ESC Guidelines for the management of cardiovascular
  disease and pregnancy (PDF da ESC, adaptado de ehaf193).
- ESC. Official Slide Set, 2025 ESC Guidelines for the management of cardiovascular
  disease and pregnancy. Figure 22.
- ESC gravidez 2025, tabelas 12, 13 e 20 e Figuras 11/22 conferidas. https://academic.oup.com/eurheartj/article/46/43/4462/8234487
theme: Terapia intensiva
title: Choque cardiogênico na gestante — porta UTI, ESC 2025
---

# Choque cardiogênico na gestante — porta UTI, ESC 2025

Esta ficha entra pela **porta da terapia intensiva**. A fonte é a mesma da porta Gravidez (De Backer, Haugaa et al., *Eur Heart J*. 2025;**46**:4462-4568; DOI 10.1093/eurheartj/ehaf193; PMID **40878294**), mas a pergunta muda: o que o intensivista faz quando a gestante — ou a puérpera — chega em choque cardiogênico. Equipe mWHO 2.0 e fluxograma de dor torácica não se repetem. IC aguda/choque pela porta obstétrica: [ESC 2025: insuficiência cardíaca aguda e choque na gestação](/biblioteca/esc-2025-ic-aguda-e-choque-na-gestacao).

## A regra da ameaça à vida

Mensagem essencial da ESC 2025: em situação ameaçadora da vida, desfibrilação, intervenções, revascularização coronária aguda, **suporte circulatório mecânico** e medicação devem ser **os mesmos da mulher não grávida**, sem retardar tratamento salvador por contraindicações relativas à gestação, com avaliação materno-fetal e adaptação da técnica. A gravidez muda a equipe ao redor (obstetrícia, neonatologia, *Pregnancy Heart Team* em paralelo). Não muda o princípio de perfundir o miocárdio e a placenta.

IC aguda pede **internação urgente**. O texto da seção pede centro com IC avançada, cirurgia no local e suporte mecânico — ou transplante — de retaguarda. *Essential Messages*: quando inotrópico ou tratamento avançado for necessário, **encaminhar a centro especialista**.

## Inotrópico na UTI — o que tem Classe

**Inotrópicos e/ou vasopressores são recomendados** na gestante com choque cardiogênico, com **levosimendana, dobutamina e milrinona** como agentes recomendados — **Classe I, nível C**. Confirmado na tabela de recomendação, nos slides oficiais e no *Supplementary data* (Recommendation Table 20).

Como usar, no texto da seção — **sem Classe isolada para cada detalhe de infusão**:

- **Levosimendana:** infusão contínua **sem dose de ataque**.
- **Dobutamina:** opção.
- **Adrenalina:** evitar.
- **Milrinona:** alternativa se o benefício superar o risco de atravessar a placenta.

**Não inventar µg/kg/min, bolus nem diluição.** Isso sai do capítulo, da bula e do protocolo local — não desta ficha.

A Figura 22 (IC aguda e choque na gravidez e até 6 meses pós-parto) coloca no ramo grave: otimizar pré-carga; **nitratos se PAS >110 mmHg**; otimização de oxigenação na hipoxemia, com suporte ventilatório conforme insuficiência respiratória; depois inotrópico/vasopressor (Classe I na figura). O 110 mmHg é limiar para nitrato, não meta de PAM no choque.

## Dois tempos que a UTI não pode atrasar

1. **Cesárea urgente** na gestante em choque, tão logo o feto seja viável, considerando idade gestacional, comorbidades e o nível de cuidado disponível — **I C**. Choque não herda a frase “parto vaginal é a primeira escolha na maioria das DCV” (I B no estável).
2. **Transferência precoce** para serviço que ofereça suporte circulatório mecânico **deve ser considerada** — **IIa C**. Narrativa da seção: no choque grave refratário, preferir ECMO-VA. Não transformar essa preferência em Classe I nem improvisar marca de cânula.

Depois do parto: otimizar a terapia de IC, respeitando o que a lactação contra-indica — **I C**. Prevenir lactação **pode ser considerado** na IC grave — **IIb B**. IECA, BRA, ARNI, ARM, ivabradina e iSGLT2 permanecem **III C** na gravidez; o choque **não** autoriza “segurar” esses fármacos no útero. Bromocriptina é recorte de PPCM **já parida** (IIb na figura) — não é o primeiro vasoativo da admissão.

## Pressão na mesma internação

Alvo da gestante na ESC 2025: PAS **<140** e PAD **<90 mmHg** — **I B**. Emergência hipertensiva gestacional (PAS ≥160 ou PAD ≥110): hospital — **I C**. Redução aguda: labetalol i.v., urapidil, nicardipino, nifedipino oral de ação curta ou metildopa; hidralazina i.v. segunda linha — **I C**. Sem miligrama aqui. Não aplicar a meta 130/80 da AHA 2025 da adulta não grávida a esta paciente.

```mermaid
flowchart TD
 R["Gestante ou puérpera com IC aguda: internação e equipe especializada"] --> D{"Choque cardiogênico?"}
 D -->|Não| C0(["Tratar congestão e causa; suporte respiratório conforme necessidade e terapia compatível com gestação ou lactação"])
 D -->|Sim| P["Estabilizar perfusão e oxigenação; vasoativo I C e acionar suporte mecânico em paralelo"]
 P --> G{"Situação obstétrica?"}
 G -->|Grávida com feto viável| C1(["Cesárea urgente I C com equipe obstétrica e neonatal; considerar transferência precoce IIa C"])
 G -->|Grávida antes da viabilidade| C2(["Priorizar estabilização materna e decisão obstétrica individualizada; suporte mecânico conforme necessidade"])
 G -->|Pós-parto| C3(["Tratar choque e causa; otimizar terapia de IC considerando lactação e suporte mecânico se refratário"])
 classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
 class C0,C1,C2,C3 conduta;
```

## O que a UTI não faz nesta ficha

Não calcula mWHO na sala de choque. Não fecha “ansiedade da gravidez” se a porta de entrada foi dor torácica — isso é outra árvore. Não inventa classe para noradrenalina, vasopressina ou milrinona “em primeiro”. Não copia tabela de SCA/DAPT.

## Tudo com Tudo

- **Terapia intensiva.** Esta porta: vasoativo, via aérea, transferência, MCS.
- **Gravidez.** [ESC 2025: insuficiência cardíaca aguda e choque na gestação](/biblioteca/esc-2025-ic-aguda-e-choque-na-gestacao); equipe/mWHO 2.0 no documento-irmão.
- **Insuficiência cardíaca.** III C dos fármacos de IC crônica na gravidez; I C do inotrópico no choque. Não misturar as duas tabelas.
- **Doença coronariana.** SCA/SCAD como na não gestante (I C).
- **Hipertensão.** <140/90 (I B); crise ≥160/110 (I C).
- **Comunicação clínica.** A cesárea I C e a transferência IIa C precisam de frase única entre UTI, obstetrícia e a mulher (ou a família).
- **Tromboembolismo.** TEP continua no diagnóstico diferencial da instabilidade; HBPM é o agente de escolha na gravidez (*Essential Messages*).

## Limite editorial

PMID **40878294**. Inotrópicos no choque gestacional: **I C**. Doses: **não inventadas**. ECMO-VA: narrativa da seção. Noradrenalina/vasopressina como vasoativo de primeira linha nesta população: **não extraído** — omitido, sem inventar Classe.
O alvo <140/90 é do tratamento da hipertensão, não uma meta de redução pressórica no choque. A escolha de suporte vasoativo depende de perfusão, pressão e mecanismo; os inotrópicos listados não são vasopressores equivalentes. Evitar adrenalina aqui se refere ao choque com circulação presente, não ao protocolo de parada cardíaca. Acionar centro com suporte mecânico em paralelo à estabilização e à decisão obstétrica, sem aguardar o parto ou falha prolongada.
