---
title: "Fluxograma: Decisão entre Terapia de Ressincronização Cardíaca (CRT) e CDI Isolado na ICFEr"
slug: fluxograma-decisao-crt-versus-cdi-isolado-icfer
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído a partir de fontes já verificadas e publicadas nesta biblioteca (tema Dispositivos e tema Insuficiência cardíaca), sem PMID/DOI novo. Os quatro estratos de QRS/morfologia em ritmo sinusal foram conferidos diretamente na tabela de recomendações da ESC 2021: BRE ≥150 ms (I/A), BRE 130-149 ms (IIa/B), não-BRE ≥150 ms (IIa/B) e não-BRE 130-149 ms (IIb/B); QRS <130 ms sem indicação de estimulação ventricular é classe III/A. CARE-HF PMID 15753115, RAFT PMID 21073365 e COMPANION PMID 15152059 (números de HR e p já conferidos e publicados em 'content/Dispositivos/terapia-de-ressincronizacao-cardiaca-sicd-e-seguimento-remoto.md' e 'content/Dispositivos/ressincronizacao-com-marcapasso-ou-com-desfibrilador-o-ensaio-companion.md'). PRAETORIAN PMID 32757521 já verificado no mesmo documento de origem. Fluxograma de CDI em prevenção primária ESC 2022 já publicado em 'content/Dispositivos/fluxograma-cdi-prevencao-primaria-esc-2022.md' — este documento cruza com ele em vez de duplicar seus critérios."
source_refs: ["2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy. Eur Heart J. 2021;42(35):3427-3520. https://academic.oup.com/eurheartj/article/42/35/3427/6358547", "Cleland JGF, Daubert JC, Erdmann E, et al; CARE-HF Study Investigators. The effect of cardiac resynchronization on morbidity and mortality in heart failure. N Engl J Med. 2005;352(15):1539-1549. DOI: 10.1056/NEJMoa050496. PMID: 15753115", "Tang ASL, Wells GA, Talajic M, et al; RAFT Investigators. Cardiac-resynchronization therapy for mild-to-moderate heart failure. N Engl J Med. 2010;363(25):2385-2395. DOI: 10.1056/NEJMoa1009540. PMID: 21073365", "Bristow MR, Saxon LA, Boehmer J, et al; COMPANION Investigators. Cardiac-resynchronization therapy with or without an implantable defibrillator in advanced chronic heart failure. N Engl J Med. 2004;350(21):2140-2150. DOI: 10.1056/NEJMoa032423. PMID: 15152059", "Knops RE, Olde Nordkamp LRA, Delnoy PHM, et al; PRAETORIAN Investigators. Subcutaneous or Transvenous Defibrillator Therapy. N Engl J Med. 2020;383(6):526-536. DOI: 10.1056/NEJMoa1915932. PMID: 32757521", "2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126. https://academic.oup.com/eurheartj/article/43/40/3997/6675633"]
---

# Fluxograma: Decisão entre Terapia de Ressincronização Cardíaca (CRT) e CDI Isolado na ICFEr

A decisão de dispositivo elétrico na ICFEr tem duas perguntas encadeadas, não
uma só: **o paciente tem critério de terapia de ressincronização (TRC)?** — que
depende de ritmo, QRS e morfologia, não só de FEVE — e, se tiver, **a TRC deve
vir com desfibrilador (CRT-D) ou apenas com marca-passo (CRT-P)?** O COMPANION
é o único grande ensaio que randomizou terapia otimizada isolada, CRT-P e
CRT-D ao mesmo tempo, e por isso é a base direta dessa segunda decisão.

## Árvore de decisão

