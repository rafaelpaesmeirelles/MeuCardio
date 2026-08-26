---
title: "Fluxograma: Anemia e decisão de transfusão no infarto"
slug: fluxograma-anemia-e-decisao-de-transfusao-no-infarto
theme: "Terapia intensiva"
kind: fluxograma
summary: "Decisão transfusional no paciente com síndrome coronariana aguda e anemia: separar sangramento ativo, reconhecer a recomendação liberal condicional abaixo de 10 g/dL e reavaliar após cada unidade sem transformar hemoglobina isolada em prescrição automática."
review_status: revisado
source_refs: ["Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes. Circulation. 2025. DOI: 10.1161/CIR.0000000000001309 — transfusão para atingir Hb >=10 g/dL pode ser razoável na SCA com anemia aguda ou crônica (Classe 2b, B-R); o resumo oficial delimita pacientes sem sangramento ativo", "Pagano MB, Stanworth SJ, Dennis J, et al. Red Cell Transfusion in Acute Myocardial Infarction: AABB International Clinical Practice Guidelines. Ann Intern Med. 2025;178(10):1469-1477. DOI: 10.7326/ANNALS-25-00706. PMID: 40825204 — estratégia liberal sugerida quando Hb <10 g/dL; recomendação condicional, evidência de baixa certeza", "Carson JL, Brooks MM, Hébert PC, et al; MINT Investigators. Restrictive or Liberal Transfusion Strategy in Myocardial Infarction and Anemia. N Engl J Med. 2023;389(26):2446-2456. DOI: 10.1056/NEJMoa2307983. PMID: 37952133. PMCID: PMC10837004 — NCT02981407, 3.504 pacientes", "Ducrocq G, Gonzalez-Juanatey JR, Puymirat E, et al; REALITY Investigators. Effect of a Restrictive vs Liberal Blood Transfusion Strategy on Major Cardiovascular Events Among Patients With Acute Myocardial Infarction and Anemia. JAMA. 2021;325(6):552-560. DOI: 10.1001/jama.2021.0135. PMID: 33560322. PMCID: PMC7873781 — ler com a correção de 2026", "Steg PG; REALITY Investigators. Primary Composite Outcome Corrected in a Trial of Transfusion Strategy in Myocardial Infarction and Anemia. JAMA. 2026;336(3):261. DOI: 10.1001/jama.2026.10006; Correction to Primary Composite Outcome in a Trial of Transfusion Strategy. JAMA. 2026;336(3):262. DOI: 10.1001/jama.2026.0015. PMID: 42340742 — eventos primários corrigidos para 29 no grupo restritivo e 36 no liberal; a conclusão de não inferioridade em 30 dias não mudou"]
review_note: "Revisão de 26/08/2026: removido o marcador humano e refeita a sequência com fontes posteriores ao documento original. O fluxo anterior terminava em estratégia restritiva quando Hb estava entre 7-8 e 10 g/dL e misturava o TRICS-III, de cirurgia cardíaca, ao IAM primário. A diretriz ACC/AHA 2025 atribui Classe 2b, B-R à transfusão para atingir Hb >=10 g/dL na SCA com anemia, e seu resumo oficial restringe a orientação a quem não está sangrando ativamente; a AABB 2025 sugere estratégia liberal no IAM com Hb <10 g/dL, mas de forma condicional e com evidência de baixa certeza. O ramo de cirurgia foi retirado. A errata REALITY 2026 foi lida: corrigiu a composição e a contagem do desfecho primário, sem alterar a conclusão de não inferioridade em 30 dias."
---

# Fluxograma: Anemia e decisão de transfusão no infarto

No paciente com síndrome coronariana aguda (SCA), a estratégia transfusional
restritiva usada rotineiramente em outras populações não deve ser importada de
forma automática. A diretriz ACC/AHA 2025 considera que transfundir para atingir
hemoglobina (Hb) **>=10 g/dL pode ser razoável** na SCA com anemia aguda ou
crônica (Classe 2b, B-R) quando não há sangramento ativo. A AABB 2025 vai na
mesma direção para o infarto agudo, porém sua recomendação é **condicional** e
baseada em evidência de **baixa certeza**.

Isso não transforma Hb <10 g/dL em ordem automática. Define uma estratégia a
ser considerada em conjunto com isquemia, tendência da Hb, risco de sobrecarga,
preferências do paciente e resposta a cada unidade.

## Árvore de decisão

