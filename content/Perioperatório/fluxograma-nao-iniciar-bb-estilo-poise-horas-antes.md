---
title: 'Fluxograma: não iniciar BB estilo POISE horas antes'
slug: fluxograma-nao-iniciar-bb-estilo-poise-horas-antes
theme: Perioperatório
kind: fluxograma
review_status: revisado
source_refs:
- POISE Study Group; Devereaux PJ, Yang H, Yusuf S, et al. Effects of extended-release metoprolol succinate in patients undergoing
  non-cardiac surgery (POISE trial). Lancet. 2008;371(9627):1839-1847. DOI 10.1016/S0140-6736(08)60601-7. PMID 18479744. NCT00182039.
- '2024 AHA/ACC perioperative guideline. DOI: 10.1161/CIR.0000000000001285. https://www.ahajournals.org/doi/10.1161/CIR.0000000000001285'
review_note: 'Leitura integral e verificação primária PubMed de POISE, POISE2 AAS/clonidina e VISION; números, populações,
  duração, danos e desenho conferidos. Resolvidas referências ausentes e limites de conduta com AHA/ACC2024/ESC2022 quando
  aplicável; retiradas instruções de produção sem retirar incerteza clínica. Tema canônico e links clinicamente pertinentes
  conferidos: poise-2-aas-nao-reduz-morte-ou-iam, poise-2-clonidina-nao-reduz-iam-e-aumenta-hipotensao, poise-bb-iniciado-horas-antes-nao-e-beneficio-liquido.'
summary: 'Pergunta desta árvore: neste paciente que vai a cirurgia, o POISE autoriza iniciar betabloqueador horas antes da
  incisão? Folhas verdes são condutas. O composto primário caiu; morte e AVC subiram. Continuar um betabloqueador já em uso
  é outra porta — o POISE não testou a suspensão. Esta árvore não atribui Classe I, IIa, IIb ou III.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: não iniciar BB estilo POISE horas antes

Pergunta desta árvore: **neste paciente que vai a cirurgia, o POISE autoriza iniciar betabloqueador horas antes da incisão?** Folhas verdes são condutas. O composto primário caiu; **morte e AVC subiram**. Continuar um betabloqueador **já em uso** é outra porta — o POISE **não** testou a suspensão. Esta árvore **não** atribui Classe I, IIa, IIb ou III. 

Confirmação em série: cirurgia **não cardíaca** **e** virgem de betabloqueador **e** a proposta é o esquema do POISE (início **2–4 h** antes). Só então a folha de não iniciar. Não misturar com o AAS do POISE-2.

## Árvore de decisão

```mermaid
flowchart TD
    R0["Cirurgia prevista — iniciar betabloqueador horas antes?"] --> D1{"Já usa betabloqueador crônico?"}

    D1 -->|"Sim — BB já em uso"| C1(["Continuar o BB crônico é outra porta.<br/>POISE não testou suspender.<br/>Não aplicar o HR 1,33 a quem já usa."])

    D1 -->|"Não — virgem de BB"| D2{"A cirurgia é não cardíaca?"}

    D2 -->|"Não — cirurgia cardíaca"| C2(["POISE não se aplica.<br/>PMID 18479744 randomizou cirurgia não cardíaca.<br/>Não extrapolar morte HR 1,33 nem AVC HR 2,17."])

    D2 -->|"Sim — não cardíaca"| D3{"Pretende iniciar metoprolol<br/>2–4 h antes da incisão,<br/>esquema do POISE?"}

    D3 -->|"Sim — esquema POISE"| C3(["Não iniciar BB de alta carga horas antes.<br/>Morte HR 1,33; AVC HR 2,17.<br/>Não é benefício líquido."])

    D3 -->|"Não"| D4{"Há indicação crônica de BB<br/>fora do perioperatório?<br/>ICFEr, FA, angina"}

    D4 -->|"Sim — outra indicação"| C4(["Essa indicação é outra porta.<br/>Não é o esquema do POISE 2–4 h antes.<br/>Avaliar indicação e tempo para titulação."])

    D4 -->|"Não"| C5(["Não iniciar BB só porque há cirurgia amanhã.<br/>POISE: morte 3,1% vs 2,3% HR 1,33;<br/>AVC 1,0% vs 0,5% HR 2,17."])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5 conduta;
```

## Como ler cada folha

**C1 — já usa betabloqueador crônico.** Continuar é outra porta. O POISE randomizou início **2–4 h** antes, não a suspensão do comprimido da ICFEr, da FA ou da angina. Não copiar o HR **1,33** nem o HR **2,17** para quem já usa. 

**C2 — cirurgia cardíaca.** PMID **18479744**: **8351** pacientes, cirurgia **não cardíaca**, 190 hospitais, 23 países. Metoprolol succinato de liberação prolongada **4174** versus placebo **4177**. 

**C3 — o colega quer o esquema do POISE.** Início **2–4 h** antes, até **30** dias. Primário (morte CV, IAM não fatal ou parada cardíaca não fatal): **244 (5,8%)** vs **290 (6,9%)**; **HR 0,84** (0,70–0,99); P=0,0399. IAM: **176 (4,2%)** vs **239 (5,7%)**; HR **0,73** (0,60–0,89); P=0,0017. **Morte**: **129 (3,1%)** vs **97 (2,3%)**; **HR 1,33** (1,03–1,74); P=0,0317. **AVC**: **41 (1,0%)** vs **19 (0,5%)**; **HR 2,17** (1,26–3,74); P=0,0053. O composto melhorou porque o IAM caiu. Morte e AVC **subiram**. Não cite o 0,84 sem o 1,33 e o 2,17. Não iniciar.

**C4 — indicação crônica que ainda não estava em uso.** ICFEr, FA com controle de frequência, angina: outra porta, outro ensaio, outra ficha. Não é “começar 2–4 h antes para proteger o coração da cirurgia”. 

**C5 — sem indicação crônica e sem esquema POISE.** Folha irmã de C3: não iniciar betabloqueador só porque a lista cirúrgica existe. Frequências naturais em 30 dias: morte em **3 em 100** com o esquema do POISE e em **2 em 100** com placebo. AVC em **1 em 100** vs **0,5 em 100**. **8331 (99,8%)** completaram o seguimento de 30 dias.


## Aplicação atual

A [AHA/ACC 2024](https://www.ahajournals.org/doi/10.1161/CIR.0000000000001285) orienta manter o betabloqueador crônico quando apropriado. Uma nova indicação em cirurgia eletiva deve ser avaliada com antecedência, idealmente mais de sete dias, permitindo titulação e avaliação de tolerância. Sem necessidade imediata, não iniciar no próprio dia da cirurgia. Instabilidade, hipotensão e bradicardia exigem avaliação individual.

## Tudo com Tudo

- [POISE-2: AAS perioperatório não reduz morte ou IAM — aumenta sangramento](/biblioteca/poise-2-aas-nao-reduz-morte-ou-iam)
- [POISE-2 clonidina: não reduz IAM — aumenta hipotensão e parada](/biblioteca/poise-2-clonidina-nao-reduz-iam-e-aumenta-hipotensao)
- [POISE: betabloqueador iniciado horas antes — não é benefício líquido](/biblioteca/poise-bb-iniciado-horas-antes-nao-e-beneficio-liquido)
