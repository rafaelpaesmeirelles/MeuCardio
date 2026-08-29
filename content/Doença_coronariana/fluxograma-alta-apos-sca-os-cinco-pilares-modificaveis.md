---
title: "Fluxograma: alta após SCA — os cinco pilares modificáveis"
slug: fluxograma-alta-apos-sca-os-cinco-pilares-modificaveis
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: grok
summary: "Árvore da manhã da alta após síndrome coronariana aguda: antitrombótico com data, LDL intensificado na internação, eixo neuro-hormonal guiado pela FEVE, cessação tabágica com fármaco, reabilitação mais diabetes/obesidade. Não clona o fluxograma de DAPT nem o de cessação; aponta para eles quando o ramo exige detalhe."
review_status: pendente_revisao
review_note: "Árvore original de alta. Prazos de DAPT dual versus monoterapia não foram inventados — o nó de antitrombótico despacha para o fluxograma de DAPT já publicado. Classes e níveis só os verificados no playbook correspondente e nas tabelas lidas. EMPACT-MI e REDUCE-AMI entram como freio de extrapolação, não como classe de diretriz."
source_refs:
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654"
  - "Cesar LAM, Gowdak LHW, Pavanello R, et al. Diretriz de Síndrome Coronariana Crônica – 2025. Arq Bras Cardiol. 2025;122(9):e20250619. DOI: 10.36660/abc.20250619. PMID: 41294178"
  - "Rached FH, Miname MH, Rocha VZ, et al. Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose – 2025. Arq Bras Cardiol. 2025;122(9):e20250640. DOI: 10.36660/abc.20250640. PMID: 41379178"
  - "Mach F, Koskinas KC, Roeters van Lennep JE, et al. 2025 Focused Update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2025;46(42):4359-4378. DOI: 10.1093/eurheartj/ehaf190. PMID: 40878289"
  - "Visseren FLJ, Mach F, Smulders YM, et al. 2021 ESC Guidelines on cardiovascular disease prevention in clinical practice. Eur Heart J. 2021;42(34):3227-3337. DOI: 10.1093/eurheartj/ehab484. PMID: 34458905"
  - "Yndigegn T, Lindahl B, Mars K, et al. Beta-Blockers after Myocardial Infarction and Preserved Ejection Fraction. N Engl J Med. 2024;390(15):1372-1381. DOI: 10.1056/NEJMoa2401479. PMID: 38587241"
  - "Butler J, Jones WS, Udell JA, et al. Empagliflozin after Acute Myocardial Infarction. N Engl J Med. 2024;390(16):1455-1466. DOI: 10.1056/NEJMoa2314051. PMID: 38587237"
  - "Lincoff AM, Brown-Frandsen K, Colhoun HM, et al. Semaglutide and Cardiovascular Outcomes in Obesity without Diabetes. N Engl J Med. 2023;389(24):2221-2232. DOI: 10.1056/NEJMoa2307563. PMID: 37952131"
---

# Fluxograma: alta após SCA — os cinco pilares modificáveis

A pergunta desta árvore não é “o paciente pode ir embora?”. É: **os cinco pilares modificáveis estão prescritos, datados e explicados, ou a alta está incompleta?** O playbook em prosa está em `prevencao-secundaria-integrada-apos-sindrome-coronariana-aguda`. Aqui entra só a sequência da manhã.

