---
title: "Fluxograma: próxima camada diurética após o diurético de alça — ADVOR ou CLOROTIC"
slug: fluxograma-proxima-camada-diuretica-apos-alca-advor-clorotic
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: grok
review_status: pendente_revisao
review_note: "Árvore estrita da camada depois da alça já otimizada: portas de NÃO associar, escolha entre acetazolamida IV (ADVOR) e hidroclorotiazida oral (CLOROTIC), parada na euvolemia. Não substitui o fluxograma amplo de resistência (que inclui ultrafiltração) nem o de sódio urinário. Números citados nas folhas vêm dos abstracts MEDLINE PMID 36027559 e 36423214 lidos nesta sessão. Classe IIa B1 extraída da Recommendation Table 9 da ESC 2026 (DOI 10.1093/eurheartj/ehag100); PDF 403. Sem corte numérico inventado de débito urinário."
source_refs:
  - "Mullens W, Dauw J, Martens P, et al.; ADVOR Study Group. Acetazolamide in Acute Decompensated Heart Failure with Volume Overload. N Engl J Med. 2022;387(13):1185-1195. DOI: 10.1056/NEJMoa2203094. PMID: 36027559. Abstract MEDLINE lido via E-utilities nesta sessão."
  - "Trullàs JC, Morales-Rull JL, Casado J, et al.; CLOROTIC trial investigators. Combining loop with thiazide diuretics for decompensated heart failure: the CLOROTIC trial. Eur Heart J. 2023;44(5):411-421. DOI: 10.1093/eurheartj/ehac689. PMID: 36423214. Abstract MEDLINE lido via E-utilities nesta sessão."
  - "European Society of Cardiology. 2026 ESC Guidelines for the management of heart failure. Eur Heart J. 2026. DOI: 10.1093/eurheartj/ehag100. Recommendation Table 9 extraída da página oficial nesta sessão."
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992."
legacy_source: "Fluxograma novo, 29/08/2026. Zoom de um único nó que o fluxograma-resistencia-diuretica-e-congestao-refrataria-na-ic-aguda.md trata como escolha binária acetazolamida vs. tiazídico, sem as portas de segurança nem o que cada ensaio autoriza a prometer. Não reescreve aquela árvore, nem a de IC aguda descompensada, nem a de sódio urinário."
---

# Fluxograma: próxima camada diurética após o diurético de alça

Aplica-se ao adulto internado por IC descompensada (vocabulário ESC 2026) **já em diurético de alça IV**, com congestão que não cedeu. Não começa na admissão. Não escolhe bolus versus infusão. Não mede o sódio urinário — se o serviço usa esse gatilho, o protocolo é `natriurese-guiada-por-sodio-urinario-na-descongestao-da-ic-aguda-push-ahf-e-enact-hf.md`. A prosa desta decisão está em `acetazolamida-e-tiazidico-na-resistencia-diuretica-advor-e-clorotic.md`. Se a segunda camada falhar, o resgate (incluindo ultrafiltração) volta para `fluxograma-resistencia-diuretica-e-congestao-refrataria-na-ic-aguda.md`.

A ESC 2026 (Recommendation Table 9, extraída da página oficial): acetazolamida IV **ou** hidroclorotiazida oral de **curto prazo** **devem ser consideradas** na sobrecarga previamente tratada com alça, para reduzir congestão — **IIa B1**. Não é Classe I. Não é redução de morte.

