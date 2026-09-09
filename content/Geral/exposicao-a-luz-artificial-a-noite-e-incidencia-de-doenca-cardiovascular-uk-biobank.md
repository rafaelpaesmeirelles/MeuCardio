---
title: "Exposição a Luz Artificial à Noite e Incidência de Doença Cardiovascular: Coorte do UK Biobank"
slug: exposicao-a-luz-artificial-a-noite-e-incidencia-de-doenca-cardiovascular-uk-biobank
theme: "Geral"
kind: estudo
review_status: revisado
source_refs: ["Windred DP, Burns AC, Rutter MK, Lane JM, Saxena R, Scheer FAJL, Cain SW, Phillips AJK. Light Exposure at Night and Cardiovascular Disease Incidence. JAMA Netw Open. 2025;8(10):e2539031. DOI: 10.1001/jamanetworkopen.2025.39031. PMID: 41129148. PMCID: PMC12550636 — coorte prospectiva UK Biobank, luz medida por sensor de pulso em ~89.000 participantes, seguimento de 9,5 anos"]
legacy_source: "Documento novo, escrito em 09/09/2026. A pasta Geral já cobre REGULARIDADE do sono (índice SRI, Chaput et al. 2025) e desssincronização circadiana por trabalho em turnos, mas nenhum documento tratava da exposição a LUZ à noite como fator de risco cardiovascular medido objetivamente por dispositivo — exposição ambiental distinta (não é sobre horário nem duração do sono, é sobre quanta luz incide sobre a pessoa enquanto ela dorme ou deveria dormir), com mecanismo próprio (supressão de melatonina e dessincronização circadiana induzida por luz, não pelo padrão de sono em si) e publicação pivotal muito recente (JAMA Network Open, out/2025) ainda sem registro nesta biblioteca."
---

# Exposição a Luz Artificial à Noite e Incidência de Doença Cardiovascular: Coorte do UK Biobank

## Definição
Um novo fator de risco cardiovascular ambiental e modificável: não o horário em que a pessoa dorme, nem por quantas horas, mas **quanta luz incide sobre ela durante a noite**, medida objetivamente por sensor de pulso — distinto da regularidade do sono (já documentada nesta pasta pelo índice SRI de Chaput et al.) e da duração do sono (metanálise de Cappuccio), e mecanisticamente ligado à dessincronização circadiana também descrita nos documentos sobre trabalho em turnos.

## O estudo
Windred DP et al. (JAMA Netw Open. 2025;8(10):e2539031, PMID 41129148, acesso aberto, PMCID PMC12550636). Coorte prospectiva de participantes do UK Biobank que usaram sensor de luz de pulso (Axivity AX3) por 1 semana entre 2013 e 2016, com desfechos cardiovasculares seguidos até novembro de 2022.

- **88.905 participantes** livres de cada desfecho cardiovascular no momento da medição de luz; idade média **62,4 anos (DP 7,8)**; **56,9% mulheres**; **97,0% brancos** (a própria coorte reconhece baixa diversidade étnica)
- **~13 milhões de horas** de dados de exposição à luz, separados por análise fatorial não supervisionada em dois clusters temporais: **dia** (07h30-20h30) e **noite** (00h30-06h00)
- Exposição categorizada em **percentis** de luz noturna e diurna: 0-50 (grupo de referência, "noites escuras"), 51-70, 71-90 e 91-100 (as noites mais claras)
- **Mediana de luz no grupo de referência (0-50)**: 0,62 lux; **no grupo mais exposto (91-100)**: 426,48 lux — diferença de mais de 600 vezes na intensidade de luz noturna entre os extremos
- **Desfechos**: incidência de doença arterial coronariana, infarto do miocárdio, insuficiência cardíaca, fibrilação atrial e AVC, definidos por registros de internação, atenção primária, autorrelato e registro de óbito (CID-9/CID-10)
- **Seguimento médio: 7,9 anos (DP 1,0)**
- Três modelos de Cox progressivamente ajustados: Modelo 1 (idade, sexo, etnia, fotoperíodo); Modelo 2 (+ escolaridade, emprego, renda, privação material); Modelo 3 (+ atividade física, tabagismo, álcool, dieta, urbanicidade) — além de análises adicionais de interação com idade, sexo e escore de risco poligênico

