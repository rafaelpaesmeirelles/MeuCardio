---
title: "Golpe de calor por esforço no atleta: reconhecimento e resfriamento"
slug: fluxograma-golpe-de-calor-por-esforco-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Revisão independente em 26/08/2026: corrigido o fluxo para iniciar resfriamento sem aguardar confirmação termométrica e para não excluir golpe de calor após atraso ou resfriamento prévio."
source_refs:
  - "Documento já publicado no acervo Corvia: golpe-de-calor-por-esforco-cardiovascular-atleta (tema Cardiologia do Esporte e do Exercício)"
  - "Roberts WO, Armstrong LE, Sawka MN, Yeargin SW, Heled Y, O'Connor FG. ACSM Expert Consensus Statement on Exertional Heat Illness: Recognition, Management, and Return to Activity. Curr Sports Med Rep. 2023;22(4):134-149. PMID: 37036463. DOI: 10.1249/JSR.0000000000001058."
  - "Hosokawa Y, Racinais S, Akama T, Zideman D, Budgett R, Casa DJ, Bermon S, Grundstein AJ, Pitsiladis YP, Schobersberger W, Yamasawa F. Prehospital management of exertional heat stroke at sports competitions: International Olympic Committee Adverse Weather Impact Expert Working Group for the Olympic Games Tokyo 2020. Br J Sports Med. 2021;55(24):1405-1410. PMID: 33888465. PMCID: PMC8639927. DOI: 10.1136/bjsports-2020-103854."
  - "Zhuang Y, Zhuang XH, Zhang XY, Wang DC, Yang Y. Mechanisms and Intervention Strategies for Heat Stroke-Associated Myocardial Dysfunction: A Narrative Review. West J Emerg Med. 2026;27(3):526-533. PMID: 42258868. PMCID: PMC13246188. DOI: 10.5811/westjem.53045."
---

# Golpe de calor por esforço no atleta: reconhecimento e resfriamento

## Árvore de decisão

```mermaid
flowchart TD
    A["Atleta com suspeita de golpe de calor por esforço (alteração do sistema nervoso central durante ou logo após esforço em ambiente de calor)"] --> B["Interromper a atividade e iniciar resfriamento ativo imediatamente, enquanto se obtém temperatura retal; não atrasar o resfriamento para medir a temperatura"]
    B --> D1{"Temperatura retal ≥40,5°C ou quadro ainda altamente compatível após atraso na aferição/resfriamento prévio?"}
    D1 -->|"Sim"| B2["Manter resfriamento corporal total rápido no local e monitorização contínua"]
    D1 -->|"Não, medida retal e avaliação clínica tornam golpe de calor improvável"| C1(["Investigar diagnósticos alternativos urgentes e transportar para avaliação; manter resfriamento se persistirem hipertermia ou alteração neurológica"])
    B2 --> D2{"A temperatura retal caiu abaixo de 39°C durante o resfriamento no local?"}
    D2 -->|"Não"| C2(["Manter resfriamento ativo no local e monitorizar ECG, sinais vitais e consciência; coordenar transporte sem interromper o resfriamento se houver necessidade imediata de suporte de via aérea, respiração ou circulação"])
    D2 -->|"Sim"| D3{"Há sinais de disfunção cardíaca associada (taquicardia persistente, arritmia, alteração eletrocardiográfica, instabilidade hemodinâmica) ou elevação relevante de biomarcadores?"}
    D3 -->|"Sim"| C3(["Transportar para cuidado clínico avançado com monitorização cardiovascular ativa (ECG seriado, biomarcadores, ecocardiograma quando indicado); não atribuir taquicardia ou troponina elevada apenas ao calor sem investigar"])
    D3 -->|"Não"| C4(["Transportar para cuidado clínico avançado para observação e coleta de sangue (afastar hiponatremia ou hipoglicemia associada); decisão de retorno à atividade individualizada por equipe de saúde qualificada"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4 conduta;
```

## Critérios usados na árvore

O golpe de calor por esforço (*exertional heat stroke*) é a manifestação mais grave do espectro de doença por calor relacionada ao esforço, caracterizado pela combinação de hipertermia central importante (frequentemente temperatura retal acima de 40,5°C) e disfunção do sistema nervoso central durante ou logo após esforço físico (Roberts et al., *Curr Sports Med Rep*. 2023, PMID 37036463). Uma medida abaixo desse valor não exclui o diagnóstico quando houve demora, resfriamento prévio ou alta compatibilidade clínica.

O princípio organizador da árvore — **"cool first, transport second"** (resfriar primeiro, transportar depois) — vem do documento do grupo de trabalho de impacto climático adverso do Comitê Olímpico Internacional para os Jogos de Tóquio 2020 (Hosokawa et al., *Br J Sports Med*. 2021, PMID 33888465): ao ser admitido na área dedicada ("heat deck"), o atleta deve ter a temperatura retal aferida — **não** por via oral, axilar ou timpânica — e ser resfriado no local até a temperatura retal ficar **abaixo de 39°C** antes do transporte, desde que não haja necessidade imediata de intervenção vital indisponível no local. Durante o resfriamento é recomendável coletar sangue para descartar hiponatremia ou hipoglicemia associadas, se isso não interromper o resfriamento. O consenso do ACSM de 2023 reforça que o resfriamento não deve aguardar a conclusão da avaliação diagnóstica.

O ramo de disfunção cardíaca reflete a revisão narrativa de 2026 sobre disfunção miocárdica associada ao golpe de calor (Zhuang et al., *West J Emerg Med*. 2026, PMID 42258868), que descreve manifestações cardíacas incluindo lesão miocárdica (elevação de biomarcadores), arritmia e disfunção ventricular, com diagnóstico precoce apoiado em ECG, biomarcadores cardíacos (incluindo troponina, citada explicitamente) e ecocardiograma. A própria fonte não estabelece um corte numérico único e validado de troponina para prognóstico nesse contexto — por isso a árvore usa "elevação relevante de biomarcadores" como critério qualitativo, sem inventar um limiar que a fonte não fornece, e mantém aberta a orientação de que taquicardia e alteração eletrocardiográfica no golpe de calor não devem ser atribuídas ao calor sem investigação, nem devem gerar investigação coronariana invasiva de rotina só pela elevação isolada de troponina. O documento de origem também registra que a literatura de recomendação de exercício em calor ainda não desenvolveu orientação específica de retorno à atividade para o cardiopata nem um intervalo fixo universal de afastamento pós-golpe de calor — por isso a conduta final da árvore remete a decisão individualizada por equipe qualificada, sem propor um prazo que a fonte não sustenta.
