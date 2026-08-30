---
title: "Fluxograma: Quando Encaminhar para Listagem de Transplante Cardíaco no Adulto"
slug: fluxograma-quando-encaminhar-para-listagem-de-transplante-cardiaco
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: grok
review_status: revisado
review_note: "Árvore de listagem no adulto, complementar — não substituta — ao fluxograma de encaminhamento a IC avançada/LVAD/transplante já publicado nesta pasta. Cortes de VO2, RER, SHFM, cateterismo, idade, IMC, TFGe, substância e demais barreiras reproduzem a ISHLT 2016 (PMID 26776864, PDF oficial lido nesta revisão editorial). Encaminhamento precoce Classe I A, I NEED HELP e Tabela 17 lidos na ESC 2026 (DOI 10.1093/eurheartj/ehag100). A árvore não atribui status de fila do sistema nacional de transplantes, não escolhe LVAD de destino versus ponte e não lista criança."
source_refs:
  - "Mehra MR, Canter CE, Hannan MM, Semigran MJ, Uber PA, Baran DA, et al. The 2016 International Society for Heart Lung Transplantation listing criteria for heart transplantation: A 10-year update. J Heart Lung Transplant. 2016 Jan;35(1):1-23. DOI: 10.1016/j.healun.2015.10.023. PMID: 26776864."
  - "Peled Y, Ducharme A, Kittleson M, et al. International Society for Heart and Lung Transplantation Guidelines for the Evaluation and Care of Cardiac Transplant Candidates—2024. J Heart Lung Transplant. 2024 Oct;43(10):1529-1628.e54. DOI: 10.1016/j.healun.2024.05.010. PMID: 39115488."
  - "Køber L, Adamo M, et al. 2026 ESC Guidelines for the management of heart failure. Eur Heart J. 2026. DOI: 10.1093/eurheartj/ehag100. Recommendation Table 11 (encaminhamento precoce Classe I A; TCPE e cateterismo direito Classe I C) e Tabela 17 (indicação e contraindicações) lidas nesta revisão editorial."
  - "Bacal F, Marcondes-Braga FG, Rohde LEP, et al. 3ª Diretriz Brasileira de Transplante Cardíaco. Arq Bras Cardiol. 2018 Aug;111(2):230-289. DOI: 10.5935/abc.20180153. PMID: 30335870. Citada no documento-irmão de indicações; a árvore não aplica o corte brasileiro de RVP >5 como nó, porque a ISHLT 2016 não o adota como absoluto no adulto."
---

# Fluxograma: Quando Encaminhar para Listagem de Transplante Cardíaco no Adulto

O fluxograma já publicado nesta pasta (`fluxograma-encaminhamento-ic-avancada-lvad-transplante.md`) responde **quando mandar o paciente a um centro de IC avançada**. Este responde a pergunta seguinte: **quando esse adulto deve ser formalmente avaliado para entrar na fila de transplante**. Encaminhar abre a porta; listar ocupa um órgão. Os dois atos não coincidem no tempo nem nos critérios.

