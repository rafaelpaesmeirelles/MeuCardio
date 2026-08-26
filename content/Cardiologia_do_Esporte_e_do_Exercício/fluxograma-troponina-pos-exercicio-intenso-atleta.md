---
title: "Troponina após exercício intenso no atleta: interpretação"
slug: fluxograma-troponina-pos-exercicio-intenso-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo Corvia: troponina-apos-exercicio-intenso-atleta-interpretacao (tema Cardiologia do Esporte e do Exercício)"
  - "Dong X, et al. The association between marathon running and high-sensitivity cardiac troponin: A systematic review and meta-analysis. J Back Musculoskelet Rehabil. 2023;36:1023-1031. PMID: 37248881. DOI: 10.3233/BMR-220352."
  - "Wang X, et al. Exercise-induced cardiac troponin elevations and cardiac ventricular dysfunction assessed by tissue Doppler echocardiography and speckle tracking among non-elite runners in Beijing marathon. J Sci Med Sport. 2024;27:508-514. PMID: 38697867. DOI: 10.1016/j.jsams.2024.04.005."
  - "Airaksinen KEJ, et al. Composition of cardiac troponin release differs after marathon running and myocardial infarction. Open Heart. 2024. PMID: 39551608."
  - "Janssen SLJE, et al. Exercise-induced cardiac troponin release in athletes with versus without coronary atherosclerosis. Am J Physiol Heart Circ Physiol. 2024;326:H1045-H1052. PMID: 38363583. DOI: 10.1152/ajpheart.00021.2024."
  - "Stekelenburg JO, Berge K, Janssen SLJE, Omland T, Myhre PL, Thompson PD, Aengevaeren VL, Eijsvogels TMH. Prevalence and Predictors of Cardiac Troponin Elevations Following Exercise: a Systematic Review, Meta-analysis, and Meta-regression. Eur J Prev Cardiol. 2026 Apr 15:zwag218. PMID: 41985028. DOI: 10.1093/eurjpc/zwag218."
---

# Troponina após exercício intenso no atleta: interpretação

## Árvore de decisão

```mermaid
flowchart TD
    A["Atleta com troponina cardíaca elevada após exercício intenso (endurance, maratona, ultramaratona)"] --> D1{"Há sintomas ou achados de alarme (dor torácica típica ou persistente, dispneia desproporcional, síncope ou instabilidade hemodinâmica, alteração isquêmica no ECG, arritmia significativa)?"}
    D1 -->|"Sim"| C1(["Investigar como possível síndrome coronariana aguda: ECG seriado, cinética de troponina e imagem quando indicada, seguindo o protocolo convencional de dor torácica"])
    D1 -->|"Não"| D2{"Há fatores de risco importantes, doença coronariana conhecida, ou cinética/magnitude da troponina discordante do contexto de exercício?"}
    D2 -->|"Sim"| C2(["Investigar dirigidamente o risco individual (avaliação de doença coronariana, imagem cardíaca quando indicada) antes de atribuir a elevação apenas ao exercício"])
    D2 -->|"Não"| C3(["Interpretar como elevação pós-exercício esperada, fenômeno bioquímico distinto de infarto tipo 1; não repetir a dosagem de rotina em atleta assintomático nem usar como rastreamento esportivo; reavaliar apenas se surgirem sintomas"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3 conduta;
```

## Critérios usados na árvore

O documento de origem reúne meta-análises e estudos observacionais que mostram que elevação de troponina cardíaca acima do percentil 99 após exercício prolongado ou muito intenso **não é rara**: uma meta-análise de 2026 com 129 estudos e 7.289 atletas (Stekelenburg et al., PMID 41985028) encontrou 36% de elevação acima do limite superior de referência, com pico de 52% entre 3 e 6 horas após esforços de endurance. Um estudo com corredores da Maratona de Pequim (Wang et al., PMID 38697867) encontrou mais de 72% acima do percentil 99, com normalização em duas semanas. Por isso a mensagem central da fonte é que **troponina elevada significa injúria miocárdica bioquímica, mas não define sozinha infarto agudo do miocárdio**.

Os achados que, segundo a fonte, tornam a hipótese de doença aguda relevante e exigem investigação convencional são: dor torácica típica ou persistente, dispneia desproporcional, síncope ou instabilidade hemodinâmica, alterações isquêmicas no ECG, arritmia significativa, elevação com cinética ou magnitude discordante do contexto, fatores de risco importantes ou doença coronariana conhecida, e achados de imagem sugestivos de isquemia, miocardite ou outra injúria estrutural. A árvore separa os dois primeiros grupos de critérios (sintomas/ECG/hemodinâmica versus risco basal/cinética) em dois nós de decisão sequenciais, porque a fonte trata o exercício recente como algo que **modifica a probabilidade diagnóstica, mas não elimina diagnósticos graves** — mesmo sem sintoma agudo, um atleta com aterosclerose coronária conhecida (Janssen et al., PMID 38363583) não deve ter o achado atribuído automaticamente ao exercício.

O estudo de Airaksinen et al. (PMID 39551608), que comparou a composição da troponina liberada por corredores versus pacientes com infarto tipo 1, é citado na fonte como informação fisiopatológica que reforça a distinção biológica — mas o próprio documento de origem adverte que isso **não é um teste clínico capaz de descartar infarto individualmente**, e por isso não foi transformado em critério de decisão na árvore. Por fim, a fonte é explícita que dosar troponina de rotina em atleta assintomático, fora de uma pergunta clínica definida, não tem papel estabelecido como estratégia de rastreamento — reafirmado na conduta final da árvore.