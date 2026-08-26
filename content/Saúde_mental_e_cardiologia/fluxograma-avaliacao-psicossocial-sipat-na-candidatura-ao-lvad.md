---
title: "Fluxograma: Avaliação Psicossocial Estruturada (SIPAT) na Candidatura ao LVAD"
slug: fluxograma-avaliacao-psicossocial-sipat-na-candidatura-ao-lvad
theme: "Saúde mental e cardiologia"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: PMID/DOI conferidos um a um via PubMed E-utilities (esearch/esummary/efetch), nenhum fabricado. Corpus da pasta conferido antes de escrever — rastreio/manejo da depressão pós-SCA e dor torácica por ansiedade/transtorno de pânico já têm fluxograma publicado; este recorte (avaliação psicossocial estruturada na candidatura ao LVAD, com achados por domínio do SIPAT) é inédito na pasta. A descrição dos quatro domínios do SIPAT foi obtida de uma revisão de escopo de 2026 (Olivero et al., PMC12977433) que a atribui explicitamente aos dois artigos originais de Maldonado et al. (2012 e 2015) — conferido linha a linha na lista de referências do XML do PMC, não aceito de segunda mão sem checar a atribuição."
source_refs:
  - "Dew MA, DiMartini AF, Dobbels F, Grady KL, Jowsey-Gregoire SG, Kaan A, et al. The 2018 ISHLT/APM/AST/ICCAC/STSW Recommendations for the Psychosocial Evaluation of Adult Cardiothoracic Transplant Candidates and Candidates for Long-term Mechanical Circulatory Support. Psychosomatics. 2018;59(5):415-440. DOI: 10.1016/j.psym.2018.04.003. PMID: 30197247."
  - "Maldonado JR, Dubois HC, David EE, Sher Y, Lolak S, Dyal J, Witten D. The Stanford Integrated Psychosocial Assessment for Transplantation (SIPAT): a new tool for the psychosocial evaluation of pre-transplant candidates. Psychosomatics. 2012;53(2):123-132. DOI: 10.1016/j.psym.2011.12.012. PMID: 22424160."
  - "Maldonado JR, Sher Y, Lolak S, Swendsen H, Skibola D, Neri E, David EE, Sullivan C, Standridge K. The Stanford Integrated Psychosocial Assessment for Transplantation: A Prospective Study of Medical and Psychosocial Outcomes. Psychosom Med. 2015;77(9):1018-1030. DOI: 10.1097/PSY.0000000000000241. PMID: 26517474."
  - "Bui QM, Braun OO, Brambatti M, Gernhofer YK, Hernandez H, Pretorius V, Adler E. The value of Stanford integrated psychosocial assessment for transplantation (SIPAT) in prediction of clinical outcomes following left ventricular assist device (LVAD) implantation. Heart Lung. 2019;48(2):85-89. DOI: 10.1016/j.hrtlng.2018.08.011. PMID: 30227993."
  - "Olt CK, Thuita LW, Soltesz EG, Tong MZ, Weiss AJ, Kendall K, Estep JD, Blackstone EH, Hsich EM; Stanford Integrated Psychosocial Assessment for Transplant Research Group. Value of psychosocial evaluation for left ventricular assist device candidates. J Thorac Cardiovasc Surg. 2023;165(3):1111-1121.e12. DOI: 10.1016/j.jtcvs.2021.04.065. PMID: 34053742."
  - "Olivero A, Miniotti M, Godono A, et al. A scoping review of the Stanford Integrated Psychosocial Assessment for Transplantation (SIPAT) for use with liver transplant candidates. Biopsychosoc Med. 2026. DOI: 10.1186/s13030-026-00352-4. PMID: 41654825 (usado apenas como fonte secundária, verificada, da descrição dos quatro domínios do SIPAT — atribuída no próprio texto a Maldonado et al. 2012 e 2015)."
---

