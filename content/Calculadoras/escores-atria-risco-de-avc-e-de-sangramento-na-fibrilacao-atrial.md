---
title: "Escores ATRIA: Risco de AVC e de Sangramento na Fibrilação Atrial"
slug: escores-atria-risco-de-avc-e-de-sangramento-na-fibrilacao-atrial
theme: "Calculadoras"
kind: estudo
review_status: revisado
source_refs: ["Singer DE, Chang Y, Borowsky LH, Fang MC, Pomernacki NK, Udaltsova N, Reynolds K, Go AS. A new risk scheme to predict ischemic stroke and other thromboembolism in atrial fibrillation: the ATRIA study stroke risk score. J Am Heart Assoc. 2013;2(3):e000250. DOI: 10.1161/JAHA.113.000250. PMID: 23782923. PMCID: PMC3698792 — texto integral aberto, lido na íntegra via PMC (Tabelas 2, 3, 4 e 5)", "Fang MC, Go AS, Chang Y, Borowsky LH, Pomernacki NK, Udaltsova N, Singer DE. A new risk scheme to predict warfarin-associated hemorrhage: The ATRIA (Anticoagulation and Risk Factors in Atrial Fibrillation) Study. J Am Coll Cardiol. 2011;58(4):395-401. DOI: 10.1016/j.jacc.2011.03.031. PMID: 21757117. PMCID: PMC3175766 — pontuação completa e taxas de evento já constam do resumo indexado no PubMed, conferido por efetch"]
legacy_source: "Documento novo, escrito em 01/08/2026. O nome 'ATRIA' já aparecia nesta biblioteca duas vezes como comparador de desempenho — na tabela de índice-c do documento do escore ORBIT e na do documento dos escores ABC — mas sem nenhum documento próprio que explicasse seus componentes, pontuação e origem. Lacuna agravada porque 'ATRIA' nomeia DOIS escores distintos, derivados da mesma coorte em anos diferentes (AVC em 2013, sangramento em 2011), e os documentos existentes citam só o de sangramento sem dizer que há um segundo."
---

# Escores ATRIA: Risco de AVC e de Sangramento na Fibrilação Atrial

## Definição e a armadilha do nome
**ATRIA** é o nome do estudo de coorte — *Anticoagulation and Risk Factors in Atrial Fibrillation* — e, por extensão, o nome de **dois escores de risco distintos** derivados dessa mesma coorte, em publicações diferentes:

1. **Escore de sangramento por varfarina** (Fang MC et al., *J Am Coll Cardiol*. 2011;58(4):395-401, PMID 21757117) — publicado primeiro, prevê hemorragia maior associada ao uso de varfarina.
2. **Escore de risco de AVC** (Singer DE et al., *J Am Heart Assoc*. 2013;2(3):e000250, PMID 23782923) — publicado depois, prevê AVC isquêmico e outros eventos tromboembólicos, e foi desenhado explicitamente para comparar desempenho com o CHADS₂ e o CHA₂DS₂-VASc.

**Quando esta biblioteca (ou qualquer outra fonte) cita apenas "ATRIA" como comparador de um escore de sangramento — como acontece nos documentos do ORBIT e dos escores ABC —, o escore referido é o de Fang 2011 (sangramento), não o de Singer 2013 (AVC).** A faixa de pontuação confirma qual é qual: o escore de sangramento vai de 0 a 10; o de AVC, de 0 a 15.

## O escore de risco de AVC (Singer et al., 2013)

### População e derivação
Coorte de derivação: **10.927 pacientes** com FA não valvar, contribuindo **32.609 pacientes-ano** fora de varfarina e **685 eventos tromboembólicos**. Validação externa numa segunda coorte, ATRIA-CVRN (*Cardiovascular Research Network*): **25.306 pacientes**, **26.263 pacientes-ano** fora de varfarina, **496 eventos**.

Por modelo de Cox, foram identificadas **8 variáveis** — idade, AVC prévio, sexo feminino, diabetes mellitus, insuficiência cardíaca, hipertensão, proteinúria e TFGe <45 mL/min/1,73m² (ou doença renal terminal) — **mais um termo de interação entre idade e AVC prévio**, incluído no modelo final. Os pontos foram atribuídos proporcionalmente ao coeficiente de regressão de cada variável, arredondados ao inteiro mais próximo.

