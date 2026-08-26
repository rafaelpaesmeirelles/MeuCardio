---
title: "Fluxograma: Síncope Situacional — Diferencial por Gatilho e Conduta (ESC 2018)"
slug: fluxograma-sincope-situacional-diferencial-e-conduta-por-gatilho
theme: "Síncope"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Documento novo. O corpus já tinha síncope situacional descrita em prosa (sincope-situacional-miccional-defecatoria-tussigena-e-de-degluticao.md, mesma fonte primária Zou et al. 2020) e em fluxogramas dedicados a avaliação inicial geral, alto risco na emergência, síncope reflexa versus cardíaca, síncope inexplicada recorrente e cardioneuroablação — nenhum deles é uma árvore de decisão estrita organizada por gatilho situacional específico com conduta diferenciada por subtipo. Este fluxograma preenche esse recorte sem duplicar conteúdo: a classificação de sinais de alarme e o encaminhamento para tilt test/monitor de eventos remetem aos fluxogramas já publicados em vez de repeti-los. PMID 31843331 e PMID 29562304 conferidos via PubMed E-utilities (esummary) antes da redação — título, revista, volume, página e ano batendo exatamente."
source_refs: ["Zou R, Wang S, Lin P, Hu C, Wang Y, Li F, Xu Y, Wang C. The clinical characteristics of situational syncope in children and adults undergoing head-up tilt testing · American Journal of Emergency Medicine · 2020 · 38(7):1419-1423 · DOI: 10.1016/j.ajem.2019.11.042 · PMID: 31843331", "Brignole M, Moya A, de Lange FJ, et al. 2018 ESC Guidelines for the diagnosis and management of syncope · European Heart Journal · 2018 · 39(21):1883-1948 · DOI: 10.1093/eurheartj/ehy037 · PMID: 29562304"]
---

# Fluxograma: Síncope Situacional — Diferencial por Gatilho e Conduta

## Por que separar por gatilho
A síncope situacional é classificada pela ESC 2018 como um subtipo de síncope reflexa, mas os gatilhos que a compõem (miccional, defecatória, tussígena, deglutição e outros menos clássicos) têm mecanismos fisiopatológicos distintos entre si — e é o gatilho identificado, não o rótulo "situacional" genérico, que orienta a conduta prática. Este fluxograma organiza essa distinção como árvore de decisão, a partir da coorte de 3.140 pacientes avaliados por tilt test de Zou et al. (2020), na qual 354 (11,3%) foram diagnosticados com síncope situacional — miccional 50,85% dos casos, defecatória 15,82%, banho 10,45%, deglutição 6,50%, tosse 4,80%, pós-prandial 3,95%, canto 3,11%, escovação dos dentes 2,26% e penteado do cabelo 2,26%.

## Árvore de decisão

