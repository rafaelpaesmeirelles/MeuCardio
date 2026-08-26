---
title: "Fluxograma: Comunicação interventricular no adulto — quando fechar (ESC 2020)"
slug: fluxograma-comunicacao-interventricular-no-adulto-quando-fechar-esc-2020
theme: "Cardiopatias congênitas"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore de decisão derivada do documento já publicado e verificado nesta pasta, 'Comunicação Interventricular (CIV) no Adulto: História Natural, Fechamento Tardio e Prolapso da Valva Aórtica' — mesmas fontes já conferidas no acervo (ESC 2020 ACHD PMID 32860028; JACC Asia 2026 PMID 42412691 e PMID 42559775). Nenhum PMID/DOI novo foi consultado nesta sessão: reaproveita citação já auditada, mesma prática de consistência já usada no fluxograma irmão de shunt esquerda-direita desta pasta."
source_refs: ["Baumgartner H, De Backer J, Babu-Narayan SV, et al. 2020 ESC Guidelines for the management of adult congenital heart disease. Eur Heart J. 2021;42(6):563-645. DOI: 10.1093/eurheartj/ehaa554. PMID: 32860028 — tabelas de recomendação para intervenção em comunicação interventricular por resistência vascular pulmonar e sobrecarga de volume do ventrículo esquerdo, mesma fonte já usada no fluxograma de shunt esquerda-direita desta pasta.", "Lin TH, Wang JK, Lin MT, et al. Impact of Device Position and Aortic Valve Prolapse on Outcomes After Transcatheter VSD Closure. JACC Asia. 2026 Aug 5. DOI: 10.1016/j.jacasi.2026.06.027. PMID: 42559775 — índice de prolapso da cúspide coronariana direita como preditor independente de falha procedimental (razão de chances 2,48 por incremento de 10%) e posição de 'clamping' do dispositivo associada a progressão de regurgitação aórtica no seguimento.", "Nguyen TVN, Ho SY, Do TN. Applied Anatomy of Perimembranous Ventricular Septal Defect for Transcatheter Device Closure. JACC Asia. 2026;6(7):1019-1032. DOI: 10.1016/j.jacasi.2026.03.002. PMID: 42412691. PMCID: PMC13350687 — classificação anatômica da CIV perimembranosa em 7 tipos morfológicos, usada para orientar a viabilidade técnica de fechamento por dispositivo."]
---

# Fluxograma: Comunicação interventricular no adulto — quando fechar (ESC 2020)

