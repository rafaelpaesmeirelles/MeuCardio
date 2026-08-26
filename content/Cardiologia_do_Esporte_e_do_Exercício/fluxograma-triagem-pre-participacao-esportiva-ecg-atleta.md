---
title: "Triagem cardiovascular pré-participação esportiva e ECG do atleta"
slug: fluxograma-triagem-pre-participacao-esportiva-ecg-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo Corvia: triagem-cardiovascular-pre-participacao-ecg-atleta-aha-acc-2025 (tema Cardiologia do Esporte e do Exercício)"
  - "Kim JH, Baggish AL, Levine BD, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. J Am Coll Cardiol. 2025;85(10):1059-1108. PMID: 39976316. DOI: 10.1016/j.jacc.2024.12.025."
  - "Versão simultânea: Kim JH, et al. Circulation. 2025;151:e716-e761. PMID: 39973614. DOI: 10.1161/CIR.0000000000001297."
---

# Triagem cardiovascular pré-participação esportiva e ECG do atleta

## Árvore de decisão

```mermaid
flowchart TD
    A["Atleta em avaliação cardiovascular pré-participação esportiva"] --> B["Realizar história cardiovascular e familiar direcionadas, mais exame físico"]
    B --> D1{"Achado sugestivo de doença cardiovascular na história ou no exame físico?"}
    D1 -->|"Sim"| C1(["Investigar dirigidamente conforme o achado (ecocardiograma, teste de esforço, Holter, ressonância cardíaca ou outro exame pertinente) antes de decidir a participação esportiva"])
    D1 -->|"Não"| D2{"Há profissional treinado em critérios de ECG específicos do atleta E via organizada de investigação de achados anormais?"}
    D2 -->|"Não"| C2(["Não realizar ECG de 12 derivações como rotina; manter história e exame físico como triagem; assegurar plano de emergência com DEA disponível"])
    D2 -->|"Sim"| E["Realizar ECG de 12 derivações, interpretado com critérios específicos do atleta"]
    E --> D3{"ECG mostra padrão que exige investigação (ex.: inversão de onda T patológica, depressão difusa de segmento ST, onda Q patológica, bloqueio completo de ramo esquerdo)?"}
    D3 -->|"Sim"| C3(["Investigação de segunda linha dirigida ao padrão eletrocardiográfico e ao contexto clínico (ecocardiograma, teste de esforço, Holter, ressonância cardíaca ou angiotomografia) antes de decidir a participação"])
    D3 -->|"Não, achado compatível com adaptação fisiológica do treinamento"| C4(["Liberar para prática esportiva competitiva; manter plano de emergência com DEA disponível independentemente do modelo de triagem"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4 conduta;
```

## Critérios usados na árvore

A declaração científica AHA/ACC 2025 (Kim JH et al., *J Am Coll Cardiol*. 2025;85(10):1059-1108; versão simultânea em *Circulation*. 2025;151:e716-e761) abandonou a dicotomia simples "ECG para todos" versus "ECG para ninguém". História cardiovascular e exame físico direcionados continuam obrigatórios em qualquer cenário, mas têm sensibilidade limitada para doença silenciosa.

O ECG de 12 derivações é considerado **razoável** de incluir no rastreamento, mas essa recomendação vem condicionada: o programa precisa ter profissional treinado em critérios contemporâneos específicos do atleta e uma via organizada de investigação dos achados anormais. Sem esse ecossistema, o próprio documento de origem alerta que um programa de ECG gera falsos positivos, exames desnecessários, ansiedade, custo e afastamento esportivo indevido — por isso a árvore trata a ausência dessa estrutura como motivo para não fazer ECG de rotina, e não como motivo para pular a etapa de investigação.

Achados eletrocardiográficos que justificam investigação dirigida, citados explicitamente na fonte: padrões específicos de inversão de onda T, depressão difusa do segmento ST, ondas Q patológicas e bloqueio completo de ramo esquerdo. Ecocardiograma, teste de esforço e monitorização ambulatorial de ritmo **não** são recomendados como rastreamento universal de primeira linha em atleta assintomático — são testes de segunda linha, selecionados conforme o achado clínico ou eletrocardiográfico, o que a árvore reflete ao só indicá-los depois de um achado positivo em uma das duas etapas anteriores.

A fonte também é explícita que nenhum programa de triagem elimina o risco de morte súbita — por isso plano de emergência (reconhecimento rápido de parada cardíaca, RCP de alta qualidade, DEA disponível, sistema coordenado de transporte) é indicado como parte da prevenção **independentemente** de qual ramo da árvore o atleta percorreu, e não foi desenhado como um ramo próprio, para não fragmentar essa recomendação transversal em vários nós repetidos.