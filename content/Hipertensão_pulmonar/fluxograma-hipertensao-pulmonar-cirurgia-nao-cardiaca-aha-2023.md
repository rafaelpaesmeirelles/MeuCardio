---
title: "Fluxograma: hipertensão pulmonar na cirurgia não cardíaca — proteger o ventrículo direito (AHA 2023)"
slug: fluxograma-hipertensao-pulmonar-cirurgia-nao-cardiaca-aha-2023
theme: "Hipertensão pulmonar"
kind: fluxograma
summary: "Trajeto perioperatório específico da hipertensão pulmonar: classificar o grupo e a urgência, avaliar reserva do ventrículo direito, otimizar antes da cirurgia eletiva e definir monitorização intra e pós-operatória pelo risco."
review_status: revisado
review_note: "Fluxograma auditado em 26/08/2026 contra o Scientific Statement AHA no PubMed/periódico (PMID 36924225; DOI 10.1161/CIR.0000000000001136) e a página oficial Top Things to Know. A árvore organiza o processo em cinco etapas proposto pela fonte, que reconhece escassez de evidência e não apresenta um algoritmo validado. Não foram criadas classes de recomendação, doses, obrigação universal de ecocardiograma ou destino universal em UTI. Cinco vínculos internos conferidos contra slugs existentes."
source_refs: ["Rajagopal S, Ruetzler K, Ghadimi K, et al. Evaluation and Management of Pulmonary Hypertension in Noncardiac Surgery: A Scientific Statement From the American Heart Association. Circulation. 2023;147(17):1317-1343. DOI: 10.1161/CIR.0000000000001136. PMID: 36924225. https://www.ahajournals.org/doi/10.1161/CIR.0000000000001136", "American Heart Association. Top Things to Know: Evaluation and Management of Pulmonary HTN in Non-Cardiac Surgery. 16/03/2023. https://professional.heart.org/en/science-news/evaluation-and-management-of-pulmonary-hypertension-in-non-cardiac-surgery/top-things-to-know"]
---

# Fluxograma: hipertensão pulmonar na cirurgia não cardíaca (AHA 2023)

O algoritmo perioperatório geral não basta para o paciente com hipertensão pulmonar (HP): o risco depende do **grupo fisiopatológico, da reserva do ventrículo direito (VD), da urgência e do estresse hemodinâmico do procedimento**. O Scientific Statement AHA propõe cinco etapas — classificar, estratificar, otimizar, proteger no intraoperatório e acompanhar a recuperação — e reconhece que a base de evidência é limitada.

## Da indicação cirúrgica ao plano

```mermaid
flowchart TD
  A["Paciente com HP conhecida ou fortemente suspeita<br/>e indicação de cirurgia não cardíaca"] --> B["Definir o grupo de HP e a causa de base<br/>+ caracterizar porte e urgência da cirurgia"]
  B --> C{"Cirurgia é emergência/urgência<br/>sem tempo seguro para otimização?"}

  C -->|Sim| D["Acionar equipe de HP, anestesia e cirurgia<br/>Foco imediato: estabilidade do VD,<br/>débito cardíaco e perfusão de órgãos"]
  C -->|Não, eletiva| E["Avaliação integrada: sintomas e classe funcional,<br/>capacidade de exercício, sinais de falência de VD,<br/>biomarcadores e imagem/hemodinâmica já disponíveis"]

  E --> F{"HP descompensada, falência de VD,<br/>terapia de base não otimizada ou<br/>plano perioperatório inadequado?"}
  F -->|Sim| G(["Adiar quando clinicamente possível<br/>Otimizar em conjunto com especialista em HP<br/>e reconsiderar porte/local da cirurgia"])
  F -->|Não| H["Decisão compartilhada sobre risco-benefício<br/>+ plano de anestesia, monitorização,<br/>medicações e destino pós-operatório"]

  G --> I{"Após otimização, risco e benefício<br/>permitem prosseguir?"}
  I -->|Não| J(["Reconsiderar indicação, via menos invasiva<br/>ou alternativa não cirúrgica"])
  I -->|Sim| H
  D --> K["Prosseguir com plano intraoperatório<br/>adaptado à gravidade e à urgência"]
  H --> K

  classDef action fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class G,J action;
```

Não há exame único que autorize ou contraindique a cirurgia. Ecocardiograma atualizado, cateterismo direito ou teste funcional são escolhidos conforme mudança clínica, grupo de HP, informação disponível e se o resultado pode modificar a decisão — não repetidos automaticamente em todos.

## Durante e depois da cirurgia

```mermaid
flowchart TD
  A["Plano perioperatório definido"] --> B["Manter terapia específica de HAP sem interrupção<br/>quando aplicável; garantir continuidade segura<br/>de infusões parenterais"]
  B --> C["Metas intraoperatórias:<br/>evitar hipotensão sistêmica;<br/>manter ritmo e condições de carga do VD;<br/>evitar aumento agudo da RVP"]
  C --> D["Prevenir/corrigir hipóxia, hipercapnia,<br/>acidose, hipotermia, dor e pressões<br/>excessivas de ventilação"]
  D --> E["Escolher técnica anestésica e monitorização<br/>pelo risco do paciente e do procedimento"]
  E --> F{"Recuperação estável, sem falência de VD,<br/>hipoxemia ou instabilidade hemodinâmica?"}
  F -->|Sim| G(["Recuperação pós-anestésica com vigilância<br/>e destino definidos pelo risco residual"])
  F -->|Não ou alto risco| H(["Cuidado crítico e tratamento imediato<br/>da causa de aumento da RVP ou falência de VD"])

  classDef action fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class G,H action;
```

RVP significa resistência vascular pulmonar. “Manter condições de carga” não quer dizer administrar volume indiscriminadamente: tanto hipovolemia quanto sobrecarga podem comprometer o VD, e a conduta deve seguir a fisiologia observada.

## Conteúdo CorVIA conectado

- [Statement AHA: risco perioperatório e estratificação](/biblioteca/hipertensao-pulmonar-e-cirurgia-nao-cardiaca-risco-perioperatorio-e-estratificacao)
- [Diretriz ESC/ERS 2022 de hipertensão pulmonar](/biblioteca/hipertensao-pulmonar-diagnostico-e-tratamento-escers-2022)
- [Fluxograma diagnóstico de hipertensão pulmonar](/biblioteca/fluxograma-hipertensao-pulmonar-diagnostico-esc-ers-2022)
- [Modificadores de risco perioperatório AHA/ACC 2024](/biblioteca/condicoes-cardiacas-agudas-e-modificadores-de-risco-aha-acc-2024-arvore)
- [Fluxograma de falência aguda do ventrículo direito](/biblioteca/fluxograma-falencia-aguda-de-ventriculo-direito)

## Limites e armadilhas

- O statement é orientação de consenso, não ensaio randomizado nem algoritmo validado.
- RCRI aparentemente baixo não neutraliza HP grave ou disfunção de VD.
- Pressão pulmonar isolada não resume a reserva do VD nem o risco do procedimento.
- Cirurgia eletiva permite otimização; na emergência, o objetivo muda para preservar VD, débito e perfusão enquanto se trata a causa.
- O destino pós-operatório é individualizado: nem todo paciente precisa de UTI, e paciente de alto risco não deve ser enviado automaticamente a uma área de baixa vigilância.
