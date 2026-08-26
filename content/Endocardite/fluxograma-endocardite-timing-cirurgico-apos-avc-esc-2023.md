---
title: "Fluxograma: Timing cirúrgico na endocardite infecciosa após complicação neurológica (ESC 2023)"
slug: fluxograma-endocardite-timing-cirurgico-apos-avc-esc-2023
theme: "Endocardite"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Auditoria científica em 26/08/2026 contra a Seção 10.4 e a Tabela de Recomendação 17 da ESC 2023 (PMID 37622656). Confirmados cirurgia sem atraso após AIT/AVC não hemorrágico quando indicada, adiamento superior a 1 mês na hemorragia estável e decisão urgente individualizada na instabilidade. Mantida pendência de revisão médica antes da publicação clínica."
source_refs: ["Delgado V, Ajmone Marsan N, de Waha S, et al.; ESC Scientific Document Group. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656 — Seção 10.4 ('Timing of surgery after ischaemic and haemorrhagic stroke') e Recommendation Table 17, texto integral já lido linha a linha e citado no documento 'timing-cirurgico-apos-avc-na-endocardite-infecciosa-esc-2023.md' desta pasta."]
---

# Fluxograma: Timing cirúrgico na endocardite infecciosa após complicação neurológica (ESC 2023)

O documento geral de indicações e timing cirúrgico já publicado nesta pasta cobre as três
famílias de indicação — insuficiência cardíaca, infecção não controlada e risco embólico —
e seus prazos gerais. Este fluxograma isola a decisão mais frequentemente mal aplicada na
prática: o que fazer quando a indicação cirúrgica já existe e o paciente teve uma
complicação neurológica. A condição central da diretriz não é "o AVC foi isquêmico ou
hemorrágico", e sim se o coma está ausente e a hemorragia cerebral já foi excluída por
imagem.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Endocardite infecciosa com indicação cirúrgica<br/>já estabelecida insuficiência cardíaca,<br/>infecção não controlada ou risco embólico alto<br/>e complicação neurológica recente"] --> D1{"O evento neurológico foi um ataque<br/>isquêmico transitório AIT, sem déficit<br/>persistente e sem lesão estabelecida em imagem?"}

  D1 -->|"Sim"| C1(["Cirurgia cardíaca sem atraso<br/>Classe I, Nível B"])

  D1 -->|"Não, houve AVC<br/>estabelecido isquêmico ou hemorrágico"| D2{"TC ou RM de crânio já excluiu<br/>hemorragia cerebral E o paciente<br/>está com coma ausente?"}

  D2 -->|"Sim"| C2(["Cirurgia cardíaca sem qualquer atraso,<br/>na presença de insuficiência cardíaca,<br/>infecção não controlada, abscesso<br/>ou risco embólico persistentemente alto<br/>Classe I, Nível B"])

  D2 -->|"Não, coma presente<br/>ou hemorragia confirmada<br/>ou ainda não excluída por imagem"| D3{"Hemorragia intracraniana<br/>confirmada por imagem?"}

  D3 -->|"Sim, e paciente<br/>clinicamente estável"| C3(["Considerar adiar a cirurgia cardíaca<br/>por mais de 1 mês, com reavaliação<br/>clínica e de imagem frequente<br/>Classe IIa, Nível C"])

  D3 -->|"Sim, mas paciente clinicamente<br/>instável por insuficiência cardíaca,<br/>infecção não controlada ou risco<br/>embólico persistentemente alto"| C4(["Considerar cirurgia urgente ou de<br/>emergência, ponderando a probabilidade<br/>de desfecho neurológico significativo<br/>Classe IIa, Nível C"])

  D3 -->|"Não confirmada, hemorragia<br/>ainda não excluída por imagem<br/>ou coma por outra causa"| C5(["Aguardar neuroimagem conclusiva e<br/>reavaliação do nível de consciência antes<br/>de aplicar a recomendação de cirurgia<br/>sem atraso — não classificar o paciente<br/>sem TC ou RM atualizada"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

- **Trombólise é formalmente contraindicada** no AVC embólico por endocardite infecciosa —
  Classe III, Nível C — ao contrário do AVC isquêmico de outras etiologias, em que a
  trombólise é conduta padrão. Essa contraindicação é decisão paralela ao timing cirúrgico,
  não um ramo da árvore acima.
- **Aneurisma micótico (infeccioso) muda o plano de investigação.** TC ou angio-RM de crânio
  é recomendada (Classe I, Nível B) quando há suspeita de aneurisma cerebral infeccioso;
  neurocirurgia ou terapia endovascular é recomendada (Classe I, Nível C) para aneurismas
  grandes, em crescimento apesar de antibioticoterapia ótima, ou rotos. A árvore trata só do
  timing da cirurgia cardíaca — a via de tratamento do próprio aneurisma é decisão paralela.
- **Números de contexto que pesam na decisão clínica, mas não mudam a classificação
  formal**: o risco de transformação hemorrágica pós-operatória após AVC pré-operatório é de
  2 a 7%, ocorrendo com frequência semelhante em quem teve embolismo cerebral silencioso
  (achado só por imagem); quando ocorre, associa-se a mortalidade de 40%. A mortalidade
  cirúrgica hospitalar da endocardite em geral é de 10 a 20%, particularmente acima de
  75 anos, por comorbidade e complicação da própria endocardite — não especificamente por
  AVC prévio.
- **A regra de "mais de 1 mês" no AVC hemorrágico não é absoluta.** Estudos retrospectivos
  relatam benefício de cirurgia precoce (dentro de 2 semanas) em casos selecionados, sem
  piorar desfecho — mas a diretriz não eleva isso a recomendação formal, mantendo o adiamento
  padrão como Classe IIa.
- **Este fluxograma não substitui o documento geral de indicação e timing cirúrgico** já
  publicado nesta pasta — é o complemento específico da Seção 10.4 (complicação
  neurológica), pressupondo que uma das três indicações cirúrgicas gerais já foi confirmada.
