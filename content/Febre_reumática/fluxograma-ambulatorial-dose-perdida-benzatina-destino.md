---
title: "Fluxograma ambulatorial: dose perdida de penicilina benzatina — destino"
slug: fluxograma-ambulatorial-dose-perdida-benzatina-destino
theme: "Febre reumática"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino após atraso/omissão da intramuscular de penicilina G benzatina: gate de alarme para PS, braço de reagendamento + retorno precoce, e braço de falha repetida/recorrência para especialidade — sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-profilaxia-benzatina-dose-perdida-quando-agir (07/09/2026). Fontes: OMS 2024 PMID 39631006; AHA 2009 PMID 19246689; Ralph 2017 PMID 28507400; WHF 2023 PMID 37914787. Sem doses; anti-colisão com fluxograma de duração/esquema e estadiamento WHF."
source_refs:
  - "World Health Organization. WHO guideline on the prevention and diagnosis of rheumatic fever and rheumatic heart disease. Geneva: WHO; 2024. PMID: 39631006"
  - "Gerber MA, et al. AHA Scientific Statement. Circulation. 2009;119(11):1541-1551. PMID: 19246689"
  - "Ralph AP, et al. Prescribing for people with acute rheumatic fever. Aust Prescr. 2017;40(2):70-75. PMID: 28507400"
  - "Rwebembera J, et al. 2023 WHF echocardiographic guidelines for RHD. Nat Rev Cardiol. 2024;21(4):250-263. PMID: 37914787"
---

# Fluxograma ambulatorial: dose perdida de penicilina benzatina — destino

Prosa: [`sinalizadores-ambulatoriais-profilaxia-benzatina-dose-perdida-quando-agir`](sinalizadores-ambulatoriais-profilaxia-benzatina-dose-perdida-quando-agir.md). Checklist: [`checklist-ambulatorial-alarme-progressao-cardiopatia-reumatica`](checklist-ambulatorial-alarme-progressao-cardiopatia-reumatica.md). Duração/esquema: [`fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema`](fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Contato ambulatorial:<br/>atraso ou omissão da IM<br/>de penicilina G benzatina<br/>em profilaxia secundária"] --> D1{"Há alarme de PS?<br/>dispneia em repouso / edema agudo<br/>hipotensão / síncope<br/>déficit focal / febre + toxemia<br/>IC descompensada"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Não postergar por 'aplicar benzatina depois'"])

  D1 -->|"Não"| D2{"Há sintomas sugestivos de<br/>recorrência de FR ou progressão?<br/>febre, artrite migratória, coreia,<br/>sopro novo, cansaço novo,<br/>palpitação sem instabilidade"}

  D2 -->|"Sim"| P1["Exame focado + considerar Jones / eco<br/>se mudar conduta; registrar gap de adesão"]
  P1 --> C2(["Retorno ambulatorial 24–72 h<br/>ou referência se cardite/valvopatia<br/>em evolução — sem doses aqui"])

  D2 -->|"Não (assintomático)"| D3{"Gap ≥1 ciclo previsto<br/>ou falhas repetidas / estoque?"}

  D3 -->|"Sim — falhas repetidas<br/>ou recorrência prévia sob 28 dias"| C3(["Reagendar IM já + referência<br/>discutir adesão e possível ajuste<br/>de intervalo (AHA 2009) — duração<br/>no fluxograma de profilaxia"])
  D3 -->|"Atraso pontual"| C4(["Reagendar IM o mais cedo possível<br/>plano escrito de alarmes<br/>retorno ≤7 dias se data não estiver<br/>garantida no mesmo dia"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora rápida"| C5(["Antecipar retorno 24 h ou PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h<br/>não inventar dose de reposição aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (descompensação / embolia / toxemia).
- **D2** = suspeita de recorrência ou progressão ambulatorial → destino clínico precoce (ponte a Jones / WHF, não a doses).
- **D3** = adesão e sistema (OMS 2024 + Ralph 2017); intervalo AHA 2009 só como ponte ao especialista.
- Não decide UI, mg, intervalo-padrão nem duração por idade/gravidade.
