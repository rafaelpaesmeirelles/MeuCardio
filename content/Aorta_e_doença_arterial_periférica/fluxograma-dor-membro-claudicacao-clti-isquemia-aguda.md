---
title: "Fluxograma: Dor em Membro Inferior — Claudicação, CLTI ou Isquemia Aguda?"
slug: fluxograma-dor-membro-claudicacao-clti-isquemia-aguda
theme: "Aorta e doença arterial periférica"
kind: fluxograma
summary: "Árvore de decisão para distinguir isquemia aguda de membro, isquemia crônica ameaçadora e DAP sintomática crônica; escolher ITB, ITB pós-exercício, TBI, imagem anatômica e reconhecer quando cilostazol não pode ser usado por insuficiência cardíaca."
review_status: revisado
source_refs: ["Gornik HL, Aronow HD, Goodney PP, et al. 2024 ACC/AHA/AACVPR/APMA/ABC/SCAI/SVM/SVN/SVS/SIR/VESS Guideline for the Management of Lower Extremity Peripheral Artery Disease. Circulation. 2024;149(24):e1313-e1410. DOI: 10.1161/CIR.0000000000001251. PMID: 38743805.", "Mazzolai L, Teixido-Tura G, Lanzi S, et al. 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases. Eur Heart J. 2024;45(36):3538-3700. DOI: 10.1093/eurheartj/ehae179. PMID: 39210722."]
---

# Fluxograma: Dor em Membro Inferior — Claudicação, CLTI ou Isquemia Aguda?

