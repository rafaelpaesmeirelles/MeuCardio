---
title: "Fluxograma: angina vasoespástica — da suspeita clínica ao teste provocativo e ao tratamento do espasmo epicárdico"
slug: fluxograma-angina-vasoespastica-teste-provocativo-e-tratamento
theme: "Doença coronariana"
kind: fluxograma
summary: "Árvore da angina de repouso (noturna/madrugada) até o endótipo: exclui SCA, cocaína e fluoropirimidina; aplica COVADIS (definitiva vs. suspeita); lê o teste de acetilcolina (>90% + dor + ECG = epicárdico; dor + ECG sem >90% = microvascular) e dirige antagonista de cálcio só no ramo epicárdico."
review_status: pendente_revisao
source_refs:
  - "Beltrame JF, Crea F, Kaski JC, Ogawa H, Ong P, Sechtem U, Shimokawa H, Bairey Merz CN; Coronary Vasomotor Disorders International Study Group (COVADIS). International standardization of diagnostic criteria for vasospastic angina. Eur Heart J. 2017;38(33):2565-2568. DOI: 10.1093/eurheartj/ehv351. PMID: 26245334. Consenso."
  - "Ong P, Camici PG, Beltrame JF, Crea F, Shimokawa H, Sechtem U, Kaski JC, Bairey Merz CN; Coronary Vasomotor Disorders International Study Group (COVADIS). International standardization of diagnostic criteria for microvascular angina. Int J Cardiol. 2018;250:16-20. DOI: 10.1016/j.ijcard.2017.08.068. PMID: 29031990. Consenso — ramo microvascular da árvore."
  - "Vrints C, Andreotti F, Koskinas KC, et al.; ESC Scientific Document Group. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45(36):3415-3537. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710. Diretriz. Classe I Nível B da CFT conferida; classe do antagonista de cálcio no endótipo vasoespástico não conferida no PDF integral nesta sessão."
  - "Byrne RA, Rossello X, Coughlan JJ, et al.; ESC Scientific Document Group. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654. Diretriz — só o desvio para SCA/MINOCA."
  - "Ong P, Athanasiadis A, Borgulya G, Mahrholdt H, Kaski JC, Sechtem U. The ACOVA Study. J Am Coll Cardiol. 2012;59(7):655-662. DOI: 10.1016/j.jacc.2011.11.015. PMID: 22322081. Coorte — prevalência, não corte de 2017."
review_note: "PMIDs 26245334, 29031990, 39210710, 37622654 e 22322081 conferidos nesta sessão via PubMed. A árvore aplica os critérios COVADIS (consenso) e a Classe I Nível B da CFT (diretriz ESC 2024). Não atribui Classe/Nível a CCB, nitrato, betabloqueador nem à janela de 48 h de suspensão pré-teste. O ramo 'CCB empírico enquanto se organiza a CFT' é síntese clínica, não linha numerada da ESC — marcado em 'O que a árvore não mostra'. Não duplica o fluxograma geral de SCC nem o de MINOCA."
---

# Fluxograma: angina vasoespástica — teste provocativo e tratamento

Esta árvore começa **depois** de a via de síndrome coronariana crônica ter afastado (ou a angiografia já ter mostrado) obstrução que explique o sintoma — ou quando o fenótipo é tão típico (angina de repouso noturna, ST transitório, resposta a nitrato) que a hipótese de espasmo epicárdico precisa ser nomeada de propósito.

