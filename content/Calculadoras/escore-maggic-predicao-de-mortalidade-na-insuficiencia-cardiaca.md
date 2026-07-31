---
title: "Escore MAGGIC: Predição de Mortalidade na Insuficiência Cardíaca (FE Reduzida e Preservada)"
slug: escore-maggic-predicao-de-mortalidade-na-insuficiencia-cardiaca
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Pocock SJ, Ariti CA, McMurray JJ, Maggioni A, Køber L, Squire IB, Swedberg K, Dobson J, et al; Meta-Analysis Global Group in Chronic Heart Failure (MAGGIC). Predicting survival in heart failure: a risk score based on 39 372 patients from 30 studies. Eur Heart J. 2013;34(19):1404-1413. DOI: 10.1093/eurheartj/ehs337. PMID: 23095984"]
legacy_source: "Documento novo, escrito em 31/07/2026. O tema Calculadoras já tinha o Seattle Heart Failure Model e o escore GWTG-HF, mas não o MAGGIC — que é o único dos três derivado de uma metanálise de dados individuais cobrindo tanto fração de ejeção reduzida quanto preservada, e o mais usado em publicação contemporânea de insuficiência cardíaca crônica."
---

# Escore MAGGIC: Predição de Mortalidade na Insuficiência Cardíaca

## O que e
Escore de risco de mortalidade em insuficiência cardíaca, derivado do **Meta-Analysis Global Group in Chronic Heart Failure (MAGGIC)**. Sua característica distintiva é a base: **metanálise de dados individuais de 39.372 pacientes, de 30 coortes** — seis delas ensaios clínicos —, cobrindo **tanto fração de ejeção reduzida quanto preservada**.

Referência: Pocock SJ et al., Eur Heart J. 2013;34(19):1404-1413 (PMID 23095984).

## Como foi derivado
- **39.372 pacientes** com insuficiência cardíaca, de 30 estudos de coorte
- **40,2% morreram** durante seguimento **mediano de 2,5 anos**
- Método: regressão de Poisson multivariável por partes (*piecewise*), com seleção passo a passo de variáveis
- Resultado convertido em **escore inteiro**, de uso simples

## As 13 variaveis, na ordem de forca preditiva
A ordem abaixo é a do próprio artigo — da mais preditiva para a menos:

1. **Idade**
2. **Fração de ejeção mais baixa**
3. **Classe funcional NYHA**
4. **Creatinina sérica**
5. **Diabetes**
6. **Não estar em uso de betabloqueador**
7. **Pressão arterial sistólica mais baixa**
8. **Massa corporal mais baixa**
9. **Tempo desde o diagnóstico**
10. **Tabagismo atual**
11. **Doença pulmonar obstrutiva crônica**
12. **Sexo masculino**
13. **Não estar em uso de inibidor da ECA ou bloqueador do receptor de angiotensina**

**Duas dessas variáveis são de tratamento, não de doença** — não usar betabloqueador e não usar IECA/BRA. Elas capturam, ao mesmo tempo, ausência de terapia com benefício comprovado e a gravidade que motivou a não prescrição (hipotensão, disfunção renal, intolerância). **O escore não deve ser lido como se prescrever o fármaco convertesse mecanicamente o risco predito no risco menor.**

## Diferenca entre fe reduzida e preservada
O artigo registra que, na **fração de ejeção preservada**, a **idade foi mais preditiva** e a **pressão sistólica menos preditiva** de mortalidade do que na fração de ejeção reduzida. É o motivo de o escore ser aplicável aos dois fenótipos sem precisar de modelo separado — mas também um lembrete de que os pesos não são idênticos entre eles.

## Gradiente de risco que o escore separa
A conversão em escore inteiro identificou **um gradiente muito acentuado**: mortalidade em 3 anos de **10% no quintil inferior de risco** e de **70% no decil superior**. É essa amplitude que torna o escore útil para conversa de prognóstico e para seleção de paciente em ensaio clínico.

## Calculadora publicada pelos autores
Os autores disponibilizaram o escore em `www.heartfailurerisk.org`, citado no próprio artigo como a via de uso clínico. **Confira a disponibilidade do site antes de indicá-lo ao paciente ou à equipe** — este documento não verificou se ele segue no ar em 2026.

## Como escolher entre os escores de ic desta pasta
- **MAGGIC** — insuficiência cardíaca **crônica**, ambulatorial, **FE reduzida ou preservada**. Base de metanálise multinacional, 13 variáveis clínicas simples
- **Seattle Heart Failure Model** — predição de sobrevida na IC crônica, com modelagem do efeito de intervenções; ver `seattle-heart-failure-model-predicao-de-sobrevida-na-ic.md`
- **GWTG-HF** — **mortalidade intra-hospitalar** na IC **aguda** descompensada, cenário e horizonte diferentes; ver `escore-gwtg-hf-mortalidade-intra-hospitalar-na-insuficiencia-cardiaca-aguda.md`

Trocar um pelo outro sem notar a diferença de cenário (crônico vs. agudo) e de horizonte (anos vs. internação) é o erro mais comum com esses três.

## Armadilhas clinicas
- **Usar o MAGGIC para decidir conduta individual como se fosse determinístico** — é estimativa populacional de risco; o gradiente é acentuado, mas o intervalo em torno de cada paciente não é estreito
- **Ler as variáveis de tratamento como alavancas** — "não usar betabloqueador" pontua também porque marca quem não tolera o fármaco
- **Aplicar o escore à insuficiência cardíaca aguda** — a coorte é de IC crônica, com seguimento mediano de 2,5 anos
- **Ignorar que os pesos diferem entre FE preservada e reduzida** — idade pesa mais, e pressão sistólica menos, na preservada
- **Supor que o escore incorpora terapias modernas** — a derivação é de coortes anteriores a 2013, e não contempla o efeito de classes incorporadas depois (inibidores de SGLT2, sacubitril-valsartana), o que tende a **superestimar** a mortalidade de um paciente tratado hoje com terapia otimizada completa
