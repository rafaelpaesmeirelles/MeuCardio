---
title: "Arritmia ventricular e risco de morte súbita"
slug: fluxograma-arritmia-ventricular-e-morte-subita
theme: "Arritmias"
kind: fluxograma
summary: "Árvore de conduta imediata para taquicardia de QRS largo e arritmias ventriculares: TV polimórfica sustentada exige choque não sincronizado imediato; TV monomórfica instável exige cardioversão sincronizada; após estabilização, mecanismo e causa orientam prevenção de recorrência e manejo da tempestade elétrica."
review_status: pendente_revisao
source_refs: ["Wigginton JG, Agarwal S, Bartos JA, et al. Part 9: Adult Advanced Life Support: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16 Suppl 2):S538-S577. DOI: 10.1161/CIR.0000000000001376. PMID: 41122884 — TV polimórfica sustentada: choque não sincronizado imediato (COR 1, B-NR); TV de QRS largo monomórfica instável: cardioversão sincronizada (COR 1, B-NR); magnésio apenas no contexto de recorrência associada a QT longo/TdP (2b, C-LD), não rotineiramente com QT normal (Classe 3: sem benefício, C-LD).", "Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126. DOI: 10.1093/eurheartj/ehac262. PMID: 36017572 — causas reversíveis, TV/TdP, isquemia, eletrólitos, pacing/isoproterenol e prevenção de morte súbita.", "Soeiro AM, Pisani CF, Petriz JLF, et al. Posicionamento sobre Diagnóstico e Tratamento da Tempestade Elétrica – 2026. Arq Bras Cardiol. 2026;123(4):e20260215. DOI: 10.36660/abc.20260215 — posicionamento GECETI/SBC e SOBRAC para reconhecimento e manejo multidisciplinar da tempestade elétrica.", "Ortiz M, Martín A, Arribas F, et al. Randomized comparison of intravenous procainamide vs intravenous amiodarone for tolerated wide QRS tachycardia: PROCAMIO. Eur Heart J. 2017;38(17):1329-1335. PMID: 27354046 — comparação farmacológica em taquicardia de QRS largo tolerada; não se aplica à TV polimórfica sustentada que requer choque.", "Sapp JL, Wells GA, Parkash R, et al. Ventricular tachycardia ablation versus escalation of antiarrhythmic drugs (VANISH). N Engl J Med. 2016;375(2):111-121. DOI: 10.1056/NEJMoa1513614. PMID: 27149033 — manejo de TV recorrente em cardiopatia isquêmica/CDI, fora da decisão elétrica imediata."]
legacy_source: "Atualização de segurança em 24/08/2026. A versão anterior aplicava a regra genérica 'instável = cardioversão sincronizada' antes de distinguir TV monomórfica de TV polimórfica e sugeria sulfato de magnésio no ramo de TV polimórfica sem QT longo. A AHA 2025 exige choque NÃO sincronizado imediato em TV polimórfica sustentada e classifica magnésio rotineiro na TV polimórfica com QT normal como sem benefício. Como houve alteração de conteúdo previamente marcado como revisado sem revisão humana documentada desta nova versão, o status foi alterado para pendente_revisao. VERIFICAÇÃO HUMANA NECESSÁRIA antes de republicar."
---

# Arritmia ventricular e risco de morte súbita

> **STATUS DE CURADORIA:** `pendente_revisao`. Atualizado para separar corretamente **TV monomórfica** de **TV polimórfica** antes de escolher terapia elétrica. **VERIFICAÇÃO HUMANA NECESSÁRIA** antes de converter o fluxo em protocolo institucional, especialmente para energia, doses e sequências farmacológicas.

## Regra de segurança que vem antes de todo o resto

Nem toda taquicardia de QRS largo instável recebe a mesma terapia elétrica:

- **TV polimórfica sustentada:** **choque não sincronizado imediato**. AHA 2025: **Classe 1, B-NR**. A sincronização não é confiável porque a morfologia do QRS muda batimento a batimento.
- **TV monomórfica sustentada hemodinamicamente instável:** **cardioversão sincronizada**. AHA 2025: **Classe 1, B-NR**.
- Se o ritmo polimórfico estiver sustentado, não atrasar o choque para determinar o QT, dosar eletrólitos ou administrar magnésio.

