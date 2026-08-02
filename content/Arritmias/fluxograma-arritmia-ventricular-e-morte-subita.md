---
title: "Arritmia ventricular e risco de morte súbita"
slug: fluxograma-arritmia-ventricular-e-morte-subita
theme: "Arritmias"
kind: fluxograma
summary: "Árvore de conduta imediata para a taquicardia de QRS largo/TV: estabilidade hemodinâmica decide primeiro (instável = cardioversão já), depois diferenciar TV de TSV aberrante, TV monomórfica sustentada versus polimórfica, e tempestade elétrica como ramo próprio com sua escalada terapêutica."
review_status: revisado
source_refs: ["2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death · ESC · 2022 · 10.1093/eurheartj/ehac262 · 36017572 · https://guardheart.ern-net.eu/wp-content/uploads/sites/4/2023/02/PMID-36017572_ESCGuideline_Zeppenfeld.pdf", "Sapp JL, Wells GA, Parkash R, et al. Ventricular tachycardia ablation versus escalation of antiarrhythmic drugs (VANISH). N Engl J Med. 2016;375(2):111-121. DOI: 10.1056/NEJMoa1513614. PMID: 27149033", "Brugada J, Katritsis DG, Arbelo E, et al. 2019 ESC Guidelines for the management of patients with supraventricular tachycardia · European Heart Journal · 2020 · 41(5):655-720 · DOI: 10.1093/eurheartj/ehz467 · PMID: 31504425", "Ortiz M, Martín A, Arribas F, et al. Randomized comparison of intravenous procainamide vs. intravenous amiodarone for the acute treatment of tolerated wide QRS tachycardia: the PROCAMIO study · European Heart Journal · 2017 · 38(17):1329-1335 · PMID: 27354046", "Multidisciplinary Critical Care Management of Electrical Storm: JACC State-of-the-Art Review · JACC · 2023 · https://www.jacc.org/doi/10.1016/j.jacc.2023.03.424", "Spotlight on the 2022 ESC guideline management of ventricular arrhythmias and prevention of sudden cardiac death: 10 novel key aspects · PMC · https://pmc.ncbi.nlm.nih.gov/articles/PMC10228619/", "Soeiro AM, Pisani CF, Petriz JLF, et al. Posicionamento sobre Diagnóstico e Tratamento da Tempestade Elétrica – 2026. GECETI/SBC e SOBRAC. Arq Bras Cardiol. 2026;123(4):e20260215. DOI: 10.36660/abc.20260215"]
---

# Arritmia ventricular e risco de morte súbita

