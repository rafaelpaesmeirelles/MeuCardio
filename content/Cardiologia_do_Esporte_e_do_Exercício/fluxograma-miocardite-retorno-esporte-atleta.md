---
title: "Miocardite no atleta: fluxograma de decisão para retorno ao esporte competitivo"
slug: fluxograma-miocardite-retorno-esporte-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Produzido e verificado por Claude em 26/08/2026: PMIDs e DOIs conferidos individualmente via PubMed E-utilities (esummary) e Crossref antes da redação; recorte inédito no acervo (tema tinha 6 fluxogramas e nenhum cobria retorno ao esporte pós-miocardite em árvore de decisão; o artigo já publicado sobre o tema é do tipo 'estudo', em prosa)."
source_refs:
  - "Kim JH, Baggish AL, Levine BD, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. Circulation. 2025;151(11):e716-e761. PMID: 39973614. DOI: 10.1161/CIR.0000000000001297."
  - "Lampert R, Chung EH, Ackerman MJ, et al. 2024 HRS expert consensus statement on arrhythmias in the athlete: evaluation, treatment, and return to play. Heart Rhythm. 2024;21(10):e151-e252. PMID: 38763377. DOI: 10.1016/j.hrthm.2024.05.018."
  - "Pelliccia A, Sharma S, Gati S, et al. 2020 ESC Guidelines on sports cardiology and exercise in patients with cardiovascular disease. Eur Heart J. 2021;42(1):17-96. PMID: 32860412. DOI: 10.1093/eurheartj/ehaa605."
  - "Dores H, Dinis P, Puga L, Freitas A, Cardim N. Myocarditis in athletes: Challenges for return to play. Rev Port Cardiol. 2026;45(6):307-317. PMID: 42061508. DOI: 10.1016/j.repc.2026.02.006."
  - "Patriki D, Baltensperger N, Berg J, et al. A Prospective Pilot Study to Identify a Myocarditis Cohort who may Safely Resume Sports Activities 3 Months after Diagnosis. J Cardiovasc Transl Res. 2021;14(4):670-673. PMID: 32367345. DOI: 10.1007/s12265-020-09983-6."
---

# Miocardite no atleta: fluxograma de decisão para retorno ao esporte competitivo

## Árvore de decisão

