---
title: "Fluxograma ambulatorial: aortopatia em VAB e EA grave assintomática — quando escalar"
slug: fluxograma-ambulatorial-bicuspide-aortopatia-e-ea-assintomatica-quando-escalar
theme: "Valvopatias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore com dois eixos independentes: VAB/aortopatia (SAA vs avaliação prioritária vs vigilância) e EA grave assintomática (sintomas no esforço, queda pressórica isolada, FEVE e critérios de intervenção precoce)."
review_status: revisado
review_note: "Revisão clínica/editorial concluída em 08/09/2026. Removidos handoffs #840 inexistentes e prazos fixos; separados eixos VAB/aortopatia e EA; EA alinhada ao fluxograma ESC/EACTS 2025 canônico; sintomas provocados e queda pressórica isolada permanecem distintos; SAA é emergência independentemente do diâmetro conhecido."
source_refs:
  - "Mazzolai L, Teixido-Tura G, Lanzi S, et al. 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases. Eur Heart J. 2024;45(36):3538-3700. DOI: 10.1093/eurheartj/ehae179. PMID: 39210722"
  - "Praz F, Borger MA, Lanz J, et al.; ESC/EACTS Scientific Document Group. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4747. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295."
---

# Fluxograma ambulatorial: aortopatia em VAB e EA grave assintomática

Prosa VAB: [`sinalizadores-ambulatoriais-de-aortopatia-em-valva-aortica-bicuspide-quando-escalar`](sinalizadores-ambulatoriais-de-aortopatia-em-valva-aortica-bicuspide-quando-escalar.md).

Prosa EA: [`sinalizadores-ambulatoriais-de-estenose-aortica-assintomatica-grave-vigilancia`](sinalizadores-ambulatoriais-de-estenose-aortica-assintomatica-grave-vigilancia.md).

Fluxo formal de EA: [`fluxograma-estenose-aortica-assintomatica-grave-timing-de-intervencao-esc-eacts-2025`](fluxograma-estenose-aortica-assintomatica-grave-timing-de-intervencao-esc-eacts-2025.md).

Fluxo formal de SAA: [`fluxograma-sindrome-aortica-aguda-esc-2024`](../Aorta_e_doença_arterial_periférica/fluxograma-sindrome-aortica-aguda-esc-2024.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>VAB/aortopatia OU EA grave assintomática"] --> D0{"Qual é o eixo clínico principal?"}

  D0 -->|"VAB / aortopatia"| A1{"Suspeita clínica de SAA?<br/>dor súbita compatível, síncope associada,<br/>malperfusão, déficit neurológico ou instabilidade"}
  A1 -->|"Sim"| A2(["EMERGÊNCIA agora<br/>Seguir fluxograma SAA ESC 2024<br/>Independentemente do diâmetro conhecido"])
  A1 -->|"Não"| A3{"Há modificador que antecipe avaliação?<br/>fenótipo/diâmetro/indexação/crescimento,<br/>imagem inadequada, história familiar,<br/>coarctação, gestação ou cirurgia valvar"}
  A3 -->|"Sim"| A4(["Avaliação PRIORITÁRIA da equipe de aorta<br/>Prazo conforme risco e rede local<br/>Usar protocolo ESC 2024 para limiares"])
  A3 -->|"Não"| A5(["Vigilância estruturada da aorta<br/>Imagem seriada + educação de SAA"])

  D0 -->|"EA grave sem sintoma espontâneo"| E1{"Há sintoma espontâneo ou instabilidade?"}
  E1 -->|"Sim"| E2(["Reclassificar fora do eixo assintomático<br/>Via aguda se descompensado<br/>Avaliação valvar especializada"])
  E1 -->|"Não"| E3{"Teste de esforço factível/seguro<br/>provoca sintoma atribuível à EA?"}
  E3 -->|"Sim"| E4(["Reclassificar como SINTOMÁTICO<br/>Seguir indicação formal de intervenção"])
  E3 -->|"Não / não factível"| E5{"Queda sustentada da PA >20 mmHg<br/>sem sintomas no esforço?"}
  E5 -->|"Sim"| E6(["Critério separado: considerar intervenção<br/>IIa/C — NÃO chamar de sintomático"])
  E5 -->|"Não"| E7{"FEVE <50% sem outra causa?"}
  E7 -->|"Sim"| E8(["Intervenção recomendada<br/>Classe I/B"])
  E7 -->|"Não"| E9{"Alto gradiente + FEVE ≥50% +<br/>baixo risco procedimental +<br/>teste normal quando factível?"}
  E9 -->|"Sim"| E10(["Heart Team: intervenção precoce<br/>como alternativa à vigilância<br/>IIa/A — decisão compartilhada"])
  E9 -->|"Não"| E11{"Outro fator de alto risco ESC/EACTS 2025?<br/>FEVE <55%, estenose muito grave,<br/>progressão rápida ou BNP repetido >3x normal"}
  E11 -->|"Sim"| E12(["Abrir fluxo formal de timing<br/>Considerar intervenção IIa/B"])
  E11 -->|"Não"| E13(["Vigilância ativa estruturada<br/>clínica/eco + educação de sintomas"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef equipe fill:#e8f0fe,stroke:#1a56db,color:#0b1f4d;
  class A2,E2 alerta;
  class A5,E13 conduta;
  class A4,E4,E6,E8,E10,E12 equipe;
```

## Notas

- VAB/aortopatia e EA grave assintomática compartilham anatomia valvar, mas **não devem ser fundidas semanticamente** em relações clínicas fortes sem nexo específico.
- Assimetria de pulsos/PA isolada não é diagnóstico de SAA; ganha peso quando acompanha quadro compatível.
- O eixo EA usa a **diretriz ESC/EACTS 2025** já incorporada ao corpus e preserva a hierarquia de classes.
- Não há prazo universal de “dias” para Heart Team/equipe de aorta; prioridade é proporcional ao risco.