A comunicação interventricular (CIV) isolada é a cardiopatia congênita mais
frequente, e a maioria fecha espontaneamente ou é corrigida na infância. Esta
árvore cobre o adulto com CIV ainda não fechada — seja porque nunca indicou
fechamento na infância (defeito pequeno e restritivo), seja porque é achado
tardio — e organiza a decisão em torno de dois eixos que a diretriz ESC 2020
de cardiopatia congênita do adulto trata como independentes: a **repercussão
hemodinâmica** (resistência vascular pulmonar e sobrecarga de volume do
ventrículo esquerdo) e o **risco valvar aórtico associado**, que pode indicar
fechamento mesmo em defeito pequeno e sem sobrecarga de volume relevante.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto com comunicação interventricular (CIV) diagnosticada<br/>— perimembranosa, subarterial, muscular ou de via de entrada"] --> D1{"Há sinal não invasivo de hipertensão pulmonar<br/>— PAP sistólica estimada elevada, sinais indiretos —<br/>ou dessaturação ao esforço?"}

  D1 -->|"Sim"| P1["Cateterismo cardíaco direito com medida invasiva<br/>de resistência vascular pulmonar é obrigatório<br/>antes de decidir fechar"]

  P1 --> D2{"Resistência vascular pulmonar (RVP),<br/>com shunt esquerda-direita confirmado"}

  D2 -->|"Abaixo de 3 unidades Wood"| C1(["Fechar — Classe I. Fechamento cirúrgico ou por dispositivo,<br/>conforme anatomia e experiência do centro"])

  D2 -->|"De 3 a menos de 5 unidades Wood"| C2(["Fechamento deve ser considerado — Classe IIa,<br/>decisão individualizada em centro especializado"])

  D2 -->|"5 unidades Wood ou mais,<br/>sem fisiologia de Eisenmenger estabelecida"| C3(["Decisão individual cuidadosa em centro especializado<br/>— Classe IIb. Sem a faixa de fechamento fenestrado<br/>que existe para a comunicação interatrial"])

  D2 -->|"Fisiologia de Eisenmenger já estabelecida"| C4(["Não fechar — Classe III. Fechar retiraria a válvula<br/>de escape que mantém o débito sistêmico e pode<br/>precipitar falência aguda do ventrículo direito"])

  D1 -->|"Não"| D3{"Há sobrecarga de volume do ventrículo esquerdo<br/>— CIV moderada a grande, não restritiva?"}

  D3 -->|"Sim"| C5(["Fechar, independentemente de sintomas — Classe I.<br/>Fechamento cirúrgico ou por dispositivo,<br/>conforme anatomia e experiência do centro"])

  D3 -->|"Não: CIV pequena, restritiva"| D4{"Há prolapso de cúspide aórtica com regurgitação<br/>aórtica progressiva, ou anatomia de alto risco<br/>— subarterial ou perimembranosa tipo 2,<br/>com extensão superior-anterior?"}

  D4 -->|"Sim"| D5{"Fechamento percutâneo por dispositivo é<br/>tecnicamente viável — borda aórtica suficiente,<br/>índice de prolapso avaliado por ecocardiograma<br/>transesofágico?"}

  D5 -->|"Sim"| C6(["Fechar por dispositivo, mesmo em defeito pequeno<br/>e sem sobrecarga de volume relevante do VE —<br/>indicação por progressão de insuficiência aórtica<br/>associada a prolapso. Evitar posição de 'clamping'<br/>do dispositivo sobre a cúspide, associada a maior<br/>progressão de regurgitação aórtica no seguimento"])

  D5 -->|"Não: anatomia desfavorável<br/>ou regurgitação aórtica já relevante"| C7(["Fechamento cirúrgico, com reparo ou anuloplastia<br/>da valva aórtica no mesmo tempo cirúrgico,<br/>quando indicado"])

  D4 -->|"Não"| C8(["Não fechar agora — seguimento ecocardiográfico<br/>regular, com atenção dirigida à cúspide aórtica<br/>adjacente ao defeito, pelo risco de prolapso<br/>progressivo mesmo décadas após o diagnóstico"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Por que a árvore separa hemodinâmica de risco valvar

A diretriz ESC 2020 usa **a mesma tabela de resistência vascular pulmonar** já
publicada no fluxograma "Comunicação interatrial e shunt esquerda-direita no
adulto" desta pasta para decidir a CIV com hipertensão pulmonar — com uma
diferença que a árvore preserva: **na CIV e na persistência do canal
arterial, a faixa de 5 unidades Wood ou mais sem Eisenmenger estabelecido é
Classe IIb** (decisão individual cuidadosa em centro especializado), não
Classe III como na comunicação interatrial, e **não existe a opção de
fechamento fenestrado** que existe para a CIA — a fisiologia ventricular não
comporta essa saída intermediária da mesma forma que a atrial.

**O ramo de risco valvar aórtico é o que diferencia esta árvore da de shunt
esquerda-direita genérico.** Em certos tipos anatômicos — sobretudo CIV
subarterial e perimembranosa tipo 2 (extensão superior-anterior) — o próprio
jato de shunt tracina a cúspide coronariana direita ou não coronariana para
dentro do orifício por efeito Venturi, levando a insuficiência aórtica
progressiva ao longo dos anos, **independentemente do tamanho do defeito**.
É por isso que a árvore chega a indicar fechamento em CIV pequena e sem
sobrecarga de volume relevante do VE: a indicação, nesse ramo, vem da
progressão da valva aórtica, não do shunt.

## O que a árvore não mostra

- **A investigação por imagem que antecede toda a árvore.** O ecocardiograma
  transtorácico localiza o defeito, mede o gradiente transdefeito e avalia
  prolapso/regurgitação da valva aórtica; o ecocardiograma transesofágico é
  recomendado antes de qualquer fechamento percutâneo, para caracterizar
  bordas do defeito e morfologia tridimensional; a ressonância cardíaca
  quantifica sobrecarga de volume do VE quando a janela ecocardiográfica é
  limitada.
- **A classificação anatômica em 7 tipos morfológicos da CIV perimembranosa**
  orienta a escolha do dispositivo quando o fechamento é percutâneo: tipos com
  extensão superior (associados a prolapso aórtico) exigem dispositivos
  flexíveis e de perfil baixo; tipos próximos ao sistema de condução exigem
  implante dentro do aneurisma do septo membranoso, quando presente, para
  reduzir risco de bloqueio atrioventricular.
- **O índice de prolapso da cúspide coronariana direita**, quantificado por
  ecocardiograma transesofágico, é hoje o único preditor independente de
  falha do fechamento por dispositivo em análise multivariada — não é
  observação secundária, é o dado que decide se o dispositivo é viável no
  ramo de risco valvar da árvore.
- **CIV associada a defeito do septo atrioventricular** segue regra própria,
  cirúrgica, já documentada no fluxograma de shunt esquerda-direita desta
  pasta — não os critérios de fechamento por dispositivo descritos aqui.
- **Gestação em mulher com CIV pequena não fechada e resistência vascular
  pulmonar normal** costuma ser bem tolerada; gestação com hipertensão
  arterial pulmonar associada segue contraindicada, mesma regra já registrada
  no fluxograma de shunt esquerda-direita desta pasta.

## Referências

Ver `source_refs` no front matter deste documento. As mesmas fontes já foram
conferidas e usadas no documento "Comunicação Interventricular (CIV) no
Adulto: História Natural, Fechamento Tardio e Prolapso da Valva Aórtica",
publicado nesta pasta — nenhum PMID ou DOI novo foi consultado nesta sessão.
