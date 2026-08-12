---
title: "Inteligência Artificial Aplicada ao ECG na Predição de Risco Cardiovascular: a Plataforma AIRE e o Estado da Arte 2025"
slug: inteligencia-artificial-aplicada-ao-ecg-na-predicao-de-risco-cardiovascular
theme: "Geral"
kind: estudo
review_status: revisado
source_refs: ["Sau A, Pastika L, Sieliwonczyk E, Patlatzoglou K, Ribeiro AH, McGurk KA, et al. Artificial intelligence-enabled electrocardiogram for mortality and cardiovascular risk estimation: a model development and validation study. Lancet Digit Health. 2024;6(11):e791-e802. DOI: 10.1016/S2589-7500(24)00172-9. PMID: 39455192 — desenvolvimento em 1.163.401 ECGs de 189.539 pacientes (BIDMC), validação externa em cinco coortes transnacionais (EUA, Brasil, Reino Unido/UK Biobank); erratum publicado em Lancet Digit Health. 2024;6(12):e882, DOI: 10.1016/S2589-7500(24)00252-8 — não lido em detalhe, declarado aqui", "Svennberg E, Han JK, Caiani EG, Engelhardt S, Ernst S, Friedman P, et al. State of the Art of Artificial Intelligence in Clinical Electrophysiology in 2025: A Scientific Statement of the European Heart Rhythm Association (EHRA) of the ESC, the Heart Rhythm Society (HRS), and the ESC Working Group on E-Cardiology. Europace. 2025;27(5):euaf071. DOI: 10.1093/europace/euaf071. PMID: 40163651. PMCID: PMC12123071 — declaração científica conjunta EHRA/HRS/ESC sobre o estado da arte e as limitações de IA em eletrofisiologia clínica", "Dhingra LS, Aminorroaya A, Sangha V, et al. Heart failure risk stratification using artificial intelligence applied to electrocardiogram images: a multinational study. Eur Heart J. 2025;46(11):1044-1053. DOI: 10.1093/eurheartj/ehae914. PMID: 39804243. PMCID: PMC12086686 — validação multinacional de modelo de IA sobre imagem de ECG (não sinal digital) para risco de insuficiência cardíaca"]
legacy_source: "Documento novo. A pasta Geral tem documentos sobre dispositivos vestíveis para detecção de FA (Apple Heart Study) e sobre custo-efetividade do rastreio de ECG em atletas, mas nenhum sobre o uso de inteligência artificial/aprendizado profundo aplicado ao próprio sinal do ECG de 12 derivações para estimar risco cardiovascular futuro na população geral — tema de rápida evolução em 2024-2026 e de interesse direto do cardiologista, que já vê ferramentas comerciais de 'IA-ECG' sendo oferecidas em consultório."
---

# Inteligência Artificial Aplicada ao ECG na Predição de Risco Cardiovascular

## O que muda: de "ECG normal" para "curva de sobrevida individual"
O ECG de 12 derivações é lido há mais de um século pelos mesmos critérios morfológicos — intervalo, eixo, onda, segmento. Modelos de aprendizado profundo treinados sobre milhões de traçados propõem algo diferente: **extrair, do mesmo sinal, um sinal de risco de longo prazo que o olho humano não lê** — não apenas "há ou não anormalidade", mas **uma estimativa quantitativa de risco futuro de morte e de doença cardiovascular incidente**, a partir de um único ECG, hoje considerado normal pelos critérios convencionais.

## AIRE (2024) — a plataforma desenvolvida em mais de 1 milhão de ECGs e validada em três continentes
Sau A et al., Lancet Digit Health. 2024;6(11):e791-e802 (PMID 39455192). **AI-ECG Risk Estimator (AIRE)**, desenvolvida com aprendizado profundo e um modelo de sobrevida de tempo discreto — o que permite estimar **não só o risco, mas o tempo até o evento**, a partir de um único ECG.

**Desenvolvimento**: **1.163.401 ECGs de 189.539 pacientes** do Beth Israel Deaconess Medical Center (BIDMC, Boston).

**Validação externa em cinco coortes transnacionais diversas** — voluntários, pacientes de atenção primária e de atenção secundária, dos EUA, do Brasil e do Reino Unido (UK Biobank).

**Desempenho (índice C, capacidade discriminativa — 0,5 é acaso, 1,0 é discriminação perfeita):**

| desfecho | C-index no desenvolvimento (BIDMC) | C-index na validação externa |
|---|---|---|
| **mortalidade por qualquer causa** | 0,775 (IC95% 0,773-0,776) | **0,638 a 0,773**, variando por coorte |
| **arritmia ventricular futura** | 0,760 (IC95% 0,756-0,763) | 0,719 no UK Biobank (IC95% 0,635-0,803) |
| **doença cardiovascular aterosclerótica futura** | 0,696 (IC95% 0,694-0,698) | 0,643 no UK Biobank (IC95% 0,624-0,662) |
| **insuficiência cardíaca futura** | 0,787 (IC95% 0,785-0,789) | 0,768 no UK Biobank (IC95% 0,733-0,802) |

**Plausibilidade biológica investigada, não só desempenho estatístico**: os autores fizeram estudos de associação pan-fenotípica e pan-genômica, e identificaram vias biológicas candidatas para o excesso de risco previsto — alterações de estrutura e função cardíacas, e genes associados a estrutura cardíaca, **envelhecimento biológico** e síndrome metabólica.

**A leitura mais honesta do próprio resultado, e a que este documento retém como mensagem central: o desempenho variou de forma relevante entre as coortes de validação externa (C-index de mortalidade entre 0,638 e 0,773)** — a plataforma discrimina risco de forma consistentemente acima do acaso, mas **não com a mesma precisão em toda população testada**.

