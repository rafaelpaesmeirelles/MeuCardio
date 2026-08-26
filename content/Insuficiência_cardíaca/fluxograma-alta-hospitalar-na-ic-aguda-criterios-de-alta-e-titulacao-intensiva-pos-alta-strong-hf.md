---
title: "Fluxograma: Alta hospitalar na insuficiência cardíaca aguda — critérios de alta e titulação intensiva pós-alta (ESC 2023, STRONG-HF)"
slug: fluxograma-alta-hospitalar-na-ic-aguda-criterios-de-alta-e-titulacao-intensiva-pos-alta-strong-hf
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "Do momento da alta por IC aguda às primeiras seis semanas: confirmar euvolemia e terapia oral iniciada com PA, potássio e creatinina estáveis; escolher entre a estratégia intensiva do STRONG-HF, com metade da dose-alvo na alta e visitas nas semanas 1, 2, 3 e 6, e o cuidado habitual com consulta em 1 a 2 semanas; e o que fazer quando um indicador de segurança aparece na visita."
review_status: revisado
review_note: "Produção científica assistida (Claude) e revisão editorial e científica independente (Codex), concluídas em 26/08/2026. Fontes primárias, coerência clínica, lógica dos fluxos, metadados e links foram conferidos; correções incorporadas. Publicação sujeita à aprovação do responsável técnico."
source_refs:
  - "McDonagh TA, Metra M, Adamo M, et al. 2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666. https://academic.oup.com/eurheartj/article/44/37/3627/7246292"
  - "2023 Focused Update of ESC Guidelines for Acute and Chronic HF: Key Points. American College of Cardiology, 2023. https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2023/08/29/14/58/2023-focused-update-esc-guidelines-hf-esc-2023"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368 — recomendações pré-alta e de consulta em 1 a 2 semanas conferidas em: 2021 ESC Guidelines for Acute and Chronic Heart Failure: Key Points. American College of Cardiology, 2021. https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2021/08/29/18/05/2021-ESC-Guidelines-for-HF-ESC-2021"
  - "Mebazaa A, Davison B, Chioncel O, et al. Safety, tolerability and efficacy of up-titration of guideline-directed medical therapies for acute heart failure (STRONG-HF): a multinational, open-label, randomised, trial. Lancet. 2022;400(10367):1938-1952. DOI: 10.1016/S0140-6736(22)02076-1. PMID: 36356631 — resumo indexado lido via https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=36356631&rettype=abstract&retmode=text"
  - "Tomasoni D, Davison B, Adamo M, et al. Safety Indicators in Patients Receiving High-intensity Care After Hospital Admission for Acute Heart Failure: The STRONG-HF Trial. J Card Fail. 2024;30(4):525-537. DOI: 10.1016/j.cardfail.2023.09.002. PMID: 37820896 — resumo indexado lido via E-utilities do PubMed"
  - "Kimmoun A, Cotter G, Davison B, et al. Safety, tolerability and efficacy of rapid optimization, helped by NT-proBNP and GDF-15, of heart failure therapies (STRONG-HF): rationale and design for a multicentre, randomized, parallel-group study. Eur J Heart Fail. 2019;21(11):1459-1467. DOI: 10.1002/ejhf.1575. PMID: 31423712 — resumo indexado lido via E-utilities do PubMed"
  - "STRONG-HF. ClinicalTrials.gov NCT03412201 — critérios de inclusão e exclusão e descrição dos braços conferidos em https://clinicaltrials.gov/study/NCT03412201"
  - "Derivado de safety-tolerability-and-efficacy-of-up-titration-of-guideline-directed-medical-therapies-for-acute-heart-failure-strong-hf.md e de atualizacao-focada-2023-das-diretrizes-esc-2021-de-insuficiencia-cardiaca.md, já publicados no acervo (Insuficiência cardíaca)."
---

# Fluxograma: Alta hospitalar na insuficiência cardíaca aguda — critérios de alta e titulação intensiva pós-alta (ESC 2023, STRONG-HF)

