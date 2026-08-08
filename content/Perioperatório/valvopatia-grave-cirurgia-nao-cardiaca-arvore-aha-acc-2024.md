---
title: "Valvopatia moderada/grave e cirurgia não cardíaca — árvore AHA/ACC 2024"
slug: valvopatia-grave-cirurgia-nao-cardiaca-arvore-aha-acc-2024
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
revisado_por_voce: false
summary: "Árvore para estenose aórtica, estenose mitral e regurgitações aórtica/mitral no planejamento de cirurgia não cardíaca."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. J Am Coll Cardiol. 2024;84(19):1869-1969. DOI: 10.1016/j.jacc.2024.06.013. PMID: 39316661."
  - "Otto CM, Nishimura RA, Bonow RO, et al. 2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease. J Am Coll Cardiol. 2021;77:e25-e197. DOI: 10.1016/j.jacc.2020.11.018."
---

# Valvopatia e cirurgia não cardíaca

A presença de valvopatia importante não é adequadamente resumida por RCRI ou Gupta MICA. O risco depende de **tipo da lesão, gravidade, sintomas, resposta ventricular, pressão pulmonar e risco hemodinâmico do procedimento**.

A primeira regra é simples: se há suspeita de lesão moderada ou grave e a informação ecocardiográfica é necessária para orientar o procedimento, **defina a anatomia e a hemodinâmica antes da cirurgia eletiva**.

## Árvore geral

```mermaid
flowchart TD
    A["Paciente candidato a cirurgia não cardíaca<br/>com sopro, valvopatia conhecida ou suspeita"] --> B{"Há suspeita de valvopatia<br/>moderada ou grave?"}
    B -->|"Não"| C["Seguir algoritmo perioperatório geral"]
    B -->|"Sim"| D["História + exame + ECG + ecocardiograma<br/>quando indicado para definir gravidade e repercussão"]
    D --> E{"Lesão predominante"}
    E -->|"Estenose aórtica"| F{"EAo grave?"}
    F -->|"Não"| C
    F -->|"Sim"| G{"Sintomas / disfunção VE / indicação padrão de intervenção?"}
    G -->|"Sim"| H["Avaliar intervenção valvar antes de cirurgia eletiva;<br/>Heart Valve Team"]
    G -->|"Não"| I{"Cirurgia não cardíaca é de baixo risco?"}
    I -->|"Sim + FEVE normal"| J["É razoável prosseguir com monitorização apropriada"]
    I -->|"Não / risco elevado"| K["Avaliação multidisciplinar;<br/>definir necessidade de intervenção e monitorização avançada"]

    E -->|"Estenose mitral"| L{"EM grave?"}
    L -->|"Não"| C
    L -->|"Sim"| M["Avaliar indicação de intervenção mitral antes de cirurgia eletiva"]
    M --> N{"Intervenção não pode ser feita antes<br/>e cirurgia precisa prosseguir?"}
    N -->|"Sim"| O["Monitorização hemodinâmica invasiva é razoável;<br/>considerar controle de FC"]
    N -->|"Não"| P["Tratar valva conforme indicação e depois redefinir timing"]

    E -->|"IM ou IA crônica"| Q{"Moderada/grave?"}
    Q -->|"Não"| C
    Q -->|"Sim"| R{"Há sintomas, disfunção ventricular<br/>ou indicação padrão de intervenção?"}
    R -->|"Sim"| S["Considerar intervenção valvar antes de cirurgia eletiva de risco elevado"]
    R -->|"Não"| T{"IM: função VE normal + PSAP <50?<br/>IA: FEVE >55%?"}
    T -->|"Sim"| U["É razoável prosseguir com cirurgia eletiva<br/>com plano hemodinâmico apropriado"]
    T -->|"Não"| V["Reavaliar risco e estratégia com Heart Valve Team"]
```

# Estenose aórtica

A AHA/ACC 2024 recomenda que pacientes com **EAo grave** sejam avaliados quanto à necessidade de intervenção aórtica antes de cirurgia não cardíaca eletiva.

A diretriz utiliza como critérios ecocardiográficos de EAo grave:

- área valvar aórtica **<1,0 cm²**; ou
- gradiente médio **≥40 mmHg**; ou
- velocidade máxima transvalvar **Vmax ≥4,0 m/s**.

Em paciente com suspeita de EAo moderada ou grave que fará cirurgia não cardíaca de risco elevado, ecocardiograma pré-operatório é recomendado para guiar manejo.

Paciente assintomático com EAo moderada/grave, função sistólica de VE normal e ecocardiograma recente pode realizar cirurgia eletiva de **baixo risco** de forma razoável, com monitorização adequada.

## Por que EAo sintomática muda tanto o risco

Na estenose fixa importante, hipotensão, taquicardia, perda de pré-carga ou grandes variações de volume podem reduzir abruptamente débito cardíaco e perfusão coronária.

O planejamento deve minimizar:

- hipotensão;
- taquicardia;
- hipertensão excessiva;
- desidratação;
- sobrecarga volêmica.

# Estenose mitral

Pacientes com **EM grave** devem ser avaliados quanto à necessidade de intervenção mitral antes de cirurgia eletiva.

Quando a intervenção não pode ser realizada e a cirurgia precisa prosseguir:

- monitorização hemodinâmica invasiva é razoável — Classe 2a;
- controle perioperatório de frequência cardíaca pode ser considerado — Classe 2b — para prolongar tempo diastólico e limitar elevação de pressão atrial/pulmonar.

A fisiologia exige atenção particular a:

- taquicardia;
- fibrilação atrial;
- hipoxemia/hipercapnia que aumentem pressão pulmonar;
- excesso de volume e edema pulmonar.

# Insuficiência mitral e insuficiência aórtica

Em suspeita de regurgitação valvar moderada ou grave, ecocardiograma pré-operatório é recomendado antes de cirurgia eletiva para definir severidade e repercussão.

Se o paciente já cumpre indicação padrão de intervenção valvar, a necessidade de tratar a valva deve ser considerada antes de cirurgia não cardíaca de risco elevado.

A AHA/ACC 2024 considera razoável prosseguir com cirurgia eletiva em:

- **IM moderada/grave assintomática**, função sistólica de VE normal e **PSAP <50 mmHg**;
- **IA moderada/grave assintomática** e função sistólica de VE normal, definida na recomendação como **FEVE >55%**.

## Diferenças hemodinâmicas importam

Lesões regurgitantes geralmente toleram melhor redução moderada de pós-carga que lesões estenóticas, mas isso não elimina risco.

- Na IM, evitar aumento excessivo de pós-carga e bradicardia importante; manter pré-carga adequada.
- Na IA importante, bradicardia prolonga diástole e pode aumentar volume regurgitante; volume e pressão precisam ser cuidadosamente manejados.

## Regra prática

**“Valvopatia grave” não é um diagnóstico único.** A árvore precisa separar estenose de regurgitação, sintomas de assintomáticos e baixo risco de cirurgia de procedimentos com grandes variações hemodinâmicas. O ecocardiograma serve para planejar manejo — não para criar atraso automático sem pergunta clínica definida.