Não é o fluxograma de ANOCA/INOCA inteiro. Só o ramo **espasmo epicárdico**. Cocaína, fluoropirimidina, MINOCA e disfunção microvascular estrutural saem em desvios explícitos.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto com angina de repouso<br/>(sobretudo noturna ou de madrugada)<br/>ou variação diurna marcada da tolerância ao esforço"] --> D1{"Dor em curso, supra persistente<br/>ou troponina com curva — SCA?"}

  D1 -->|"Sim"| C1(["Sair: fluxograma de SCA.<br/>Se angiografia sem obstrução, via MINOCA<br/>(não provocar espasmo na fase instável)"])

  D1 -->|"Não"| D2{"Exposição atual a cocaína<br/>ou a fluoropirimidina (5-FU/capecitabina)?"}

  D2 -->|"Sim"| C2(["Sair: protocolos próprios<br/>(cocaína; 5-FU/capecitabina).<br/>Não tratar como VSA primária"])

  D2 -->|"Não"| P1["ECG de 12 derivações, nitrato de ação curta se houver dor,<br/>identificar gatilhos (tabagismo). Tentar capturar ECG no episódio"]

  P1 --> D3{"Episódio espontâneo documentado:<br/>angina que cede com nitrato E alteração isquêmica<br/>transitória em ≥2 derivações contíguas<br/>(ST ≥0,1 mV para cima ou para baixo, ou U negativa nova)?"}

  D3 -->|"Sim"| C3(["VSA definitiva pelos critérios clínicos COVADIS<br/>(elemento 1 + elemento 2).<br/>Iniciar antagonista de cálcio e cessar tabagismo.<br/>CFT ainda útil para documentar o vaso e o endótipo"])

  D3 -->|"Não — ECG não capturado<br/>ou equívoco"| D4{"Angiografia já mostrou ausência de obstrução<br/>que explique o sintoma?"}

  D4 -->|"Não"| C4(["Seguir o fluxograma de SCC (ESC 2024).<br/>Se a anatomia vier sem obstrução, voltar a este ponto"])

  D4 -->|"Sim — ANOCA com fenótipo espástico"| D5{"CFT disponível no mesmo procedimento<br/>ou em centro de referência?<br/>Classe I, Nível B (ESC 2024)"}

  D5 -->|"Não neste momento"| C5(["Encaminhar para CFT.<br/>Se a suspeita clínica de VSA for alta,<br/>antagonista de cálcio enquanto se organiza o exame<br/>(síntese — classe específica: verificação humana)"])

  D5 -->|"Sim"| P2["Teste provocativo com acetilcolina<br/>(ou ergot, conforme o centro),<br/>nitrato intracoronariano já na mesa"]

  P2 --> D6{"Os três critérios COVADIS do teste<br/>estão presentes no mesmo momento?<br/>dor habitual + ECG isquêmico + constrição epicárdica >90%"}

  D6 -->|"Sim, os três"| C6(["Espasmo EPICÁRDICO.<br/>Antagonista de cálcio como base<br/>(doses frequentemente altas nos casos graves).<br/>Nitrato de ação curta no episódio; longa ação se persistir.<br/>Cessar tabagismo. Não iniciar betabloqueador<br/>como antianginoso deste endótipo"])

  D6 -->|"Dor + ECG, sem constrição >90%"| C7(["Espasmo MICROVASCULAR — outro endótipo.<br/>Sair para o protocolo ANOCA/INOCA.<br/>Não rotular como VSA clássica nem tratar só com mais cálcio"])

  D6 -->|"Negativo"| C8(["Mecanismo espástico não reproduzido neste teste.<br/>Completar CFR/IMR (CMD estrutural),<br/>considerar ponte miocárdica e causa não coronariana"])

  C6 --> D7{"Sintoma controlado com antagonista de cálcio<br/>e cessação do tabagismo?"}

  D7 -->|"Sim"| C9(["Manter a terapia. Reavaliar gatilhos.<br/>Não stentear vaso que só espasma"])

  D7 -->|"Não"| C10(["Conferir adesão e dose (casos graves exigem dose mais alta).<br/>Acrescentar nitrato de longa ação.<br/>Recorrência grave: reavaliar endótipo e centro experiente"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10 conduta;
```

## Como ler cada desvio

**C1 — SCA primeiro.** Supra persistente não é “Prinzmetal até prova em contrário”. É oclusão até a angiografia dizer o contrário. O espasmo entra depois, como causa possível de MINOCA, no fluxograma próprio.

**C2 — tóxico-induzido não é VSA primária.** Cocaína e fluoropirimidina têm mecanismo, tempo de reexposição e conduta diferentes. Misturar os três no mesmo ramo ensina o erro.

**C3 — dá para diagnosticar sem cateterismo.** COVADIS aceita VSA definitiva com angina nitrato-responsiva **mais** ECG isquêmico espontâneo, sem exigir o critério 3. A CFT continua útil, mas não é o que autoriza começar o antagonista de cálcio.

**C5 — o empirismo tem preço.** Começar cálcio na suspeita alta enquanto a CFT não está disponível é síntese clínica, não linha Classe I lida na ESC 2024. Se o endótipo real for microvascular estrutural, o cálcio isolado pode não ser a melhor primeira escolha. Por isso o encaminhamento para CFT permanece o alvo (Classe I B).

**C6 versus C7 — o corte de 90%.** Os três critérios juntos definem epicárdico. Dor + ECG sem constrição > 90% é microvascular. Relatar o percentual; não copiar o ≥ 75% do ACOVA (2012), que é pré-COVADIS.

**C8 — teste negativo não é alta com “ansiedade”.** A metade adenosina da CFT (CFR/IMR) ainda não foi lida nesse ramo. Ponte miocárdica também causa angina com artéria “livre” na diástole.

## O que a árvore não mostra

**Protocolo miligrama a miligrama de acetilcolina.** Varia entre centros (Japão versus Europa, dose máxima na DA versus circunflexa/direita). Não cabe em bifurcação binária e não foi lido como tabela ESC 2024. **VERIFICAÇÃO HUMANA NECESSÁRIA** para protocolar dose institucional.

**Janela de 48 horas sem nitrato/cálcio antes do teste.** Prática de laboratório para reduzir falso-negativo; não conferida como recomendação classificada da ESC 2024.

**Contraindicações absolutas do teste.** Listas japonesas e de revisões especializadas existem (tronco não tratado, disfunção ventricular grave, gestação, SCA instável). Não reproduzir como se fossem da ESC 2024 sem conferir o PDF. **VERIFICAÇÃO HUMANA NECESSÁRIA.**

**Classe e nível do antagonista de cálcio, do nitrato e da “proibição” de betabloqueador.** O texto da ESC 2024 aponta o cálcio como primeira linha do endótipo vasoespástico; COVADIS usa a resposta diferencial cálcio versus betabloqueador como critério diagnóstico. Nenhuma das duas frases foi lida aqui como Classe I ou Classe III numerada. A árvore trata o cálcio como base **sem** inventar classe.

**CDI após parada atribuída a espasmo, nicorandil, dose-alvo de diltiazem/verapamil.** Fora do recorte. Não fechar.

**Sexo.** Coortes posteriores ao ACOVA sugerem mais espasmo epicárdico em homens e mais microvascular em mulheres — epidemiologia, não bifurcação da árvore. A leitura do teste é a mesma.

## Tudo com Tudo

- [Protocolo: angina vasoespástica — critérios COVADIS, diagnóstico e tratamento](angina-vasoespastica-criterios-covadis-diagnostico-e-tratamento.md)
- [ANOCA/INOCA — protocolo geral ESC 2024](anoca-inoca-angina-e-isquemia-sem-obstrucao-coronariana-esc-2024.md)
- [Fluxograma de síndrome coronariana crônica — ESC 2024](fluxograma-sindrome-coronariana-cronica-esc-2024.md)
- [Fluxograma MINOCA](fluxograma-minoca-investigacao-diagnostica.md)
- [MINOCA e SCAD](minoca-e-scad-infarto-sem-doenca-coronariana-obstrutiva-e-dissecção-espontânea.md)
- [Disfunção microvascular e CorMicA](../Farmacologia/disfuncao-microvascular-coronariana-angina-microvascular-diagnostico-funcional-e-tratamento-guiado.md)
- [Cocaína](../Geral/cocaina-e-risco-cardiovascular-vasoespasmo-coronariano-e-infarto.md)
- [Fluoropirimidinas](../Cardio-oncologia/sindrome-coronariana-aguda-e-vasoespasmo-por-fluoropirimidinas-5fu-capecitabina.md)