O fluxograma da IC aguda descompensada, nesta pasta, termina quando a congestão foi resolvida; o de sequenciamento da terapia quádrupla decide em que ordem os pilares entram quando há barreira de segurança. Este começa no ponto entre os dois: o momento em que se decide **se o paciente pode ir embora e com que plano**. A ESC 2021 já dava classe I, nível C, para três atos que costumam ser pulados — excluir congestão residual antes da alta, testar a terapia oral ainda internado e rever o paciente em 1 a 2 semanas. A atualização focada de 2023 acrescentou, com base no STRONG-HF, uma recomendação classe I nível B: estratégia intensiva de início e titulação rápida da terapia baseada em evidência antes da alta e em visitas frequentes e cuidadosas nas primeiras 6 semanas, para reduzir reinternação por IC ou morte. No ensaio, o desfecho primário de reinternação por IC ou morte por qualquer causa em 180 dias caiu de 23,3% para 15,2%. A decisão que este fluxograma organiza é quem recebe essa estratégia, o que precisa estar pronto antes da alta e o que fazer quando uma visita mostra um indicador de segurança.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente internado por IC aguda,<br/>congestão em resolução,<br/>planejamento da alta"]
  D1{"Euvolêmico ao exame,<br/>sem sinal de congestão residual?"}
  C1(["Não dar alta: manter descongestão<br/>e reavaliação diária de peso, exame,<br/>função renal e eletrólitos<br/>ver fluxograma da IC aguda descompensada"])
  D2{"Terapia oral baseada em evidência<br/>iniciada e tolerada, com PA, potássio<br/>e creatinina estáveis?"}
  C2(["Iniciar ou ajustar a terapia oral<br/>ainda internado, corrigir potássio<br/>e função renal e só então rediscutir a alta<br/>ver fluxograma de sequenciamento"])
  D3{"Candidato à estratégia intensiva<br/>tipo STRONG-HF: NT-proBNP elevado,<br/>hemodinamicamente estável, sem indicador<br/>de segurança presente e capaz de<br/>comparecer às visitas semanais?"}
  C3(["Alta com cuidado habitual reforçado:<br/>consulta em 1 a 2 semanas para congestão,<br/>tolerância e titulação em ritmo<br/>individualizado, educação e reconciliação<br/>medicamentosa"])
  P1["Alta com pelo menos metade da dose-alvo<br/>de IECA, BRA ou ARNI, betabloqueador e ARM,<br/>ajustada nas 48 h antes da alta,<br/>visitas nas semanas 1, 2, 3 e 6 com exame,<br/>PA, FC, potássio, TFGe e NT-proBNP"]
  D4{"Na visita: algum indicador de<br/>segurança presente?"}
  C4(["Titular até a dose plena, meta de<br/>2 semanas após a alta, manter as visitas<br/>das semanas 3 e 6 e seguir no ambulatório<br/>de IC com iSGLT2 conforme indicação"])
  D5{"Qual indicador?"}
  C5(["Congestão clínica ou NT-proBNP<br/>mais de 10% acima do valor pré-alta:<br/>aumentar diurético, não subir<br/>betabloqueador nesta visita e reavaliar<br/>na visita seguinte"])
  C6(["PAS abaixo de 95 mmHg ou hipotensão<br/>sintomática: não titular IECA, BRA ou<br/>ARNI, ARM e betabloqueador, investigar<br/>a causa e rever em uma semana<br/>ver fluxograma de hipotensão sintomática"])
  C7(["Potássio acima de 5,0 mmol/L ou<br/>TFGe abaixo de 30: não titular IECA,<br/>BRA ou ARNI e ARM, repetir laboratório<br/>em uma semana e, se hipercalemia, considerar<br/>quelante antes de reduzir dose"])
  C8(["FC abaixo de 55 bpm: não titular<br/>betabloqueador, fazer ECG e seguir<br/>titulando os demais pilares<br/>conforme tolerância"])

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| D3
  D3 -->|"Não: contraindicação, fragilidade<br/>ou sem acesso a visitas frequentes"| C3
  D3 -->|"Sim"| P1
  P1 --> D4
  D4 -->|"Não"| C4
  D4 -->|"Sim"| D5
  D5 -->|"Congestão ou NT-proBNP em alta"| C5
  D5 -->|"Hipotensão"| C6
  D5 -->|"Hipercalemia ou queda da TFGe"| C7
  D5 -->|"Bradicardia"| C8

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Antes da alta: o que precisa estar pronto

Os dois primeiros nós vêm da ESC 2021, que recomenda em classe I, nível C, excluir cuidadosamente sobrecarga de volume antes da alta e testar a terapia oral guiada por diretriz ainda no hospital. Congestão residual na alta é o cenário em que a titulação rápida vira problema, não solução: o STRONG-HF só randomizou pacientes hemodinamicamente estáveis, com NT-proBNP acima de 2.500 pg/mL na triagem e queda de mais de 10% entre triagem e randomização, ou seja, pacientes que estavam de fato descongestionando. Quem não está euvolêmico volta ao fluxograma da IC aguda descompensada; quem está euvolêmico mas ainda não iniciou a terapia oral, ou tem potássio e creatinina instáveis, resolve isso internado, na ordem que o fluxograma de sequenciamento da terapia quádrupla propõe.

## Quem entra na estratégia intensiva

