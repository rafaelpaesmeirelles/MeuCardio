---
title: "Fluxograma: Bradiarritmia — indicação de marcapasso definitivo (ESC 2021)"
slug: fluxograma-bradiarritmia-indicacao-de-marcapasso-esc-2021
theme: "Dispositivos"
kind: fluxograma
summary: "Duas árvores de decisão da diretriz ESC 2021 de estimulação cardíaca: a da bradiarritmia documentada, em que o bloqueio atrioventricular avançado indica marcapasso mesmo sem sintoma, e a da síncope com distúrbio de condução, em que o estudo eletrofisiológico decide."
review_status: revisado
source_refs: ["Glikson M, Nielsen JC, Kronborg MB, et al. 2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy · European Heart Journal · 2021 · 42(35):3427-3520 · DOI: 10.1093/eurheartj/ehab364 · PMID: 34455430", "2021 ESC Guidelines on Cardiac Pacing and CRT: Key Points · American College of Cardiology · 2021 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2021/08/31/18/37/2021-ESC-Guidelines-on-Cardiac-Pacing-ESC-2021"]
---

# Fluxograma: Bradiarritmia — indicação de marcapasso definitivo (ESC 2021)

Duas assimetrias organizam toda a decisão, e quem as inverte erra sempre:

1. **Na disfunção do nó sinusal, quem manda é o sintoma.** Bradicardia sinusal
   assintomática não se estimula — a recomendação é explicitamente contrária
   (Classe III). Sem sintoma atribuível, não há indicação.
2. **No bloqueio atrioventricular avançado, quem manda é o eletrocardiograma.**
   Bloqueio de terceiro grau, de segundo grau tipo 2, 2:1 infranodal ou avançado
   indicam marcapasso **independentemente de sintomas** (Classe I), porque aqui a
   estimulação tem valor prognóstico, não só sintomático.

E antes das duas, a pergunta que anula todo o resto: **a causa é transitória e
corrigível?** Bradiarritmia por fármaco, distúrbio eletrolítico, isquemia aguda
ou processo infeccioso não é indicação de marcapasso — é Classe III enquanto a
causa puder ser corrigida e prevenida.

## Árvore de decisão: bradiarritmia documentada

```mermaid
flowchart TD
  R0["Bradiarritmia ou distúrbio de<br/>condução documentado"] --> D1{"Causa transitória, corrigível<br/>e prevenível?<br/>(fármaco, eletrólito, isquemia aguda, infecção)"}

  D1 -->|"Sim"| C1(["Corrigir a causa e reavaliar.<br/>Marcapasso não recomendado — Classe III"])

  D1 -->|"Não"| D2{"Substrato eletrocardiográfico"}

  D2 -->|"BAV de 3º grau, 2º grau tipo 2,<br/>2:1 infranodal ou BAV avançado"| D3{"Ritmo de base"}
  D3 -->|"Ritmo sinusal"| C2(["Marcapasso, com ou sem sintomas — Classe I.<br/>Preferir DDD ao ventricular de câmara única<br/>(Classe IIa, nível A)"])
  D3 -->|"Fibrilação atrial permanente"| C3(["Marcapasso, com ou sem sintomas — Classe I,<br/>em modo ventricular com resposta<br/>de frequência (VVIR)"])

  D2 -->|"BAV de 2º grau tipo 1<br/>(Wenckebach)"| D4{"Causa sintomas, ou bloqueio<br/>intra/infra-His no estudo<br/>eletrofisiológico?"}
  D4 -->|"Sim"| C4(["Marcapasso deve ser considerado — Classe IIa"])
  D4 -->|"Não"| C5(["Sem indicação de marcapasso:<br/>acompanhamento clínico"])

  D2 -->|"BAV de 1º grau com PR > 0,30 s"| D5{"Sintomas persistentes de síndrome<br/>do marcapasso, claramente<br/>atribuíveis ao PR longo?"}
  D5 -->|"Sim"| C6(["Marcapasso deve ser considerado — Classe IIa"])
  D5 -->|"Não"| C7(["Sem indicação de marcapasso:<br/>acompanhamento clínico"])

  D2 -->|"Disfunção do nó sinusal"| D6{"Os sintomas se atribuem<br/>à bradiarritmia?"}
  D6 -->|"Sim, claramente"| C8(["Marcapasso — Classe I.<br/>Em DDD, programar para minimizar<br/>a estimulação ventricular (Classe I, nível A)"])
  D6 -->|"Provavelmente, sem<br/>evidência conclusiva"| C9(["Marcapasso pode ser considerado — Classe IIb"])
  D6 -->|"Não: assintomático"| C10(["Marcapasso não recomendado — Classe III"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10 conduta;
```

## Árvore de decisão: síncope com distúrbio de condução ou reflexa

