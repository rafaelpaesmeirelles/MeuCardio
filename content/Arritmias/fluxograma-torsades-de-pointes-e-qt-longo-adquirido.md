---
title: "Fluxograma: Torsades de Pointes e QT Longo Adquirido — Conduta Imediata"
slug: fluxograma-torsades-de-pointes-e-qt-longo-adquirido
theme: "Arritmias"
kind: fluxograma
summary: "Árvore de decisão atualizada para TV polimórfica sustentada e torsades de pointes: choque não sincronizado imediato quando a arritmia está sustentada, distinção entre QT longo e QT normal e prevenção de recorrência orientada pelo mecanismo."
review_status: revisado
source_refs: ["Wigginton JG, Agarwal S, Bartos JA, et al. Part 9: Adult Advanced Life Support: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16 Suppl 2):S538-S577. DOI: 10.1161/CIR.0000000000001376. PMID: 41122884 — TV polimórfica sustentada: choque não sincronizado imediato (COR 1, LOE B-NR); magnésio pode ser considerado na recorrência associada a QT longo/TdP (COR 2b, LOE C-LD); sem benefício do magnésio rotineiro na TV polimórfica com QT normal (COR 3, LOE C-LD).", "Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126. DOI: 10.1093/eurheartj/ehac262. PMID: 36017572 — retirada de fármaco causal, correção de eletrólitos, magnésio IV na TdP e aumento da frequência com pacing/isoproterenol em recorrência no QT longo adquirido.", "Tisdale JE, Jaynes HA, Kingery JR, et al. Circ Cardiovasc Qual Outcomes. 2013;6(4):479-487. DOI: 10.1161/CIRCOUTCOMES.113.000152. PMID: 23716032 — escore de risco de prolongamento de QTc em pacientes hospitalizados, não escore de tratamento da TdP; ≥2 fármacos pró-QT somam 6 pontos no total (3 do primeiro + 3 adicionais)."]
legacy_source: "Atualização de segurança e revisão documental independente concluídas em 24/08/2026. A versão anterior encaminhava TV polimórfica com pulso e instabilidade para cardioversão sincronizada e não deixava claro que ≥2 fármacos pró-QT somam 6 pontos no total no Tisdale. O texto foi alinhado à AHA 2025, à ESC 2022 e ao estudo original do Tisdale; parâmetros operacionais continuam sujeitos ao protocolo institucional."
---

# Fluxograma: Torsades de Pointes e QT Longo Adquirido — Conduta Imediata

> **STATUS DE CURADORIA:** `revisado`. Revisão documental independente concluída. Doses, energia e metas eletrolíticas exigem validação no protocolo institucional antes de serem convertidas em ordens clínicas.

A decisão inicial é mais simples e mais segura do que na versão anterior: **TV polimórfica sustentada é arritmia eletricamente instável e requer choque não sincronizado imediato**. A presença de pulso não transforma a terapia elétrica em cardioversão sincronizada. Depois de interromper a arritmia, o QT basal e o contexto etiológico orientam a prevenção de recorrência.

## Árvore de decisão

```mermaid
flowchart TD
  R1{"TV polimórfica sustentada<br/>em curso?"}
  C_shock(["Choque NÃO sincronizado imediato<br/>— alta energia conforme fabricante/protocolo.<br/>AHA 2025: Classe 1, B-NR.<br/>Não atrasar para sincronização, magnésio ou laboratório."])
  D_qt{"Após terminar o episódio:<br/>QT basal conhecido/suspeito prolongado?"}
  C_tdp(["Provável TdP / QT longo:<br/>retirar gatilho pró-QT;<br/>corrigir K/Mg/Ca;<br/>magnésio IV pode ser considerado<br/>para prevenir/suprimir recorrências<br/>(AHA 2025: 2b, C-LD)."])
  C_nonqt(["TV polimórfica sem QT longo:<br/>buscar/tratar isquemia e outras causas;<br/>lidocaína ou amiodarona podem ser consideradas<br/>para recorrências conforme contexto.<br/>Magnésio rotineiro: NÃO recomendado<br/>(AHA 2025: Classe 3, C-LD)."])
  D_recur{"TdP recorrente e<br/>bradicardia/pausa-dependente?"}
  C_rate(["Consulta especializada:<br/>overdrive pacing ou isoproterenol<br/>podem ser usados no QT longo ADQUIRIDO<br/>para aumentar a frequência e reduzir recorrência."])
  C_monitor(["Monitorização contínua;<br/>reavaliar QT, eletrólitos, função renal/hepática,<br/>fármacos/interações e causa reversível."])
  R2{"QT longo identificado,<br/>mas sem TV polimórfica em curso?"}
  C_prev(["Prevenção:<br/>retirar/reduzir gatilhos quando possível;<br/>corrigir eletrólitos;<br/>rever função renal/hepática e combinações pró-QT;<br/>usar Tisdale apenas como risco de QTc prolongado<br/>na população hospitalar em que foi validado."])

  R1 -->|"Sim"| C_shock
  C_shock --> D_qt
  D_qt -->|"Sim / provável"| C_tdp
  D_qt -->|"Não"| C_nonqt
  C_tdp --> D_recur
  D_recur -->|"Sim"| C_rate
  D_recur -->|"Não"| C_monitor
  C_rate --> C_monitor
  C_nonqt --> C_monitor
  R1 -->|"Não"| R2
  R2 -->|"Sim"| C_prev
  R2 -->|"Não / diagnóstico incerto"| C_monitor

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C_shock,C_tdp,C_nonqt,C_rate,C_monitor,C_prev conduta;
```

