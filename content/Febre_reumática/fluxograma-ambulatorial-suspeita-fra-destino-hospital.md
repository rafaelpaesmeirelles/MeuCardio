---
title: "Fluxograma ambulatorial: suspeita de febre reumática aguda — destino hospitalar"
slug: fluxograma-ambulatorial-suspeita-fra-destino-hospital
theme: "Febre reumática"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: alarme hemodinâmico → PS; sem alarme → hospital com eco Doppler + investigação Jones — sem doses nem reescrever critérios 2015."
review_status: revisado
review_note: "Revisão consolidada: reconstruídas exceção da coreia, erradicação durante suspeita e ligações canônicas ausentes no HEAD remoto4e8fb13 apesar de comentário local564719. Eco em toda suspeita; critérios Jones preservados; Australian guideline3.3/2025 conferida; sem doses novas."
source_refs:
  - "RHD Australia. Australian guideline for prevention, diagnosis and management of acute rheumatic fever and rheumatic heart disease. Edition3.3, August2025. https://www.rhdaustralia.org.au/wp-content/uploads/2025/09/Australian-ARF-RHD-Guideline-2025_August_1.pdf"
  - "Gewitz MH, et al. Revision of the Jones Criteria… AHA. Circulation. 2015;131(20):1806-1818. PMID: 25908771"
  - "Ralph AP, et al. The 2020 Australian guideline… Med J Aust. 2021;214(5):220-227. PMID: 33190309"
  - "World Health Organization. WHO guideline… rheumatic fever and rheumatic heart disease. 2024. PMID: 39631006"
  - "Rwebembera J, et al. 2023 WHF echocardiographic guidelines for RHD. Nat Rev Cardiol. 2024;21(4):250-263. PMID: 37914787"
---

# Fluxograma ambulatorial: suspeita de FRA — destino hospitalar

Prosa: [sinalizadores-ambulatoriais-suspeita-febre-reumatica-aguda-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-suspeita-febre-reumatica-aguda-quando-encaminhar). Checklist: [checklist-ambulatorial-alarme-cardite-suspeita-fra](/biblioteca/checklist-ambulatorial-alarme-cardite-suspeita-fra). Diagnóstico: [fluxograma-febre-reumatica-aguda-criterios-de-jones-2015](/biblioteca/fluxograma-febre-reumatica-aguda-criterios-de-jones-2015). Adesão benzatina (#850): [febre-reumatica-aguda-na-crianca-criterios-de-jones-2015-e-tratamento-da-fase-aguda](/biblioteca/febre-reumatica-aguda-na-crianca-criterios-de-jones-2015-e-tratamento-da-fase-aguda).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>febre + artrite/artralgia<br/>ou coreia / sopro novo / pele<br/>em idade típica ou área endêmica"] --> D0{"Há pista de FRA?<br/>Jones pré-teste + estreptococo<br/>OU coreia de Sydenham isolada<br/>(exceção sem prova estreptocócica)<br/>ou recorrência em FRA/CR conhecida"}

  D0 -->|"Não"| C0(["Investigar outras causas<br/>(infecção, Kawasaki, PSRA, etc.)<br/>Não forçar rótulo de FRA"])

  D0 -->|"Sim ou dúvida fundamentada"| D1{"Alarme de PS?<br/>hipotensão / hipoperfusão<br/>dispneia em repouso / edema agudo<br/>síncope / toxemia / déficit focal"}

  D1 -->|"Sim"| C1(["Encaminhar AGORA ao PS / urgência<br/>Não postergar por 'eco amanhã'"])

  D1 -->|"Não"| P1["Exame focado<br/>Analgesia sem mascarar evolução<br/>Eco Doppler em toda suspeita<br/>Acionar tratamento agudo/erradicação"]
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

- Coreia isolada pode ocorrer sem evidência estreptocócica; excluir alternativas e manter eco.
- [Tratamento agudo/erradicação](/biblioteca/febre-reumatica-aguda-na-crianca-criterios-de-jones-2015-e-tratamento-da-fase-aguda): não adiar somente porque confirmação está pendente; hemoculturas se febril sem atrasar emergência.

- **D0** = filtro de suspeita clínica (pré-teste), não diagnóstico Jones completo.
- **D1** = gate de segurança (IC / choque / toxemia / AVC).
- **D2** = ponte para Jones 2015 + eco (Gewitz Classe I) e, se cardite, graduação SBC — **sem** doses de profilaxia ou AINE aqui.
- Não decide UI, mg, intervalo de benzatina nem duração por categoria (ver #850 e fluxograma de profilaxia).
