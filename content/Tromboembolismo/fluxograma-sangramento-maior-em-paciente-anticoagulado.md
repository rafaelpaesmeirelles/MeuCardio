---
title: "Sangramento maior em paciente anticoagulado"
slug: fluxograma-sangramento-maior-em-paciente-anticoagulado
theme: "Tromboembolismo"
kind: fluxograma
summary: "Fluxo de reversão urgente por classe de anticoagulante, distinguindo sangramento menor de maior, evitando suspensão automática de antiagregante e incorporando o alerta FDA de 2025 que retirou alfa-andexanete do mercado dos EUA por balanço risco-benefício desfavorável."
review_status: revisado
source_refs: ["Tomaselli GF, Mahaffey KW, Cuker A, et al. 2020 ACC Expert Consensus Decision Pathway on Management of Bleeding in Patients on Oral Anticoagulants. J Am Coll Cardiol. 2020;76(5):594-622. DOI: 10.1016/j.jacc.2020.04.053. PMID: 32680646", "Greenberg SM, Ziai WC, Cordonnier C, et al. 2022 Guideline for the Management of Patients With Spontaneous Intracerebral Hemorrhage. Stroke. 2022;53(7):e282-e361. DOI: 10.1161/STR.0000000000000407. PMID: 35579034", "Pollack CV Jr, Reilly PA, van Ryn J, et al. Idarucizumab for Dabigatran Reversal — Full Cohort Analysis. N Engl J Med. 2017;377(5):431-441. DOI: 10.1056/NEJMoa1707278. PMID: 28693366", "Connolly SJ, Sharma M, Cohen AT, et al; ANNEXA-I Investigators. Andexanet for Factor Xa Inhibitor-Associated Acute Intracerebral Hemorrhage. N Engl J Med. 2024;390(19):1745-1755. DOI: 10.1056/NEJMoa2313040. NCT03661528", "US Food and Drug Administration. Update on the Safety of Andexxa by AstraZeneca: FDA Safety Communication. Atualização de 22/12/2025 — FDA concluiu que os riscos superam os benefícios; vendas e fabricação nos EUA encerradas em 22/12/2025 e retirada da aprovação registrada em 23/12/2025", "Agência Nacional de Vigilância Sanitária. Ondexxya (alfa-andexanete): novo registro. Publicado em 05/09/2023 — registro brasileiro para reversão de apixabana ou rivaroxabana em sangramento com risco à vida ou não controlado", "Garcia DA, Baglin TP, Weitz JI, Samama MM. Parenteral Anticoagulants: Antithrombotic Therapy and Prevention of Thrombosis, 9th ed. Chest. 2012;141(2 Suppl):e24S-e43S. DOI: 10.1378/chest.11-2291. PMID: 22315264"]
review_note: "Revisão de 26/08/2026: removido o ramo automático e as doses de alfa-andexanete após incorporar ANNEXA-I e a comunicação FDA de dezembro de 2025. O ensaio mostrou melhor controle de expansão do hematoma, porém mais trombose e AVC isquêmico, sem diferença apreciável em função ou morte em 30 dias; a FDA posteriormente concluiu que os riscos superavam os benefícios e retirou a aprovação nos EUA. O registro Anvisa de 2023 foi preservado como contexto regulatório brasileiro, sem inferir situação comercial em tempo real. Corrigida a suspensão automática de antiagregante, adicionada a reversão parcial de heparina de baixo peso molecular e retirada a regra simplificada de protamina que ignorava dose e tempo desde a heparina."
---

# Sangramento maior em paciente anticoagulado