```mermaid
flowchart TD
  R1["Síncope inexplicada após<br/>avaliação inicial"] --> D7{"Achado que orienta a conduta"}

  D7 -->|"Bloqueio de ramo alternante"| C11(["Marcapasso, com ou sem sintomas — Classe I"])

  D7 -->|"Bloqueio bifascicular"| D8{"Estudo eletrofisiológico"}
  D8 -->|"HV ≥ 70 ms, bloqueio intra/infra-His de<br/>2º ou 3º grau na estimulação atrial<br/>incremental, ou resposta anormal<br/>ao teste farmacológico"| C12(["Marcapasso — Classe I, nível B"])
  D8 -->|"Estudo normal, em idoso frágil,<br/>alto risco ou síncope recorrente"| C13(["Marcapasso pode ser considerado — Classe IIb"])
  D8 -->|"Estudo normal, sem esses fatores"| C14(["Seguir investigando a síncope;<br/>não implantar por bloqueio isolado"])

  D7 -->|"Bloqueio de ramo ou bifascicular<br/>assintomático, sem síncope"| C15(["Marcapasso não recomendado — Classe III"])

  D7 -->|"Reflexo cardioinibitório documentado,<br/>idade > 40 anos, síncope grave,<br/>imprevisível e recorrente"| C16(["Marcapasso de dupla câmara — Classe I, nível A"])

  D7 -->|"Nenhum reflexo cardioinibitório<br/>documentado"| C17(["Marcapasso não indicado — Classe III"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C11,C12,C13,C14,C15,C16,C17 conduta;
```

## O que conta como reflexo cardioinibitório documentado

A recomendação Classe I, nível A, para marcapasso de dupla câmara na síncope
reflexa exige **idade acima de 40 anos** e síncope **grave, imprevisível e
recorrente**, mais um destes três achados:

- **pausa assistólica espontânea sintomática > 3 s**, ou **pausa assintomática
  > 6 s**, por parada sinusal ou bloqueio atrioventricular;
- **síndrome do seio carotídeo cardioinibitória**;
- **síncope assistólica durante o teste de inclinação**.

Sem reflexo cardioinibitório documentado, a estimulação **não está indicada**
(Classe III) — implantar por síncope recorrente sem documentação é o erro que
essa recomendação existe para impedir.

## Modo de estimulação: o que a árvore só resume

**Na disfunção do nó sinusal**, o DDD é o modo de primeira escolha, mas com uma
condição que vale como recomendação Classe I, nível A: **programar para minimizar
a estimulação ventricular desnecessária**. Estimular o ventrículo direito sem
necessidade favorece fibrilação atrial e deterioração da insuficiência cardíaca,
sobretudo quando a função sistólica já é limítrofe. Um DDD mal programado, nesse
cenário, é pior do que o problema que veio tratar.

**Na incompetência cronotrópica** com sintomas claros ao esforço, deve-se
considerar DDD com resposta de frequência (Classe IIa).

**No bloqueio atrioventricular**, o DDD deve ser preferido ao marcapasso
ventricular de câmara única, para evitar síndrome do marcapasso e melhorar
qualidade de vida (Classe IIa, nível A) — mas **na fibrilação atrial permanente**
não há átrio a sincronizar, e a recomendação é estimulação ventricular com
resposta de frequência (Classe I).

## Duas saídas que evitam o implante

**Ablação da fibrilação atrial** deve ser considerada como estratégia para evitar
o implante em pacientes com bradicardia relacionada à FA ou pausas
pré-automáticas sintomáticas após a reversão (Classe IIa).

**Na forma bradicardia-taquicardia** da disfunção do nó sinusal, o marcapasso é
indicado no paciente sintomático para corrigir a bradiarritmia e **permitir o
tratamento farmacológico** da taquiarritmia (Classe I) — **a menos que a ablação
da taquiarritmia seja preferível**. A ordem importa: perguntar primeiro se a
arritmia rápida pode ser tratada na origem.

## O que as árvores não mostram

**BAV 2:1 com QRS estreito e assintomático** tem uma ressalva na própria
diretriz: a estimulação pode ser evitada quando houver suspeita clínica ou
demonstração de bloqueio supra-hissiano — Wenckebach concomitante e
desaparecimento do bloqueio com o exercício.

**A investigação etiológica é paralela à decisão**: polissonografia, testes
laboratoriais dirigidos, imagem cardíaca quando se suspeita de doença estrutural,
teste de esforço quando o sintoma aparece ao exercício e teste genético na doença
de condução progressiva de início precoce (abaixo de 50 anos). Nada disso é ramo
da árvore, mas muda a causa — e a causa muda a conduta.

**Marcapasso após infarto, após cirurgia cardíaca e após TAVI** tem recomendações
próprias na mesma diretriz, com janelas de espera específicas, e não estão
representados aqui.
