---
title: "Insuficiência cardíaca aguda descompensada"
slug: fluxograma-insuficiencia-cardiaca-aguda-descompensada
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "Conduta imediata na IC aguda congestiva: separar perfusão preservada, hipoperfusão sem choque e choque; medir resposta precoce ao diurético de alça, dobrar a dose quando insuficiente e só então avançar para bloqueio sequencial, sem inotrópico automático no perfil frio."
review_status: revisado
source_refs: ["Felker GM, Lee KL, Bull DA, et al. Diuretic strategies in patients with acute decompensated heart failure (DOSE-AHF). N Engl J Med. 2011;364(9):797-805. DOI: 10.1056/NEJMoa1005419. PMID: 21366472", "Bart BA, Goldsmith SR, Lee KL, et al. Ultrafiltration in decompensated heart failure with cardiorenal syndrome (CARRESS-HF). N Engl J Med. 2012;367(24):2296-2304. DOI: 10.1056/NEJMoa1210357. PMID: 23131078", "Mullens W, Dauw J, Martens P, et al. Acetazolamide in acute decompensated heart failure with volume overload (ADVOR). N Engl J Med. 2022;387(13):1185-1195. DOI: 10.1056/NEJMoa2203094. PMID: 36027559", "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992", "2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666", "Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. Circulation. 2022;145(18):e895-e1032. DOI: 10.1161/CIR.0000000000001063. PMID: 35363499", "Hollenberg SM, Warner Stevenson L, Ahmad T, et al. 2024 ACC Expert Consensus Decision Pathway on Clinical Assessment, Management, and Trajectory of Patients Hospitalized With Heart Failure. J Am Coll Cardiol. 2024. DOI: 10.1016/j.jacc.2024.06.002", "Cuffe MS, Califf RM, Adams KF Jr, et al; OPTIME-CHF Investigators. Short-term intravenous milrinone for acute exacerbation of chronic heart failure: a randomized controlled trial. JAMA. 2002;287(12):1541-1547. DOI: 10.1001/jama.287.12.1541. PMID: 11911756", "Felker GM, Benza RL, Chandler AB, et al; OPTIME-CHF Investigators. Heart failure etiology and response to milrinone in decompensated heart failure: results from the OPTIME-CHF study. J Am Coll Cardiol. 2003;41(6):997-1003. DOI: 10.1016/S0735-1097(02)02968-6. PMID: 12651048", "Trullàs JC, Morales-Rull JL, Casado J, Carrera-Izquierdo M, Sánchez-Marteles M, Conde-Martel A, et al. Combining loop with thiazide diuretics for decompensated heart failure: the CLOROTIC trial. Eur Heart J. 2023;44(5):411-421. DOI: 10.1093/eurheartj/ehac689. PMID: 36423214", "Nohria A, Tsang SW, Fang JC, Lewis EF, Jarcho JA, Mudge GH, Stevenson LW. Clinical assessment identifies hemodynamic profiles that predict outcomes in patients admitted with heart failure. J Am Coll Cardiol. 2003;41(10):1797-1804. DOI: 10.1016/s0735-1097(03)00309-7. PMID: 12767667"]
review_note: "Revisão de 26/08/2026: removido o último marcador humano de fluxogramas após confronto com ESC 2021, AHA/ACC/HFSA 2022 e ACC 2024. A resposta ao diurético deixou de depender de peso diário e passou a incluir diurese horária e sódio urinário precoce; a sequência foi corrigida para dobrar/reavaliar o diurético de alça antes do bloqueio sequencial, sem exigir infusão contínua. No perfil frio e úmido, inotrópico não é automático: ESC o desaconselha rotineiramente, exceto com hipotensão sintomática e hipoperfusão; no choque, AHA/ACC/HFSA recomenda suporte inotrópico para preservar perfusão. Doses de vasopressor/inotrópico permanecem fora deste fluxo e são remetidas ao documento específico, sem pendência humana."
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
  D2{"Resposta precoce adequada?<br/>Na urinária >50-70 mEq/L em 2 h<br/>ou diurese >100-150 mL/h nas primeiras 6 h"}
  C1(["Manter diurético IV até resolver<br/>congestão; revisar diariamente peso,<br/>exame, balanço, função renal e eletrólitos;<br/>planejar dose oral antes da alta"])
  C2(["Dobrar a dose IV do diurético de alça<br/>e medir novamente a resposta precoce"])
  D5{"Resposta continua inadequada<br/>após otimizar o diurético de alça?"}
  C5(["Adicionar segundo diurético em outro<br/>segmento do néfron, como acetazolamida<br/>ou tiazídico; monitorar Na, K e função renal"])
  D6{"Congestão permanece refratária<br/>à estratégia farmacológica escalonada?"}
  C6(["Reavaliar diagnóstico/hemodinâmica;<br/>ultrafiltração apenas em caso selecionado,<br/>não como substituto precoce do diurético"])
  D3{"Choque cardiogênico associado<br/>(hipotensão persistente +<br/>hipoperfusão orgânica)?"}
  C3(["Usar suporte inotrópico para manter<br/>perfusão; vasopressor conforme pressão<br/>e equipe de choque/MCS; iniciar ou retomar<br/>descongestão quando a perfusão permitir"])
  D4{"Sem choque: há hipotensão sintomática<br/>e evidência objetiva de hipoperfusão?"}
  C4(["Inotrópico de curto prazo pode ser<br/>considerado sob especialista; reavaliar<br/>continuamente e retirar quando possível"])
  C7(["Não usar inotrópico de rotina:<br/>rever diagnóstico/hemodinâmica e fazer<br/>descongestão cautelosa com resposta precoce"])

  R0 --> D1
  D1 -->|"Quente e úmido — perfusão<br/>preservada, congestão predominante"| P1
  P1 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| C2
  C2 --> D5
  D5 -->|"Não — respondeu"| C1
  D5 -->|"Sim"| C5
  C5 --> D6
  D6 -->|"Não — respondeu"| C1
  D6 -->|"Sim"| C6
  D1 -->|"Frio e úmido — hipoperfusão<br/>somada a congestão"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| C7
  C3 --> P1
  C4 --> P1
  C7 --> P1

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que se repete em todo ramo, e por isso não está no diagrama

