---
title: "Fluxograma ambulatorial: AOS no retorno cardiológico — rastreio e destino"
slug: fluxograma-ambulatorial-aos-rastreio-destino
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: pista de AOS em paciente CV → triagem STOP-Bang/história → polissonografia/sono vs plano habitual; braço de AOS conhecida → adesão CPAP vs alarme. Sem doses."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR875 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Kapur VK et al. Clinical Practice Guideline for Diagnostic Testing for Adult Obstructive Sleep Apnea. J Clin Sleep Med. 2017. DOI: 10.5664/jcsm.6506. PMID: 28162150."
  - "Yeghiazarians Y, Jneid H, Tietjens JR, et al. Obstructive Sleep Apnea and Cardiovascular Disease: A Scientific Statement From the American Heart Association. Circulation. 2021;144(3):e56-e67. DOI: 10.1161/CIR.0000000000000988. PMID: 34148375"
  - "Chung F, Yegneswaran B, Liao P, et al. STOP Questionnaire: A Tool to Screen Patients for Obstructive Sleep Apnea. Anesthesiology. 2008;108(5):812-821. DOI: 10.1097/ALN.0b013e31816d83e4. PMID: 18431116"
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
  - "McEvoy RD, Antic NA, Heeley E, et al. CPAP for Prevention of Cardiovascular Events in Obstructive Sleep Apnea. N Engl J Med. 2016;375(10):919-931. DOI: 10.1056/NEJMoa1606599. PMID: 27571048"
---

# Fluxograma ambulatorial: AOS — rastreio e destino

Prosa: [`sinalizadores-ambulatoriais-de-aos-quando-rastrear-e-encaminhar`](/biblioteca/sinalizadores-ambulatoriais-de-aos-quando-rastrear-e-encaminhar). AOS conhecida: [`checklist-ambulatorial-aos-conhecida-adesao-cpap-e-alarmes`](/biblioteca/checklist-ambulatorial-aos-conhecida-adesao-cpap-e-alarmes). Perioperatório: [`aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca`](/biblioteca/aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno cardiológico<br/>HAS / FA / IC / DAC / obesidade"] --> D0{"AOS já diagnosticada?"}

  D0 -->|"Sim"| C0(["Ir ao checklist de adesão CPAP<br/>e alarmes — doc irmão"])

  D0 -->|"Não / desconhecido"| D1{"Há pista clínica de AOS?<br/>ronco, sonolência, apneia observada,<br/>cefaleia matinal, pescoço largo<br/>OU HAS resistente / FA recorrente"}

  D1 -->|"Não"| C1(["Plano CV habitual<br/>Reavaliar contexto CV de alta suspeita<br/>Questionário não exclui sozinho"])

  D1 -->|"Sim"| P1["Triagem estruturada<br/>STOP-Bang e/ou história dirigida"]
  P1 --> D2{"Triagem de risco aumentado?<br/>STOP-Bang elevado ou história forte"}

  D2 -->|"Baixo questionário sem fenótipo de alta suspeita"| C2
  D2 -->|"HAS resistente, HP, FA recorrente ou suspeita forte"| C4(["Reavaliar se nova pista<br/>Manter plano CV"])

  D2 -->|"Sim"| D3{"Sonolência grave com risco<br/>ocupacional OU IC/HAS<br/>muito descompensada?"}

  D3 -->|"Sim"| C3(["Emergência se descompensação CV aguda<br/>Avaliação de sono após estabilizar<br/>Orientar segurança / direção"])

  D3 -->|"Não"| C4(["Serviço de sono escolhe teste<br/>PSG se doença cardiorrespiratória relevante<br/>HSAT apenas adulto não complicado<br/>Triagem ≠ diagnóstico<br/>Retorno CV curto se resistente"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C3 alerta;
  class C0,C1,C2,C4 conduta;
```

## Notas

- **D0**: bifurca diagnóstico prévio vs primeira suspeita.
- **D1**: filtro de probabilidade — alinhado a AHA 2021 e ao papel da AOS na HAS (ESC 2024).
- **D2**: STOP-Bang é **triagem** (PMID 18431116), não fecha AOS.
- **D3/C3**: prioriza segurança e descompensação; não inventa meta de eventos do SAVE.
- Não decide pressão de CPAP, tipo de máscara nem suspender GDMT.

## Integração com o hub e limites

Usar o [hub apneia do sono e coração](/doencas/apneia-do-sono-e-coracao) para a sequência diagnóstica longitudinal; este documento organiza somente destino/adesão, sem algoritmo concorrente. STOP-Bang é triagem, nunca diagnóstico nem exclusão isolada em HAS resistente, HP ou FA recorrente. AHA 2021 recomenda atenção a esses fenótipos mesmo sem ronco/sonolência. HSAT serve a adultos não complicados de alta probabilidade; PSG é preferível em doença cardiorrespiratória significativa, suspeita central/hipoventilação, neuromuscular, opioides, insônia grave ou HSAT negativo/inconclusivo com suspeita. AOS e apneia central não usam estratégias ventilatórias intercambiáveis.

SAVE não demonstrou redução significativa do composto CV primário na população/adesão estudadas; isso não nega benefícios sintomáticos de CPAP. Avaliar máscara, fuga, AHI residual, dados de uso e barreiras sem meta universal de horas/noite. Tratar AOS e HAS/FA/IC em paralelo. Sonolência ao dirigir exige segurança imediata e avaliação urgente conforme regras locais; não inventar prazo legal.
