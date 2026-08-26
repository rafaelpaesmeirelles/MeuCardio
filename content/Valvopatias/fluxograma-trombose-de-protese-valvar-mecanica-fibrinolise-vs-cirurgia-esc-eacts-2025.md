---
title: "Fluxograma: Trombose de Prótese Valvar Mecânica — Fibrinólise versus Cirurgia (ESC/EACTS 2025)"
slug: fluxograma-trombose-de-protese-valvar-mecanica-fibrinolise-vs-cirurgia-esc-eacts-2025
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Atualizado para a diretriz ESC/EACTS 2025 (PMID 40878295), que substituiu a preferência rígida de 2021 por avaliação urgente do Heart Team em IC aguda NYHA III/IV causada por trombose obstrutiva, escolhendo entre nova troca valvar e fibrinólise de baixa dose em infusão lenta (I/B). Para trombose não obstrutiva, cirurgia deve ser considerada quando trombo >10 mm é complicado por embolia ou persiste apesar de anticoagulação oral ótima (IIa/C). Anticoagulação subterapêutica deve ser corrigida prontamente em todos, mas não substitui a decisão de reperfusão no paciente com IC aguda importante. O esquema antigo de rt-PA em bolus/90 minutos foi removido por ter sido superado na diretriz 2025."
source_refs: ["Praz F, Borger MA, Lanz J, et al.; ESC/EACTS Scientific Document Group. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4747. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295 — seção 14.4, Figura 20 e Recommendation Table 17.", "Raj Mantoo M, Makkar N, Sharma G. Prosthetic valve thrombosis: contemporary concepts in diagnosis and management. Expert Rev Cardiovasc Ther. 2026;24(7):609-624. DOI: 10.1080/14779072.2026.2700450. PMID: 42412081."]
---

# Fluxograma: Trombose de Prótese Valvar Mecânica — Fibrinólise versus Cirurgia (ESC/EACTS 2025)

Trombose de prótese mecânica é emergência potencial mesmo quando o paciente
parece estável — o atraso na decisão entre fibrinólise e cirurgia piora
desfecho. A diretriz ESC/EACTS 2025 separa a decisão em dois ramos, obstrutiva e
não obstrutiva, e exige avaliação do Heart Team quando a obstrução causa IC
aguda importante. Este fluxograma organiza essa decisão sem reutilizar o
esquema acelerado de fibrinólise da versão de 2021.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de trombose de prótese<br/>valvar mecânica — dispneia recente<br/>ou evento embólico em portador<br/>de prótese"] --> D1{"Confirmada por ecocardiograma<br/>transtorácico/transesofágico,<br/>± cinefluoroscopia ou tomografia<br/>cardíaca: trombose obstrutiva?"}

  D1 -->|"Não — trombose<br/>não obstrutiva"| D2{"Trombo >10 mm complicado<br/>por embolia, ou persistente<br/>apesar de anticoagulação<br/>oral ótima?"}

  D2 -->|"Não"| C1(["Restaurar/otimizar AVK e repetir<br/>imagem em seguimento próximo;<br/>sem indicação automática de<br/>intervenção"])

  D2 -->|"Sim"| C2(["Cirurgia deve ser considerada —<br/>Classe IIa, Nível C; Heart Team<br/>pondera risco cirúrgico, embolia e<br/>alternativas se cirurgia proibitiva"])

  D1 -->|"Sim — trombose<br/>obstrutiva"| D3{"IC aguda NYHA III/IV ou<br/>instabilidade hemodinâmica?"}

  D3 -->|"Sim"| C3(["Avaliação urgente do Heart Team para<br/>nova troca valvar OU fibrinólise de<br/>baixa dose em infusão lenta —<br/>Classe I, Nível B; não atrasar a<br/>decisão para tentar apenas heparina"])

  D3 -->|"Não — sintomas não pronunciados"| C4(["Restaurar anticoagulação adequada<br/>imediatamente e discutir no Heart Team<br/>conforme tamanho/mobilidade do trombo,<br/>evento embólico, posição, risco<br/>cirúrgico e contraindicações à lise"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Por que a diretriz 2025 exige Heart Team

Cirurgia e fibrinólise têm riscos relevantes e nenhum único critério escolhe
sempre a melhor opção. A diretriz atual incorpora a fibrinólise de baixa dose
em infusão lenta como alternativa à nova troca valvar na IC NYHA III/IV e exige
decisão urgente com base em risco cirúrgico, contraindicações hemorrágicas,
posição e geração da prótese, tamanho do trombo e expertise local.

## O que a árvore não mostra

- **Trombose de bioprótese não segue esta árvore.** Tem primeira linha
  farmacológica com AVK (Classe I, Nível B na ESC/EACTS 2025),
  não cirúrgica — a distinção entre trombo e pannus por tomografia também
  importa aqui, e está descrita à parte no documento de origem.
- **Falha de fibrinólise com alto risco cirúrgico é reconhecida pela própria
  diretriz como decisão particularmente difícil**, sem algoritmo fechado —
  cabe à Heart Team individualizar, e por isso não aparece como ramo desta
  árvore.
- **O esquema posológico da fibrinólise não está na árvore.** A ESC/EACTS 2025
  passou a favorecer baixa dose em infusão lenta; protocolo, contraindicações e
  monitorização devem ser definidos pelo Heart Team, não transcritos de um
  esquema acelerado antigo.
- **A revisão de 2026** (Raj Mantoo M et al.) reforça que a prática vem se
  deslocando para decisão individualizada guiada por imagem, mas isso não
  substitui — e é consistente com — a árvore da diretriz vigente reproduzida
  acima.
