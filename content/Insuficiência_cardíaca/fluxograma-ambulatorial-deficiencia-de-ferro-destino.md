---
title: "Fluxograma ambulatorial: deficiência de ferro na IC — destino (PS vs ferro EV vs plano)"
slug: fluxograma-ambulatorial-deficiencia-de-ferro-destino
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: alarme (sangramento/instabilidade) → PS; ICFEr/ICFElr sintomática com deficiência → encaminhar ferro EV; demais → plano/rastreio. Sem doses."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-deficiencia-de-ferro-na-ic-quando-escalar (07/09/2026). Além #842/#878. ESC 2021 PMID 34447992; ESC 2023 PMID 37622666. Não substitui o fluxograma ESC 2023 de rastreio/reposição (já revisado)."
source_refs:
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992"
  - "McDonagh TA, Metra M, Adamo M, et al. 2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666"
  - "Ponikowski P, van Veldhuisen DJ, Comin-Colet J, et al. Beneficial effects of long-term intravenous iron therapy with ferric carboxymaltose in patients with symptomatic heart failure and iron deficiency (CONFIRM-HF). Eur Heart J. 2015;36(11):657-668. DOI: 10.1093/eurheartj/ehu385. PMID: 25176939"
---

# Fluxograma ambulatorial: deficiência de ferro na IC — destino

Prosa: [`sinalizadores-ambulatoriais-deficiencia-de-ferro-na-ic-quando-escalar`](sinalizadores-ambulatoriais-deficiencia-de-ferro-na-ic-quando-escalar.md). Encaminhar: [`checklist-ambulatorial-encaminhar-ferro-endovenoso-na-ic`](checklist-ambulatorial-encaminhar-ferro-endovenoso-na-ic.md). Indicação/doses: [`fluxograma-deficiencia-de-ferro-na-insuficiencia-cardiaca-rastreio-e-reposicao-endovenosa-esc-2023`](fluxograma-deficiencia-de-ferro-na-insuficiencia-cardiaca-rastreio-e-reposicao-endovenosa-esc-2023.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta IC: astenia / anemia /\nferritina-saturação já pedidas"] --> D1{"Alarme imediato?\nsangramento ativo, instabilidade,\nIC descompensada grave,\nreação grave a ferro EV"}

  D1 -->|"Sim"| C1(["PS / urgência AGORA\nNão protocolar ferro EV aqui\nInvestigar causa no ambiente adequado"])

  D1 -->|"Não"| D2{"Há deficiência de ferro\npelos critérios ESC?\n(ferritina baixa OU\nferritina intermediária + TSAT baixa)"}

  D2 -->|"Não / desconhecido"| C2(["Rastrear ou repetir periodicamente\nHemograma + ferritina + TSAT\nPlano escrito; retorno programado"])

  D2 -->|"Sim"| D3{"FEVE \u003c 50%\n(ICFEr ou ICFElr)\nE sintomático?"}

  D3 -->|"Não — ICFEp ou assintomático"| C3(["Investigar causa da deficiência\nSem indicação ESC formal de EV\npara desfecho de IC — caso a caso"])

  D3 -->|"Sim"| D4{"Já há plano de ferro EV\nou ciclo recente em janela\nde reavaliação?"}

  D4 -->|"Não"| C4(["Encaminhar cedo a ferro EV /\ncentro de infusão\nChecklist irmão — SEM doses aqui\nInvestigar causa em paralelo"])

  D4 -->|"Sim"| C5(["Manter plano / aguardar\njanela de reavaliação de\nferritina-TSAT (ver fluxograma revisado)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5 conduta;
```

## Notas

- **D1** = gate de segurança (sangramento/instabilidade ≠ “só ferro”).
- **D2** = critérios laboratoriais no fluxograma ESC 2023 **já revisado** — não redefinir cortes neste desenho.
- **D3** = escopo da recomendação 2023 (ICFEr/ICFElr sintomática).
- **C4** = destino operacional; miligramas e formulação ficam no documento revisado.
- Não decide congestão (#842) nem encaminhamento de IC avançada (#878).
