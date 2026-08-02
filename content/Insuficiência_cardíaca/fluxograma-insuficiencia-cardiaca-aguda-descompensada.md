---
title: "Insuficiência cardíaca aguda descompensada"
slug: fluxograma-insuficiencia-cardiaca-aguda-descompensada
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "Conduta imediata na suspeita de IC aguda descompensada: classificação por perfil clínico (Nohria-Stevenson) separando quente-úmido de frio-úmido, e a decisão de escalonar a estratégia diurética quando a resposta inicial é inadequada."
review_status: revisado
source_refs: ["Felker GM, Lee KL, Bull DA, et al. Diuretic strategies in patients with acute decompensated heart failure (DOSE-AHF). N Engl J Med. 2011;364(9):797-805. DOI: 10.1056/NEJMoa1005419. PMID: 21366472", "Bart BA, Goldsmith SR, Lee KL, et al. Ultrafiltration in decompensated heart failure with cardiorenal syndrome (CARRESS-HF). N Engl J Med. 2012;367(24):2296-2304. DOI: 10.1056/NEJMoa1210357. PMID: 23131078", "Mullens W, Dauw J, Martens P, et al. Acetazolamide in acute decompensated heart failure with volume overload (ADVOR). N Engl J Med. 2022;387(13):1185-1195. DOI: 10.1056/NEJMoa2203094. PMID: 36027559", "2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726", "2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666", "Cuffe MS, Califf RM, Adams KF Jr, et al; OPTIME-CHF Investigators. Short-term intravenous milrinone for acute exacerbation of chronic heart failure: a randomized controlled trial. JAMA. 2002;287(12):1541-1547. DOI: 10.1001/jama.287.12.1541. PMID: 11911756", "Felker GM, Benza RL, Chandler AB, et al; OPTIME-CHF Investigators. Heart failure etiology and response to milrinone in decompensated heart failure: results from the OPTIME-CHF study. J Am Coll Cardiol. 2003;41(6):997-1003. DOI: 10.1016/S0735-1097(02)02968-6. PMID: 12651048", "Trullàs JC, Morales-Rull JL, Casado J, Carrera-Izquierdo M, Sánchez-Marteles M, Conde-Martel A, et al. Combining loop with thiazide diuretics for decompensated heart failure: the CLOROTIC trial. Eur Heart J. 2023;44(5):411-421. DOI: 10.1093/eurheartj/ehac689. PMID: 36423214", "Nohria A, Tsang SW, Fang JC, Lewis EF, Jarcho JA, Mudge GH, Stevenson LW. Clinical assessment identifies hemodynamic profiles that predict outcomes in patients admitted with heart failure. J Am Coll Cardiol. 2003;41(10):1797-1804. DOI: 10.1016/s0735-1097(03)00309-7. PMID: 12767667"]
---

# Insuficiência cardíaca aguda descompensada

Gatilho: dispneia, congestão (ortopneia, edema, turgência jugular, estertores)
e ganho de peso rápido. Antes de tratar, classifique o perfil clínico
(Nohria-Stevenson) — ele separa quem trata só com diurético de quem pode
precisar de suporte hemodinâmico antes ou junto do diurético. Dentro do ramo
diurético, a pergunta que decide o próximo passo é sempre a mesma: a resposta
ao diurético inicial foi adequada?

## Árvore de decisão

