---
title: "Fluxograma: Cardiopatia Reumática Subclínica — Estadiamento Ecocardiográfico A-D e Seguimento (WHF 2023)"
slug: fluxograma-cardiopatia-reumatica-subclinica-estadiamento-whf-2023
theme: "Febre reumática"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Nenhum dos 5 fluxogramas já publicados em Febre reumática cobre o seguimento ecocardiográfico da cardiopatia reumática SUBCLÍNICA (eles cobrem critérios de Jones, graduação/tratamento da cardite aguda, artrite/PSRA, duração da profilaxia secundária e decisão de intervenção na valvopatia mitral crônica já estabelecida) — lacuna confirmada por leitura direta dos 5 arquivos com kind: fluxograma na pasta antes de escrever. Árvore construída a partir do documento já publicado e verificado nesta mesma pasta (criterios-ecocardiograficos-whf-2023-rastreamento-confirmacao-e-estadiamento.md), com a tabela de estadiamento A-D, os cortes de característica morfológica por idade e a nota de que 50% dos casos limítrofes e 30% dos leves regridem espontaneamente. Os dois PMIDs citados nesse documento foram RECONFERIDOS nesta sessão, diretamente via PubMed E-utilities (esummary): PMID 37914787 confere título/revista/DOI (2023 World Heart Federation guidelines for the echocardiographic diagnosis of rheumatic heart disease; Nat Rev Cardiol; abril de 2024; DOI 10.1038/s41569-023-00940-9); PMID 38532021 confere (Author Correction; Nat Rev Cardiol; maio de 2024; DOI 10.1038/s41569-024-01018-w). Nenhum PMID/DOI novo foi inventado. O ramo de característica morfológica única em paciente acima de 20 anos, e o ramo de regurgitação leve confirmada sem morfologia em paciente acima de 20 anos, terminam em conduta que registra explicitamente a assimetria que a própria diretriz não resolve (não existe Estágio A para o adulto; 1 característica não basta para Estágio B no adulto) — decisão de não fabricar um corte que a fonte não define, mantendo a árvore como leitura fiel do documento-fonte."
source_refs: ["2023 World Heart Federation guidelines for the echocardiographic diagnosis of rheumatic heart disease · Nature Reviews Cardiology · Rwebembera J, Marangou J, Mwita JC, Mocumbi AO, Mota C, et al. · 2024 Apr;21(4):250-263 · DOI: 10.1038/s41569-023-00940-9 · PMID: 37914787 — reconferido via PubMed E-utilities (esummary) nesta sessão, título/revista/DOI batendo exatamente", "Author Correction: 2023 World Heart Federation guidelines for the echocardiographic diagnosis of rheumatic heart disease · Nature Reviews Cardiology · 2024 May;21(5):347 · DOI: 10.1038/s41569-024-01018-w · PMID: 38532021 — reconferido via PubMed E-utilities (esummary) nesta sessão; errata de referência cruzada (Box 4 para Box 5), sem alteração de valor numérico"]
---

# Fluxograma: Cardiopatia Reumática Subclínica — Estadiamento Ecocardiográfico A-D e Seguimento (WHF 2023)

## Definição
Este fluxograma organiza a decisão de **estadiamento e seguimento** de um achado ecocardiográfico já avaliado pelos critérios **CONFIRMATÓRIOS** da World Heart Federation (WHF) 2023 — a etapa que vem **depois** do rastreamento, quando se decide em que estágio A-D o paciente se encontra e qual o intervalo de reavaliação. É um recorte diferente dos cinco fluxogramas já publicados nesta pasta: eles cobrem o diagnóstico da febre reumática aguda (critérios de Jones), a graduação e o tratamento da cardite na fase aguda, o diagnóstico diferencial de artrite/PSRA, a duração da profilaxia secundária e a decisão de intervenção na valvopatia mitral **crônica já estabelecida**. Aqui a pergunta é anterior a todas essas: **este achado ecocardiográfico é cardiopatia reumática subclínica, em que estágio, e com que conduta de seguimento?**

