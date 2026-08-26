---
title: "Fluxograma: Escolha de Antidepressivo e Antipsicótico no Cardiopata — Risco de Prolongamento de QT"
slug: fluxograma-escolha-de-antidepressivo-e-antipsicotico-no-cardiopata-risco-de-qt
theme: "Saúde mental e cardiologia"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Cardiovascular Considerations in Antidepressant Therapy: An Evidence-Based Review · PMC · https://pmc.ncbi.nlm.nih.gov/articles/PMC4434967/"
  - "Glassman AH, O'Connor CM, Califf RM, Swedberg K, Schwartz P, et al; Sertraline Antidepressant Heart Attack Randomized Trial (SADHART) Group. Sertraline treatment of major depression in patients with acute MI or unstable angina. JAMA. 2002;288(6):701-709. DOI: 10.1001/jama.288.6.701. PMID: 12169073."
  - "Angermann CE, Gelbrich G, Störk S, Gunold H, Edelmann F, et al; MOOD-HF Study Investigators. Effect of Escitalopram on All-Cause Mortality and Hospitalization in Patients With Heart Failure and Depression: The MOOD-HF Randomized Clinical Trial. JAMA. 2016;315(24):2683-2693. DOI: 10.1001/jama.2016.7635. PMID: 27367876."
  - "Ray WA, Meredith S, Thapa PB, Meador KG, Hall K, Murray KT. Antipsychotics and the risk of sudden cardiac death. Arch Gen Psychiatry. 2001;58(12):1161-1167. DOI: 10.1001/archpsyc.58.12.1161. PMID: 11735845."
  - "Ray WA, Chung CP, Murray KT, Hall K, Stein CM. Atypical antipsychotic drugs and the risk of sudden cardiac death. N Engl J Med. 2009;360(3):225-235. DOI: 10.1056/NEJMoa0806994. PMID: 19144938."
  - "Wenzel-Seifert K, Wittmann M, Haen E. QTc prolongation by psychotropic drugs and the risk of Torsade de Pointes. Dtsch Arztebl Int. 2011;108(41):687-693. DOI: 10.3238/arztebl.2011.0687. PMID: 22114630."
  - "Drew BJ, Ackerman MJ, Funk M, Gibler WB, Kligfield P, Menon V, Philippides GJ, Roden DM, Zareba W; American Heart Association Acute Cardiac Care Committee. Prevention of torsade de pointes in hospital settings: a scientific statement from the American Heart Association and the American College of Cardiology Foundation. Circulation. 2010;121(8):1047-1060. DOI: 10.1161/CIRCULATIONAHA.109.192704. PMID: 20142454."
  - "Derivado de seguranca-cardiovascular-de-psicofarmacos-antidepressivos-e-doenca-cardiaca.md e antipsicoticos-e-prolongamento-de-qt-risco-de-morte-subita-cardiaca.md, já publicados no acervo (Saúde mental e cardiologia)."
---

# Fluxograma: Escolha de Antidepressivo e Antipsicótico no Cardiopata — Risco de Prolongamento de QT

Duas classes de psicofármacos, dois documentos já publicados nesta pasta, duas árvores separadas — porque a lógica de decisão de cada classe é distinta. Antidepressivo: a escolha entre ISRS já embute o risco de QT (citalopram e escitalopram no topo do risco), e o cenário cardiovascular do paciente (síndrome coronariana aguda recente vs. insuficiência cardíaca) muda a expectativa de benefício. Antipsicótico: a decisão gira em torno de quando pedir ECG basal e quando agir diante de um QTc alterado, sem que a divisão típico/atípico sirva de critério de segurança.

## Árvore de decisão: escolha de antidepressivo no cardiopata

