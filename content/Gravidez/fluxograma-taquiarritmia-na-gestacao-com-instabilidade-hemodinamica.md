---
title: "Fluxograma: Taquiarritmia na gestação com instabilidade hemodinâmica"
slug: fluxograma-taquiarritmia-na-gestacao-com-instabilidade-hemodinamica
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de emergência para TSV/FA/flutter na gestante, priorizando cardioversão sincronizada na instabilidade e manobras vagais/adenosina na taquicardia regular de QRS estreito estável."
review_status: revisado
review_note: "Sequência conferida diretamente nas seções 12.4.1.1–12.4.1.2 da ESC 2025 (PMID 40878294). Mantidas as doses da Figura 14 para adenosina, metoprolol e verapamil. Removido o encaminhamento automático de TSV estreita persistente ou ritmo não identificado para amiodarona: a diretriz restringe esse fármaco na gestação a arritmia refratária ou ameaçadora à vida sem alternativa eficaz, não ao próximo passo rotineiro da TSV estável."
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294. Seções 12.4.1.1 e 12.4.1.2."]
---

# Taquiarritmia na gestação

```mermaid
flowchart TD
  R0["Gestante com TSV, FA ou flutter<br/>e taquicardia sustentada"]
  D1{"Instabilidade hemodinâmica causada pela arritmia?<br/>hipotensão/choque, isquemia, edema pulmonar,<br/>alteração importante da consciência"}
  C1(["Sim: cardioversão elétrica sincronizada imediata;<br/>usar a MESMA energia indicada fora da gestação;<br/>monitorar FC fetal após cardioversão"])
  D2{"Estável + QRS estreito e regular<br/>compatível com AVNRT/AVRT?"}
  P1["Sim: manobras vagais / Valsalva modificada"]
  D3{"Reverteu?"}
  C2(["Sim: observação, ECG e investigação do substrato"])
  P2["Não: adenosina IV 6–18 mg em bolus<br/>conforme ESC 2025"]
  D4{"Reverteu/controle adequado?"}
  C3(["Sim: observar e planejar prevenção de recorrência"])
  P3["Não: considerar metoprolol IV 2,5–15 mg<br/>ou verapamil IV 2,5–10 mg em 5 min<br/>conforme mecanismo e condição materna;<br/>atenolol contraindicado"]
  D6{"Reverteu ou obteve<br/>controle adequado?"}
  C6(["Não: avaliação cardiológica/eletrofisiológica urgente;<br/>confirmar o mecanismo e considerar cardioversão<br/>sincronizada se houver persistência sintomática<br/>ou qualquer deterioração — não usar amiodarona<br/>automaticamente para TSV estreita estável"])
  D5{"FA/flutter estável?"}
  P4["Preferir estratégia de ritmo; se coração estruturalmente<br/>normal, flecainida/ibutilida podem ser consideradas;<br/>para frequência, beta-bloqueador, verapamil ou digoxina;<br/>avaliar HBPM/ETE e não usar DOAC na gestação"]
  C4(["Monitorar resposta e anticoagulação;<br/>se FA/flutter desestabilizar em qualquer momento:<br/>cardioversão sincronizada imediata"])
  C5(["Outro ritmo: confirmar mecanismo e seguir o<br/>algoritmo específico (por exemplo, QRS largo/TV<br/>ou FA pré-excitada); não escolher amiodarona<br/>antes de identificar o cenário"])

  R0 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P1
  D2 -->|"Não"| D5
  P1 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| P2
  P2 --> D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| P3
  P3 --> D6
  D6 -->|"Sim"| C3
  D6 -->|"Não"| C6
  D5 -->|"Sim"| P4
  D5 -->|"Não/outro ritmo"| C5
  P4 --> C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Regra prática

**Instabilidade materna vence a preocupação com a gestação:** cardioverter sem atraso. Na estável com AVNRT/AVRT, Valsalva e adenosina são o caminho inicial recomendado pela ESC 2025.

Falha de adenosina, metoprolol ou verapamil em uma TSV estreita estável não
transforma automaticamente o caso em indicação de amiodarona. É preciso
confirmar o mecanismo e reavaliar estabilidade; amiodarona fica restrita a
arritmia refratária ou ameaçadora à vida sem alternativa eficaz, não ao próximo
degrau rotineiro de AVNRT/AVRT.
