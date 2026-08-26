---
title: "Fluxograma: Trombose venosa superficial — quando anticoagular vs. observar"
slug: fluxograma-trombose-venosa-superficial-quando-anticoagular
theme: "Tromboembolismo"
kind: fluxograma
fonte_producao: chatgpt
summary: "A conduta na trombose venosa superficial (TVS) de membro inferior depende de três eixos — trombose profunda concomitante, distância da junção safenofemoral/safenopoplítea e comprimento do trombo. O ensaio CALISTO estabeleceu o fondaparinux 2,5 mg por 45 dias como conduta para TVS ≥5 cm sem trombose profunda associada; abaixo disso, observação com AINE costuma bastar."
review_status: revisado
review_note: "3 PMIDs conferidos individualmente no PubMed via E-utilities (esearch/esummary/efetch) nesta sessão: 20860504 (ensaio CALISTO — Decousus H et al., 'Fondaparinux for the treatment of superficial-vein thrombosis in the legs', N Engl J Med. 2010;363(13):1222-1232 — inclusão/exclusão, dose, duração e resultado do composto primário conferidos no abstract completo via efetch), 26867832 (diretriz CHEST 2016 de terapia antitrombótica para doença tromboembólica venosa — Kearon C et al., Chest. 2016;149(2):315-352 — recomendação de fondaparinux/HBPM profilática por 45 dias em TVS ≥5cm, preferência por fondaparinux) e 33334670 (diretriz ESVS 2021 de manejo da trombose venosa — Kakkos SK et al., Eur J Vasc Endovasc Surg. 2021;61(1):9-82, seção de trombose venosa superficial, que fundamenta o critério de distância da junção safenofemoral/safenopoplítea como equivalente a tratar como TVP). Título, revista, volume/página e autor conferidos contra o registro oficial (esummary) antes de citar; abstract completo lido via efetch para o CALISTO. Tema sem cobertura prévia em fluxograma no acervo — os 5 fluxogramas já publicados do tema cobrem diagnóstico e estratificação de risco do TEP agudo, duração de anticoagulação após TEV não provocado, TEV incidental em exame de imagem e sangramento maior em paciente anticoagulado; documentos em prosa já existentes no tema (duração estendida no câncer, trombo de ventrículo esquerdo, TEV recorrente sob anticoagulação terapêutica) foram conferidos antes de escolher o recorte, para não duplicar."
source_refs: ["Fondaparinux for the treatment of superficial-vein thrombosis in the legs (ensaio CALISTO) · Decousus H et al. · The New England Journal of Medicine · 2010 · 363(13):1222-1232 · doi:10.1056/NEJMoa0912072 · https://pubmed.ncbi.nlm.nih.gov/20860504/", "Antithrombotic Therapy for VTE Disease: CHEST Guideline and Expert Panel Report · Kearon C et al. · Chest · 2016 · 149(2):315-352 · doi:10.1016/j.chest.2015.11.026 · https://pubmed.ncbi.nlm.nih.gov/26867832/", "Editor's Choice — European Society for Vascular Surgery (ESVS) 2021 Clinical Practice Guidelines on the Management of Venous Thrombosis · Kakkos SK et al. · European Journal of Vascular and Endovascular Surgery · 2021 · 61(1):9-82 · doi:10.1016/j.ejvs.2020.09.023 · https://pubmed.ncbi.nlm.nih.gov/33334670/"]
---

# Fluxograma: Trombose venosa superficial — quando anticoagular vs. observar

