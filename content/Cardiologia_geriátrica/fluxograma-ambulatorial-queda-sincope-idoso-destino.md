---
slug: fluxograma-ambulatorial-queda-sincope-idoso-destino
title: 'Fluxograma ambulatorial: queda/síncope no idoso — PS agora vs. retorno precoce'
kind: fluxograma
theme: Cardiologia geriátrica
summary: 'Árvore ambulatorial de destino: gate de alto risco ESC/ECG/trauma/isquemia para PS; braço ortostático
  e braço equívoco com retorno precoce — sem doses.'
tags: []
source_refs:
- 'Brignole M; Moya A; de Lange FJ. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J.
  2018;39:1883. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304.'
- 'Damluji AA; Forman DE; Wang TY. Management of Acute Coronary Syndrome in the Older Adult Population: A Scientific
  Statement From the American Heart Association. Circulation. 2023;147:e32. DOI: 10.1161/CIR.0000000000001112. PMID:
  36503287.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: queda/síncope no idoso — destino

Prosa: [sinalizadores-ambulatoriais-queda-sincope-idoso-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-queda-sincope-idoso-quando-encaminhar). Emergência: [sincope-e-queda-no-idoso-estratificacao-de-risco-na-emergencia](/biblioteca/sincope-e-queda-no-idoso-estratificacao-de-risco-na-emergencia).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>queda inexplicada / pré-síncope / síncope<br/>no idoso"] --> I0["Sinais vitais, ECG de 12 derivações,<br/>exame neurológico e avaliação de trauma/sangramento;<br/>se instável, emergência sem aguardar exames"]
 I0 --> D1{"Há alarme de PS?<br/>esforço ou supina / palpitações → evento<br/>ECG de risco / BAV avançado / pausas relevantes / isquemia<br/>trauma craniano em anticoagulado / sangramento<br/>instabilidade incerta / hipotensão persistente<br/>suspeita isquêmica ou IC aguda (dispneia/dor/congestão)"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS<br/>Usar estratificação de emergência<br/>e fluxograma já publicados no tema"])

  D1 -->|"Não"| D2{"PA ortostática positiva<br/>sem marcador de alto risco?"}

  D2 -->|"Sim"| P1["Revisar volume, gatilhos e fármacos<br/>Rever ECG já obtido; alarme novo leva ao PS<br/>Orientar alarmes por escrito"]
  P1 --> C2["Retorno ambulatorial 24–72 h<br/>(ou ≤7 dias se isolado e suporte OK)"]

  D2 -->|"Não / equívoco"| D3{"Episódio recente sem história clara<br/>ou recorrência leve sem alto risco?"}

  D3 -->|"Sim"| C3(["ECG + exame focado<br/>Manter síncope no diferencial<br/>Retorno 24–72 h; PS se surgir alarme"])
  D3 -->|"Não / estável baixo risco aparente"| C4(["Plano usual + educação de alarmes<br/>Não rotular queda mecânica só por idade"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / fragilidade alta / novo episódio"| C5(["Providenciar avaliação presencial em serviço acessível;<br/>piora rápida ou alarme exige urgência imediata"])
  D4 -->|"Sim"| C6(["Manter retorno precoce<br/>Não protocolar doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = triagem de segurança (alto risco ESC 2018 + trauma + equivalente isquêmico AHA 2023).
- **D2** = braço ortostático sem alto risco → destino clínico precoce, não alta sem plano.
- **D3** = queda sem história clara permanece síncope no diferencial até prova em contrário.
- Não decide indicação de marca-passo, Holter de longo prazo, doses nem estratégia de SCA invasiva.

## Limites antes de retorno

ECG normal isolado não afasta SCA. Se suspeita aguda residual, concluir avaliação seriada segura em unidade adequada; não enviar para casa aguardando troponina. Delirium, fadiga, náusea e queda são inespecíficos: avaliar infecção, hipovolemia, medicamentos, distúrbios metabólicos, AVC e outras causas simultaneamente.

Hipotensão ortostática positiva não exclui arritmia, valvopatia, hemorragia ou doença neurológica. Avaliar consequência da queda, especialmente trauma craniano/sangramento em anticoagulado. Instabilidade incerta, IC aguda ou suspeita isquêmica exige avaliação imediata. Retorno em dias só após afastamento razoável das emergências, estabilidade documentada e rede segura. Fragilidade e objetivos modulam tratamento após avaliação, sem atrasar reconhecimento.
Os intervalos de retorno indicados são sugestões operacionais ajustadas à gravidade e ao acesso; não constituem prazos fixados pela ESC.
