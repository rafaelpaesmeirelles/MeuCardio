---
title: "Fluxograma: Palpitações — avaliação inicial ambulatorial sem diagnóstico prévio"
slug: fluxograma-palpitacoes-avaliacao-inicial-ambulatorial
theme: "Geral"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para a queixa indiferenciada de palpitações em consulta ambulatorial: reconhece sinais de alarme, distingue o padrão sugestivo de taquicardia supraventricular ou de fibrilação atrial (encaminhando para os fluxogramas específicos), e escolhe o método de monitorização ambulatorial pela frequência dos episódios, com triagem extracardíaca quando a causa não é arrítmica."
review_status: revisado
review_note: "PMID conferidos via PubMed E-utilities (esearch/esummary) em 26/08/2026: 21697315 (Raviele et al., posicionamento da EHRA — fonte primária do algoritmo de sinais de alarme e da escolha de monitorização por frequência de episódios) e 9571258 (Zimetbaum & Josephson, NEJM — fonte clássica complementar sobre estratégia de monitorização e diagnóstico diferencial). Recorte verificado contra o corpus de Geral (4 fluxogramas existentes, nenhum sobre palpitações) e contra os temas dedicados Arritmias/Fibrilação_atrial/Síncope, que já cobrem taquicardia de QRS estreito/largo, FA e síncope especificamente — este fluxograma cobre só a investigação inicial indiferenciada, antes de um desses diagnósticos estar estabelecido, e encaminha explicitamente para os fluxogramas específicos quando o padrão relatado já sugere um deles."
source_refs: ["Raviele A, Giada F, Bergfeldt L, Blanc JJ, Blomstrom-Lundqvist C, Mont L, Morgan JM, Raatikainen MJ, Steinbeck G, Viskin S, Kirchhof P, Braunschweig F, Borggrefe M, Hocini M, Della Bella P, Shah DC; European Heart Rhythm Association. Management of patients with palpitations: a position paper from the European Heart Rhythm Association. Europace. 2011 Jul;13(7):920-34. DOI: 10.1093/europace/eur130. PMID: 21697315.", "Zimetbaum P, Josephson ME. Evaluation of patients with palpitations. N Engl J Med. 1998 May 7;338(19):1369-73. DOI: 10.1056/NEJM199805073381907. PMID: 9571258."]
---

# Fluxograma: Palpitações — avaliação inicial ambulatorial sem diagnóstico prévio

A queixa de "palpitação" no consultório não é um diagnóstico — é um sintoma que pode vir de arritmia sustentada, extrassistolia isolada, ansiedade, causa metabólica ou, com frequência, de nenhuma delas identificável no momento da consulta. Este fluxograma cobre a **primeira consulta ambulatorial, com o paciente estável**, sem diagnóstico arrítmico prévio — a etapa que decide se o caso já tem padrão reconhecível (e deve migrar para o fluxograma específico de taquicardia ou de fibrilação atrial) ou se depende de monitorização prolongada para captar o ritmo durante o sintoma. Não é um fluxograma de emergência: paciente instável, com palpitação associada a síncope franca, dor torácica ou sinais de choque no momento do atendimento não segue este caminho — vai direto para avaliação cardiovascular prioritária.

A estrutura segue o posicionamento da European Heart Rhythm Association (Raviele et al., Europace 2011): anamnese e ECG basal primeiro; sinais de alarme decidem prioridade e via de investigação; padrão do sintoma relatado (regular versus irregular, início/término súbitos versus graduais) direciona para os fluxogramas de arritmia específica quando aplicável; e, na ausência de sinal de alarme e de padrão sugestivo de taquicardia ou FA, a frequência dos episódios — não a gravidade percebida pelo paciente — é o que escolhe o método de monitorização ambulatorial, do Holter de 24-48h ao monitor de eventos implantável. Zimetbaum & Josephson (NEJM 1998) sustentam a mesma lógica de escalonamento por frequência de sintoma e complementam a discussão da triagem extracardíaca.

## Árvore de decisão