```mermaid
flowchart TD
  R0["Dispneia + congestão<br/>(ortopneia, ganho de peso rápido,<br/>estertores, edema, turgência jugular):<br/>suspeita de IC aguda descompensada"]
  D1{"Perfil clínico (Nohria-Stevenson):<br/>perfusão periférica quente ou fria?"}
  P1["Iniciar diurético de alça<br/>intravenoso em dose adequada:<br/>conduta central deste perfil"]
  D2{"Resposta adequada ao diurético<br/>inicial (diurese/perda de peso<br/>conforme meta)?"}
  C1(["Manter diurético IV, reavaliar peso<br/>e diurese diariamente até euvolemia,<br/>transicionar para via oral na alta"])
  C2(["Resposta inadequada: escalonar a<br/>estratégia diurética (dose/via, depois<br/>associação de segundo agente);<br/>ultrafiltração só se a escalada<br/>farmacológica falhar — ver prosa abaixo"])
  D3{"Choque cardiogênico associado<br/>(hipotensão persistente +<br/>hipoperfusão orgânica)?"}
  C3(["Priorizar suporte hemodinâmico:<br/>vasopressor e avaliação de suporte<br/>circulatório mecânico — seguir o<br/>fluxograma de choque cardiogênico<br/>(estágios SCAI); associar diurético IV<br/>assim que a perfusão permitir"])
  D4{"Resposta adequada ao diurético IV,<br/>associado a inotrópico quando<br/>indicado?"}
  C4(["Manter diurético IV ± inotrópico,<br/>reavaliar peso e diurese diariamente<br/>até euvolemia; cautela com inotrópico<br/>em etiologia isquêmica"])
  C5(["Resposta inadequada: escalonar a<br/>estratégia diurética (dose/via, depois<br/>associação de segundo agente);<br/>ultrafiltração só se a escalada<br/>farmacológica falhar — ver prosa abaixo"])

  R0 --> D1
  D1 -->|"Quente e úmido — perfusão<br/>preservada, congestão predominante"| P1
  P1 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| C2
  D1 -->|"Frio e úmido — hipoperfusão<br/>somada a congestão"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não — baixo débito<br/>sem choque franco"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que se repete em todo ramo, e por isso não está no diagrama

**Reavaliação diária** de peso, balanço hídrico, diurese, função renal e
eletrólitos — em qualquer perfil e em qualquer ponto da árvore, é o que
decide se o paciente segue no mesmo passo ou precisa reclassificar.

**Investigar e tratar o fator precipitante** (síndrome coronariana aguda,
arritmia, infecção, má adesão, crise hipertensiva) em paralelo ao tratamento
da congestão, não depois dele.

**Suporte geral**: oxigênio se saturação baixa, monitorização contínua,
via de administração intravenosa desde a admissão.

## Como escalonar a estratégia diurética quando a resposta é inadequada

A escalada não é um único passo, é uma sequência, na ordem em que a evidência
sustenta:

1. **Otimizar o próprio diurético de alça primeiro** — aumentar a dose e
   considerar infusão contínua antes de acrescentar qualquer outro fármaco. O
   DOSE-AHF (Felker GM et al., 2011, PMID 21366472) não mostrou diferença
   significativa entre bolus e infusão contínua, nem entre dose baixa e dose
   alta (2,5× a dose oral prévia) nos desfechos coprimários — mas a dose alta
   produziu maior diurese, à custa de piora transitória e não significativa da
   creatinina.
2. **Associar um segundo agente** quando o diurético de alça otimizado ainda
   não é suficiente: acetazolamida (ADVOR, Mullens W et al., 2022, PMID
   36027559 — descongestão bem-sucedida em 42,2% vs. 30,5% com placebo, sem
   diferença em morte ou re-hospitalização) ou um tiazídico associado, no
   bloqueio sequencial do néfron (CLOROTIC, Trullàs JC et al., 2023, PMID
   36423214 — mais perda de peso e mais diurese, à custa de piora renal
   significativamente mais frequente: 46,5% vs. 17,2%).
3. **Ultrafiltração como último recurso**, não como alternativa antecipada à
   falta de resposta: o CARRESS-HF (Bart BA et al., 2012, PMID 23131078)
   mostrou que a ultrafiltração foi inferior à terapia farmacológica
   escalonada, com maior piora da função renal e mais eventos adversos
   graves, sem descongestionar melhor.

Os números completos de cada ensaio estão em
`estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada.md` e em
`resistencia-diuretica-na-insuficiencia-cardiaca-aguda-mecanismos-e-bloqueio-sequencial-do-nefron.md`,
nesta mesma pasta — não duplicados aqui.

## Suporte hemodinâmico no perfil frio e úmido

Quando há hipoperfusão associada à congestão, o diurético isolado pode não
ser suficiente ou pode precisar de suporte associado para ser tolerado. Dois
pontos vindos da evidência revisada nesta pasta:

- **Se há choque cardiogênico franco** (hipotensão persistente com
  hipoperfusão orgânica), a prioridade muda para suporte hemodinâmico e
  avaliação de suporte circulatório mecânico — cenário já coberto pelo
  fluxograma de choque cardiogênico (estágios SCAI), que também traz o
  resultado negativo do ECLS-SHOCK para ECMO venoarterial precoce de rotina.
- **Sem choque franco**, o inotrópico pode ser associado ao diurético para
  baixo débito persistente, mas o OPTIME-CHF (Cuffe MS et al., 2002, PMID
  11911756) não sustenta o uso rotineiro de milrinone: sem diferença no
  desfecho primário frente a placebo, e mais hipotensão sustentada e
  arritmia atrial nova. A subanálise por etiologia (Felker GM et al., 2003,
  PMID 12651048) é o que mais pesa na decisão: em cardiomiopatia
  **isquêmica**, milrinone associou-se a pior desfecho (interação
  significativa); em **não isquêmica**, o efeito foi neutro a favorável.

**Escolha e dose exatas de vasopressor/inotrópico** no choque cardiogênico
não são detalhadas aqui — não são o tema do documento-fonte deste
fluxograma. `VERIFICAÇÃO HUMANA NECESSÁRIA` antes de prescrever; consulte o
fluxograma de choque cardiogênico e o documento de suporte inotrópico
(`suporte-inotropico-na-ic-aguda-descompensada-optime-chf-e-o-sinal-na-etiologia-isquemica.md`)
nesta pasta.

## O que este fluxograma não cobre

**Vasodilatadores intravenosos na fase aguda** — não cobertos pelo
documento-fonte da estratégia diurética, que já registra essa lacuna.

**Critério numérico de quando escalar de farmacológico para ultrafiltração**
— a hierarquia (farmacológico antes de mecânico) está estabelecida, o
gatilho exato não.

**Dose exata do algoritmo escalonado de diurético e da hidroclorotiazida do
CLOROTIC** — protocolo completo não lido nas revisões que sustentam este
fluxograma; ver as lacunas já registradas nos documentos de origem.
