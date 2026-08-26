---
title: "Fluxograma: fibrilação atrial de início recente no pronto-socorro"
slug: fluxograma-fa-inicio-recente-pronto-socorro
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Pluymaekers NAHA, Dudink EAMP, Luermans JGLM, et al; RACE 7 ACWAS Investigators. Early or Delayed Cardioversion in Recent-Onset Atrial Fibrillation. New England Journal of Medicine. 2019;380(16):1499-1508. DOI: 10.1056/NEJMoa1900353. PMID: 30883054."
  - "Van der Velden RMJ, Pluymaekers NAHA, Dudink EAMP, et al. Cardioversion strategy impacts rate control during recurrences in patients with paroxysmal atrial fibrillation: A subanalysis of the RACE 7 ACWAS trial. Clinical Cardiology. 2024;47(1):e24161. DOI: 10.1002/clc.24161. PMID: 37872853."
  - "Alboni P, Botto GL, Baldi N, et al. Outpatient treatment of recent-onset atrial fibrillation with the 'pill-in-the-pocket' approach. New England Journal of Medicine. 2004;351(23):2384-2391. DOI: 10.1056/NEJMoa041233. PMID: 15575054."
  - "Derivado dos documentos já publicados no acervo '\"Esperar e Ver\" versus Cardioversão Precoce na FA de Início Recente: o Ensaio RACE 7 ACWAS' e '\"Pill in the Pocket\": Cardioversão Química Ambulatorial na FA de Início Recente' (content/Fibrilação_atrial/), que citam as mesmas fontes acima."
---

# Fluxograma: fibrilação atrial de início recente no pronto-socorro

A prática consagrada era reverter o ritmo imediatamente e mandar o paciente para casa em ritmo sinusal. O RACE 7 ACWAS testou se essa pressa é necessária — e mostrou que, em paciente hemodinamicamente estável, mais de dois terços dos casos revertem sozinhos em 48 horas, sem qualquer procedimento de cardioversão. Já o paciente com FA recorrente e "pill in the pocket" já validado num teste hospitalar prévio segue um caminho totalmente diferente, de autoadministração em casa.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com FA de início recente (até 48 horas), sintomática, avaliado no pronto-socorro"] --> D1{"Estabilidade hemodinâmica?"}

  D1 -->|"Instável (hipotensão, choque, isquemia ou insuficiência cardíaca aguda relacionada à FA)"| C1(["Cardioversão elétrica imediata, sem aguardar reversão espontânea"])

  D1 -->|"Estável"| D2{"O paciente já tem 'pill in the pocket' prescrito e validado em teste hospitalar prévio, para este episódio recorrente?"}

  D2 -->|"Sim"| D3{"Os critérios de segurança do teste original se mantêm (doença cardíaca leve ou ausente, FA bem tolerada, mesmo perfil clínico)?"}
  D3 -->|"Sim"| C2(["Autoadministrar em casa a dose única de flecainida/propafenona já prescrita, evitando nova ida à emergência; manter a avaliação de risco tromboembólico de forma independente"])
  D3 -->|"Não (mudança clínica, nova comorbidade ou dúvida sobre tolerância)"| C3(["Reavaliar no pronto-socorro como um novo episódio; não usar a dose de casa sem essa reavaliação"])

  D2 -->|"Não (primeiro episódio, ou nunca testado sob observação hospitalar)"| D4{"Duração da FA menor que 36 horas e sem indicação de reversão imediata?"}
  D4 -->|"Sim"| P1["Estratégia 'esperar e ver': iniciar controle de frequência (betabloqueador; ou verapamil/diltiazem; ou digoxina) e observar por até 48 horas"]
  P1 --> D5{"Reversão espontânea ao ritmo sinusal dentro de 48 horas?"}
  D5 -->|"Sim"| C4(["Alta em ritmo sinusal; nenhum procedimento de cardioversão foi necessário"])
  D5 -->|"Não"| C5(["Realizar cardioversão farmacológica ou elétrica tardia, conforme disponibilidade e preferência"])

  D4 -->|"Não (duração de 36 horas ou mais, duração indeterminada, ou decisão de reverter de imediato)"| C6(["Seguir a via de cardioversão com anticoagulação periprocedimento guiada por tempo de anticoagulação ou ecocardiograma transesofágico, em vez da estratégia de esperar e ver"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**"Esperar e ver" não é "não tratar".** No RACE 7 ACWAS, o braço de conduta tardia recebia controle de frequência ativo desde a chegada — betabloqueador em primeira escolha, verapamil/diltiazem em segunda, digoxina em terceira, com meta de frequência cardíaca abaixo de 110 bpm — e só era encaminhado à cardioversão se a arritmia persistisse além de 48 horas, um prazo pré-definido, não uma espera indefinida.

**O resultado do RACE 7 ACWAS é de não inferioridade, não de superioridade**: ritmo sinusal em 4 semanas foi de 91% no grupo tardio contra 94% no grupo precoce — a estratégia expectante não piora o desfecho de ritmo, e o ganho prático está em evitar sedação, antiarrítmico ou choque elétrico em pacientes que revertem sozinhos.

**O "pill in the pocket" exige uma etapa de validação hospitalar que não pode ser pulada.** No ensaio original de Alboni et al., 22% dos candidatos foram excluídos do uso ambulatorial por falha de tratamento ou efeito adverso durante o teste sob observação — só quem reverteu com segurança no hospital recebe autorização para tomar a dose em casa. O risco específico a explicar ao paciente é o flutter atrial com condução ventricular rápida, mecanismo pelo qual o fármaco de classe IC pode organizar a fibrilação em um flutter que conduz 1:1 pelo nó atrioventricular.

**Nenhum dos dois caminhos dispensa a avaliação de risco tromboembólico** — a decisão sobre anticoagulação segue as mesmas regras da cardioversão em geral, independentemente da estratégia escolhida no pronto-socorro.