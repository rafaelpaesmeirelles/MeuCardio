---
title: "Fluxograma ambulatorial: sinalizadores na FA (não-anticoagulação) — PS vs retorno precoce vs plano"
slug: fluxograma-ambulatorial-sinalizadores-fa-nao-anticoag-destino
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino na FA: gate de alarme (instabilidade/congestão aguda/isquemia/déficit), braço de falha de frequência ou sintomas novos de IC com retorno precoce, e braço estável com plano — sem anticoagulação e sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-falha-controle-frequencia-e-novos-sintomas-de-ic-na-fa (07/09/2026). PIVOT: lacuna destino ambulatorial não-anticoag; evita #827 e fluxogramas de dose/DOAC. Fontes: ESC AF 2024 PMID 39210723; SBC/SOBRAC 2025 PMID 41294177. Sem doses."
source_refs:
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723"
  - "Cintra FD, Pisani CF, Rezende AGS, et al. Diretriz Brasileira de Fibrilação Atrial – 2025. Arq Bras Cardiol. 2025;122(9):e20250618. DOI: 10.36660/abc.20250618. PMID: 41294177"
---

# Fluxograma ambulatorial: sinalizadores na FA (não-anticoag) — destino

Prosa: [`sinalizadores-ambulatoriais-falha-controle-frequencia-e-novos-sintomas-de-ic-na-fa`](sinalizadores-ambulatoriais-falha-controle-frequencia-e-novos-sintomas-de-ic-na-fa.md). Pós-ablação (complicação): [`sinalizadores-ambulatoriais-pos-ablacao-fa-alarme-complicacao-nao-recorrencia`](sinalizadores-ambulatoriais-pos-ablacao-fa-alarme-complicacao-nao-recorrencia.md). Controle de frequência (droga/alvo): [`fluxograma-controle-de-frequencia-na-fa-escolha-da-droga-por-feve-e-alvo-esc-2024`](fluxograma-controle-de-frequencia-na-fa-escolha-da-droga-por-feve-e-alvo-esc-2024.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento<br/>FA em acompanhamento"] --> D0{"Ablação recente<br/>+ suspeita de complicação<br/>estrutural/infecciosa?"}
  D0 -->|"Sim"| C0(["Ir ao pacote pós-ablação<br/>alarme-complicacao-nao-recorrencia"])
  D0 -->|"Não"| D1{"Alarme imediato?<br/>instabilidade / congestão aguda<br/>dor isquêmica em curso<br/>déficit neurológico / síncope"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA<br/>ECG + sinais vitais<br/>Não ajustar em casa"])

  D1 -->|"Não"| D2{"Falha sintomática de frequência<br/>OU sintomas novos de IC<br/>sem instabilidade?"}

  D2 -->|"Sim"| P1["Precipitantes + ECG<br/>eco se IC nova / mudança clínica"]
  P1 --> C2(["Retorno precoce<br/>Reavaliar estratégia frequência ↔ ritmo<br/>Sem inventar doses neste fluxo"])

  D2 -->|"Não"| D3{"Estável, sem congestão,<br/>sem falha sintomática?"}

  D3 -->|"Sim"| C3(["Plano escrito de alarmes<br/>Retorno programado + AF-CARE C/E"])
  D3 -->|"Não / dúvida"| C4(["Retorno curto prudente<br/>ou cardiologia / arritmia"])

  C2 --> D4{"Acesso a reavaliação OK<br/>e sem piora em horas?"}
  D4 -->|"Não / piora"| C5(["Antecipar PS<br/>se surgir alarme da tabela"])
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
