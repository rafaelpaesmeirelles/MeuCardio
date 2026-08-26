---
title: "Extrassístoles ventriculares frequentes ao Holter no atleta: avaliação e liberação esportiva"
slug: fluxograma-extrassistoles-ventriculares-frequentes-holter-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: PMID 38763377 (HRS 2024) e PMID 39973614 (AHA/ACC 2025) conferidos via PubMed E-utilities (esummary) — título, revista e data batem exatamente. Árvore de decisão derivada do documento já publicado no acervo Corvia extrassistoles-e-arritmias-ventriculares-no-atleta.md, que cita as mesmas duas fontes mais o estudo VENTOUX (PMID 40675176). Estrutura validada por script próprio: uma raiz, todo nó não-raiz com exatamente um pai, sem ciclo/merge, cada losango com ≥2 ramos rotulados, toda folha em forma de conduta."
source_refs:
  - "Documento já publicado no acervo Corvia: extrassistoles-e-arritmias-ventriculares-no-atleta (tema Cardiologia do Esporte e do Exercício)"
  - "Lampert R, et al. 2024 HRS expert consensus statement on arrhythmias in the athlete: Evaluation, treatment, and return to play. Heart Rhythm. 2024;21:e151-e252. PMID: 38763377. DOI: 10.1016/j.hrthm.2024.05.018."
  - "Kim JH, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. Circulation. 2025. PMID: 39973614."
---

# Extrassístoles ventriculares frequentes ao Holter no atleta: avaliação e liberação esportiva

## Árvore de decisão

```mermaid
flowchart TD
    A["Atleta com extrassístoles ventriculares (EVs) frequentes identificadas ao Holter ou monitorização ambulatorial prolongada"] --> D1{"Há sinal de alarme (síncope ou pré-síncope ao esforço, dor torácica desproporcional, dispneia desproporcional) ou história familiar de morte súbita, cardiomiopatia ou canalopatia?"}
    D1 -->|"Sim"| B1["Tratar como achado de alto risco: não liberar para treino competitivo antes de excluir causa estrutural ou elétrica"]
    B1 --> D2{"A morfologia das EVs e/ou seu comportamento (polimorfismo, pares, salvas, TV não sustentada, piora com o esforço) sugerem substrato patológico?"}
    D2 -->|"Sim"| C1(["Investigação estrutural dirigida: ecocardiograma, teste de esforço máximo reproduzindo a demanda esportiva, ressonância cardíaca com avaliação de realce tardio, estudo genético se houver suspeita fenotípica ou familiar; restringir participação competitiva até definição diagnóstica"])
    D2 -->|"Não, mas o sinal de alarme clínico/familiar persiste"| C2(["Mesmo sem morfologia de alto risco, manter investigação estrutural completa (ecocardiograma, teste de esforço, ressonância cardíaca) antes de liberar, pela presença do sinal de alarme clínico ou familiar; restringir participação competitiva enquanto isso"])
    D1 -->|"Não"| D3{"A morfologia é compatível com foco idiopático conhecido, com baixa complexidade, ausência de pares polimórficos/salvas/TV não sustentada e comportamento não preocupante?"}
    D3 -->|"Sim"| D4{"Ecocardiograma e ECG de repouso são normais, sem sinais sugestivos de cardiomiopatia?"}
    D4 -->|"Sim"| C3(["Ectopia idiopática de baixo risco: liberar participação esportiva sem restrição cardíaca, com reavaliação clínica periódica"])
    D4 -->|"Não, há achado estrutural"| C4(["Investigar a anormalidade estrutural encontrada com ressonância cardíaca e avaliação dirigida à cardiopatia suspeita antes de liberar; a conduta de retorno ao esporte passa a depender do diagnóstico definido"])
    D3 -->|"Não"| D5{"O teste de esforço, reproduzindo a intensidade e a modalidade do esporte praticado, mostra piora da ectopia, surgimento de pares/salvas ou TV não sustentada?"}
    D5 -->|"Sim"| C5(["Piora induzida pelo esforço: investigar substrato com ressonância cardíaca (fibrose/realce tardio) e avaliação estrutural completa; restringir participação competitiva até definição diagnóstica"])
    D5 -->|"Não, comportamento estável ou com supressão ao esforço"| C6(["Comportamento tranquilizador ao esforço, mas sem morfologia claramente idiopática: complementar com ressonância cardíaca dirigida para excluir fibrose ou cardiomiopatia antes da liberação plena; se negativa, liberar com reavaliação clínica periódica"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5,C6 conduta;
```

