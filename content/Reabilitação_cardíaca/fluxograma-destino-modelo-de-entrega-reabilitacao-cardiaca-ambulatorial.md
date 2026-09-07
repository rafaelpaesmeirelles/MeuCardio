---
title: "Fluxograma: destino do modelo de entrega na reabilitação cardíaca ambulatorial"
slug: fluxograma-destino-modelo-de-entrega-reabilitacao-cardiaca-ambulatorial
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino: PS agora vs. escalar para presencial vs. manter domiciliar/híbrido — pacote de destino sem inventar intensidades ou doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo reabilitacao-cardiaca-domiciliar-ou-hibrida-quando-escalar-para-presencial (07/09/2026). Além #831/#858. ESC 2026 DOI ehag099; Cochrane PMID 37888805; Thomas PMID 31082266; ESC 2021 PMID 34458905. Sem doses."
source_refs:
  - "European Society of Cardiology. 2026 ESC Guidelines on cardiac rehabilitation. Eur Heart J. 2026. DOI: 10.1093/eurheartj/ehag099"
  - "McDonagh STJ, Dalal H, Moore S, et al. Home-based versus centre-based cardiac rehabilitation. Cochrane Database Syst Rev. 2023;10(10):CD007130. PMID: 37888805"
  - "Thomas RJ, Beatty AL, Beckie TM, et al. Home-Based Cardiac Rehabilitation: A Scientific Statement From the AACVPR, the AHA, and the ACC. Circulation. 2019;140(1):e69-e89. PMID: 31082266"
  - "Visseren FLJ, Mach F, Smulders YM, et al. 2021 ESC Guidelines on cardiovascular disease prevention in clinical practice. Eur Heart J. 2021;42(34):3227-3337. PMID: 34458905"
---

# Fluxograma: destino do modelo de entrega na reabilitação cardíaca ambulatorial

Prosa: [`reabilitacao-cardiaca-domiciliar-ou-hibrida-quando-escalar-para-presencial`](reabilitacao-cardiaca-domiciliar-ou-hibrida-quando-escalar-para-presencial.md). Sintomas na sessão: [`quando-pausar-o-exercicio-na-sessao-de-reabilitacao-cardiaca-sintomas-de-alarme`](quando-pausar-o-exercicio-na-sessao-de-reabilitacao-cardiaca-sintomas-de-alarme.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em RC fase II<br/>domiciliar / remoto / híbrido"] --> D1{"Há alarme agudo?<br/>(angina típica, síncope,<br/>déficit focal, arritmia grave,<br/>hipotensão sintomática no esforço)"}

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

- **D1** = gate de segurança (mesma lógica do #858 / hub #831).
- **D2** = escalada de **modelo**, não de intensidade numérica.
- **D3** = permanência só com estabilidade documentável (Thomas 2019; ESC 2026).
- Não decide METs, %FC máxima nem doses de fármacos.
