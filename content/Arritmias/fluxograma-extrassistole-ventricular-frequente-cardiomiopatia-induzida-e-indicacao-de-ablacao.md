---
title: "Fluxograma: Extrassístole Ventricular Frequente — Quando Investigar Cardiomiopatia Induzida e Quando Indicar Ablação"
slug: fluxograma-extrassistole-ventricular-frequente-cardiomiopatia-induzida-e-indicacao-de-ablacao
theme: "Arritmias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Documento novo (14/08/2026). Recorte ainda não coberto como árvore de decisão estrita no tema Arritmias — o corpus já tinha uma análise narrativa da carga de PVC que prevê disfunção (extrassistole-ventricular-frequente-e-cardiomiopatia-induzida-carga-que-preve-disfuncao.md, baseada em Baman 2010/Olgun 2011), mas nenhum fluxograma-<slug> tratava do caminho avaliação → suspeita de cardiomiopatia induzida → indicação de ablação. Fonte principal de conduta e classe de recomendação: consenso de especialistas HRS/EHRA/APHRS/LAHRS 2019 sobre ablação por cateter de arritmias ventriculares (Cronin et al., J Arrhythm 2020, PMID 32071620, texto completo aberto em PMC7011820 — recomendações das seções 3.2.2 a 3.2.4 e 4.3 conferidas linha a linha nesta sessão). O corte de carga de PVC >24% e a menor carga associada a cardiomiopatia reversível (10%) vêm de Baman et al., Heart Rhythm 2010 (PMID 20348027), já usado no documento narrativo do corpus e reconferido nesta sessão via PubMed E-utilities (esummary). Doses/fármacos específicos de terapia antiarrítmica não foram detalhados pela diretriz nesta seção — ficam genéricos de propósito, sem inventar posologia."
source_refs: ["Cronin EM, Bogun FM, Maury P, Peichl P, Chen M, Namboodiri N, Aguinaga L, Leite LR, et al. 2019 HRS/EHRA/APHRS/LAHRS expert consensus statement on catheter ablation of ventricular arrhythmias: Executive summary. J Arrhythm. 2020;36(1):1-58. DOI: 10.1002/joa3.12264. PMID: 32071620 — texto completo aberto em PMC7011820, conferido linha a linha nesta sessão: recomendação 3.2.2 (Classe I, B-NR — ecocardiograma na avaliação de arritmia ventricular), 3.2.3 (Classe IIa, B-NR — RM cardíaca útil para estratificação de risco de morte súbita em PVC frequente; Classe IIa, C-LD — estudo eletrofisiológico programado útil para estratificação de risco em doença estrutural cardíaca submetida a ablação de PVC), 3.2.4 (Classe IIa, B-NR — monitorização periódica de carga de PVC e função/dimensão de VE em PVC frequente assintomática com função normal) e 4.3 (Classe I, B-NR — ablação por cateter recomendada quando cardiomiopatia é suspeita de ser causada por PVC frequente e predominantemente monomórfica, com antiarrítmico ineficaz/não tolerado/não preferido para uso prolongado; Classe IIa, B-NR — ablação pode ser útil quando doença estrutural cardíaca com PVC frequente é suspeita de contribuir para a cardiomiopatia, nas mesmas condições de falha/intolerância/preferência quanto ao antiarrítmico).", "Baman TS, Lange DC, Ilg KJ, Gupta SK, Liu TY, Alguire C, Armstrong W, Good E, Chugh A, Jongnarangsin K, Pelosi F Jr, Crawford T, Ebinger M, Oral H, Morady F, Bogun F. Relationship between burden of premature ventricular complexes and left ventricular function. Heart Rhythm. 2010;7(7):865-869. DOI: 10.1016/j.hrthm.2010.03.036. PMID: 20348027 — coorte de 174 pacientes consecutivos encaminhados para ablação de PVC idiopática frequente; corte de carga de PVC >24% com sensibilidade 79%, especificidade 78% e AUC 0,89 para função de VE comprometida; menor carga associada a cardiomiopatia reversível observada foi 10%.", "Olgun H, Yokokawa M, Baman T, Kim HM, Armstrong W, Good E, Chugh A, Pelosi F Jr, Crawford T, Oral H, Morady F, Bogun F. The role of interpolation in PVC-induced cardiomyopathy. Heart Rhythm. 2011;8(7):1046-1049. DOI: 10.1016/j.hrthm.2011.02.034. PMID: 21376837 — PVC interpolada é fator de risco adicional para cardiomiopatia induzida, independente da carga isolada."]
---

