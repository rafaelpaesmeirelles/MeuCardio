---
title: "Fluxograma: Escolha e duração da antibioticoterapia na endocardite infecciosa por agente etiológico (ESC 2023)"
slug: fluxograma-endocardite-antibioticoterapia-por-agente-etiologico-esc-2023
theme: "Endocardite"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída integralmente a partir do documento já publicado e revisado 'esquemas-antibioticos-na-endocardite-infecciosa-por-agente-esc-2023.md' desta pasta, que transcreve as Tabelas de Recomendação 7, 8, 9 e 10 da diretriz ESC 2023 (lidas no texto integral em sessão anterior). Nenhuma fonte nova foi consultada; todos os fármacos, doses, durações e classes/níveis foram conferidos contra o corpo desse documento antes de montar a árvore — nenhuma dose foi transcrita de memória."
source_refs: ["Delgado V, Ajmone Marsan N, de Waha S, et al.; ESC Scientific Document Group. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656 — Tabelas de Recomendação 7, 8, 9 e 10 (estreptococos, estafilococos, enterococos e tratamento empírico), texto integral já lido e citado no documento 'esquemas-antibioticos-na-endocardite-infecciosa-por-agente-esc-2023.md' desta pasta."]
---

# Fluxograma: Escolha e duração da antibioticoterapia na endocardite infecciosa por agente etiológico (ESC 2023)

O documento de esquemas antibióticos já publicado nesta pasta traz, em prosa e tabelas, o
regime de cada agente identificado por hemocultura e o esquema empírico antes da
identificação. Este fluxograma organiza a mesma informação como árvore de decisão, partindo
do agente etiológico (ou da ausência dele) até o fármaco e a duração, sempre distinguindo
valva nativa de prótese — a distinção que mais muda o tratamento em cada ramo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Endocardite infecciosa confirmada,<br/>iniciar ou ajustar antibioticoterapia<br/>ESC 2023"] --> D1{"Qual o resultado da hemocultura?"}

  D1 -->|"Estreptococos orais<br/>ou grupo Streptococcus gallolyticus"| D2{"Endocardite de valva nativa,<br/>não complicada, com função renal normal —<br/>elegível para esquema curto?"}

  D2 -->|"Sim"| C1(["Penicilina G, amoxicilina ou ceftriaxona,<br/>combinada a gentamicina, por 2 semanas<br/>Classe I, Nível B"])

  D2 -->|"Não, prótese,<br/>complicação ou função<br/>renal alterada"| C2(["Penicilina G, amoxicilina ou ceftriaxona<br/>isolada, por 4 semanas em valva nativa<br/>ou 6 semanas em prótese<br/>Classe I, Nível B"])

  D1 -->|"Staphylococcus sensível<br/>à meticilina"| D3{"Valva nativa ou prótese?"}

  D3 -->|"Valva nativa"| C3(["Flucloxacilina ou cloxacilina, ou cefazolina,<br/>por 4 a 6 semanas<br/>Classe I, Nível B"])

  D3 -->|"Prótese"| C4(["Flucloxacilina ou cloxacilina, ou cefazolina,<br/>com rifampicina por ao menos 6 semanas<br/>e gentamicina por 2 semanas<br/>Classe I, Nível B"])

  D1 -->|"Staphylococcus resistente<br/>à meticilina"| D4{"Valva nativa ou prótese?"}

  D4 -->|"Valva nativa"| C5(["Vancomicina por 4 a 6 semanas<br/>Classe I, Nível B"])

  D4 -->|"Prótese"| C6(["Vancomicina, com rifampicina por ao<br/>menos 6 semanas e gentamicina<br/>por 2 semanas<br/>Classe I, Nível B"])

  D1 -->|"Enterococcus sensível a<br/>betalactâmico e gentamicina"| D5{"Há alto nível de resistência<br/>a aminoglicosídeo HLAR?"}

  D5 -->|"Não, sem HLAR"| C7(["Ampicilina ou amoxicilina com<br/>ceftriaxona por 6 semanas, ou com<br/>gentamicina por 2 semanas<br/>Classe I, Nível B"])

  D5 -->|"Sim, HLAR presente"| C8(["Ampicilina ou amoxicilina com<br/>ceftriaxona por 6 semanas —<br/>gentamicina não contribui nesse cenário<br/>Classe I, Nível B"])

  D1 -->|"Hemoculturas ainda negativas<br/>ou agente não identificado,<br/>terapia empírica"| D6{"Endocardite de valva nativa adquirida<br/>na comunidade, ou prótese tardia<br/>12 meses ou mais após a cirurgia?"}

  D6 -->|"Sim"| C9(["Ampicilina com ceftriaxona, ou com<br/>flucloxacilina/cloxacilina, mais gentamicina<br/>Classe IIa"])

  D6 -->|"Não, prótese precoce menos<br/>de 12 meses da cirurgia, ou endocardite<br/>associada a cuidados de saúde"| C10(["Vancomicina ou daptomicina,<br/>combinadas a gentamicina e rifampicina<br/>Classe IIb"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10 conduta;
```

## O que a árvore não mostra

- **Agentes de cultura negativa e patógenos incomuns não estão incluídos.** *Legionella*,
  *Bartonella*, *Coxiella*, *Brucella* e fungos têm tabela própria na diretriz, com esquemas
  longos e específicos (por exemplo, *Legionella* recebe levofloxacino 500 mg a cada 12
  horas por 6 semanas ou mais) — fora do escopo desta árvore, que cobre os agentes mais
  frequentes.
- **A estrutura em duas fases do tratamento não aparece como ramo.** Em geral, as duas
  primeiras semanas são de terapia parenteral hospitalar — é a janela em que a cirurgia
  indicada, a remoção de material infectado e a drenagem de abscesso devem acontecer — e a
  fase seguinte pode ser oral ou parenteral ambulatorial em paciente selecionado e estável,
  até completar a duração total indicada em cada ramo.
- **Ajuste renal e monitorização de nível sérico não estão contemplados.** Vancomicina,
  gentamicina e os demais fármacos desta árvore exigem ajuste por função renal e
  monitorização de concentração sérica que este fluxograma não cobre.
- **As doses exatas de cada fármaco** (por exemplo, penicilina G 12–18 milhões U/dia,
  vancomicina 30–60 mg/kg/dia, gentamicina 3 mg/kg/dia) estão detalhadas no documento de
  esquemas antibióticos já publicado nesta pasta, e não foram repetidas nos nós da árvore
  para manter os rótulos legíveis.
- **Se as hemoculturas iniciais forem negativas e não houver resposta clínica**, a diretriz
  orienta considerar etiologia de cultura negativa e ampliar o espectro — e, havendo
  indicação cirúrgica, buscar diagnóstico molecular no material operatório.
- **A decisão de operar corre em paralelo ao antibiótico, não depois dele** — a indicação e
  o timing cirúrgico têm documentos próprios nesta pasta, inclusive o de timing após
  complicação neurológica.