A nomenclatura antiga ("borderline", "definite", "latente") foi aposentada pela WHF 2023 em favor do estadiamento A-D, e essa troca não é só de rótulo: o **estágio A carrega conduta própria** (reavaliação em 1-2 anos, com possibilidade de suspender a profilaxia se o exame normalizar) que o termo "borderline" nunca teve associada de forma padronizada.

## Dois pontos que a árvore assume como já resolvidos, e por quê
- **Critérios confirmatórios, não de rastreio.** A WHF 2023 separa critérios de rastreamento (para busca ativa, até 20 anos) dos confirmatórios (para o especialista, qualquer idade). Este fluxograma parte do zero já usando os confirmatórios — velocidade ≥3,0 m/s, jato pansistólico/pandiastólico, gradiente ≥4,0 mmHg na estenose — porque é isso que autoriza estadiamento.
- **Excluir causas não reumáticas de regurgitação leve já é pré-requisito da própria diretriz** — sobretudo prolapso de valva mitral e valva aórtica bicúspide — antes de aplicar qualquer ramo desta árvore.

## Duas assimetrias que a própria diretriz reconhece, e que a árvore não esconde
A diretriz é explícita: **o estágio A simplesmente não existe para o adulto** (só se aplica até 20 anos), e o número de características morfológicas exigido para o estágio B é **assimétrico por idade** — 1 característica basta até 20 anos, mas são exigidas **2** acima de 20 anos. Isso deixa dois cenários sem estágio formal definido pela diretriz: adulto com regurgitação leve confirmada e **zero** características morfológicas, e adulto com regurgitação leve confirmada e **apenas 1** característica. A árvore termina esses dois ramos com a conduta honesta — reavaliação programada e decisão clínica individualizada — em vez de inventar um corte que a fonte não define.

## Números que sustentam a conduta de reavaliar em vez de intervir no estágio A/B
A própria diretriz registra que **até 50% dos casos limítrofes (estágio A) e 30% dos casos leves regridem espontaneamente** — é o que justifica reavaliar em 1-2 anos em vez de tratar agressivamente um achado inicial mínimo, e é também o que justifica considerar suspender a profilaxia secundária se o exame normalizar nesse intervalo.

## Árvore de decisão

