---
title: "Fluxograma: Trombose de Prótese Valvar Mecânica — Fibrinólise versus Cirurgia (ESC/EACTS 2021)"
slug: fluxograma-trombose-de-protese-valvar-mecanica-fibrinolise-vs-cirurgia-esc-eacts-2021
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída inteiramente a partir do documento já publicado e revisado nesta pasta 'trombose-de-protese-valvar-mecanica-diagnostico-e-decisao-entre-fibrinolise-e-cirurgia.md', que já descreve, em prosa, o algoritmo da Figura 10 da diretriz ESC/EACTS 2021 (obstrutiva vs. não obstrutiva, com os pontos de decisão de instabilidade hemodinâmica, causa por anticoagulação subterapêutica, posição da prótese e tamanho do trombo) e a tabela de recomendações formais (Classe I/B para troca valvar urgente/emergência em paciente criticamente enfermo; Classe IIa/B para fibrinólise quando cirurgia indisponível/risco muito alto ou prótese em posição direita; Classe IIa/C para cirurgia em trombo não obstrutivo grande complicado por embolismo). Nesta sessão reconferi os três PMIDs citados no documento de origem (34453165, 19427604, 42412081) via PubMed E-utilities (esummary): título, revista e ano batem exatamente com o já citado em cada um. Esta árvore converte a descrição em prosa da Figura 10 em fluxograma formal de árvore de decisão, sem alterar nenhuma classe/nível nem acrescentar ramo não descrito na fonte."
source_refs: ["Vahanian A, Beyersdorf F, Praz F, et al.; ESC/EACTS Scientific Document Group. 2021 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2022;43(7):561-632. DOI: 10.1093/eurheartj/ehab395. PMID: 34453165 — seção 11.4.4 (Thrombosis) e Figura 10 (Management of left-sided obstructive and non-obstructive mechanical prosthetic thrombosis), já reproduzida em prosa no documento de origem desta pasta; título/revista/ano reconferidos nesta sessão via PubMed E-utilities.", "Roudaut R, Lafitte S, Roudaut MF, et al. Management of prosthetic heart valve obstruction: fibrinolysis versus surgery. Arch Cardiovasc Dis. 2009;102(4):269-277. DOI: 10.1016/j.acvd.2009.01.007. PMID: 19427604 — fonte-base citada pela própria diretriz ESC/EACTS 2021 (referência 542) para a comparação entre fibrinólise e cirurgia; título/revista/ano reconferidos nesta sessão via PubMed E-utilities.", "Raj Mantoo M, Makkar N, Sharma G. Prosthetic valve thrombosis: contemporary concepts in diagnosis and management. Expert Rev Cardiovasc Ther. 2026;24(7):609-624. DOI: 10.1080/14779072.2026.2700450. PMID: 42412081 — revisão de 2026; título/revista/ano reconferidos nesta sessão via PubMed E-utilities."]
---

# Fluxograma: Trombose de Prótese Valvar Mecânica — Fibrinólise versus Cirurgia (ESC/EACTS 2021)