```mermaid
flowchart TD
  R0["Cardiopata com indicação de iniciar antidepressivo<br/>do grupo dos ISRS"] --> D1{"Qual ISRS está<br/>sendo considerado?"}

  D1 -->|"Citalopram ou escitalopram"| P1["Citalopram e escitalopram são, em geral,<br/>opções menos preferidas nesse contexto —<br/>citalopram tem a maior capacidade cardiotóxica<br/>dose-dependente entre os ISRS e é o mais<br/>associado a prolongamento de QT (risco<br/>conhecido de torsades de pointes)"]
  P1 --> D2{"Há contraindicação (síndrome do QT longo<br/>congênito, bradicardia, hipopotassemia,<br/>hipomagnesemia, infarto do miocárdio recente<br/>ou insuficiência cardíaca descompensada)?"}
  D2 -->|"Sim"| C1(["Evitar citalopram/escitalopram; preferir<br/>sertralina, fluoxetina ou paroxetina como<br/>ISRS de escolha em doença coronariana"])
  D2 -->|"Não"| D3{"Idade do paciente (limite de<br/>dose do citalopram pela FDA)"}
  D3 -->|"Acima de 60 anos"| C2(["Se optar por citalopram apesar da<br/>preferência por outro ISRS, não exceder<br/>20 mg/dia; escitalopram não deve exceder<br/>20 mg/dia em nenhuma idade"])
  D3 -->|"60 anos ou menos"| C3(["Se optar por citalopram apesar da<br/>preferência por outro ISRS, não exceder<br/>40 mg/dia; escitalopram não deve<br/>exceder 20 mg/dia"])

  D1 -->|"Sertralina, fluoxetina ou paroxetina"| D4{"Há contraindicação (síndrome do QT longo<br/>congênito, bradicardia, hipopotassemia,<br/>hipomagnesemia, infarto do miocárdio recente<br/>ou insuficiência cardíaca descompensada)?"}
  D4 -->|"Sim"| C4(["Corrigir a contraindicação (eletrólitos,<br/>quadro agudo) e considerar ECG basal<br/>antes de iniciar"])
  D4 -->|"Não"| D5{"Contexto clínico<br/>cardiovascular do paciente"}
  D5 -->|"Síndrome coronariana aguda recente<br/>(até 30 dias) ou angina instável"| C5(["Sertralina 50 a 200 mg/dia tem segurança<br/>cardiovascular estabelecida nesse cenário<br/>(SADHART): sem efeito sobre fração de<br/>ejeção, extrassístoles ventriculares<br/>ou QTc versus placebo"])
  D5 -->|"Insuficiência cardíaca<br/>com depressão"| C6(["Iniciar com cautela e sem prometer<br/>benefício cardíaco: no MOOD-HF,<br/>escitalopram não superou o placebo na<br/>melhora da depressão nem reduziu<br/>mortalidade/internação nesta população —<br/>a indicação é a depressão em si"])
  D5 -->|"Doença coronariana estável, sem<br/>síndrome aguda recente e sem<br/>insuficiência cardíaca"| C7(["Sertralina, fluoxetina ou paroxetina<br/>são as opções preferidas (ISRS de<br/>escolha em doença coronariana)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Árvore de decisão: escolha de antipsicótico e monitorização de QT

```mermaid
flowchart TD
  R0["Paciente com indicação de iniciar antipsicótico, em<br/>avaliação de risco cardiovascular de prolongamento<br/>de QT"] --> D1{"Paciente tem fator de risco cardiovascular conhecido<br/>(doença cardíaca estrutural, arritmia prévia, QT longo<br/>congênito ou adquirido, uso concomitante de outro<br/>fármaco prolongador de QT, distúrbio eletrolítico,<br/>idade avançada), OU o fármaco considerado é<br/>tioridazina, ziprasidona ou haloperidol<br/>intravenoso em dose alta?"}

  D1 -->|"Não"| C1(["Iniciar o antipsicótico conforme a indicação<br/>psiquiátrica; realizar ECG seriado após<br/>qualquer escalonamento de dose e reavaliar<br/>com ECG diante de sintoma sugestivo de<br/>arritmia (síncope, palpitação, quase-síncope),<br/>independentemente do fármaco escolhido"])

  D1 -->|"Sim"| P1["Realizar ECG basal e corrigir<br/>hipocalemia e hipomagnesemia<br/>antes de iniciar"]
  P1 --> D2{"Emergência psiquiátrica com risco iminente<br/>de auto ou heteroagressão, sem tempo hábil<br/>para aguardar o ECG basal?"}
  D2 -->|"Sim"| C2(["Não adiar o tratamento da emergência<br/>psiquiátrica: escolher a via de administração<br/>e a dose dentro do perfil de menor risco<br/>disponível, e obter o ECG assim que possível"])
  D2 -->|"Não"| P2["Escolher o fármaco lembrando que a divisão<br/>entre antipsicótico típico e atípico não prediz<br/>risco cardíaco (risco numericamente maior nos<br/>atípicos: razão de incidência 2,26 vs. 1,99 no<br/>estudo de Ray et al., 2009, NEJM) e que o risco<br/>é dose-dependente nas duas classes"]
  P2 --> D3{"QTc basal ou após início do fármaco<br/>ultrapassa 500 ms, ou aumenta 60 ms ou<br/>mais em relação ao valor basal<br/>(critério da AHA/ACCF, 2010)?"}
  D3 -->|"Sim"| C3(["Ação pronta indicada: trocar o fármaco,<br/>corrigir interação medicamentosa,<br/>bradiarritmia ou distúrbio eletrolítico, e<br/>garantir desfibrilador disponível"])
  D3 -->|"Não"| C4(["Manter o fármaco; realizar ECG seriado<br/>após qualquer escalonamento de dose e<br/>reavaliar com ECG diante de sintoma<br/>sugestivo de arritmia"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## O que as árvores não mostram

**O risco cardíaco de um paciente polimedicado é cumulativo, não do fármaco isolado.** Além dos antipsicóticos e do citalopram, quetiapina, amisulprida e antidepressivos tricíclicos/tetracíclicos também aparecem entre os relatos de prolongamento de QTc — a avaliação de risco precisa somar toda a farmacoterapia.

**Não existe protocolo numerado e universal de periodicidade de ECG por fármaco** — duas revisões independentes (Wenzel-Seifert et al. e Beach et al.) concluem que a frequência de monitorização deve ser individualizada pelo fármaco e pelos fatores de risco do paciente, não fixada em uma tabela.

**Suspender o antipsicótico por receio cardiovascular tem custo de mortalidade próprio** — já documentado no acervo desta pasta (esquizofrenia e mortalidade cardiovascular): a decisão correta é estratificar risco e trocar por fármaco de perfil mais favorável, não interromper o tratamento psiquiátrico.