A versão anterior colocava “instável → cardioversão sincronizada” antes de diferenciar morfologia; essa arquitetura foi removida.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Taquicardia de QRS largo / provável arritmia ventricular"]
  D0{"Morfologia é polimórfica<br/>e o episódio está sustentado?"}
  C_PVT(["CHOQUE NÃO SINCRONIZADO imediato<br/>— alta energia conforme fabricante/protocolo.<br/>AHA 2025: Classe 1, B-NR."])
  D_QT{"Após terminar o episódio:<br/>QT basal prolongado / TdP provável?"}
  C_TDP(["TdP / QT longo:<br/>retirar gatilho pró-QT, corrigir K/Mg/Ca;<br/>magnésio IV pode ser considerado para recorrências<br/>(AHA 2025: 2b, C-LD);<br/>bradicardia/pausas recorrentes → consulta especializada<br/>para overdrive pacing/isoproterenol no QT longo adquirido."])
  C_PVTN(["TV polimórfica sem QT longo:<br/>buscar e tratar isquemia/infarto e outras causas;<br/>lidocaína ou amiodarona podem ser consideradas<br/>para recorrências conforme contexto.<br/>Magnésio rotineiro NÃO é recomendado<br/>(AHA 2025: Classe 3, C-LD)."])
  D1{"Se não é TV polimórfica sustentada:<br/>há instabilidade atribuível à taquicardia?"}
  C_SYNC(["TV/QRS largo monomórfico instável:<br/>cardioversão elétrica SINCRONIZADA imediata<br/>(AHA 2025: Classe 1, B-NR)."])
  D2{"Estável: TV monomórfica é<br/>confirmada ou fortemente presumida?"}
  C_WCT(["QRS largo regular monomórfico de mecanismo incerto:<br/>tratar como TV até prova em contrário;<br/>adenosina pode ser considerada apenas se regular/monomórfica;<br/>verapamil e diltiazem NÃO devem ser usados em QRS largo<br/>de etiologia incerta."])
  C_MVT(["TV monomórfica estável/tolerada:<br/>antiarrítmico IV pode ser considerado<br/>(procainamida, amiodarona ou sotalol conforme contexto),<br/>com cardioversão se falha, contraindicação ou deterioração;<br/>recorrência/incessância → avaliar estratégia de ablação."])
  D_ES{"Há tempestade elétrica<br/>(múltiplos episódios de TV/FV/terapias apropriadas)?"}
  C_ES(["Tempestade elétrica:<br/>cada episódio segue a regra elétrica pela morfologia;<br/>entre episódios: corrigir gatilhos, sedação/ansiólise,<br/>interrogar/reprogramar CDI quando aplicável,<br/>antiarrítmicos/betabloqueio conforme substrato e<br/>considerar ablação/modulação autonômica/suporte avançado<br/>em centro experiente conforme SBC/SOBRAC 2026."])
  C_END(["Após estabilização:<br/>definir mecanismo, causa reversível, cardiopatia estrutural,<br/>risco de recorrência e prevenção de morte súbita."])

  R0 --> D0
  D0 -->|"Sim"| C_PVT
  C_PVT --> D_QT
  D_QT -->|"Sim / provável"| C_TDP
  D_QT -->|"Não"| C_PVTN
  D0 -->|"Não"| D1
  D1 -->|"Sim"| C_SYNC
  D1 -->|"Não"| D2
  D2 -->|"Não / incerto"| C_WCT
  D2 -->|"Sim"| C_MVT
  C_TDP --> D_ES
  C_PVTN --> D_ES
  C_SYNC --> D_ES
  C_WCT --> D_ES
  C_MVT --> D_ES
  D_ES -->|"Sim"| C_ES
  D_ES -->|"Não"| C_END
  C_ES --> C_END

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C_PVT,C_TDP,C_PVTN,C_SYNC,C_WCT,C_MVT,C_ES,C_END conduta;
```

## TV polimórfica: QT longo versus QT normal

AHA 2025 enfatiza que o **QT basal** muda o tratamento de recorrência:

### QT longo / torsades de pointes

- Choque não sincronizado se o episódio estiver sustentado.
- Retirar fármacos pró-QT quando possível e corrigir hipocalemia, hipomagnesemia e hipocalcemia.
- Magnésio IV **pode ser considerado** para recorrências (**2b, C-LD**), mesmo sem hipomagnesemia documentada.
- Em TdP adquirida recorrente, pausa/bradicardia-dependente, considerar com especialista overdrive pacing ou isoproterenol.

### QT não prolongado

- Choque não sincronizado se sustentada.
- Isquemia/infarto são causas frequentes e devem ser tratados ativamente.
- Lidocaína ou amiodarona podem ser consideradas para recorrências (**2b, C-LD**), junto ao manejo etiológico.
- **Não usar magnésio rotineiramente apenas porque a TV é polimórfica** — AHA 2025: **Classe 3, sem benefício, C-LD**.

## Taquicardia de QRS largo monomórfica

Na TV monomórfica/QRS largo regular, a estabilidade ainda é decisiva:

- **instável:** cardioversão sincronizada imediata;
- **estável:** há tempo para ECG de 12 derivações, acesso IV e terapia farmacológica selecionada;
- AHA 2025 permite considerar amiodarona, procainamida ou sotalol IV (**2b, B-R**);
- adenosina pode ser considerada quando a taquicardia é **regular e monomórfica** e o diagnóstico ainda é incerto (**2b, B-NR**);
- verapamil/diltiazem não devem ser administrados em taquicardia de QRS largo de etiologia incerta, pelo risco de deterioração quando o ritmo é ventricular.

O PROCAMIO informa a escolha farmacológica em taquicardia de QRS largo **tolerada**; não deve ser extrapolado para TV polimórfica sustentada ou paciente instável.

## Tempestade elétrica: o tratamento entre episódios não substitui a terapia do episódio

O Posicionamento SBC/SOBRAC 2026 organiza a tempestade elétrica como síndrome de recorrência arrítmica que requer busca de gatilhos, controle autonômico/sedação, otimização de antiarrítmicos, programação do CDI e acesso precoce a ablação e suporte avançado conforme gravidade.

A regra transversal é:

- episódio **polimórfico sustentado** → choque não sincronizado;
- episódio **monomórfico instável** → cardioversão sincronizada;
- depois do término, tratar mecanismo/substrato e prevenir recorrência.

Isso evita que o rótulo “tempestade elétrica” apague a diferença crítica entre as duas morfologias.

## Causas reversíveis correm em paralelo

Investigar e tratar, conforme o cenário:

- isquemia/infarto agudo;
- hipocalemia, hipomagnesemia e outras alterações eletrolíticas;
- fármacos pró-arrítmicos/toxicidade/interações;
- insuficiência cardíaca descompensada;
- hipóxia, acidose e distúrbios sistêmicos;
- canalopatias e cardiomiopatias quando o contexto sugere.

“Causa reversível” não significa automaticamente risco futuro zero; a ESC 2022 ressalta que sobreviventes de parada atribuída a causa aparentemente corrigível ainda podem manter risco relevante conforme a cardiopatia de base.

## Conexões canônicas

- `fluxograma-torsades-de-pointes-e-qt-longo-adquirido`
- `torsades-de-pointes-e-qt-longo-adquirido-escore-de-tisdale-e-manejo-agudo`
- tempestade elétrica / posição SBC-SOBRAC 2026
- síndrome coronariana aguda/isquemia quando TV polimórfica ocorre sem QT longo
- fármacos pró-QT, hipocalemia, hipomagnesemia e hipocalcemia
- ablação de TV, CDI e prevenção secundária de morte súbita

## Pendências deliberadas

1. Auditar `fluxograma-taquicardia-de-qrs-largo-esc-2019.md` para garantir que a distinção monomórfica/polimórfica esteja explícita à luz da AHA 2025.
2. Auditar o serviço/calculadora ACLS 2025 e o documento farmacológico correspondente para consistência com o fluxo canônico, sem duplicar algoritmo.
3. Revisar o módulo de sulfato de magnésio para evitar que “primeira linha farmacológica” seja interpretada como anterior ao choque da TV polimórfica sustentada.
4. Conectar formalmente hipomagnesemia/hipocalemia e exames canônicos de K/Mg em lotes separados.
