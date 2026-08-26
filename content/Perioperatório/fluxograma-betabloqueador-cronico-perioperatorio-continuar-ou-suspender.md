---
title: "Fluxograma: betabloqueador crônico no perioperatório — continuar ou suspender"
slug: fluxograma-betabloqueador-cronico-perioperatorio-continuar-ou-suspender
theme: "Perioperatório"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primária conferida via PubMed E-utilities (esearch/esummary/efetch) para os quatro PMIDs citados, incluindo leitura do abstract completo da metanálise de 2024 (PMID 39584914) via PMC (PMCID PMC11587062) para conferir RR/IC95%/p de cada desfecho antes de escrever. Checado contra o corpus canônico de content/Perioperatório/ antes de escrever: 'betabloqueador-perioperatorio-poise-e-recomendacao-atual.md' e 'betabloqueador-cronico-e-avc-isquemico-apos-cirurgia-nao-cardiaca-coorte-hope.md' já cobrem o tema em prosa/estudo isolado, mas nenhum documento do acervo tratava a decisão continuar-vs-suspender do betabloqueador crônico como árvore de decisão estrita — este é o primeiro fluxograma dedicado a esse recorte. PMID da diretriz ESC 2022 corrigido para 36017553 (conferido por esummary; o arquivo 'avaliacao-cardiovascular-e-manejo-em-cirurgia-nao-cardiaca-esc-2022.md' já publicado no acervo cita 36449042 para a mesma diretriz, divergência não corrigida aqui por não ser o arquivo desta tarefa)."
source_refs:
  - "Devereaux PJ, Yang H, Yusuf S, et al; POISE Study Group. Effects of extended-release metoprolol succinate in patients undergoing non-cardiac surgery (POISE trial): a randomised controlled trial. Lancet. 2008;371(9627):1839-1847. DOI: 10.1016/S0140-6736(08)60601-7. PMID: 18479744."
  - "Herrera Hernández D, Abreu B, Siu Xiao T, et al. Beta-Blocker Use in Patients Undergoing Non-Cardiac Surgery: A Systematic Review and Meta-Analysis. Medical Sciences (Basel). 2024;12(4):64. DOI: 10.3390/medsci12040064. PMID: 39584914."
  - "Halvorsen S, Mehilli J, Cassese S, et al. 2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery. European Heart Journal. 2022;43(39):3826-3924. DOI: 10.1093/eurheartj/ehac270. PMID: 36017553."
  - "Rudolph MI, Borngaesser F, Zmily OM, et al. Preoperative beta blocker use and postoperative ischaemic stroke risk in noncardiac surgery: a multicentre retrospective cohort study. British Journal of Anaesthesia. 2026;137(1):129-140. DOI: 10.1016/j.bja.2025.11.027. PMID: 41506973. Já publicado no acervo como 'betabloqueador-cronico-e-avc-isquemico-apos-cirurgia-nao-cardiaca-coorte-hope.md'."
---

# Fluxograma: betabloqueador crônico no perioperatório — continuar ou suspender

