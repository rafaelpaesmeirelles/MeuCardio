---
title: "Fluxograma: Notificação de Pulso Irregular em Dispositivo Vestível — Confirmação Diagnóstica de Fibrilação Atrial"
slug: fluxograma-notificacao-pulso-irregular-dispositivo-vestivel-confirmacao-fa
theme: "Geral"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído a partir de duas diretrizes atuais lidas na íntegra por WebFetch em 26/08/2026: a ESC 2024 (AF-CARE, Eur Heart J. 2024;45(36):3314-3414, via academic.oup.com/eurheartj/article/45/36/3314/7738779) e a ACC/AHA/ACCP/HRS 2023/2024 (Circulation. 2024;149(1):e1-e156, texto integral via PMC11095842). As duas convergem no ponto central deste fluxograma: notificação de dispositivo baseado em fotopletismografia (smartwatch/anel inteligente) não estabelece diagnóstico de FA por si só; a confirmação exige ECG com traçado (12 derivações, ou single-lead/multiderivação com pelo menos 30 segundos de registro) interpretado por um médico. A ACC/AHA/ACCP/HRS 2023 cita isso como recomendação Classe 1 (COR 1, LOE B-NR) para o diagnóstico inicial de FA por interpretação visual do clínico, e afirma explicitamente que monitor de fotopletismografia 'não é suficientemente confiável para estabelecer diagnóstico de FA' isoladamente. O dado epidemiológico sobre frequência e valor preditivo da notificação reaproveita o Apple Heart Study, já verificado no documento correlato desta biblioteca (dispositivos-vestiveis-e-deteccao-de-fibrilacao-atrial-na-populacao-geral-o-apple-heart-study.md). Nenhum PMID, DOI ou classe de recomendação foi incluído sem confirmação direta na fonte; onde a diretriz não especificava um número (por exemplo, duração exata de monitorização ambulatorial dedicada fora do limiar de 30s), o fluxograma deixou a decisão como individualizada, sem inventar um cutoff."
source_refs: ["2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the European Association for Cardio-Thoracic Surgery (EACTS). Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723 — texto integral lido por WebFetch em 26/08/2026: dispositivos não-ECG baseados em fotopletismografia não estabelecem diagnóstico de FA; confirmação exige ECG de 12 derivações (10s) ou registro de single-lead/multiderivação com pelo menos 30 segundos, revisado por médico; achado assintomático em dispositivo implantado exige revisão de eletrograma intracardíaco ou traçado de ECG por profissional competente antes de qualquer conduta.", "Joglar JA, Chung MK, Armbruster AL, et al. 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation. Circulation. 2024;149(1):e1-e156. DOI: 10.1161/CIR.0000000000001193. PMID: 38033089. PMCID: PMC11095842 — texto integral lido por WebFetch em 26/08/2026: recomendação Classe 1 (COR 1, LOE B-NR), o diagnóstico inicial de FA em indivíduo sem história prévia deve ser feito por um clínico por interpretação visual do traçado eletrocardiográfico, independentemente do tipo de ritmo ou dispositivo de monitorização; monitor de fotopletismografia (smartwatch) pode alertar para obter um traçado de ECG, mas não é suficientemente confiável para estabelecer o diagnóstico isoladamente; uma vez com FA diagnosticada, é razoável (COR 2a, LOE B-R) recomendar dispositivo de ECG acessível ao consumidor, com traçado de boa qualidade, para detectar recorrência.", "Perez MV, Mahaffey KW, Hedlin H, et al; Apple Heart Study Investigators. Large-Scale Assessment of a Smartwatch to Identify Atrial Fibrillation. N Engl J Med. 2019;381(20):1909-1917. DOI: 10.1056/NEJMoa1901183. PMID: 31722151. PMCID: PMC8112605 — usado apenas para o dado epidemiológico de fundo: notificação de pulso irregular foi rara (0,52% dos participantes monitorados), com valor preditivo positivo de 0,84 no cenário de maior concordância, mas a maioria dos notificados que completou a investigação formal (patch de ECG) não tinha FA confirmada (34% de positividade); já detalhado no documento correlato desta biblioteca."]
---

