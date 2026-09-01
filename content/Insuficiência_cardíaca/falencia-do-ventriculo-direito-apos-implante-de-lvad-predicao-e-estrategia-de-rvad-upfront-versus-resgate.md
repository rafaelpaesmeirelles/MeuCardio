---
title: "Falência do Ventrículo Direito Após Implante de LVAD: Predição, Definição e a Estratégia de RVAD Upfront versus Resgate"
slug: falencia-do-ventriculo-direito-apos-implante-de-lvad-predicao-e-estrategia-de-rvad-upfront-versus-resgate
theme: "Insuficiência cardíaca"
kind: "documento"
review_status: "pendente_revisao"
source_refs: ["Nonaka H, Lu LY, Obonyo NG, Suen JY, McGiffin DC, Fanning JP, Fraser JF. Right heart failure after left ventricular assist device implantation: latest insights and knowledge gaps on mechanism and prediction. Front Cardiovasc Med. 2025;12. DOI: 10.3389/fcvm.2025.1586389. PMID: 40476140 — abstract estruturado lido na íntegra via Europe PMC REST API (europepmc.org, registro EXT_ID:40476140, resultType=core) em 01/09/2026; título, autoria, periódico, ano e DOI conferidos contra o mesmo registro. Usado apenas para a afirmação geral de que a falência de VD pós-LVAD é frequente e é 'major driver' de morbimortalidade, com mecanismos ainda debatidos e predição difícil — não foram extraídos números específicos deste artigo, que é uma revisão de lacunas de conhecimento.", "Pre-implant Right Ventricular dP/dt Can Predict Severe Right Ventricular Failure After Left Ventricular Assist Device Implantation. Cardiac Fail Rev. 2025;11. DOI: 10.15420/cfr.2025.21. PMID: 41211198 — abstract estruturado lido na íntegra via Europe PMC REST API em 01/09/2026 (mesmo método acima). Números extraídos do abstract: coorte de 65 pacientes; RV dP/dt (não invasivo, por Doppler, medido fora de inotrópico) ≥300 mmHg/s associado a baixo risco de falência grave de VD, com sensibilidade de 89%; dP/dt persistentemente reduzido apesar de suporte inotrópico associado a maior risco de falência (OR 10,5). Nome(s) de autor(es) não constavam no campo retornado pela API neste registro — DOI e PMID conferidos, título e afiliação de periódico conferidos.", "Clinical impact of an upfront RVAD strategy in HeartMate 3 LVAD recipients with severe early right ventricular failure requiring temporary mechanical support. JHLT Open. 2025. DOI: 10.1016/j.jhlto.2025.100388. PMID: 41113999 — abstract estruturado lido na íntegra via Europe PMC REST API em 01/09/2026. Números extraídos: estudo retrospectivo com 64 receptores de HeartMate 3 com falência precoce grave de VD; estratégia de RVAD temporário 'upfront' (implantado de imediato) versus 'de resgate' (implantado após tentativa de manejo clínico/farmacológico); mortalidade intra-hospitalar 31% (upfront) vs. 57% (resgate); mortalidade em 90 dias 33% (upfront) vs. 68% (resgate); análise ajustada favoreceu a estratégia upfront para mortalidade em 90 dias; upfront também associada a menor arritmia perioperatória e menor necessidade de terapia renal substitutiva.", "Analysis of outcomes in patients with HeartMate 3 with and without right ventricular assist device support. ESC Heart Fail. 2025. DOI: 10.1002/ehf2.15353. PMID: 40557852 — abstract estruturado lido na íntegra via Europe PMC REST API em 01/09/2026. Números extraídos: coorte de 192 receptores de HeartMate 3, dos quais 51 (26%) necessitaram de RVAD temporário; mortalidade em 1 ano 33% (com RVAD temporário) vs. 3% (sem); mortalidade intra-hospitalar 26% vs. 1%; maior risco de AVC e de necessidade de diálise no grupo com RVAD temporário."]
legacy_source: "Documento novo, escrito em 01/09/2026, após checagem de colisão (grep -rlwi sobre content/**/*.md e sobre doencas/metadados.json, doencas/fragmentos/*.json, doencas/correcoes/*.json) por 'RVAD', 'ProtekDuo', 'Impella RP' e variações de 'falência de VD após/pós-LVAD'. A biblioteca tem MOMENTUM 3 (LVAD centrífugo vs. axial, desfechos gerais do dispositivo), o fluxograma de encaminhamento para IC avançada (LVAD/transplante), a IC direita crônica por doença tricúspide (fisiopatologia da congestão, sem LVAD), a falência aguda de VD na UCO e o consenso ACVC/ESC 2024 de cor pulmonale agudo (fisiopatologia geral de VD, sem foco em LVAD) e o documento de cateter de artéria pulmonar (PAPi como preditor hemodinâmico geral de disfunção de VD, com uma frase batendo que PAPi ≤0,9 não deve indicar RVAD automaticamente). Nenhum documento reunia especificamente a falência de VD COMO COMPLICAÇÃO PÓS-IMPLANTE DE LVAD — sua predição pré-operatória (RV dP/dt), a comparação de desfechos entre pacientes que precisam ou não de RVAD temporário, e a evidência recente (2025) sobre estratégia de RVAD 'upfront' versus 'de resgate' quando a falência de VD grave já ocorreu. É essa lacuna que este documento fecha."
---

