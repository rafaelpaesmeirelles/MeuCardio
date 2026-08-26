---
title: "Fluxograma: Qual Escore de Risco Cirúrgico Usar em Cada Cenário Perioperatório"
slug: fluxograma-escolha-escore-risco-cirurgico-perioperatorio
theme: "Calculadoras"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: orcamento de WebSearch da sessao esgotado antes desta tarefa (200/200); nenhuma nova fonte externa foi buscada. Conteudo deriva integralmente de seis documentos ja publicados e revisados no acervo (tema Calculadoras), com PMID/DOI ja conferidos naqueles documentos e reproduzidos aqui sem alteracao — nenhum identificador foi inventado ou extrapolado nesta tarefa."
source_refs:
  - "Lee TH, Marcantonio ER, Mangione CM, Thomas EJ, Polanczyk CA, et al. Derivation and prospective validation of a simple index for prediction of cardiac risk of major noncardiac surgery. Circulation. 1999;100(10):1043-1049. PMID: 10477528 — RCRI, 4.315 pacientes com 50 anos ou mais, coorte de derivação (2.893) e de validação (1.422)"
  - "Ford MK, Beattie WS, Wijeysundera DN. Systematic review: prediction of perioperative cardiac complications and mortality by the revised cardiac risk index. Ann Intern Med. 2010;152(1):26-35. PMID: 20048269 — revisão sistemática de 24 estudos e 792.740 pacientes; RCRI com AUC 0,75 em cirurgia mista e 0,64 em cirurgia vascular"
  - "Gupta PK, Gupta H, Sundaram A, Kaushik M, Fang X, et al. Development and validation of a risk calculator for prediction of cardiac risk after surgery. Circulation. 2011;124(4):381-387. PMID: 21730309 — escore NSQIP MICA, derivação em 211.410 pacientes (2007) e validação em 257.385 (2008)"
  - "Bertges DJ, Goodney PP, Zhao Y, Schanzer A, Nolan BW, Likosky DS, Eldrup-Jorgensen J, Cronenwett JL; Vascular Study Group of New England. The Vascular Study Group of New England Cardiac Risk Index (VSG-CRI) predicts cardiac complications more accurately than the Revised Cardiac Risk Index in vascular surgery patients. J Vasc Surg. 2010;52(3):674-683, 683.e1-683.e3. DOI: 10.1016/j.jvs.2010.03.031. PMID: 20570467 — 10.081 pacientes da Vascular Study Group of New England (2003-2008)"
  - "Nashef SA, Roques F, Sharples LD, Nilsson J, Smith C, Goldstone AR, Lockowandt U. EuroSCORE II. Eur J Cardiothorac Surg. 2012;41(4):734-744. DOI: 10.1093/ejcts/ezs043. PMID: 22378855"
  - "O'Brien SM, Feng L, He X, et al. The Society of Thoracic Surgeons 2018 Adult Cardiac Surgery Risk Models: Part 2-Statistical Methods and Results. Ann Thorac Surg. 2018;105(5):1419-1428. DOI: 10.1016/j.athoracsur.2018.03.003. PMID: 29577924"
  - "Ranucci M, Castelvecchio S, Menicanti L, Frigiola A, Pelissero G. Risk of assessing mortality risk in elective cardiac operations: age, creatinine, ejection fraction, and the law of parsimony. Circulation. 2009;119(24):3053-3061. DOI: 10.1161/CIRCULATIONAHA.108.842393. PMID: 19506110 — escore ACEF, série de desenvolvimento (n=4.557) e de validação (n=4.091)"
---

# Fluxograma: Qual Escore de Risco Cirúrgico Usar em Cada Cenário Perioperatório

A pasta Calculadoras acumulou seis documentos de risco cirúrgico — RCRI/NSQIP MICA, VSG-CRI, EuroSCORE II, STS Risk Score e ACEF —, cada um derivado e validado em uma população diferente, mas nenhum fluxograma amarrava a pergunta que antecede o cálculo: **diante deste paciente, qual desses escores é o certo a aplicar?** Este fluxograma responde a essa pergunta de triagem, sem repetir o cálculo interno de cada escore (que já está documentado em seu respectivo artigo nesta pasta).

## Árvore de decisão

