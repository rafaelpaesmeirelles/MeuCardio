---
slug: fluxograma-ambulatorial-sinalizadores-fa-nao-anticoag-destino
title: 'Fluxograma ambulatorial: sinalizadores na FA (não-anticoagulação) — PS vs retorno precoce vs plano'
kind: fluxograma
theme: Fibrilação atrial
summary: 'Árvore ambulatorial de destino na FA: gate de alarme (instabilidade/congestão aguda/isquemia/déficit),
  braço de falha de frequência ou sintomas novos de IC com retorno precoce, e braço estável com plano — sem anticoagulação
  e sem doses.'
tags: []
source_refs:
- 'Tzeis S, et al. 2024 EHRA/HRS/APHRS/LAHRS expert consensus statement on catheter and surgical ablation of atrial
  fibrillation. Europace. 2024;26:euae043. DOI: 10.1093/europace/euae043. https://pmc.ncbi.nlm.nih.gov/articles/PMC11000153/'
- 'Van Gelder IC; Rienstra M; Bunting KV. 2024 ESC Guidelines for the management of atrial fibrillation developed
  in collaboration with the European Association for Cardio-Thoracic Surgery (EACTS). Eur Heart J. 2024;45:3314.
  DOI: 10.1093/eurheartj/ehae176. PMID: 39210723.'
- 'Cintra FD; Pisani CF; Rezende AGDS. Brazilian Atrial Fibrillation Guidelines - 2025. Arq Bras Cardiol. 2025;122:e20250618.
  DOI: 10.36660/abc.20250618. PMID: 41294177.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: sinalizadores na FA (não-anticoag) — destino

Prosa: [sinalizadores-ambulatoriais-falha-controle-frequencia-e-novos-sintomas-de-ic-na-fa](/biblioteca/sinalizadores-ambulatoriais-falha-controle-frequencia-e-novos-sintomas-de-ic-na-fa). Pós-ablação (complicação): [sinalizadores-ambulatoriais-pos-ablacao-fa-alarme-complicacao-nao-recorrencia](/biblioteca/sinalizadores-ambulatoriais-pos-ablacao-fa-alarme-complicacao-nao-recorrencia). Controle de frequência (droga/alvo): [fluxograma-controle-de-frequencia-na-fa-escolha-da-droga-por-feve-e-alvo-esc-2024](/biblioteca/fluxograma-controle-de-frequencia-na-fa-escolha-da-droga-por-feve-e-alvo-esc-2024).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento<br/>FA em acompanhamento"] --> D0{"Ablação prévia, nas janelas específicas<br/>dias–semanas ou semanas–meses,<br/>com suspeita de complicação<br/>estrutural/infecciosa?"}
  D0 -->|"Sim"| C0(["Emergência se fístula, tamponamento<br/>ou instabilidade suspeitos;<br/>demais casos: pacote pós-ablação"])
  D0 -->|"Não"| D1{"Alarme imediato?<br/>instabilidade / congestão aguda<br/>dor isquêmica em curso<br/>déficit neurológico / síncope"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA<br/>ECG + sinais vitais<br/>Não ajustar em casa"])

  D1 -->|"Não"| D2{"Falha sintomática de frequência<br/>OU sintomas novos de IC<br/>sem instabilidade?"}

  D2 -->|"Sim"| P1["Precipitantes + ECG<br/>eco se IC nova / mudança clínica"]
  P1 --> C2["Avaliação precoce conforme gravidade<br/>Reavaliar estratégia frequência ↔ ritmo<br/>Sem inventar doses neste fluxo"]

  D2 -->|"Não"| D3{"Estável, sem congestão,<br/>sem falha sintomática?"}

  D3 -->|"Sim"| C3(["Plano escrito de alarmes<br/>Retorno programado + AF-CARE C/E"])
  D3 -->|"Não / dúvida"| C4(["Retorno curto prudente<br/>ou cardiologia / arritmia"])

  C2 --> D4{"Acesso a reavaliação OK<br/>e sem piora em horas?"}
  D4 -->|"Não / piora"| C5(["Providenciar avaliação presencial urgente<br/>em serviço acessível; PS se piora/alarme<br/>ou ausência de alternativa segura"])
  D4 -->|"Sim"| C6(["Completar investigação dirigida<br/>Não esperar retorno de rotina longo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C0,C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (instabilidade / congestão aguda / isquemia / déficit).
- **D2** = falha de frequência sintomática ou IC nova ambulatorial → retorno precoce + reavaliar estratégia (ESC AF-CARE R/E; SBC 2025).
- **D0** = desvia complicação pós-ablação para o pacote dedicado (não misturar com recorrência/blanking).
- **Não decide** anticoagulação, doses, bridge nem CHA₂DS₂-VA.

## Salvaguardas de complicações e destino

Suspeita de fístula atrioesofágica exige emergência e comunicação explícita de ablação de FA e data. Evitar endoscopia, ETE ou instrumentação esofágica não planejada até avaliação especializada, pelo risco de embolia aérea. Não exigir tríade completa. Tamponamento, déficit neurológico e insuficiência respiratória são emergências. Estenose de veia pulmonar e lesão frênica estáveis pedem investigação especializada prioritária, não PS automático.

Frequência elevada isolada não define emergência. IC nova pede ecocardiograma e investigação de cardiomiopatia induzida por taquicardia, valvopatia, isquemia e outras causas; não presumir falha de frequência. Recorrência precoce isolada não equivale a falha da ablação. Sucesso aparente de ritmo não autoriza interromper anticoagulação prescrita pelo risco.
