---
title: "Fluxograma: Intolerância a Estatina — Definição por CK e Protocolo de Reexposição (EAS 2015)"
slug: fluxograma-intolerancia-a-estatina-definicao-e-protocolo-de-reexposicao
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Stroes ES, Thompson PD, Corsini A, Vladutiu GD, Raal FJ, Ray KK, Roden M, Stein E, Tokgözoğlu L, Nordestgaard BG, Bruckert E, De Backer G, Krauss RM, Laufs U, Santos RD, Hegele RA, Hovingh GK, Leiter LA, Mach F, März W, Newman CB, Wiklund O, Jacobson TA, Catapano AL, Chapman MJ, Ginsberg HN; European Atherosclerosis Society Consensus Panel. Statin-associated muscle symptoms: impact on statin therapy-European Atherosclerosis Society Consensus Panel Statement on Assessment, Aetiology and Management. Eur Heart J. 2015;36(17):1012-1022. DOI: 10.1093/eurheartj/ehv043. PMID: 25694464. PMCID: PMC4416140."
  - "Herrett E, Williamson E, Brack K, et al; StatinWISE Trial Group. Statin treatment and muscle symptoms: series of randomised, placebo controlled n-of-1 trials. BMJ. 2021;372:n135. DOI: 10.1136/bmj.n135. PMID: 33627334."
  - "Derivado de intolerancia-a-estatina-definicao-operacional-e-protocolo-de-reexposicao-eas-2015.md, já publicado no acervo (Prevenção e lipídios)."
---

# Fluxograma: Intolerância a Estatina — Definição por CK e Protocolo de Reexposição (EAS 2015)

"Intolerância a estatina" costuma ser declarada depois de uma única queixa muscular, sem CK medida nem reexposição documentada. O Consenso da European Atherosclerosis Society (2015) propõe um critério operacional que separa o que precisa de investigação de CK e troca de esquema do que precisa de suspensão imediata — e reserva o rótulo de "intolerante à classe" para depois de um protocolo estruturado de suspensão e reexposição, geralmente com ao menos três estatinas diferentes.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em uso de estatina relata sintoma muscular<br/>(dor, fraqueza ou cãibra) — Consenso EAS 2015"] --> D1{"Nível de CK (creatina quinase)"}

  D1 -->|"Normal a menos de 4 vezes<br/>o limite superior da normalidade (LSN)"| C1(["Causalidade incerta: ensaios controlados por<br/>placebo não mostram excesso de sintoma<br/>muscular nesta faixa de CK. Não suspender a<br/>estatina por este achado isolado; considerar<br/>protocolo de suspensão-reexposição estruturado<br/>antes de rotular como sintoma associado à<br/>estatina (SAMS)"])

  D1 -->|"De 4 a menos de 10 vezes o LSN"| D2{"Risco cardiovascular do paciente"}
  D2 -->|"Baixo risco"| C2(["Suspender a estatina e reavaliar a necessidade<br/>de tratamento hipolipemiante; se ainda indicado,<br/>tentar dose menor de estatina alternativa com<br/>monitorização de CK"])
  D2 -->|"Alto risco"| P1["Estatina pode ser continuada, com<br/>monitorização concomitante de CK"]
  P1 --> D3{"CK ultrapassa 10 vezes o LSN<br/>durante o seguimento?"}
  D3 -->|"Sim"| C3(["Suspender a estatina, ao menos<br/>temporariamente; se a CK cair, tentar<br/>reintrodução em dose menor com<br/>monitorização; se a elevação persistir,<br/>considerar causa secundária (hipotireoidismo,<br/>doença muscular metabólica) e encaminhar<br/>a especialista neuromuscular"])
  D3 -->|"Não"| C4(["Manter a estatina, com monitorização<br/>periódica de CK"])

  D1 -->|"10 vezes o LSN ou mais"| D4{"Há causa secundária evidente para a<br/>elevação de CK (ex.: exercício físico<br/>vigoroso extenuante)?"}
  D4 -->|"Sim"| C5(["Investigar e tratar a causa secundária;<br/>reavaliar a CK antes de decidir<br/>sobre a estatina"])
  D4 -->|"Não"| P2["Suspender a estatina,<br/>pelo risco de rabdomiólise"]
  P2 --> D5{"Houve rabdomiólise confirmada?"}
  D5 -->|"Sim"| C6(["Não reintroduzir a estatina"])
  D5 -->|"Não"| D6{"CK normaliza após a<br/>suspensão da estatina?"}
  D6 -->|"Sim"| C7(["Considerar reexposição com estatina<br/>alternativa em dose menor e<br/>monitorização cuidadosa"])
  D6 -->|"Não"| C8(["CK que não normaliza — ou piora — após<br/>suspender a estatina foge deste algoritmo:<br/>investigar miopatia necrotizante autoimune<br/>associada a estatina (anti-HMGCR)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore não mostra

**O protocolo de reexposição não é uma tentativa única.** O consenso recomenda, em geral, testar **ao menos três estatinas diferentes** (dose, fármaco ou esquema intermitente) antes de declarar o paciente intolerante à classe — só depois dessa sequência esgotada é que se parte para terapia hipolipemiante não estatínica.

**A reexposição cega valida o próprio protocolo**: no ensaio StatinWISE, 200 pacientes que já atribuíam sintoma muscular à estatina foram reexpostos de forma cega a estatina e placebo, alternando em blocos de 2 meses — sem diferença no escore de sintoma muscular entre os braços, e taxa de suspensão quase idêntica (9% vs. 7%). Isso não invalida a queixa do paciente; mostra por que a reexposição estruturada, e não a atribuição de memória, é o que separa causalidade real de coincidência temporal.

**Quando a intolerância é confirmada, a meta de LDL não é abandonada** — combina-se a dose máxima tolerada de estatina (que pode ser baixa ou intermitente) com terapia não estatínica (ezetimiba, ácido bempedoico, inibidor de PCSK9, conforme o cenário).

**A definição de "intolerante a estatina" usada em ensaios como o CLEAR Outcomes é mais ampla e menos rigorosa** que este protocolo — baseia-se em incapacidade ou recusa declarada pelo paciente, sem exigir a sequência estruturada de reexposição do consenso EAS. Vale ter essa diferença em mente ao extrapolar o resultado de um ensaio para um paciente individual.