Trombose de prótese mecânica é emergência potencial mesmo quando o paciente
parece estável — o atraso na decisão entre fibrinólise e cirurgia piora
desfecho. A diretriz ESC/EACTS 2021 separa a decisão em dois ramos, obstrutiva e
não obstrutiva, e dentro de cada um o achado clínico decide o próximo passo.
Este fluxograma converte esse algoritmo — descrito em prosa no documento de
origem desta pasta — em árvore de decisão formal.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de trombose de prótese<br/>valvar mecânica — dispneia recente<br/>ou evento embólico em portador<br/>de prótese"] --> D1{"Confirmada por ecocardiograma<br/>transtorácico/transesofágico,<br/>± cinefluoroscopia ou tomografia<br/>cardíaca: trombose obstrutiva?"}

  D1 -->|"Não — trombose<br/>não obstrutiva"| D2{"Evento tromboembólico<br/>associado?"}

  D2 -->|"Não"| C1(["Otimizar anticoagulação e<br/>reavaliar em seguimento —<br/>sem indicação automática<br/>de intervenção"])

  D2 -->|"Sim, trombo <10 mm"| C2(["Otimizar anticoagulação e<br/>repetir imagem em<br/>seguimento próximo"])

  D2 -->|"Sim, trombo ≥10 mm, ou<br/>persistente/recorrente<br/>apesar da otimização"| D3{"Alto risco cirúrgico?"}

  D3 -->|"Não"| C3(["Cirurgia — Classe IIa,<br/>Nível C, para trombo não<br/>obstrutivo grande complicado<br/>por embolismo"])

  D3 -->|"Sim"| C4(["Fibrinólise, dado o<br/>risco cirúrgico muito alto"])

  D1 -->|"Sim — trombose<br/>obstrutiva"| D4{"Paciente criticamente enfermo<br/>(instabilidade hemodinâmica)?"}

  D4 -->|"Sim"| C5(["Troca valvar urgente ou de<br/>emergência — Classe I, Nível B,<br/>se disponível prontamente"])

  D4 -->|"Não"| D5{"Causa provável é<br/>anticoagulação recente<br/>subterapêutica?"}

  D5 -->|"Sim"| C6(["Heparina não fracionada<br/>intravenosa ± AAS, com<br/>reavaliação de sucesso<br/>ou falha"])

  D5 -->|"Não"| D6{"Prótese em posição direita<br/>(tricúspide ou pulmonar)?"}

  D6 -->|"Sim"| C7(["Fibrinólise — Classe IIa,<br/>Nível B, preferida nesta posição<br/>mesmo com cirurgia disponível"])

  D6 -->|"Não — posição esquerda<br/>(aórtica ou mitral)"| D7{"Cirurgia disponível<br/>prontamente e risco<br/>cirúrgico aceitável?"}

  D7 -->|"Sim"| C8(["Cirurgia — maior sucesso<br/>hemodinâmico e menos<br/>complicações embólicas<br/>que a fibrinólise"])

  D7 -->|"Não"| C9(["Fibrinólise —<br/>Classe IIa, Nível B"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## Os números que sustentam a preferência por cirurgia (nó D7)

A referência citada pela própria diretriz (Roudaut R et al., Arch Cardiovasc
Dis 2009) comparou 263 episódios de obstrução de prótese valvar em 210
pacientes: mortalidade precoce **igual** entre cirurgia e fibrinólise (10% nos
dois grupos), mas sucesso hemodinâmico maior com cirurgia (89% vs. 70,9%) e
episódios embólicos bem menores (0,7% vs. 15%). É por isso que o nó D7 favorece
cirurgia quando ela está prontamente disponível e o risco cirúrgico é
aceitável — a mortalidade não muda, mas a chance de resolver o problema sem
complicação embólica é maior.

## Por que a posição direita muda a resposta (nó D6)

Fibrinólise em prótese tricúspide/pulmonar tem preferência mesmo com cirurgia
disponível — situação distinta da posição esquerda. O risco de embolização
pulmonar associado à fibrinólise nesse território é menor do que o risco de
embolização sistêmica/cerebral que preocupa na posição esquerda, o que muda o
balanço risco-benefício a favor do tratamento farmacológico.

## O que a árvore não mostra

- **Trombose de bioprótese não segue esta árvore.** Tem primeira linha
  farmacológica (anticoagulação com AVK e/ou heparina, Classe I, Nível C),
  não cirúrgica — a distinção entre trombo e pannus por tomografia também
  importa aqui, e está descrita à parte no documento de origem.
- **Falha de fibrinólise com alto risco cirúrgico é reconhecida pela própria
  diretriz como decisão particularmente difícil**, sem algoritmo fechado —
  cabe à Heart Team individualizar, e por isso não aparece como ramo desta
  árvore.
- **O esquema posológico da fibrinólise não está na árvore** — ativador de
  plasminogênio tecidual recombinante (10 mg em bolus + 90 mg em 90 minutos,
  com heparina não fracionada) ou estreptoquinase (1.500.000 U em 60 minutos,
  sem heparina) estão detalhados no documento de origem.
- **A revisão de 2026** (Raj Mantoo M et al.) reforça que a prática vem se
  deslocando para decisão individualizada guiada por imagem, mas isso não
  substitui — e é consistente com — a árvore da diretriz vigente reproduzida
  acima.
