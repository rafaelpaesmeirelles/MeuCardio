---
title: "Escore de Duke do Teste Ergométrico (Duke Treadmill Score)"
slug: escore-de-duke-do-teste-ergometrico-treadmill-score
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Mark DB, Shaw L, Harrell FE Jr, Hlatky MA, Lee KL, Bengtson JR, McCants CB, et al. Prognostic value of a treadmill exercise score in outpatients with suspected coronary artery disease. N Engl J Med. 1991;325(12):849-853. DOI: 10.1056/NEJM199109193251204. PMID: 1875969 — validação em 613 pacientes ambulatoriais"]
legacy_source: "Documento novo, escrito em 31/07/2026. O tema Calculadoras tinha escores de risco de sangramento, de síndrome coronariana aguda, de insuficiência cardíaca e de cirurgia cardíaca, mas nenhum sobre teste ergométrico — apesar de o escore de Duke ser calculado a partir de um exame de altíssima disponibilidade no Brasil e de transformar seu resultado em estimativa de sobrevida."
---

# Escore de Duke do Teste Ergométrico

## O que e
Escore prognóstico calculado a partir de três variáveis do próprio teste ergométrico em esteira, que estratifica o risco de morte e ajuda a decidir sobre encaminhamento para cateterismo. Foi derivado em pacientes internados encaminhados para cateterismo e **validado prospectivamente em pacientes ambulatoriais** — que é o cenário em que mais se usa.

Referência: Mark DB et al., N Engl J Med. 1991;325(12):849-853 (PMID 1875969).

## A formula
```
Escore = duração do exercício (minutos)
         − (5 × desvio máximo do segmento ST, em milímetros)
         − (4 × índice de angina na esteira)
```

**Índice de angina na esteira** (valor numérico):
- **0** — sem angina
- **1** — angina não limitante
- **2** — angina que limita o exercício

O desvio de ST é o **máximo durante ou após** o exercício. A duração é o tempo de exercício em minutos — na coorte original, em protocolo de esteira.

**Faixa possível do escore: de −25 (maior risco) a +15 (menor risco).**

## Estratificacao e sobrevida medida
| Faixa | Risco | Frequência na coorte | Sobrevida em 4 anos | Mortalidade anual média |
|---|---|---|---|---|
| **≥ +5** | baixo | cerca de **2/3** dos pacientes | **99%** | **0,25%** |
| entre −10 e +5 | intermediário | — | — | — |
| **< −10** | alto | **4%** dos pacientes | **79%** | **5%** |

Os valores de sobrevida acima são os medidos no estudo de validação ambulatorial, com **seguimento de 4 anos e 98% de completude**.

**A distribuição importa tanto quanto os cortes:** dois terços dos pacientes caem na faixa de baixo risco, com mortalidade anual de 0,25% — e é isso que faz o escore ser útil para **evitar** cateterismo, não só para indicá-lo.

## Desempenho
- **Área sob a curva ROC de 0,849** para separar quem morreu de quem sobreviveu em 4 anos
- **O escore discriminou melhor que os dados clínicos** e foi **mais útil em pacientes ambulatoriais do que havia sido em internados** — resultado incomum, já que escores costumam perder desempenho fora da coorte de derivação

## Populacao de derivacao e validacao
- **613 pacientes ambulatoriais consecutivos** com suspeita de doença coronariana, encaminhados para teste ergométrico entre **1983 e 1985**
- Seguimento **98% completo em 4 anos**

## Limites que precisam acompanhar o uso
- **Coorte dos anos 1980.** O tratamento da doença coronariana mudou substancialmente desde então — estatina de alta intensidade, antiagregação dupla, revascularização percutânea moderna. As taxas absolutas de sobrevida de hoje tendem a ser **melhores** que as da tabela, o que **superestima o risco** do paciente contemporâneo
- **Depende de o paciente conseguir se exercitar.** Quem não atinge esforço adequado não gera escore interpretável — e a incapacidade de exercitar-se é, por si, marcador prognóstico
- **Não substitui a avaliação de probabilidade pré-teste.** Um escore de baixo risco em paciente com probabilidade pré-teste muito alta merece leitura diferente
- **A validação foi em pacientes ambulatoriais com suspeita de doença coronariana** — não em síndrome coronariana aguda, não em portadores de doença já estabelecida em investigação de isquemia residual
- **Desempenho em mulheres** foi objeto de análise específica posterior na literatura, e a coorte de 1991 não estratificou o resultado por sexo neste artigo

## Onde ele se encaixa entre os escores desta pasta
Diferente do TIMI, GRACE e CRUSADE, que são de **síndrome coronariana aguda**, e do SCORE2, que é de **risco populacional em prevenção**, o escore de Duke é de **estratificação prognóstica a partir de um exame funcional** em paciente estável com suspeita de doença coronariana. É a ponte entre o resultado do teste e a decisão sobre cateterismo.

## Armadilhas clinicas
- **Aplicar as taxas de sobrevida de 1991 como estimativa atual** — o tratamento mudou, e o escore tende a superestimar o risco de hoje
- **Calcular o escore em teste submáximo ou interrompido por motivo não cardíaco** — a duração do exercício é o componente de maior peso e fica distorcida
- **Usar o índice de angina errado** — é 0/1/2 conforme ausência, angina não limitante e angina limitante, multiplicado por 4; trocar por presença/ausência muda o resultado
- **Esquecer o sinal negativo dos dois termos** — desvio de ST e angina **subtraem**; escore alto positivo é bom
- **Indicar cateterismo com escore de baixo risco isoladamente** — a mortalidade anual dessa faixa é de 0,25%, e é justamente a faixa em que o exame invasivo tende a não agregar
- **Aplicar em síndrome coronariana aguda** — não é a população de validação
