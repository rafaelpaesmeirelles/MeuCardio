---
title: "Fluxograma ambulatorial: miocardite — risco ESC 2025 e destino"
slug: fluxograma-ambulatorial-miocardite-risco-destino
theme: "Pericárdio"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: alto risco → PS/urgência; intermediário → retorno precoce + RMC; baixo risco → plano ambulatorial com restrição de exercício — alinhada à ESC 2025."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-miocardite-quando-encaminhar (07/09/2026). ESC 2025 PMID 40878297. Anti-colisão #846 pericardite, #848 esporte, #834 ICI. Sem doses."
source_refs:
  - "Schulz-Menger J, Collini V, Gröschel J, Adler Y, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297"
---

# Fluxograma ambulatorial: miocardite — risco e destino

Prosa: [`sinalizadores-ambulatoriais-miocardite-quando-encaminhar`](sinalizadores-ambulatoriais-miocardite-quando-encaminhar.md). Checklist: [`miocardite-checklist-ambulatorial-de-alarme`](miocardite-checklist-ambulatorial-de-alarme.md). Diagnóstico/EMB: [`miocardite-diagnostico-estratificacao-de-risco-e-biopsia-endomiocardica-esc-2025`](miocardite-diagnostico-estratificacao-de-risco-e-biopsia-endomiocardica-esc-2025.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>suspeita ou miocardite conhecida"] --> D1{"Alto risco clínico?<br/>IC aguda / choque / NYHA III–IV refratária<br/>síncope / PCR / FV-TV sustentada<br/>BAV alto grau<br/>FEVE <40% ou LGE extenso + piora"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA<br/>PS / urgência / centro<br/>Seguir fluxograma agudo / EMB"])

  D1 -->|"Não"| D2{"Risco intermediário?<br/>dispneia nova/progressiva<br/>TVNS / troponina persistente<br/>FEVE 41–49% ou LGE ≥2 segmentos"}

  D2 -->|"Sim"| P1["ECG + exame focado<br/>Planejar RMC se mudar conduta"]
  P1 --> C2(["Retorno 24–72 h<br/>Alarmes escritos<br/>Restrição de exercício"])

  D2 -->|"Não"| D3{"Baixo risco documentado?<br/>FEVE ≥50%<br/>LGE ausente ou <2 segmentos<br/>oligo/assintomático estável"}

  D3 -->|"Sim"| C3(["Plano ambulatorial<br/>Educação de alarmes<br/>Sem liberar esporte aqui"])
  D3 -->|"Incerto / dados incompletos"| C4(["Tratar como intermediário<br/>até completar ECG/eco/RMC<br/>Retorno curto"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora rápida"| C5(["Antecipar retorno 24 h<br/>ou PS se surgir alto risco"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h<br/>Não protocolar imunossupressão aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (alto risco ESC 2025).
- **D2** = intermediário → destino clínico precoce + imagem.
- **D3** = baixo risco só com dados suficientes; na dúvida, sobe para intermediário.
- Retorno ao esporte e ICI ficam fora deste fluxograma (anti-colisão).