```mermaid
flowchart TD
  R["Paciente relata palpitações em consulta ambulatorial, sem diagnóstico arrítmico prévio, estável no momento do atendimento"] --> D1{"Anamnese e exame físico dirigidos: há sinal de alarme — síncope/pré-síncope associada, palpitação desencadeada pelo esforço físico, cardiopatia estrutural conhecida, história familiar de morte súbita ou cardiomiopatia hereditária, ou ECG de 12 derivações basal anormal?"}

  D1 -->|"Sim"| C1(["Encaminhar com prioridade à cardiologia/eletrofisiologia — ecocardiograma, teste ergométrico e estratificação de risco antes de definir a estratégia de monitorização ambulatorial (EHRA 2011)"])
  D1 -->|"Não"| X2["Caracterizar o padrão relatado pelo paciente: ritmo regular ou irregular, início e término súbitos ou graduais"]

  X2 --> D2{"O padrão relatado é regular, rápido, de início e término súbitos, sugestivo de taquicardia supraventricular?"}
  D2 -->|"Sim"| C2(["Conduzir pelo fluxograma específico de taquicardia de QRS estreito/largo (ESC 2019) — não reiniciar a investigação genérica de palpitação"])
  D2 -->|"Não"| D3{"O padrão relatado é irregular, tipo 'batimentos caóticos e imprevisíveis', sugestivo de fibrilação atrial?"}

  D3 -->|"Sim"| C3(["Conduzir pelo fluxograma específico de fibrilação atrial de início recente ou pela via AF-CARE (ESC 2024) — não reiniciar a investigação genérica de palpitação"])
  D3 -->|"Não"| X3["Palpitação inespecífica, extrassistolia isolada ou sensação de 'falha'/'batimento forte': estimar a frequência dos episódios para escolher o método de monitorização ambulatorial (EHRA 2011; Zimetbaum e Josephson 1998)"]

  X3 --> D4{"Qual a frequência aproximada dos episódios?"}
  D4 -->|"Diária"| C4(["Holter de 24-48 horas"])
  D4 -->|"Semanal a mensal"| C5(["Monitor de eventos externo (looper), 2-4 semanas, ativado pelo paciente no momento do sintoma"])
  D4 -->|"Esporádica (menos de uma vez ao mês), recorrente e incapacitante"| C6(["Monitor de eventos implantável (loop recorder implantável) para captura prolongada"])
  D4 -->|"Episódio isolado, já resolvido, sem recorrência esperada no curto prazo"| X4["Investigar causas extracardíacas e desencadeantes: dosar TSH e hemograma, revisar cafeína/álcool/estimulantes/medicações e sintomas de ansiedade"]

  X4 --> D5{"A triagem extracardíaca (TSH, hemograma, revisão de desencadeantes) identifica causa específica — por exemplo hipertireoidismo, anemia, uso de estimulante?"}
  D5 -->|"Sim"| C7(["Tratar a causa identificada e reavaliar os sintomas após a correção; retomar a investigação cardíaca se as palpitações persistirem"])
  D5 -->|"Não"| C8(["Tranquilizar o paciente, orientar diário de sintomas e reavaliação clínica programada; considerar avaliação para transtorno de ansiedade/pânico se o quadro for sugestivo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Por que a frequência do episódio decide o exame, não a gravidade percebida

A armadilha mais comum na prática é pedir Holter de 24-48h para todo paciente com palpitação, mesmo quando o episódio ocorre uma vez por mês — a chance de capturar o ritmo durante um evento tão espaçado numa janela de 1-2 dias é baixa, e um Holter negativo não exclui nada, só custa tempo e gera falsa tranquilidade. A lógica que este fluxograma segue (EHRA 2011; Zimetbaum & Josephson 1998) é a inversa: quanto mais raro o episódio, mais prolongada precisa ser a janela de monitorização — dali vem a progressão de Holter (diário) para monitor de eventos externo (semanal a mensal) e, para o episódio raro mas clinicamente relevante, o monitor de eventos implantável.

## Os dois desvios obrigatórios para fluxograma específico

Este fluxograma **não tenta diagnosticar arritmia sustentada pela descrição verbal do paciente** — ele só reconhece dois padrões clássicos o suficiente para justificar migrar para uma via já estruturada em vez de reiniciar a investigação do zero:

- **Regular, rápida, início e término súbitos** — padrão clássico de taquicardia supraventricular. Migra para o fluxograma de taquicardia de QRS estreito/largo (ESC 2019), que já cobre a estratificação e o manejo agudo.
- **Irregularmente irregular, "batimentos caóticos"** — padrão clássico de fibrilação atrial. Migra para o fluxograma de FA de início recente ou para a via AF-CARE (ESC 2024).

Quando a descrição do paciente não se encaixa claramente em nenhum dos dois — o caso mais frequente no consultório —, a árvore segue para a escolha de monitorização por frequência, que é onde este fluxograma realmente resolve o problema.

## O que este fluxograma deliberadamente não faz

- não substitui a avaliação de emergência quando a palpitação vem acompanhada de síncope franca, dor torácica aguda ou instabilidade hemodinâmica no momento do atendimento — esse cenário segue via de urgência, não este fluxo ambulatorial;
- não diagnostica o tipo de arritmia pela descrição verbal — só reconhece os dois padrões clássicos (SVT e FA) suficientes para redirecionar a um fluxograma já estruturado; qualquer padrão fora desses dois segue para monitorização, não para rótulo diagnóstico presumido;
- não define corte de duração de monitorização em horas ou dias — a faixa (diária/semanal-mensal/esporádica) orienta a categoria de exame, e a duração exata é decisão clínica caso a caso;
- não trata FA subclínica detectada por dispositivo vestível, que já tem fluxo próprio publicado em Geral (notificação de pulso irregular);
- não cobre a investigação de fadiga/intolerância ao esforço quando a palpitação não é o sintoma predominante — esse recorte já tem fluxograma próprio em Geral.

## Conexões no CorVIA

- Arritmias: fluxograma de taquicardia supraventricular de QRS estreito (ESC 2019) e de taquicardia de QRS largo (ESC 2019);
- Fibrilação atrial: fluxograma de FA de início recente no pronto-socorro e via AF-CARE (ESC 2024);
- Síncope: fluxogramas de avaliação inicial e de critérios de alto risco (ESC 2018/EUSEM 2024), para quando a palpitação vem acompanhada de perda de consciência;
- Geral: fluxograma de notificação de pulso irregular por dispositivo vestível (confirmação de FA) e fluxograma de fadiga e intolerância ao esforço.
