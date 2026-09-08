---
title: "Fluxograma ambulatorial: hipertensão por VEGF/TKI — PS agora vs. pausa vs. retorno precoce"
slug: fluxograma-ambulatorial-hipertensao-por-vegf-tki-destino
theme: "Cardio-oncologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial sob inibidores da via VEGF: gate de lesão aguda/PRES, pausa por PA grave, ramo específico PAS>=160 E PAD>=100 e avaliação separada de sintomas cardiovasculares."
review_status: revisado
review_note: "Revisão clínica final 08/09/2026. Corrigidos operadores ESC (PAS >=180 OU PAD >=110 para pausa; PAS >=160 E PAD >=100 para associação anti-HTA específica), removida intensificação anti-HTA disparada por sintoma CV isolado, reforçado gate renal agudo e diferenciada suspeita de PRES de PRES confirmado sob bevacizumabe."
source_refs:
  - "Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568"
  - "Maitland ML, Bakris GL, Black HR, et al. Initial Assessment, Surveillance, and Management of Blood Pressure in Patients Receiving Vascular Endothelial Growth Factor Signaling Pathway Inhibitors. J Natl Cancer Inst. 2010;102(9):596-604. DOI: 10.1093/jnci/djq091. PMID: 20351338"
  - "Steingart RM, Bakris GL, Chen HX, et al. Management of cardiac toxicity in patients receiving vascular endothelial growth factor signaling pathway inhibitors. Am Heart J. 2012;163(2):156-163. DOI: 10.1016/j.ahj.2011.10.018. PMID: 22305831"
---

# Fluxograma ambulatorial: hipertensão por VEGF/TKI — destino

Prosa: [`sinalizadores-ambulatoriais-hipertensao-por-vegf-tki-quando-encaminhar`](sinalizadores-ambulatoriais-hipertensao-por-vegf-tki-quando-encaminhar.md). Checklist: [`hipertensao-por-vegf-tki-checklist-ambulatorial-de-alarme`](hipertensao-por-vegf-tki-checklist-ambulatorial-de-alarme.md). Crise/TKI: [`fluxograma-hipertensao-grave-e-crise-hipertensiva-induzida-por-tki`](fluxograma-hipertensao-grave-e-crise-hipertensiva-induzida-por-tki.md).

```mermaid
flowchart TD
  R0["Consulta/contato sob inibidor da via VEGF<br/>PA elevada e/ou sintoma"] --> D1{"Lesão aguda de órgão-alvo ou PRES?<br/>SCA · IC aguda · síndrome aórtica<br/>déficit/convulsão/alteração visual<br/>oligúria/IRA ou rápida piora renal"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / emergência AGORA<br/>Suspender temporariamente agente causal<br/>Manejo conforme órgão-alvo / PRES"])

  D1 -->|"Não"| D2{"PAS >=180 OU PAD >=110 mmHg?"}

  D2 -->|"Sim"| C2(["Pausar TEMPORARIAMENTE terapia associada à HTN<br/>Otimizar anti-HTA oral<br/>Discussão oncologia/cardio-oncologia antes de reinício"])

  D2 -->|"Não"| D3{"PAS >=160 E PAD >=100 mmHg?"}

  D3 -->|"Sim"| C3(["IECA ou BRA + BCC di-hidropiridínico<br/>salvo contraindicação/interação<br/>Monitorização e retorno precoce"])

  D3 -->|"Não"| D4{"Há sintoma cardiovascular novo<br/>sem critério de emergência?"}

  D4 -->|"Sim"| C4(["Investigar sintoma: ECG +/- biomarcador/eco<br/>CTRCD/isquemia conforme apresentação<br/>NÃO intensificar anti-HTA apenas pelo sintoma"])

  D4 -->|"Não"| C5(["Tratar PA conforme risco/contexto oncológico<br/>MRPA/diário também para outros inibidores VEGF<br/>Reforçar adesão e alarmes"])

  C1 --> D5{"PRES confirmado sob bevacizumabe?"}
  D5 -->|"Sim"| C6(["Descontinuar bevacizumabe<br/>segurança de reinício desconhecida"])
  D5 -->|"Não / suspeita"| C7(["Manter suspensão enquanto investiga<br/>seguir protocolo específico"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C6 alerta;
  class C2,C3,C4,C5,C7 conduta;
```

## Notas

- **D1**: lesão aguda/PRES define urgência; o número isolado da PA não.
- **D2**: pausa da terapia associada à hipertensão em **PAS >=180 OU PAD >=110 mmHg**.
- **D3**: recomendação ESC específica para **PAS >=160 E PAD >=100 mmHg** exige ambos os componentes.
- **D4**: sintoma cardiovascular tem investigação própria; não é sinônimo de necessidade de mais anti-hipertensivo.
- O fluxograma não define doses nem redução percentual da terapia oncológica.
