---
title: "Escore SAVE: Sobrevida Após ECMO Venoarterial no Choque Cardiogênico Refratário"
slug: escore-save-sobrevida-apos-ecmo-venoarterial-no-choque-cardiogenico-refratario
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Schmidt M, Burrell A, Roberts L, Bailey M, Sheldrake J, Rycus PT, Hodgson C, Scheinkestel C, Cooper DJ, Thiagarajan RR, Brodie D, Pellegrino V, Pilcher D. Predicting survival after ECMO for refractory cardiogenic shock: the survival after veno-arterial-ECMO (SAVE)-score. Eur Heart J. 2015;36(33):2246-2256. DOI: 10.1093/eurheartj/ehv194. PMID: 26033984"]
legacy_source: "Documento novo, escrito nesta sessão. O tema Terapia intensiva já cobre ECMO venoarterial no choque do infarto (ECLS-SHOCK/ECMO-CS) em documento próprio, mas nenhum documento desta base descrevia uma ferramenta de predição de sobrevida pré-canulação — pergunta distinta de qual estratégia de suporte usar, e que a pasta Calculadoras ainda não tinha para o cenário de choque cardiogênico refratário sob ECMO."
---

# Escore SAVE: Sobrevida Após ECMO Venoarterial no Choque Cardiogênico Refratário

## O que é e o problema que resolve
O ECMO venoarterial (ECMO-VA) é usado no choque cardiogênico refratário à terapia médica convencional, mas **decidir quem se beneficia dele antes da canulação** é uma das perguntas mais difíceis da terapia intensiva cardiovascular — o próprio suporte tem morbidade relevante, e prever sobrevida ajuda tanto na decisão individual quanto na comparação de resultados entre centros. Schmidt M et al., *European Heart Journal* 2015;36(33):2246-2256 (PMID 26033984), desenharam o escore **SAVE (Survival After Veno-Arterial-ECMO)** exatamente para essa lacuna: identificar, **antes de iniciar o ECMO**, quais fatores predizem sobrevida hospitalar.

## Como foi derivado
- Base de dados: registro internacional da **Extracorporeal Life Support Organization (ELSO)**, com pacientes em ECMO-VA por choque cardiogênico refratário entre janeiro de 2003 e dezembro de 2013;
- **3.846 pacientes com choque cardiogênico tratados com ECMO** entram na análise; **1.601 (42%) sobreviveram até a alta hospitalar**;
- Regressão logística multivariável com metodologia de bootstrapping, com validação interna e **validação externa** numa coorte australiana independente de 161 pacientes.

## Fatores associados a PIOR sobrevida (pré-ECMO)
- Insuficiência renal crônica;
- Maior duração de ventilação mecânica antes do início do ECMO;
- Falências orgânicas pré-ECMO (múltiplos órgãos);
- Parada cardíaca pré-ECMO;
- Cardiopatia congênita;
- Menor pressão de pulso;
- Menor bicarbonato sérico (HCO₃⁻).

## Fatores associados a MELHOR sobrevida (protetores)
- Idade mais jovem;
- Menor peso corporal;
- Miocardite aguda como causa do choque;
- Transplante cardíaco (como contexto clínico);
- Taquicardia ou fibrilação ventricular refratária como indicação;
- Maior pressão arterial diastólica;
- Menor pressão inspiratória de pico (ventilatória).

## Desempenho e validação
- **Discriminação na coorte de derivação**: área sob a curva ROC (AUROC) de **0,68** (IC95% 0,64-0,71);
- **Validação externa na coorte australiana** (161 pacientes): AUROC de **0,90** (IC95% 0,85-0,95) — discriminação **excelente**, e substancialmente melhor do que na derivação, achado que os próprios autores registram sem propor explicação definitiva no resumo.
- A calculadora oficial do escore está disponibilizada pelos próprios autores em `www.save-score.com`, citada explicitamente no artigo.

## O que este documento NÃO reproduz
**A tabela de pontos variável a variável** (o peso numérico de cada fator listado acima) não está disponível no resumo indexado desta sessão. Para aplicação em um paciente real, use a calculadora oficial (`save-score.com`) citada pelos próprios autores, em vez de reconstruir os pesos por fonte secundária não conferida — mesmo cuidado já registrado nos documentos de GRACE 2.0 e REVEAL desta pasta.

## Leitura clínica
O padrão de fatores é coerente com a fisiopatologia esperada: **falência de múltiplos órgãos e parada cardíaca pré-ECMO** sinalizam deterioração já estabelecida antes do suporte mecânico ser iniciado, enquanto **miocardite aguda e arritmia ventricular refratária** são causas de choque frequentemente reversíveis, compatíveis com melhor prognóstico sob suporte temporário. A discriminação moderada na derivação (AUROC 0,68) — ainda que excelente na validação externa — reforça que o escore é **um insumo para a decisão clínica, não um substituto dela**: no choque cardiogênico refratário, a decisão de canular segue sendo multifatorial e urgente por natureza.