# Fluxograma: Avaliação Psicossocial Estruturada (SIPAT) na Candidatura ao LVAD

O consenso multissocietário ISHLT/APM/AST/ICCAC/STSW de 2018 recomenda a avaliação psicossocial estruturada como parte da candidatura a dispositivo de assistência ventricular esquerda (LVAD), tanto em ponte para transplante quanto em terapia de destino. O instrumento mais estudado nesse contexto é o SIPAT (Stanford Integrated Psychosocial Assessment for Transplantation), validado originalmente em transplante (fígado, coração, pulmão) e depois testado especificamente em candidatos a LVAD em duas coortes independentes. **O achado central dessas duas coortes muda a forma de usar o instrumento**: a pontuação TOTAL do SIPAT não previu reinternação nem óbito pós-LVAD — mas domínios específicos do próprio instrumento previram, cada um, um tipo diferente de desfecho adverso. Este fluxograma traduz esse achado em conduta por domínio, em vez de tratar o SIPAT como um escore único de corte.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com indicação clínica para LVAD (ponte para<br/>transplante ou terapia de destino), em avaliação<br/>multidisciplinar de candidatura"] --> D1{"Avaliação psicossocial estruturada e validada<br/>(ex.: SIPAT) foi realizada como parte<br/>da candidatura?"}

  D1 -->|"Não"| C1(["Encaminhar para avaliação psicossocial estruturada<br/>antes de prosseguir — recomendada como componente<br/>da avaliação multidisciplinar pelo consenso ISHLT/APM/<br/>AST/ICCAC/STSW 2018, e testada especificamente em<br/>candidatos a LVAD em duas coortes (Bui et al., 2019,<br/>n=50; Olt/Hsich et al., 2021, n=263)"])

  D1 -->|"Sim"| P1["A pontuação TOTAL do SIPAT não se mostrou associada<br/>a reinternação nem a óbito pós-LVAD nas duas coortes<br/>que testaram isso (Bui et al., 2019: SIPAT categórico<br/>sem associação com reinternação cumulativa; Olt/Hsich<br/>et al., 2021, n=263, mediana do SIPAT 16 [IQR 8-28]:<br/>escore total sem associação com reinternação ou óbito<br/>em análise multivariada). A decisão não deve se apoiar<br/>isoladamente no escore total — avaliar os domínios<br/>específicos abaixo"]

  P1 --> D2{"Domínio de psicopatologia orgânica/comprometimento<br/>neurocognitivo identificado (componente SIPAT C-X)?"}

  D2 -->|"Sim"| C2(["Associado a maior risco de óbito no seguimento<br/>(coeficiente 0,59 ± erro padrão 0,21; p=0,006;<br/>Olt/Hsich et al., 2021). Solicitar avaliação<br/>neuropsicológica formal, reforçar a rede de apoio para<br/>os cuidados do dispositivo (troca de curativo, manejo<br/>do controlador) e confirmar cuidador substituto<br/>comprometido antes de prosseguir com a candidatura"])

  D2 -->|"Não"| D3{"Ambiente domiciliar inadequado ou instável para os<br/>cuidados do LVAD identificado (componente SIPAT<br/>B-VIII, domínio de suporte social)?"}

  D3 -->|"Sim"| C3(["Associado a maior risco de reinternação relacionada ao<br/>dispositivo (coeficiente 0,83 ± erro padrão 0,34;<br/>p=0,014; Olt/Hsich et al., 2021). Não constitui<br/>contraindicação isolada — acionar o serviço social antes<br/>do implante para plano estruturado de moradia,<br/>eletricidade estável e contingência para troca de bateria"])

  D3 -->|"Não"| D4{"Psicopatologia ativa significativa identificada no<br/>domínio de estabilidade psicológica<br/>(componente SIPAT C-IX)?"}

  D4 -->|"Sim"| C4(["Associado a maior risco de reinternação por<br/>hemocompatibilidade (coef. 0,21±0,11; p=0,040) e de<br/>reinternação cardíaca (coef. 0,15±0,065; p=0,02)<br/>(Olt/Hsich et al., 2021). Otimizar o tratamento<br/>psiquiátrico e envolver psiquiatria de ligação antes e<br/>depois do implante — achado isolado não indica exclusão<br/>da candidatura"])

  D4 -->|"Não"| D5{"Prontidão para o manejo da doença/autocuidado<br/>comprometida (domínio SIPAT de prontidão,<br/>componentes A-III ou pontuação A total elevada)?"}

  D5 -->|"Sim"| C5(["Associado a maior risco de reinternação não cardíaca<br/>(coef. 0,24±0,099; p=0,016, componente A-III) e de<br/>reinternação cardíaca (coef. 0,037±0,014; p=0,007,<br/>pontuação A total) (Olt/Hsich et al., 2021). Intensificar<br/>educação estruturada sobre autocuidado do dispositivo<br/>antes do implante"])

  D5 -->|"Não"| C6(["Nenhum domínio isolado de alto risco identificado nesta<br/>avaliação. Prosseguir a candidatura pela via<br/>multidisciplinar padrão — ausência de risco em um<br/>domínio específico não substitui o julgamento conjunto<br/>de cardiologia, cirurgia, psiquiatria/psicologia e<br/>serviço social"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**As duas coortes de LVAD são retrospectivas e unicêntricas** — Bui et al. (2019, UC San Diego, n=50) e Olt/Hsich et al. (2021, Cleveland Clinic, n=263). São hipótese-geradoras, não uma regra clínica prospectivamente validada como ferramenta específica de MCS; os próprios autores do estudo maior concluem que os achados "poderiam ser usados para criar uma ferramenta psicossocial específica do programa de LVAD" — ainda não existe essa ferramenta pronta.

**Um achado do estudo de Bui et al. (2019) foi deliberadamente deixado fora da árvore**: pontuação SIPAT mais alta (isto é, pior) associou-se a mais sangramento maior — direção contraintuitiva, sem explicação mecanística estabelecida no próprio artigo, numa amostra de apenas 50 pacientes. Incluir esse achado como nó de decisão correria o risco de sugerir uma relação causal que a fonte não sustenta.

**O consenso ISHLT/APM/AST/ICCAC/STSW 2018 (Dew et al.) é citado aqui como o documento-quadro que recomenda a avaliação psicossocial estruturada como parte da candidatura** — é um consenso de 27 especialistas de 6 sociedades, com revisão de literatura e opinião de especialistas, cobrindo conteúdo e processo da avaliação. O texto completo, com as recomendações específicas de conteúdo item a item, não foi acessado nesta verificação (bloqueio de acesso já registrado no acervo para outras diretrizes da mesma família de publicação) — por isso nenhuma recomendação numerada desse consenso foi citada individualmente aqui, só a existência e o escopo do documento, confirmados no próprio resumo indexado no PubMed.

**Não existe corte numérico do SIPAT aplicado a esta árvore de propósito.** O corte mais citado na literatura (≥21 associado a maior risco) vem sobretudo de estudos em transplante hepático, com valores de corte heterogêneos entre estudos (revisão de escopo de Olivero et al., 2026) — e nas duas coortes específicas de LVAD usadas aqui, foi exatamente a pontuação total que NÃO previu desfecho. Por isso a árvore segue os achados desta população específica (domínio, não escore de corte), em vez de importar um corte validado noutra população de transplante.

**As associações por domínio são estatísticas, obtidas em análise multivariável de coorte retrospectiva — não são, isoladamente, contraindicação à candidatura.** O próprio artigo de Olt/Hsich et al. propõe usá-las para orientar intervenção e acompanhamento mais próximo, não para excluir candidato. A decisão final de candidatura continua sendo do julgamento conjunto da equipe multidisciplinar.