# Falência do Ventrículo Direito Após Implante de LVAD: Predição, Definição e a Estratégia de RVAD Upfront versus Resgate

## Por que este documento existe, e o que ele NÃO repete

Esta biblioteca já cobre o dispositivo em si — o ensaio MOMENTUM 3, comparando LVAD de fluxo centrífugo e axial — e o momento de encaminhar o paciente para terapia avançada (fluxograma de encaminhamento para IC avançada: LVAD e transplante). Cobre também, em outro tema, a fisiopatologia geral da falência aguda de VD na UCO e o consenso ACVC/ESC 2024 sobre cor pulmonale agudo, além de um índice hemodinâmico frequentemente citado nesse contexto, o PAPi (índice de pulsatilidade da artéria pulmonar), no documento sobre cateter de artéria pulmonar no choque cardiogênico — que já registra explicitamente que "não existe RVAD automático baseado apenas em PAPi". O que faltava era o meio do caminho, específico do LVAD: a falência de VD que se manifesta **depois** do implante do dispositivo de assistência ventricular esquerda é a complicação mais temida do pós-operatório imediato — atinge uma proporção relevante dos receptores, é descrita como "major driver" de morbimortalidade, e ainda assim seus mecanismos permanecem parcialmente incompreendidos e sua predição continua difícil (Nonaka et al., *Front Cardiovasc Med*, 2025). Este documento reúne três frentes de evidência de 2025 sobre esse problema específico: como prever antes da cirurgia quem vai falir de VD, o que muda no desfecho de quem precisa de suporte temporário de VD, e — o achado mais acionável — se antecipar o suporte de VD ("upfront") muda o resultado comparado a esperar e resgatar depois que a falência já está instalada.

## O problema: por que o VD falha depois que o LVAD "resolve" o lado esquerdo

O LVAD descarrega o ventrículo esquerdo e reduz de forma abrupta a pós-carga que o VD enfrentava através da circulação pulmonar — mas ao mesmo tempo aumenta o retorno venoso ao VD, porque agora ele precisa bombear todo o débito que o LVAD está ejetando. Esse desequilíbrio agudo entre pré-carga aumentada e uma pós-carga que cai, mas não elimina a resistência vascular pulmonar previamente elevada (frequente em IC avançada de longa data), é o pano de fundo hemodinâmico da falência de VD pós-implante. Nonaka et al. sintetizam a literatura recente sobre esse mecanismo e sobre os fatores de risco associados, mas destacam que lacunas de conhecimento persistem — não há, hoje, um modelo preditivo único e amplamente validado, e diferentes coortes usam diferentes definições de "falência de VD", o que dificulta comparar estudos entre si. Esse é o contexto em que os três achados abaixo — todos de 2025 — se encaixam: cada um ataca uma parte diferente do problema (predizer antes, quantificar o impacto, e decidir a estratégia de suporte quando a falência já ocorreu).