```mermaid
flowchart TD
    A["Atleta com miocardite aguda confirmada (clínica, biomarcadores e/ou ressonância cardíaca compatíveis)"] --> B["Suspender exercício físico moderado-intenso durante a fase ativa; período histórico de referência de 3 a 6 meses antes da reavaliação"]
    B --> D1{"Ao final do período de restrição: assintomático, biomarcadores normalizados/em tendência de normalização e sem sinais de inflamação ativa?"}
    D1 -->|"Não"| C1(["Manter restrição de exercício vigoroso; reavaliar periodicamente até resolução da fase ativa"])
    D1 -->|"Sim"| D2{"Miocardite recorrente (2º episódio ou mais) ou achados sugestivos de cardiomiopatia/predisposição genética subjacente?"}
    D2 -->|"Sim"| C2(["Não liberar para esporte competitivo; encaminhar investigação de cardiomiopatia genética antes de qualquer nova decisão de retorno"])
    D2 -->|"Não"| D3{"Função ventricular (FEVE) normal na reavaliação, sem disfunção residual?"}
    D3 -->|"Não"| C3(["Não liberar para esporte competitivo; manter seguimento cardiológico com reavaliação seriada da função ventricular"])
    D3 -->|"Sim"| D4{"Holter e/ou teste de esforço na intensidade da modalidade mostram arritmia ventricular complexa (TVNS, ectopia frequente ou polimórfica)?"}
    D4 -->|"Sim"| C4(["Não liberar; encaminhar avaliação eletrofisiológica especializada antes de reconsiderar o retorno"])
    D4 -->|"Não"| D5{"Antecedente de síncope inexplicada ou parada cardíaca associada ao episódio de miocardite?"}
    D5 -->|"Sim"| C5(["Não liberar; avaliação especializada adicional (eletrofisiologia/cardiomiopatias) antes de qualquer retorno ao esporte"])
    D5 -->|"Não"| D6{"Ressonância cardíaca de reavaliação mostra realce tardio (LGE) residual?"}
    D6 -->|"Não"| C6(["Liberar retorno gradual e progressivo ao esporte competitivo, com reavaliação periódica"])
    D6 -->|"Sim, extenso ou com padrão sugestivo de substrato arritmogênico"| C7(["Não liberar; individualizar fortemente com decisão compartilhada multidisciplinar e considerar avaliação eletrofisiológica avançada"])
    D6 -->|"Sim, discreto/isolado e sem os demais marcadores de risco acima"| C8(["Considerar retorno gradual sob decisão compartilhada, com monitorização adicional (Holter e teste de esforço específico da modalidade) e reavaliação seriada"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Critérios usados na árvore

A restrição de exercício físico intenso durante a fase ativa da miocardite é conduta histórica e consensual (ESC 2020, task force AHA/ACC anteriores e a atualização AHA/ACC 2025), sustentada pelo risco aumentado de arritmia ventricular e morte súbita associado à inflamação ativa, disfunção ventricular e instabilidade elétrica durante o esforço. O período de referência de 3 a 6 meses citado na árvore vem dessa tradição de diretrizes; a revisão de Dores et al. (2026, *Rev Port Cardiol*) e o statement AHA/ACC 2025 (Kim JH et al., *Circulation*, PMID 39973614) explicitam, porém, que a evidência prospectiva para um intervalo único e universal é limitada — por isso a árvore não trata o tempo isoladamente como critério de liberação, mas apenas como o ponto de corte a partir do qual a reavaliação multiparamétrica deve ocorrer.

O estudo piloto prospectivo de Patriki et al. (2020/2021, *J Cardiovasc Transl Res*, PMID 32367345) testou justamente esse desenho: 30 pacientes com miocardite e FEVE preservada ou apenas discretamente reduzida foram reavaliados aos 3 meses, e todos exceto um foram liberados sem eventos cardíacos no seguimento disponível — o que dá suporte empírico (ainda que de amostra pequena) à lógica de reavaliação multiparamétrica ao final da restrição, em vez de liberação automática por tempo decorrido.

A árvore incorpora, na ordem em que a literatura consistentemente aponta como determinantes de maior cautela (Kim JH et al. 2025; Lampert R et al., HRS 2024, PMID 38763377; Dores H et al. 2026, PMID 42061508): recorrência do episódio ou suspeita de cardiomiopatia genética subjacente; disfunção ventricular residual; arritmia ventricular complexa documentada em monitorização ou teste de esforço específico da modalidade; síncope inexplicada ou parada cardíaca associada ao quadro; e, por fim, o achado de realce tardio (LGE) residual na ressonância cardíaca de reavaliação.

O nó sobre LGE residual reflete explicitamente a zona de incerteza descrita nas fontes: a persistência de realce tardio após resolução clínica não equivale automaticamente a inflamação ativa ou a proibição esportiva, e seu significado depende de padrão, extensão e associação com os demais marcadores de risco já avaliados nos nós anteriores da árvore. Por isso a árvore só classifica o LGE residual como impeditivo de liberação quando ele é extenso ou tem padrão compatível com substrato arritmogênico; LGE discreto e isolado, na ausência de qualquer outro marcador de risco, é tratado como cenário de decisão compartilhada com monitorização adicional, e não como contraindicação automática — consistente com a ênfase do statement AHA/ACC 2025 e do HRS 2024 em avaliação individualizada e decisão compartilhada no esporte, evitando tanto exposição irresponsável ao risco quanto exclusão esportiva desnecessária.
