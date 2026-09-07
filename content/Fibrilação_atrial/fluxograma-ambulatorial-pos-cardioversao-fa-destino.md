---
title: "Fluxograma ambulatorial: pós-cardioversão de FA — PS agora vs retorno precoce vs plano"
slug: fluxograma-ambulatorial-pos-cardioversao-fa-destino
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino após cardioversão de FA: gate de alarme (AVC/AIT, instabilidade, congestão, isquemia, bradi sintomática), braço de recorrência estável com retorno precoce, e braço estável com plano — sem doses e sem decidir anticoagulação peri."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-pos-cardioversao-fa-quando-voltar-ao-ps (07/09/2026). PIVOT: lacuna destino pós-cardioversão; evita #827 e #852. Fontes: ESC AF 2024 PMID 39210723; SBC/SOBRAC 2025 PMID 41294177. Sem doses."
source_refs:
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723"
  - "Cintra FD, Pisani CF, Rezende AGS, et al. Diretriz Brasileira de Fibrilação Atrial – 2025. Arq Bras Cardiol. 2025;122(9):e20250618. DOI: 10.36660/abc.20250618. PMID: 41294177"
---

# Fluxograma ambulatorial: pós-cardioversão de FA — destino

Prosa: [`sinalizadores-ambulatoriais-pos-cardioversao-fa-quando-voltar-ao-ps`](sinalizadores-ambulatoriais-pos-cardioversao-fa-quando-voltar-ao-ps.md). Recorrência leve: [`recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps`](recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps.md). Peri anticoag (não este): [`fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento`](fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento\npós-cardioversão de FA\n(elétrica ou química)"] --> D0{"Ablação recente\n+ suspeita de complicação\nestrutural/infecciosa?"}
  D0 -->|"Sim"| C0(["Ir ao pacote pós-ablação\nalarme-complicacao (#852)\nNão misturar com este fluxo"])
  D0 -->|"Não"| D1{"Alarme imediato?\nDéficit neurológico / AVC-AIT\ninstabilidade / congestão aguda\nisquemia / bradi sintomática grave\nsangramento maior"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA\nECG + sinais vitais\nNão ajustar em casa"])

  D1 -->|"Não"| D2{"Recorrência de FA/flutter\nsem instabilidade\nsem congestão aguda?"}

  D2 -->|"Sim"| P1["Confirmar ECG / monitor\nRevisar precipitantes\nApontar documento peri\n(sem doses neste fluxo)"]
  P1 --> C2(["Retorno precoce\n(horas–poucos dias)\nReavaliar estratégia ritmo/frequência"])

  D2 -->|"Não"| D3{"Estável em ritmo\nsem alarmes da tabela?"}

  D3 -->|"Sim"| C3(["Plano escrito de alarmes\nManter janela peri\nRetorno programado"])
  D3 -->|"Não / dúvida"| C4(["Retorno curto prudente\nou cardiologia / arritmia"])

  C2 --> D4{"Acesso a reavaliação OK\ne sem piora em horas?"}
  D4 -->|"Não / piora"| C5(["Antecipar PS\nse surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Completar investigação dirigida\nNão esperar retorno de rotina longo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C0,C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança pós-cardioversão (neurológico / hemodinâmico / congestivo / isquêmico / bradi grave).
- **D2** = recorrência estável → retorno precoce, não “alta sem plano”.
- **D0** = desvia complicação pós-ablação para o pacote #852.
- **Não decide** anticoagulação peri, doses, bridge nem CHA₂DS₂-VA.