## Prever antes da cirurgia: RV dP/dt não invasivo

Um estudo publicado em *Cardiac Failure Review* (2025) testou se a contratilidade do VD, medida de forma não invasiva por Doppler antes do implante (RV dP/dt), prediz a falência grave de VD depois da cirurgia. Em uma coorte de 65 pacientes, os achados foram consistentes com a intuição fisiológica, mas com números concretos e clinicamente úteis:

- **RV dP/dt ≥300 mmHg/s, medido fora de suporte inotrópico**, identificou um subgrupo de baixo risco de falência grave de VD pós-LVAD, com **sensibilidade de 89%** — ou seja, um valor acima desse limiar praticamente afasta o desfecho grave, com bom valor preditivo negativo.
- Pacientes cujo RV dP/dt permanecia **persistentemente reduzido apesar de suporte inotrópico** (ou seja, o VD não "respondia" ao inotrópico pré-operatório) tinham risco muito maior de falência grave — **odds ratio de 10,5**.

O valor prático desse achado é que se trata de uma medida **não invasiva e obtida antes da cirurgia**, o que a torna, em princípio, incorporável à avaliação pré-operatória de rotina em centros com LVAD — complementando, e não substituindo, os índices hemodinâmicos invasivos já discutidos nesta biblioteca (PAPi, RAP/PCWP) que seguem sendo usados no período perioperatório e na UCO.

## O impacto de precisar de suporte temporário de VD: o tamanho do problema

Um estudo publicado em *ESC Heart Failure* (2025) comparou desfechos entre receptores de HeartMate 3 que precisaram e que não precisaram de RVAD temporário (tRVAD). Em uma coorte de 192 pacientes, **51 (26%) precisaram de tRVAD** — quase um em cada quatro — e a diferença de prognóstico entre os dois grupos foi acentuada:

- Mortalidade **intra-hospitalar**: 26% (com tRVAD) vs. 1% (sem tRVAD).
- Mortalidade em **1 ano**: 33% (com tRVAD) vs. 3% (sem tRVAD).
- Maior risco de **AVC** e de **necessidade de diálise** no grupo que precisou de tRVAD.

Esses números dão a magnitude real do problema: precisar de suporte temporário de VD não é um detalhe técnico do pós-operatório — é, por si, um marcador de prognóstico muito pior, com mortalidade em 1 ano dez vezes maior que a de quem não precisa. Isso reforça a importância prática do achado seguinte, que trata de **como** dar esse suporte quando ele se torna necessário.

## A pergunta com resposta acionável: RVAD "upfront" ou "de resgate"?

Um estudo publicado em *JHLT Open* (2025) comparou, em 64 receptores de HeartMate 3 com falência precoce **grave** de VD que exigiu suporte mecânico temporário, duas estratégias de tempo de implante do RVAD temporário:

- **Estratégia upfront**: RVAD temporário implantado de imediato, junto com o LVAD ou logo após, diante de sinais de falência grave de VD.
- **Estratégia de resgate**: RVAD temporário implantado apenas depois de uma tentativa inicial de manejo clínico/farmacológico (inotrópico, vasodilatador pulmonar, otimização de volume) que falhou.

Os desfechos favoreceram claramente a estratégia upfront:

- Mortalidade **intra-hospitalar**: 31% (upfront) vs. 57% (resgate).
- Mortalidade em **90 dias**: 33% (upfront) vs. 68% (resgate).
- Em análise ajustada, a estratégia upfront manteve associação com **risco substancialmente menor de mortalidade em 90 dias**.
- A estratégia upfront também se associou a **menor incidência de arritmia perioperatória** e **menor necessidade de terapia renal substitutiva**.

