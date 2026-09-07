---
title: "Fluxograma ambulatorial: suspeita de febre reumática aguda — destino hospitalar"
slug: fluxograma-ambulatorial-suspeita-fra-destino-hospital
theme: "Febre reumática"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: alarme hemodinâmico → PS; sem alarme → hospital com eco Doppler + investigação Jones — sem doses nem reescrever critérios 2015."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-suspeita-febre-reumatica-aguda-quando-encaminhar (07/09/2026). Gewitz 2015 PMID 25908771; Ralph 2021 PMID 33190309; OMS 2024 PMID 39631006; WHF 2023 PMID 37914787. Anti-colisão #850 benzatina e Jones completo. Sem doses."
source_refs:
  - "Gewitz MH, et al. Revision of the Jones Criteria… AHA. Circulation. 2015;131(20):1806-1818. PMID: 25908771"
  - "Ralph AP, et al. The 2020 Australian guideline… Med J Aust. 2021;214(5):220-227. PMID: 33190309"
  - "World Health Organization. WHO guideline… rheumatic fever and rheumatic heart disease. 2024. PMID: 39631006"
  - "Rwebembera J, et al. 2023 WHF echocardiographic guidelines for RHD. Nat Rev Cardiol. 2024;21(4):250-263. PMID: 37914787"
---

# Fluxograma ambulatorial: suspeita de FRA — destino hospitalar

Prosa: [`sinalizadores-ambulatoriais-suspeita-febre-reumatica-aguda-quando-encaminhar`](sinalizadores-ambulatoriais-suspeita-febre-reumatica-aguda-quando-encaminhar.md). Checklist: [`checklist-ambulatorial-alarme-cardite-suspeita-fra`](checklist-ambulatorial-alarme-cardite-suspeita-fra.md). Diagnóstico: [`fluxograma-febre-reumatica-aguda-criterios-de-jones-2015`](fluxograma-febre-reumatica-aguda-criterios-de-jones-2015.md). Adesão benzatina (#850): [`fluxograma-ambulatorial-dose-perdida-benzatina-destino`](fluxograma-ambulatorial-dose-perdida-benzatina-destino.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>febre + artrite/artralgia<br/>ou coreia / sopro novo / pele<br/>em idade típica ou área endêmica"] --> D0{"Há pista de FRA?<br/>Jones pré-teste + estreptococo<br/>ou recorrência em FRA/CR conhecida"}

  D0 -->|"Não"| C0(["Investigar outras causas<br/>(infecção, Kawasaki, PSRA, etc.)<br/>Não forçar rótulo de FRA"])

  D0 -->|"Sim ou dúvida fundamentada"| D1{"Alarme de PS?<br/>hipotensão / hipoperfusão<br/>dispneia em repouso / edema agudo<br/>síncope / toxemia / déficit focal"}

  D1 -->|"Sim"| C1(["Encaminhar AGORA ao PS / urgência<br/>Não postergar por 'eco amanhã'"])

  D1 -->|"Não"| P1["Exame focado<br/>Evitar AINE até fechar/afastar FRA<br/>Solicitar/encaminhar eco Doppler"]
  P1 --> C2(["Hospital / unidade com eco<br/>horas a ≤48 h<br/>ECG + fase aguda + estreptococo<br/>Alarmes escritos"])

  C2 --> D2{"Eco / Jones disponíveis<br/>na mesma rede?"}
  D2 -->|"Sim — internar/observar"| C3(["Aplicar fluxograma Jones 2015<br/>Graduar cardite se presente<br/>— sem doses neste fluxograma"])
  D2 -->|"Só ambulatorial com eco ≤48 h"| C4(["Retorno 24–48 h<br/>Antecipar PS se surgir alarme"])
  D2 -->|"Sem acesso a eco"| C5(["Referência urgente a centro<br/>com Doppler — AHA 2015 Classe I<br/>em todo caso suspeito"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C0,C2,C3,C4,C5 conduta;
```

## Notas

- **D0** = filtro de suspeita clínica (pré-teste), não diagnóstico Jones completo.
- **D1** = gate de segurança (IC / choque / toxemia / AVC).
- **D2** = ponte para Jones 2015 + eco (Gewitz Classe I) e, se cardite, graduação SBC — **sem** doses de profilaxia ou AINE aqui.
- Não decide UI, mg, intervalo de benzatina nem duração por categoria (ver #850 e fluxograma de profilaxia).
