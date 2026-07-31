---
title: "Escore DASH: Risco de Recorrência após TEV Não Provocado"
slug: escore-dash-risco-de-recorrencia-apos-tev-nao-provocado
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Tosetto A, Iorio A, Marcucci M, Baglin T, Cushman M, Eichinger S, et al. Predicting disease recurrence in patients with previous unprovoked venous thromboembolism: a proposed prediction score (DASH). J Thromb Haemost. 2012;10(6):1019-1025. DOI: 10.1111/j.1538-7836.2012.04735.x. PMID: 22489957 — dados individuais de 1.818 casos, agrupados de sete estudos prospectivos"]
legacy_source: "Documento novo, escrito em 31/07/2026. A biblioteca tinha a regra HERDOO2, que responde à mesma pergunta mas só em mulheres, e a discussão de duração de anticoagulação dentro dos documentos de TEV — mas não o DASH, que se aplica aos dois sexos e é o escore mais usado para decidir entre parar e manter indefinidamente."
---

# Escore DASH: Risco de Recorrência após TEV Não Provocado

## A decisao que o escore serve
Depois de um primeiro episódio de tromboembolismo venoso **não provocado**, tratado por pelo menos 3 meses, vem a pergunta mais difícil da anticoagulação: **parar ou manter indefinidamente?** Como os autores colocam, a duração ótima **se ancora em estimar o risco de recorrência**.

Anticoagular para sempre previne recorrência e acumula risco de sangramento ao longo de anos. O DASH existe para dar um número a esse lado da balança.

## Derivacao
Tosetto A et al., J Thromb Haemost. 2012;10(6):1019-1025 (PMID 22489957):
- **Dados individuais de 1.818 casos** de TEV não provocado, **agrupados de sete estudos prospectivos**
- Todos tratados por **pelo menos 3 meses com antagonista da vitamina K**
- Coeficientes de Cox corrigidos para otimismo; validação interna por *bootstrap*

## Os quatro componentes — o acronimo e a formula
**DASH = D-dímero, Age (idade), Sex (sexo), Hormonal therapy (terapia hormonal)**

Os preditores principais de recorrência foram:
- **D-dímero anormal APÓS parar a anticoagulação**
- **Idade abaixo de 50 anos**
- **Sexo masculino**
- **TEV NÃO associado a terapia hormonal** (em mulheres)

**Atenção ao ponto que mais gera erro de aplicação:** o D-dímero do escore é o **colhido depois de suspender o anticoagulante**, não durante o tratamento. Dosá-lo em vigência de anticoagulação não serve — e é o engano mais comum com este escore.

Note também que **três dos quatro itens apontam para o mesmo perfil**: homem, jovem, sem gatilho hormonal. O escore formaliza a observação de que **mulher cujo TEV ocorreu sob terapia hormonal tem risco de recorrência menor** depois de removido o gatilho.

## Desempenho e risco anual de recorrencia
- **Área sob a curva ROC de 0,71** — capacidade preditiva satisfatória, e não excelente; é honesto tratá-la assim

| Pontuação | Risco anual de recorrência |
|---|---|
| **≤ 1** | **3,1%** (IC95% 2,3-3,9) |
| **= 2** | **6,4%** (IC95% 4,8-7,9) |
| **≥ 3** | **12,3%** (IC95% 9,9-14,7) |

**A leitura de impacto**, nas palavras dos autores: considerando de baixo risco quem tem escore ≤ 1, a **anticoagulação por toda a vida poderia ser evitada em cerca de metade dos pacientes** com TEV não provocado.

## Como usar, e o que a decisao ainda exige
- **O escore estima só um lado da balança** — o risco de **recorrência**. A decisão de manter ou parar exige pôr ao lado o **risco de sangramento** daquele paciente, que o DASH não mede
- **É para TEV NÃO PROVOCADO.** Trombose com fator desencadeante claro (cirurgia, imobilização prolongada, trauma) tem outra história natural e outra regra de duração
- **O D-dímero é pós-suspensão** — o escore não é aplicável sem essa medida
- **Compare com a HERDOO2**, que responde à mesma pergunta **apenas em mulheres** e usa outros itens; está em `regra-herdoo2-duracao-da-anticoagulacao-apos-tev-nao-provocado-em-mulheres.md`, no tema Tromboembolismo. **O DASH vale para os dois sexos**
- **Validação interna por bootstrap**, não validação externa independente no artigo original — é limitação a citar

## Armadilhas clinicas
- **Dosar o D-dímero durante a anticoagulação** — o item do escore é o valor **após** suspender
- **Aplicar a TEV provocado** — a população derivada é de TEV **não** provocado
- **Decidir só pelo DASH** — falta o risco de sangramento, que é o outro prato da balança
- **Tratar a AUC de 0,71 como discriminação excelente** — é satisfatória, e a decisão continua sendo clínica
- **Esquecer que o item hormonal se aplica a mulheres** — é a ausência de gatilho hormonal que aumenta o risco de recorrência
- **Usar em quem foi tratado por menos de 3 meses** — a coorte tinha pelo menos esse tempo de anticoagulação
