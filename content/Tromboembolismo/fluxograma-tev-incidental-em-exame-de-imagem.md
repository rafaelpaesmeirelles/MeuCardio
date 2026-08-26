---
title: "Fluxograma: TEV incidental achado em exame de imagem por outro motivo"
slug: fluxograma-tev-incidental-em-exame-de-imagem
theme: "Tromboembolismo"
kind: fluxograma
fonte_producao: chatgpt
summary: "TEP ou TVP achados incidentalmente num exame pedido por outro motivo — mais comum em oncologia — costumam exigir a mesma anticoagulação terapêutica do evento sintomático; a exceção reconhecida é o TEP subsegmentar isolado, único, sem fator de risco adicional, onde vigilância pode ser considerada."
review_status: revisado
review_note: "PMIDs conferidos individualmente no PubMed via E-utilities (esummary) nesta sessão: 31504429 (ESC 2019 diretriz de TEP agudo, seção sobre TEP incidental, Konstantinides SV, Eur Heart J 41(4):543-603) e 31492632 (diretrizes internacionais ITAC 2019 de tratamento e profilaxia de TEV em câncer, que aborda TEV incidental na população oncológica, Farge D, Lancet Oncology 20(10):e566-e581). Título, revista, volume/página e autor conferidos contra o registro oficial antes de citar. Tema sem fluxograma prévio no acervo — os dois fluxogramas já publicados do tema cobrem diagnóstico de TEP sintomático e sangramento maior em anticoagulado. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS) · European Heart Journal · 2020 · 41(4):543-603 · https://pubmed.ncbi.nlm.nih.gov/31504429/", "2019 international clinical practice guidelines for the treatment and prophylaxis of venous thromboembolism in patients with cancer (ITAC) · The Lancet Oncology · 2019 · 20(10):e566-e581 · https://pubmed.ncbi.nlm.nih.gov/31492632/"]
---

# Fluxograma: TEV incidental achado em exame de imagem

Um achado de trombo em artéria pulmonar ou em veia profunda, num exame pedido
por outro motivo — estadiamento oncológico é o cenário mais comum —, não é
automaticamente "menos grave" por ser assintomático. A diretriz ESC 2019 e as
diretrizes internacionais de TEV em câncer (ITAC) convergem num princípio: a
maioria dos achados incidentais deve ser tratada como o evento sintomático
equivalente. A exceção reconhecida e estreita é o TEP subsegmentar único, sem
fator de risco adicional, onde vigilância pode ser uma alternativa
compartilhada com o paciente.

## Árvore de decisão

```mermaid
flowchart TD
  R0["TEV (TEP ou TVP) achado<br/>incidentalmente em exame de<br/>imagem pedido por outro motivo,<br/>paciente sem sintoma atribuível"] --> D1{"O achado é TEP ou<br/>TVP incidental?"}

  D1 -->|"TEP incidental"| D2{"Localização no tronco, artéria<br/>lobar/segmentar, ou múltiplos ramos<br/>subsegmentares?"}

  D2 -->|"Sim"| C1(["Tratar como TEP sintomático:<br/>anticoagulação terapêutica plena,<br/>com a mesma duração e a mesma<br/>estratificação de risco (PESI/sPESI,<br/>disfunção de VD) do TEP clínico"])

  D2 -->|"Não — subsegmentar<br/>isolado e único"| D3{"O achado foi confirmado após revisão<br/>da angioTC por radiologista experiente?"}

  D3 -->|"Não ou duvidoso"| C2(["Rever a imagem e obter segunda<br/>opinião; evitar anticoagulação<br/>potencialmente nociva por artefato<br/>ou diagnóstico falso-positivo"])

  D3 -->|"Sim"| D5{"Ultrassom compressivo bilateral<br/>mostra TVP proximal?"}

  D5 -->|"Sim"| C1

  D5 -->|"Não"| D6{"Câncer ativo, gravidez, reserva<br/>cardiopulmonar limitada, imobilização<br/>ou outro alto risco de recorrência?"}

  D6 -->|"Sim"| C6(["Individualizar, em geral favorecendo<br/>anticoagulação; no câncer, a evidência<br/>para TEP subsegmentar único sem TVP<br/>é menos definida que para localização<br/>segmentar ou mais proximal"])

  D6 -->|"Não"| C3(["Pode-se considerar vigilância<br/>estruturada sem anticoagulação, com<br/>ultrassom venoso seriado, acesso<br/>rápido à assistência e decisão<br/>compartilhada com o paciente"])

  D1 -->|"TVP incidental"| D4{"Trombose proximal (poplítea ou<br/>mais central), achada<br/>incidentalmente?"}

  D4 -->|"Sim"| C4(["Tratar como TVP sintomática:<br/>anticoagulação terapêutica plena,<br/>com a mesma duração"])

  D4 -->|"Não — TVP distal<br/>isolada incidental"| C5(["Conduta conforme TVP distal isolada<br/>sintomática: anticoagulação ou<br/>vigilância seriada por imagem,<br/>conforme risco de extensão"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**No paciente oncológico, TEP incidental segmentar ou mais proximal, múltiplos
subsegmentares, ou um subsegmentar acompanhado de TVP devem ser tratados como
o evento sintomático equivalente.** Para um único defeito subsegmentar sem TVP,
a evidência é menos definida; câncer ativo pesa a favor de anticoagular, mas a
decisão deve confirmar primeiro que o achado é real e considerar risco de
sangramento e interações.

**A leitura radiológica de "TEP subsegmentar" tem variabilidade
interobservador reconhecida.** Diante de defeito único ou duvidoso, a ESC
orienta discutir o exame com o radiologista e buscar segunda opinião para
evitar diagnóstico falso-positivo e anticoagulação desnecessária. Vigilância
sem anticoagulação só é uma opção depois de excluir TVP proximal bilateral e
garantir seguimento estruturado.

**A escolha do anticoagulante** (heparina de baixo peso molecular, DOAC ou
antagonista de vitamina K) segue os mesmos critérios do TEV sintomático —
função renal, interação medicamentosa, tipo de neoplasia — e não está
representada aqui por não ser específica do caráter incidental do achado.

**TVP incidental de membro superior associada a cateter** segue algoritmo
próprio (decisão entre remover ou manter o cateter, ao lado da anticoagulação)
e não está coberta por esta árvore, que trata do território venoso profundo de
membros inferiores e do leito pulmonar.