## Critérios usados na árvore

A árvore parte do documento já publicado no acervo Corvia (`extrassistoles-e-arritmias-ventriculares-no-atleta`), apoiado no consenso de especialistas da HRS 2024 (Lampert R, et al. *Heart Rhythm*. 2024;21:e151-e252, PMID 38763377) e no *scientific statement* AHA/ACC 2025 (Kim JH, et al. *Circulation*. 2025, PMID 39973614) — ambos PMID conferidos nesta sessão via PubMed E-utilities (`esummary`), título, revista e data batendo exatamente com o citado.

O primeiro corte da árvore é o **sinal de alarme clínico ou familiar**: síncope ou pré-síncope ao esforço, dor torácica ou dispneia desproporcional ao esforço, ou história familiar de morte súbita, cardiomiopatia ou canalopatia. Presente qualquer um deles, a fonte trata o achado como alto risco até prova em contrário, independentemente da morfologia da ectopia — e mesmo quando a morfologia das EVs não é, isoladamente, sugestiva de substrato patológico, a investigação estrutural completa (ecocardiograma, teste de esforço reproduzindo a demanda esportiva real e ressonância cardíaca) precisa ser concluída antes de qualquer liberação, pela presença do próprio sinal de alarme.

Na ausência de sinal de alarme, o corte seguinte é a **morfologia e o comportamento da ectopia**: compatibilidade com foco idiopático conhecido, baixa complexidade, ausência de pares polimórficos, salvas ou taquicardia ventricular não sustentada, e comportamento não preocupante. A fonte é explícita que nenhum desses itens isoladamente confirma benignidade — a conclusão é integrativa, e por isso a árvore ainda exige ecocardiograma e ECG de repouso normais antes de liberar sem restrição.

Quando a morfologia não é claramente idiopática, o teste de esforço — feito em intensidade e modalidade que reproduzam a demanda esportiva real, não interrompido precocemente ao atingir uma frequência-alvo — decide o próximo passo: piora da ectopia ou surgimento de pares/salvas/TV não sustentada aponta para investigação de substrato com ressonância cardíaca; comportamento estável ou com supressão ao esforço é tranquilizador, mas a fonte recomenda ainda assim complementar com ressonância dirigida antes da liberação plena, porque supressão ao esforço não exclui doença estrutural por si só.

A quantidade de EVs não integra nenhum ramo da árvore como critério isolado: a fonte é explícita que a carga (número absoluto) de ectopia não deve ser usada isoladamente como marcador prognóstico em atleta sem doença estrutural conhecida — o que decide é morfologia, complexidade, comportamento ao esforço e substrato estrutural, que é exatamente o que os ramos acima avaliam. A retirada da árvore serve tanto para não fabricar um corte numérico que a fonte não define quanto para não confundir carga de ectopia com risco.

Esta árvore cobre a etapa de **avaliação inicial e estratificação de risco**. A decisão final de retorno ao esporte, quando um substrato estrutural, arritmia associada a cardiomiopatia, miocardite, fibrose relevante ou canalopatia é identificado, depende do manejo específico da doença de base e de nova estratificação — etapa posterior, não coberta por este diagrama, que a fonte trata em conjunto com o consenso HRS 2024 sobre retorno ao esporte em condições arrítmicas complexas.