```mermaid
flowchart TD
    R["Ecocardiograma com achado sugestivo de cardiopatia reumática,<br/>avaliado pelos critérios CONFIRMATÓRIOS de disfunção valvar (WHF 2023)"]
    D1{"Estenose mitral ou aórtica (qualquer gravidade),<br/>OU regurgitação mitral/aórtica moderada a grave,<br/>OU hipertensão pulmonar, OU disfunção sistólica de VE?"}
    R --> D1
    D2{"Complicação clínica já estabelecida?<br/>(cirurgia cardíaca prévia, insuficiência cardíaca,<br/>arritmia, AVC ou endocardite infecciosa)"}
    D1 -->|"Sim"| D2
    C1(["Estágio D — avançada, com complicação estabelecida:<br/>encaminhar para avaliação de intervenção valvar/cirúrgica;<br/>seguimento especializado"])
    D2 -->|"Sim"| C1
    C2(["Estágio C — avançada, com risco de complicação:<br/>seguimento ecocardiográfico mais frequente;<br/>avaliar indicação de intervenção valvar;<br/>manter profilaxia secundária"])
    D2 -->|"Não"| C2
    D3{"Regurgitação mitral ou aórtica LEVE,<br/>confirmada pelos critérios da WHF 2023<br/>(ao menos uma valva)?"}
    D1 -->|"Não (sem estenose, sem HP/disfunção de VE,<br/>regurgitação no máximo leve)"| D3
    C3(["Ecocardiograma sem critério de cardiopatia reumática (WHF 2023):<br/>não indicar profilaxia secundária com base neste exame;<br/>investigar diagnóstico alternativo se houver suspeita clínica"])
    D3 -->|"Não — sem regurgitação patológica confirmada"| C3
    D4{"Regurgitação leve confirmada presente<br/>nas DUAS valvas simultaneamente,<br/>mitral E aórtica?"}
    D3 -->|"Sim"| D4
    C4(["Estágio B — leve (regurgitação leve mitral e aórtica combinada):<br/>risco moderado a alto de progressão;<br/>seguimento ecocardiográfico periódico;<br/>manter profilaxia secundária"])
    D4 -->|"Sim"| C4
    D5{"Número de características morfológicas confirmatórias<br/>(espessamento do folheto anterior mitral por corte de idade,<br/>anormalidade de mobilidade valvar, achados aórticos confirmatórios)?"}
    D4 -->|"Não (regurgitação leve em uma única valva)"| D5
    C7(["Estágio B — leve: regurgitação leve<br/>+ 2 ou mais características morfológicas;<br/>risco moderado a alto de progressão;<br/>seguimento ecocardiográfico periódico;<br/>manter profilaxia secundária"])
    D5 -->|"Duas ou mais características"| C7
    D6{"Idade do paciente ≤20 anos?"}
    D5 -->|"Uma característica"| D6
    C7b(["Estágio B — leve: regurgitação leve<br/>+ 1 característica morfológica (critério válido até 20 anos);<br/>risco moderado a alto de progressão;<br/>seguimento ecocardiográfico periódico;<br/>manter profilaxia secundária"])
    D6 -->|"Sim (≤20 anos: 1 característica já basta para Estágio B)"| C7b
    C8(["Assimetria reconhecida pela própria WHF 2023: 1 característica<br/>morfológica não basta para Estágio B no adulto (exige ≥2),<br/>e não há Estágio A acima de 20 anos — a diretriz não define<br/>conduta explícita para este cenário; reavaliação ecocardiográfica<br/>programada e decisão individualizada, correlacionando com o quadro clínico"])
    D6 -->|"Não (>20 anos)"| C8
    D7{"Idade do paciente ≤20 anos?"}
    D5 -->|"Nenhuma característica morfológica"| D7
    C5(["Estágio A — critérios mínimos ('borderline'), só até 20 anos:<br/>reavaliação ecocardiográfica em 1-2 anos;<br/>considerar suspender a profilaxia secundária se o exame normalizar<br/>(até 50% dos casos limítrofes regridem espontaneamente)"])
    D7 -->|"Sim (≤20 anos)"| C5
    C9(["Sem Estágio A para o adulto (a diretriz não o define acima de 20 anos):<br/>regurgitação leve confirmada, sem característica morfológica —<br/>reavaliação ecocardiográfica programada e decisão individualizada,<br/>excluindo causas não reumáticas (prolapso mitral, valva aórtica bicúspide)"])
    D7 -->|"Não (>20 anos)"| C9

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5,C7,C7b,C8,C9 conduta;
```

## Armadilhas clínicas
- **Laudar "cardiopatia reumática limítrofe" ou "definitiva".** A nomenclatura foi aposentada pela WHF 2023; o estágio A carrega conduta própria (reavaliação programada, possibilidade de suspender profilaxia) que o termo antigo não tinha associada de forma padronizada.
- **Aplicar os critérios de RASTREAMENTO no adulto.** Acima de 20 anos a diretriz exige os critérios CONFIRMATÓRIOS — a evidência do rastreio nessa faixa etária é limitada, e é a partir dos confirmatórios que esta árvore de estadiamento começa.
- **Assumir que existe Estágio A no adulto.** Não existe — é uma assimetria explícita da própria diretriz, não uma omissão deste fluxograma.
- **Usar o mesmo corte de característica morfológica em qualquer idade.** É assimétrico: 1 característica basta até 20 anos, são exigidas 2 acima de 20 anos.
- **Tratar achado de estágio A/B como indicação de intervenção.** Não é — a conduta nos estágios A e B é seguimento ecocardiográfico periódico e manutenção/consideração de suspensão da profilaxia secundária, não intervenção valvar. Intervenção entra na conversa a partir do estágio C.
- **Esquecer de excluir prolapso de valva mitral e valva aórtica bicúspide** antes de rotular uma regurgitação leve como reumática — pré-requisito da própria diretriz.
- **Ignorar que boa parte dos achados iniciais regride espontaneamente.** Até 50% dos casos limítrofes e 30% dos leves — é o que justifica reavaliar antes de escalonar conduta.