## Resultados (Modelo 3, totalmente ajustado — noite mais clara [91-100] vs. noite mais escura [0-50])
- **Doença arterial coronariana**: HR 1,23 (IC95% 1,10-1,38)
- **Infarto do miocárdio**: HR 1,42 (IC95% 1,21-1,66)
- **Insuficiência cardíaca**: HR 1,45 (IC95% 1,24-1,69)
- **Fibrilação atrial**: HR 1,28 (IC95% 1,15-1,43)
- **AVC**: HR 1,28 (IC95% 1,06-1,55)
- **Relação dose-resposta**: associação log-linear significativa para todos os cinco desfechos por desvio-padrão de aumento na luz noturna (ex.: insuficiência cardíaca HR 1,08, IC95% 1,05-1,11, por DP de luz noturna) — o risco cresce de forma gradual com a intensidade da luz, não é um efeito de limiar
- **Robustez**: as associações da luz noturna se mantiveram estatisticamente significativas e de magnitude semelhante do Modelo 1 ao Modelo 3, isto é, **não foram atenuadas** por ajuste para atividade física, tabagismo, álcool, dieta, duração e eficiência do sono, turno de trabalho, diabetes, hipertensão, IMC elevado ou colesterol — nenhuma dessas variáveis explicou a associação
- **Luz diurna**: em contraste, as associações (algumas delas na direção de menor risco de insuficiência cardíaca e AVC) observadas nos modelos 1 e 2 **perderam significância estatística no Modelo 3** totalmente ajustado (ex.: insuficiência cardíaca no grupo de luz diurna mais alta: HR 0,93, IC95% 0,77-1,13, p=0,48) — ao contrário da luz noturna, o sinal da luz diurna não é robusto ao ajuste completo
- **Interação por sexo**: associação de luz noturna com maior magnitude em **mulheres** para insuficiência cardíaca (p de interação=0,006) e doença arterial coronariana (p de interação=0,02)
- **Interação por idade**: associação de maior magnitude em **indivíduos mais jovens** da coorte para insuficiência cardíaca (p de interação=0,04) e fibrilação atrial (p de interação=0,02)
- **Risco poligênico**: análises de interação com escore de risco poligênico foram realizadas (restritas a ancestralidade europeia); os autores relatam resultados detalhados no artigo completo — **VERIFICAÇÃO HUMANA NECESSÁRIA** para a direção e magnitude exata dessa interação especificamente, não reproduzida em detalhe no resumo estruturado nem na porção do texto completo aqui consultada

## Conclusão do próprio estudo
**"Neste estudo de coorte, a exposição à luz noturna foi um fator de risco significativo para o desenvolvimento de doenças cardiovasculares em adultos com mais de 40 anos. Esses achados sugerem que, além das medidas preventivas atuais, evitar luz à noite pode ser uma estratégia útil para reduzir o risco de doenças cardiovasculares."**

## Por que isso importa na prática
O achado central é que **luz ambiente à noite — não o padrão de sono em si, e sim quanta luz atinge a pessoa enquanto deveria estar dormindo — é um fator de risco cardiovascular independente**, com relação dose-resposta e robusto a ajuste extenso para os principais confundidores comportamentais e metabólicos conhecidos. Isso amplia a orientação de higiene do sono cardiovascular: além de perguntar sobre duração e regularidade do sono (ver documentos relacionados nesta pasta), há razão baseada em evidência para orientar **redução de exposição à luz durante a noite** — cortinas blackout, remoção de telas e luzes de aparelhos do quarto, evitar dormir com luz artificial acesa — como medida adicional, de baixo custo e sem contraindicação conhecida, especialmente em pacientes com risco cardiovascular já elevado.

