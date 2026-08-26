---
title: "Síncope durante o exercício no atleta"
slug: fluxograma-sincope-durante-exercicio-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo Corvia: sincope-durante-exercicio-atleta-avaliacao-retorno-esporte (tema Cardiologia do Esporte e do Exercício)"
  - "Lampert R, et al. 2024 HRS expert consensus statement on arrhythmias in the athlete: Evaluation, treatment, and return to play. Heart Rhythm. 2024. PMID: 38763377. DOI: 10.1016/j.hrthm.2024.05.018."
  - "Kim JH, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. Circulation. 2025. PMID: 39973614. DOI: 10.1161/CIR.0000000000001297."
---

# Síncope durante o exercício no atleta

## Árvore de decisão

```mermaid
flowchart TD
    A["Atleta com episódio de síncope relacionado ao exercício"] --> D1{"A síncope ocorreu durante o esforço ou logo após a interrupção do exercício?"}
    D1 -->|"Durante o exercício"| B1["Tratar como sinal de alarme: não retornar ao treino competitivo antes de esclarecer causa cardíaca"]
    B1 --> D2{"Há sinais de alarme adicionais (ausência de pródromo típico, palpitação antes do evento, dor torácica ou dispneia desproporcional, ECG anormal, cardiopatia estrutural conhecida, história familiar de morte súbita, arritmia induzida pelo exercício, episódios recorrentes inexplicados)?"}
    D2 -->|"Sim"| C1(["Investigação cardíaca completa e dirigida ao achado: ecocardiograma, teste de esforço máximo reproduzindo a demanda da modalidade, monitorização ambulatorial, ressonância cardíaca, angiotomografia coronária e estudo genético conforme suspeita; restringir participação competitiva até esclarecimento"])
    D2 -->|"Não, mas o episódio ocorreu em pleno esforço"| C2(["Mesmo sem sinal de alarme adicional, investigar causas potencialmente graves (arritmia ventricular, canalopatia, cardiomiopatia, obstrução da via de saída, anomalia coronária) antes de liberar; restringir participação competitiva enquanto isso"])
    D1 -->|"Imediatamente após a interrupção do esforço"| D3{"Há sinais de alarme associados (mesmos critérios acima) ou recuperação atípica do episódio?"}
    D3 -->|"Sim"| C3(["Investigar como possível causa cardíaca: história detalhada, ECG com critérios específicos do atleta e exames adicionais dirigidos ao achado, antes de liberar"])
    D3 -->|"Não, recuperação típica de mecanismo reflexo"| C4(["Considerar mecanismo vasovagal/reflexo pós-esforço; orientar o atleta e permitir retorno gradual, sem restrição cardíaca adicional"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4 conduta;
```

## Critérios usados na árvore

O documento de origem, apoiado no consenso HRS 2024 (Lampert R, et al. *Heart Rhythm*. 2024. PMID 38763377) e no statement AHA/ACC 2025 (Kim JH, et al. *Circulation*. 2025. PMID 39973614), estabelece que a síncope no atleta deve ser interpretada primeiro **pelo momento em relação ao esforço**. Perder a consciência durante o exercício levanta suspeita para mecanismos potencialmente graves — arritmia ventricular, canalopatia, cardiomiopatia, obstrução dinâmica ou fixa da via de saída, anomalia coronária e doença estrutural — e deve ser tratada como sinal de alarme até que essas causas sejam excluídas, independentemente de outros achados. Já a síncope logo após a interrupção do esforço pode ter mecanismo reflexo (redução abrupta do retorno venoso), especialmente se o atleta ficou imóvel após esforço intenso — mas isso não é presumido automaticamente: a fonte é explícita que "síncope pós-esforço não é automaticamente benigna".

Os sinais que aumentam a preocupação, listados literalmente na fonte, são: síncope durante o esforço, ausência de pródromos típicos de mecanismo reflexo, palpitação imediatamente antes do evento, dor torácica ou dispneia desproporcional, ECG anormal, cardiopatia estrutural conhecida, história familiar de morte súbita prematura ou canalopatia/cardiomiopatia, arritmia induzida pelo exercício e episódios recorrentes sem explicação convincente.

A fonte recomenda que a avaliação comece por história direcionada, exame físico e ECG de 12 derivações com critérios específicos do atleta, escalando — conforme o achado — para ecocardiograma, teste de esforço máximo reproduzindo a demanda fisiológica da modalidade, monitorização ambulatorial, ressonância cardíaca, angiotomografia coronária e estudo genético quando há suspeita fenotípica ou familiar apropriada. Um atleta com síncope inexplicada durante exercício não deve retornar ao treino competitivo intenso antes de esclarecer causas cardíacas relevantes — restrição inicial de segurança, não proibição permanente. O retorno definitivo depende do diagnóstico final, do tratamento quando necessário, da ausência de arritmia relevante em avaliação apropriada e do risco residual específico da doença, sempre por decisão compartilhada — etapa posterior à árvore acima, que cobre a investigação inicial.