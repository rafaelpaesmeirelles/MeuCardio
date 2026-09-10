---
title: Vutrisiran
slug: vutrisiran
theme: Farmacologia
kind: farmacologia
review_status: revisado
source_refs:
- 'Fontana M, Berk JL, Gillmore JD, Witteles RM, Grogan M, Drachman B, et al; HELIOS-B Trial Investigators. Vutrisiran
  in Patients with Transthyretin Amyloidosis with Cardiomyopathy. N Engl J Med. 2025;392(1):33-44. Epub 2024 Aug
  30. DOI: 10.1056/NEJMoa2409134. PMID: 39213194. NCT04153149 — 655 pacientes, abstract completo lido via PubMed
  E-utilities em 09/09/2026'
- FDA, Drugs@FDA (openFDA drugsfda API), aplicação BLA/NDA 215515 (AMVUTTRA, vutrisiran, Alnylam Pharmaceuticals)
  · https://api.fda.gov/drug/drugsfda.json?search=openfda.generic_name:vutrisiran · consultado em 09/09/2026 — aprovação
  original (Tipo 1, nova entidade molecular) em 13/06/2022 para polineuropatia da amiloidose hereditária por transtirretina
  (hATTR-PN); suplemento de eficácia (submission_number 6) aprovado em 20/03/2025, ampliando a indicação para cardiomiopatia
  amiloide por transtirretina (ATTR-CM), com base nos dados do HELIOS-B
- 'Fontana M, Gillmore JD, Witteles RM, Laryea B, Dworkin M, Payne A, et al. Treatment with vutrisiran in people
  with transthyretin amyloidosis with cardiomyopathy: a plain language summary. Future Cardiol. 2025;21(8):555-565.
  DOI: 10.1080/14796678.2025.2493019. PMID: 40371908 — resumo em linguagem simples do HELIOS-B, usado apenas para
  confirmar desenho de administração (a cada 12 semanas, por até 3 anos) e financiamento; não usado como fonte primária
  de números de eficácia'
legacy_source: Documento novo, escrito em 09/09/2026. A pasta Farmacologia já cobre dois fármacos de ATTR-CM por
  outro mecanismo — estabilizadores de transtirretina (tafamidis.md e, em Cardiomiopatias, o ensaio ATTR-ACT e a
  extensão aberta de 54 meses do acoramidis/ATTRibute-CM) — mas nenhum documento do acervo (conferido em content/**/*.md,
  não só nos JSONs) cobre o vutrisiran, terapêutica de RNA de interferência (siRNA) que silencia a produção hepática
  de transtirretina. É mecanismo farmacológico distinto (supressão da síntese da proteína amiloidogênica na origem,
  não estabilização da forma tetramérica circulante) e teve extensão de indicação para cardiomiopatia aprovada pela
  FDA em março de 2025, com base em ensaio de desfecho de mortalidade (HELIOS-B) publicado no NEJM — assunto genuinamente
  2024-2025, ainda não coberto.
summary: null
tags: []
evidence_level: null
source_tier: A
gaps: []
published: false
---

# Vutrisiran

## Nome generico
Vutrisiran (sal sódico)

## Classe
Terapêutica de RNA de interferência (siRNA) contra a transtirretina — mesma classe mecanística do patisiran, mas com conjugação a N-acetilgalactosamina (GalNAc) que permite administração subcutânea trimestral em vez de infusão intravenosa

## Mecanismo acao
Silencia, por interferência de RNA, a produção hepática de transtirretina (TTR) — reduz a síntese da proteína na origem, e não apenas sua agregação em fibrilas amiloides. É mecanisticamente distinto dos estabilizadores de TTR (tafamidis, acoramidis): estes impedem a dissociação do tetrâmero já formado e circulante; o vutrisiran reduz a quantidade de proteína disponível para se agregar, atuando a montante. O uso concomitante de tafamidis foi permitido no HELIOS-B. A consistência de subgrupos não prova benefício incremental significativo em cada subgrupo nem estabelece a superioridade de combinar tratamentos.

