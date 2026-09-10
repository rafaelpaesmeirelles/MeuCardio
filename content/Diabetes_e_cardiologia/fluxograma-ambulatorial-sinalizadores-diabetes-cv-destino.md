---
slug: fluxograma-ambulatorial-sinalizadores-diabetes-cv-destino
title: 'Fluxograma ambulatorial: sinalizadores diabetes-CV — PS vs retorno precoce vs plano'
kind: fluxograma
theme: Diabetes e cardiologia
summary: 'Fluxograma de destino ambulatorial no diabetes: hipoglicemia, cetoacidose, infecção e intolerância terapêutica,
  distinguindo emergência atual de revisão precoce.'
tags: []
source_refs:
- 'ADA. Glycemic Goals, Hypoglycemia, and Hyperglycemic Crises: Standards of Care in Diabetes—2026. Diabetes Care.
  2026;49:S132-S149. DOI: 10.2337/dc26-S006.'
- 'Senneville E, et al. IWGDF/IDSA Guidelines on the Diagnosis and Treatment of Diabetes-related Foot Infections.
  2023. DOI: 10.1093/cid/ciad527.'
- 'Marx N; Federici M; Schütt K. 2023 ESC Guidelines for the management of cardiovascular disease in patients with
  diabetes. Eur Heart J. 2023;44:4043. DOI: 10.1093/eurheartj/ehad192. PMID: 37622663.'
- 'American Diabetes Association Professional Practice Committee for Diabetes*. 10. Cardiovascular Disease and Risk
  Management: Standards of Care in Diabetes-2026. Diabetes Care. 2026;49:S216. DOI: 10.2337/dc26-S010. PMID: 41358899.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: sinalizadores diabetes-CV — destino

Prosa: [sinalizadores-ambulatoriais-hipoglicemia-grave-no-consultorio-de-cardiologia](/biblioteca/sinalizadores-ambulatoriais-hipoglicemia-grave-no-consultorio-de-cardiologia) · [sinalizadores-ambulatoriais-intolerancia-e-alarme-sglt2-glp1-sem-doses](/biblioteca/sinalizadores-ambulatoriais-intolerancia-e-alarme-sglt2-glp1-sem-doses).

Não substitui #826 (lesão de órgão-alvo / IC-FA), CAD euglicêmica detalhada, nem CVOTs de classe.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento<br/>diabético na cardiologia"] --> D1{"Alarme imediato?<br/>hipoglicemia grave ATUAL / síncope / convulsão<br/>suspeita euDKA ou sepse geniturinária<br/>abdômen agudo / anafilaxia<br/>pé infectado grave / instabilidade"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA<br/>Tratar hipoglicemia atual imediatamente<br/>Se euDKA: cetonas + avaliação acidobásica<br/>Não titular em casa"])

  D1 -->|"Não"| D2{"Intolerância / evento de segurança<br/>não urgente?<br/>GI persistente GLP-1<br/>micose/ITU recorrente iSGLT2<br/>hipoglicemia leve recorrente<br/>em insulina/secretagogo"}

  D2 -->|"Sim"| P1["Precipitantes + adesão<br/>Articular diabetes/endocrino"]
  P1 --> C2["Retorno precoce<br/>Reavaliar estratégia<br/>Sem inventar doses neste fluxo"]

  D2 -->|"Não"| D3{"Estável, tolerando classe,<br/>sem red flag glicêmico/pé?"}

  D3 -->|"Sim"| C3(["Plano escrito de alarmes<br/>Retorno programado<br/>Manter proteção CV conforme indicação"])
  D3 -->|"Não / dúvida"| C4(["Retorno curto prudente<br/>ou cardiologia + diabetes"])

  C2 --> D4{"Acesso a reavaliação OK<br/>e sem piora em horas?"}
  D4 -->|"Não / piora"| C5(["Providenciar serviço presencial acessível<br/>no prazo necessário; piora exige avaliação imediata,<br/>PS se alarme ou sem alternativa segura"])
  D4 -->|"Sim"| C6(["Completar articulação<br/>Não esperar retorno longo de rotina"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (hipoglicemia grave, euDKA, infecção grave, pé, instabilidade).
- **D2** = intolerância / evento não urgente → retorno precoce + diabetes (**sem doses**).
- **Não decide** lesão de órgão-alvo, SCORE2, rastreio de IC/FA, miligramas nem escolha de CVOT.

## Segurança operacional

Hipoglicemia nível 3 é alteração mental/física que exige auxílio, independentemente da glicemia. Episódio histórico inteiramente recuperado, com estabilidade e causa avaliada, pede revisão rápida de metas/esquema, educação e plano de resgate; recorrência, convulsão persistente, trauma, isquemia ou arritmia exigem urgência. Confirmar glicemia quando possível sem atrasar resgate; palpitação/pré-síncope mantém diferenciais cardíacos.

Suspeita de euDKA requer cetonas e avaliação acidobásica mesmo com glicemia não elevada, com suspensão temporária do iSGLT2 durante investigação/estado agudo. Dor/edema/eritema perineal desproporcional com febre/toxemia sugere Fournier: emergência. Micose genital ou ITU simples não equivale a sepse/intolerância de classe.

Vômitos persistentes com desidratação/LRA, dor abdominal intensa persistente, suspeita de pancreatite/obstrução ou reação alérgica exigem avaliação urgente; não atribuir automaticamente à GLP-1RA. Pé com infecção grave/sistêmica, isquemia, necrose, abscesso profundo ou progressão rápida pede urgência; úlcera/infecção leve estável segue via rápida de pé diabético.