## Limitações, declaradas com honestidade
- **Desenho observacional**: não estabelece causalidade. É biologicamente plausível (supressão de melatonina, dessincronização circadiana já demonstrada em modelos experimentais e animais, conforme citado na introdução do próprio artigo), mas causalidade reversa (doença subclínica alterando padrão de exposição à luz) e confusão residual não podem ser excluídas
- **Luz medida por apenas 1 semana** no início do seguimento (2013-2016) — não captura mudança de exposição ao longo dos quase 8 anos de acompanhamento subsequente
- **Coorte do UK Biobank**: 97,0% de participantes brancos, população mais saudável que a população geral do Reino Unido (viés de participação voluntária já conhecido desta coorte) — limita generalização para populações mais diversas
- **Faixa etária estudada**: 43,5-79,0 anos no momento da medição de luz — não informa sobre a mesma associação em adultos mais jovens
- **Sensor de pulso mede luz ambiente, não necessariamente exposição à retina** (pode não refletir com precisão a luz recebida pelos olhos, especialmente se o participante dorme com o braço coberto) — limitação técnica reconhecida do método
- **Mecanismo não testado diretamente neste estudo**: a plausibilidade biológica (melatonina, dessincronização circadiana) vem de estudos experimentais prévios citados pelos autores, não de dosagem hormonal ou desfecho intermediário medido nesta própria coorte

## Tudo com Tudo

- [Regularidade do Sono (Não Só a Duração) e Eventos Cardiovasculares Maiores: o Índice SRI no UK Biobank](/biblioteca/regularidade-do-sono-e-eventos-cardiovasculares-maiores-indice-sri-no-uk-biobank)
- [Duração do Sono Curta e Longa Como Preditor Cardiovascular: a Metanálise de Cappuccio](/biblioteca/duracao-do-sono-curta-e-longa-como-preditor-cardiovascular-metanalise-de-cappuccio)
- [Trabalho em Turnos Noturnos/Rotativos: Mecanismo de Dessincronização Circadiana e Risco Cardiovascular](/biblioteca/trabalho-em-turnos-noturnos-mecanismo-de-dessincronizacao-circadiana-e-risco-cardiovascular)
- [Trabalho em Turno Noturno Rotativo e Risco Coronariano: Nurses' Health Study](/biblioteca/trabalho-em-turno-noturno-rotativo-e-risco-coronariano-nurses-health-study)
- [Mudança Sazonal de Horário (Horário de Verão) e Risco Cardiovascular](/biblioteca/mudanca-sazonal-de-horario-horario-de-verao-e-risco-cardiovascular)
- [Ruído de Transporte Urbano e Aeroportuário como Fator de Risco Cardiovascular](/biblioteca/ruido-de-transporte-urbano-e-aeroportuario-como-fator-de-risco-cardiovascular)
- [Life's Essential 8: o Novo Construto de Saúde Cardiovascular da AHA](/biblioteca/lifes-essential-8-o-novo-construto-de-saude-cardiovascular-da-aha)

## Armadilhas clínicas
- **Confundir este achado com os documentos sobre regularidade (SRI) ou duração do sono** — são coortes e exposições diferentes; aqui o fator de risco é a intensidade de luz noturna medida objetivamente, não o horário nem a duração do sono
- **Tratar como prova de causalidade** — é coorte observacional; embora robusta a ajuste extenso, não substitui ensaio de intervenção
- **Extrapolar para adultos jovens (<40 anos)** — a coorte foi medida entre 43,5 e 79,0 anos
- **Ignorar o achado de que a luz diurna não teve sinal robusto no modelo totalmente ajustado**, ao contrário da luz noturna — a mensagem prática do estudo é especificamente sobre exposição à luz **à noite**, não sobre luz em geral
- **Recomendar blackout total como se fosse intervenção validada por ensaio clínico** — a orientação de reduzir luz noturna é razoável e de baixo risco à luz da plausibilidade biológica e da robustez estatística deste estudo, mas não foi testada como intervenção neste próprio artigo (que é observacional, não um ensaio de blackout vs. exposição usual)
