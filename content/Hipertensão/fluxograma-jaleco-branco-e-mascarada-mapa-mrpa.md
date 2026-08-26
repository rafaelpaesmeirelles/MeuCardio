---
title: "Fluxograma: Hipertensão do Jaleco Branco e Mascarada — Quando Pedir MAPA/MRPA e Como Decidir o Tratamento"
slug: fluxograma-jaleco-branco-e-mascarada-mapa-mrpa
theme: "Hipertensão"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Corpus conferido antes de escrever (content/Hipertensão/) — os 5 fluxogramas já publicados cobrem emergência hipertensiva por síndrome-alvo, crise adrenérgica do feocromocitoma, classificação/alvo ESC 2024, hipertensão resistente/quarta droga e investigação de hipertensão secundária; nenhum cobre a decisão de quando pedir MAPA/MRPA para jaleco branco/mascarada nem a decisão terapêutica que depende desse resultado — lacuna fechada aqui. A árvore deriva inteiramente da diretriz ESH 2023 (Mancia G et al., J Hypertens. 2023;41(12):1874-2071, PMID 37345492, DOI 10.1097/HJH.0000000000003480), já publicada e citada em profundidade no documento em prosa `hipertensao-do-jaleco-branco-e-mascarada-mapa-mrpa-prevalencia-e-decisao-terapeutica.md`, desta mesma pasta — os cortes diagnósticos (Tabela 4) e as recomendações de classe/nível de rastreio (Classe I, Nível B) e de tratamento farmacológico (Classe II, Nível C) foram conferidos linha a linha naquele documento e reaproveitados aqui, sem reextrair o PDF de novo. O PMID/DOI foi reconferido nesta sessão via PubMed esummary (título, revista, volume, fascículo, páginas e DOI batendo exatamente). Nenhum dado foi fabricado; a categoria de PA de consultório 'normal-alta' (130-139 e/ou 85-89 mmHg) segue a classificação padrão ESH/ESC de PA de consultório, mantida na diretriz de 2023 e já referenciada, em outras faixas, no documento em prosa desta mesma pasta."
source_refs: ["2023 ESH Guidelines for the management of arterial hypertension. Mancia G, Kreutz R, Brunström M, Burnier M, Grassi G, et al. J Hypertens. 2023;41(12):1874-2071. DOI: 10.1097/HJH.0000000000003480. PMID: 37345492 — Seções 14.2 (Hipertensão do jaleco branco), 14.3 (Hipertensão mascarada), 14.4 (WUCH/MUCH), Tabela 4 (cortes diagnósticos por MAPA/MRPA) e Tabela 5 (indicações clínicas de rastreio), com classe/nível de recomendação de rastreio e de tratamento farmacológico já conferidos linha a linha no documento em prosa desta mesma pasta"]
---

# Fluxograma: Hipertensão do Jaleco Branco e Mascarada — Quando Pedir MAPA/MRPA e Como Decidir o Tratamento

