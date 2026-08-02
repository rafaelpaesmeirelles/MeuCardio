---
title: "Algoritmo YEARS: Diagnóstico de TEP com Corte de D-dímero Adaptativo"
slug: algoritmo-years-diagnostico-de-tep-com-corte-de-d-dimero-adaptativo
theme: "Calculadoras"
kind: estudo
review_status: revisado
source_refs: ["van der Hulle T, Cheung WY, Kooij S, Beenen LFM, van Bemmel T, van Es J, et al; YEARS study group. Simplified diagnostic management of suspected pulmonary embolism (the YEARS study): a prospective, multicentre, cohort study. Lancet. 2017;390(10091):289-297. DOI: 10.1016/S0140-6736(17)30885-1. PMID: 28549662 — estudo prospectivo, multicêntrico, 12 hospitais holandeses, 3.465 pacientes, outubro/2013 a julho/2015"]
legacy_source: "Documento novo. Existe em content/Gravidez/diagnostico-de-tep-na-gestante-years-adaptado-e-a-estrategia-do-ct-pe-pregnancy.md o algoritmo YEARS ADAPTADO PARA GESTANTES (Artemis, van der Pol et al., NEJM 2019, PMID 30893534) — este documento é distinto e trata do algoritmo YEARS ORIGINAL, na população geral não gestante, com foco no ângulo de simplificação diagnóstica frente aos escores clássicos (Wells, Genebra) já cadastrados nesta pasta de Calculadoras."
---

# Algoritmo YEARS: Diagnóstico de TEP com Corte de D-dímero Adaptativo

## O que este documento cobre, e o que não cobre
Este documento trata do **algoritmo YEARS original**, publicado por van der Hulle et al. no Lancet em 2017 (PMID 28549662), validado em população geral de pacientes ambulatoriais e de pronto-socorro com suspeita de tromboembolismo pulmonar (TEP) — **não gestantes**. A versão adaptada para gestantes (estudo Artemis) já está registrada em `content/Gravidez/diagnostico-de-tep-na-gestante-years-adaptado-e-a-estrategia-do-ct-pe-pregnancy.md`, com algoritmo, corte e desfechos próprios daquela população; não é repetida aqui. O recorte deste documento é conceitual: **por que o YEARS simplifica a decisão clínica em relação aos escores de Wells e de Genebra**, e o que o estudo original mostrou em números.

## Os 3 critérios do YEARS
O algoritmo YEARS reduz a probabilidade pré-teste a **apenas três itens clínicos binários** (presente/ausente), avaliados junto com a dosagem de D-dímero na mesma coleta — sem necessidade de calcular pontuação nem de tabela de conversão:

1. **Sinais clínicos de trombose venosa profunda (TVP)**
2. **Hemoptise**
3. **TEP é o diagnóstico mais provável** (julgamento clínico do próprio médico assistente, sem outro diagnóstico alternativo mais plausível)

Não há pontuação a somar: o algoritmo apenas registra **quantos desses três itens estão presentes — zero, ou um ou mais** —, e é essa contagem binária (zero vs. ≥1) que determina qual corte de D-dímero será aplicado na etapa seguinte.

## O corte de D-dímero adaptativo (o núcleo da simplificação)
Diferente dos escores clássicos, que usam um único corte fixo de D-dímero (tipicamente <500 ng/mL) independente da probabilidade clínica, o YEARS **ajusta o corte de D-dímero conforme a presença ou ausência dos três itens**:

- **Nenhum item do YEARS presente** → TEP é excluído se D-dímero **< 1.000 ng/mL**
- **Um ou mais itens do YEARS presentes** → TEP é excluído se D-dímero **< 500 ng/mL**

Se o D-dímero estiver acima do corte aplicável (ou se houver qualquer item do YEARS combinado com D-dímero ≥500 ng/mL), o paciente segue para angiotomografia de artérias pulmonares (angioTC). É essa combinação de um único conjunto de três perguntas simples com dois pontos de corte de D-dímero — em vez de uma pontuação de múltiplas variáveis com uma tabela de conversão de risco separada — que caracteriza a simplificação do YEARS frente a Wells e a Genebra (fonte: PMID 28549662, descrição do algoritmo).

### Por que isso reduz a necessidade de angioTC
Ao permitir um corte de D-dímero mais alto (1.000 ng/mL) exatamente nos pacientes sem nenhum item de suspeita clínica reforçada, o algoritmo evita encaminhar para angioTC pacientes de baixíssima probabilidade cujo D-dímero está discretamente elevado (entre 500 e 999 ng/mL) — faixa que, nos algoritmos de corte fixo, obrigaria seguir para exame de imagem mesmo com probabilidade clínica baixa. É esse mecanismo — permissividade maior do D-dímero justamente onde a probabilidade pré-teste é mais baixa — que produz a redução de exames relatada no estudo (ver abaixo), sem exigir mais uma etapa de cálculo de escore.