Toda taquicardia de QRS largo é **taquicardia ventricular até prova em
contrário**. A árvore abaixo cobre o atendimento imediato a partir desse
princípio: a instabilidade hemodinâmica decide antes de qualquer diagnóstico
diferencial; estável, o próximo passo é separar TV de TSV com aberrância
quando isso for seguro; TV monomórfica sustentada e TV polimórfica seguem
condutas diferentes; e a tempestade elétrica — três ou mais episódios de TV
sustentada, FV ou choques apropriados do CDI em 24h, com pelo menos 5 minutos
entre eles — é reconhecida como um quadro à parte, com escalada terapêutica
própria.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com taquicardia de QRS largo<br/>(QRS ≥ 120 ms), com suspeita<br/>ou diagnóstico de arritmia ventricular"]
  D1{"Quadro clínico no momento da avaliação"}
  C1(["Cardioversão elétrica sincronizada imediata —<br/>não atrasar por tentativa farmacológica"])
  D2{"É possível diferenciar com segurança<br/>TV de TSV com aberrância?<br/>(dissociação AV, batimentos de<br/>fusão/captura, concordância precordial,<br/>cardiopatia estrutural conhecida)"}
  P1["Tempestade elétrica confirmada: interrogar<br/>e reprogramar o CDI se presente,<br/>sedação/ansiólise, corrigir gatilho<br/>(isquemia aguda, distúrbio eletrolítico,<br/>insuficiência cardíaca descompensada)"]
  C2(["Tratar como TV até prova em contrário —<br/>verapamil contraindicado. Manobra vagal,<br/>adenosina se sem pré-excitação,<br/>antiarrítmico EV (procainamida preferencial,<br/>amiodarona alternativa); se não reverter<br/>nem controlar, cardioversão elétrica<br/>sincronizada"])
  C3(["Conduzir como taquicardia supraventricular<br/>conforme o mecanismo identificado;<br/>verapamil só entra depois de diagnóstico<br/>de TSV completamente estabelecido"])
  D3{"Morfologia da TV"}
  C4(["Cardioversão elétrica sincronizada precoce<br/>(Classe I), mesmo com o paciente tolerado,<br/>se baixo risco anestésico/de sedação —<br/>não aguardar falha farmacológica.<br/>Alternativa: antiarrítmico EV.<br/>Se TV incessante ou recorrente,<br/>encaminhar para ablação por cateter<br/>em centro experiente"])
  C5(["Sulfato de magnésio 2-3g em 30 min<br/>visando magnésio sérico > 2 mEq/L;<br/>corrigir a causa de base (isquemia,<br/>distúrbio eletrolítico); se degenerar<br/>ou instabilizar, cardioversão/desfibrilação"])
  C6(["Não usar amiodarona — seguir o protocolo<br/>específico de torsades de pointes/QT longo<br/>(fora deste fluxograma)"])
  D4{"Contexto/canalopatia de base"}
  C7(["Não usar amiodarona — seguir o protocolo<br/>específico de torsades de pointes/QT longo<br/>(fora deste fluxograma): correção de<br/>potássio/magnésio, retirar o fármaco<br/>agressor, considerar marca-passo transvenoso<br/>para overdrive pacing ou isoproterenol"])
  C8(["Isoproterenol como antiarrítmico<br/>de primeira linha — amiodarona pode<br/>piorar a arritmia nesse contexto"])
  P2["Antiarrítmico EV de primeira linha:<br/>amiodarona (bolus ~300 mg/6-7 mg/kg<br/>em 20-60 min, manutenção 900-1200 mg/dia<br/>por 24-48h) ou betabloqueador<br/>(metoprolol 25-50 mg a cada 12h,<br/>ou esmolol/propranolol);<br/>sulfato de magnésio 2-3g se<br/>componente polimórfico"]
  D5{"Tempestade elétrica controlada com<br/>o antiarrítmico de primeira linha?"}
  C9(["Tempestade elétrica controlada:<br/>manter/otimizar o antiarrítmico, tratar<br/>a causa de base e encaminhar para<br/>avaliação de ablação por cateter<br/>em centro experiente"])
  P3["Escalonar antiarrítmico: associar<br/>segunda linha — lidocaína (bolus<br/>1-1,5 mg/kg, manutenção 1-4 mg/min)<br/>ou esmolol (bolus 0,5 mg/kg<br/>+ infusão 50-300 mcg/kg/min)"]
  D6{"Tempestade elétrica controlada com<br/>antiarrítmico otimizado (1ª + 2ª linha)?"}
  C10(["Tempestade elétrica controlada:<br/>manter o antiarrítmico otimizado, tratar<br/>a causa de base e encaminhar para<br/>avaliação de ablação por cateter<br/>em centro experiente"])
  C11(["Tempestade elétrica refratária:<br/>ablação por cateter em centro experiente<br/>é a terapia preferencial sobre sedação<br/>profunda, modulação autonômica ou suporte<br/>circulatório isolados; considerar associar<br/>bloqueio do gânglio estrelado, anestesia<br/>peridural torácica, denervação simpática<br/>cardíaca cirúrgica/renal, sedação profunda<br/>e suporte circulatório mecânico (ECMO,<br/>balão intra-aórtico, TandemHeart, Impella)<br/>conforme disponibilidade e gravidade"])

  R0 --> D1
  D1 -->|"Instável — hipotensão, choque,<br/>congestão pulmonar aguda, dor torácica<br/>isquêmica ou rebaixamento do nível<br/>de consciência"| C1
  D1 -->|"Estável, episódio único<br/>ou primeiro evento"| D2
  D1 -->|"3 ou mais episódios de TV sustentada,<br/>FV ou choques apropriados do CDI em 24h,<br/>separados por ≥5 min entre si<br/>(tempestade elétrica)"| P1

  D2 -->|"Não é possível diferenciar<br/>com segurança"| C2
  D2 -->|"TSV com aberrância confirmada"| C3
  D2 -->|"TV confirmada ou fortemente presumida"| D3

  D3 -->|"Monomórfica sustentada"| C4
  D3 -->|"Polimórfica, sem QT longo/torsades<br/>associado (ex.: isquemia aguda,<br/>Brugada, cardiopatia estrutural)"| C5
  D3 -->|"Polimórfica associada a<br/>QT longo ou torsades de pointes"| C6

  P1 --> D4
  D4 -->|"QT longo (congênito ou adquirido)<br/>ou torsades de pointes"| C7
  D4 -->|"Síndrome de Brugada ou<br/>síndrome do QT curto"| C8
  D4 -->|"Nenhuma das anteriores<br/>(ex.: cardiopatia isquêmica<br/>ou estrutural)"| P2

  P2 --> D5
  D5 -->|"Sim"| C9
  D5 -->|"Não — refratária"| P3

  P3 --> D6
  D6 -->|"Sim"| C10
  D6 -->|"Não — refratária"| C11

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11 conduta;
```

## Por que a tempestade elétrica é um ramo à parte

Tempestade elétrica não é "muita TV" — é um quadro com risco próprio: mortalidade
de até 14% nas primeiras 48 horas, com risco de morte 2,4 vezes maior durante a
internação e até 5,4 vezes maior nos 3 meses seguintes, frente a episódios
isolados de TV/FV. Por isso ela muda a lógica de manejo: em vez de decidir sobre
um episódio, decide-se sobre um padrão recorrente, com escalada terapêutica que
vai de antiarrítmico endovenoso a ablação por cateter e suporte avançado.

**Cada episódio agudo dentro da tempestade elétrica continua seguindo a regra de
estabilidade hemodinâmica do início desta árvore** — se um dos episódios cursa
com instabilidade, a conduta daquele episódio é cardioversão elétrica
sincronizada imediata, como em qualquer outro. O ramo de tempestade elétrica
descrito aqui é o que organiza o tratamento **entre** os episódios e depois
deles, não substitui o atendimento de cada evento agudo isolado.

## Verapamil é contraindicação formal

Verapamil não é recomendado na taquicardia de QRS largo de etiologia
desconhecida: em paciente com TV até então estável, ele pode provocar
deterioração hemodinâmica grave. Só tem lugar quando o diagnóstico de
taquicardia supraventricular está completa e seguramente estabelecido — é o
erro mais comum desse cenário, tratar como supraventricular a taquicardia
"regular, bem tolerada, em paciente jovem" que na verdade é TV.

## Por que a cardioversão entra mais cedo quando a TV já está confirmada

Quando o diagnóstico de TV monomórfica sustentada está estabelecido, a
diretriz desloca a cardioversão elétrica para o início do atendimento — mesmo
com o paciente hemodinamicamente tolerado, desde que o risco anestésico/de
sedação seja baixo — em vez de esperar a falha da sequência farmacológica. Isso
é diferente da lógica da taquicardia de QRS largo **sem diagnóstico
estabelecido**, em que a incerteza justifica tentar manobra vagal, adenosina
(se sem pré-excitação) e antiarrítmico antes de escalar.

## O que a árvore não mostra

**Critérios eletrocardiográficos de TV** — dissociação atrioventricular,
batimentos de captura e de fusão, concordância precordial, morfologia do QRS —
resumidos na aresta do nó de diferenciação, não são detalhados em ramos
próprios porque não mudam a conduta imediata: na dúvida, trata-se como TV.

**Torsades de pointes e TV polimórfica por QT longo** têm protocolo próprio
(`fluxograma-torsades-de-pointes-e-qt-longo-adquirido.md`, nesta mesma pasta) e
não entram nesta árvore além do ponto em que é preciso reconhecer o quadro e
desviar para lá — inclusive dentro da tempestade elétrica.

**Causa reversível é investigação paralela**: isquemia aguda, distúrbio
eletrolítico, intoxicação por fármaco e descompensação de insuficiência
cardíaca mudam o tratamento de fundo, não o passo imediato, e correm em
paralelo em qualquer ramo desta árvore.

**Se o paciente evolui para parada cardiorrespiratória**, o atendimento passa a
ser o de `fluxograma-parada-cardiorrespiratoria-ritmo-inicial.md`
(Terapia_intensiva), não mais o desta árvore.
