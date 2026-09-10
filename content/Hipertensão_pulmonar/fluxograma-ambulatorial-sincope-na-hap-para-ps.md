---
slug: fluxograma-ambulatorial-sincope-na-hap-para-ps
title: 'Fluxograma ambulatorial: síncope na HAP — quando ir ao PS'
kind: fluxograma
theme: Hipertensão pulmonar
summary: 'Destino da síncope ou pré-síncope em HAP/HP pré-capilar: sinais de alarme exigem urgência; avaliação de
  provável evento reflexo estável depende do centro de HP e de plano seguro.'
tags: []
source_refs:
- 'Humbert M, Kovacs G, Hoeper MM, et al; ESC/ERS Scientific Document Group. 2022 ESC/ERS Guidelines for the diagnosis
  and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID:
  36017548'
- https://www.ishlt.org/docs/default-source/standards-guidelines/2022_endorsement_esc_ers_phguidelines.pdf?sfvrsn=a6cbfe7_1
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: síncope na HAP — quando ir ao PS

Prosa de falência direita: [`sinalizadores-ambulatoriais-falencia-de-vd-na-hp`](/biblioteca/sinalizadores-ambulatoriais-falencia-de-vd-na-hp). Suspeita de CTEPH: [`sinalizadores-ambulatoriais-suspeita-de-cteph-quando-referenciar`](/biblioteca/sinalizadores-ambulatoriais-suspeita-de-cteph-quando-referenciar).

Na estratificação ESC/ERS 2022, síncope ocasional integra a categoria intermediária e síncope repetida a de alto risco no modelo de três estratos; frequência, contexto e outras variáveis devem ser integrados. No consultório, avaliar prontamente a causa e os sinais atuais, sem igualar pré-síncope a categoria prognóstica formal.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno / demanda: paciente com HAP ou HP pré-capilar<br/>relata síncope ou pré-síncope"] --> D0{"Episódio relacionado a esforço<br/>durante atividade física, além de apenas ficar em pé?"}

  D0 -->|"Sim — esforço físico"| C0(["PS / urgência AGORA<br/>Contatar centro de HP<br/>Não liberar para retorno eletivo"])

  D0 -->|"Não claro / em repouso"| D1{"Há sinais de falência de VD,<br/>hipotensão, hemoptise, confusão<br/>ou trauma craniano?"}

  D1 -->|"Sim"| C0

  D1 -->|"Não"| PI["Avaliação inicial: história, medicações,<br/>exame, PA ortostática e ECG 12 derivações"]
  PI --> DR{"Novo achado de risco ou exame indisponível?"}
  DR -->|"Sim"| C0
  DR -->|"Não"| D2{"História tipicamente reflexa<br/>(prolongado em pé, calor, náusea prodômica)<br/>SEM esforço e SEM HP descompensada?"}

  D2 -->|"Não ou dúvida"| C1(["Investigar causa potencialmente grave<br/>PS ou observação com suporte<br/>+ contato com centro de HP"])

  D2 -->|"Muito típico reflexo E estável"| C2(["Exceção estreita: observação breve<br/>Reavaliação definida com o centro<br/>Orientação escrita: novo episódio → PS<br/>Avisar centro de HP no mesmo dia"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef neutro fill:#eef2f7,stroke:#3d5a80,color:#102a43;
  class C0,C1 alerta;
  class C2 neutro;
```

## Notas

- **D0**: síncope de esforço na HAP é sinal de alarme para possível baixo débito; não equivale isoladamente à categoria prognóstica formal de alto risco — destino padrão é **PS**, não "marcar eco na semana que vem".
- **D1**: acopla ao checklist de falência de VD; qualquer sinal de descompensação fecha a porta da observação eletiva.
- **D2/C2**: exceção **estreita** para quadro tipicamente reflexo sem esforço; ainda assim exige contato com o centro e plano escrito de retorno ao PS. Na dúvida, escolher C0/C1.
- Este fluxograma **não** diferencia causas neurológicas/arrítmicas detalhadas — no paciente com HAP, a prioridade ambulatorial é **não subestimar** o significado prognóstico da síncope.
- Doses, titulação e dispositivos seguem avaliação especializada.

## Segurança adicional

Pós-TEP, sintomas novos/persistentes devem ser avaliados, especialmente na revisão de 3–6 meses. Não esperar três meses diante de deterioração. V/Q com mismatch persistente após tratamento adequado requer centro CTEPH; angio-TC normal isolada não exclui doença crônica. Operabilidade e combinação de EAP/BPA/fármacos dependem do centro, sem inferir causalidade a partir de comparação observacional entre operados e não operados.

Interrupção de infusão contínua IV/SC de prostaciclina por bomba/linha requer contato imediato com centro de HP e emergência para restauração segura, mesmo antes de sintomas. Não aplicar esse risco indistintamente a toda dose oral perdida. Edema, função renal/hepática, sódio, BNP e VD devem ser interpretados em tendência; não ajustar terapia específica às cegas.
