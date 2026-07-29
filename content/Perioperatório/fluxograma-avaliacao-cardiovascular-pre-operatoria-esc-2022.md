---
title: "Fluxograma: Avaliação cardiovascular pré-operatória em cirurgia não cardíaca (ESC 2022)"
slug: fluxograma-avaliacao-cardiovascular-pre-operatoria-esc-2022
theme: "Perioperatório"
kind: fluxograma
summary: "Duas árvores da diretriz ESC 2022: a que decide quem investiga antes da cirurgia — em que 'não pedir exame' é recomendação Classe III, não omissão — e a do manejo farmacológico perioperatório, com a diferença entre manter e iniciar betabloqueador."
review_status: revisado
source_refs: ["Halvorsen S, Mehilli J, Cassese S, et al. 2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery · European Heart Journal · 2022 · 43(39):3826-3924 · DOI: 10.1093/eurheartj/ehac270 — Tabela 5 (risco cirúrgico por procedimento) e Tabelas de Recomendação 6, 7 e 8, além da tabela-resumo de mensagens-chave"]
---

# Fluxograma: Avaliação cardiovascular pré-operatória em cirurgia não cardíaca (ESC 2022)

A diretriz de 2022 organiza a avaliação pré-operatória em torno de uma pergunta
que costuma ser pulada: **este paciente precisa de algum exame?** A resposta
negativa não é descuido — é recomendação formal. Pedir ECG, troponina e peptídeo
natriurético de rotina em paciente de baixo risco para cirurgia de baixo ou
intermediário risco é **Classe III**, e amostragem universal de biomarcador para
estratificação também.

Duas outras coisas que a árvore torna difíceis de confundir:

- **Manter e iniciar betabloqueador são decisões opostas.** Manter em quem já usa
  é **Classe I, nível B**. Iniciar de rotina no perioperatório é **Classe III,
  nível A** — recomendado contra, com o nível de evidência mais forte que existe.
- **O risco do procedimento vem antes do risco do paciente.** Sem classificar a
  cirurgia em baixo, intermediário ou alto risco, nenhuma das outras
  recomendações se aplica corretamente, porque quase todas são condicionadas a
  essa faixa.

## O risco cirúrgico do procedimento (Tabela 5 da diretriz)

Estimativa de evento cardiovascular em 30 dias, por tipo de procedimento:

| Faixa | Risco em 30 dias | Exemplos citados na diretriz |
|---|---|---|
| Baixo | menos de 1% | mama, dentária, tireoide, oftalmológica, ginecológica menor, ortopédica menor como meniscectomia, reconstrutiva, cirurgia superficial, ressecção transuretral de próstata, ressecção pulmonar menor por videotoracoscopia |
| Intermediário | de 1 a 5% | carótida assintomática e sintomática, correção endovascular de aneurisma de aorta, cirurgia de cabeça e pescoço, intraperitoneal como esplenectomia, hérnia de hiato e colecistectomia, intratorácica não maior, neurológica ou ortopédica maior como quadril e coluna, angioplastia arterial periférica, transplante renal |
| Alto | mais de 5% | — |

## Árvore de decisão: quem investigar antes da cirurgia