```mermaid
flowchart TD
  R0["ICFEr sintomática (NYHA II-IV) apesar<br/>de terapia otimizada — avaliação para<br/>dispositivo elétrico"]
  D1{"Ritmo sinusal, FEVE ≤ 35% e<br/>QRS ≥ 130 ms apesar de terapia otimizada?"}
  D1B{"Fibrilação atrial com estratégia de<br/>ablação do nó AV, bloqueio AV de alto<br/>grau ou carga relevante de estimulação<br/>ventricular prevista/presente?"}
  D1A{"Morfologia e duração do QRS<br/>(ESC 2021)?"}
  C0(["Aplicar algoritmo específico de TRC em<br/>FA/ablação do nó AV ou em indicação de<br/>estimulação ventricular — o limiar de<br/>QRS do ritmo sinusal não deve excluir<br/>esses pacientes"])
  D2{"Há também indicação de CDI em<br/>prevenção primária pela FEVE/etiologia<br/>(ver fluxograma dedicado de CDI em<br/>prevenção primária, ESC 2022)?"}
  C1(["TRC com desfibrilador (CRT-D) — o<br/>COMPANION mostrou redução de morte ou<br/>internação por qualquer causa tanto com<br/>CRT-P (HR 0,81) quanto com CRT-D (HR<br/>0,80) frente à terapia otimizada<br/>isolada; a indicação concomitante de<br/>CDI reforça a escolha por CRT-D"])
  D3{"Expectativa de vida com boa capacidade<br/>funcional além de 1 ano e ausência de<br/>contraindicação a choque (ex. cuidado<br/>paliativo, comorbidade limitante)?"}
  C2(["Escolha compartilhada entre CRT-P e<br/>CRT-D — sem indicação independente de<br/>CDI, o COMPANION não demonstrou<br/>superioridade direta de CRT-D sobre<br/>CRT-P; ponderar etiologia, risco<br/>arrítmico, idade, comorbidades e<br/>preferências"])
  C3(["Preferir CRT-P — menor complexidade de<br/>implante e menor risco de choque<br/>inapropriado, sem que o benefício<br/>adicional do desfibrilador seja<br/>proporcional ao risco/benefício neste<br/>perfil"])
  D4{"Há indicação isolada de CDI em<br/>prevenção primária pelos critérios de<br/>FEVE/etiologia (fluxograma de CDI em<br/>prevenção primária, ESC 2022)?"}
  C4(["CDI isolado — transvenoso ou<br/>subcutâneo conforme necessidade de<br/>estimulação por marca-passo (S-ICD não<br/>estimula; ver PRAETORIAN para a<br/>comparação de segurança entre as duas<br/>vias) — sem indicação de TRC pelos<br/>critérios atuais de QRS/ritmo"])
  C5(["Sem indicação de dispositivo elétrico<br/>neste momento pelos critérios de<br/>QRS/FEVE — manter otimização da terapia<br/>quádrupla e reavaliar QRS e FEVE<br/>periodicamente"])

  R0 --> D1
  D1 -->|"Sim"| D1A
  D1 -->|"Não"| D1B
  D1B -->|"Sim"| C0
  D1B -->|"Não"| D4
  D1A -->|"BRE ≥150 ms — classe I/A"| D2
  D1A -->|"BRE 130-149 ms ou não-BRE<br/>≥150 ms — classe IIa/B"| D2
  D1A -->|"Não-BRE 130-149 ms —<br/>pode ser considerada, IIb/B"| D2
  D2 -->|"Sim — também indicação de CDI"| C1
  D2 -->|"Não — só indicação de TRC"| D3
  D3 -->|"Sim — expectativa de vida/função<br/>compatíveis, sem contraindicação"| C2
  D3 -->|"Não"| C3
  D4 -->|"Sim — indicação isolada de CDI"| C4
  D4 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**QRS estreito e indicação independente de estimulação** — a regra de não
indicar TRC com QRS <130 ms aplica-se a quem não tem indicação de estimulação
ventricular. Bloqueio AV de alto grau com ICFEr e carga prevista de estimulação
ventricular, ou necessidade de ablação do nó AV, exige um algoritmo próprio e
não deve ser excluído por este limiar.

**Fibrilação atrial concomitante** muda a discussão de TRC — a diretriz exige
garantia de captura biventricular quase completa nesse cenário, frequentemente
com ablação do nó AV associada. Este fluxograma pressupõe ritmo sinusal, como
o próprio critério principal já explicita.

**Estimulação do sistema de conducão (feixe de His ou ramo esquerdo)** como
alternativa à TRC biventricular clássica não está representada — é decisão de
centro especializado, coberta em outros documentos desta biblioteca em
Dispositivos (`estimulacao-do-feixe-de-his-versus-biventricular-o-ensaio-his-sync.md`,
`estimulacao-do-ramo-esquerdo-versus-biventricular-o-ensaio-lbbp-resync.md`).

**Escolha entre CDI transvenoso e subcutâneo (S-ICD)**, quando a indicação é
de CDI isolado, depende da necessidade de estimulação por marca-passo e não é
detalhada em profundidade nesta árvore — ver o documento dedicado em
Dispositivos, que traz os números completos do PRAETORIAN.