Antídoto não é resposta para qualquer sangramento. Primeiro classifique a
gravidade; depois identifique fármaco, última dose, função renal e sítio. Em
hemorragia intracraniana ou outro local crítico, a reversão não deve esperar o
resultado de ensaio específico quando há exposição clinicamente relevante.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Sangramento ativo em paciente<br/>que usa anticoagulante"]
  D1{"Sangramento maior?<br/>Local crítico, instabilidade, queda de Hb >=2 g/dL<br/>ou necessidade de >=2 unidades de hemácias"}
  C1["Sangramento não maior:<br/>controle local e revisão da próxima dose;<br/>não administrar reversor rotineiramente"]
  P1["Interromper o anticoagulante; registrar agente,<br/>dose/horário e função renal; hemograma, coagulação,<br/>tipagem e controle imediato da fonte"]
  D2{"Qual anticoagulante?"}
  C2["Antagonista da vitamina K:<br/>vitamina K IV + CCP de 4 fatores;<br/>dose do CCP pelo INR/produto;<br/>plasma apenas se CCP indisponível"]
  C3["Dabigatrana:<br/>idarucizumabe 5 g IV;<br/>se indisponível, CCP ativado ou CCP<br/>pode ser considerado"]
  C4["Apixabana, rivaroxabana ou edoxabana:<br/>CCP de 4 fatores ou CCP ativado pode ser<br/>considerado conforme protocolo institucional"]
  C7["Heparina não fracionada:<br/>protamina IV calculada pela heparina residual<br/>(dose e tempo); máximo 50 mg e infusão lenta"]
  C8["Heparina de baixo peso molecular:<br/>protamina pode reverter apenas parcialmente;<br/>calcular por agente, dose e tempo"]
  C9["Outro agente ou exposição incerta:<br/>hematologia/toxicologia e protocolo específico;<br/>não improvisar antídoto cruzado"]

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P1
  P1 --> D2
  D2 -->|"Varfarina/AVK"| C2
  D2 -->|"Dabigatrana"| C3
  D2 -->|"Inibidor direto do fator Xa"| C4
  D2 -->|"HNF"| C7
  D2 -->|"HBPM"| C8
  D2 -->|"Outro/incerto"| C9

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C7,C8,C9 conduta;
```

## Correções de segurança inseparáveis do fluxo

**Antiagregante não é suspenso automaticamente.** O anticoagulante causador é
interrompido no sangramento maior. Já aspirina ou inibidor P2Y12 exige balanço
entre hemostasia e indicação — sobretudo após intervenção coronária recente —
com a equipe responsável. A versão anterior mandava suspender ambos em bloco.

**Alfa-andexanete não é mais um ramo automático.** No ANNEXA-I, em hemorragia
intracerebral após inibidor do fator Xa, eficácia hemostática ocorreu em 67,0%
com alfa-andexanete e 53,1% com cuidado usual, mas eventos trombóticos ocorreram
em 10,3% versus 5,6% e AVC isquêmico em 6,5% versus 1,5%; não houve diferença
apreciável em função ou morte em 30 dias. Em 22 de dezembro de 2025, a FDA
informou que os riscos superavam os benefícios e encerrou venda/fabricação nos
EUA; a retirada da aprovação consta em 23 de dezembro de 2025.

A Anvisa havia concedido registro ao Ondexxya em 4 de setembro de 2023 para
apixabana/rivaroxabana em sangramento com risco à vida ou não controlado. Como
os marcos regulatórios divergiram, eventual uso fora dos EUA requer conferir a
situação regulatória e disponibilidade locais e decisão multidisciplinar; este
fluxograma não publica dose nem o posiciona à frente do CCP.

**Protamina depende de exposição residual.** A equivalência de 1 mg por 100 UI
vale para heparina ainda circulante e deve cair conforme o tempo desde a dose.
Aplicá-la a toda a heparina das últimas 2-3 horas superestima a necessidade e
aumenta risco de hipotensão/broncoespasmo. Na HBPM, a neutralização é parcial.

**Carvão ativado não ocupa o algoritmo central.** Pode reduzir absorção após
ingestão muito recente de anticoagulante oral, mas a janela varia pelo agente e
a evidência clínica é limitada; risco de aspiração e proteção de via aérea são
decisivos. Discutir com toxicologia, sem atrasar controle da fonte e reversão.

## Retomada da anticoagulação

Reversão aumenta risco trombótico, mas “retomar assim que houver hemostasia”
não é um prazo universal. Sítio e causa do sangramento, controle definitivo da
fonte, indicação trombótica e risco de recorrência definem a decisão. Hemorragia
intracraniana exige algoritmo próprio e não deve herdar o prazo de sangramento
extracraniano.

## Tudo com Tudo

- [Reversão de anticoagulante em sangramento maior](reversao-de-anticoagulante-em-sangramento-maior-idarucizumabe-e-andexanet-alfa.md)
- [Reinício da anticoagulação após hemorragia intracraniana](../Fibrilação_atrial/reiniciar-anticoagulacao-na-fa-apos-hemorragia-intracraniana-sostart-prestige-af-e-a-metanalise-cocroach.md)
- [TEV recorrente sob anticoagulação terapêutica](tev-recorrente-sob-anticoagulacao-em-dose-terapeutica-conduta.md)
- [Interrupção do anticoagulante para procedimento eletivo](../Fibrilação_atrial/interrupcao-do-anticoagulante-para-procedimento-eletivo-na-fa-bridge-e-pause.md)
