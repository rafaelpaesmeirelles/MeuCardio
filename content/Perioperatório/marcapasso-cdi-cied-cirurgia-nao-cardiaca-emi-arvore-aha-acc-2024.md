---
title: "Marcapasso, CDI e outros CIEDs na cirurgia não cardíaca — árvore AHA/ACC 2024"
slug: marcapasso-cdi-cied-cirurgia-nao-cardiaca-emi-arvore-aha-acc-2024
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
revisado_por_voce: false
summary: "Identificação do dispositivo, dependência de pacing, risco de interferência eletromagnética, uso de magneto/reprogramação e restauração pós-operatória."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. J Am Coll Cardiol. 2024;84(19):1869-1969. DOI: 10.1016/j.jacc.2024.06.013. PMID: 39316661."
---

# CIED no perioperatório

Pacientes com marcapasso, CDI, ressincronizador, marcapasso sem eletrodo ou CDI subcutâneo precisam de um **plano do dispositivo**, não apenas de uma anotação “portador de MP/CDI”.

Antes da cirurgia, é necessário esclarecer:

- tipo de dispositivo;
- fabricante e modelo;
- indicação do implante;
- dependência de estimulação;
- resposta específica ao magneto;
- estado da bateria e funcionamento recente;
- local da cirurgia e uso previsto de fonte de interferência eletromagnética (EMI).

## Regra central AHA/ACC 2024

Em cirurgia eletiva com possibilidade de EMI, deve existir plano prévio de manejo do CIED — Classe 1, B-NR.

A EMI é particularmente relevante com eletrocautério monopolar e quando a fonte está próxima ao gerador/eletrodos. Cirurgias abaixo do umbigo geralmente apresentam risco menor de EMI para sistemas transvenosos, mas a geometria do circuito e a placa dispersiva continuam relevantes.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente com CIED candidato a cirurgia"] --> B["Identificar dispositivo, fabricante/modelo,<br/>indicação, bateria e última avaliação"]
    B --> C{"Paciente é dependente de pacing?"}
    C --> D{"Há EMI prevista?<br/>especialmente eletrocautério monopolar"}
    D -->|"Não"| E["Em geral sem mudança programada;<br/>manter monitorização apropriada"]
    D -->|"Sim"| F{"Cirurgia acima do umbigo<br/>ou EMI próxima ao dispositivo?"}
    F -->|"Não"| G["Risco menor; individualizar pela trajetória da corrente<br/>e tipo de dispositivo"]
    F -->|"Sim"| H{"Tipo de dispositivo"}
    H -->|"Marcapasso transvenoso + dependente"| I["Reprogramar para modo assíncrono<br/>OU magneto se resposta conhecida e confiável"]
    H -->|"CDI transvenoso + dependente"| J["Desabilitar terapias de taquicardia E<br/>reprogramar pacing para modo assíncrono"]
    H -->|"CDI transvenoso + não dependente"| K["Reprogramação ou magneto para inibir<br/>terapias de taquicardia/inapropriadas"]
    H -->|"Marcapasso leadless + dependente"| L["Reprogramar para modo assíncrono;<br/>não presumir resposta ao magneto"]
    H -->|"CDI subcutâneo"| M["Se EMI relevante, reprogramar ou usar magneto<br/>para desabilitar temporariamente terapias"]
    I --> N["Disponibilizar pacing/defibrilação externos<br/>e monitorização contínua"]
    J --> N
    K --> N
    L --> N
    M --> N
    E --> O["Realizar procedimento"]
    G --> O
    N --> O
    O --> P{"Dispositivo foi reprogramado ou<br/>terapias foram desabilitadas?"}
    P -->|"Não"| Q["Cuidados pós-operatórios usuais do CIED"]
    P -->|"Sim"| R["Restaurar programação/terapias no pós-operatório<br/>antes de alta para ambiente não monitorizado"]
```

## Pontos críticos por dispositivo

### Marcapasso transvenoso

Em paciente **dependente de pacing** submetido a cirurgia **acima do umbigo** com EMI prevista, a AHA/ACC recomenda reprogramação ou magneto capaz de produzir modo assíncrono para evitar inibição de pacing.

Mas o magneto só é seguro se a resposta daquele dispositivo for conhecida. Respostas variam por fabricante, modelo, programação e bateria.

### CDI transvenoso

A EMI pode ser interpretada como taquiarritmia e disparar terapias inadequadas.

- se o paciente é dependente de pacing: desabilitar terapias de taquicardia **e** garantir pacing assíncrono;
- se não é dependente: reprogramação ou magneto podem ser usados para impedir terapias inadequadas.

**Magneto sobre CDI não transforma automaticamente o pacing em modo assíncrono.**

### Marcapasso leadless

A resposta ao magneto é dependente do fabricante/modelo e pode não existir. Em paciente dependente submetido a cirurgia acima do umbigo com EMI, a diretriz recomenda reprogramação para modo assíncrono.

### CDI subcutâneo

Para cirurgia com EMI relevante acima da virilha, reprogramação ou magneto para suspensão temporária das terapias é razoável.

## Durante a cirurgia

Quando terapias de CDI estiverem desativadas ou pacing tiver sido alterado:

- monitorização cardíaca contínua;
- disponibilidade imediata de desfibrilação externa;
- considerar pads de pacing/desfibrilação já posicionados quando apropriado;
- usar eletrocautério bipolar/ultrassônico quando possível;
- com monopolar, usar menor energia eficaz e rajadas curtas/intermitentes;
- posicionar placa dispersiva de forma que a corrente não atravesse o gerador/eletrodos.

## Passo pós-operatório que não pode ser esquecido

Pacientes cujo CDI teve terapias desativadas ou cujo marcapasso/CDI foi reprogramado precisam ter a função **restaurada antes da alta para ambiente sem monitorização**.

A falha de reativar terapias de CDI após cirurgia já foi associada a mortes evitáveis.

## Regra prática

**O magneto não é uma solução universal.** O plano seguro depende de três perguntas: o paciente depende de pacing? haverá EMI relevante? o que exatamente esse dispositivo faz quando recebe um magneto? A quarta pergunta é obrigatória depois: **quem vai restaurar a programação antes da alta?**