"Suspender o betabloqueador antes da cirurgia por segurança" e "iniciar betabloqueador para proteger o coração" são os dois erros simétricos que o POISE (2008) já havia desarmado: início agudo em dose fixa **aumentou morte e AVC**, apesar de reduzir infarto não fatal. Uma metanálise de 2024, com mais de 1,3 milhão de pacientes, revisita a questão numa amostra muito maior e encontra um sinal semelhante de risco de AVC associado ao uso perioperatório de betabloqueador — mas sem diferença significativa em mortalidade ou infarto, e com efeito protetor de mortalidade num subgrupo específico. A árvore abaixo trata o caso mais comum do consultório — o paciente que **já usa** betabloqueador cronicamente — e mantém a recomendação central inalterada por essa evidência mais recente: não suspender por rotina, mas vigiar ativamente a hemodinâmica.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em avaliação pré-operatória de cirurgia não cardíaca, em uso crônico de betabloqueador ou candidato a iniciar a classe"] --> D1{"Já está em uso crônico do betabloqueador (semanas a meses antes da cirurgia), por indicação cardiovascular própria?"}
  D1 -->|"Não, seria iniciar agora só como profilaxia perioperatória"| C1(["Não iniciar betabloqueador de novo apenas por causa da cirurgia: no POISE, início agudo em dose fixa reduziu infarto não fatal mas aumentou mortalidade e AVC"])
  D1 -->|"Sim, uso crônico estabelecido"| D2{"Há instabilidade hemodinâmica aguda ou contraindicação ativa (choque, bradicardia sintomática, BAV avançado sem marcapasso, hipotensão grave)?"}
  D2 -->|"Sim"| C2(["Suspender temporariamente, tratar a causa da instabilidade e planejar reintrodução gradual assim que houver estabilidade hemodinâmica"])
  D2 -->|"Não"| D3{"É possível manter a via oral/enteral habitual no perioperatório, incluindo a dose do dia da cirurgia?"}
  D3 -->|"Sim"| C3(["Manter o betabloqueador na dose habitual por via oral, incluindo a dose da manhã da cirurgia; monitorizar frequência cardíaca e pressão arterial para evitar hipotensão/bradicardia intraoperatória"])
  D3 -->|"Não (jejum prolongado, cirurgia do trato gastrointestinal, íleo)"| D4{"Há via parenteral ou por sonda enteral disponível, com dose equivalente?"}
  D4 -->|"Sim"| C4(["Converter temporariamente para via parenteral ou por sonda, mantendo dose equivalente, sem interromper o tratamento; monitorizar frequência cardíaca e pressão arterial"])
  D4 -->|"Não"| D5{"O período previsto sem administração é curto (1 a 2 doses) e o paciente permanece hemodinamicamente estável?"}
  D5 -->|"Sim"| C5(["Tolerar omissão breve, sem suspensão formal, com monitorização estrita de frequência cardíaca e pressão arterial; reintroduzir assim que a via oral for restabelecida"])
  D5 -->|"Não, jejum prolongado sem via alternativa disponível"| C6(["Planejar a via alternativa com a equipe cirúrgica e anestésica antes da cirurgia; evitar suspensão abrupta não planejada pelo risco de rebote com taquicardia, hipertensão e isquemia"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**A metanálise de 2024 (Herrera Hernández et al., *Medical Sciences*, 28 estudos, 1.342.430 pacientes, PMID 39584914) é a evidência mais robusta em volume já reunida sobre o tema, e o resultado é misto, não uma condenação da classe.** Uso perioperatório de betabloqueador associou-se a mais AVC (RR 1,42; IC95% 1,03–1,97; p=0,03), sem diferença significativa em mortalidade (RR 0,62; IC95% 0,38–1,01; p=0,05) nem em infarto do miocárdio (RR 0,82; IC95% 0,53–1,28; p=0,36), e a mais hipotensão (RR 1,46; IC95% 1,26–1,70; p<0,01) e bradicardia (RR 2,26; IC95% 1,37–3,74; p<0,01). É esse último par — hipotensão e bradicardia — que a própria metanálise aponta como mecanismo plausível do excesso de AVC, replicando exatamente o achado do POISE original.

**Achado que sustenta manter a terapia, não suspendê-la, num subgrupo específico:** a análise de subgrupo da metanálise de 2024 mostrou **efeito protetor de mortalidade em pacientes de maior risco cardiovascular** — história de fibrilação atrial, insuficiência cardíaca crônica ou outras arritmias. Nesses pacientes, a indicação do betabloqueador é o próprio motivo pelo qual a droga está sendo usada — suspendê-la para "reduzir risco cirúrgico" retiraria justamente a proteção que a evidência mostra mais forte.

**Limitação declarada pelos próprios autores, e por isso repetida aqui:** boa parte dos estudos incluídos na metanálise **não distinguiu uso crônico de início perioperatório novo** — a heterogeneidade estatística foi alta (I² de até 100% para mortalidade). Isso significa que o sinal de AVC não pode ser atribuído com segurança só ao paciente que já usa a classe cronicamente; parte do efeito pode vir de estudos com início agudo, o mesmo cenário que o POISE já havia identificado como o problema. A árvore acima trata separadamente os dois cenários (D1) exatamente por essa razão — misturar início agudo com continuação crônica é o erro de leitura mais provável ao citar esta metanálise.

**A recomendação de continuar o betabloqueador crônico no perioperatório é da ESC 2022** (Halvorsen et al., PMID 36017553): manter a medicação sem suspender, evitando o risco de rebote de hipertensão, taquicardia e isquemia associado à descontinuação abrupta — recomendação que a metanálise de 2024 não contradiz, mas reforça a necessidade de vigilância hemodinâmica ativa nos ramos C3–C5 desta árvore.

**A coorte HOPE (Rudolph et al., *British Journal of Anaesthesia*, 2026, PMID 41506973), já publicada neste acervo em documento próprio, levanta um sinal semelhante em desenho observacional retrospectivo**: uso crônico de betabloqueador associou-se a mais AVC isquêmico em 30 dias (RR ajustado 1,26; IC95% 1,17–1,36) e em 365 dias (RR ajustado 1,22; IC95% 1,16–1,28), mais forte em pacientes ASA 1–2 do que ASA 3–4. Os próprios autores da coorte HOPE são explícitos: **o estudo não randomizou pacientes para manter, iniciar ou suspender a droga**, e prescrição crônica de betabloqueador é, em si, um marcador de doença cardiovascular de base — o achado não justifica suspensão automática, é gerador de hipótese para pesquisa futura, não mudança de conduta.

**Em nenhum ramo desta árvore a decisão final é "suspender por rotina" um betabloqueador crônico sem instabilidade hemodinâmica ativa (D2) ou sem impossibilidade real de administração (D3–D5)** — o único ramo que evita a droga por completo (C1) é o de início agudo sem indicação cardiovascular própria, que é exatamente o cenário testado e reprovado pelo POISE original.
