---
kind: fluxograma
published: true
review_note: Conferência individual CASTLE-AF, CASTLE-HTx e RAFT-AF contra resumos
  primários; ESC FA 2024 PDF Tables 6/10 e recomendações de frequência/ablação; ESC
  IC 2026 Table 15 e DRC 2026. Resolvidos PMID 39210723, classes por documento e indicação,
  exceções ao escore, FA subclínica e elegibilidade de DOAC; fluxo refeito sem convergência
  e sem classificar FEVE >35 como necessariamente preservada.
review_status: revisado
slug: fluxograma-fa-sintomatica-na-icfer-apos-castle-af
source_refs:
- Marrouche NF, et al. Catheter Ablation for Atrial Fibrillation with Heart Failure.
  N Engl J Med. 2018;378:417-427. PMID 29385358.
- Køber L, Adamo M et al. ESC HF 2026. DOI 10.1093/eurheartj/ehag100. PMID 42661420;
  Table 15.
- Van Gelder IC, Rienstra M et al. ESC AF 2024. DOI 10.1093/eurheartj/ehae176. PMID
  39210723; Tables 6, 10, rate control and ablation recommendations.
theme: Fibrilação atrial
title: 'Fluxograma: FA sintomática na ICFEr após CASTLE-AF'
---

# Fluxograma: FA sintomática na ICFEr após CASTLE-AF

CASTLE-AF: FEVE ≤35%, CDI, FA sintomática. Composto morte/hosp. IC 28,5% vs 44,6%; HR 0,62. Não é ICFEp. A ESC IC 2026, Tabela 15, classifica ablação por cateter como IIa C em selecionados com FA sintomática e ICFEr, visando qualidade de vida e redução de hospitalização por IC ou morte. Essa é a linha da diretriz de IC de 2026; a ESC FA 2024 tem uma indicação específica I B quando há alta probabilidade de cardiomiopatia induzida por taquicardia, e IIa B em outros selecionados com ICFEr. Não atribuir a mesma classe a todas as situações nem transferir o resultado do CASTLE-AF para qualquer FEVE.

## Árvore de decisão

```mermaid
flowchart TD
  X0["Paciente com FA e IC"]
  D0{"FEVE ≤ 35% — recorte CASTLE-AF?"}
  C0(["FEVE >35% está fora do CASTLE-AF; avaliar o fenótipo real e as demais indicações de ablação. Não rotular toda FEVE >35% como preservada"])
  D1{"CDI já implantado?"}
  C1(["CASTLE-AF entrou com CDI. Não pular prevenção súbita. Discutir dispositivo em paralelo"])
  D2{"FA sintomática — não resposta, intolerância ou recusa de antiarrítmico?"}
  C2(["FA oligossintomática: CASTLE-AF não é ensaio de ablação profilática. Otimizar quádrupla e frequência"])
  D3{"Quádrupla da ICFEr em curso?"}
  C3(["Otimizar terapia fundacional em paralelo à avaliação de ritmo; ablação não substitui a base"])
  C4(["Discutir ablação de FA: composto 51/179 vs 82/184; HR 0,62. Morte 13,4% vs 25,0%. Centro de FA+IC"])
  C5(["Manter estratégia médica de ritmo/frequência se ablação inviável ou recusada. Recalcular CHA2DS2-VA"])

  X0 --> D0
  D0 -->|"Não — FEVE acima de 35%"| C0
  D0 -->|"Sim"| D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| D3
  D3 -->|"Base incompleta"| C3
  D3 -->|"Base feita — paciente concorda com ablação"| C4
  D3 -->|"Ablação inviável ou recusada"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f
  class C0,C1,C2,C3,C4,C5 conduta
```

## Tudo com Tudo

- Fibrilação atrial
- Insuficiência cardíaca
- Dispositivos
- Arritmias
- Comunicação clínica

Instabilidade hemodinâmica com FA rápida exige avaliação urgente para cardioversão, antes desta árvore eletiva. A ausência de CDI limita a reprodução do CASTLE-AF, mas não é contraindicação universal à ablação. Avaliar anticoagulação pelo risco e pelo contexto, independentemente do aparente sucesso de controle do ritmo.