## Evidencia pivotal — HELIOS-B
Fontana M et al., N Engl J Med. 2025;392(1):33-44 (DOI 10.1056/NEJMoa2409134, PMID 39213194), NCT04153149. Ensaio duplo-cego, randomizado 1:1, **655 pacientes** com ATTR-CM (326 vutrisiran, 329 placebo), vutrisiran 25 mg ou placebo por via subcutânea a cada 12 semanas, por até 36 meses. Uso concomitante de tafamidis no início do estudo era permitido; análises hierárquicas pré-especificadas foram feitas tanto na população geral quanto na população em monoterapia (sem tafamidis basal).

- **Desfecho primário (composto de morte por qualquer causa e eventos cardiovasculares recorrentes)**: HR **0,72** (IC95% 0,56-0,93; p=0,01) na população geral; HR **0,67** (IC95% 0,49-0,93; p=0,02) na população em monoterapia
- **Mortalidade por qualquer causa em até 42 meses**: HR **0,65** (IC95% 0,46-0,90; p=0,01) na população geral
- **Pacientes com pelo menos um evento do desfecho primário**: **125/326 (vutrisiran) vs. 159/329 (placebo)**
- **Teste de caminhada de 6 minutos**: diferença de médias de mínimos quadrados de **26,5 m** a favor do vutrisiran (IC95% 13,4-39,6; p<0,001) frente ao declínio observado no placebo
- **Qualidade de vida (KCCQ-OS)**: diferença de **5,8 pontos** a favor do vutrisiran (IC95% 2,4-9,2; p<0,001)
- **Segurança**: incidência de eventos adversos semelhante entre grupos (99% vutrisiran vs. 98% placebo); eventos adversos graves em **62% (vutrisiran) vs. 67% (placebo)** — sem sinal de excesso de toxicidade com o fármaco ativo nesta métrica agregada
- **fonte**: NEJM (HELIOS-B, PMID 39213194)

## Indicacoes cardiologicas
Cardiomiopatia amiloide por transtirretina (ATTR-CM), tanto na forma hereditária (variante) quanto na forma selvagem (*wild-type*) — mesma população-alvo do tafamidis e do acoramidis. A indicação para ATTR-CM é uma **extensão** da indicação original do vutrisiran, aprovada primeiro (2022) para a polineuropatia da amiloidose hereditária por transtirretina (hATTR-PN), não para a doença cardíaca

## Dose e apresentacoes
- **dose**: 25 mg por via subcutânea, a cada **3 meses**, conforme a bula (o ensaio usou intervalos de 12 semanas)
- **fontes**: NEJM (HELIOS-B), bula brasileira abaixo e [bula FDA](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8db0facb-81b6-4006-9239-27dc6409c5d3).
- **Populações especiais:** sem ajuste em disfunção renal leve/moderada (eTFG ≥30) ou hepática leve/moderada; não estudado em comprometimento grave ou doença renal terminal. Não há estudos clínicos formais de interação; baixo potencial previsto via CYP não significa ausência comprovada de toda interação.
- **Vitamina A:** suplementar a quantidade diária recomendada; não aumentar doses apenas para normalizar níveis séricos. Sintomas como cegueira noturna exigem avaliação oftalmológica.
- **Bula brasileira:** contraindicação em hipersensibilidade grave ao fármaco/excipientes; gravidez não recomendada, com contracepção eficaz durante tratamento. Lactação requer avaliação individual. Administração por profissional de saúde; seringa de 25 mg/0,5 mL.