**Reavaliação precoce e diária.** Nas primeiras horas, diurese e sódio urinário
identificam rapidamente resposta insuficiente; depois, peso, exame de congestão,
balanço, função renal e eletrólitos mostram a trajetória até a euvolemia.

**Investigar e tratar o fator precipitante** (síndrome coronariana aguda,
arritmia, infecção, má adesão, crise hipertensiva) em paralelo ao tratamento
da congestão, não depois dele.

**Suporte geral**: oxigênio quando há hipoxemia (ESC: SpO2 <90% ou PaO2
<60 mmHg), monitorização proporcional à gravidade e tratamento simultâneo do
fator precipitante.

## Como escalonar a estratégia diurética quando a resposta é inadequada

A escalada não é um único passo, é uma sequência, na ordem em que a evidência
sustenta:

1. **Medir cedo e otimizar o diurético de alça primeiro.** A ESC propõe como
   resposta satisfatória sódio urinário >50-70 mEq/L em 2 horas e/ou diurese
   >100-150 mL/h nas primeiras 6 horas. Se insuficiente, dobrar a dose IV e
   medir novamente. O DOSE-AHF (PMID 21366472) não mostrou superioridade de
   infusão contínua sobre bolus; por isso, infusão não é degrau obrigatório
   antes de associar outro fármaco.
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
- **Sem choque franco**, “frio e úmido” não autoriza inotrópico por si só. A
  ESC desaconselha uso rotineiro, exceto quando coexistem hipotensão sintomática
  e hipoperfusão. O OPTIME-CHF (PMID 11911756) reforça a cautela: milrinone de
  rotina não melhorou o desfecho primário e aumentou hipotensão sustentada e
  arritmia atrial nova. Na subanálise (PMID 12651048), a etiologia isquêmica
  apresentou sinal de pior desfecho.

**Escolha e dose exatas de vasopressor/inotrópico** não são detalhadas aqui.
AHA/ACC/HFSA recomenda suporte inotrópico no choque para manter perfusão e
preservar órgãos, mas não demonstra superioridade robusta de um agente. Pressão,
arritmias, etiologia e disponibilidade orientam a escolha. Consulte o fluxo de
choque cardiogênico e o documento específico de suporte inotrópico ligados
abaixo; este fluxograma não deve ser usado como prescrição.

## O que este fluxograma não cobre

**Vasodilatadores intravenosos na fase aguda** — não cobertos pelo
documento-fonte da estratégia diurética, que já registra essa lacuna.

**Critério numérico de quando escalar de farmacológico para ultrafiltração**
— a hierarquia (farmacológico antes de mecânico) está estabelecida, o
gatilho exato não.

**Doses completas dos esquemas de diurético e da hidroclorotiazida do
CLOROTIC** — ficam no protocolo farmacológico/institucional; este fluxo define
a sequência e os critérios de resposta, não substitui prescrição.

## Tudo com Tudo

- [Estratégia diurética na IC aguda descompensada](estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada.md)
- [Fluxograma de resistência diurética e congestão refratária](fluxograma-resistencia-diuretica-e-congestao-refrataria-na-ic-aguda.md)
- [Resistência diurética e bloqueio sequencial do néfron](resistencia-diuretica-na-insuficiencia-cardiaca-aguda-mecanismos-e-bloqueio-sequencial-do-nefron.md)
- [Suporte inotrópico na IC aguda e OPTIME-CHF](suporte-inotropico-na-ic-aguda-descompensada-optime-chf-e-o-sinal-na-etiologia-isquemica.md)
- [Fluxograma de choque cardiogênico — estágios SCAI](../Terapia_intensiva/fluxograma-choque-cardiogenico-estagios-scai.md)