A recomendação da ESC 2023 é classe I nível B para todos os internados por IC, mas a evidência vem de uma população definida. Na atualização focada, o STRONG-HF é descrito assim: 1.078 pacientes hospitalizados por IC aguda, estáveis, com NT-proBNP elevado, ainda sem doses plenas de terapia baseada em evidência, randomizados para cuidado habitual ou cuidado de alta intensidade. Os critérios que o nó D3 pede são os que o ensaio usou para entrar e para titular. O registro do ensaio (NCT03412201) e o resumo do Lancet trazem critérios explícitos: idade de 18 a 85 anos; PAS de 100 mmHg ou mais, FC de 60 bpm ou mais e potássio de 5,0 mmol/L ou menos nas 24 h antes da randomização; NT-proBNP acima de 1.500 pg/mL na randomização; exclusão de TFGe abaixo de 30 mL/min/1,73 m2 na triagem ou diálise, intolerância documentada a doses altas de betabloqueador ou de bloqueador do SRAA, expectativa de vida abaixo de 6 meses, alta prevista para instituição de longa permanência e incapacidade de cumprir o seguimento por comorbidade, condição social ou histórico de não adesão. Fragilidade em si não é critério nominal do protocolo; o que o ramo de cuidado habitual traduz é essa combinação de idade acima de 85 anos, intolerância documentada, TFGe abaixo de 30 e inviabilidade de quatro visitas com laboratório em seis semanas.

O ramo de cuidado habitual não é abandono: mantém a consulta em 1 a 2 semanas da ESC 2021 para avaliar congestão, tolerância e iniciar ou titular a terapia, em ritmo individualizado. É também o momento de reconciliação medicamentosa e educação, cobertos em Comunicação clínica.

## O protocolo do STRONG-HF

| Elemento | O que o ensaio fez | Fonte lida |
|---|---|---|
| Primeira visita de titulação | Nas 48 h antes da alta, meta de pelo menos metade das doses-alvo de IECA ou BRA ou ARNI, betabloqueador e ARM | ESC 2023, texto integral |
| Dose plena | Tentada em até 2 semanas após a alta | ESC 2023, resumo do Lancet |
| Visitas | Semanas 1, 2, 3 e 6 após a randomização, com exame físico e laboratório incluindo NT-proBNP; quatro visitas ambulatoriais em 2 meses | ESC 2023, resumo do Lancet |
| O que vigiar | Sintomas e sinais de congestão, PA, FC, NT-proBNP, potássio e TFGe | ESC 2023 |
| iSGLT2 | Não exigido pelo protocolo | ESC 2023 |
| Desfecho primário em 180 dias | Reinternação por IC ou morte: 15,2% vs 23,3%; diferença ajustada 8,1%, IC 95% 2,9 a 13,2; p igual a 0,0021; RR ajustado 0,66, IC 95% 0,50 a 0,86 | Resumo do Lancet, ESC 2023 |
| Dose plena atingida | SRAA 55% vs 2%, betabloqueador 49% vs 4%, ARM 84% vs 46% | ESC 2023 |
| Eventos adversos aos 90 dias | Qualquer: 41% vs 29%; graves: 16% vs 17%; fatais: 5% vs 6% | Resumo do Lancet, ESC 2023 |
| Interrupção | Precoce, por recomendação do comitê de segurança, por diferença maior que a esperada entre os grupos | Resumo do Lancet |

Aos 90 dias, PA, pulso, classe NYHA, peso e NT-proBNP caíram mais no grupo intensivo, com melhora de qualidade de vida. A leitura prática: a estratégia é mais trabalhosa e gera mais eventos adversos não graves, sem aumentar os graves, e o que compra é cerca de um em cada doze pacientes a menos reinternado ou morto em seis meses (diferença absoluta ajustada de 8,1%).

## Indicadores de segurança na visita

Os cinco indicadores do protocolo, conforme a análise de Tomasoni e colaboradores, foram: TFGe abaixo de 30 mL/min/1,73 m2, potássio acima de 5,0 mmol/L, PAS abaixo de 95 mmHg, FC abaixo de 55 bpm e NT-proBNP mais de 10% acima do valor pré-alta. Eles apareceram em 57,7% dos pacientes do braço intensivo em alguma visita, e, quando tratados conforme o protocolo, não se associaram a aumento significativo do desfecho primário composto; isoladamente, TFGe abaixo de 30 associou-se a mais reinternações por IC (HR ajustado 3,60, IC 95% 1,22 a 10,60) e PAS abaixo de 95 mmHg a tendência de maior mortalidade (HR ajustado 2,68, IC 95% 0,94 a 7,64, p igual a 0,065). Isso muda a interpretação do nó D4: o indicador não é falha da estratégia, é o gatilho de pausa que a torna segura. O artigo de desenho descreve a regra geral: a titulação é adiada diante de piora da congestão, hipercalemia, hipotensão, bradicardia, piora da função renal ou aumento significativo do NT-proBNP entre visitas.

