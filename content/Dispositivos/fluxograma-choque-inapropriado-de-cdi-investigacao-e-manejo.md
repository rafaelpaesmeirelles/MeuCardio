---
title: "Fluxograma: Choque inapropriado de CDI — investigação e manejo"
slug: fluxograma-choque-inapropriado-de-cdi-investigacao-e-manejo
theme: "Dispositivos"
kind: fluxograma
fonte_producao: chatgpt
summary: "Investigação sistemática de um choque de CDI a partir da interrogação do dispositivo: confirmar se a terapia foi apropriada e, quando não foi, distinguir taquicardia supraventricular mal discriminada, sobredetecção não fisiológica por falha de eletrodo, ruído/miopotencial e sobredetecção de onda T — cada causa com reprogramação ou conduta própria."
review_status: revisado
review_note: "PMIDs conferidos individualmente no PubMed via E-utilities (esummary) nesta sessão: 36017572 (ESC 2022 VA/SCD, Zeppenfeld K, Eur Heart J 43(40):3997-4126 — corrige um PMID citado incorretamente em rodada anterior deste projeto, 36017553, que na verdade é a diretriz de avaliação perioperatória), 26949427 (consenso HRS/EHRA/APHRS/SOLAECE 2015 de programação de CDI, Wilkoff BL, J Arrhythm 32(1):1-28) e 23131066 (MADIT-RIT, Moss AJ, NEJM 367(24):2275-2283) — título, revista, volume/página e autor conferidos contra o registro oficial antes de citar."
source_refs: ["2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death · European Heart Journal · 2022 · 43(40):3997-4126 · https://pubmed.ncbi.nlm.nih.gov/36017572/", "2015 HRS/EHRA/APHRS/SOLAECE expert consensus statement on optimal implantable cardioverter-defibrillator programming and testing · Journal of Arrhythmia · 2016 · 32(1):1-28 · https://pubmed.ncbi.nlm.nih.gov/26949427/", "Reduction in inappropriate therapy and mortality through ICD programming (MADIT-RIT) · New England Journal of Medicine · 2012 · 367(24):2275-2283 · https://pubmed.ncbi.nlm.nih.gov/23131066/"]
---

# Fluxograma: Choque inapropriado de CDI — investigação e manejo

Todo choque de CDI, apropriado ou não, deve ser interrogado antes de qualquer
decisão. O passo que evita erro é sempre o mesmo: revisar o eletrograma
armazenado do episódio, não confiar no relato do paciente nem presumir pela
frequência cardíaca isolada. A árvore abaixo parte dessa revisão e segue as
quatro causas mais frequentes de terapia inapropriada — taquicardia
supraventricular mal discriminada, falha de integridade do sistema de
eletrodo, ruído/miopotencial e sobredetecção de onda T —, cada uma com conduta
própria.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Choque(s) do CDI —<br/>interrogar o dispositivo"] --> D1{"Eletrograma armazenado:<br/>a terapia foi apropriada?"}

  D1 -->|"Sim, para TV/FV real"| C1(["Confirmar adequação da terapia;<br/>otimizar substrato e tratamento<br/>farmacológico; manter a programação"])

  D1 -->|"Não, ou permanece incerta"| D2{"Causa do choque inapropriado"}

  D2 -->|"Taquicardia supraventricular<br/>na zona de detecção"| D3{"Discriminadores SVT/VT<br/>já estão otimizados?"}
  D3 -->|"Não"| C2(["Reprogramar discriminadores e zonas<br/>conforme o consenso HRS/EHRA/APHRS/<br/>SOLAECE 2015; ampliar a janela de<br/>monitorização antes da terapia"])
  D3 -->|"Sim, mesmo assim recorrente"| C3(["Tratar a taquiarritmia atrial<br/>(controle de frequência/ritmo ou<br/>ablação) e reduzir a zona de<br/>detecção de VT quando possível"])

  D2 -->|"Sobredetecção não fisiológica<br/>(ruído/miopotencial/interferência)"| D4{"Integridade do sistema de<br/>eletrodo confirmada (impedância,<br/>radiografia)?"}
  D4 -->|"Não — fratura, deslocamento<br/>ou dano de isolamento"| C4(["Reprogramar em modo de segurança<br/>temporário e planejar reintervenção<br/>ou troca do eletrodo"])
  D4 -->|"Sim — sistema íntegro"| C5(["Ajustar sensibilidade, filtro e vetor<br/>de sensing; orientar o paciente sobre<br/>manipulação do gerador"])

  D2 -->|"Sobredetecção de onda T"| C6(["Reprogramar vetor/polaridade de<br/>sensing e sensibilidade dinâmica<br/>conforme o consenso de programação"])

  D2 -->|"Causa não identificada<br/>na interrogação"| C7(["Intensificar a monitorização remota,<br/>reavaliar em consulta próxima e<br/>considerar Holter/monitor externo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**A reprogramação de discriminadores segue princípios do consenso de 2015, não
uma regra única.** O documento recomenda, entre outras medidas, ampliar o
número de intervalos exigidos antes da terapia e usar zonas de detecção mais
altas quando clinicamente seguro — a escolha exata depende da arritmia clínica
de base, não é um ajuste padronizado para todo paciente.

**MADIT-RIT é a evidência de que reprogramar reduz terapia inapropriada e
mortalidade, não só desconforto.** O braço com detecção retardada/zona alta
teve redução de 79% na primeira terapia inapropriada e também menor
mortalidade por todas as causas em relação à programação convencional — é por
isso que a árvore trata reprogramação como conduta ativa, não como medida
paliativa.

**Fratura de eletrodo pode coexistir com terapia apropriada prévia.** Um
sistema que já tratou VT real corretamente no passado não está isento de
desenvolver falha de integridade depois — a checagem de impedância e imagem
vale mesmo quando o histórico do dispositivo é bom.

**O suporte psicológico ao choque, apropriado ou não, não está na árvore** por
não ser um ramo de decisão clínica sobre a programação, mas é parte
recomendada do seguimento — choque de CDI é evento com impacto relatado sobre
qualidade de vida e ansiedade, independentemente da causa identificada.