# Fluxograma: Notificação de Pulso Irregular em Dispositivo Vestível — Confirmação Diagnóstica de Fibrilação Atrial

Relógios e anéis inteligentes de consumo hoje emitem notificações de "pulso irregular" ou "possível fibrilação atrial" com base em fotopletismografia óptica, fora de qualquer contexto clínico. Esse é hoje um dos motivos mais comuns de procura espontânea ao cardiologista por paciente sem diagnóstico prévio e sem sintoma. O ponto que este fluxograma resolve é simples de enunciar e fácil de errar na prática: a notificação do dispositivo é um **gatilho para investigação**, nunca um diagnóstico — tanto a ESC 2024 quanto a ACC/AHA/ACCP/HRS 2023 são explícitas em exigir um traçado de ECG interpretado por médico (12 derivações, ou single-lead/multiderivação com pelo menos 30 segundos) antes de rotular o paciente como portador de FA e antes de qualquer decisão terapêutica, incluindo anticoagulação.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente sem diagnóstico prévio de FA<br/>procura atendimento por notificação de<br/>'pulso irregular' ou 'possível FA' emitida por<br/>relógio ou anel inteligente (fotopletismografia)"] --> D0{"Há sintoma atual de alarme?<br/>dor torácica importante, síncope/pré-síncope,<br/>dispneia significativa ou instabilidade hemodinâmica"}

  D0 -->|Sim| C1(["Não aguardar confirmação ambulatorial:<br/>avaliação de urgência com ECG de 12 derivações imediato<br/>e conduta pelo sintoma dominante<br/>(fluxo de FA de início recente no pronto-socorro<br/>ou de dor torácica, conforme o caso)"])

  D0 -->|Não| P1["Anamnese dirigida — fatores de risco cardioembólico/estrutural,<br/>estimulantes, frequência e reprodutibilidade das notificações —<br/>e ECG de 12 derivações no atendimento"]

  P1 --> D1{"O ECG de 12 derivações feito na consulta<br/>mostra FA no momento do exame?"}

  D1 -->|Sim| C2(["Diagnóstico clínico de FA confirmado<br/>por ECG de 12 derivações interpretado por médico —<br/>seguir a trajetória AF-CARE<br/>(comorbidades, CHA2DS2-VA, controle de sintoma)"])

  D1 -->|"Não, ritmo sinusal na consulta"| D2{"Notificação é recorrente<br/>ou paciente tem fator de risco cardioembólico/estrutural relevante<br/>(idade avançada, hipertensão, IC, valvopatia,<br/>AVC prévio, apneia do sono)?"}

  D2 -->|"Não, episódio único e baixo risco"| P2["Orientar registro de ECG por dispositivo de nível clínico<br/>na próxima notificação — single-lead ou multiderivação<br/>com traçado real, nunca fotopletismografia isolada —<br/>ou repetir ECG em nova consulta se recorrer"]

  P2 --> D3{"Traçado obtido (pelo paciente ou em consulta)<br/>mostra FA por 30 segundos ou mais,<br/>revisado por médico?"}

  D3 -->|Sim| C3(["Diagnóstico clínico de FA confirmado —<br/>seguir a trajetória AF-CARE<br/>(comorbidades, CHA2DS2-VA, controle de sintoma)"])

  D3 -->|Não| C4(["FA não confirmada:<br/>orientar que fotopletismografia isolada não é diagnóstico,<br/>manter uso do dispositivo para nova notificação<br/>e reavaliar se recorrer ou surgir sintoma"])

  D2 -->|"Sim, recorrente ou risco relevante"| P3["Monitorização ambulatorial dedicada com traçado de ECG<br/>(Holter estendido, monitor de eventos ou patch),<br/>duração definida pela frequência das notificações<br/>e pela suspeita clínica"]

  P3 --> D4{"Monitorização dedicada confirma FA —<br/>ECG com FA por 30 segundos ou mais,<br/>ou 12 derivações, revisado por médico?"}

  D4 -->|Sim| C5(["Diagnóstico clínico de FA confirmado —<br/>seguir a trajetória AF-CARE<br/>(comorbidades, CHA2DS2-VA, controle de sintoma)"])

  D4 -->|Não| D5{"Monitorização mostra episódio atrial de alta frequência<br/>que não atinge o limiar de FA clínica<br/>(muito breve ou não revisado como FA)?"}

  D5 -->|Sim| C6(["Não rotular como FA clínica nem iniciar anticoagulação<br/>pelo achado isolado: registrar achado subclínico,<br/>individualizar seguimento e reforçar controle<br/>de fator de risco cardiovascular"])

  D5 -->|Não| C7(["FA não confirmada:<br/>orientar que fotopletismografia isolada não é diagnóstico,<br/>manter uso do dispositivo para nova notificação<br/>e reavaliar se recorrer ou surgir sintoma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Por que a fotopletismografia sozinha não fecha o diagnóstico

A ESC 2024 é explícita: a recomendação de confirmação diagnóstica "não inclui dispositivos vestíveis não baseados em ECG e outros dispositivos que tipicamente usam fotopletismografia". O padrão aceito é um traçado real — ECG de 12 derivações (10 segundos) ou registro de single-lead/multiderivação com pelo menos 30 segundos — sempre revisado por um médico. A ACC/AHA/ACCP/HRS 2023 chega à mesma exigência por um caminho formal: recomendação Classe 1 (COR 1, LOE B-NR) de que o diagnóstico inicial de FA seja feito por interpretação visual do clínico sobre o sinal eletrocardiográfico, "independentemente do tipo de ritmo ou dispositivo de monitorização". A mesma diretriz nomeia o papel correto do smartwatch: ele pode **alertar** o paciente a buscar um ECG, mas "não é suficientemente confiável para estabelecer diagnóstico de FA" isoladamente.

## Achado de alta frequência atrial abaixo do limiar clínico

Quando a monitorização dedicada não encontra FA sustentada por 30 segundos ou mais, mas mostra episódios atriais rápidos muito breves, o caso não deve ser tratado como FA clínica — e também não deve ser descartado sem registro. A ESC 2024 trata esse cenário como o mesmo problema da FA subclínica detectada por dispositivo já implantado: exige revisão de um profissional competente sobre o traçado antes de qualquer conduta, e não autoriza equiparar automaticamente o achado a indicação de anticoagulação. Este fluxograma para de propósito nesse ponto — a decisão fina de quando tratar um episódio subclínico está fora do escopo de uma notificação de smartwatch e é tratada no documento desta biblioteca sobre FA subclínica por dispositivo implantado (NOAH-AFNET 6/ARTESiA).

## O que este fluxograma deliberadamente não faz

- não trata a notificação do dispositivo como diagnóstico, em nenhum ramo;
- não decide anticoagulação — uma vez confirmada a FA clínica, a decisão de anticoagular segue o CHA2DS2-VA na trajetória AF-CARE, não este fluxograma;
- não define rastreio populacional ativo de FA (convocar quem nunca teve notificação alguma) — essa é a pergunta do LOOP e do STROKESTOP, documentada à parte;
- não cria cutoff próprio de duração para Holter, monitor de eventos ou patch além do limiar de 30 segundos citado nas diretrizes;
- não se aplica a paciente com FA já diagnosticada ou com dispositivo cardíaco implantável prévio (marca-passo, CDI) — esse achado incidental tem trajetória própria.

## Conexões no CorVIA

- Documento-base sobre o próprio dispositivo: `dispositivos-vestiveis-e-deteccao-de-fibrilacao-atrial-na-populacao-geral-o-apple-heart-study`;
- Diagnóstico confirmado, próximo passo: `fluxograma-fibrilacao-atrial-af-care-esc-2024`;
- Sintoma agudo/instabilidade: `fluxograma-fa-inicio-recente-pronto-socorro`;
- Rastreio ativo de FA em população sem notificação prévia: `rastreio-populacional-de-fibrilacao-atrial-no-idoso-loop-e-strokestop`.
