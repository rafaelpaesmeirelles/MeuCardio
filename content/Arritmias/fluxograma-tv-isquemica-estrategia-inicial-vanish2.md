---
title: 'Fluxograma: TV isquêmica — estratégia inicial após VANISH2'
slug: fluxograma-tv-isquemica-estrategia-inicial-vanish2
theme: Arritmias
kind: fluxograma
review_status: revisado
source_refs:
- Sapp JL, Tang ASL, Parkash R, Stevenson WG, Healey JS, et al.; VANISH2 Study Team. Catheter Ablation or Antiarrhythmic Drugs
  for Ventricular Tachycardia. N Engl J Med. 2025 Feb 20;392(8):737-747. DOI 10.1056/NEJMoa2409501. Epub 2024 Nov 16. PMID
  39555820. NCT02830360.
review_note: 'Leitura e confronto com VANISH2/CASTLE-HTx: compostos, numeradores, cruzamento e janelas de segurança conferidos;
  removida referência IPD não identificada e exigência indevida de CDI antes de ablação urgente. Vínculos conferidos por slug
  e pertinência clínica: ablacao-de-tv-apos-iam-quando-o-ensaio-sustenta, castle-htx-nao-e-vanish2.'
summary: 'Pergunta desta árvore: neste paciente com cardiomiopatia isquêmica e TV clinicamente significativa, o VANISH2 informa
  a estratégia inicial — ablação versus antiarrítmico — sem pular o CDI? Folhas verdes são condutas. O ensaio ganhou no composto,
  não em mortalidade isolada. Não inventar Classe I nem Classe III. Um pai por nó. Sem ciclo. Folhas em estádio.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: TV isquêmica — estratégia inicial após VANISH2

Pergunta desta árvore: **neste paciente com cardiomiopatia isquêmica e TV clinicamente significativa, o VANISH2 informa a estratégia inicial — ablação versus antiarrítmico — sem pular o CDI?** Folhas verdes são condutas. O ensaio ganhou no **composto**, não em mortalidade isolada. Não inventar Classe I nem Classe III. Um pai por nó. Sem ciclo. Folhas em estádio.

Confirmação em série: cardiomiopatia isquêmica **e** TV clinicamente significativa **e** contexto de CDI. Só então decisão compartilhada. VANISH2 favorece ablação no composto. Risco peri-procedimento: morte em 30 dias **1,0%**. Braço fármaco: morte por toxicidade pulmonar **0,5%**. Não pular CDI se indicado.

## Árvore de decisão

```mermaid
flowchart TD
    R0["TV e suspeita de cardiomiopatia isquêmica<br/>estratégia inicial"] --> D1{"IAM prévio / cardiomiopatia isquêmica?"}

    D1 -->|"Não"| C1(["VANISH2 não se aplica.<br/>Não extrapolar para TV não isquêmica."])

    D1 -->|"Sim"| D2{"TV clinicamente significativa?<br/>tempestade, choque ou ATP apropriado,<br/>ou TV sustentada interrompida por emergência"}

    D2 -->|"Não"| C2(["Fora do recorte VANISH2.<br/>Não pular CDI se o CDI estiver indicado."])

    D2 -->|"Sim"| D3{"CDI já implantado?"}

    D3 -->|"Não"| C3(["Não pular o CDI se indicado.<br/>VANISH2 entrou com CDI em todos.<br/>Ablação não substitui o desfibrilador."])

    D3 -->|"Sim"| D4{"Decisão compartilhada:<br/>ablação ou antiarrítmico como estratégia inicial?"}

    D4 -->|"Ablação"| C4(["VANISH2 favorece ablação no composto.<br/>103/203 50,7% vs 129/213 60,6%;<br/>HR 0,75; IC95% 0,58–0,97; P=0,03.<br/>Morte em 30 dias: 2 1,0%; EA não fatal 23 11,3%.<br/>Não é benefício isolado de mortalidade."])

    D4 -->|"Antiarrítmico"| C5(["Sotalol ou amiodarona segundo critérios pré-especificados.<br/>Composto 129/213 60,6%.<br/>Morte por toxicidade pulmonar: 1 0,5%;<br/>EA não fatal: 46 21,6%.<br/>Não pular CDI. Não inventar classe."])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5 conduta;
```

## Como ler cada folha

**C1 — sem cardiomiopatia isquêmica.** VANISH2 randomizou infarto prévio. TV não isquêmica **não** herda o HR 0,75.

**C2 — TV que não é “clinicamente significativa” no ensaio.** Tempestade, choque ou ATP apropriado, ou TV sustentada interrompida por emergência. Extra-sístole e TV não sustentada isolada **não** abrem C4/C5. Tempestade **entra** em D2 como critério positivo. O CDI, se indicado por outra porta, **não** se omite.

**C3 — CDI ainda não implantado.** Todos os 416 tinham CDI. Ablação **não** substitui o desfibrilador. Avaliar a indicação do CDI com a equipe de eletrofisiologia; a sequência de intervenções depende da urgência clínica, e o ensaio não exige adiar ablação de resgate para implantar um dispositivo. Folha terminal: sem seta de volta para D4. Não pular o dispositivo.

**C4 — ablação como estratégia inicial.** Composto **103/203 (50,7%)** vs **129/213 (60,6%)**; **HR 0,75**; IC95% **0,58–0,97**; **P = 0,03**; mediana **4,3 anos**. Morte em 30 dias: **2 (1,0%)**; EA não fatal: **23 (11,3%)**. O composto inclui morte — **não** traduzir HR 0,75 como mortalidade isolada. Sem Classe I inventada.

**C5 — antiarrítmico como estratégia inicial.** Sotalol ou amiodarona segundo critérios pré-especificados. Composto **129/213 (60,6%)**. Morte por toxicidade pulmonar: **1 (0,5%)**; EA não fatal: **46 (21,6%)**. Os dois braços têm dano nomeável. Não pular CDI.

## O que a árvore não mostra

**VANISH 2016** era ablação versus **escalada** de fármaco. Esta árvore é estratégia **inicial**.

**Instabilidade aguda** pede estabilização agora. Tempestade já revertida **foi** critério de inclusão do VANISH2; não é folha de exclusão.

**Mortalidade isolada.** O primário vencedor do VANISH2 foi composto; não atribuir ao estudo redução comprovada da mortalidade isolada.

**Classe de diretriz.** Esta árvore **não** atribui I, IIa, IIb ou III.

**Reabilitação, IC e coronária** valem nos dois ramos de D4 e ficaram fora do diagrama: não ramificam com VANISH2.

## Tudo com Tudo

- **Arritmias:** esta porta — árvore da estratégia inicial.
- **Dispositivos:** C3 existe para não pular o CDI.
- **Doença coronariana:** D1 é IAM prévio / cardiomiopatia isquêmica.
- **Insuficiência cardíaca:** a FE isquêmica não some porque a TV “ganhou” ablação no composto.
- **Comunicação clínica:** frequências naturais em [Como explicar ablação de TV em vez de só amiodarona](/biblioteca/como-explicar-ablacao-de-tv-em-vez-de-so-amiodarona).
- **Reabilitação cardíaca:** tempestade e choque atrasam a volta à função; C4 e C5 não dispensam o encaminhamento.

### Leituras conectadas

- [Ablação de TV após IAM: quando o ensaio sustenta](/biblioteca/ablacao-de-tv-apos-iam-quando-o-ensaio-sustenta)
- [CASTLE-HTx não é VANISH2: ablação de FA na IC terminal não é ablação de TV](/biblioteca/castle-htx-nao-e-vanish2)