Vacina anual contra influenza (ESC 2023, Classe I, nível A) e teach-back na alta (ESC 2023, Classe IIa, nível B) valem para todos os ramos e ficaram de fora do diagrama de propósito: não ramificam.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente internado por SCA<br/>pronto para alta"] --> D1{"Pilar 1 — DAPT definida<br/>com os dois fármacos, doses<br/>e data de reavaliação?"}

  D1 -->|"Não"| C1(["Completar antes de assinar a alta:<br/>esquema, prazo e data de revisão.<br/>Não desescalar nos primeiros 30 dias<br/>ESC 2023 Classe III B.<br/>Detalhe de 1 vs 3 vs 12 meses:<br/>fluxograma de DAPT — não inventar aqui"])

  D1 -->|"Sim"| D2{"Pilar 2 — estatina de alta intensidade<br/>já na internação, com meta de LDL<br/>escrita no sumário?"}

  D2 -->|"Não"| C2(["Iniciar ou intensificar agora.<br/>ESC/EAS 2025: intensificar na internação<br/>Classe I C se já usava; IIa B estatina<br/>alta + ezetimiba se virgem e a meta<br/>não virá só com estatina.<br/>SBC 2025 dislipidemias: potente em 24 h<br/>Forte Alta. Meta ESC menor 55;<br/>SBC 2025 menor 50 — anotar a régua"])

  D2 -->|"Sim"| D3{"Pilar 3 — FEVE numérica no prontuário<br/>e decisão de IECA/ARNI, BB, MRA<br/>e iSGLT2 tomada — não deixada em branco?"}

  D3 -->|"Não"| C3(["Não alta sem FEVE.<br/>Seguir a subárvore do pilar 3 abaixo"])

  D3 -->|"Sim"| D4{"Pilar 4 — status tabágico registrado<br/>e, se fuma, fármaco iniciado<br/>ainda na internação?"}

  D4 -->|"Fuma e sairia só com conselho"| C4(["Iniciar vareniclina ou TRN combinada<br/>agora, com suporte após a alta.<br/>ESC 2021 Classe I A para cessar.<br/>SBC 2021: não vaporizador Classe III.<br/>Ver fluxograma de cessação"])

  D4 -->|"Não fuma, ou fármaco já iniciado"| D5{"Pilar 5 — reabilitação com data<br/>E diabetes/obesidade tratados<br/>como prevenção secundária,<br/>não como glicosímetro?"}

  D5 -->|"Reabilitação sem data<br/>ou metabolismo ignorado"| C5(["Encaminhar RC estruturada Classe I A<br/>ESC 2021, com contato marcado.<br/>T2DM: iSGLT2 e/ou GLP-1 SBC 2025 I A.<br/>IMC ≥ 27 sem DM: SELECT existe<br/>HR 0,80 — não inventar Classe I"])

  D5 -->|"Os cinco de pé"| C6(["Alta possível.<br/>Teach-back, material escrito,<br/>vacina influenza, retorno com data.<br/>Polipílula SECURE se adesão for o elo frágil<br/>e o esquema couber na composição"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Subárvore do pilar 3 — FEVE e o que não sai por reflexo

```mermaid
flowchart TD
  F0["FEVE da internação índice"] --> F1{"FEVE ≤ 40% ou IC clínica?"}

  F1 -->|"Sim"| C7(["BB com evidência em IC/FE reduzida<br/>AHA/ACC 2023 I A.<br/>IECA ou BRA SBC 2025 SCC I A;<br/>ARNI se ICFEr sintomática ESC 2021 I B.<br/>MRA: ESC 2021 I A na ICFEr;<br/>SBC 2025 IIa A se FEVE ≤ 35%<br/>com DM ou IC em terapia otimizada.<br/>iSGLT2: ESC 2021 I A na ICFEr"])

  F1 -->|"Não"| F2{"FEVE 40–49% sem IC clínica?"}

  F2 -->|"Sim"| C8(["BB: sinal de benefício na IPD 2025<br/>HR 0,75 — não é Classe ESC 2023.<br/>VERIFICAÇÃO HUMANA NECESSÁRIA<br/>antes de transformar em rotina.<br/>iSGLT2 se T2DM, DRC ou ICFEm.<br/>Não usar EMPACT-MI como Classe I"])

  F2 -->|"Não — FEVE ≥ 50%"| F3{"Há angina, hipertensão,<br/>arritmia ou outra indicação de BB?"}

  F3 -->|"Não"| C9(["Não prescrever BB rotineiro prolongado.<br/>REDUCE-AMI HR 0,96 p=0,64.<br/>IECA se diabetes SBC 2025 SCC I A.<br/>iSGLT2 só se T2DM, DRC ou outra indicação<br/>— EMPACT-MI primário neutro"])

  F3 -->|"Sim"| C10(["BB pela indicação que existe,<br/>não pelo infarto isolado.<br/>iSGLT2 e IECA pelas portas<br/>de DM, DRC ou IC — não pelo IAM em si"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C7,C8,C9,C10 conduta;
```

## O que as árvores não mostram

**Anticoagulação oral concomitante sai das duas árvores.** Terapia tripla por dias e dupla (P2Y12 + anticoagulante) depois é algoritmo próprio. Encaixar esse paciente no pilar 1 como se fosse só “DAPT mais curta” é o erro clássico da alta.

**O pilar 1 não decide 1 mês versus 12 meses.** MASTER-DAPT, ULTIMATE-DAPT, NEO-MINDSET e TARGET-FIRST não cabem num losango só. O ramo C1 manda para `fluxograma-duracao-e-desescalonamento-da-dapt-apos-icp`. Converter cada ensaio em prazo único é **VERIFICAÇÃO HUMANA NECESSÁRIA**.

**A meta de LDL tem duas réguas.** ESC/EAS mantém < 55 mg/dL e redução ≥ 50% no muito alto risco. A SBC 2025 de dislipidemias usa < 50 mg/dL (Forte, Alta) e < 40 mg/dL no extremo (Forte, Moderada). C2 obriga a anotar qual régua, não a misturá-las.

**EMPACT-MI não aparece como sim/não de iSGLT2.** Aparece como freio: IAM recente de alto risco para IC, sem IC estabelecida, sem diabetes e sem DRC, **não** ganha classe de iSGLT2 com o primário daquele ensaio (HR 0,90; IC95% 0,76–1,06). Quem já tem ICFEr, T2DM ou DRC entra pelas portas que preexistem.

**SELECT não vira Classe I neste diagrama.** O ensaio (PMID 37952131) randomizou DCV + IMC ≥ 27 sem diabetes e reduziu MACE (HR 0,80; IC95% 0,72–0,90). C5 obriga a não ignorar o IMC. A classe de diretriz para semaglutida 2,4 mg nesse nicho permanece **VERIFICAÇÃO HUMANA NECESSÁRIA**.

**Polipílula do SECURE não substitui pilar 3.** AAS + ramipril + atorvastatina não carregam BB, MRA nem iSGLT2. C6 só a oferece quando adesão é o problema e a composição cabe.

**Instabilidade não resolvida bloqueia reabilitação**, não a alta farmacológica. SBC 2021 SCASSST Classe III, nível A contra reabilitar enquanto a condição de instabilidade não estiver resolvida.

## Cruzamentos que a sequência esconde

O iSGLT2 do pilar 3 (IC) e o do pilar 5 (diabetes) são o mesmo comprimido. Quem tem os dois motivos não leva dois iSGLT2. Quem tem só IMC alto sem DM não leva iSGLT2 “porque SELECT” — SELECT é semaglutida 2,4 mg, outra classe.

IECA do pilar 3 e ramipril da polipílula são o mesmo eixo. Escolher polipílula não é acrescentar um terceiro bloqueio do sistema renina-angiotensina.

Reabilitação (pilar 5) é também o lugar em que se confere se os pilares 1–4 sobreviveram às duas primeiras semanas em casa. A ESC 2026 trata otimização farmacológica como componente do programa, não como assunto de outro setor.

## Documentos para os quais cada ramo despacha

- Pilar 1: `fluxograma-duracao-e-desescalonamento-da-dapt-apos-icp`, `sindrome-coronariana-aguda-duracao-de-dapt-complemento-final`, `posologia-de-antiagregantes-e-anticoagulantes-na-sindrome-coronariana-aguda-esc-2023`, `master-dapt-dapt-abreviada-em-alto-risco-hemorragico`, `ultimate-dapt-ticagrelor-monoterapia-apos-1-mes-acs-pci`
- Pilar 2: `dislipidemia-metas-ldl-estratificacao-risco-esc-eas-2025`, `fluxograma-dislipidemia-meta-de-ldl-e-escalonamento-esc-eas-2025`
- Pilar 3: `reduce-ami-betabloqueador-pos-iam-fe-preservada`, `betabloqueador-pos-iam-evidencia-estratificada-por-feve-40-49-versus-50`, `empact-mi-empagliflozina-pos-iam-alto-risco`
- Pilar 4: `fluxograma-cessacao-do-tabagismo-no-cardiopata-farmacoterapia-e-seguimento`
- Pilar 5: `reabilitacao-cardiaca-e-prescricao-de-exercicio-na-prevencao-secundaria`, `esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia`, `select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes`, `inibidores-de-sglt2-e-protecao-cardiovascular-empa-reg-outcome-e-declare-timi-58`, `polipilula-em-prevencao-secundaria-pos-infarto-o-ensaio-secure`