Este fluxograma deriva do documento `doenca-arterial-periferica-de-membros-diagnostico-por-itb-e-isquemia-critica` e responde primeiro à pergunta que muda prognóstico: **há ameaça imediata à viabilidade do membro?** Somente depois organiza a investigação fisiológica da DAP crônica.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Dor, fadiga, fraqueza, ferida<br/>ou alteração de perfusão em membro inferior"] --> D0{"Início súbito/agudo<br/>com membro frio, pálido, pulso ausente/reduzido,<br/>parestesia ou déficit motor?"}

  D0 -->|Sim| A0["Suspeitar isquemia aguda de membro — ALI<br/>avaliação vascular emergencial<br/>julgar viabilidade sem aguardar imagem avançada"]
  A0 --> D1{"Membro potencialmente salvável?"}
  D1 -->|Sim| A1["Heparina não fracionada sistêmica se não houver contraindicação<br/>+ estratégia urgente de revascularização<br/>imagem somente se não atrasar salvamento"]
  A1 --> C1(["Após controlar a ameaça ao membro<br/>investigar trombose sobre DAP, enxerto/stent,<br/>FA/fonte cardioembólica, aorta, trauma e estados pró-trombóticos"])
  D1 -->|Não| C0(["Membro irreversível/não salvável<br/>não realizar revascularização de tecido inviável<br/>definir manejo cirúrgico e sistêmico com equipe vascular"])

  D0 -->|Não| D2{"Há dor isquêmica em repouso,<br/>ferida que não cicatriza ou gangrena?"}
  D2 -->|Sim| A2["Suspeitar CLTI<br/>avaliação vascular rápida e multidisciplinar"]
  A2 --> A3["ITB + perfusão distal conforme contexto<br/>TBI/pressão do hálux com formas de onda,<br/>TcPO2 e/ou pressão de perfusão cutânea"]
  A3 --> C2(["Imagem arterial para planejar revascularização<br/>+ tratamento de ferida/infecção/descarga<br/>usar WIfI como estadiamento, não como comando automático de técnica"])

  D2 -->|Não| D3{"Sintoma é reproduzido por caminhada/esforço<br/>e melhora com repouso?"}
  D3 -->|Não| C3(["Reavaliar causas não arteriais<br/>neurológica, musculoesquelética, venosa,<br/>neuropatia e outras etiologias<br/>sem excluir DAP se risco vascular permanecer alto"])
  D3 -->|Sim| A4["Suspeitar DAP sintomática crônica<br/>realizar ITB de repouso"]

  A4 --> D4{"Resultado do ITB"}
  D4 -->|"≤ 0,90"| A5["DAP fisiologicamente confirmada"]
  D4 -->|"0,91–1,40"| A6["ITB de repouso normal/limítrofe<br/>mas sintomas persistem"]
  A6 --> C4(["Realizar ITB pós-exercício em esteira<br/>se sintomas ao esforço continuam sugestivos"])
  D4 -->|"> 1,40"| C5(["Artérias não compressíveis<br/>realizar TBI/pressão do hálux com formas de onda<br/>não rotular resultado como normal"])

  A5 --> A7["Redução de risco cardiovascular<br/>+ exercício estruturado/SET para claudicação"]
  A7 --> D5{"Cilostazol está sendo considerado<br/>para claudicação?"}
  D5 -->|Não| D6{"Claudicação segue<br/>funcionalmente limitante apesar de GDMT<br/>e exercício estruturado?"}
  D5 -->|Sim| D7{"Há insuficiência cardíaca<br/>de qualquer gravidade?"}
  D7 -->|Sim| C6(["NÃO usar cilostazol<br/>Classe III: dano na ACC/AHA 2024"])
  D7 -->|Não| A8["Cilostazol é terapia recomendada<br/>para melhorar sintomas e distância de caminhada"]
  A8 --> D6

  D6 -->|Não| C7(["Manter tratamento clínico e exercício<br/>reavaliar função e sintomas"])
  D6 -->|Sim| A9["Definir anatomia com duplex, angio-TC,<br/>angio-RM ou angiografia conforme caso"]
  A9 --> C8(["Discutir revascularização para melhora funcional<br/>incorporando anatomia, risco, durabilidade<br/>e objetivos do paciente"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C0,C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Como usar o ramo de isquemia aguda

Na ALI, o objetivo inicial é classificar **viabilidade do membro**, não obter o exame anatômico mais sofisticado. A ACC/AHA 2024 recomenda avaliação emergencial por profissional capaz de julgar viabilidade e implementar tratamento — **Classe I, C-EO** — e permite que essa avaliação inicial seja feita sem duplex, angio-TC ou angio-RM — **Classe I, C-LD**.

Déficit sensitivo e, sobretudo, **fraqueza/paralisia** elevam a suspeita de ameaça imediata. A classificação Rutherford ajuda a organizar o risco:

- **I:** viável;
- **IIa:** marginalmente ameaçado;
- **IIb:** imediatamente ameaçado;
- **III:** irreversível.

Em membro salvável, revascularização endovascular ou cirúrgica é indicada — **Classe I, A**. Heparina não fracionada sistêmica deve ser administrada no diagnóstico salvo contraindicação — **Classe I, C-EO**. A própria diretriz reconhece que esta anticoagulação é sustentada por prática consolidada/consenso e não por ensaio randomizado de heparina versus nenhuma anticoagulação.

## Como usar o ramo de DAP crônica

### ITB de repouso

Com história/exame sugestivos de DAP, ITB de repouso é recomendado — **Classe I, B-NR**. As categorias são:

- ≤0,90: anormal;
- 0,91–0,99: limítrofe;
- 1,00–1,40: normal;
- >1,40: não compressível.

### Sintoma típico, ITB normal/limítrofe

Se sintomas ao esforço continuam sugestivos com ITB >0,90 e ≤1,40, realizar **ITB pós-exercício — Classe I, B-NR**. Esse ramo existe para impedir o erro “ITB normal em repouso = DAP excluída”.

### ITB >1,40

Usar **TBI/pressão do hálux com formas de onda — Classe I, B-NR**. A ACC/AHA 2024 considera TBI ≤0,70 anormal. Diabetes e DRC aumentam a chance de artérias não compressíveis.

## Interação clínica que deve aparecer no grafo: cilostazol × insuficiência cardíaca

Na claudicação, cilostazol é recomendado para melhorar sintomas e distância de caminhada — **Classe I, A**. Porém, se o paciente tem **insuficiência cardíaca de qualquer gravidade**, cilostazol **não deve ser administrado — Classe III: dano, C-LD**.

Isso deve conectar três superfícies do CorVIA:

**DAP/claudicação → cilostazol → insuficiência cardíaca/contraindicação**.

O objetivo não é produzir alerta indiscriminado para todo uso do fármaco, mas evitar que uma recomendação legítima para claudicação seja exibida sem a principal condição cardiovascular que a invalida.

## Quando a imagem anatômica muda conduta

Imagem arterial não deve ser automaticamente pedida para toda claudicação. Ela ganha valor quando:

- claudicação permanece funcionalmente limitante apesar de tratamento orientado por guideline e exercício estruturado e revascularização está sendo considerada — **Classe I, B-NR**;
- há CLTI e a anatomia é necessária para planejar revascularização — **Classe I, B-NR**;
- a fisiologia permanece inconclusiva apesar de suspeita clínica — imagem não invasiva pode ser considerada — **Classe IIb, C-EO**.

## Conexões no CorVIA

- documento-base: `doenca-arterial-periferica-de-membros-diagnostico-por-itb-e-isquemia-critica`;
- fluxograma geral já existente: `fluxograma-dap-doenca-arterial-periferica`;
- fármaco: `cilostazol`;
- IC: módulos de insuficiência cardíaca para contraindicação do cilostazol;
- diabetes: rastreio de DAP silenciosa e ITB potencialmente enganoso;
- fibrilação atrial: fonte cardioembólica em ALI;
- aorta/aneurisma: fonte arterial de embolização;
- cardio-oncologia: `isquemia-aguda-de-membro-e-doenca-arterial-por-nilotinibe-ou-ponatinibe`;
- exames: ITB, ITB pós-exercício, TBI, duplex, angio-TC/angio-RM e medidas de perfusão distal;
- emergência: ALI ameaçando membro e necessidade de transferência quando não há capacidade de revascularização local.

## Limites

- claudicação é síndrome clínica; não deve ser diagnosticada por um único sintoma sem avaliação vascular;
- WIfI e Rutherford organizam risco, mas não escolhem isoladamente a técnica de revascularização;
- heparina na ALI tem recomendação forte de guideline, porém nível de evidência C-EO;
- a estratégia endovascular versus cirúrgica depende de anatomia, risco, conduit, durabilidade e experiência local;
- este fluxograma não contém esquema posológico e não substitui protocolo vascular local para anticoagulação e revascularização.