## Regras de segurança incorporadas ao fluxo

### 1. Não sincronizar TV polimórfica sustentada

AHA 2025: os complexos variam de morfologia e **não permitem sincronização confiável**. O tratamento é choque não sincronizado imediato, mesmo quando há pulso. A versão anterior deste fluxograma continha o ramo “com pulso + instável → cardioversão sincronizada”; ele foi removido.

### 2. Não usar “magnésio para toda TV polimórfica”

- **QT longo/TdP recorrente:** magnésio pode ser considerado (**2b, C-LD**).
- **QT normal:** magnésio rotineiro não é recomendado (**Classe 3: sem benefício, C-LD**).

A distinção importa porque TV polimórfica sem QT longo é frequentemente isquêmica e exige tratamento etiológico diferente.

### 3. Corrigir eletrólitos, mas não apresentar meta antiga como certeza moderna

Hipocalemia, hipomagnesemia e hipocalcemia reduzem a reserva de repolarização e devem ser corrigidas. A faixa de K⁺ **4,5-5,0 mmol/L** aparece em recomendações/consensos mais antigos com evidência baixa; a AHA 2025 não a transforma em meta universal para toda TdP.

> **VALIDAÇÃO INSTITUCIONAL NECESSÁRIA:** metas numéricas de K/Mg, dose/velocidade de MgSO4 e energia específica do choque devem ser validadas contra o protocolo local antes de virar ordem operacional.

### 4. Pacing/isoproterenol são estratégia de recorrência, não substituto do choque

Em TdP adquirida recorrente associada a bradicardia/pausas, AHA 2025 recomenda consulta especializada para **overdrive pacing ou isoproterenol**; ESC 2022 também reconhece essas estratégias. Elas não devem atrasar o choque de TV polimórfica sustentada.

Não extrapolar isoproterenol para síndrome de QT longo congênito sem avaliação especializada.

## Escore de Tisdale — encaixe correto

O Tisdale foi criado para predizer **prolongamento de QTc em paciente hospitalizado**, não para decidir choque, dose de magnésio ou probabilidade direta de TdP. No estudo original, QTc prolongado foi definido como >500 ms ou aumento >60 ms do basal.

| Variável | Pontos |
|---|---:|
| Idade ≥68 anos | 1 |
| Sexo feminino | 1 |
| Diurético de alça | 1 |
| Potássio sérico ≤3,5 mEq/L | 2 |
| QTc na admissão ≥450 ms | 2 |
| IAM agudo | 2 |
| Sepse | 3 |
| Insuficiência cardíaca | 3 |
| Um fármaco prolongador de QTc | 3 |
| ≥2 fármacos prolongadores de QTc | **6 no total** (3 do primeiro + 3 adicionais) |
| **Pontuação máxima** | **21** |

Estratos originais: baixo 0-6, moderado 7-10, alto 11-21. O escore não deve ser automaticamente generalizado para ambulatório, pediatria ou para estimar risco absoluto de TdP.

## Conexões prioritárias

- `torsades-de-pointes-e-qt-longo-adquirido-escore-de-tisdale-e-manejo-agudo`
- `sulfato-de-magnesio-em-cardiologia-torsades-de-pointes-e-adjuvante-no-controle-de-frequencia-da-fa`
- fármacos pró-QT (sotalol, ibutilida, metadona, antipsicóticos, antieméticos e outros)
- hipocalemia/hipomagnesemia/hipocalcemia
- isquemia miocárdica/ACS quando TV polimórfica ocorre sem QT longo
- intoxicação digitálica quando houver TV bidirecional/polimórfica por mecanismo tóxico

## Pendências para os próximos lotes

1. Auditar o verbete de sulfato de magnésio para alinhar a frase “primeira linha farmacológica” à prioridade do choque na TV polimórfica sustentada.
2. Criar módulo de hipomagnesemia e sua relação com hipocalemia refratária, diuréticos, digoxina e risco arrítmico.
3. Procurar outras ocorrências no corpus de “TV polimórfica → cardioversão sincronizada” e de “magnésio para qualquer TV polimórfica”.
4. Normalizar exames canônicos de potássio e magnésio em lote seguro, sem edição cega do manifesto monolítico.
