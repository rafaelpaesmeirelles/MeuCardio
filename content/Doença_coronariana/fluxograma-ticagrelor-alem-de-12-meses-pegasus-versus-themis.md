---
title: "Fluxograma: ticagrelor além de 12 meses — PLATO acabou, PEGASUS ou THEMIS?"
slug: fluxograma-ticagrelor-alem-de-12-meses-pegasus-versus-themis
theme: "Doença coronariana"
kind: fluxograma
summary: "Depois dos 12 meses de DAPT da SCA (PLATO), a pergunta de somar ticagrelor de novo só se abre com IAM prévio de 1–3 anos (PEGASUS). DAC estável + diabete sem IAM é o THEMIS — em geral não. Alto risco hemorrágico sai. Não mistura TWILIGHT (tirar AAS cedo)."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em PEGASUS (PMID 25773268), THEMIS (PMID 31475798) e PLATO (PMID 19717846). Classe ESC de DAPT estendida não relida. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Bonaca MP, et al. PEGASUS-TIMI 54. N Engl J Med. 2015;372(19):1791-1800. PMID: 25773268."
  - "Steg PG, et al. THEMIS. N Engl J Med. 2019;381(14):1309-1320. PMID: 31475798."
  - "Documentos da casa pegasus-timi-54-ticagrelor-apos-mais-de-um-ano-do-iam e themis-ticagrelor-na-dac-estavel-com-diabetes."
---

# Fluxograma: ticagrelor além de 12 meses — PEGASUS ou THEMIS?

```mermaid
flowchart TD
  R0["Paciente em AAS, DAPT da SCA já encerrada<br/>ou nunca teve SCA"] --> D1{"Ainda está nos primeiros 12 meses<br/>de uma SCA?"}

  D1 -->|"Sim"| C0(["Não é esta árvore.<br/>PLATO / fluxograma de escolha do P2Y12<br/>e de duração da DAPT"])

  D1 -->|"Não"| D2{"IAM há 1 a 3 anos<br/>(população PEGASUS)?"}

  D2 -->|"Sim"| D3{"Alto risco hemorrágico,<br/>AVC hemorrágico prévio ou<br/>sangramento maior recente?"}

  D3 -->|"Sim"| C1(["Não reabrir ticagrelor.<br/>PEGASUS: TIMI maior 2,3–2,6% vs 1,06%"])

  D3 -->|"Não — risco isquêmico residual alto"| C2(["Considerar ticagrelor 60 mg 2× + AAS.<br/>PEGASUS: composto 7,77% vs 9,04% (HR 0,84).<br/>ICH/fatal semelhantes ao placebo"])

  D2 -->|"Não"| D4{"DAC estável + diabete tipo 2,<br/>SEM IAM e SEM AVC (THEMIS)?"}

  D4 -->|"Sim"| C3(["Em geral NÃO somar ticagrelor.<br/>THEMIS: isquemia −0,8 pp, TIMI maior +1,2 pp"])

  D4 -->|"Não"| C4(["Sem evidência PEGASUS/THEMIS.<br/>Manter AAS. Não medicalizar com P2Y12 potente"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4 conduta;
```

## Mensagem prática

**IAM há 1–3 anos + baixo sangramento: PEGASUS pode reabrir o ticagrelor. Diabete estável sem IAM: THEMIS, em geral não.** Os 12 meses da SCA já foram o PLATO.