## O que um modelo assim faz, e o que ele não faz
- **Faz**: a partir de um único ECG de 12 derivações, hoje classificado como "normal" pelos critérios convencionais, estima risco de morte, arritmia ventricular, doença aterosclerótica e insuficiência cardíaca futuras — com estimativa de **tempo até o evento**, não só probabilidade binária.
- **Não faz** (ainda, segundo a própria publicação): não foi incorporado a fluxo clínico assistencial de rotina nas coortes estudadas — é estudo de **desenvolvimento e validação**, não de implementação clínica prospectiva com mudança de conduta guiada pelo modelo.

## Heart failure a partir de IMAGEM do ECG — sem precisar do sinal digital bruto
Dhingra LS et al., Eur Heart J. 2025;46(11):1044-1053 (PMID 39804243). Estudo multinacional que treinou e validou modelo de IA para estratificação de risco de insuficiência cardíaca **a partir de imagens fotografadas ou escaneadas de ECG**, não do sinal eletrônico bruto — relevante para sistemas de saúde e consultórios onde o ECG ainda é registrado em papel, sem exportação digital do traçado.

**Isto amplia a aplicabilidade potencial**: um modelo que depende do sinal digital bruto de determinado fabricante de eletrocardiógrafo tem alcance limitado a quem tem aquele equipamento; um modelo validado sobre imagem tem, em tese, alcance mais amplo — inclusive **em cenários de recursos limitados**, à condição de a validação externa confirmar desempenho equivalente nesses cenários.

## O que a declaração científica conjunta EHRA/HRS/ESC de 2025 acrescenta: o contraponto necessário
Svennberg E et al., Europace. 2025;27(5):euaf071 (PMID 40163651), declaração científica conjunta da European Heart Rhythm Association (EHRA/ESC), da Heart Rhythm Society (HRS) e do ESC Working Group on E-Cardiology sobre o **estado da arte de IA em eletrofisiologia clínica em 2025**. Este documento é a fonte que este texto usa para o contraponto de prudência: sociedades de arritmia dedicam declaração científica inteira ao tema **precisamente porque a validação externa heterogênea, a explicabilidade limitada e a ausência de ensaios prospectivos de impacto clínico são reconhecidas pelas próprias sociedades como lacunas abertas** — não uma ressalva de fora da área, e sim da própria comunidade que desenvolve e estuda essas ferramentas.

## O que isso NÃO autoriza
- **Tratar um "IA-ECG de alto risco" como diagnóstico** — os C-index de validação externa (0,638 a 0,773 para mortalidade) descrevem discriminação populacional, não certeza individual. Um C-index de 0,70 é modesto a moderado, não é alta precisão diagnóstica.
- **Assumir que o desempenho medido no BIDMC (a coorte de desenvolvimento) se repete identicamente em qualquer outra população** — a própria validação externa mostrou variação relevante entre coortes.
- **Considerar essas ferramentas prontas para guiar conduta clínica de rotina** — nenhuma das fontes aqui citadas descreve ensaio clínico randomizado testando se agir sobre o escore de IA-ECG muda desfecho do paciente; são estudos de desenvolvimento/validação de modelo preditivo.
- **Substituir a leitura eletrocardiográfica convencional pela saída do modelo de IA** — as fontes descrevem a IA como camada adicional de informação sobre o mesmo traçado, não substituta da interpretação clínica.

## Limites
- **Nenhuma das fontes aqui citadas é ensaio clínico randomizado** — são estudos de desenvolvimento e validação de modelo preditivo (AIRE, Dhingra et al.) e uma declaração científica de síntese (EHRA/HRS/ESC). Não há, nestas fontes, demonstração de que agir sobre o resultado do modelo melhora desfecho do paciente.
- **A validação externa do AIRE variou por coorte** (C-index de mortalidade entre 0,638 e 0,773) — nenhuma das cinco coortes de validação é brasileira fora do braço específico mencionado; extrapolação para a população geral brasileira não é automática apenas por o Brasil ter integrado uma das coortes.
- **Há erratum publicado para o artigo do AIRE** (Lancet Digit Health. 2024;6(12):e882) — declarado aqui, **não lido em detalhe nesta sessão**; antes de citar valor numérico específico do estudo em contexto que exija precisão máxima, conferir se a errata o afeta.
- **O documento EHRA/HRS/ESC é declaração de estado da arte, não diretriz com recomendação de classe/nível de evidência** — não deve ser citado como se estabelecesse recomendação formal de uso clínico.

## Armadilhas clínicas
- **Interpretar C-index de 0,70 como "alta acurácia"** — é discriminação moderada, adequada para estratificação populacional, insuficiente para decisão individual isolada.
- **Ignorar a variação de desempenho entre coortes de validação externa** ao extrapolar um C-index favorável relatado numa coorte para a prática em outra população.
- **Confundir modelo de predição de risco com ferramenta diagnóstica** — a saída desses modelos é probabilidade/tempo até evento futuro, não diagnóstico de doença presente.
- **Tratar "IA aplicada ao ECG" como tecnologia única e uniforme** — os desfechos estudados (mortalidade geral, arritmia ventricular, doença aterosclerótica, insuficiência cardíaca) e as fontes de dado (sinal digital bruto vs. imagem) são diferentes entre os modelos citados, com desempenho próprio a cada um.
- **Assumir maturidade regulatória e de implementação equivalente à de escore de risco clássico** (como os já validados e em uso rotineiro) — a própria comunidade de eletrofisiologia, na declaração EHRA/HRS/ESC de 2025, trata o tema como estado da arte em evolução, não como prática estabelecida.