A árvore começa no paciente com IC crônica em tratamento otimizado para o fenótipo e pergunta se há sinal de IC avançada. Não exige FEVE reduzida. Não espera o teste cardiopulmonar no paciente já em inotrópico ou em suporte mecânico temporário. Não transforma VO₂, SHFM ou RVP em único número decisivo — a ISHLT 2016 dedica duas recomendações de Classe III exatamente a listar só com VO₂ ou só com escore.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto com IC crônica, qualquer fenótipo de FEVE,<br/>em terapia otimizada e máxima tolerada para o fenótipo"]
  D1{"Sinal de IC avançada ou de alto risco<br/>I NEED HELP ou regra dos três,<br/>NYHA III-IV persistente, internamentos<br/>recorrentes, intolerância a GDMT,<br/>hipoperfusão ou caquexia?"}
  C1(["Não encaminhar para listagem agora.<br/>Manter tratamento do fenótipo<br/>e reavaliar periodicamente"])
  D2{"Já em inotrópico venoso contínuo,<br/>suporte mecânico temporário,<br/>ou choque cardiogênico com<br/>recuperação neurológica?"}
  C2(["Encaminhamento URGENTE ao centro<br/>de transplante — avaliação de listagem<br/>em paralelo à estabilização.<br/>Não esperar TCPE ambulatorial"])
  D3{"Barreira de Classe III presente<br/>e não reversível — substância ativa<br/>incluindo álcool, não adesão reiterada<br/>ao regime, HCV/HBV com cirrose<br/>hipertensão portal ou CHC,<br/>comorbidade grave de prognóstico<br/>próprio não reversível com o enxerto?"}
  C3(["Não listar. Discutir LVAD como destino<br/>se houver anatomia e suporte,<br/>ou cuidado paliativo integrado.<br/>A barreira ao transplante não torna<br/>o paciente automaticamente candidato a LVAD"])
  D4{"Barreira relativa modificável<br/>IMC ≥35, TFGe <30 ainda não estabelecida<br/>como irreversível, tabaco nos 6 meses,<br/>HbA1c ≥7,5% com lesão de órgão-alvo,<br/>idade >70, suporte social frágil,<br/>RVP alta ainda não desafiada?"}
  C4(["Encaminhar mesmo assim — avaliar<br/>ponte para candidatura com LVAD<br/>e prazo de reversão da barreira.<br/>Não atrasar o centro para 'emagrecer<br/>ou parar de fumar sozinho'"])
  D5{"Candidato ambulatorial: TCPE máximo<br/>RER >1,05 com limiar anaeróbico —<br/>VO2 pico ≤12 em betabloqueador<br/>ou ≤14 sem betabloqueador,<br/>ou ≤50% do predito em mulher/<50 anos?"}
  D6{"Zona cinzenta de VO2 12-14<br/>ou teste submáximo?<br/>SHFM sobrevida em 1 ano <80%<br/>ou HFSS médio/alto,<br/>ou VE/VCO2 >35 se RER <1,05?"}
  C5(["Sem critério funcional objetivo agora.<br/>Não listar só por NYHA.<br/>Reavaliar após otimização;<br/>repetir TCPE se o quadro piorar"])
  D7{"Cateterismo direito: PSAP ≥50 mmHg<br/>e GTP ≥15 ou RVP >3 UW?<br/>Desafio vasodilatador com PAS >85?"}
  C6(["Listagem formal no centro de transplante<br/>se avaliação psicossocial, infecciosa<br/>incluindo Chagas quando indicado,<br/>oncológica e de órgãos-alvo<br/>não revelar Classe III.<br/>RHC periódico a cada 3-6 meses<br/>enquanto estiver na fila"])
  C7(["Internar para descarregar o VE<br/>diurético, inotrópico, vasoativo;<br/>se falhar, considerar IABP/LVAD<br/>e reavaliar RVP em 3-6 meses<br/>antes de concluir irreversibilidade"])

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não — ambulatorial"| D3
  D3 -->|"Sim — Classe III fixa"| C3
  D3 -->|"Não"| D4
  D4 -->|"Sim — relativa modificável"| C4
  D4 -->|"Não"| D5
  D5 -->|"Sim — TCPE máximo no corte"| D7
  D5 -->|"Não ou TCPE ainda não feito"| D6
  D6 -->|"Sim — escore ou VE/VCO2 apoia"| D7
  D6 -->|"Não"| C5
  D7 -->|"Sem critério de desafio<br/>ou desafio reversível"| C6
  D7 -->|"Desafio falhou"| C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Como ler os nós, na ordem em que o erro costuma acontecer

**O nó D1 não é listagem.** É o mesmo sinal de estágio D que a ESC 2026 pede para consultar o centro cedo (Classe I, A): I NEED HELP, regra dos três, internamentos recorrentes, intolerância à terapia, hipoperfusão, caquexia. Mulher e minoria sociocultural tendem a ser encaminhadas mais tarde — o nó não deve ser aplicado com barra mais alta nesses grupos.