A trombose venosa superficial (TVS) do membro inferior — cordão palpável,
doloroso, eritematoso, ao longo do trajeto de uma veia superficial, tipicamente
varicosa — foi por décadas tratada como condição benigna e autolimitada,
manejada só com anti-inflamatório e compressão. O ensaio CALISTO (2010) mudou
essa leitura ao mostrar que a TVS de comprimento relevante carrega risco real
de progressão para trombose venosa profunda (TVP) e tromboembolismo pulmonar
(TEP), e que a anticoagulação em dose profilática por 45 dias reduz esse risco
de forma expressiva. A diretriz CHEST 2016 incorporou esse resultado como
recomendação formal, e a diretriz ESVS 2021 detalhou os critérios que separam
quem só precisa de vigilância de quem deve ser tratado como TVP. A árvore
abaixo organiza essa decisão em três eixos sucessivos: existe trombose
profunda concomitante, o trombo está perto demais da junção safenofemoral (ou
safenopoplítea), e o trombo é longo o suficiente para justificar anticoagulação
em dose profilática.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com trombose venosa superficial<br/>(TVS) de membro inferior, confirmada por<br/>eco-Doppler venoso de todo o membro"] --> D1{"O eco-Doppler mostra TVP<br/>concomitante ou TEP sintomático<br/>associado?"}

  D1 -->|"Sim"| C1(["Tratar como TEV profundo: anticoagulação<br/>terapêutica plena, na mesma dose e duração<br/>do evento correspondente — a TVS deixa de<br/>ser o diagnóstico principal"])

  D1 -->|"Não — TVS isolada,<br/>sem trombose profunda"| D2{"O trombo está a menos de 3 cm da<br/>junção safenofemoral (ou<br/>safenopoplítea), ou já se estende<br/>ao sistema venoso profundo?"}

  D2 -->|"Sim"| C2(["Tratar como TVP: anticoagulação terapêutica<br/>plena, mesmo esquema e duração de TVP<br/>proximal — nesta distância o risco de<br/>propagação ao sistema profundo é tratado<br/>como equivalente ao da TVP já instalada"])

  D2 -->|"Não — trombo distante da<br/>junção, sistema profundo poupado"| D3{"Extensão do trombo ≥ 5 cm de<br/>comprimento (critério de<br/>inclusão do CALISTO)?"}

  D3 -->|"Não — trombo<br/>curto, < 5 cm"| D4{"Fator de alto risco presente (câncer<br/>ativo, TEV prévio, trombofilia<br/>conhecida, TVS recorrente ou<br/>multifocal, veia varicosa extensa)?"}

  D4 -->|"Não"| C3(["Sem anticoagulação rotineira: AINE oral ou<br/>tópico, compressão elástica, e reavaliação<br/>clínica com novo eco-Doppler em 7–10 dias<br/>para excluir progressão"])

  D4 -->|"Sim"| C4(["Individualizar mesmo com trombo < 5 cm:<br/>considerar fondaparinux 2,5 mg SC 1x/dia por<br/>45 dias (ou HBPM em dose profilática) diante<br/>do risco de recorrência/extensão — decisão<br/>compartilhada com o paciente"])

  D3 -->|"Sim — trombo<br/>≥ 5 cm"| D5{"Há contraindicação à anticoagulação<br/>(sangramento ativo, plaquetopenia<br/>grave, alergia a fondaparinux)?"}

  D5 -->|"Sim"| C5(["Sem anticoagulação: compressão elástica, AINE,<br/>eco-Doppler seriado (semanal) até resolução;<br/>ligadura cirúrgica da junção safenofemoral se<br/>houver progressão em direção ao sistema profundo"])

  D5 -->|"Não"| C6(["Fondaparinux 2,5 mg SC 1x/dia por 45 dias<br/>(CALISTO) — reduziu o composto de TEP/TVP<br/>sintomática, extensão até a junção<br/>safenofemoral, recorrência e morte de 5,9%<br/>para 0,9% (RRR ~85%), com sangramento maior<br/>raro e semelhante ao placebo. HBPM em dose<br/>profilática por 45 dias é alternativa aceita<br/>pela diretriz CHEST 2016"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**O eco-Doppler de rastreio precisa avaliar o membro inteiro, não só o
segmento sintomático.** O CALISTO e as diretrizes que o incorporaram partem de
TVS já confirmada por imagem, com o sistema profundo formalmente examinado —
até um quarto dos casos de TVS tem TVP concomitante ao diagnóstico, muitas
vezes assintomática, e é essa checagem inicial que decide o primeiro ramo da
árvore.

**O critério de "3 cm da junção" não é um número exato e universal** — é a
forma como a literatura opera o conceito de proximidade que ameaça o sistema
profundo, e a distância exata pode variar entre o texto de diferentes
diretrizes. Diante de trombo próximo à junção mas com medida limítrofe, a
decisão de tratar como TVP em vez de aplicar o ramo de dose profilática tende
a pesar para o lado mais cauteloso, sobretudo se houver qualquer sinal
ecográfico de fluxo comprometido na junção.

**TVS recorrente ou migratória (tromboflebite migratória)** é achado clássico
associado a neoplasia oculta (síndrome de Trousseau) e, nesse cenário, costuma
justificar investigação oncológica dirigida por idade e fatores de risco — a
mesma lógica de rastreio de câncer oculto já usada após TEV não provocado,
não representada nesta árvore por ser uma investigação paralela, não um ramo
de conduta imediata da TVS.

**TVS em veia não varicosa** (veia superficial de calibre normal, sem
doença varicosa de base) tem associação mais forte com trombofilia e neoplasia
do que a TVS que ocorre sobre uma variz já conhecida — é um sinal de alerta
adicional para investigar causa subjacente, sem mudar a árvore de decisão
terapêutica em si.

**Tromboflebite séptica** (sinais infecciosos francos — febre, calafrio,
secreção purulenta no trajeto, geralmente associada a cateter venoso
periférico) é uma entidade distinta, que exige antibioticoterapia e, com
frequência, remoção cirúrgica do segmento infectado — não está coberta por
esta árvore, que trata da TVS espontânea/varicosa.

**A doença de Mondor** (TVS da parede torácica ou mamária) segue princípio
semelhante de conduta conservadora com AINE na maioria dos casos, mas por
localização e mecanismo distintos (trauma local, pós-cirúrgico, raramente
associada a neoplasia de mama) não está representada nesta árvore, construída
para o território de membro inferior que sustenta o corpo de evidência do
CALISTO e das diretrizes citadas.

**A escolha entre fondaparinux e HBPM em dose profilática** segue
disponibilidade e preferência local — a diretriz CHEST 2016 expressa
preferência pelo fondaparinux sobre a HBPM profilática nesse cenário
específico, mas trata as duas como opções aceitáveis, e a diferença não muda
nenhum ramo desta árvore.
