---
title: "Algoritmo Multissensor de Descompensação (HeartLogic/MultiSENSE) e o Contraste com a Impedância Intratorácica Isolada (OptiVol/DOT-HF)"
slug: algoritmo-multissensor-heartlogic-multisense-e-o-contraste-com-optivol-dot-hf
theme: "Dispositivos"
kind: estudo
review_status: revisado
source_refs: ["Boehmer JP, Hariharan R, Devecchi FG, et al. A Multisensor Algorithm Predicts Heart Failure Events in Patients With Implanted Devices: Results From the MultiSENSE Study. JACC Heart Fail. 2017;5(3):216-225. DOI: 10.1016/j.jchf.2016.12.011. PMID: 28254128", "Gardner RS, Singh JP, Stancak B, et al. HeartLogic Multisensor Algorithm Identifies Patients During Periods of Significantly Increased Risk of Heart Failure Events: Results From the MultiSENSE Study. Circ Heart Fail. 2018;11(7):e004669. DOI: 10.1161/CIRCHEARTFAILURE.117.004669. PMID: 30002113. Correção publicada em Circ Heart Fail. 2018;11(8):e000029, PMID 30354568 — não lida nesta redação", "Hernandez AF, Albert NM, Allen LA, et al; MANAGE-HF Study. Multiple cArdiac seNsors for mAnaGEment of Heart Failure (MANAGE-HF) - Phase I Evaluation of the Integration and Safety of the HeartLogic Multisensor Algorithm in Patients With Heart Failure. J Card Fail. 2022;28(8):1245-1254. DOI: 10.1016/j.cardfail.2022.03.349. PMID: 35460884", "van Veldhuisen DJ, Braunschweig F, Conraads V, et al; DOT-HF Investigators. Intrathoracic impedance monitoring, audible patient alerts, and outcome in patients with heart failure. Circulation. 2011;124(16):1719-1726. DOI: 10.1161/CIRCULATIONAHA.111.043042. PMID: 21931078"]
legacy_source: "Documento novo — a biblioteca já tinha monitorização hemodinâmica implantável por sensor de pressão em artéria pulmonar (CHAMPION/GUIDE-HF), mas nenhum registro sobre os algoritmos multissensores embutidos no próprio CDI/CRT-D, que usam dados que o dispositivo já coleta em vez de um sensor implantado à parte."
---

# Algoritmo Multissensor de Descompensação (HeartLogic/MultiSENSE) e o Contraste com a Impedância Intratorácica Isolada (OptiVol/DOT-HF)

## Definicao
Diferente do sensor de pressão de artéria pulmonar (CardioMEMS, documento próprio nesta biblioteca), este é um **algoritmo de software** que roda dentro de um CDI ou CRT-D já implantado por outro motivo, combinando vários parâmetros que o próprio dispositivo mede continuamente — sons cardíacos, impedância intratorácica, frequência respiratória, frequência cardíaca noturna e nível de atividade física — num índice único, com o objetivo de sinalizar um período de risco aumentado de descompensação antes que o paciente procure atendimento. Não exige implante adicional nem procedimento novo: é reprogramação/leitura de um dispositivo que já está no paciente.

## MultiSENSE — desenvolvimento e validação do índice (Boehmer 2017)
Boehmer JP et al. JACC Heart Fail. 2017;5(3):216-225 (PMID 28254128). Estudo prospectivo, multicêntrico, com **900 pacientes** portadores de CRT-D, divididos em coorte de desenvolvimento (500 pacientes, usada para calibrar o algoritmo) e coorte de teste independente (400 pacientes, usada para validar o desempenho):
- **Dois desfechos coprimários pré-especificados, ambos atingidos** na coorte de teste: **sensibilidade de 70%** (IC95% 55,4%-82,1%) para detectar evento de insuficiência cardíaca (hospitalização ou visita não planejada tratada com diurético IV/aumento de dose), e **taxa de alerta não explicado de 1,47 por paciente-ano** (IC95% 1,32-1,65) — ou seja, quantas vezes por ano, em média, o dispositivo dispara alerta sem um evento clínico de IC associado
- **Tempo de antecedência (lead time)**: mediana de **34,0 dias** (intervalo interquartil 19,0-66,3 dias) entre o início do estado de alerta e o evento clínico de IC — é essa janela que sustenta a proposta de intervir antes da descompensação franca, não só documentá-la

## MultiSENSE — risco durante o estado de alerta e interação com NT-proBNP (Gardner 2018)
Gardner RS et al. Circ Heart Fail. 2018;11(7):e004669 (PMID 30002113), mesma coorte do MultiSENSE (900 pacientes), acompanhados por 1 ano, com **192 eventos de insuficiência cardíaca adjudicados de forma independente** (taxa média de 0,20 evento/paciente-ano no estudo todo):
- **Taxa de evento de IC dentro do estado de alerta foi 10 vezes maior que fora dele**: **0,80 vs. 0,08 evento/paciente-ano**
- **Combinando o alerta do dispositivo com NT-proBNP** (limiar de 1.000 pg/mL): o grupo de **menor risco** (NT-proBNP baixo, fora de alerta) teve **0,02 evento/paciente-ano**; o grupo de **maior risco** (NT-proBNP alto, dentro de alerta) teve **1,00 evento/paciente-ano** — uma diferença de **50 vezes** entre os extremos
- **Leitura correta do resultado**: isto é desempenho de **estratificação de risco em um intervalo de tempo**, não um ensaio que testou se agir sobre o alerta muda desfecho — nenhum dos dois estudos do MultiSENSE randomizou conduta clínica

