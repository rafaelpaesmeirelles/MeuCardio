---
title: "Escores ABC na Fibrilação Atrial: Risco de AVC e de Sangramento por Biomarcadores"
slug: escores-abc-na-fibrilacao-atrial-risco-de-avc-e-de-sangramento-por-biomarcadores
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Hijazi Z, Lindbäck J, Alexander JH, Hanna M, Held C, Hylek EM, et al; ARISTOTLE and STABILITY Investigators. The ABC (age, biomarkers, clinical history) stroke risk score: a biomarker-based risk score for predicting stroke in atrial fibrillation. Eur Heart J. 2016;37(20):1582-1590. DOI: 10.1093/eurheartj/ehw054. PMID: 26920728 — NCT00412984 e NCT00799903", "Hijazi Z, Oldgren J, Lindbäck J, Alexander JH, Connolly SJ, Eikelboom JW, et al; ARISTOTLE and RE-LY Investigators. The novel biomarker-based ABC (age, biomarkers, clinical history)-bleeding risk score for patients with atrial fibrillation: a derivation and validation study. Lancet. 2016;387(10035):2302-2311. DOI: 10.1016/S0140-6736(16)00741-8. PMID: 27056738 — derivação em 14.537 pacientes do ARISTOTLE, validação externa em 8.468 do RE-LY"]
legacy_source: "Documento novo, escrito em 31/07/2026. O tema Calculadoras tinha CHA₂DS₂-VA, CHADS₂ e HAS-BLED — todos baseados só em variáveis clínicas. Faltavam os escores ABC, que acrescentam biomarcadores e superaram os clássicos em discriminação nos dois lados da balança da anticoagulação."
---

# Escores ABC na Fibrilação Atrial: Risco de AVC e de Sangramento por Biomarcadores

## A ideia comum aos dois escores
A decisão de anticoagular na fibrilação atrial equilibra **redução de AVC isquêmico** contra **aumento de sangramento maior**. Os escores clássicos — CHA₂DS₂-VASc de um lado, HAS-BLED do outro — usam apenas **variáveis clínicas**.

Os escores **ABC** acrescentam **biomarcadores** a essa conta, e o nome é o próprio conteúdo: **A**ge (idade), **B**iomarkers (biomarcadores), **C**linical history (história clínica). São dois escores distintos, um para cada lado da balança, derivados do mesmo programa de pesquisa.

## Abc-stroke — risco de avc
Hijazi Z et al., Eur Heart J. 2016;37(20):1582-1590 (PMID 26920728):
- Desenvolvido e validado internamente em **14.701 pacientes** com FA, seguimento mediano de **1,9 ano**; **validação externa em 1.400 pacientes**, seguimento mediano de 3,4 anos
- **Componentes**, em ordem de importância preditiva: **AVC ou AIT prévio**, **NT-proBNP**, **troponina cardíaca de alta sensibilidade** e **idade**

**Desempenho:** índice-c **maior que o do CHA₂DS₂-VASc** nas duas coortes — **0,68 vs. 0,62** na derivação (p<0,001) e **0,66 vs. 0,58** na validação externa (p<0,001), com vantagem consistente em subgrupos importantes.

## Abc-bleeding — risco de sangramento
Hijazi Z et al., Lancet. 2016;387(10035):2302-2311 (PMID 27056738):
- Derivado em **14.537 pacientes** do **ARISTOTLE** (apixabana vs. varfarina) e **validado externamente em 8.468** do **RE-LY** (dabigatrana vs. varfarina); sangramentos maiores adjudicados centralmente
- **Componentes**: **GDF-15** (fator de diferenciação de crescimento 15), **troponina cardíaca de alta sensibilidade**, **hemoglobina**, **idade** e **sangramento prévio**

**Desempenho:** índice-c superior ao do HAS-BLED **e** ao do ORBIT nas duas coortes:
- Derivação: **0,68** (IC95% 0,66-0,70) vs. **0,61** (HAS-BLED) vs. **0,65** (ORBIT) — p<0,0001 e p=0,0008
- Validação externa: **0,71** (IC95% 0,68-0,73) vs. **0,62** (HAS-BLED) vs. **0,68** (ORBIT)

## Estabilidade no tempo — uma preocupacao razoavel, medida
Escore que depende de biomarcador levanta a dúvida: **o valor de hoje serve para daqui a dois meses?** Isso foi testado.

Hijazi Z et al., J Am Heart Assoc. 2017;6(6):e004851 (PMID 28645934), em 4.796 pacientes do ARISTOTLE com amostras na entrada **e aos 2 meses**: as variações médias dos biomarcadores em 2 meses foram **pequenas** (mediana +2,8% para troponina T, +2,0% para troponina I, +13,5% para NT-proBNP), com **correlação intraindivíduo alta (todas ≥ 0,82)**. O **ABC-stroke aos 2 meses manteve índice-c de 0,70**, igual ao do basal, e seguiu bem calibrado.

## O limite pratico, que decide se o escore serve ao seu paciente
**Os escores ABC exigem dosar biomarcadores que não fazem parte da rotina** de avaliação da FA no Brasil:
- **NT-proBNP e troponina de alta sensibilidade** são acessíveis na maioria dos serviços
- **GDF-15**, componente do ABC-bleeding, **não é exame de rotina** e tem disponibilidade limitada — é o que mais restringe a aplicação desse escore na prática

**Além disso**, as coortes de derivação e validação vêm de **ensaios randomizados de anticoagulantes** (ARISTOTLE, RE-LY), ou seja, populações selecionadas por critérios de ensaio — mais homogêneas e com menos comorbidade extrema que a população geral com FA.

## Como isso se encaixa na decisao
- **A superioridade em índice-c é real e consistente**, mas a magnitude é modesta: 0,68 contra 0,62 continua sendo discriminação moderada em ambos
- **Os escores clínicos seguem sendo o padrão de trabalho** justamente por não exigirem exame adicional — ver `cha2ds2-va.md` e `has-bled.md`, nesta mesma pasta. Lembre que a ESC 2024 **deixou de recomendar escore de sangramento** para decidir início ou suspensão de anticoagulante, o que muda o papel de qualquer escore desse tipo, inclusive o ABC-bleeding
- **O ABC pode agregar quando a decisão está genuinamente em dúvida** e os biomarcadores já foram dosados por outro motivo
- **Nenhum dos dois substitui a decisão compartilhada** — são estimativas de risco, não indicações

## Armadilhas clinicas
- **Pedir GDF-15 de rotina** — não é exame de rotina e sua disponibilidade limita o ABC-bleeding no Brasil
- **Tratar a superioridade de índice-c como grande** — 0,68 vs. 0,62 é melhora real e modesta; ambos discriminam moderadamente
- **Usar o ABC-bleeding para decidir suspender anticoagulante** — a ESC 2024 recomenda **não** usar escore de sangramento com essa finalidade (Classe III), e isso vale para escore com biomarcador também
- **Extrapolar de população de ensaio para a população geral** — as coortes vêm do ARISTOTLE e do RE-LY
- **Confundir os dois escores** — ABC-stroke usa NT-proBNP, troponina, idade e AVC/AIT prévio; ABC-bleeding usa GDF-15, troponina, hemoglobina, idade e sangramento prévio
- **Repetir os biomarcadores com frequência esperando ganho** — a variabilidade em 2 meses é pequena e a remedição não acrescentou valor prognóstico para AVC
