---
title: "Fluxograma: indicação de ablação por cateter na fibrilação atrial (ESC 2024)"
slug: fluxograma-indicacao-ablacao-cateter-fa-esc-2024
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primária conferida — a tabela de recomendações de ablação da diretriz ESC 2024 (Eur Heart J. 2024;45(36):3314-3414) já havia sido lida na íntegra e registrada em documento do acervo em 30/07/2026; corroborado agora via WebFetch em resumo da ACC (Ten Points to Remember) e em artigo da EP Europace sobre os 10 aspectos-chave da diretriz. Nenhum PMID ou DOI foi inventado: o DOI da diretriz ESC 2024 é reaproveitado de citação já presente no acervo, sem PMID porque nenhum dos documentos-fonte anteriores registrou um."
source_refs:
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS. European Heart Journal. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176."
  - "Marrouche NF, Brachmann J, Andresen D, et al; CASTLE-AF Investigators. Catheter ablation for atrial fibrillation with heart failure (CASTLE-AF). New England Journal of Medicine. 2018;378(5):417-427. DOI: 10.1056/NEJMoa1707855. PMID: 29385358."
  - "2024 ESC Guidelines for Management of Atrial Fibrillation: Key Points · American College of Cardiology · 2024 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2024/09/17/04/05/2024-ESC-guidelines-for-AF-esc-2024 · consultado via WebFetch em 26/08/2026."
  - "Spotlight on the 2024 ESC/EACTS management of atrial fibrillation guidelines: 10 novel key aspects · EP Europace · 2024 · 26(12):euae298 · https://academic.oup.com/europace/article/26/12/euae298/7931832 · consultado via WebFetch em 26/08/2026."
  - "Derivado dos documentos já publicados no acervo 'Ablação por Cateter em Fibrilação Atrial: Indicações e Técnica' (content/Fibrilação_atrial/ablacao-por-cateter-em-fibrilacao-atrial-indicacoes-e-tecnica.md), que traz a tabela de recomendações da ESC 2024 lida na íntegra e resolvida por subgrupo (paroxística vs. persistente), e 'Controle de Ritmo vs. Frequência na Fibrilação Atrial: AFFIRM, EAST-AFNET 4 e CASTLE-AF' (content/Fibrilação_atrial/controle-de-ritmo-vs-frequencia-na-fibrilacao-atrial-affirm-east-afnet-4-e-castle-af.md), que traz os números do CASTLE-AF."
---

# Fluxograma: indicação de ablação por cateter na fibrilação atrial (ESC 2024)

