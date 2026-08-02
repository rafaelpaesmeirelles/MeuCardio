---
title: "Dor torácica aguda com uso recente confirmado ou suspeito de cocaína"
slug: fluxograma-dor-toracica-aguda-com-uso-recente-confirmado-ou-suspeito-de-cocaina
theme: "Saúde mental e cardiologia"
kind: fluxograma
summary: "Árvore de decisão para dor torácica aguda com uso recente (confirmado ou suspeito) de cocaína, sobretudo na primeira hora após o uso: avaliação padrão de SCA, e a diferenciação entre infarto por trombose coronariana verdadeira e disfunção miocárdica induzida por estimulante, potencialmente reversível."
review_status: revisado
source_refs: ["Mittleman MA, Mintzer D, Maclure M, Tofler GH, Sherwood JB, Muller JE. Triggering of myocardial infarction by cocaine. Circulation. 1999;99(21):2737-2741. PMID: 10351966 — estudo caso-cruzado do Determinants of Myocardial Infarction Onset Study, 3.946 pacientes pós-IAM entrevistados sobre uso de cocaína na hora anterior ao início dos sintomas", "McCord J, Jneid H, Hollander JE, de Lemos JA, Cercek B, Hsue P, Gibler WB, Ohman EM, Drew B, Philippides G, Newby LK; American Heart Association Acute Cardiac Care Committee of the Council on Clinical Cardiology. Management of cocaine-associated chest pain and myocardial infarction: a scientific statement from the American Heart Association. Circulation. 2008;117(14):1897-1907. PMID: 18347214 — declaração científica dedicada ao tema; existência e citação confirmadas, mas texto integral bloqueado por paywall em ahajournals.org, sem versão em PMC — conteúdo de manejo tratado como não conferido nesta sessão, ver marcação abaixo", "Schürer S, Klingel K, Sandri M, Majunke N, Besler C, Kandolf R, Lurz P, Luck M, Hertel P, Schuler G, Linke A, Mangner N. Clinical Characteristics, Histopathological Features, and Clinical Outcome of Methamphetamine-Associated Cardiomyopathy. JACC Heart Fail. 2017;5(6):435-445. PMID: 28571597 — coorte de 30 pacientes com biópsia endomiocárdica e desfecho comparado entre abstinência e uso continuado", "Sliman S, Waalen J, Shaw D. Methamphetamine-Associated Congestive Heart Failure: Increasing Prevalence and Relationship of Clinical Outcomes to Continued Use or Abstinence. Cardiovasc Toxicol. 2016;16(4):381-389. PMID: 26661075 — coorte independente confirmando o mesmo padrão de reversibilidade condicionada à abstinência"]
---

# Dor torácica aguda com uso recente confirmado ou suspeito de cocaína

A cocaína eleva o risco de início de infarto em **23,7 vezes** na hora seguinte
ao uso, efeito abrupto e transitório que cai rapidamente depois dessa janela
(Mittleman et al., 1999). A avaliação inicial segue o padrão de qualquer
síndrome coronariana aguda, mas duas particularidades mudam a conduta: evitar
betabloqueador isolado, e diferenciar infarto por trombose coronariana
verdadeira de disfunção miocárdica induzida pelo estimulante — que pode ser
reversível.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Dor torácica aguda em paciente com uso<br/>recente, confirmado ou suspeito, de cocaína<br/>— risco de infarto especialmente alto<br/>na 1ª hora após o uso"]
  P1["ECG e troponina seriados,<br/>como em qualquer SCA.<br/>Evitar betabloqueador isolado<br/>na fase aguda"]
  D1{"ECG e/ou troponina indicam<br/>lesão miocárdica aguda?"}
  C1(["Sem evidência de lesão aguda:<br/>observação com reavaliação seriada<br/>de ECG e troponina. Manter suspeita<br/>pela janela de risco da 1ª hora"])
  P2["Avaliar anatomia coronariana<br/>(angiografia/cateterismo)"]
  D2{"Angiografia mostra lesão<br/>obstrutiva compatível com trombose?"}
  C2(["Infarto por trombose coronariana<br/>confirmado: tratar como SCA padrão,<br/>com revascularização conforme indicado.<br/>Manter sem betabloqueador isolado"])
  C3(["Suspeitar de cardiomiopatia induzida<br/>por estimulante (potencialmente reversível):<br/>tratar a disfunção miocárdica/IC,<br/>sem intervenção coronariana obrigatória.<br/>Cessação do uso é a medida mais<br/>associada à recuperação da função"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P2
  P2 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não, mas com disfunção<br/>ventricular associada"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## O que se repete em todo ramo, e por isso não está no diagrama

**Reavaliação seriada de ECG e troponina** enquanto durar a dor ou a suspeita,
independente do ramo em que o paciente estiver.

**Suporte geral de qualquer dor torácica aguda** — monitorização contínua,
acesso venoso, oxigênio se houver hipoxemia — corre em paralelo, em qualquer
ramo.

**Perguntar diretamente sobre uso de substância** faz parte da anamnese em
qualquer paciente jovem com dor torácica ou disfunção ventricular nova, mesmo
sem fator de risco cardiovascular clássico — é informação que o paciente
frequentemente não oferece espontaneamente.

## Por que evitar betabloqueador isolado

A mesma ressalva farmacológica vale aqui e no fluxograma desta coleção sobre
vasoespasmo coronariano induzido por cocaína: o bloqueio beta isolado deixaria
a vasoconstrição alfa-adrenérgica sem oposição. Essa recomendação é amplamente
citada na literatura de emergência, mas **VERIFICAÇÃO HUMANA NECESSÁRIA** — a
declaração científica dedicada da American Heart Association que a sustenta
(McCord et al., 2008) está bloqueada por paywall e não foi lida na íntegra
nesta sessão.

## Por que a disfunção sem lesão obstrutiva pode não ser um infarto definitivo

O mecanismo da cocaína inclui vasoconstrição coronariana direta, inclusive de
segmentos sem placa angiograficamente visível — ou seja, dano miocárdico sem
trombose obstrutiva é biologicamente plausível na apresentação aguda. A
evidência de que essa disfunção pode reverter vem da cardiomiopatia associada
à metanfetamina (MACM): numa coorte de 30 pacientes com biópsia
endomiocárdica, a fração de ejeção subiu de **19 ± 6% para 43 ± 13%** entre os
que pararam de usar, e não melhorou entre os que mantiveram o uso (Schürer et
al., 2017), padrão confirmado em coorte independente (Sliman et al., 2016). O
dado prático: **fração de ejeção baixa na apresentação não prediz, sozinha, o
prognóstico** — a resposta à cessação do uso é o que separa quem recupera de
quem não recupera, o que torna o encaminhamento a tratamento de transtorno por
uso de substância parte central da conduta, não um adendo social.
