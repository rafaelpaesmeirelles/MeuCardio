---
title: "Fluxograma: Angina estável refratária — manejo escalonado além da terapia padrão"
slug: fluxograma-angina-estavel-refrataria-manejo-escalonado
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: chatgpt
summary: "Caminho decisório para o paciente que permanece sintomático apesar de terapia antianginosa otimizada e revascularização já considerada: da otimização de 2ª linha até as terapias intervencionistas específicas para angina refratária (redutor de seio coronário, neuroestimulação medular, EECP)."
review_status: revisado
review_note: "PMIDs conferidos nesta sessão via PubMed E-utilities (esearch/esummary): 39210710 (ESC 2024 CCS), 38015442 (ORBITA-2, Rajkumar CA et al., NEJM 2023;389(25):2319-2330) e 25651246 (Verheye S et al., NEJM 2015;372(6):519-527, ensaio COSIRA do redutor de seio coronário) — título, revista, ano e volume/páginas batendo exatamente com o texto do documento. Nenhuma dose, corte numérico ou indicação foi escrita de memória; onde a diretriz não estratifica formalmente a escolha entre as terapias intervencionistas de 3ª linha, isso está declarado em 'O que a árvore não mostra'."
source_refs: ["Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes · European Heart Journal · 2024 · 45(36):3415-3537 · PMID: 39210710", "Rajkumar CA, Foley MJ, Ahmed-Jushuf F, et al. A Placebo-Controlled Trial of Percutaneous Coronary Intervention for Stable Angina (ORBITA-2) · New England Journal of Medicine · 2023 · 389(25):2319-2330 · PMID: 38015442", "Verheye S, Jolicœur EM, Behan MW, et al. Efficacy of a device to narrow the coronary sinus in refractory angina (COSIRA) · New England Journal of Medicine · 2015 · 372(6):519-527 · PMID: 25651246"]
---

# Fluxograma: Angina estável refratária — manejo escalonado

Angina refratária é definida pela persistência de sintomas isquêmicos apesar de
tratamento antianginoso otimizado **e** de revascularização já realizada ou
formalmente considerada inviável. É uma minoria dos pacientes com doença
coronariana crônica, mas o cardiologista clínico esbarra nela com frequência
maior do que o volume de evidência sugere — as opções de 3ª linha (redutor de
seio coronário, neuroestimulação medular, contrapulsação externa
intensificada/EECP) têm nível de evidência mais baixo que o restante do
arsenal antianginoso, e a diretriz ESC 2024 não estabelece uma hierarquia
rígida entre elas. O fluxograma abaixo organiza a sequência de decisões antes
de chegar a esse ponto, e como escolher entre as opções quando se chega.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Angina apesar de tratamento antianginoso otimizado,<br/>com revascularização já considerada"] --> D1{"Recebe ao menos duas classes de antianginosos<br/>em dose otimizada, incluindo opção de 2ª linha<br/>(ivabradina, ranolazina, trimetazidina ou nitrato de longa ação)?"}

  D1 -->|"Não"| C1(["Otimizar o tratamento farmacológico:<br/>associar antianginoso de 2ª linha antes de<br/>considerar procedimento para angina refratária"])

  D1 -->|"Sim"| D2{"Existe lesão coronariana anatomicamente<br/>revascularizável (incluindo oclusão total crônica)<br/>ainda não tratada?"}

  D2 -->|"Sim"| C2(["Encaminhar para revascularização<br/>(ICP, incluindo tentativa de OTC, ou CRM),<br/>guiada por anatomia e território isquêmico"])

  D2 -->|"Não — angina refratária verdadeira"| D3{"Paciente é candidato e tem acesso a terapia<br/>intervencionista específica para angina refratária<br/>(redutor de seio coronário, neuroestimulação<br/>medular ou EECP)?"}

  D3 -->|"Não — contraindicação, indisponibilidade<br/>ou recusa"| C3(["Manter otimização clínica máxima e<br/>reabilitação cardiovascular supervisionada;<br/>reavaliar periodicamente"])

  D3 -->|"Sim"| D4{"Anatomia venosa favorável ao implante do<br/>redutor de seio coronário, sem contraindicação<br/>ao procedimento?"}

  D4 -->|"Sim"| C4(["Implante do redutor de seio coronário<br/>(dispositivo de estreitamento do seio coronário)"])

  D4 -->|"Não"| C5(["Considerar neuroestimulação medular ou EECP,<br/>conforme disponibilidade local e perfil do paciente"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**A ORBITA-2 mudou a leitura de "já tentei tudo" antes da 3ª linha.** O
ensaio, duplo-cego e controlado por placebo (sham), mostrou que a ICP reduz
angina mesmo em pacientes já otimizados clinicamente — o que reforça que a
revascularização anatomicamente possível (mesmo de oclusão total crônica)
deve ser exaurida antes de rotular alguém como refratário verdadeiro. A
árvore reflete isso ao colocar D2 (lesão revascularizável) antes de qualquer
terapia de 3ª linha.

**Não há hierarquia formal entre redutor de seio coronário, neuroestimulação
medular e EECP.** A diretriz ESC 2024 lista as três como opções de
classe IIb, sem comparação direta entre elas. A árvore usa a anatomia venosa
favorável como critério de desempate porque é a única checagem objetiva e
rápida disponível à beira do leito — na prática, disponibilidade local e
experiência do centro pesam tanto quanto a anatomia.

**O nível de evidência da 3ª linha é modesto e precisa ser comunicado ao
paciente.** O ensaio do redutor de seio coronário (COSIRA) randomizou 104
pacientes e teve como desfecho primário a melhora de pelo menos duas classes
da Canadian Cardiovascular Society (CCS) ou pelo menos uma classe para
CCS I — um desfecho sintomático subjetivo, sem poder para mortalidade ou
eventos cardiovasculares maiores.

**Vasoespasmo e disfunção microvascular (ANOCA/INOCA) não entram nesta
árvore.** Angina refratária pressupõe doença coronariana obstrutiva já
conhecida; quando a angiografia é normal ou quase normal, a investigação
segue outra via, tratada em documento próprio da biblioteca.