A diretriz ESC 2024 reorganizou a indicação de ablação por cateter em três recomendações que coexistem lado a lado, para populações diferentes — e a leitura errada mais comum é tratá-las como uma sequência única (primeiro antiarrítmico, depois ablação) em vez de reconhecer que o padrão temporal da FA muda o ponto de entrada. Este fluxograma segue a árvore de decisão real da diretriz: exclusão de trombo em átrio esquerdo primeiro (única contraindicação absoluta), depois o contexto de insuficiência cardíaca (onde a evidência do CASTLE-AF justifica indicar ablação por benefício direto), depois a história prévia de antiarrítmico, e só então o padrão temporal — paroxística ou persistente — que determina se a ablação de primeira linha tem força Classe I/A ou Classe IIb/C.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com FA sintomática, sendo avaliado para controle de ritmo com ablação por cateter"] --> D1{"Trombo em átrio esquerdo confirmado por ETE, ou ausência de exclusão de trombo pré-procedimento?"}

  D1 -->|"Trombo presente, ou não excluído"| C1(["Contraindicação absoluta atual à ablação — é a única contraindicação absoluta da técnica.<br/>Anticoagular em dose terapêutica e repetir a ETE antes de reconsiderar o procedimento"])

  D1 -->|"Trombo excluído por ETE"| D2{"Há suspeita de cardiomiopatia induzida por taquicardia (disfunção de VE atribuída à FA) ou FA associada a IC sintomática com FEVE ≤35% (NYHA II-IV)?"}

  D2 -->|"Sim, um dos dois cenários"| P1["Base de evidência: CASTLE-AF (IC-FEr com desfibrilador) reduziu mortalidade por qualquer causa (HR 0,53) e hospitalização por piora de IC (HR 0,56) com ablação vs. terapia medicamentosa"]
  P1 --> C2(["Indicar ablação por cateter neste contexto — recomendação ESC 2024 para cardiomiopatia por taquicardia presumida, e a considerar em casos selecionados de FA com IC-FEr.<br/>Anticoagular por ≥3 semanas antes do procedimento, independentemente do CHA2DS2-VA; DOAC não interrompido durante; manter por 2 meses depois"])

  D2 -->|"Não, sem esse contexto"| D3{"Já houve falha terapêutica ou intolerância a pelo menos um antiarrítmico para controle de ritmo?"}

  D3 -->|"Sim, falhou ou não tolerou antiarrítmico"| P2["Anticoagular por ≥3 semanas antes do procedimento independentemente do CHA2DS2-VA; realizar a ablação com o DOAC não interrompido; manter anticoagulação por 2 meses após"]
  P2 --> C3(["Indicar ablação por cateter como segunda linha — Classe I, nível A (ESC 2024), válida tanto para FA paroxística quanto persistente.<br/>Decisão de manter ou suspender a anticoagulação após os 2 meses segue o CHA2DS2-VA, não o sucesso da ablação"])

  D3 -->|"Não, ainda sem tentativa de antiarrítmico"| D4{"Qual o padrão temporal predominante da FA?"}

  D4 -->|"Paroxística"| P3["Mesma preparação periprocedimento das demais indicações: anticoagular ≥3 semanas antes, DOAC não interrompido durante o procedimento, manter por 2 meses depois"]
  P3 --> C4(["Oferecer ablação por cateter como primeira linha dentro de decisão compartilhada — Classe I, nível A (ESC 2024), mesma força de evidência da indicação de segunda linha"])

  D4 -->|"Persistente"| D5{"Paciente selecionado para ablação de primeira linha (sintomas relevantes, decisão compartilhada, sem fatores de má resposta como átrio esquerdo muito dilatado)?"}

  D5 -->|"Sim, critérios de seleção presentes"| P4["Explicar expectativa de resultado inferior à da FA paroxística e maior chance de precisar de estratégias adjuvantes ao isolamento de veias pulmonares — parede posterior, gatilhos não relacionados a veia pulmonar, etanol na veia de Marshall"]
  P4 --> C5(["Ablação por cateter como primeira linha pode ser considerada em caso selecionado — Classe IIb, nível C (ESC 2024), evidência bem mais fraca que nas duas indicações anteriores"])

  D5 -->|"Não, sem critérios de seleção"| C6(["Iniciar controle de ritmo farmacológico com antiarrítmico.<br/>Reconsiderar ablação por cateter como segunda linha (Classe I, nível A) em caso de falha terapêutica ou intolerância"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**As três recomendações da ESC 2024 não são uma escada única.** Elas descrevem populações diferentes lado a lado na mesma tabela: ablação como segunda linha após falha/intolerância a antiarrítmico (Classe I, A, para paroxística **ou** persistente), ablação como primeira linha em FA paroxística dentro de decisão compartilhada (Classe I, A) e ablação como primeira linha em FA persistente só em pacientes selecionados (Classe IIb, C — evidência bem mais fraca). Tratar isso como "sempre tentar antiarrítmico primeiro" ignora que a paroxística já tem indicação de primeira linha com a força máxima da diretriz.

**O CABANA não entra nesta árvore como determinante da indicação.** O ensaio não mostrou diferença no desfecho primário composto por intenção de tratar (8,0% ablação vs. 9,2% terapia medicamentosa; HR 0,86; p=0,30), mas teve 27,5% de crossover do braço controle para ablação — motivo citado pelos próprios autores para não tratar esse resultado como palavra final. Os desfechos secundários (recorrência de FA, morte/hospitalização cardiovascular) favoreceram ablação. A diretriz ESC 2024 não se apoia no CABANA para as recomendações de força Classe I acima.

**Recidiva tardia por gatilho fora da veia pulmonar** é a causa mais citada de recorrência após um primeiro procedimento tecnicamente bem-sucedido, e é indicação típica de ablação repetida — cenário fora do escopo desta árvore, que trata da indicação inicial.

**FA assintomática de carga elevada** (detectada por ECG sistemático ou monitor com registro eletrocardiográfico, nunca por fotopletismografia isolada) também pode ser candidata a ablação na diretriz atual, mesmo sem o critério de sintoma explícito usado como ponto de partida nesta árvore.

**Tecnologia de ablação por campo pulsado (PFA)**, fonte de energia não térmica, não muda a indicação clínica mostrada aqui — a discussão sobre PFA é de técnica e perfil de segurança, não de quem deve ser indicado ao procedimento.
