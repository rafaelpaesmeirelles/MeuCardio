---
title: "Fluxograma ambulatorial: pericardite com piora — PS agora vs. retorno precoce vs. especialidade"
slug: fluxograma-ambulatorial-pericardite-piora-destino
theme: "Pericárdio"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino na pericardite: gate de alarme para PS/tamponamento, braço de inflamação controlável com retorno precoce, e braço de recorrência/falha terapêutica para referência especializada."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-pericardite-quando-encaminhar (07/09/2026). ESC 2025 PMID 40878297; ICAP PMID 23992557; RHAPSODY PMID 33200890. Sem doses; anti-colisão com escalonamento refratário e tamponamento."
source_refs:
  - "Schulz-Menger J, Collini V, Gröschel J, Adler Y, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297"
  - "Imazio M, Brucato A, Cemin R, et al. A randomized trial of colchicine for acute pericarditis (ICAP). N Engl J Med. 2013;369(16):1522-1528. DOI: 10.1056/NEJMoa1208536. PMID: 23992557"
  - "Klein AL, Imazio M, Cremer P, et al. Phase 3 Trial of Interleukin-1 Trap Rilonacept in Recurrent Pericarditis (RHAPSODY). N Engl J Med. 2021;384(1):31-41. DOI: 10.1056/NEJMoa2027892. PMID: 33200890"
---

# Fluxograma ambulatorial: pericardite com piora — destino

Prosa: [`sinalizadores-ambulatoriais-pericardite-quando-encaminhar`](sinalizadores-ambulatoriais-pericardite-quando-encaminhar.md). Checklist: [`pericardite-checklist-ambulatorial-de-alarme`](pericardite-checklist-ambulatorial-de-alarme.md). Escalonamento farmacológico: [`fluxograma-pericardite-recorrente-refrataria-escalonamento-terapeutico`](fluxograma-pericardite-recorrente-refrataria-escalonamento-terapeutico.md). Tamponamento: [`fluxograma-tamponamento-cardiaco`](fluxograma-tamponamento-cardiaco.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / contato<br/>com pericardite aguda ou recorrente<br/>e piora referida"] --> D1{"Há alarme de PS?<br/>hipotensão / turgência + bulhas abafadas<br/>dispneia em repouso / síncope<br/>derrame grande sintomático<br/>miopericardite com instabilidade<br/>toxemia / trauma + derrame"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Se tamponamento: fluxograma-tamponamento-cardiaco"])

  D1 -->|"Não"| D2{"Inflamação em evolução sem hipoperfusão?<br/>dor tipicamente pericárdica / PCR elevada<br/>febre baixa / atrito — sem alarme da tabela"}

  D2 -->|"Sim"| P1["Checar adesão AAS/AINE + colchicina<br/>restrição de exercício; ECG ± PCR ± eco<br/>se mudarem conduta"]
  P1 --> C2(["Retorno ambulatorial 24–72 h<br/>Orientação escrita de alarmes"])

  D2 -->|"Não / muito brando"| D3{"Recorrência ou falha à 1ª linha<br/>bem feita / corticoide-dependência?"}

  D3 -->|"Sim"| C3(["Referência especializada<br/>Usar fluxograma de escalonamento<br/>recorrente refratária — sem doses aqui"])
  D3 -->|"Não"| C4(["Plano usual + educação de alarmes<br/>Manter restrição de exercício até remissão<br/>Retorno conforme estabilidade"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora rápida / anticoagulação + derrame"| C5(["Antecipar retorno 24 h ou PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h<br/>Não escalonar anti-IL-1 neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (tamponamento / miopericardite grave / toxemia — ESC 2025).
- **D2** = inflamação ambulatorial controlável → destino clínico precoce.
- **D3** = ponte para o pacote de escalonamento (ICAP para base de colchicina; RHAPSODY/ESC 2025 para anti-IL-1), **sem** decidir fármaco aqui.
- Não decide doses de AINE, colchicina, corticoide nem anti-IL-1.