| Indicador | Conduta no diagrama |
|---|---|
| Congestão ou NT-proBNP mais de 10% acima do pré-alta | Aumentar diurético, não subir betabloqueador nesta visita |
| PAS abaixo de 95 mmHg | Não titular IECA, BRA ou ARNI, ARM nem betabloqueador |
| Potássio acima de 5,0 mmol/L ou TFGe abaixo de 30 | Não titular IECA, BRA ou ARNI nem ARM |
| FC abaixo de 55 bpm | Não titular betabloqueador |

A atribuição de cada indicador a fármacos específicos, tal como aparece nas condutas C5 a C8, foi conferida no protocolo completo do STRONG-HF: IECA/BRA/ARNI e ARM não são titulados com PAS abaixo de 95 mmHg, potássio acima de 5,0 mmol/L ou TFGe abaixo de 30 mL/min/1,73 m²; betabloqueador não é titulado com frequência abaixo de 55 bpm ou PAS abaixo de 95 mmHg. Pausar a titulação não é retirar a dose atual. Hipotensão sintomática persistente e hipercalemia têm fluxogramas próprios.

## O que vale para todos os ramos

Quatro pontos não estão no diagrama porque se aplicam a qualquer alta por IC: iSGLT2 iniciado conforme a indicação por fração de ejeção, independentemente da estratégia de titulação, porque não exige titulação nem foi parte do protocolo do STRONG-HF; plano diurético oral por escrito, com peso-alvo e instrução de quando ligar; reconciliação medicamentosa e educação com teach-back na alta; e retorno imediato ao hospital diante de congestão franca, que reabre o fluxograma da IC aguda descompensada em qualquer ponto desta árvore.

## Limitações e o que confirmar

- **Critérios de inclusão e exclusão do STRONG-HF** foram conferidos no registro NCT03412201 e no resumo do Lancet (idade 18 a 85 anos, TFGe abaixo de 30 excluída na triagem, intolerância documentada a doses altas, incapacidade de cumprir o seguimento); fragilidade não é critério nominal e o ramo de cuidado habitual continua sendo julgamento clínico. Não houve exclusão por fração de ejeção; a randomização foi estratificada por FEVE de 40% ou menos versus acima de 40%.
- **Regra por fármaco diante de cada indicador de segurança:** conferida no protocolo completo do STRONG-HF (Cotter et al., Eur J Heart Fail. 2019; DOI 10.1002/ejhf.1575).
- **Recomendações pré-alta da ESC 2021**: classe I, nível C, conferidas na tabela da seção 11.3.11 do texto integral em academic.oup.com.
- **Taxas específicas de hipotensão, hipercalemia e piora renal** por braço não constam do resumo nem do texto da ESC 2023 lidos; só os totais de eventos adversos estão na tabela.
- O ensaio foi aberto, interrompido precocemente e o grupo controle recebeu doses baixas: a magnitude do efeito pode estar superestimada, como a própria atualização focada registra ao notar que a maioria do controle recebeu menos da metade das doses plenas.
- Este fluxograma não define doses por fármaco nem cobre a alta de pacientes em choque, com suporte inotrópico ou candidatos a terapia avançada, que têm fluxogramas próprios nesta pasta.

## Tudo com Tudo

- [Insuficiência cardíaca aguda descompensada](/biblioteca/fluxograma-insuficiencia-cardiaca-aguda-descompensada)
- [Fluxograma: Sequenciamento e Titulação da Terapia Quádrupla na ICFEr](/biblioteca/fluxograma-sequenciamento-titulacao-terapia-quadrupla-icfer)
- [Fluxograma: Manejo da Hipotensão Sintomática Limitando a Titulação de IECA/BRA/ARNI na ICFEr](/biblioteca/fluxograma-hipotensao-sintomatica-titulacao-ieca-arni-icfer)
- [Safety, Tolerability and Efficacy of Up-titration of Guideline-Directed Medical Therapies for Acute Heart Failure (STRONG-HF)](/biblioteca/safety-tolerability-and-efficacy-of-up-titration-of-guideline-directed-medical-therapies-for-acute-heart-failure-strong-hf)
- [Atualização Focada 2023 das Diretrizes ESC 2021 de Insuficiência Cardíaca](/biblioteca/atualizacao-focada-2023-das-diretrizes-esc-2021-de-insuficiencia-cardiaca)
- [Transição Hospital-Domicílio na Insuficiência Cardíaca: o Ensaio PACT-HF](/biblioteca/transicao-hospital-domicilio-na-ic-o-ensaio-pact-hf)
- [Fluxograma: Reconciliação Medicamentosa na Transição de Cuidado](/biblioteca/fluxograma-reconciliacao-medicamentosa-na-transicao-de-cuidado)