```mermaid
flowchart TD
    A{"Cirurgia cardíaca ou cirurgia não cardíaca?"}
    A -->|"Cirurgia cardíaca (troca valvar, revascularização miocárdica, cirurgia combinada)"| B{"Objetivo: decisão de Heart Team (TAVI/troca percutânea vs. cirurgia aberta) ou estimativa rápida à beira do leito?"}
    A -->|"Cirurgia não cardíaca"| E{"É cirurgia vascular arterial maior (aneurisma de aorta, revascularização de membro, endarterectomia de carótida)?"}

    B -->|"Decisão de Heart Team, dados completos disponíveis"| C1(["Aplicar EuroSCORE II e STS Risk Score lado a lado — nenhum isoladamente exclui o paciente de cirurgia; o STS também estima AVC, insuficiência renal e reoperação por modelo separado, com dados do ACSD"])
    B -->|"Estimativa rápida, cirurgia eletiva, dados completos do EuroSCORE II/STS ainda indisponíveis"| C2(["Usar o escore ACEF (idade ÷ fração de ejeção + 1 se creatinina > 2 mg/dL) como segunda estimativa simples de 3 variáveis, para cruzar com EuroSCORE II/STS assim que os dados completos estiverem disponíveis"])

    E -->|"Sim — cirurgia vascular arterial"| C3(["Usar o VSG-CRI — derivado e validado dentro da própria cirurgia vascular; o RCRI tem discriminação fraca neste cenário (AUC 0,64, revisão sistemática) e tende a subestimar risco em vascular"])
    E -->|"Não — demais cirurgias não cardíacas (geral, ortopédica, ginecológica, etc.)"| F{"Prioridade é simplicidade à beira do leito (6 variáveis clínicas, sem calculadora) ou maior discriminação com ajuste por tipo específico de procedimento?"}

    F -->|"Simplicidade e triagem inicial"| C4(["Usar o RCRI (Revised Cardiac Risk Index) — 6 preditores clínicos simples, sem necessidade de ferramenta online; discrimina razoavelmente em cirurgia mista (AUC 0,75), mas não foi validado para estimar mortalidade isolada"])
    F -->|"Maior discriminação / estratificação fina por procedimento"| C5(["Usar o NSQIP MICA — calculadora online do American College of Surgeons, ajustada por tipo específico de procedimento; discrimina melhor que o RCRI na coorte de derivação, à custa de exigir acesso à ferramenta"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5 conduta;
```

## Por que a bifurcação inicial é cardíaca vs. não cardíaca, e não "qual escore é melhor"

Os seis escores desta pasta não competem pela mesma população — cada um foi derivado em um universo cirúrgico distinto, e usar o modelo errado para o cenário é o erro mais comum na prática, não a escolha entre modelos igualmente válidos:

- **EuroSCORE II** (Nashef SA et al., Eur J Cardiothorac Surg. 2012, PMID 22378855) e **STS Risk Score** (O'Brien SM et al., Ann Thorac Surg. 2018, PMID 29577924) foram desenvolvidos e validados **exclusivamente em cirurgia cardíaca** — o primeiro em 22.381 pacientes de 154 hospitais de 43 países, o segundo em centenas de milhares de procedimentos do banco americano ACSD. Não têm papel em cirurgia não cardíaca.
- **ACEF** (Ranucci M et al., Circulation. 2009, PMID 19506110) também é escore de **cirurgia cardíaca eletiva**, desenhado deliberadamente com apenas 3 variáveis para evitar o sobreajuste dos modelos maiores em populações de baixa mortalidade — não é substituto do EuroSCORE II/STS, é complemento rápido quando os dados completos ainda não estão disponíveis.
- **RCRI** (Lee TH et al., Circulation. 1999, PMID 10477528) foi derivado em **cirurgia não cardíaca eletiva mista**. A revisão sistemática de Ford, Beattie e Wijeysundera (Ann Intern Med. 2010, PMID 20048269; 24 estudos, 792.740 pacientes) mostrou AUC de 0,75 nessa população mista, mas **apenas 0,64 em cirurgia vascular** — pouco acima do acaso.
- **VSG-CRI** (Bertges DJ et al., J Vasc Surg. 2010, PMID 20570467; 10.081 pacientes do Vascular Study Group of New England) foi derivado especificamente para resolver essa fraqueza do RCRI em cirurgia vascular.
- **NSQIP MICA** (Gupta PK et al., Circulation. 2011, PMID 21730309; derivação em 211.410 e validação em 257.385 pacientes) cobre o mesmo universo do RCRI — cirurgia não cardíaca mista —, mas ajusta por tipo específico de procedimento, à custa de exigir a calculadora online em vez de soma manual de pontos.

## Armadilhas clínicas

- Usar EuroSCORE II, STS ou ACEF fora de cirurgia cardíaca — nenhum dos três tem validação para esse cenário.
- Aplicar o RCRI isoladamente em cirurgia vascular esperando a mesma discriminação da cirurgia mista — a própria revisão sistemática que valida o RCRI documenta a queda de AUC 0,75 para 0,64 nesse subgrupo.
- Comparar o percentual do EuroSCORE II diretamente com o do STS Risk Score, ou o do RCRI com o do NSQIP MICA, como se fossem a mesma métrica — são modelos com variáveis e populações de derivação diferentes, sem equivalência direta estabelecida entre eles.
- Usar qualquer um destes seis escores isoladamente para excluir um paciente de cirurgia — todos são insumo quantitativo à decisão compartilhada (Heart Team, avaliação pré-operatória), não substituto do julgamento clínico e da avaliação de fragilidade, que nenhum deles captura integralmente.
- Presumir que a escolha do escore certo elimina a necessidade de avaliação clínica completa — a árvore acima resolve "qual ferramenta calcular", não "o que fazer com o resultado", que depende do contexto clínico e da decisão compartilhada em cada cenário.
