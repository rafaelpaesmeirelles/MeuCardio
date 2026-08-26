---
title: "Fluxograma: Escolha entre inibidor de SGLT2 e agonista de GLP-1 no diabético com doença cardiovascular"
slug: fluxograma-escolha-isglt2-glp1-diabetico-doenca-cardiovascular
theme: "Diabetes e cardiologia"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de três documentos já publicados e revisados nesta pasta, sem consulta a fonte nova: 'fluxograma-diabetes-e-doenca-cardiovascular-esc-2023.md' (indicação de iSGLT2 em insuficiência cardíaca de qualquer fração de ejeção e de iSGLT2/GLP-1 em doença aterosclerótica estabelecida, independentemente do controle glicêmico, ESC 2023, PMID já conferido no documento de origem), 'combinacao-de-isglt2-e-agonista-de-glp-1-versus-monoterapia-desfechos-cardiovasculares-e-renais.md' (metanálise em rede, Chuang MH et al., CMAJ 2026, PMID 42442791 — usada para o ramo de combinação das duas classes e para a redução de hospitalização por insuficiência cardíaca) e 'confidence-combinacao-de-finerenona-e-empagliflozina-na-doenca-renal-cronica-diabetica.md' (usado só para justificar a associação de finerenona quando a albuminúria persiste sob iSGLT2 na DRC). Os cortes de indicação e a lógica de priorização por condição predominante foram conferidos contra o texto desses três documentos antes de montar a árvore; nenhum PMID novo foi buscado para este fluxograma."
source_refs: ["Marx N, Federici M, Schütt K, et al. 2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes. Eur Heart J. 2023;44(39):4043-4140. DOI: 10.1093/eurheartj/ehad192. PMID: 37622663 — já citado em 'fluxograma-diabetes-e-doenca-cardiovascular-esc-2023.md' desta pasta.", "Chuang MH, Ho CW, Wang HY, Pan HC, Wu VC, Tu YK, Chen JY. Cardiovascular and renal outcomes of combined SGLT2 inhibitors and GLP-1 receptor agonists versus monotherapy: a systematic review and network meta-analysis of randomized controlled trials. CMAJ. 2026;198(26):E992-E1001. DOI: 10.1503/cmaj.250369. PMID: 42442791 — já citado em 'combinacao-de-isglt2-e-agonista-de-glp-1-versus-monoterapia-desfechos-cardiovasculares-e-renais.md' desta pasta.", "American Diabetes Association Professional Practice Committee. Cardiovascular Disease and Risk Management: Standards of Care in Diabetes—2026. Diabetes Care. 2026;49(Suppl 1):S216-S245. DOI: 10.2337/dc26-S010. PMID: 41358899 — já citado em 'ada-standards-of-care-2026-capitulo-10-doenca-cardiovascular-e-manejo-de-risco.md' desta pasta, usado para o ramo de insuficiência cardíaca com fração de ejeção preservada e obesidade."]
---

# Fluxograma: Escolha entre inibidor de SGLT2 e agonista de GLP-1 no diabético com doença cardiovascular

Com dois trials pivotais de cada classe já documentados nesta pasta, a pergunta de
consultório que falta responder é prática: diante de um diabético tipo 2 com doença
cardiovascular ou renal já estabelecida, qual classe começar primeiro — e quando associar
as duas. Este fluxograma organiza essa escolha pela condição clínica predominante.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Diabetes tipo 2 com doença aterosclerótica<br/>cardiovascular estabelecida, insuficiência<br/>cardíaca ou doença renal crônica"] --> D1{"Qual é a condição predominante?"}

  D1 -->|"Insuficiência cardíaca,<br/>qualquer fração de ejeção"| C1(["Inibidor de SGLT2, independente<br/>do controle glicêmico — classe com<br/>a evidência mais consistente para<br/>reduzir hospitalização por IC"])

  D1 -->|"Doença renal crônica com<br/>albuminúria ou TFGe reduzida"| D2{"TFGe permite início de iSGLT2?<br/>geralmente igual ou superior<br/>a 20mL/min/1,73m²"}

  D1 -->|"Doença aterosclerótica cardiovascular<br/>estabelecida, sem IC nem DRC predominante"| D3{"Necessidade de perda de peso<br/>relevante ou obesidade associada?"}

  D2 -->|"Sim"| P1["Inibidor de SGLT2"]

  D2 -->|"Não, TFGe abaixo<br/>do limite de início"| C2(["Agonista de receptor de GLP-1<br/>com benefício cardiovascular<br/>comprovado"])

  P1 --> D4{"Albuminúria persiste apesar de IECA/BRA<br/>na máxima dose tolerada e iSGLT2,<br/>com TFGe e potássio permitindo<br/>finerenona?"}

  D4 -->|"Sim"| C3(["Associar finerenona ao inibidor<br/>de SGLT2, com monitorização de<br/>potássio e função renal"])

  D4 -->|"Não"| C4(["Manter inibidor de SGLT2<br/>isolado, com seguimento<br/>periódico de função renal"])

  D3 -->|"Sim"| C5(["Agonista de receptor de GLP-1<br/>ou GLP-1/GIP com benefício<br/>cardiovascular comprovado —<br/>maior perda de peso esperada"])

  D3 -->|"Não"| C6(["Inibidor de SGLT2 ou agonista de<br/>GLP-1, conforme tolerância e<br/>preferência do paciente"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

- **A combinação das duas classes não é um ramo isolado da árvore, porque ela é
  compatível com qualquer um dos seis desfechos finais.** A metanálise em rede de Chuang
  et al. (CMAJ 2026, 99.683 participantes) estimou menor hospitalização por IC com a
  combinação frente a cada monoterapia, mas a comparação é de uma metanálise em rede e
  não equivale a um ensaio que randomizou diretamente combinação versus cada classe.
  Portanto, os RRs não devem ser apresentados como prova causal suficiente para combinar
  as classes; a decisão se apoia primeiro nas indicações independentes de cada uma e nas
  características do paciente.
- **A escolha por condição predominante é simplificação didática.** Na prática, um mesmo
  paciente costuma reunir mais de uma condição ao mesmo tempo (DRC e ASCVD, por exemplo)
  — a árvore segue a ordem de prioridade mais citada na literatura (IC primeiro, depois
  DRC, depois ASCVD isolada), mas a decisão final é sempre individualizada.
- **Generalização de classe para molécula não é automática.** As diretrizes especificam
  agentes com benefício cardiovascular ou renal demonstrado em trial dedicado — o
  resultado de um agente específico não deve ser presumido para toda a classe sem o
  próprio trial daquele fármaco.
- **Controle glicêmico continua sendo meta em paralelo**, mas não é o critério que decide
  esta escolha — as duas classes são indicadas por redução de risco cardiovascular e
  renal, independentemente do valor de HbA1c, e essa é justamente a mudança de lógica que
  a diretriz ESC 2023 introduziu (documentada no fluxograma diagnóstico geral desta
  pasta).
- **Contraindicações e efeitos adversos específicos de cada classe não são ramos** (risco
  de cetoacidose euglicêmica e de infecção genital com iSGLT2; efeitos gastrointestinais e
  risco de aspiração perioperatória com GLP-1, documentados em itens próprios desta
  pasta) — entram na decisão individual, não na estrutura geral do algoritmo.