```mermaid
flowchart TD
  R1["SCA/infarto em curso<br/>com anemia"]
  D1{"Sangramento ativo não controlado<br/>ou instabilidade atribuível à hemorragia?"}
  D2{"Hb < 10 g/dL?"}
  D3{"IAM confirmado?"}
  C1["Sair deste algoritmo de limiar:<br/>controlar a fonte e ressuscitar conforme<br/>hemorragia, perfusão e evolução seriada;<br/>MINT/REALITY não definem gatilho fixo aqui"]
  C2["Não transfundir apenas por anemia:<br/>Hb >=10 g/dL está fora da população<br/>randomizada; investigar e tratar a causa"]
  C3["Considerar estratégia liberal:<br/>concentrado de hemácias para atingir<br/>Hb >=10 g/dL pode ser razoável<br/>(ACC/AHA 2025, Classe 2b, B-R)"]
  C4["Além da ACC/AHA, AABB 2025 sugere<br/>estratégia liberal no IAM com Hb <10 g/dL<br/>(condicional; baixa certeza)"]
  D4{"Após discutir contexto, risco transfusional<br/>e preferência, decisão é transfundir?"}
  C5["Administrar 1 unidade por vez;<br/>reavaliar Hb, isquemia, perfusão e congestão;<br/>se mantida a estratégia liberal, titular<br/>para Hb >=10 g/dL"]
  C6["Não transfundir agora:<br/>documentar a razão, tratar a causa da anemia<br/>e reavaliar Hb/isquemia de forma seriada"]

  R1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| D3
  D3 -->|"Não / SCA sem IAM confirmado"| C3
  D3 -->|"Sim"| C4
  C3 --> D4
  C4 --> D4
  D4 -->|"Sim"| C5
  D4 -->|"Não"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Como executar sem converter recomendação fraca em regra rígida

**Sangramento ativo é outro algoritmo.** MINT pausava o protocolo quando o
clínico julgava necessária transfusão imediata por sangramento, e excluiu
sangramento agudo não controlado que exigisse sangue não compatibilizado. A
orientação resumida da ACC/AHA para manter Hb em 10 g/dL também explicita a
ausência de sangramento ativo. Nesse cenário, uma Hb estática não substitui
controle da fonte, avaliação de perfusão e evolução seriada.

**Uma unidade e nova avaliação.** No MINT, ambos os grupos recebiam uma unidade
por vez, seguida de nova medida da Hb. Essa sequência reduz transfusão além do
necessário e permite interromper ou desacelerar diante de congestão, reação ou
mudança do quadro clínico. A estratégia liberal do ensaio mantinha Hb >=10
g/dL; a restritiva permitia transfusão abaixo de 8 g/dL, recomendava fortemente
abaixo de 7 g/dL e também permitia transfundir por angina persistente apesar de
tratamento medicamentoso.

**A recomendação atual favorece considerar a liberal, não obriga transfusão.**
O MINT não atingiu superioridade estatística no composto de morte ou reinfarto
em 30 dias (16,9% versus 14,5%; RR 1,15; IC95% 0,99-1,34; p=0,07), mas não
excluiu dano com a estratégia restritiva. A AABB agregou quatro ensaios e
concluiu que 7-8 g/dL pode aumentar mortalidade no IAM; ainda assim, classificou
a sugestão liberal como condicional e de baixa certeza, exigindo contexto além
da concentração de Hb.

**REALITY deve ser lido com a correção de 2026.** O cálculo original incluiu
indevidamente insuficiência cardíaca no composto primário e classificou quatro
retiradas de consentimento como ausência de evento. A correção reduziu os
eventos primários para 29 no grupo restritivo e 36 no liberal, sem mudar a
conclusão de não inferioridade em 30 dias. Isso não anula a incerteza clínica
nem transforma não inferioridade de um ensaio em recomendação universal.

**Cirurgia cardíaca não pertence a esta árvore.** O TRICS-III estudou o período
perioperatório de cirurgia cardíaca em pacientes de risco moderado a alto, não
o IAM primário em curso; o MINT excluiu cirurgia cardíaca prevista durante a
internação. O limiar de 7,5 g/dL do TRICS-III não deve ser usado como atalho no
ramo de SCA deste fluxograma.

## Tudo com Tudo

- [Diretriz ACC/AHA 2025 de síndrome coronariana aguda](../Doença_coronariana/acc-aha-2025-diretriz-sindrome-coronariana-aguda.md)
- [MINT: estratégia liberal versus restritiva no IAM com anemia](../Doença_coronariana/mint-transfusao-liberal-restritiva-iam-anemia.md)
- [Limiares de transfusão no cardiopata: MINT, REALITY e TRICS-III](limiar-de-transfusao-no-cardiopata-mint-reality-e-trics-iii.md)
- [Fluxograma de síndrome coronariana aguda — ESC 2023](../Doença_coronariana/fluxograma-sindrome-coronariana-aguda-esc-2023.md)