## Resultado do estudo de validação (números reais, PMID 28549662)
O estudo YEARS foi um estudo de manejo prospectivo, multicêntrico, conduzido em **12 hospitais na Holanda**, com **3.465 pacientes** consecutivos com suspeita clínica de TEP, entre outubro de 2013 e julho de 2015 (van der Hulle T et al., Lancet 2017;390(10091):289-297).

- TEP foi **excluído sem necessidade de angioTC** em pacientes com nenhum item do YEARS e D-dímero <1.000 ng/mL, ou com um ou mais itens e D-dímero <500 ng/mL.
- Entre os **2.946 pacientes** nos quais o TEP foi inicialmente excluído pelo algoritmo e que permaneceram sem anticoagulação, o seguimento de **3 meses** identificou tromboembolismo venoso sintomático em **18 pacientes — 0,61% (IC 95% 0,36-0,96%)**, incluindo **6 casos de TEP fatal**.
- A angioTC **não foi indicada em 1.651 (48%) dos 3.465 pacientes** usando o algoritmo YEARS, contra uma proporção estimada de **1.174 (34%)** que teria sido dispensada da angioTC caso a estratégia convencional (baseada em Wells) tivesse sido aplicada à mesma coorte — uma **redução absoluta de aproximadamente 14 pontos percentuais** no uso de angioTC, mantida de forma consistente entre subgrupos e faixas etárias.

Os autores concluíram que o TEP foi **excluído com segurança** pelo algoritmo YEARS, com redução substancial e clinicamente relevante do número de angioTC realizadas em comparação com a abordagem convencional.

## Comparação conceitual com Wells e Genebra
Os escores de Wells e de Genebra (revisado e simplificado, já cadastrados nesta pasta de Calculadoras) somam pontos de sete a mais itens clínicos, chegam a um escore numérico e então classificam o paciente em categorias de probabilidade (baixa/intermediária/alta, ou TEP improvável/provável), com o corte de D-dímero permanecendo **fixo** independentemente dessa categoria na maioria das implementações em uso corrente.

O YEARS inverte a lógica operacional: em vez de transformar itens clínicos em uma pontuação que por sua vez modula a interpretação de um D-dímero de corte único, o YEARS usa os itens clínicos diretamente para **escolher entre dois cortes de D-dímero pré-definidos**. Na prática de beira-leito, isso significa:

- **Menos itens para memorizar** — três perguntas binárias, sem necessidade de somar pontos nem consultar tabela de categorização de risco;
- **Uma única coleta de sangue e uma única decisão**, sem etapa intermediária de calcular e classificar um escore antes de interpretar o D-dímero;
- **O mesmo D-dímero já solicitado na rotina** é reaproveitado com dois pontos de corte possíveis, em vez de um escore clínico separado ser calculado antes.

Esta é uma leitura conceitual da diferença estrutural entre os algoritmos, não uma comparação estatística direta de acurácia entre YEARS e Wells/Genebra medida no mesmo estudo — **VERIFICAÇÃO HUMANA NECESSÁRIA** para qualquer afirmação de superioridade diagnóstica (sensibilidade/especificidade) do YEARS sobre Wells ou Genebra em comparação randomizada ou de acurácia cabeça a cabeça, que não foi verificada nesta sessão.

## Limitações e populações não representadas
- O estudo original **excluiu gestantes** — para essa população existe o algoritmo YEARS adaptado, com corte próprio, coberto em documento específico do tema Gravidez (ver acima).
- A coorte de validação foi conduzida em **hospitais holandeses**, com prevalência de TEP e organização de fluxo diagnóstico próprias daquele sistema de saúde; a generalização direta do desempenho numérico (taxa de falha de 0,61%) para outros contextos assistenciais não foi verificada nesta sessão — **VERIFICAÇÃO HUMANA NECESSÁRIA** para dados de validação externa em outras populações/países, se existirem.
- O terceiro item do algoritmo ("TEP é o diagnóstico mais provável") depende de **julgamento clínico subjetivo do médico assistente**, o mesmo tipo de variável que já é criticado nos escores de Wells e de Genebra por introduzir variabilidade entre observadores; o estudo original não relatou, no resumo consultado nesta sessão, uma medida de concordância interobservador para esse item — **VERIFICAÇÃO HUMANA NECESSÁRIA** se esse dado for necessário.
- Pacientes com D-dímero acima do corte aplicável, mesmo sem nenhum item do YEARS presente, ainda seguem para angioTC — o algoritmo reduz, mas não elimina, a necessidade de exame de imagem.