```mermaid
flowchart TD
  R0["Cirurgia não cardíaca eletiva programada"] --> P1["Classificar o risco do procedimento pela Tabela 5:<br/>baixo, abaixo de 1%; intermediário, de 1 a 5%;<br/>alto, acima de 5% de evento cardiovascular em 30 dias"]

  P1 --> D1{"Risco do procedimento e perfil clínico do paciente"}

  D1 -->|"Cirurgia de baixo risco"| C1(["Encaminhar à cirurgia. Coronariografia invasiva<br/>pré-operatória não é recomendada no paciente<br/>cardiologicamente estável — Classe III"])

  D1 -->|"Cirurgia de risco intermediário ou alto,<br/>em paciente de baixo risco clínico:<br/>sem doença cardiovascular conhecida,<br/>sem fator de risco e com menos de 65 anos"| C2(["Não solicitar de rotina ECG, hs-troponina T ou I,<br/>nem BNP ou NT-proBNP — Classe III.<br/>Encaminhar à cirurgia"])

  D1 -->|"Cirurgia de risco intermediário ou alto,<br/>em paciente com doença cardiovascular conhecida,<br/>fator de risco cardiovascular incluindo idade<br/>de 65 anos ou mais, ou sintoma ou sinal<br/>sugestivo de doença cardiovascular"| P2["Primeira camada de avaliação: ECG de 12 derivações<br/>— Classe I, nível C; hs-troponina T ou I antes e com<br/>24 e 48 horas de pós-operatório — Classe I, nível B;<br/>medir BNP ou NT-proBNP deve ser considerado<br/>— Classe IIa, nível B"]

  P2 --> D2{"O que a primeira camada e o exame clínico mostraram,<br/>e para que porte de cirurgia?"}

  D2 -->|"Cirurgia de alto risco, com capacidade funcional ruim<br/>e/ou NT-proBNP ou BNP elevado, ou sopro detectado"| P3["Ecocardiograma transtorácico, para permitir<br/>estratégias de redução de risco<br/>— Classe I, nível B"]

  P3 --> D3{"Probabilidade de doença coronariana<br/>e risco clínico global"}

  D3 -->|"Capacidade funcional ruim com alta probabilidade<br/>de doença coronariana ou alto risco clínico"| C3(["Imagem de estresse antes da cirurgia eletiva<br/>de alto risco — Classe I, nível B"])

  D3 -->|"Sem esse perfil"| C4(["Seguir para a cirurgia com as estratégias<br/>de redução de risco. Coronariografia invasiva<br/>de rotina não é recomendada no paciente estável<br/>com síndrome coronariana crônica — Classe III"])

  D2 -->|"Cirurgia de alto risco, com suspeita de doença<br/>cardiovascular nova ou sinal ou sintoma inexplicado"| C5(["Ecocardiograma transtorácico deve ser considerado<br/>— Classe IIa"])

  D2 -->|"Cirurgia de risco intermediário, com capacidade<br/>funcional ruim, ECG alterado, NT-proBNP ou BNP elevado,<br/>ou ao menos um fator de risco clínico"| C6(["Ecocardiograma transtorácico pode ser considerado<br/>— Classe IIb"])

  D2 -->|"Nenhum desses achados"| C7(["Seguir para a cirurgia, mantendo a dosagem<br/>de hs-troponina no pós-operatório"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Árvore de decisão: manejo farmacológico perioperatório

```mermaid
flowchart TD
  R1["Paciente com risco pré-operatório já estimado,<br/>definindo o que fazer com cada fármaco"] --> D4{"Qual classe está em questão?"}

  D4 -->|"Betabloqueador"| D5{"O paciente já usa<br/>cronicamente?"}

  D5 -->|"Sim"| C8(["Manter no perioperatório<br/>— Classe I, nível B"])

  D5 -->|"Não, virgem de tratamento"| C9(["Não iniciar de rotina no perioperatório<br/>— Classe III, nível A.<br/>Iniciar antes da cirurgia pode ser considerado apenas<br/>em quem tem doença coronariana conhecida<br/>ou isquemia miocárdica — Classe IIb, nível B"])

  D4 -->|"Estatina"| D6{"O paciente já usa?"}

  D6 -->|"Sim"| C10(["Manter a estatina durante todo o período<br/>perioperatório — Classe I, nível B"])

  D6 -->|"Não"| C11(["Controlar os fatores de risco cardiovascular antes<br/>da cirurgia — pressão arterial, dislipidemia e diabetes<br/>— Classe I, nível B"])

  D4 -->|"Inibidor do sistema<br/>renina-angiotensina-aldosterona"| D7{"O paciente tem<br/>insuficiência cardíaca?"}

  D7 -->|"Sim, insuficiência cardíaca estável"| C12(["Manter no perioperatório pode ser considerado<br/>— Classe IIb, nível C"])

  D7 -->|"Não"| C13(["Suspender no dia da cirurgia deve ser considerado,<br/>para prevenir hipotensão perioperatória — Classe IIa"])

  D4 -->|"Antiagregante após<br/>intervenção coronariana"| D8{"Qual foi o evento<br/>ou procedimento índice?"}

  D8 -->|"Angioplastia eletiva"| C14(["Adiar a cirurgia não cardíaca eletiva<br/>por 6 meses — Classe I, nível A"])

  D8 -->|"Síndrome coronariana aguda"| C15(["Adiar a cirurgia não cardíaca eletiva<br/>por 12 meses — Classe I, nível A"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C8,C9,C10,C11,C12,C13,C14,C15 conduta;
```

## Capacidade funcional: o exame mais barato da lista

A diretriz transforma capacidade funcional em pergunta objetiva: **ajustar a
avaliação de risco pela capacidade autorrelatada de subir dois lances de escada
deve ser considerado** em quem vai para cirurgia de risco intermediário ou alto —
**Classe IIa**. Não custa nada, não depende de agenda de exame, e é o que separa
o paciente que segue direto do paciente que ganha ecocardiograma.

**Fragilidade tem rastreio próprio.** A partir dos 70 anos, antes de cirurgia de
risco intermediário ou alto, rastrear fragilidade com instrumento validado deve
ser considerado — **Classe IIa**. Fragilidade e capacidade funcional não são a
mesma coisa e não se substituem.

## O que as árvores não mostram

**Cessação de tabagismo com mais de 4 semanas de antecedência é Classe I,
nível B** para reduzir complicação e mortalidade pós-operatórias. Vale para todos
os ramos, e por isso saiu do diagrama.

**Função renal e obesidade têm recomendação própria.** Rastrear doença renal
pré-operatória com creatinina sérica e taxa de filtração glomerular é Classe I
antes de cirurgia de risco intermediário ou alto; e avaliar aptidão
cardiorrespiratória no paciente obeso, com atenção especial a esses mesmos
portes de cirurgia, também é Classe I.

**Cirurgia eletiva em insuficiência cardíaca descompensada não é para ser
feita** — a diretriz é explícita. O ecocardiograma que embasa essa decisão não
deve ter mais de 6 meses, ou deve ser refeito imediatamente antes se houver
piora clínica.

**Betabloqueador para prevenir fibrilação atrial pós-operatória em cirurgia não
cardíaca é Classe III.** É um uso diferente do da árvore — lá a pergunta é sobre
proteção miocárdica, aqui é sobre arritmia —, e nos dois a resposta é não iniciar.

**Vigilância pós-operatória não é opcional no paciente que entrou na árvore
grande.** A recomendação de hs-troponina é explicitamente seriada: antes, com
24 horas e com 48 horas. Medir só no pré-operatório cumpre metade da
recomendação e perde exatamente a lesão miocárdica pós-operatória, que é
assintomática na maioria dos casos.
