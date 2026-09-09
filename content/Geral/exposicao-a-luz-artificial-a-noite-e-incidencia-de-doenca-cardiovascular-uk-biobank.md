---
kind: estudo
legacy_source: Documento novo, escrito em 09/09/2026. A pasta Geral já cobre REGULARIDADE
  do sono (índice SRI, Chaput et al. 2025) e desssincronização circadiana por trabalho
  em turnos, mas nenhum documento tratava da exposição a LUZ à noite como fator de
  risco cardiovascular medido objetivamente por dispositivo — exposição ambiental
  distinta (não é sobre horário nem duração do sono, é sobre quanta luz incide sobre
  a pessoa enquanto ela dorme ou deveria dormir), com mecanismo próprio (supressão
  de melatonina e dessincronização circadiana induzida por luz, não pelo padrão de
  sono em si) e publicação pivotal muito recente (JAMA Network Open, out/2025) ainda
  sem registro nesta biblioteca.
published: true
review_note: 'Texto completo e tabelas conferidos: mediana noturna máxima 105,30 e
  não 426,48 lux; corrigidos unidade log, atenuação/AVC não significativo nos ajustes,
  interação genética e causalidade.'
review_status: revisado
slug: exposicao-a-luz-artificial-a-noite-e-incidencia-de-doenca-cardiovascular-uk-biobank
source_refs:
- 'Windred DP, Burns AC, Rutter MK, Lane JM, Saxena R, Scheer FAJL, Cain SW, Phillips
  AJK. Light Exposure at Night and Cardiovascular Disease Incidence. JAMA Netw Open.
  2025;8(10):e2539031. DOI: 10.1001/jamanetworkopen.2025.39031. PMID: 41129148. PMCID:
  PMC12550636 — coorte prospectiva UK Biobank, luz medida por sensor de pulso em ~89.000
  participantes, seguimento de 9,5 anos'
theme: Geral
title: 'Exposição a Luz Artificial à Noite e Incidência de Doença Cardiovascular:
  Coorte do UK Biobank'
---

# Exposição a Luz Artificial à Noite e Incidência de Doença Cardiovascular: Coorte do UK Biobank

## Definição

Estudo observacional da associação entre exposição noturna à luz medida no pulso e incidência de doenças cardiovasculares. A exposição pode relacionar-se a sono, atividade e ritmo circadiano; seu ajuste estatístico não estabelece independência causal nem benefício de reduzir luz sobre eventos clínicos.

## O estudo
Windred DP et al. (JAMA Netw Open. 2025;8(10):e2539031, PMID 41129148, acesso aberto, PMCID PMC12550636). Coorte prospectiva de participantes do UK Biobank que usaram sensor de luz de pulso (Axivity AX3) por 1 semana entre 2013 e 2016, com desfechos cardiovasculares seguidos até novembro de 2022.

- **88.905 participantes** livres de cada desfecho cardiovascular no momento da medição de luz; idade média **62,4 anos (DP 7,8)**; **56,9% mulheres**; **97,0% brancos** (a própria coorte reconhece baixa diversidade étnica)
- **~13 milhões de horas** de dados de exposição à luz, separados por análise fatorial não supervisionada em dois clusters temporais: **dia** (07h30-20h30) e **noite** (00h30-06h00)
- Exposição categorizada em **percentis** de luz noturna e diurna: 0-50 (grupo de referência, "noites escuras"), 51-70, 71-90 e 91-100 (as noites mais claras)
- **Mediana de luz no grupo de referência (0-50)**: 0,62 lux; **no grupo mais exposto (91-100)**: 105,30 lux — diferença de aproximadamente 170 vezes na intensidade de luz noturna entre os extremos
- **Desfechos**: incidência de doença arterial coronariana, infarto do miocárdio, insuficiência cardíaca, fibrilação atrial e AVC, definidos por registros de internação, atenção primária, autorrelato e registro de óbito (CID-9/CID-10)
- **Seguimento médio: 7,9 anos (DP 1,0)**
- Três modelos de Cox progressivamente ajustados: Modelo 1 (idade, sexo, etnia, fotoperíodo); Modelo 2 (+ escolaridade, emprego, renda, privação material); Modelo 3 (+ atividade física, tabagismo, álcool, dieta, urbanicidade) — além de análises adicionais de interação com idade, sexo e escore de risco poligênico

## Resultados (Modelo 3, totalmente ajustado — noite mais clara [91-100] vs. noite mais escura [0-50])
- **Doença arterial coronariana**: HR 1,23 (IC95% 1,10-1,38)
- **Infarto do miocárdio**: HR 1,42 (IC95% 1,21-1,66)
- **Insuficiência cardíaca**: HR 1,45 (IC95% 1,24-1,69)
- **Fibrilação atrial**: HR 1,28 (IC95% 1,15-1,43)
- **AVC**: HR 1,28 (IC95% 1,06-1,55)
- **Modelo de exposição contínua:** associações foram avaliadas com luz noturna transformada em log. Os HRs da luz são por unidade dessa transformação, não por desvio-padrão de lux; uma forma log-linear assumida no modelo não demonstra ausência de limiar biológico.
- **Ajustes adicionais:** houve atenuação das associações. Em análises separadas, a associação com AVC deixou de atingir significância após ajuste para sono curto e para razão de colesterol elevada. Essas variáveis não foram todas incluídas simultaneamente no Modelo 3; confundimento residual continua possível.
- **Luz diurna**: em contraste, as associações (algumas delas na direção de menor risco de insuficiência cardíaca e AVC) observadas nos modelos 1 e 2 **perderam significância estatística no Modelo 3** totalmente ajustado (ex.: insuficiência cardíaca no grupo de luz diurna mais alta: HR 0,93, IC95% 0,77-1,13, p=0,48) — ao contrário da luz noturna, o sinal da luz diurna não é robusto ao ajuste completo
- **Interação por sexo**: associação de luz noturna com maior magnitude em **mulheres** para insuficiência cardíaca (p de interação=0,006) e doença arterial coronariana (p de interação=0,02)
- **Interação por idade**: associação de maior magnitude em **indivíduos mais jovens** da coorte para insuficiência cardíaca (p de interação=0,04) e fibrilação atrial (p de interação=0,02)
- **Risco poligênico:** o texto completo relata ausência de interação estatisticamente significativa entre exposição noturna e os escores para os desfechos avaliados. As análises genéticas restringiram-se à ancestralidade europeia; ausência de interação detectada não demonstra efeito idêntico em toda população.

## Conclusão do próprio estudo

Os autores sugerem investigar a redução da luz noturna como estratégia adicional de prevenção. Trata-se de uma interpretação de associação de coorte; o estudo não randomizou redução de luz nem demonstrou que essa intervenção reduza eventos.

## Por que isso importa na prática

O histórico de sono e exposição ambiental pode enriquecer a avaliação clínica. Evitar luz desnecessária durante o sono é uma medida de conforto e higiene do sono a individualizar, mantendo iluminação necessária para segurança e mobilidade. **Não há neste estudo ensaio de blackout, retirada de telas ou redução de iluminação demonstrando prevenção de infarto, AVC ou insuficiência cardíaca.** As medidas não substituem prevenção cardiovascular estabelecida.

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