## MANAGE-HF Fase I — segurança da integração clínica, ainda sem desfecho duro
Hernandez AF et al.; MANAGE-HF Study. J Card Fail. 2022;28(8):1245-1254 (PMID 35460884). Estudo de fase I, **sem grupo controle**, **200 pacientes** com FEVE <35%, NYHA II-III, evento de IC recente ou peptídeo natriurético elevado (BNP ≥150 pg/mL ou NT-proBNP ≥600 pg/mL), todos com dispositivo implantado e o algoritmo ativo:
- **585 episódios de alerta registrados** (1,76 por paciente-ano); em **74% dos alertas** houve intensificação da medicação de IC pela equipe assistente
- **NT-proBNP mediano caiu de 1.316 para 743 pg/mL em 12 meses** (p<0,001) — mudança de biomarcador, não desfecho clínico duro
- **Segurança**: 5 eventos adversos sérios relacionados (0,015 por paciente-ano)
- **O que este estudo prova e o que não prova**: demonstra que integrar o alerta à rotina assistencial é seguro e leva a ação terapêutica na maioria das vezes — **não** é um ensaio randomizado de desfecho, e os autores o descrevem como preparatório para um estudo maior, ainda não publicado com resultado de eficácia

## Contraste — OptiVol isolado e o ensaio DOT-HF, resultado oposto ao esperado
**A impedância intratorácica sozinha, com alerta audível direto ao paciente, já foi testada em desenho randomizado — e não funcionou.** van Veldhuisen DJ et al.; DOT-HF Investigators. Circulation. 2011;124(16):1719-1726 (PMID 21931078). Ensaio randomizado, **335 pacientes** com IC e dispositivo com monitorização de impedância intratorácica (OptiVol, Medtronic — sem os outros sensores do HeartLogic), randomizados para alerta audível ativado (grupo "acesso") vs. impedância monitorada de forma cega, sem alerta (controle), seguimento médio de 14,9 ± 5,4 meses:
- **Desfecho primário** (morte por qualquer causa ou hospitalização por IC): ocorreu em **48 pacientes (29%) no grupo com alerta vs. 33 pacientes (20%) no controle** (HR 1,52; IC95% 0,97-2,37; p=0,063) — tendência **na direção de pior desfecho** com o alerta ativado, sem atingir significância estatística
- **Hospitalização por IC isoladamente, maior e estatisticamente significativa no grupo com alerta**: HR 1,79; IC95% 1,08-2,95; p=0,022
- **Mortalidade**: sem diferença (19 vs. 15 óbitos; p=0,54)
- **Consultas ambulatoriais não programadas, muito mais frequentes no grupo com alerta**: 250 vs. 84 (p<0,0001)
- **Conclusão textual dos autores**: o uso da ferramenta de impedância intratorácica com alerta audível **"não melhorou o desfecho e aumentou hospitalizações por insuficiência cardíaca e visitas ambulatoriais"**

## Sintese pratica
O MultiSENSE mostrou que um índice que combina cinco parâmetros — não a impedância isolada — discrimina bem períodos de risco aumentado (sensibilidade de 70%, razão de 10 a 50 vezes na taxa de evento dentro vs. fora do estado de alerta), com antecedência mediana de mais de um mês. O MANAGE-HF Fase I mostrou que agir sobre esse alerta na prática clínica é seguro e leva a intensificação terapêutica na maioria dos casos, com queda de NT-proBNP. **Nenhum desses estudos, porém, é um ensaio randomizado que provou redução de hospitalização ou morte por agir sobre o alerta multissensor** — essa é a lacuna que ainda separa "índice discrimina risco" de "índice muda desfecho". E o precedente mais próximo de um teste randomizado dessa ideia, o DOT-HF com a impedância intratorácica isolada, foi **neutro para o desfecho composto e pior para hospitalização por IC**, com aumento relevante de consultas não programadas — o oposto do que a lógica do dispositivo prometia.

## Armadilhas clinicas
- Tratar o desempenho de estratificação de risco do MultiSENSE (sensibilidade, razão de taxas dentro/fora de alerta) como se fosse prova de benefício clínico — os dois artigos do MultiSENSE (Boehmer 2017 e Gardner 2018) são estudos de desempenho diagnóstico, não ensaios de desfecho
- Extrapolar o resultado neutro/negativo do DOT-HF (impedância intratorácica isolada, com alerta audível direto ao paciente) para o HeartLogic — são tecnologias diferentes: o HeartLogic combina cinco sensores e o alerta vai para a equipe assistente rever o paciente, não um alerta sonoro direto ao paciente como no DOT-HF
- Citar o MANAGE-HF Fase I como se já fosse a prova de eficácia que falta — é estudo de segurança e viabilidade, sem grupo controle, explicitamente preparatório para um estudo maior
- Ignorar que o DOT-HF teve um sinal de **dano** (mais hospitalização por IC no grupo com alerta) que os próprios autores atribuem, em parte, a mais visitas e possivelmente a intervenção precoce excessiva ou ansiedade do paciente — não é um "estudo neutro" simples, é um resultado que pesou contra a intervenção testada
- Confundir o limiar de NT-proBNP usado na sub-análise de Gardner 2018 (1.000 pg/mL, para estratificar risco combinado com o estado de alerta) com um valor de corte diagnóstico geral de insuficiência cardíaca
