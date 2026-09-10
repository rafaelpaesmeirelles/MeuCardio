---
slug: fluxograma-suspeita-miocardite-por-inibidor-de-checkpoint-ambulatorial
title: 'Fluxograma: suspeita ambulatorial de miocardite por inibidor de checkpoint'
kind: fluxograma
theme: Cardio-oncologia
summary: Miocardite por inibidor de checkpoint pode se apresentar com dor torácica, dispneia, fadiga, palpitações
  ou alterações de biomarcadores. O fluxograma direciona a suspeita clínica para avaliação hospitalar monitorizada
  e identifica sobreposição com miosite e miastenia.
tags: []
source_refs:
- 'Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology developed in collaboration
  with the European Hematology Association (EHA), the European Society for Therapeutic Radiology and Oncology (ESTRO)
  and the International Cardio-Oncology Society (IC-OS) · European Heart Journal · 2022 · 43(41):4229-4361 · DOI:
  10.1093/eurheartj/ehac244 · PMID: 36017568'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma: suspeita ambulatorial de miocardite por inibidor de checkpoint

Miocardite por inibidor de checkpoint imunológico (ICI) é incomum, mas a mortalidade relatada é alta quando grave. No ambulatório o erro clássico é atribuir cansaço ao câncer ou à anemia e mandar o paciente 'voltar na próximo ciclo'. Este fluxograma cobre a **porta ambulatorial**; o manejo de emergência/UTI está em documento separado desta biblioteca.

A ESC 2022 reconhece critérios diagnósticos próprios para miocardite por ICI (maiores/menores e via histopatológica). Aqui a ênfase é **triagem e escalonamento**, não substituir o algoritmo diagnóstico completo.

## Red flags ambulatoriais sob ICI (ou semanas após a última dose)

- dor torácica, dispneia, ortopneia, síncope, palpitações;
- fadiga abrupta desproporcional;
- sinais de IC nova;
- mialgia intensa, fraqueza proximal, ptose, diplopia, disfagia, alteração vocal ou dispneia neuromuscular — pensar overlap **miocardite–miosite–miastenia**;
- elevação inexplicada de CK, AST/ALT ou LDH em exames de rotina oncológica (podem ser a primeira pista).

## Fluxograma ambulatorial

```mermaid
flowchart TD
  A["Paciente em ICI ou recente<br/>com sintoma/exame suspeito"] --> B{"Instabilidade?<br/>hipotensão, hipoxemia,<br/>síncope, dor isquêmica,<br/>edema agudo, BAV,<br/>arritmia grave"}

  B -->|Sim| ER["Encaminhar PS/UTI agora<br/>Suspender ICI<br/>Seguir fluxograma de<br/>emergência de miocardite por ICI"]

  B -->|Não| C["Interromper temporariamente do ICI; avaliação hospitalar monitorizada no mesmo dia:<br/>ECG + troponina hs + BNP/NT-proBNP<br/>+ CK ± enzimas<br/>Avaliar força muscular / sintomas miastênicos"]

  C --> D{"ECG anormal OU<br/>troponina elevada OU<br/>sinais de IC OU<br/>suspeita de overlap
miosite/miastenia"}

  D -->|Sim| E["Suspender ICI<br/>Eco urgente<br/>Contatar cardio-oncologia<br/>Internar com telemetria<br/>Troponina seriada, eco e cardio-oncologia"]

  D -->|Não — ECG normal,<br/>troponina negativa,<br/>sem sinais de IC| F{"Sintoma residual<br/>ou enzimas musculares<br/>ainda inexplicadas?"}

  F -->|Sim| G["Repetir troponina/ECG em curto intervalo<br/>Eco preferencial<br/>Não liberar próximo ciclo de ICI<br/>sem reavaliação especializada"]

  F -->|Não — quadro banal<br/>e workup negativo| H["Registrar baseline<br/>Educar red flags<br/>Retorno oncológico só após avaliação clínica excluir suspeita<br/>com aviso explícito à equipe"]

  E --> I{"Há fraqueza, ptose, diplopia,<br/>disfagia, alteração vocal, dispneia neuromuscular<br/>ou CK elevada com suspeita de sobreposição?"}
  I -->|Sim| J["Ativar overlap miocardite-miosite-miastenia<br/>Evitar fármacos que agravem bloqueio neuromuscular<br/>Unidade com capacidade de UTI<br/>Avaliação neurológica e respiratória urgente/seriada"]
  I -->|Não| K["Seguir investigação de miocardite<br/>e decisão de imunossupressão<br/>com equipe especializada"]

  classDef urgente fill:#fdecea,stroke:#a33,color:#400;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class ER,J urgente;
  class E,G,H,K conduta;
```

## Condutas-chave (ambulatorial)

1. **Não aplicar o próximo ciclo de ICI** até esclarecer suspeita razoável.
2. **Troponina negativa uma vez não encerra** se o sintoma persiste — repita e faça eco.
3. **Overlap** muda o risco: trate como emergência neurológico-cardíaca até prova em contrário.
4. Imunossupressão (corticoide e escalonamentos) é decisão especializada após estratificar gravidade — este fluxograma não protocola doses.
5. Rechallenge de ICI após miocardite é exceção documentada em frameworks específicos; não decidir no corredor do ambulatório.

## Relação com outros documentos desta pasta

- Fluxograma / texto de **miocardite por ICI em emergência**;
- Overlap miocardite–miosite–miastenia;
- Biomarcadores não cardíacos de rotina (CK, AST, ALT, LDH) na vigilância;
- Estratificação HFA-ICOS e miocardite por checkpoint.

## Mensagem de bolso

No ambulatório sob ICI: **sintoma cardiovascular ou enzima muscular nova → ECG + troponina no mesmo dia; se positivo ou dúvida, suspender ICI e acionar cardio-oncologia**. Estabilidade hemodinâmica não autoriza 'esperar o próximo retorno'.

## Interpretação e segurança

CK, AST/ALT e LDH isoladas são inespecíficas; não diagnosticam miocardite. Troponina T pode aumentar em miosite, e troponina I pode ajudar a distinguir lesão cardíaca, integrada a sintomas, ECG e imagem. Troponina negativa única ou RMC normal precoce não excluem miocardite por ICI. Considerar biópsia endomiocárdica se diagnóstico incerto ou gravidade exige, por equipe especializada. Suspeita razoável exige interrupção imediata do ICI e avaliação hospitalar monitorizada; instabilidade exige emergência imediata. Avaliar sobreposição miastênica e risco ventilatório urgentemente; não manter overlap em seguimento ambulatorial. Decisão definitiva sobre suspensão/rechallenge é multidisciplinar.

## Conteúdo CorVIA conectado

- [Miocardite por inibidor de checkpoint imune: emergência ESC 2025](/biblioteca/miocardite-por-inibidor-de-checkpoint-imune-emergencia-esc-2025)
- [Sobreposição de miocardite, miosite e miastenia por ICI](/biblioteca/overlap-miocardite-miosite-miastenia-por-ici)
- [Biomarcadores musculares na vigilância por checkpoint](/biblioteca/biomarcadores-nao-cardiacos-de-rotina-ck-ast-alt-ldh-na-vigilancia-da-miocardite-por-checkpoint)
Quando miocardite por ICI é considerada provável, a equipe deve iniciar tratamento prontamente conforme protocolo especializado; não aguardar confirmação tardia por RMC ou biópsia para tratar uma apresentação grave.