Não há corte numérico validado, nestes dois ensaios, de débito urinário ou de quilos para declarar “resposta inadequada à alça”. Os nós abaixo são qualitativos de propósito. Não inventar um gatilho que o abstract não traz.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Congestão residual sob diurético<br/>de alça IV na IC descompensada"]
  D1{"A alça já está em dose e via<br/>otimizadas?"}
  C1(["Não abrir a segunda camada:<br/>otimizar primeiro a própria alça.<br/>Ver estrategia-diuretica-...<br/>e o fluxograma de IC aguda"])
  D2{"Há hipoperfusão ou choque<br/>(pele fria, hipotensão que<br/>não sustenta órgão, SCAI)?"}
  C2(["Priorizar suporte hemodinâmico.<br/>Segundo diurético não trata baixo débito.<br/>Ver fluxograma de perfis hemodinâmicos"])
  D3{"Ainda há sobrecarga objetiva<br/>(edema, turgência, estertores,<br/>derrame, ascite, ganho de peso)?"}
  C3(["Não associar segundo diurético:<br/>já euvolêmico. Seguir para alta<br/>e titulação — ver ic-descompensada-esc-2026-..."])
  D4{"Dá para dosar K e creatinina<br/>amanhã e enquanto a associação durar?"}
  C4(["Não associar. Sem malha de K/creatinina<br/>a segunda camada deixa de ser ensaio.<br/>Reavaliar via, precipitante e resgate<br/>no fluxograma de resistência"])
  D5{"Hipocalemia não corrigida agora?"}
  C5(["Repor K antes. Não iniciar HCTZ<br/>com K baixo. Reavaliar a árvore<br/>depois da correção"])
  D6{"Qual segundo diurético — um só,<br/>curto prazo, sobre a alça que continua?"}
  C6(["Acetazolamida IV 500 mg 1×/dia<br/>até 3 dias ou até descongestão<br/>(ADVOR: 42,2% vs. 30,5%; RR 1,46).<br/>Não prometer mortalidade:<br/>morte ou re-hosp. IC 29,7% vs. 27,8%; HR 1,07"])
  C7(["Hidroclorotiazida oral, não clortalidona<br/>(CLOROTIC: −2,3 vs. −1,5 kg em 72 h;<br/>dispneia p=0,497; piora renal<br/>46,5% vs. 17,2%). Dose por TFGe:<br/>nota da Figura 15 ESC 2026 — conferir PDF"])
  C8(["Não empilhar as duas moléculas<br/>como rotina: cada ensaio testou<br/>um add-on, não os dois juntos"])
  D7{"Descongestão clínica atingida<br/>sem necessidade de escalar mais?"}
  C9(["Parar o segundo diurético na euvolemia.<br/>Manter alça na dose da euvolemia.<br/>Não levar o esquema de ensaio para casa<br/>sem plano de monitorização"])
  C10(["Segunda camada falhou: voltar ao<br/>fluxograma de resistência — resgate<br/>farmacológico restante ou ultrafiltração<br/>depois da falha, não antes"])

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Não — euvolêmico"| C3
  D3 -->|"Sim — ainda congesto"| D4
  D4 -->|"Não"| C4
  D4 -->|"Sim"| D5
  D5 -->|"Sim — K baixo sem reposição"| C5
  D5 -->|"Não — K corrigido ou reposição já em curso"| D6
  D6 -->|"Acetazolamida — primário de descongestão,<br/>segurança renal/K semelhante no abstract"| C6
  D6 -->|"HCTZ — primário de peso, mais piora renal"| C7
  D6 -->|"Tentação de somar as duas"| C8
  C6 --> D7
  C7 --> D7
  D7 -->|"Sim"| C9
  D7 -->|"Não"| C10

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10 conduta;
```

## Como ler as duas folhas de escolha

**Acetazolamida (ADVOR, PMID 36027559).** N=519 randomizados. Primário: ausência de sinais de sobrecarga em 3 dias sem escalonar. 108/256 (42,2%) vs. 79/259 (30,5%); RR 1,46 (IC95% 1,17–1,82; p<0,001). Morte ou re-hospitalização por IC em 3 meses: 29,7% vs. 27,8%; HR 1,07 (IC95% 0,78–1,48) — **não** usar descongestão como mortalidade. Abstract: piora renal, hipocalemia, hipotensão e eventos **semelhantes** (sem porcentagem). Dose no abstract: **500 mg IV 1×/dia** sobre alça equivalente ao dobro da manutenção oral. FEVE ≤40% ou >40% — o ensaio não é só ICFEr.

**Hidroclorotiazida (CLOROTIC, PMID 36423214).** N=230. Coprimários em 72 h: peso venceu (2,3 vs. 1,5 kg; diferença ajustada 1,14 kg; p=0,002); dispneia **não** (AUC 960 vs. 720; p=0,497). Diurese 24 h: 1775 vs. 1400 mL (p=0,05). Piora renal (↑ creatinina 26,5 µmol/L ou ↓ eGFR 50%): **46,5% vs. 17,2%** (p=0,001). Mortalidade/reinternação: sem diferença. O XML MEDLINE corrompe a frase de hipocalemia; a ESC 2026 descreve mais hipocalemia com HCTZ e pede cautela. **Não** substituir HCTZ por clortalidona nesta folha.

**Classe da diretriz.** IIa B1 para **reduzir congestão**, curto prazo, depois de alça. A folha C6/C7 é “considerar”, não “obrigatório em todo congesto”.

## O que esta árvore recusa fazer

- Inventar um número de diurese ou de sódio urinário como porta de entrada — o corte de 70 mmol/L pertence ao PUSH-AHF, outro documento.
- Tratar clortalidona, metolazona ou clorotiazida IV como o braço do CLOROTIC.
- Empilhar acetazolamida + HCTZ porque “os dois ensaios foram positivos”.
- Levar o segundo diurético para o domicílio no esquema do ensaio sem malha de K e creatinina.
- Pular para ultrafiltração **antes** de tentar a camada farmacológica — isso é o CARRESS-HF no fluxograma de resistência, não nesta árvore.

## Relação com o acervo

- Prosa desta decisão: `acetazolamida-e-tiazidico-na-resistencia-diuretica-advor-e-clorotic.md`
- Mecanismos e texto integral do CLOROTIC já revisado: `resistencia-diuretica-na-insuficiencia-cardiaca-aguda-mecanismos-e-bloqueio-sequencial-do-nefron.md`
- Resistência completa, incluindo ultrafiltração: `fluxograma-resistencia-diuretica-e-congestao-refrataria-na-ic-aguda.md`
- Sódio urinário: `natriurese-guiada-por-sodio-urinario-na-descongestao-da-ic-aguda-push-ahf-e-enact-hf.md`
- Depois da euvolemia: `ic-descompensada-esc-2026-e-titulacao-pos-alta.md`
