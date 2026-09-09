---
title: "Duração da Hipotermia Terapêutica Pós-Parada Cardiorrespiratória: o Ensaio ICECAP (JAMA 2026)"
slug: duracao-da-hipotermia-terapeutica-pos-parada-cardiorrespiratoria-o-ensaio-icecap
theme: "Terapia intensiva"
kind: estudo
review_status: revisado
source_refs: ["Meurer WJ, Yeatts SD, Geocadin RG, Roy A, Callaway CW, Ramakrishnan V, Berry SM, Caveney AF, Meyer S, Bozeman N, Harney DM, Speers M, Stevenson VLW, Sozener CB, Daya MR, Beiser DG, Elmer J, Khan IR, Hirsch KG, Kilgannon JH, Nassal M, Johnson NJ, Beekman R, May TL, Brown J, Silbergleit R; SIREN Investigators. Duration of Therapeutic Hypothermia After Out-of-Hospital Cardiac Arrest: The ICECAP Randomized Clinical Trial. JAMA. 2026 Aug 5:e2610247. DOI: 10.1001/jama.2026.10247. PMID: 42554995. PMCID: PMC13445112. Trial registration: ClinicalTrials.gov NCT04217551."]
legacy_source: "Documento novo, escrito em 09/09/2026. Verificado por grep em toda a pasta content/Terapia_intensiva/ (termos 'duracao', 'ICECAP', 'resfriamento', 'cooling'): os documentos existentes sobre pós-parada (TTM/TTM2, evolução histórica, HYPERION, BOX, cuidados pós-parada AHA 2025, neuroprognóstico) tratam da meta de temperatura (33°C vs. 36°C/normotermia) ou de subgrupo por ritmo, mas nenhum trata da pergunta que o ICECAP responde: uma vez decidido usar hipotermia a 33°C, por quanto tempo mantê-la. Abstract completo lido verbatim via efetch do PubMed nesta sessão (PMID 42554995) antes da redação; nenhum número foi escrito de memória."
---

# Duração da Hipotermia Terapêutica Pós-Parada Cardiorrespiratória: o Ensaio ICECAP (JAMA 2026)

## Definicao
Os documentos já existentes nesta biblioteca sobre controle de temperatura pós-parada (`controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2.md`, `evolucao-historica-do-controle-de-temperatura-pos-parada-de-haca-bernard-2002-ao-ttm2.md`, `hipotermia-terapeutica-em-ritmo-nao-chocavel-pos-parada-o-ensaio-hyperion.md`) respondem "hipotermia a 33°C ou normotermia com controle de febre" (TTM2) e "hipotermia funciona também em ritmo não chocável" (HYPERION). Nenhum deles responde a uma pergunta operacional distinta e não trivial: uma vez que a equipe decidiu induzir hipotermia a 33°C, **por quanto tempo mantê-la**? Na prática clínica e nos protocolos anteriores ao ICECAP, essa duração variava amplamente (24 a 48 horas, sem base randomizada firme). O ICECAP é o primeiro ensaio randomizado desenhado especificamente para responder a essa pergunta de duração, com desenho bayesiano adaptativo.

## O ensaio ICECAP (Meurer, JAMA 2026)
Meurer WJ et al.; SIREN Investigators. JAMA. 2026 Aug 5:e2610247 (PMID 42554995; PMCID PMC13445112; NCT04217551). Ensaio multicêntrico, randomizado, de alocação adaptativa, conduzido em **71 hospitais dos Estados Unidos**, com pacientes recrutados entre **junho de 2020 e junho de 2025**.

**População**: adultos com parada cardiorrespiratória extra-hospitalar (PCR-EH) que permaneceram inconscientes, atingiram temperatura-alvo abaixo de 34°C dentro de 4 horas da parada, e já tinham dispositivo definitivo de controle de temperatura iniciado.

