---
title: "Fluxograma ambulatorial: PDE5 — quando evitar e escalar"
slug: fluxograma-ambulatorial-pde5-quando-evitar-e-escalar
theme: "Farmacologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: paciente cardiológico pede ou usa PDE5 → filtro nitrato/riociguate/SCA → liberar vs contraindicar vs emergência por hipotensão — sem doses de DE."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-pde5-e-nitrato (07/09/2026). AHA 2012 PMID 22267846; Princeton III PMID 22862865; ESC CCS 2019. Anti-colisão com monografia sildenafila-citrato, #843/#874 coronária, #841 HP."
source_refs:
  - "Levine GN, Steinke EE, Bakaeen FG, et al. Sexual activity and cardiovascular disease: a scientific statement from the American Heart Association. Circulation. 2012;125(8):1058-1072. DOI: 10.1161/CIR.0b013e3182447787. PMID: 22267846"
  - "Nehra A, Jackson G, Miner M, et al. The Princeton III Consensus recommendations for the management of erectile dysfunction and cardiovascular disease. Mayo Clin Proc. 2012;87(8):766-778. DOI: 10.1016/j.mayocp.2012.06.015. PMID: 22862865"
  - "Knuuti J, Wijns W, Saraste A, et al. 2019 ESC Guidelines for the diagnosis and management of chronic coronary syndromes. Eur Heart J. 2020;41(3):407-477. DOI: 10.1093/eurheartj/ehz425"
---

# Fluxograma ambulatorial: PDE5 — quando evitar e escalar

Prosa: [`sinalizadores-ambulatoriais-pde5-e-nitrato`](sinalizadores-ambulatoriais-pde5-e-nitrato.md). Checklist: [`checklist-ambulatorial-pde5-no-retorno-cardiologico`](checklist-ambulatorial-pde5-no-retorno-cardiologico.md). Monografia: [`sildenafila-citrato`](sildenafila-citrato.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno cardiológico\nDAC / angina / pós-IAM / IC / HAP"] --> D0{"Usa ou pede PDE5\n(sildenafila / tadalafila / vardenafila)?"}

  D0 -->|"Não"| C0(["Plano habitual\nSe nitrato na bolsa:\neducar CI se um dia usar PDE5"])

  D0 -->|"Sim"| D1{"Filtro duro?\nNitrato contínuo ou recente /\nriociguate / SCA ou angina\ninstável não estabilizada /\nhipotensão sintomática"}

  D1 -->|"Sim"| D2{"Já há alarme?\nSíncope / PA muito baixa /\ndor torácica pós-PDE5"}

  D2 -->|"Sim"| C1(["Emergência agora\nSem nitrato se ainda na janela\n24h sildenafila/vardenafila\nou 48h tadalafila"])
  D2 -->|"Não"| C2(["Não iniciar / suspender PDE5\nRevisar necessidade do nitrato\nEstabilizar coronária se preciso"])

  D1 -->|"Não"| D3{"Risco sexual estratificado\nPrinceton / AHA:\nbaixo ou intermediário estável?"}
  D3 -->|"Sim"| C3(["Pode discutir PDE5\nDocumentar: sem nitrato/riociguate\nTeach-back: dor no peito ≠ nitrato\na janela pós-PDE5"])
  D3 -->|"Não / alto risco"| C4(["Adiar PDE5\nOtimizar isquemia / IC\nReavaliar após estabilização"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C0,C2,C3,C4 conduta;
```

## Notas

- **D1**: CI absoluta PDE5×nitrato e PDE5×riociguate (AHA 2012; monografia); SCA não estabilizado (Princeton III).
- **C1**: dentro da janela pós-PDE5, nitrato de resgate clássico está **proibido** até completar washout.
- **C3**: liberação é de **segurança de interação + estratificação**, não posologia de DE.
- Não decide dose de sildenafila/tadalafila nem substitui urologia/HP.
