---
title: "Golpe de calor por esforço no atleta: reconhecimento e resfriamento"
slug: fluxograma-golpe-de-calor-por-esforco-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
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
    A["Atleta com suspeita de golpe de calor por esforço (confusão, sonolência ou alteração do nível de consciência durante ou logo após esforço em ambiente de calor)"] --> B["Interromper imediatamente a atividade física, para cessar a geração de calor corporal"]
    B --> D1{"A temperatura retal confirma hipertermia central (referência mais citada na literatura: acima de 40,5°C)?"}
    D1 -->|"Não confirmado, ou temperatura aferida por via oral/axilar/timpânica"| C1(["Não confirmar o diagnóstico de golpe de calor por via não retal; aferir temperatura retal antes de decidir a conduta; manter resfriamento se a suspeita clínica persistir"])
    D1 -->|"Sim, hipertermia central confirmada por via retal"| B2["Iniciar resfriamento corporal total rápido no local, antes do transporte"]
    B2 --> D2{"A temperatura retal caiu abaixo de 39°C durante o resfriamento no local?"}
    D2 -->|"Não"| C2(["Manter resfriamento ativo no local; não transportar antes de atingir a meta de temperatura — resfriar primeiro, transportar depois; monitorizar ECG, sinais vitais e nível de consciência continuamente"])
    D2 -->|"Sim"| D3{"Há sinais de disfunção cardíaca associada (taquicardia persistente, arritmia, alteração eletrocardiográfica, instabilidade hemodinâmica) ou elevação relevante de biomarcadores?"}
    D3 -->|"Sim"| C3(["Transportar para cuidado clínico avançado com monitorização cardiovascular ativa (ECG seriado, biomarcadores, ecocardiograma quando indicado); não atribuir taquicardia ou troponina elevada apenas ao calor sem investigar"])
    D3 -->|"Não"| C4(["Transportar para cuidado clínico avançado para observação e coleta de sangue (afastar hiponatremia ou hipoglicemia associada); decisão de retorno à atividade individualizada por equipe de saúde qualificada"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4 conduta;
```

## Critérios usados na árvore

O golpe de calor por esforço (*exertional heat stroke*) é a manifestação mais grave do espectro de doença por calor relacionada ao esforço, definido pela combinação de temperatura corporal central elevada (referência mais citada: temperatura retal acima de 40,5°C) com disfunção do sistema nervoso central durante ou logo após esforço físico (Roberts et al., *Curr Sports Med Rep*. 2023, PMID 37036463). É apontado como a terceira causa de morte em atletas durante atividade física, com mortalidade descrita em torno de 27% (Garcia et al., *BMJ Med*. 2022, citado no documento de origem).

O princípio organizador da árvore — **"cool first, transport second"** (resfriar primeiro, transportar depois) — vem literalmente do documento do grupo de trabalho de impacto climático adverso do Comitê Olímpico Internacional para os Jogos de Tóquio 2020 (Hosokawa et al., *Br J Sports Med*. 2021, PMID 33888465): ao ser admitido na área dedicada ("heat deck"), o atleta deve ter a temperatura retal aferida — **não** por via oral, axilar ou timpânica —, ser resfriado no local até a temperatura retal ficar **abaixo de 39°C**, e só então ser transportado; durante o resfriamento é recomendável coletar sangue para descartar hiponatremia ou hipoglicemia associadas, desde que isso não interrompa o resfriamento. Essa mesma lógica é reforçada pelo consenso de especialistas do ACSM de 2023 (Roberts et al., PMID 37036463), organizado em torno de uma "cadeia de sobrevivência" do calor: reconhecimento rápido, interrupção da atividade e resfriamento corporal total rápido são as medidas essenciais para sobrevivência.

O ramo de disfunção cardíaca reflete a revisão narrativa de 2026 sobre disfunção miocárdica associada ao golpe de calor (Zhuang et al., *West J Emerg Med*. 2026, PMID 42258868), que descreve manifestações cardíacas incluindo lesão miocárdica (elevação de biomarcadores), arritmia e disfunção ventricular, com diagnóstico precoce apoiado em ECG, biomarcadores cardíacos (incluindo troponina, citada explicitamente) e ecocardiograma. A própria fonte não estabelece um corte numérico único e validado de troponina para prognóstico nesse contexto — por isso a árvore usa "elevação relevante de biomarcadores" como critério qualitativo, sem inventar um limiar que a fonte não fornece, e mantém aberta a orientação de que taquicardia e alteração eletrocardiográfica no golpe de calor não devem ser atribuídas ao calor sem investigação, nem devem gerar investigação coronariana invasiva de rotina só pela elevação isolada de troponina. O documento de origem também registra que a literatura de recomendação de exercício em calor ainda não desenvolveu orientação específica de retorno à atividade para o cardiopata nem um intervalo fixo universal de afastamento pós-golpe de calor — por isso a conduta final da árvore remete a decisão individualizada por equipe qualificada, sem propor um prazo que a fonte não sustenta.