Nenhum dos cinco fluxogramas já publicados nesta pasta responde a uma pergunta
de consultório muito comum: diante de uma pressão de consultório específica,
**quando vale a pena pedir MAPA ou MRPA**, e o que fazer com o resultado. O
documento em prosa já publicado nesta mesma pasta traz os cortes diagnósticos
exatos (Tabela 4 da ESH 2023), a prevalência de cada fenótipo e a recomendação
formal de classe/nível — mas em texto corrido, sem o caminho de decisão passo a
passo. Este fluxograma organiza esse caminho em árvore, separando quem nunca
tratou (investigação de jaleco branco ou de mascarada) de quem já está em
tratamento (investigação de WUCH — jaleco branco não controlada — ou de MUCH —
mascarada não controlada), e termina sempre na decisão prática: tratar com
fármaco ou não.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em avaliação de pressão arterial"] --> D1{"Já está em uso de anti-hipertensivo?"}

  D1 -->|"Não, sem tratamento anti-hipertensivo"| P1["Medir PA de consultório com técnica padronizada, repetida em pelo menos 2 consultas"]
  D1 -->|"Sim, já em tratamento anti-hipertensivo"| P6["Medir PA de consultório com técnica padronizada, em vigência do tratamento atual"]

  P1 --> D2{"Em que faixa cai a PA de consultório?"}
  D2 -->|"Menor que 130/85 mmHg (normal)"| C1(["Sem indicação rotineira de MAPA/MRPA para rastreio de jaleco branco/mascarada:<br/>seguir diagnóstico e meta pressórica da diretriz vigente (ESC 2024/SBC),<br/>com reavaliação periódica"])
  D2 -->|"130-139 e/ou 85-89 mmHg (normal-alta)"| P2["Indicação de rastreio de hipertensão mascarada — Classe I, Nível B (ESH 2023):<br/>solicitar MAPA e/ou MRPA, idealmente os dois métodos"]
  D2 -->|"140/90 mmHg ou mais, sobretudo grau 1 (140-159/90-99 mmHg)"| P3["Indicação de rastreio de hipertensão do jaleco branco — Classe I, Nível B (ESH 2023):<br/>solicitar MAPA e/ou MRPA, idealmente os dois métodos"]

  P2 --> D3{"MAPA e/ou MRPA confirmam PA elevada fora do consultório?<br/>(MAPA 24h ≥130/80 · vigília ≥135/85 · sono ≥120/70 · MRPA ≥135/85 mmHg)"}
  D3 -->|"Não, PA fora do consultório normal"| C2(["Normotensão verdadeira confirmada — não é hipertensão mascarada:<br/>seguimento habitual, reavaliação periódica de rotina"])
  D3 -->|"Sim, PA elevada fora do consultório confirmada"| P4["Hipertensão mascarada confirmada — idealmente com concordância entre MAPA e MRPA<br/>(a reprodutibilidade do fenótipo é limitada)"]

  P4 --> D4{"Lesão de órgão-alvo presente ou risco cardiovascular particularmente elevado?"}
  D4 -->|"Sim"| C3(["Considerar tratamento farmacológico — Classe II, Nível C (ESH 2023):<br/>não há ensaio randomizado dedicado à hipertensão mascarada — associar<br/>intervenção no estilo de vida e seguimento mais próximo (Classe I)"])
  D4 -->|"Não"| C4(["Tratamento farmacológico não recomendado rotineiramente:<br/>intervenção no estilo de vida e seguimento mais próximo (Classe I);<br/>reavaliar por MAPA/MRPA periodicamente, pela reprodutibilidade limitada do fenótipo"])

  P3 --> D5{"MAPA e/ou MRPA confirmam PA elevada também fora do consultório?"}
  D5 -->|"Sim, PA elevada confirmada fora do consultório"| C5(["Hipertensão sustentada verdadeira confirmada — NÃO é jaleco branco:<br/>tratar conforme diretriz vigente de hipertensão (ESC 2024/SBC)"])
  D5 -->|"Não, PA normal fora do consultório"| P5["Hipertensão do jaleco branco confirmada — idealmente com concordância<br/>entre MAPA e MRPA (a reprodutibilidade do fenótipo é melhor que na mascarada,<br/>mas ainda limitada)"]

  P5 --> D6{"Lesão de órgão-alvo presente ou alto risco cardiovascular?"}
  D6 -->|"Sim"| C6(["Considerar tratamento farmacológico — Classe II, Nível C (ESH 2023):<br/>associar avaliação de risco cardiovascular/lesão de órgão-alvo (Classe I, B)<br/>e intervenção no estilo de vida com seguimento mais próximo (Classe I, B)"])
  D6 -->|"Não"| C7(["Tratamento farmacológico não recomendado rotineiramente:<br/>intervenção no estilo de vida e seguimento mais próximo (Classe I, B);<br/>reavaliação periódica de PA e de risco cardiovascular"])

  P6 --> D7{"PA de consultório está controlada (menor que 140/90 mmHg)?"}
  D7 -->|"Sim, controlada no consultório"| P7["Indicação de rastreio de hipertensão mascarada não controlada (MUCH):<br/>solicitar MAPA e/ou MRPA"]
  D7 -->|"Não, PA elevada no consultório apesar do tratamento"| P8["Indicação de rastreio de hipertensão do jaleco branco não controlada (WUCH):<br/>solicitar MAPA e/ou MRPA"]

  P7 --> D8{"MAPA/MRPA mostram PA elevada fora do consultório, apesar do controle no consultório?"}
  D8 -->|"Sim, PA elevada fora do consultório"| C8(["MUCH confirmada (mascarada não controlada) — mesma recomendação de<br/>rastreio de HM/HJB, Classe I, Nível C (ESH 2023): considerar intensificar<br/>a dose se bem tolerada, mesmo sem ensaio de desfecho dedicado a este fenótipo"])
  D8 -->|"Não, PA normal fora do consultório"| C9(["Controle pressórico verdadeiro confirmado — sem MUCH:<br/>manter esquema atual, reavaliação periódica"])

  P8 --> D9{"MAPA/MRPA mostram PA elevada também fora do consultório?"}
  D9 -->|"Não, PA normal fora do consultório"| C10(["WUCH confirmada (jaleco branco não controlada) — mesma recomendação de<br/>rastreio de HM/HJB, Classe I, Nível C (ESH 2023): evitar intensificar a<br/>terapia só com base na medida de consultório; considerar intensificar<br/>apenas se bem tolerada, com reavaliação por MAPA/MRPA"])
  D9 -->|"Sim, PA elevada também fora do consultório"| C11(["Hipertensão não controlada verdadeira confirmada — NÃO é jaleco branco:<br/>intensificar a terapia conforme diretriz vigente de hipertensão (ESC 2024/SBC)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11 conduta;
```

## Por que a árvore se separa logo no início entre tratado e não tratado

A ESH 2023 define hipertensão do jaleco branco e hipertensão mascarada
especificamente em quem **nunca tratou** — são fenótipos diagnósticos. Em
quem já está em tratamento, os nomes mudam para **WUCH** (*white-coat
uncontrolled hypertension*) e **MUCH** (*masked uncontrolled hypertension*),
e a pergunta clínica também muda: não é mais "este paciente tem
hipertensão?", é "o controle que a PA de consultório sugere é real?". Tratar
os dois cenários como se fossem o mesmo caminho de decisão confundiria uma
pergunta diagnóstica com uma pergunta de reavaliação terapêutica — por isso a
bifurcação `D1` vem antes de qualquer corte de PA.

## O que este fluxograma não decide sozinho

A recomendação de tratamento farmacológico em hipertensão do jaleco branco e
em hipertensão mascarada é **Classe II, Nível C** nos dois sentidos — a ESH
2023 é explícita que nunca houve ensaio randomizado dedicado a nenhum dos dois
fenótipos, então a decisão de tratar depende de uma avaliação de lesão de
órgão-alvo e de risco cardiovascular global que este fluxograma não substitui
(nós `D4` e `D6`). A reprodutibilidade limitada dos dois fenótipos — pior na
hipertensão mascarada que na do jaleco branco, e pior por MRPA que por MAPA —
é o motivo pelo qual a diretriz recomenda repetir a medida fora do
consultório antes de fechar qualquer um dos diagnósticos desta árvore, e não
apenas confiar num único MAPA ou MRPA isolado.