# Fluxograma: Extrassístole Ventricular Frequente — Quando Investigar Cardiomiopatia Induzida e Quando Indicar Ablação

Extrassístole ventricular (PVC) frequente é achado comum, e na maioria das
vezes benigno. A decisão que este fluxograma organiza não é "tratar ou não
tratar" — é **quando a carga de PVC deve ser investigada como causa de
cardiomiopatia** e, dentro desse subgrupo, **quando a ablação por cateter passa
de opção para indicação formal**, segundo o consenso HRS/EHRA/APHRS/LAHRS 2019
e o corte numérico de Baman et al. (2010) que a literatura de referência usa
para separar disfunção de VE preservada de comprometida.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Extrassístole ventricular (PVC) frequente identificada<br/>(Holter de 24h ou ECG)"]
  P1["Avaliação inicial: história, exame físico,<br/>ECG de 12 derivações em ritmo sinusal<br/>e ecocardiograma transtorácico<br/>— Classe I, B-NR"]
  D1{"Ecocardiograma mostra disfunção sistólica de VE<br/>(FEVE reduzida) ou dilatação de VE?"}
  P2["Sem disfunção de VE:<br/>quantificar carga de PVC no Holter de 24h"]
  D2{"Carga de PVC ≥10%?<br/>(menor carga já associada a<br/>cardiomiopatia reversível na literatura)"}
  C1(["Carga relevante sem disfunção atual:<br/>considerar RM cardíaca para estratificação<br/>de risco de morte súbita — Classe IIa, B-NR;<br/>monitorização periódica mais próxima de carga<br/>de PVC e função de VE — Classe IIa, B-NR;<br/>ablação NÃO indicada neste momento"])
  C2(["PVC frequente assintomática, FEVE e dimensões<br/>normais, carga <10%: monitorização periódica<br/>de carga de PVC e função de VE<br/>— Classe IIa, B-NR; sem indicação de ablação"])
  P3["Disfunção de VE presente:<br/>quantificar carga de PVC no Holter de 24h,<br/>revisar morfologia (predominantemente<br/>monomórfica?) e investigar causas<br/>alternativas de cardiomiopatia"]
  D3{"Carga de PVC >24%, predominantemente<br/>monomórfica e sem outra causa mais provável<br/>de cardiomiopatia identificada?<br/>(corte com sensibilidade 79%,<br/>especificidade 78%, AUC 0,89)"}
  P4["Cardiomiopatia induzida por PVC provável:<br/>iniciar tentativa de terapia antiarrítmica<br/>(ex.: betabloqueador, bloqueador de canal<br/>de cálcio ou antiarrítmico conforme substrato)"]
  D4{"Terapia antiarrítmica ineficaz, não tolerada<br/>ou não preferida pelo paciente para uso<br/>prolongado?"}
  C3(["Ablação por cateter recomendada<br/>— Classe I, B-NR"])
  C4(["Manter terapia antiarrítmica com resposta<br/>clínica adequada; reavaliar carga de PVC<br/>e função de VE periodicamente"])
  P5["RM cardíaca para caracterizar substrato/fibrose<br/>e investigar causa estrutural alternativa<br/>— Classe IIa, B-NR"]
  D5{"Doença estrutural cardíaca (SHD) identificada,<br/>com PVC frequente ainda suspeita de contribuir<br/>para a cardiomiopatia?"}
  C5(["Cardiomiopatia atribuída a outra causa<br/>identificada: tratar a causa de base;<br/>PVC não é alvo primário de ablação<br/>neste momento"])
  P6["SHD com PVC frequente contribuinte suspeita:<br/>tentar terapia antiarrítmica"]
  D6{"Terapia antiarrítmica ineficaz, não tolerada<br/>ou não preferida pelo paciente para uso<br/>prolongado?"}
  C6(["Ablação por cateter pode ser útil<br/>— Classe IIa, B-NR"])
  C7(["Manter tratamento da cardiopatia estrutural<br/>de base e da terapia antiarrítmica;<br/>reavaliar periodicamente"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| P2
  D1 -->|"Sim"| P3
  P2 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| C2
  P3 --> D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| P5
  P4 --> D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| C4
  P5 --> D5
  D5 -->|"Não"| C5
  D5 -->|"Sim"| P6
  P6 --> D6
  D6 -->|"Sim"| C6
  D6 -->|"Não"| C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Por que o corte de 24% orienta, mas não decide sozinho

O corte de carga de PVC >24% vem de uma coorte de 174 pacientes consecutivos
encaminhados para ablação (Baman et al., Heart Rhythm 2010): foi o valor que
melhor separou função de VE preservada de comprometida (sensibilidade 79%,
especificidade 78%, AUC 0,89). Mas a **menor carga já associada a
cardiomiopatia reversível observada nessa coorte foi 10%** — por isso a árvore
não descarta o paciente com carga entre 10% e 24% e sem disfunção atual: ele
entra em vigilância mais próxima e estratificação de risco por RM, não em
"sem problema". Um segundo fator, do mesmo grupo (Olgun et al., 2011): **PVC
interpolada** (a extrassístole que se insere entre dois batimentos sinusais
sem pausa compensatória) é fator de risco adicional para cardiomiopatia,
independente da carga isolada — dois pacientes com a mesma carga percentual
não têm necessariamente o mesmo risco.

## A indicação de ablação depende de excluir alternativa e de o antiarrítmico falhar

O consenso HRS/EHRA/APHRS/LAHRS 2019 não recomenda ablação para toda PVC
frequente com disfunção de VE — a Classe I exige que a cardiomiopatia seja
**suspeita de ser causada** pela PVC (frequente e predominantemente
monomórfica) **e** que o antiarrítmico já tenha sido tentado e tenha se
mostrado ineficaz, não tolerado ou não preferido pelo paciente para uso
prolongado. Quando há doença estrutural cardíaca de base e a PVC é apenas
**suspeita de contribuir** para a cardiomiopatia (não a causa isolada), a
classe cai para IIa — ablação "pode ser útil", não "é recomendada". É essa
distinção que separa os ramos C3 e C6 da árvore.

## O que a árvore não decide

**Doses e escolha específica de antiarrítmico** não são detalhadas pela
diretriz nesta seção do consenso — a árvore mantém o passo genérico
("terapia antiarrítmica") de propósito, para não inventar posologia que a
fonte consultada não especifica.

**Focally triggered VF** (fibrilação ventricular refratária a antiarrítmico e
desencadeada por PVC similar, Classe IIa, B-NR) e **não resposta a terapia de
ressincronização cardíaca por PVC muito frequente unifocal** (Classe IIa,
C-LD) são outras duas indicações de ablação de PVC no mesmo consenso, mas são
cenários clínicos distintos do escopo desta árvore (cardiomiopatia induzida
por carga) — ficam como nota, não como ramo, para não misturar populações
diferentes na mesma árvore de decisão.

## Conexões prioritárias

- `extrassistole-ventricular-frequente-e-cardiomiopatia-induzida-carga-que-preve-disfuncao` (análise narrativa da coorte de Baman/Olgun que fundamenta o corte numérico usado aqui)
- `suprimir-extrassistole-nao-e-tratar-o-paciente-cast-e-sword` (por que a supressão farmacológica da extrassístole não é objetivo em si)
- `wolff-parkinson-white-assintomatico-e-cardiomiopatia-induzida-por-extrassistoles` (cenário específico de PVC associada a pré-excitação)
- `ablacao-por-campo-pulsado-em-taquicardia-ventricular-e-extrassistole-idiopatica` (técnica de ablação aplicável ao ramo de indicação Classe I/IIa desta árvore)
