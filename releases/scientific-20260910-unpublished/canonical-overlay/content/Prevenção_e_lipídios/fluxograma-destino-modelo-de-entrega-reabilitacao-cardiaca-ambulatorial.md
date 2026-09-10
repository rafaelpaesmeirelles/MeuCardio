---
slug: fluxograma-destino-modelo-de-entrega-reabilitacao-cardiaca-ambulatorial
title: 'Fluxograma: destino do modelo de entrega na reabilitação cardíaca ambulatorial'
kind: fluxograma
theme: Prevenção e lipídios
summary: 'Árvore ambulatorial de destino: PS agora vs. escalar para presencial vs. manter domiciliar/híbrido — pacote
  de destino sem inventar intensidades ou doses.'
tags: []
source_refs:
- 'McDonagh STJ, Dalal H, Moore S, et al. Home-based versus centre-based cardiac rehabilitation. Cochrane Database
  Syst Rev. 2023;10(10):CD007130. PMID: 37888805'
- 'Thomas RJ, Beatty AL, Beckie TM, et al. Home-Based Cardiac Rehabilitation: A Scientific Statement From the AACVPR,
  the AHA, and the ACC. Circulation. 2019;140(1):e69-e89. PMID: 31082266'
- 'Visseren FLJ, Mach F, Smulders YM, et al. 2021 ESC Guidelines on cardiovascular disease prevention in clinical
  practice. Eur Heart J. 2021;42(34):3227-3337. PMID: 34458905'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma: destino do modelo de entrega na reabilitação cardíaca ambulatorial

Prosa: [reabilitacao-cardiaca-domiciliar-ou-hibrida-quando-escalar-para-presencial](/biblioteca/reabilitacao-cardiaca-domiciliar-ou-hibrida-quando-escalar-para-presencial). Sintomas na sessão: [esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia](/biblioteca/esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em RC fase II<br/>domiciliar / remoto / híbrido"] --> D1{"Há alarme agudo?<br/>(dor persistente/recorrente ou nova preocupante,<br/>síncope,<br/>déficit focal, arritmia grave,<br/>hipotensão sintomática no esforço)"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["DESTINO: PS / emergência agora<br/>Não remarcar sessão remota"])

  D1 -->|"Não"| D2{"Há sinalizador de escalada<br/>para presencial?<br/>(instabilidade relativa, IC duvidosa,<br/>queda, falha de contato, pós-evento,<br/>barreira digital de segurança)"}

  D2 -->|"Sim"| C2(["DESTINO: presencial / centro<br/>Reestratificar risco<br/>Não ‘empurrar’ o remoto"])

  D2 -->|"Não"| D3{"Gates verdes de permanência<br/>intactos? (estabilidade, risco,<br/>autocuidado, canal de retorno)"}

  D3 -->|"Sim"| C3(["DESTINO: manter domiciliar/híbrido<br/>Reavaliar periodicamente<br/>Contato ativo se faltar sessão"])
  D3 -->|"Não / incerto"| C4(["DESTINO: avaliação presencial breve<br/>ou híbrido com âncora no centro<br/>até reestratificar"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef meio fill:#fff8e6,stroke:#b78105,color:#3b2f0a;
  class C1 alerta;
  class C2,C4 meio;
  class C3 conduta;
```

## Notas

- **D1** = gate de segurança (sintomas e sinais de instabilidade).
- **D2** = escalada de **modelo**, não de intensidade numérica.
- **D3** = permanência só com estabilidade documentável (Thomas2019 / ESC2021).
- Não decide METs, %FC máxima nem doses de fármacos.

## Segurança clínica e ocupacional

Interromper a sessão quando ocorrer sintoma preocupante. Dor persistente, recorrente, em repouso ou acompanhada de instabilidade exige emergência. Angina de esforço conhecida que resolve prontamente não implica PS automático, mas exige revisão do plano antes de retomar exercício; sintomas novos requerem avaliação presencial breve, com urgência conforme contexto.

Direção profissional, aviação, máquinas perigosas e trabalho em altura exigem avaliação de medicina do trabalho e critérios regulatórios específicos, incluindo incapacitação súbita, espera após eventos e restrições de dispositivos. Compatibilidade funcional isolada não libera essas funções. Barreiras de compreensão exigem suporte/educação acessível, não exclusão automática do programa ou do trabalho.
