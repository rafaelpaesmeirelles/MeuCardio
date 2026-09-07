---
title: "Fluxograma ambulatorial: sinalizadores diabetes-CV — PS vs retorno precoce vs plano"
slug: fluxograma-ambulatorial-sinalizadores-diabetes-cv-destino
theme: "Diabetes e cardiologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino no diabético visto na cardiologia: gate de alarme (hipoglicemia grave, euDKA/iSGLT2, infecção/pé, instabilidade), braço de intolerância/evento não urgente com retorno precoce, e braço estável — sem doses e além de #826."
review_status: pendente_revisao
review_note: "Irmão dos protocolos hipoglicemia-grave e intolerancia-alarme-sglt2-glp1 (07/09/2026). PIVOT: destino ambulatorial fino; evita #826. Fontes: ESC 2023 PMID 37622656; ADA SoC 2026 Cap. 10 PMID 41358899. Sem doses."
source_refs:
  - "Marx N, Federici M, Schütt K, et al. 2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes. Eur Heart J. 2023;44(39):4043-4140. DOI: 10.1093/eurheartj/ehad192. PMID: 37622656"
  - "American Diabetes Association Professional Practice Committee. Cardiovascular Disease and Risk Management: Standards of Care in Diabetes—2026. Diabetes Care. 2026;49(Suppl 1):S216-S245. DOI: 10.2337/dc26-S010. PMID: 41358899"
---

# Fluxograma ambulatorial: sinalizadores diabetes-CV — destino

Prosa: [`sinalizadores-ambulatoriais-hipoglicemia-grave-no-consultorio-de-cardiologia`](sinalizadores-ambulatoriais-hipoglicemia-grave-no-consultorio-de-cardiologia.md) · [`sinalizadores-ambulatoriais-intolerancia-e-alarme-sglt2-glp1-sem-doses`](sinalizadores-ambulatoriais-intolerancia-e-alarme-sglt2-glp1-sem-doses.md).

Não substitui #826 (lesão de órgão-alvo / IC-FA), CAD euglicêmica detalhada, nem CVOTs de classe.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento<br/>diabético na cardiologia"] --> D1{"Alarme imediato?<br/>hipoglicemia grave / síncope / convulsão<br/>suspeita euDKA ou sepse geniturinária<br/>abdômen agudo / anafilaxia<br/>pé infectado grave / instabilidade"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA<br/>Glicemia ± cetonas se iSGLT2<br/>Não titular em casa"])

  D1 -->|"Não"| D2{"Intolerância / evento de segurança<br/>não urgente?<br/>GI persistente GLP-1<br/>micose/ITU recorrente iSGLT2<br/>hipoglicemia leve recorrente<br/>em insulina/secretagogo"}

  D2 -->|"Sim"| P1["Precipitantes + adesão<br/>Articular diabetes/endocrino"]
  P1 --> C2(["Retorno precoce<br/>Reavaliar estratégia<br/>Sem inventar doses neste fluxo"])

  D2 -->|"Não"| D3{"Estável, tolerando classe,<br/>sem red flag glicêmico/pé?"}

  D3 -->|"Sim"| C3(["Plano escrito de alarmes<br/>Retorno programado<br/>Manter proteção CV conforme indicação"])
  D3 -->|"Não / dúvida"| C4(["Retorno curto prudente<br/>ou cardiologia + diabetes"])

  C2 --> D4{"Acesso a reavaliação OK<br/>e sem piora em horas?"}
  D4 -->|"Não / piora"| C5(["Antecipar PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Completar articulação<br/>Não esperar retorno longo de rotina"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (hipoglicemia grave, euDKA, infecção grave, pé, instabilidade).
- **D2** = intolerância / evento não urgente → retorno precoce + diabetes (**sem doses**).
- **Não decide** lesão de órgão-alvo, SCORE2, rastreio IC/FA (#826), miligramas nem escolha de CVOT.