```mermaid
flowchart TD
    RAIZ["Perda transitória de consciência com recuperação espontânea, ocorrida durante ou imediatamente após gatilho situacional identificável (micção, defecação, tosse, deglutição ou outro esforço/estímulo reconhecível)"]
    RAIZ --> D1
    D1{"Sinais de alarme presentes? (síncope aos esforços, história familiar de morte súbita, cardiopatia estrutural conhecida, ECG anormal na avaliação inicial, ausência de pródromo típico, ou síncope traumática)"}
    D1 -->|"Sim"| C1(["Não assumir síncope situacional benigna: encaminhar para investigação cardíaca estruturada (ECG, ecocardiograma, avaliação especializada) independentemente do gatilho aparente, conforme os critérios de alto risco já estabelecidos na avaliação inicial da síncope"])
    D1 -->|"Não"| D2{"Qual foi o gatilho identificado?"}
    D2 -->|"Miccional ou defecatória"| R1["Mecanismo: manobra de Valsalva (esforço abdominal contra glote fechada) reduz o retorno venoso, o débito sistólico, a pressão arterial e o fluxo cerebral"]
    D2 -->|"Tussígena"| R2["Mecanismo: reflexo vasodepressor-bradicárdico mediado neuralmente, desencadeado pela tosse"]
    D2 -->|"Deglutição"| C5(["Educar sobre o reflexo vagovagal gastrointestinal-cardíaco desencadeado pela deglutição e distensão gástrica rápida; orientar refeições fracionadas e deglutição pausada; tranquilizar quanto à natureza benigna do episódio"])
    D2 -->|"Outro gatilho situacional (banho, período pós-prandial, canto, escovação dos dentes, penteado do cabelo)"| C6(["Reconhecer o gatilho menos clássico como causa situacional legítima; aplicar a mesma conduta de base dos demais subtipos: educação, orientação de estilo de vida e tranquilização quanto à natureza benigna"])
    R1 --> D3{"Episódio recorrente apesar de orientação comportamental inicial (evitar ortostatismo prolongado pós-esforço, esvaziar vesical/intestinal sentado quando possível, hidratação adequada)?"}
    D3 -->|"Não — episódio único ou esporádico"| C2(["Educação, orientação de estilo de vida e tranquilização quanto à natureza benigna — conduta aplicada à maioria dos pacientes com síncope miccional ou defecatória na coorte de referência"])
    D3 -->|"Sim — recorrência apesar das medidas"| C3(["Reavaliar o diagnóstico e encaminhar para investigação de síncope reflexa recorrente (tilt test / monitor de eventos implantável), seguindo o fluxograma dedicado a síncope inexplicada recorrente"])
    R2 --> D4{"Causa da tosse crônica/subjacente identificada e tratável (ex.: DPOC, refluxo, uso de IECA, asma)?"}
    D4 -->|"Sim"| C4(["Tratar a causa da tosse subjacente — como a perda de consciência é consequência direta do próprio episódio de tosse, eliminar o gatilho tende a eliminar o episódio sincopal"])
    D4 -->|"Não identificada ou não tratável na avaliação atual"| C7(["Encaminhar para investigação pneumológica ou otorrinolaringológica dedicada da tosse crônica; manter educação sobre o mecanismo e acompanhamento"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que vale para todos os ramos, e não está no diagrama
Independentemente do gatilho identificado e da conduta escolhida em cada folha da árvore, dois pontos são transversais e não repetidos em cada ramo:

- **Reavaliação de sinais de alarme a cada recorrência.** Um padrão inicialmente compatível com síncope situacional benigna não isenta o paciente de reavaliação se o padrão do episódio mudar (novo pródromo ausente, aparecimento de sintomas ao esforço, trauma associado) — a árvore trata os sinais de alarme na entrada, mas a vigilância é contínua, não um filtro único.
- **Prognóstico geral favorável na ausência de doença sistêmica associada.** Na coorte de referência, eventos adversos relacionados à síncope situacional foram raros — o que sustenta a conduta predominantemente educativa em quase todos os ramos, exceto quando um sinal de alarme desvia o paciente para investigação cardíaca estruturada.

## Armadilhas clínicas
- Investigar exaustivamente com exames cardíacos invasivos um paciente jovem com episódio único e claro de síncope miccional noturna, sem sinais de alarme — o padrão típico dispensa investigação extensa na maioria dos casos.
- Tratar síncope tussígena como "síncope reflexa comum" sem investigar e tratar a causa da tosse persistente — eliminar o gatilho é o tratamento mais eficaz nesse subtipo específico, não a orientação genérica sobre síncope.
- Ignorar gatilhos menos clássicos (canto, escovação dos dentes, penteado do cabelo, período pós-prandial) como possíveis desencadeantes situacionais — a lista de gatilhos descritos na literatura é mais ampla do que os exemplos mais citados (micção, defecação, tosse).
- Assumir que toda recorrência é sempre benigna sem reavaliar sinais de alarme — recorrência apesar de medidas comportamentais é o ponto da árvore em que o encaminhamento para investigação adicional (tilt test / monitor de eventos) se torna apropriado.