**Intervenção**: hipotermia terapêutica a **33°C** para todos os pacientes — o que varia entre os grupos é **apenas a duração** da hipotermia, com alocação randomizada adaptativa entre **6, 12, 18, 24, 30, 36, 42, 48, 60 e 72 horas**. Os primeiros 200 pacientes foram randomizados nas durações de 12, 24 e 48 horas, em proporção 1:1:1; a partir daí, um algoritmo de randomização adaptativa por resposta passou a alocar preferencialmente para os grupos com maior probabilidade de serem ótimos, informando a curva de duração-resposta separadamente para cada tipo de ritmo inicial (chocável vs. não chocável).

**Desfecho primário**: função neurológica em 90 dias, medida por escore ponderado da escala de Rankin modificada, analisado por modelo bayesiano de duração-resposta. A análise primária estimou a probabilidade posterior de cada duração ser "ótima" — definida como a duração mais curta compatível com o melhor desfecho observado em qualquer duração testada.

**Resultados**:
- **1.158 pacientes randomizados** (883 com ritmo não chocável, 275 com ritmo chocável); idade mediana de 61 anos (IQR 50-70), **39,6% mulheres**
- O ensaio atingiu uma **regra de interrupção pré-especificada na análise interina**
- No **coorte de ritmo não chocável**: a probabilidade posterior de que **6 horas** fosse a duração mais curta que atingia o escore médio ponderado máximo de Rankin modificado foi de **0,51**
- Resultados **semelhantes no coorte de ritmo chocável**
- **Nenhuma diferença** foi observada nos desfechos secundários ou na mortalidade entre as diferentes durações de resfriamento

## Conclusao do proprio ensaio
**"Entre sobreviventes comatosos de parada cardiorrespiratória extra-hospitalar tratados com hipotermia terapêutica a 33°C, aumentar a duração do resfriamento não melhorou os desfechos neurológicos."**

## Sintese pratica
O ICECAP não questiona se hipotermia a 33°C deve ou não ser usada — essa é a pergunta do TTM2, já registrada nesta biblioteca, e o ICECAP manteve 33°C como base fixa para **todos** os braços. A pergunta respondida aqui é mais estreita e mais aplicável ao dia a dia da UTI: **uma vez optado por hipotermia a 33°C, mais tempo de resfriamento (até 72 horas) não é melhor do que menos tempo (a partir de 6 horas)**. A probabilidade posterior de 0,51 para a duração de 6 horas no coorte não chocável é o achado central, mas é uma probabilidade discreta — não um resultado esmagador — e o desenho bayesiano adaptativo não gera o mesmo tipo de intervalo de confiança frequentista que os outros ensaios desta biblioteca (TTM, TTM2, BOX). Combinado ao TTM2 (hipotermia não superou normotermia com controle rigoroso de febre) e ao BOX (metas mais agressivas de PAM/oxigenação não mudaram desfecho), o ICECAP reforça o mesmo padrão já documentado nesta pasta para o período pós-parada: escalonar a intensidade ou a duração de uma intervenção, além de um patamar mínimo razoável, não demonstrou benefício adicional em ensaio randomizado.

## Armadilhas clinicas
- **Não confundir o ICECAP com um ensaio de "hipotermia vs. normotermia"** — todos os braços receberam hipotermia a 33°C; a única variável testada foi a duração. Quem procura o resultado sobre "vale a pena resfriar" deve continuar consultando o documento de TTM/TTM2 desta biblioteca, não este.
- **Não tratar a probabilidade posterior de 0,51 (coorte não chocável) como certeza estatística** — é uma estimativa bayesiana de que 6 horas é a duração mais curta compatível com o melhor desfecho, não uma prova de superioridade de 6 horas sobre as demais durações testadas.
- **Não extrapolar a duração de 6 horas como nova prática padrão automática** — o próprio resultado mostra ausência de diferença de desfecho entre as durações testadas (6 a 72 horas), o que sustenta usar durações mais curtas por não haver prejuízo demonstrado e por reduzir a exposição a complicações da hipotermia prolongada (arritmia, coagulopatia, infecção) — mas o ensaio não teve poder desenhado para provar que 6 horas é superior às demais, apenas que não é inferior.
- **Não aplicar este resultado a parada intra-hospitalar** — a população estudada foi exclusivamente de parada extra-hospitalar (PCR-EH), assim como no TTM2 e no BOX já registrados nesta biblioteca.
- **Não ignorar a proporção de ritmo não chocável na amostra (883/1.158, cerca de 76%)** — resultado semelhante foi relatado também no subgrupo de ritmo chocável, mas o abstract não fornece o valor numérico da probabilidade posterior desse subgrupo — **VERIFICAÇÃO HUMANA NECESSÁRIA** antes de citar um número específico para o coorte chocável.