### Coeficientes de regressão (Tabela 2 do artigo)

| Característica clínica | Coeficiente | Razão de risco (HR) | Pontos |
|---|---|---|---|
| Idade ≥85, **com** AVC prévio | 2,48 | 11,92 | **9** |
| Idade 75-84, **com** AVC prévio | 2,03 | 7,61 | **7** |
| Idade 65-74, **com** AVC prévio | 2,07 | 7,89 | **7** |
| Idade <65, **com** AVC prévio | 2,20 | 8,99 | **8** |
| Idade ≥85, **sem** AVC prévio | 1,85 | 6,38 | **6** |
| Idade 75-84, **sem** AVC prévio | 1,33 | 3,79 | **5** |
| Idade 65-74, **sem** AVC prévio | 0,74 | 2,10 | **3** |
| Sexo feminino | 0,42 | 1,52 | **1** |
| Diabetes mellitus | 0,34 | 1,40 | **1** |
| Insuficiência cardíaca | 0,24 | 1,27 | **1** |
| Hipertensão | 0,22 | 1,24 | **1** |
| Proteinúria | 0,34 | 1,40 | **1** |
| TFGe <45 mL/min/1,73m² ou doença renal terminal | 0,28 | 1,33 | **1** |

Idade e AVC prévio foram os preditores dominantes — daí a interação entre as duas variáveis em vez de tratá-las como independentes.

### Tabela de pontuação final (Tabela 3 do artigo)

| Fator de risco | Pontos sem AVC prévio | Pontos com AVC prévio |
|---|---|---|
| Idade ≥85 anos | 6 | 9 |
| Idade 75-84 anos | 5 | 7 |
| Idade 65-74 anos | 3 | 7 |
| Idade <65 anos | 0 | 8 |
| Sexo feminino | +1 | +1 |
| Diabetes mellitus | +1 | +1 |
| Insuficiência cardíaca | +1 | +1 |
| Hipertensão | +1 | +1 |
| Proteinúria | +1 | +1 |
| TFGe <45 ou doença renal terminal | +1 | +1 |

**Faixa de pontuação possível: 0 a 12 pontos para quem nunca teve AVC, e 7 a 15 pontos para quem já teve.** Repare que essas faixas **não se separam por sexo nem pelas demais comorbidades** — cada uma soma até 6 pontos adicionais (1 ponto × 6 variáveis) sobre a base de idade/AVC prévio.

### Categorias de risco e desempenho
O escore foi agrupado em três categorias, ajustadas para corresponder a taxas anuais de evento tromboembólico de **<1%, 1% a <2%, e ≥2%**:

| Categoria | Pontuação | Taxa observada na coorte ATRIA |
|---|---|---|
| Baixo risco | 0 a 5 | <1%/ano |
| Risco moderado | 6 | 1% a <2%/ano |
| Alto risco | 7 a 15 | ≥2%/ano |

Índice-c (capacidade discriminativa), coorte de derivação, com a pontuação completa: **ATRIA 0,73 (IC95% 0,71-0,75)**, contra **CHADS₂ 0,69 (0,67-0,71)** e **CHA₂DS₂-VASc 0,70 (0,68-0,72)**. Ao restringir a eventos graves (Rankin ≥3 na alta ou óbito em até 30 dias), o índice-c do ATRIA sobe para **0,76 (0,74-0,79)**. Na validação externa (ATRIA-CVRN), os valores foram semelhantes: **0,70 (0,67-0,72)** para todos os eventos e **0,75 (0,72-0,78)** para eventos graves. Houve **melhora líquida de reclassificação positiva** do ATRIA sobre os dois escores comparadores, tanto com os pontos de corte publicados quanto com pontos de corte otimizados para o CHADS₂ e o CHA₂DS₂-VASc.

## O escore de risco de sangramento (Fang et al., 2011)

### População e derivação
**9.186 pacientes** com FA em uso de varfarina, contribuindo **32.888 pacientes-ano** de seguimento, com **461 primeiras hemorragias maiores** (taxa anual de **1,4%**). Por regressão de Cox com seleção de variáveis por bootstrapping, o modelo final reteve **5 variáveis independentes**, cada uma ponderada pelo coeficiente de regressão:

| Componente | Pontos |
|---|---|
| Anemia | **3** |
| Doença renal grave (TFG <30 mL/min ou dependência de diálise) | **3** |
| Idade ≥75 anos | **2** |
| Sangramento prévio | **1** |
| Hipertensão | **1** |

**Escore total: 0 a 10 pontos** (soma simples).

### Taxas de sangramento e categorias de risco
A taxa de hemorragia maior variou de **0,4%/ano (0 pontos) a 17,3%/ano (10 pontos)**. Reduzido a três categorias:

| Categoria | Pontuação | Taxa de sangramento maior |
|---|---|---|
| Baixo risco | 0 a 3 | **0,8%/ano** |
| Risco intermediário | 4 | **2,6%/ano** |
| Alto risco | 5 a 10 | **5,8%/ano** |

Índice-c: **0,74** para o escore contínuo e **0,69** para a versão em 3 categorias — nos dois casos, superior aos seis esquemas de risco de sangramento com os quais o artigo comparou. Melhora líquida de reclassificação de **27% a 56%** em relação a esses seis comparadores.

## Armadilhas de leitura
- **"ATRIA" sem qualificação é ambíguo.** Antes de usar o número, confirme a faixa de pontuação (0-10 é sangramento/Fang 2011; 0-15 é AVC/Singer 2013) e o ano da publicação citada — os dois escores nasceram da mesma coorte, com quase três anos de diferença entre as publicações.
- **O escore de sangramento foi derivado só em pacientes usando varfarina** (2011, antes da era dos DOAC). Extrapolar os pontos e as taxas de evento para quem usa apixabana, rivaroxabana, dabigatrana ou edoxabana não tem validação direta na fonte original.
- **A interação idade × AVC prévio produz pontuação não intuitiva no escore de AVC.** Um paciente com menos de 65 anos e AVC prévio soma **8 pontos** — mais do que um paciente de 65 a 74 anos **sem** AVC prévio (3 pontos), e quase o mesmo que um paciente de 75 a 84 anos sem AVC prévio (5 pontos, contra 7 do grupo mais jovem com AVC prévio). **Ler a tabela pela coluna certa (com/sem AVC prévio) é indispensável** — aplicar os pontos "sem AVC prévio" a quem já teve AVC subestima o risco.
- **"Doença renal grave" no escore de sangramento (TFG <30 ou diálise) não é o mesmo corte do escore de AVC** (TFGe <45 ou doença renal terminal) **nem do CRUSADE** (clearance de creatinina por Cockcroft-Gault em faixas próprias, já registrado no documento correspondente desta biblioteca). Três escores, três definições de disfunção renal — não substituir uma pela outra.
- **O resumo indexado do escore de AVC (PubMed) não traz a tabela de pontos** — só descreve as 8 variáveis e o desempenho agregado. A tabela de pontuação completa (Tabelas 2 e 3 acima) foi extraída do **texto integral aberto no PMC** (PMC3698792); o resumo do escore de sangramento, ao contrário, já traz a pontuação completa das 5 variáveis, por isso as duas fontes foram lidas de formas diferentes — uma exigiu o artigo inteiro, a outra não.
- **Nenhum dos dois escores substitui a decisão de anticoagular.** O de AVC estima o benefício esperado da anticoagulação; o de sangramento, o custo esperado dela — nenhum decide sozinho, e nenhum é critério formal de exclusão de terapia, mesma ressalva que vale para o HAS-BLED, o ORBIT e os escores ABC já registrados nesta biblioteca.

## Fonte
Singer DE, Chang Y, Borowsky LH, Fang MC, Pomernacki NK, Udaltsova N, Reynolds K, Go AS. A new risk scheme to predict ischemic stroke and other thromboembolism in atrial fibrillation: the ATRIA study stroke risk score. J Am Heart Assoc. 2013;2(3):e000250. DOI: 10.1161/JAHA.113.000250. PMID: 23782923.

Fang MC, Go AS, Chang Y, Borowsky LH, Pomernacki NK, Udaltsova N, Singer DE. A new risk scheme to predict warfarin-associated hemorrhage: The ATRIA (Anticoagulation and Risk Factors in Atrial Fibrillation) Study. J Am Coll Cardiol. 2011;58(4):395-401. DOI: 10.1016/j.jacc.2011.03.031. PMID: 21757117.
