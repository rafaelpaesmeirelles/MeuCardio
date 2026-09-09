---
title: "Fluxograma ambulatorial: PDE5 — quando evitar e escalar"
slug: fluxograma-ambulatorial-pde5-quando-evitar-e-escalar
theme: "Farmacologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: paciente cardiológico pede ou usa PDE5 → filtro nitrato/riociguate/SCA → liberar vs contraindicar vs emergência por hipotensão — sem doses de DE."
review_status: revisado
review_note: "Revisão final 08/09/2026: Princeton IV/ESC CCS2024; baixo risco após reclassificação; HAP separada de DE; washout unidirecional e depuração; poppers, última dose e outros PDE5; contraindicação preservada com reconciliação supervisionada."
source_refs:
  - "Kloner RA, et al. Princeton IV consensus guidelines: PDE5 inhibitors and cardiac health. J Sex Med. 2024;21:90–116. DOI: 10.1093/jsxmed/qdad163. PMID: 38148297"
  - "Vrints C, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710"
  - "Levine GN, Steinke EE, Bakaeen FG, et al. Sexual activity and cardiovascular disease: a scientific statement from the American Heart Association. Circulation. 2012;125(8):1058-1072. DOI: 10.1161/CIR.0b013e3182447787. PMID: 22267844"
  - "Nehra A, Jackson G, Miner M, et al. The Princeton III Consensus recommendations for the management of erectile dysfunction and cardiovascular disease. Mayo Clin Proc. 2012;87(8):766-778. DOI: 10.1016/j.mayocp.2012.06.015. PMID: 22862865"
  - "Knuuti J, Wijns W, Saraste A, et al. 2019 ESC Guidelines for the diagnosis and management of chronic coronary syndromes. Eur Heart J. 2020;41(3):407-477. DOI: 10.1093/eurheartj/ehz425"
---

# Fluxograma ambulatorial: PDE5 — quando evitar e escalar

Prosa: [sinalizadores-ambulatoriais-pde5-e-nitrato](/biblioteca/sinalizadores-ambulatoriais-pde5-e-nitrato). Checklist: [checklist-ambulatorial-pde5-no-retorno-cardiologico](/biblioteca/checklist-ambulatorial-pde5-no-retorno-cardiologico). Monografia: [sildenafila-citrato](/biblioteca/sildenafila-citrato).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno cardiológico<br/>DAC / angina / pós-IAM / IC / HAP"] --> D0{"Usa ou pede PDE5<br/>(sildenafila / tadalafila / vardenafila)?"}

  D0 -->|"Não"| C0(["Plano habitual<br/>Se nitrato na bolsa:<br/>educar CI se um dia usar PDE5"])

  D0 -->|"Sim"| D1{"Filtro duro?<br/>Nitrato/nitrito/poppers contínuo ou recente /<br/>riociguate / SCA ou angina<br/>instável não estabilizada /<br/>hipotensão sintomática"}

  D1 -->|"Sim"| D2{"Já há alarme?<br/>Síncope / PA muito baixa /<br/>dor torácica pós-PDE5"}

  D2 -->|"Sim"| C1(["Emergência agora<br/>Sem nitrato se ainda na janela<br/>24h sildenafila/vardenafila<br/>ou 48h tadalafila"])
  D2 -->|"Não"| C2(["DE: não iniciar/não repetir PDE5<br/>HAP: reconciliação imediata especializada<br/>Revisar necessidade do nitrato<br/>Estabilizar coronária se preciso"])

  D1 -->|"Não"| DI{"Indicação do PDE5?"}
  DI -->|"HAP"| CH(["Manter plano especializado<br/>Não suspender por risco sexual isolado"])
  DI -->|"Disfunção erétil"| D3{"Risco sexual estratificado<br/>Princeton / AHA:<br/>baixo após avaliação/reclassificação?"}
  D3 -->|"Sim"| C3(["Pode discutir PDE5<br/>Documentar: sem nitrato/riociguate<br/>Teach-back: dor no peito ≠ nitrato<br/>a janela pós-PDE5"])
  D3 -->|"Intermediário / indeterminado"| CI(["Avaliação adicional, inclusive teste quando indicado<br/>Reclassificar antes de liberar atividade/DE"])
  D3 -->|"Alto risco"| C4(["Adiar PDE5<br/>Otimizar isquemia / IC<br/>Reavaliar após estabilização"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C0,C2,C3,C4 conduta;
```

## Notas

- **D1**: CI absoluta PDE5×nitrato e PDE5×riociguate (AHA 2012; monografia); SCA não estabilizado (Princeton III).
- **C1**: dentro da janela pós-PDE5, nitrato de resgate clássico está **proibido** até avaliação do intervalo mínimo e da depuração.
- **C3**: liberação é de **segurança de interação + estratificação**, não posologia de DE.
- Não decide dose de sildenafila/tadalafila nem substitui urologia/HP.

## Aplicação segura das janelas

Registrar data e hora da última dose, molécula, repetição do uso, função renal/hepática e interações, sobretudo inibidores fortes de CYP3A4. Os mínimos de 24 h para sildenafila/vardenafila e 48 h para tadalafila não garantem segurança se depuração estiver prolongada; requerem avaliação individual e, quando necessário, decisão especializada com monitorização. Não aplicar esses intervalos no sentido nitrato → PDE5: formulação, duração de ação e necessidade clínica do nitrato determinam a transição. Para outros PDE5, como lodenafila, consultar a bula específica; não extrapolar intervalo.

Perguntar diretamente sobre nitritos recreativos/poppers: a combinação também é contraindicada. Reconciliação não significa escolher arbitrariamente qual terapia crônica retirar. Para DE, não repetir PDE5 até avaliação; se já houve uso recente, não administrar nitrato automaticamente. Se PDE5 trata HAP, contatar a equipe especializada imediatamente para impedir coadministração e definir ajuste seguro, sem retirar terapia de HAP com base apenas no risco da atividade sexual.
