---
title: "Escore C2HEST: Predição de Fibrilação Atrial Incidente na População Geral e no AVC Criptogênico"
slug: escore-c2hest-predicao-de-fibrilacao-atrial-incidente
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Li YG, Pastori D, Farcomeni A, Yang PS, Jang E, Joung B, et al. A Simple Clinical Risk Score (C2HEST) for Predicting Incident Atrial Fibrillation in Asian Subjects: Derivation in 471 446 Chinese Subjects, With Internal Validation and External Application in 451 199 Korean Subjects. Chest. 2019;155(3):510-518. DOI: 10.1016/j.chest.2018.09.011. PMID: 30292759", "Pinnacchio G, Scacciavillani R, Narducci ML, et al. External Validation of Published Scoring Systems to Predict Incident Atrial Fibrillation After Cryptogenic Stroke/Embolic Stroke of Undetermined Source. J Am Heart Assoc. 2026;15(13):e047601. DOI: 10.1161/JAHA.125.047601. PMID: 42333650"]
legacy_source: "Documento novo, escrito em 09/09/2026. A pasta já cobre escores de risco de AVC/sangramento na FA já estabelecida (CHA₂DS₂-VA, CHADS₂, HAS-BLED, ABC) e escores de recorrência pós-ablação (APPLE/APCEL), mas nenhum escore respondia à pergunta anterior: quem, sem FA diagnosticada, tem risco relevante de desenvolvê-la — pergunta central para decidir rastreio prolongado (Holter estendido, monitor implantável) em AVC criptogênico e na triagem oportunística de FA subclínica."
---

# Escore C2HEST: Predição de Fibrilação Atrial Incidente na População Geral e no AVC Criptogênico

## A pergunta que o escore responde
Todos os escores já registrados nesta pasta para fibrilação atrial (FA) — CHA₂DS₂-VA, CHADS₂, HAS-BLED, os escores ABC, APPLE/APCEL — pressupõem que a **FA já foi diagnosticada**. O C2HEST resolve um problema anterior: **quem, na população geral ainda sem FA, tem risco alto o bastante de desenvolvê-la para justificar rastreio ativo** (Holter prolongado, monitor cardíaco implantável, ECG oportunístico em consulta)? É a mesma lógica clínica que motiva a triagem de FA subclínica após AVC criptogênico/AVC embólico de origem indeterminada (ESUS).

## Derivação e validação externa — Li et al., Chest 2019
Li YG et al., *Chest*. 2019;155(3):510-518 (PMID 30292759):
- **Coorte de derivação**: 471.446 indivíduos chineses, sem FA e sem uso de anticoagulante no início do seguimento
- **Validação externa independente**: 451.199 indivíduos coreanos
- Desfecho: **FA incidente** (nova, diagnosticada durante o seguimento)

**Fatores de risco identificados por regressão** (texto da fonte): doença cardíaca estrutural (SHD), insuficiência cardíaca (HF), idade ≥ 75 anos, doença arterial coronariana (CAD), hipertireoidismo, DPOC e hipertensão.

## Os componentes e a pontuação — C2HEST
O nome é o próprio mnemônico dos componentes, com a pontuação de cada um:

| Componente | Critério | Pontos |
|---|---|---|
| **C** | Doença arterial coronariana (CAD) OU DPOC | **1 ponto** (cada, cumulativo — daí o "C₂") |
| **H** | Hipertensão | **1 ponto** |
| **E** | Idoso, idade ≥ 75 anos | **2 pontos** |
| **S** | Insuficiência cardíaca sistólica | **2 pontos** |
| **T** | Doença tireoidiana (hipertireoidismo) | **1 ponto** |

Pontuação total possível: **0 a 8**. Ao contrário de HAS-BLED ou CHA₂DS₂-VASc, o "C" soma dois itens distintos (coronariopatia **e** DPOC) — cada um vale 1 ponto isoladamente, e o paciente com os dois soma 2.

## Desempenho medido
- **Coorte de derivação (chinesa)**: AUC 0,75 (IC95% 0,73-0,77); validação interna por *bootstrap* confirmou o mesmo valor
- **Aplicação externa (coreana)**: AUC 0,65 (IC95% 0,65-0,66) — queda esperada de uma validação externa em outra população, mas ainda com discriminação superior aos comparadores
- **Calibração**: p = 0,774 na coorte externa (sem evidência de descalibração)
- **Comparação direta, no próprio artigo**: *"O escore C2HEST foi superior ao CHADS₂ e ao CHA₂DS₂-VASc nas duas coortes na predição de FA incidente"* — atenção: essa comparação é sobre **predizer o aparecimento** de FA, não sobre o uso original desses dois escores (risco de AVC em quem **já tem** FA). Comparar um escore de predição de doença nova com um escore de risco de complicação de doença já estabelecida é comparação de propósito, não de mesma pergunta clínica — o artigo faz a comparação estatística mesmo assim, porque ambos usam variáveis clínicas simples de forma semelhante.