## O que este documento não cobre
**O valor numérico da probabilidade posterior no coorte de ritmo chocável** — o abstract consultado nesta sessão descreve o resultado como "semelhante" ao do coorte não chocável, sem fornecer o número; não afirmado aqui por não ter sido confirmado na fonte.

**Detalhes de desfechos secundários específicos (qualidade de vida, biomarcadores, tempo de internação)** — o abstract relata ausência de diferença nos desfechos secundários e na mortalidade, mas não descreve valores individuais; a publicação completa deveria ser consultada para esses números.

**Comentário editorial associado ao artigo** (referenciado no registro do PubMed como "Comment in") — não lido nesta sessão; não incluído aqui.

**Recomendação formal de diretriz (AHA/ERC-ESICM) incorporando o ICECAP** — o documento desta biblioteca sobre cuidados pós-parada AHA 2025 foi escrito antes da publicação do ICECAP (agosto de 2026) e não o incorpora; nenhuma atualização de diretriz citando o ICECAP foi verificada nesta sessão.

## Tudo com Tudo
- [/biblioteca/controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2](/biblioteca/controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2) — TTM e TTM2, a pergunta anterior e mais ampla (se e a que temperatura resfriar), que o ICECAP não reabre
- [/biblioteca/evolucao-historica-do-controle-de-temperatura-pos-parada-de-haca-bernard-2002-ao-ttm2](/biblioteca/evolucao-historica-do-controle-de-temperatura-pos-parada-de-haca-bernard-2002-ao-ttm2) — contexto histórico de como a duração de 24h (e depois 28h no TTM2) foi escolhida empiricamente antes de qualquer ensaio randomizado de duração
- [/biblioteca/hipotermia-terapeutica-em-ritmo-nao-chocavel-pos-parada-o-ensaio-hyperion](/biblioteca/hipotermia-terapeutica-em-ritmo-nao-chocavel-pos-parada-o-ensaio-hyperion) — mesmo eixo de estratificação por ritmo inicial (chocável vs. não chocável) usado no desenho adaptativo do ICECAP
- [/biblioteca/metas-de-pressao-arterial-e-de-oxigenacao-pos-parada-cardiorrespiratoria-o-ensaio-box](/biblioteca/metas-de-pressao-arterial-e-de-oxigenacao-pos-parada-cardiorrespiratoria-o-ensaio-box) — mesmo padrão de resultado (escalonar a intensidade de uma variável de suporte pós-parada não mudou desfecho) em outro eixo (PAM e oxigenação)
- [/biblioteca/cuidados-pos-parada-cardiaca-na-uco-aha-2025-oxigenacao-pressao-temperatura-neuroprognostico](/biblioteca/cuidados-pos-parada-cardiaca-na-uco-aha-2025-oxigenacao-pressao-temperatura-neuroprognostico) — diretriz-guarda-chuva do manejo pós-parada, publicada antes do ICECAP e ainda não atualizada com este achado
- [/biblioteca/neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025](/biblioteca/neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025) — desfecho neurológico em 90 dias como métrica compartilhada entre o ICECAP e o algoritmo de neuroprognóstico
- [/biblioteca/pos-rosc-primeiras-24-horas-o-que-o-cardiologista-decide](/biblioteca/pos-rosc-primeiras-24-horas-o-que-o-cardiologista-decide) — decisão prática nas primeiras 24 horas pós-RCE, janela em que a duração da hipotermia (6 a 72 horas) é decidida à beira do leito