O racional clínico por trás desse achado é coerente com o que já se sabe de choque cardiogênico em geral (e que esta biblioteca já documenta no contexto de suporte circulatório mecânico temporário e no documento de cateter de artéria pulmonar): esperar a falência de órgão se instalar antes de intervir tende a produzir pior desfecho do que reconhecer precocemente os sinais de falência grave de VD e agir antes que a hipoperfusão sistêmica e a disfunção renal e hepática se estabeleçam. A diferença aqui é que, tratando-se de um estudo retrospectivo, não é possível excluir viés de indicação — pacientes selecionados para a estratégia upfront podem ter sido identificados precocemente por sinais mais claros ou centros com protocolo mais agressivo de reconhecimento, o que a leitura do resultado deve levar em conta antes de generalizar como recomendação de classe/nível.

## Síntese prática

1. **A falência de VD pós-LVAD é comum e grave**, não um evento raro e incidental — cerca de um em cada quatro receptores de HeartMate 3 pode precisar de suporte temporário de VD, com mortalidade muito maior nesse subgrupo.
2. **A predição pode começar antes da cirurgia**: RV dP/dt não invasivo (fora de inotrópico) ≥300 mmHg/s sinaliza baixo risco; dP/dt que não melhora com inotrópico pré-operatório sinaliza risco alto (OR 10,5).
3. **Quando a falência grave de VD já ocorreu, não esperar para intervir**: a evidência retrospectiva de 2025 favorece implantar o RVAD temporário de forma antecipada ("upfront"), em vez de reservá-lo como resgate após falha do manejo clínico — com diferença de mortalidade em 90 dias quase pela metade (33% vs. 68%).
4. **Persistem lacunas** — os próprios autores da revisão de mecanismo e predição (Nonaka et al.) apontam que a definição de "falência de VD" ainda varia entre estudos e que os mecanismos completos não estão elucidados; nenhum dos números acima deve ser lido como recomendação de diretriz, e sim como evidência recente que informa a discussão em equipe (heart team) de cada caso.
5. **Este documento não repete** a seleção de candidato a LVAD, os critérios de encaminhamento para IC avançada, nem a comparação de dispositivos (MOMENTUM 3) — todos já cobertos alhures nesta biblioteca; ele cobre especificamente o que acontece com o VD depois que o LVAD é implantado.

## Tudo com Tudo

- [LVAD de Fluxo Centrífugo versus Axial: o Ensaio MOMENTUM 3](/biblioteca/lvad-de-fluxo-centrifugo-versus-axial-o-ensaio-momentum-3)
- [Fluxograma: Quando Encaminhar para IC Avançada — LVAD e Transplante Cardíaco](/biblioteca/fluxograma-encaminhamento-ic-avancada-lvad-transplante)
- [Insuficiência Cardíaca Direita Isolada por Doença Tricúspide: Fisiopatologia da Congestão e Manejo Clínico](/biblioteca/insuficiencia-cardiaca-direita-isolada-por-doenca-tricuspide-fisiopatologia-da-congestao-e-manejo-clinico)
- [Falência Aguda do Ventrículo Direito (Cor Pulmonale Agudo): Consenso ACVC/ESC 2024](/biblioteca/falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo-consenso-acvc-esc-2024)
- [Cateter de Artéria Pulmonar no Choque Cardiogênico: CPO, PAPi, RAP/PCWP e Tendências](/biblioteca/cateter-de-arteria-pulmonar-no-choque-cardiogenico-cpo-papi-e-ra-pcwp)
- [Decisão Compartilhada para LVAD de Terapia de Destino: o Ensaio DECIDE-LVAD](/biblioteca/decisao-compartilhada-para-lvad-de-terapia-de-destino-o-ensaio-decide-lvad)
- [Síndrome Cardiorrenal: Classificação em Cinco Tipos e Manejo na Insuficiência Cardíaca](/biblioteca/sindrome-cardiorrenal-classificacao-em-cinco-tipos-e-manejo-na-insuficiencia-cardiaca)
