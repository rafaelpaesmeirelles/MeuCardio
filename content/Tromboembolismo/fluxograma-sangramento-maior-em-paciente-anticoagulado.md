---
title: "Sangramento maior em paciente anticoagulado"
slug: fluxograma-sangramento-maior-em-paciente-anticoagulado
theme: "Tromboembolismo"
kind: fluxograma
summary: "Árvore de decisão para sangramento em paciente anticoagulado: confirma primeiro se o sangramento é maior antes de cogitar qualquer antídoto, depois direciona a reversão específica por classe — varfarina, dabigatrana, inibidor do fator Xa (rivaroxabana/apixabana) ou heparina não fracionada."
review_status: revisado
source_refs: ["Pollack CV Jr, Reilly PA, van Ryn J, et al. Idarucizumab for Dabigatran Reversal — Full Cohort Analysis. N Engl J Med. 2017;377(5):431-441. DOI: 10.1056/NEJMoa1707278. PMID: 28693366", "Connolly SJ, Crowther M, Eikelboom JW, et al; ANNEXA-4 Investigators. Full Study Report of Andexanet Alfa for Bleeding Associated with Factor Xa Inhibitors. N Engl J Med. 2019;380(14):1326-1335. DOI: 10.1056/NEJMoa1814051. PMID: 30730782", "Tomaselli GF, Mahaffey KW, Cuker A, et al. 2020 ACC Expert Consensus Decision Pathway on Management of Bleeding in Patients on Oral Anticoagulants: A Report of the American College of Cardiology Solution Set Oversight Committee. J Am Coll Cardiol. 2020;76(5):594-622. DOI: 10.1016/j.jacc.2020.04.053. PMID: 32680646", "Garcia DA, Baglin TP, Weitz JI, Samama MM. Parenteral Anticoagulants: Antithrombotic Therapy and Prevention of Thrombosis, 9th ed: American College of Chest Physicians Evidence-Based Clinical Practice Guidelines. Chest. 2012;141(2 Suppl):e24S-e43S. DOI: 10.1378/chest.11-2291. PMID: 22315264"]
---

# Sangramento maior em paciente anticoagulado

Nem todo sangramento em paciente anticoagulado pede antídoto: a primeira
decisão é separar sangramento **maior** — risco de vida, local crítico ou
instabilidade hemodinâmica — de sangramento menor, que tem conduta
conservadora. Só depois dessa confirmação a árvore se ramifica pela classe do
anticoagulante, porque o agente de reversão é específico para cada uma.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em uso de anticoagulante,<br/>com sangramento ativo"]
  R0 --> D1

  D1{"É sangramento maior?<br/>Local crítico (SNC, pericárdio, via aérea,<br/>retroperitônio, intra-articular),<br/>instabilidade hemodinâmica, ou<br/>queda de Hb ≥2 g/dL / transfusão ≥2 unidades"}
  D1 -->|"Não, sangramento menor"| C1
  D1 -->|"Sim, sangramento maior"| P1

  C1(["Conduta conservadora: medidas locais/compressão,<br/>considerar retardar ou omitir a próxima dose;<br/>não usar antídoto específico"])

  P1["Suspender anticoagulante e antiagregante.<br/>Medidas locais/compressão, acesso calibroso,<br/>reposição volêmica e suporte hemodinâmico"]
  P1 --> D2

  D2{"Qual classe de anticoagulante?"}
  D2 -->|"Varfarina ou outro antagonista de vitamina K"| C2
  D2 -->|"Dabigatrana"| C3
  D2 -->|"Rivaroxabana ou apixabana"| D3
  D2 -->|"Heparina não fracionada"| C7

  C2(["Vitamina K 5-10 mg IV<br/>+ CCP de 4 fatores (25 U/kg se INR 2 a menor que 4;<br/>35 U/kg se INR 4-6; 50 U/kg se INR maior que 6).<br/>Se CCP indisponível, plasma 10-15 mL/kg"])

  C3(["Idarucizumabe 5 g IV<br/>(dois bolus de 2,5 g, até 15 min entre eles).<br/>Se indisponível, CCP ou CCP ativado 50 U/kg.<br/>Considerar carvão ativado se ingestão há 2-4h"])

  D3{"Andexanet alfa disponível?"}
  D3 -->|"Sim"| D4
  D3 -->|"Não"| C6

  C6(["CCP de 4 fatores (dose fixa de 2.000 U é razoável)<br/>ou CCP ativado. Considerar carvão ativado<br/>se ingestão há 2-4h"])

  D4{"Dose de andexanet pelo critério do fármaco:<br/>apixabana até 5 mg, rivaroxabana até 10 mg,<br/>ou última dose há 8h ou mais = dose baixa;<br/>doses maiores, ou menos de 8h/hora desconhecida = dose alta"}
  D4 -->|"Critério de dose baixa"| C4
  D4 -->|"Critério de dose alta"| C5

  C4(["Andexanet alfa dose baixa:<br/>bolus IV 400 mg a 30 mg/min,<br/>seguido de infusão 4 mg/min por 120 min"])

  C5(["Andexanet alfa dose alta:<br/>bolus IV 800 mg a 30 mg/min,<br/>seguido de infusão 8 mg/min por 120 min"])

  C7(["Protamina IV, 1 mg para cada 100 UI de heparina<br/>recebida nas últimas 2-3h<br/>(dose máxima 50 mg, infundir a menos de 5 mg/min)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que se repete em todo ramo, e por isso não está no diagrama

**Suporte hemodinâmico e correção de fatores agravantes.** Cristaloide para
reposição volêmica, correção de hipotermia e acidose — ambas pioram a
coagulopatia —, e investigação de comorbidades que também contribuem para o
sangramento (trombocitopenia, uremia, doença hepática). Transfusão de
concentrado de hemácias segue meta habitual de hemoglobina, mais alta em
doença coronariana estabelecida.

**Envolvimento precoce da especialidade do sítio de sangramento**
(neurocirurgia, endoscopia, radiologia intervencionista) corre em paralelo à
reversão farmacológica, sem esperar o antídoto para acionar.

**Risco trombótico após a reversão.** Os dois antídotos específicos removem
temporariamente a proteção antitrombótica: evento trombótico em 30-90 dias
ocorreu em 6,3-7,4% dos pacientes revertidos com idarucizumabe e em 10% dos
revertidos com andexanet alfa. A anticoagulação deve ser retomada assim que a
hemostasia permitir, não adiada indefinidamente por precaução.

**Andexanet alfa não deve ser considerado sinônimo de sangramento controlado
apenas pela queda laboratorial da atividade anti-fator Xa** — o ANNEXA-4
mostrou que essa redução não prediz de forma confiável a eficácia hemostática
clínica global, ao contrário do idarucizumabe, em que reversão laboratorial e
desfecho clínico caminharam juntos.

**Cada antídoto é específico para sua classe.** Andexanet alfa não reverte
dabigatrana, e idarucizumabe não reverte inibidor do fator Xa — não há
eficácia cruzada entre eles.