## Validação recente no AVC criptogênico/ESUS — Pinnacchio et al., JAHA 2026
Pinnacchio G et al., *J Am Heart Assoc*. 2026;15(13):e047601 (PMID 42333650), validação externa de **sete** sistemas de escore para prever FA incidente especificamente em pacientes com AVC criptogênico ou ataque isquêmico transitório (AIT) que receberam **monitor cardíaco implantável**:
- **132 pacientes**, seguimento médio de **13 ± 12 meses**
- **FA detectada em 40 pacientes (30,3%)** — taxa alta, esperada nessa população selecionada por monitorização contínua
- Escores testados: C2HEST, Brown ESUS-AF, ESUS-AF, HAVOC, ACTEL, AS5F e CHASE-LESS
- **AUC do C2HEST nesta coorte: 0,704** — desempenho "aceitável" pelo próprio critério do estudo (limiar de AUC > 0,7)
- Os três de melhor desempenho no estudo foram **C2HEST (0,704), Brown ESUS-AF (0,755) e AS5F (0,726)**; os demais (ESUS-AF 0,607, HAVOC 0,661, ACTEL 0,650, CHASE-LESS 0,671) ficaram abaixo do limiar
- Conclusão da fonte, citada literalmente: esses três escores *"predisseram de forma confiável a FA em pacientes com AVC criptogênico/ESUS e podem ajudar a identificar indivíduos de baixo risco, apoiando o uso mais direcionado de ferramentas diagnósticas e orientando estratégias de prevenção de AVC"*.

**Nota sobre os quatro comparadores desta validação (Brown ESUS-AF, ESUS-AF, HAVOC, ACTEL, AS5F, CHASE-LESS)**: não são descritos em detalhe neste documento — cada um tem componentes e pontuação próprios, que não foram conferidos nesta sessão contra a fonte primária de cada escore. `VERIFICAÇÃO HUMANA NECESSÁRIA` antes de citar a composição desses cinco instrumentos; os números de AUC acima, esses sim, vêm diretamente do artigo de validação e estão conferidos.

## Como usar na prática
- **Escore baixo (0-1)**: risco de FA incidente baixo — não é indicação isolada para rastreio ativo prolongado
- **Escore intermediário a alto (≥ 2, e sobretudo componentes de 2 pontos como idade ≥ 75 ou IC sistólica)**: sustenta rastreio mais agressivo — ECG oportunístico repetido, Holter prolongado, ou monitor implantável quando o cenário clínico já favorecer investigação (por exemplo, AVC criptogênico)
- O escore foi derivado e validado em **populações asiáticas** (China e Coreia) — a validação em AVC criptogênico (Pinnacchio 2026) amplia a aplicação a uma coorte ocidental com AVC/AIT, mas **não** é uma validação em população geral ocidental sem evento cerebrovascular prévio

## Armadilhas clínicas
- **Confundir com CHA₂DS₂-VASc/CHADS₂**: aqueles estimam risco de **AVC em quem já tem FA**; o C2HEST estima risco de **desenvolver FA** em quem ainda não tem — são perguntas clínicas diferentes, mesmo usando variáveis parecidas (idade, hipertensão, IC)
- **Somar CAD e DPOC como um só ponto** — são dois critérios independentes dentro do "C", 1 ponto cada, cumulativos
- **Extrapolar o desempenho da coorte chinesa/coreana (AUC 0,75/0,65) diretamente para a decisão de implantar monitor cardíaco em AVC criptogênico** sem considerar que a validação específica nessa população (Pinnacchio 2026) mostrou AUC mais modesto (0,704) — ainda útil, mas não altamente discriminativo isoladamente
- **Tratar o C2HEST como superior aos outros seis escores testados no AVC criptogênico** de forma absoluta — o Brown ESUS-AF teve AUC numericamente maior (0,755) na mesma coorte; a diferença não foi discutida como estatisticamente significativa no resumo disponível, então não se deve afirmar superioridade do C2HEST sobre o Brown ESUS-AF a partir só desses números
- **Usar isoladamente para decidir anticoagulação empírica** — o C2HEST orienta a intensidade do **rastreio**, não substitui a confirmação eletrocardiográfica da FA antes de anticoagular
