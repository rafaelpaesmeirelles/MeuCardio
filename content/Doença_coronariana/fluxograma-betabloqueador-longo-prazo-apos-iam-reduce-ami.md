---
kind: fluxograma
published: true
review_note: Comparados REDUCE-AMI, REBOOT, BETAMI-DANBLOCK e IPD por população, denominador
  e composto; corrigidas inferências de equivalência, indicação e descontinuação quando
  presentes.
review_status: revisado
slug: fluxograma-betabloqueador-longo-prazo-apos-iam-reduce-ami
source_refs:
- Yndigegn T, Lindahl B, Mars K, et al.; REDUCE-AMI Investigators. Beta-Blockers after
  Myocardial Infarction and Preserved Ejection Fraction. N Engl J Med. 2024 Apr 18;390(15):1372-1381.
  DOI 10.1056/NEJMoa2401479. PMID 38587241. NCT03278509.
- Yndigegn T, Lindahl B, Alfredsson J, et al. Design and rationale of randomized evaluation
  of decreased usage of beta-blockers after acute myocardial infarction (REDUCE-AMI).
  Eur Heart J Cardiovasc Pharmacother. 2023 Feb 2;9(2):192-197. DOI 10.1093/ehjcvp/pvac070.
  PMID 36513329. PMCID PMC9892870.
- Silvain J, et al. ABYSS. N Engl J Med. 2024. DOI 10.1056/NEJMoa2404204.
- Choi KH, et al. SMART-DECISION. N Engl J Med. 2026;394:1302-1312. DOI 10.1056/NEJMoa2601005.
- 'Køber L, Adamo M, et al. 2026 ESC Guidelines for the management of heart failure.
  DOI 10.1093/eurheartj/ehag100. PMID 42661420. Tabela: estágio B e disfunção ventricular
  (slides oficiais, p. 32).'
theme: Doença coronariana
title: 'Fluxograma: betabloqueador de longo prazo após IAM — REDUCE-AMI'
---

# Fluxograma: betabloqueador de longo prazo após IAM — REDUCE-AMI

Pergunta desta árvore: **neste paciente após IAM, o REDUCE-AMI informa a decisão de betabloqueador de longo prazo?** Não informa a fase aguda intravenosa. Não inventa classe de recomendação na FE reduzida. Folhas verdes são condutas.

Vacina, estatina, antitrombótico e reabilitação valem para todos os ramos e ficaram fora do diagrama de propósito: não ramificam com o REDUCE-AMI.

## Árvore de decisão

```mermaid
flowchart TD
    R0["Pós-IAM — decisão de betabloqueador<br/>de longo prazo"] --> D1{"Houve angiografia coronária<br/>nesta internação?"}

    D1 -->|"Não"| C1(["REDUCE-AMI não se aplica.<br/>O ensaio exigiu angiografia<br/>e doença obstrutiva.<br/>Não extrapolar.<br/>Decisão individual, fora deste ensaio."])

    D1 -->|"Sim"| D2{"FEVE ≥ 50%?"}

    D2 -->|"Não — FEVE menor que 50%"| C2(["Fora do recorte do REDUCE-AMI.<br/>Avaliar grau de disfunção e indicação de BB.<br/>Não extrapolar o resultado neutro."])

    D2 -->|"Sim"| D3{"Há outra indicação de betabloqueador?<br/>Angina, fibrilação atrial,<br/>hipertensão, arritmia"}

    D3 -->|"Sim"| C3(["Manter ou iniciar betabloqueador<br/>pela indicação que existe,<br/>não pelo infarto isolado.<br/>REDUCE-AMI excluiu quem já tinha<br/>outra indicação."])

    D3 -->|"Não — estável, sem outra indicação"| C4(["REDUCE-AMI: 7,9% vs 8,3%<br/>morte ou novo IAM.<br/>HR 0,96; IC95% 0,79–1,16; P=0,64.<br/>Não mostrou redução com BB de longo prazo.<br/>Discutir preferência.<br/>Não é contraindicação."])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4 conduta;
```

## O que a árvore não mostra

**Fase aguda intravenosa.** A raiz é a decisão **oral de longo prazo**, em paciente já internado. Betabloqueador IV na apresentação, na reperfusão ou no infarto hiperagudo é outra pergunta. O REDUCE-AMI randomizou entre os dias 1 e 7, com metoprolol ou bisoprolol orais. Não extrapolar C4 para o IV.

**FE reduzida não ganha classe neste diagrama.** C2 identifica população não estudada, sem tornar todo valor abaixo de 50% uma indicação automática. Quem precisa de classe e nível deve ir ao documento de insuficiência cardíaca, não a este fluxograma.

**C4 não manda suspender quem já usa e tolera por outro motivo.** O ensaio comparou estratégia de usar versus não usar betabloqueador de longo prazo **nessa população**, após IAM recente com FEVE ≥ 50% e angiografia. Não é um ensaio de descontinuação tardia em coronariopata estável de anos. E não é contraindicação: 7,9% versus 8,3% é resultado **neutro**, não sinal de dano.

**Números que cabem na folha C4, e só esses.** 5.020 pacientes; 95,4% da Suécia; seguimento mediano 3,5 anos (IIQ 2,2–4,7); 199/2.508 (7,9%) versus 208/2.512 (8,3%); HR 0,96; IC95% 0,79–1,16; P = 0,64. Morte 3,9% vs 4,1%; morte CV 1,5% vs 1,3%; IAM 4,5% vs 4,7%; internamento por FA 1,1% vs 1,4%; internamento por IC 0,8% vs 0,9%. Nada além disso entra na árvore.

**Preferência compartilhada.** Quando o ramo cai em C4, a conduta é conversar — ver o documento de comunicação clínica desta tríade — não decretar “proibido” nem “obrigatório”.

## Diretriz vigente
A ESC 2026 de IC recomenda betabloqueador no estágio B com FEVE <50% para reduzir internação por IC ou morte (Classe I, nível B1). Essa recomendação de diretriz deve ser distinguida dos resultados de cada ensaio e da IPD restrita a FEVE ≥50%. Disfunção ventricular assintomática após IAM pode configurar estágio B; ausência de sintomas não exclui essa indicação. Avaliar contraindicações e tolerância.

## Aplicação individual
Angina, FA ou hipertensão só justificam manutenção se houver indicação clínica específica para betabloqueador; o diagnóstico isolado não torna a classe obrigatória. IC com FE preservada tampouco é indicação universal. Esses estudos não devem ser usados para retirar tratamento de disfunção sistólica relevante.

A decisão de não iniciar após IAM recente não equivale à retirada tardia. ABYSS não demonstrou não inferioridade da interrupção para seu composto amplo; SMART-DECISION demonstrou não inferioridade em pacientes estáveis, FEVE ≥40%, sem IC, tratados por pelo menos um ano, para morte, novo IAM ou internação por IC. Populações, desfechos e margens diferem. Reavaliar individualmente; não suspender abruptamente.

## Tudo com Tudo

Doença coronariana · Insuficiência cardíaca · Hipertensão · Arritmias · Fibrilação atrial · Comunicação clínica · Reabilitação cardíaca
