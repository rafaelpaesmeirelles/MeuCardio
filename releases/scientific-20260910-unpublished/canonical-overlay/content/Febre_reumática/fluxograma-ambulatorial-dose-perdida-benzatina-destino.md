---
slug: fluxograma-ambulatorial-dose-perdida-benzatina-destino
title: 'Fluxograma ambulatorial: dose perdida de penicilina benzatina — destino'
kind: fluxograma
theme: Febre reumática
summary: 'Árvore ambulatorial de destino após atraso/omissão da intramuscular de penicilina G benzatina: gate de
  alarme para PS, braço de reagendamento + retorno precoce, e braço de falha repetida/recorrência para especialidade
  — sem doses.'
tags: []
source_refs:
- 'World Health Organization. WHO guideline on the prevention and diagnosis of rheumatic fever and rheumatic heart
  disease. Geneva: WHO; 2024. PMID: 39631006'
- 'Gerber MA; Baltimore RS; Eaton CB. Prevention of rheumatic fever and diagnosis and treatment of acute Streptococcal
  pharyngitis: a scientific statement from the American Heart Association Rheumatic Fever, Endocarditis, and Kawasaki
  Disease Committee of the Council on Cardiovascular Disease in the Young, the Interdisciplinary Council on Functional
  Genomics and Translational Biology, and the Interdisciplinary Council on Quality of Care and Outcomes Research:
  endorsed by the American Academy of Pediatrics. Circulation. 2009;119:1541. DOI: 10.1161/CIRCULATIONAHA.109.191959.
  PMID: 19246689.'
- 'Ralph AP; Noonan S; Boardman C. Prescribing for people with acute rheumatic fever. Aust Prescr. 2017;40:70. DOI:
  10.18773/austprescr.2017.011. PMID: 28507400.'
- 'Rwebembera J; Marangou J; Mwita JC. 2023 World Heart Federation guidelines for the echocardiographic diagnosis
  of rheumatic heart disease. Nat Rev Cardiol. 2024;21:250. DOI: 10.1038/s41569-023-00940-9. PMID: 37914787.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: dose perdida de penicilina benzatina — destino

Prosa: [sinalizadores-ambulatoriais-profilaxia-benzatina-dose-perdida-quando-agir](/biblioteca/sinalizadores-ambulatoriais-profilaxia-benzatina-dose-perdida-quando-agir). Checklist: [checklist-ambulatorial-alarme-progressao-cardiopatia-reumatica](/biblioteca/checklist-ambulatorial-alarme-progressao-cardiopatia-reumatica). Duração/esquema: [fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema](/biblioteca/fluxograma-profilaxia-secundaria-febre-reumatica-duracao-e-esquema).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Contato ambulatorial:<br/>atraso ou omissão da IM<br/>de penicilina G benzatina<br/>em profilaxia secundária"] --> D1{"Há alarme de PS?<br/>dispneia em repouso / edema agudo<br/>hipotensão / síncope<br/>déficit focal / febre + toxemia<br/>IC descompensada"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Não postergar por 'aplicar benzatina depois'"])

  D1 -->|"Não"| D2{"Há sintomas sugestivos de<br/>recorrência de FR ou progressão?<br/>febre, artrite migratória, coreia,<br/>sopro novo, cansaço novo,<br/>palpitação sem instabilidade"}

  D2 -->|"Sim"| P1["Exame focado + considerar Jones / eco<br/>se mudar conduta; registrar gap de adesão"]
  P1 --> C2["Avaliação médica no mesmo dia<br/>Suspeita de FRA/cardite: via hospital/eco<br/>Retorno só após avaliação inicial segura"]

  D2 -->|"Não (assintomático)"| D3{"Falhas repetidas de adesão<br/>ou recorrência documentada?"}

  D3 -->|"Sim — falhas repetidas<br/>ou recorrência prévia sob 28 dias"| C3(["Reagendar IM já + referência<br/>resolver barreiras e revisar esquema<br/>no protocolo dedicado — duração<br/>no fluxograma de profilaxia"])
  D3 -->|"Atraso pontual"| C4(["Reagendar IM o mais cedo possível<br/>plano escrito de alarmes<br/>confirmar efetivação da aplicação<br/>sem inventar consulta obrigatória"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora rápida"| C5(["Providenciar avaliação presencial em serviço acessível;<br/>piora rápida ou alarme exige urgência imediata"])
  D4 -->|"Sim"| C6(["Retorno definido após avaliação inicial<br/>não adiar investigação de FRA/cardite<br/>não inventar dose de reposição"])

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

## Salvaguardas de adesão e diagnóstico

Atraso isolado assintomático não é emergência nem exige retorno artificial: garantir aplicação o mais cedo possível e resolver estoque, transporte, dor ou medo. Não dobrar dose, inventar reposição, reiniciar série ou encurtar intervalo; seguir prescrição e protocolo dedicado. Falhas repetidas pedem intervenção de adesão; recorrência documentada pede avaliação especializada.

Febre, artrite migratória, coreia e sopro novo abrem investigação pelos critérios de Jones e diferenciais, sem confirmar recorrência isoladamente. Instabilidade, IC, deterioração ou manifestações neurológicas graves exigem avaliação imediata. Profilaxia não depende de eco anual para continuar; indicação/duração seguem história de FR/cardite/RHD e diretriz específica.
