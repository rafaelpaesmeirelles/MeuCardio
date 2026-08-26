---
title: "Afogamento — manejo da parada cardiorrespiratória"
slug: fluxograma-afogamento-manejo-da-parada-cardiorrespiratoria
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão do afogamento: separa a vítima consciente/respirando (prevenção da parada pelo ABCDE, com oxigênio titulado e escalonamento ventilatório) da vítima inconsciente sem respiração normal, em que a reanimação abre por 5 ventilações — não por compressão — antes de seguir para 30:2, DEA e, se malsucedida, RCP extracorpórea."
review_status: revisado
review_note: "Atualizado em 26/08/2026 contra ERC/RCUK 2025. Mantidas as cinco ventilações iniciais com oxigênio a 100% quando disponível, o prosseguimento com RCP padrão e a consideração de ECPR conforme protocolo local; acrescentada a limitação de pressão na bolsa-válvula-máscara para reduzir insuflação gástrica. Os alvos do ramo sem parada permanecem atribuídos à fonte ERC 2021."
source_refs: ["Lott C, Karageorgos V, Abelairas-Gomez C, et al. European Resuscitation Council Guidelines 2025 Special Circumstances in Resuscitation. Resuscitation. 2025;215 Suppl 1:110753. DOI: 10.1016/j.resuscitation.2025.110753. PMID: 41117569.", "Resuscitation Council UK. Special circumstances guidelines 2025 — seção Drowning, texto oficial conferido em 26/08/2026. https://www.resus.org.uk/library/2025-resuscitation-guidelines/special-circumstances-guidelines", "Lott C, Truhlář A, Alfonzo A, et al. European Resuscitation Council Guidelines 2021: Cardiac arrest in special circumstances. Resuscitation. 2021;161:152-219. DOI: 10.1016/j.resuscitation.2021.02.011. PMID: 33773826 — mantida para oxigenação e suporte ventilatório no paciente com circulação."]
---

# Afogamento — manejo da parada cardiorrespiratória

Gatilho para este protocolo: **vítima recuperada de submersão em água**. O
eixo que separa as condutas é o estado de consciência e respiração no
resgate — e, para quem já precisa de reanimação, a sequência começa por
**ventilação**, não por compressão, porque a causa da deterioração é
hipóxia.

## Árvore de decisão

```mermaid
flowchart TD
  R["Vítima recuperada de submersão em água —<br/>avaliação dinâmica de risco (duração da submersão<br/>é o preditor mais forte de desfecho)"]
  R --> D1

  D1{"Consciente e/ou respirando normalmente?"}
  D1 -->|"Sim"| C1
  D1 -->|"Não — inconsciente, sem respiração normal"| M1

  C1(["Prevenir a PCR pelo ABCDE: via aérea desobstruída;<br/>O2 100% até SpO2 confiável, depois titular para SpO2 94-98%<br/>(PaO2 75-100 mmHg); considerar VNI (desconforto respiratório,<br/>via aérea segura) ou ventilação invasiva (insegura/falha da VNI);<br/>considerar ECMO se má resposta à ventilação invasiva;<br/>monitorizar FC/PA/ECG, acesso IV, fluido/vasoativo se necessário"])

  M1["Iniciar a reanimação com 5 VENTILAÇÕES DE RESGATE iniciais,<br/>com oxigênio a 100% inspirado se disponível — não iniciar<br/>por compressão, a causa é hipóxia"]
  M1 --> D2

  D2{"Permanece inconsciente e sem respiração<br/>normal após as 5 ventilações iniciais?"}
  D2 -->|"Sim"| M2
  D2 -->|"Não — retomou respiração normal"| C2

  C2(["Reclassificar como vítima sem PCR: seguir a prevenção da<br/>parada pelo ABCDE — via aérea, oxigênio titulado (SpO2 94-98%),<br/>monitorização de FC/PA/ECG"])

  M2["Iniciar compressões torácicas: ciclos de 30 compressões<br/>para 2 ventilações; na bolsa-válvula-máscara, limitar pressão<br/>para reduzir insuflação gástrica; aplicar DEA assim que disponível;<br/>considerar via aérea avançada se puder ser obtida com segurança"]
  M2 --> D3

  D3{"Esforços iniciais de reanimação malsucedidos?"}
  D3 -->|"Sim, malsucedidos"| C3
  D3 -->|"Não — retorno da circulação espontânea"| C4

  C3(["Considerar RCP extracorpórea (ECPR), conforme<br/>protocolos e critérios de elegibilidade locais"])
  C4(["Cuidados pós-parada: pacote padrão pós-PCR<br/>(oxigenação/ventilação-alvo, hemodinâmica, controle de<br/>temperatura), com atenção à lesão pulmonar por aspiração"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## O que vale para todos os ramos, e por isso não está no diagrama

**A duração da submersão é o preditor mais forte de desfecho** (certeza
moderada) — deve orientar a alocação de recursos de busca e resgate.
**Salinidade da água tem efeito inconsistente**, e a revisão do ILCOR
recomenda **contra** usar idade, tempo de resposta do SAMU, tipo/temperatura
da água ou status de testemunha para decidir prognóstico (evidência de
certeza muito baixa).

**A base de evidência para o manejo da PCR no afogamento é consenso de
especialistas**, informado por revisão de escopo do ILCOR — não há ensaio
clínico controlado randomizado dedicado ao tema. Isso não reduz a força da
recomendação de iniciar a reanimação assim que for seguro e viável, que o
grupo redator apoia fortemente dado o peso prognóstico da duração da
submersão e da PCR.