**O nó D2 existe para não transformar o TCPE em pedágio.** Paciente em inotrópico contínuo, em ECMO ou Impella, ou em choque com recuperação neurológica, vai ao centro agora. A ISHLT 2016 construiu os cortes de VO₂ para o **ambulatorial**. Esperar um teste máximo num paciente que não consegue andar até o corredor é o atraso clássico.

**O nó D3 é o “não listar” verdadeiro**, não a relativa que o plantonista chama de absoluta. Abuso ativo de substância inclusive álcool, não adesão reiterada, hepatopatia crônica viral **com** cirrose/hipertensão portal/CHC, e comorbidade grave cujo prognóstico o enxerto não reverte são Classe III da ISHLT 2016 ou absolutos da Tabela 17 da ESC 2026. Demência com incapacidade permanente de cooperar entra aqui. HIV selecionado **não** entra: CD4 >200, RNA indetectável, cART estável >3 meses e sem oportunista específica podem ser considerados (Classe IIa, C).

**O nó D4 é o mais mal usado na prática.** IMC ≥35, TFGe <30 ainda não crônica irreversível, cigarro nos últimos 6 meses, HbA1c ≥7,5% com lesão de órgão-alvo, idade >70 selecionada, suporte social frágil e RVP alta ainda não desafiada são relativas. A conduta é encaminhar e discutir **ponte para candidatura**, não mandar o paciente “resolver em casa” e voltar daqui a um ano. A ISHLT 2016 dá Classe IIb, C exatamente para LVAD nesse papel.

**Os nós D5 e D6 separam corte de TCPE de zona cinzenta.** Corte de listagem no teste máximo: ≤12 mL/kg/min com betabloqueador, ≤14 sem betabloqueador; em mulher ou <50 anos, ≤50% do predito entra como IIa. Zona cinzenta: SHFM com sobrevida em 1 ano <80% (mortalidade estimada >20%) ou HFSS médio/alto, ou VE/VCO₂ >35 se o teste foi submáximo. Listar só com VO₂ ou só com escore é Classe III.

**O nó D7 é hemodinâmica pulmonar, não um número mágico de RVP.** Desafio vasodilatador quando PSAP ≥50 mmHg e (GTP ≥15 ou RVP >3 UW), com PAS >85 mmHg. Irreversibilidade só depois de falha da terapia médica **e** de não conseguir descarregar o VE com IABP/LVAD, com reavaliação 3 a 6 meses após LVAD. A árvore **não** aplica o corte brasileiro de RVP >5 da SBC 2018 como nó — esse número é do documento nacional, não da ISHLT 2016, e a decisão fina é do centro.

## O que a árvore não mostra

**Status de fila do sistema nacional de transplantes** (urgência, prioridade, critérios de alocação) não é ISHLT e não cabe neste fluxograma.

**Escolha entre LVAD de ponte e LVAD de destino**, e entre modelos de dispositivo, não é ramo desta árvore — ver o fluxograma de encaminhamento a IC avançada e o documento do MOMENTUM 3.

**INTERMACS** não lista. Não aparece como nó de propósito: não é critério de listagem na ISHLT 2016 nem na 2024.

**Criança e adolescente** têm documento próprio. Não usar estes cortes de VO₂, idade 70 ou IMC 35 na pediatria.

**Critérios completos de infecção, neoplasia e psicossocial** (Chagas, TB latente, HIV selecionado, tempo de remissão oncológica sem quarentena arbitrária, avaliação de suporte) estão no documento-irmão `indicacoes-de-transplante-cardiaco-adulto-ishlt-2016.md`. A árvore só pergunta se a barreira é Classe III fixa ou relativa modificável.

**Sobrevida do enxerto** depois de transplantado também não está aqui — calibra a conversa com a família, não o nó de listar.
