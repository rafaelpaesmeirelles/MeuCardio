---
title: "Fluxograma: Decisão entre Terapia de Ressincronização Cardíaca (CRT) e CDI Isolado na ICFEr"
slug: fluxograma-decisao-crt-versus-cdi-isolado-icfer
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído a partir de fontes já verificadas e publicadas nesta biblioteca (tema Dispositivos e tema Insuficiência cardíaca), sem PMID/DOI novo. Critério principal de indicação de TRC (ritmo sinusal, FEVE ≤35%, QRS ≥150ms com morfologia de bloqueio de ramo esquerdo) reproduz literalmente o que já está registrado em 'content/Dispositivos/terapia-de-ressincronizacao-cardiaca-sicd-e-seguimento-remoto.md' (fonte: 2021 ESC Guidelines on cardiac pacing and CRT). Deliberadamente NÃO foram incluídos os subcritérios de QRS 130-149ms com BRE ou QRS ≥150ms sem morfologia de BRE (Classe IIa na diretriz completa) por não estarem detalhados com classe/nível no documento-fonte já verificado nesta biblioteca — o texto do fluxograma remete explicitamente ao texto integral da diretriz para esses subcritérios, em vez de reconstituí-los de memória. CARE-HF PMID 15753115, RAFT PMID 21073365 e COMPANION PMID 15152059 (números de HR e p já conferidos e publicados em 'content/Dispositivos/terapia-de-ressincronizacao-cardiaca-sicd-e-seguimento-remoto.md' e 'content/Dispositivos/ressincronizacao-com-marcapasso-ou-com-desfibrilador-o-ensaio-companion.md'). PRAETORIAN PMID 32757521 já verificado no mesmo documento de origem. Fluxograma de CDI em prevenção primária ESC 2022 já publicado em 'content/Dispositivos/fluxograma-cdi-prevencao-primaria-esc-2022.md' — este documento cruza com ele em vez de duplicar seus critérios."
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
  D1{"Critério principal de TRC presente —<br/>ritmo sinusal, FEVE ≤ 35%, QRS ≥ 150 ms<br/>com morfologia de bloqueio de ramo<br/>esquerdo (ESC 2021)?"}
  D2{"Há também indicação de CDI em<br/>prevenção primária pela FEVE/etiologia<br/>(ver fluxograma dedicado de CDI em<br/>prevenção primária, ESC 2022)?"}
  C1(["TRC com desfibrilador (CRT-D) — o<br/>COMPANION mostrou redução de morte ou<br/>internação por qualquer causa tanto com<br/>CRT-P (HR 0,81) quanto com CRT-D (HR<br/>0,80) frente à terapia otimizada<br/>isolada; a indicação concomitante de<br/>CDI reforça a escolha por CRT-D"])
  D3{"Expectativa de vida com boa capacidade<br/>funcional além de 1 ano e ausência de<br/>contraindicação a choque (ex. cuidado<br/>paliativo, comorbidade limitante)?"}
  C2(["Considerar CRT-D mesmo sem indicação<br/>isolada de CDI pela FEVE — a TRC por si<br/>só reduz risco arrítmico ao promover<br/>remodelamento reverso; decisão<br/>individualizada com o paciente entre<br/>CRT-P e CRT-D (COMPANION)"])
  C3(["Preferir CRT-P — menor complexidade de<br/>implante e menor risco de choque<br/>inapropriado, sem que o benefício<br/>adicional do desfibrilador seja<br/>proporcional ao risco/benefício neste<br/>perfil"])
  D4{"Há indicação isolada de CDI em<br/>prevenção primária pelos critérios de<br/>FEVE/etiologia (fluxograma de CDI em<br/>prevenção primária, ESC 2022)?"}
  C4(["CDI isolado — transvenoso ou<br/>subcutâneo conforme necessidade de<br/>estimulação por marca-passo (S-ICD não<br/>estimula; ver PRAETORIAN para a<br/>comparação de segurança entre as duas<br/>vias) — sem indicação de TRC pelos<br/>critérios atuais de QRS/ritmo"])
  C5(["Sem indicação de dispositivo elétrico<br/>neste momento pelos critérios de<br/>QRS/FEVE — manter otimização da terapia<br/>quádrupla e reavaliar QRS e FEVE<br/>periodicamente"])

  R0 --> D1
  D1 -->|"Sim — critério de TRC presente"| D2
  D1 -->|"Não — QRS menor que 150 ms,<br/>morfologia não-BRE ou ritmo não<br/>sinusal"| D4
  D2 -->|"Sim — também indicação de CDI"| C1
  D2 -->|"Não — só indicação de TRC"| D3
  D3 -->|"Sim — expectativa de vida/função<br/>compatíveis, sem contraindicação"| C2
  D3 -->|"Não"| C3
  D4 -->|"Sim — indicação isolada de CDI"| C4
  D4 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**Subcritérios de QRS 130-149 ms com BRE, ou QRS ≥150 ms sem morfologia de
BRE** — a diretriz completa ESC 2021 trata essas faixas com recomendação de
classe diferente (geralmente IIa) da do critério principal usado nesta árvore
(QRS ≥150 ms com BRE). `VERIFICAÇÃO HUMANA NECESSÁRIA`: consulte o texto
integral da diretriz para esses subcritérios antes de excluir um paciente só
por não se encaixar no critério principal aqui representado.

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