## Regulatorio — aprovação FDA e status no Brasil
- **Aprovação original (FDA)**: 13/06/2022, como nova entidade molecular (Tipo 1), para polineuropatia da amiloidose hereditária por transtirretina — não incluía cardiomiopatia
- **Extensão de indicação para ATTR-CM (FDA)**: suplemento de eficácia aprovado em **20/03/2025**, com base no HELIOS-B
- **Nome comercial (EUA)**: AMVUTTRA (vutrisiran), Alnylam Pharmaceuticals, BLA/NDA 215515
- **Brasil:** a bula profissional publicada pelo fabricante, aprovada em 31/03/2025, inclui adultos com amiloidose hereditária com polineuropatia e amiloidose selvagem/hereditária com cardiomiopatia. Registro 1.9361.0004.001-6. [Bula brasileira](https://www.alnylam.com.br/sites/default/files/pdfs/Amvuttra_Bula_Profissional.pdf).
- **fonte**: FDA, Drugs@FDA / openFDA (consultado em 09/09/2026)

## Vutrisiran vs. estabilizadores de TTR (tafamidis, acoramidis) — o que o HELIOS-B não permite concluir
- O HELIOS-B **não comparou vutrisiran diretamente contra tafamidis ou acoramidis** — o comparador foi placebo, com tafamidis basal permitido em ambos os braços. Não há, a partir deste ensaio isolado, uma resposta sobre qual fármaco (ou classe) é superior
- O desfecho de **mortalidade por qualquer causa** como componente do desfecho primário (e como desfecho isolado, com HR 0,65 até 42 meses) não deve ser comparado diretamente com o resultado do ATTR-ACT do tafamidis, cujo desfecho de mortalidade descrito no acervo (ver `tafamidis.md`) foi de 29,5% vs. 42,9% ao longo de 30 meses — números de estudos diferentes, populações e desenhos distintos, que não devem ser comparados informalmente como se fossem braços do mesmo ensaio
- A permissão de uso concomitante de tafamidis no protocolo do HELIOS-B **sugere** possibilidade de terapia combinada (estabilização do tetrâmero remanescente + silenciamento da síntese hepática), mas o ensaio não foi desenhado para isolar o efeito incremental da combinação sobre qualquer monoterapia

## Armadilhas clínicas
- **Confundir a indicação original (2022, polineuropatia) com a indicação cardiológica (2025, cardiomiopatia)** — são aprovações regulatórias separadas, baseadas em ensaios diferentes; um registro de bula desatualizado pode não refletir a extensão de 2025
- **Extrapolar o HR do desfecho primário composto para "redução de mortalidade isolada" sem checar qual dos dois números está sendo citado** — o ensaio reporta ambos (HR 0,72 para o composto; HR 0,65 para óbito isolado em 42 meses), e são estimativas diferentes, não intercambiáveis
- **Tratar HELIOS-B como prova de superioridade sobre tafamidis ou acoramidis** — o comparador foi placebo (com tafamidis basal permitido), não um comparador ativo
- **Presumir que resultados do estudo substituam a bula local** — a indicação brasileira foi conferida, mas as condições de uso seguem a bula vigente

## Conteúdo CorVIA conectado
- [Tafamidis](/biblioteca/tafamidis)
- [Tafamidis Treatment for Patients with Transthyretin Amyloid Cardiomyopathy (ATTR-ACT)](/biblioteca/tafamidis-treatment-for-patients-with-transthyretin-amyloid-cardiomyopathy-attr-act)
- [Acoramidis na Amiloidose Cardíaca por Transtirretina: Extensão Aberta de 54 Meses do ATTRibute-CM](/biblioteca/acoramidis-extensao-aberta-de-54-meses-do-attribute-cm)
- [Diagnóstico e Tratamento da Amiloidose Cardíaca](/biblioteca/diagnostico-e-tratamento-da-amiloidose-cardiaca)
- [Fluxograma: Amiloidose cardíaca — algoritmo diagnóstico não invasivo e tipagem genética](/biblioteca/fluxograma-amiloidose-cardiaca-diagnostico-nao-invasivo)
