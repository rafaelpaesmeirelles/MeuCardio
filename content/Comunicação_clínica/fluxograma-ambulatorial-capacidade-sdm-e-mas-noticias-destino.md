---
title: "Fluxograma ambulatorial: capacidade, SDM e má notícia — pausar vs. seguir vs. retorno precoce"
slug: fluxograma-ambulatorial-capacidade-sdm-e-mas-noticias-destino
theme: "Comunicação clínica"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: gate de capacidade/ambiente → pausar SDM; braço de má notícia com choque → retorno precoce; braço capacidade OK → SDM (Elwyn/AHRQ)."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-capacidade-e-sdm-no-consultorio-cardiologico (07/09/2026). Appelbaum PMID 18003940; Elwyn PMID 22618581; AHRQ SHARE. Anti-colisão #832 teach-back e #847 crise psiquiátrica."
source_refs:
  - "Appelbaum PS. Assessment of patients' competence to consent to treatment. N Engl J Med. 2007;357(18):1834-1840. DOI: 10.1056/NEJMcp074045. PMID: 18003940"
  - "Elwyn G, Frosch D, Thomson R, et al. Shared decision making: a model for clinical practice. J Gen Intern Med. 2012;27(10):1361-1367. DOI: 10.1007/s11606-012-2077-6. PMID: 22618581"
  - "Agency for Healthcare Research and Quality. The SHARE Approach. https://www.ahrq.gov/health-literacy/professional-training/shared-decision/index.html"
---

# Fluxograma ambulatorial: capacidade, SDM e má notícia — destino

Prosa: [`sinalizadores-ambulatoriais-capacidade-e-sdm-no-consultorio-cardiologico`](sinalizadores-ambulatoriais-capacidade-e-sdm-no-consultorio-cardiologico.md). Checklist: [`checklist-ambulatorial-capacidade-consentimento-consulta-cardiologica`](checklist-ambulatorial-capacidade-consentimento-consulta-cardiologica.md). SPIKES (estrutura completa): [`fluxograma-protocolo-spikes-mas-noticias-cardiologia`](fluxograma-protocolo-spikes-mas-noticias-cardiologia.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial com decisão<br/>preferência-sensível e/ou má notícia"] --> D1{"Há dúvida de capacidade<br/>ou ambiente inadequado?<br/>compreender / apreciar<br/>raciocinar / expressar escolha<br/>dor, delírio, pressa, coerção"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PAUSAR SDM / consentimento<br/>da decisão não urgente<br/>Simplificar + suporte + documentar<br/>Não assinar sob pressão"])

  D1 -->|"Não"| D2{"Má notícia acabou de ser dada<br/>com choque emocional agudo?"}

  D2 -->|"Sim"| P1["Framing: setting + notícia curta<br/>Checar impacto; validar emoção<br/>(SPIKES já na pasta — não reescrever)"]
  P1 --> C2(["Adiar decision talk<br/>Retorno ambulatorial 24–72 h<br/>Orientação escrita de alarmes clínicos"])

  D2 -->|"Não / paciente pronto"| D3{"Decisão é preferência-sensível<br/>com mais de um caminho razoável?"}

  D3 -->|"Sim"| C3(["Seguir SDM<br/>Elwyn team/option/decision talk<br/>AHRQ SHARE — documentar"])
  D3 -->|"Não / recomendação clara"| C4(["Consentimento informado padrão<br/>+ educação; sem forçar menu artificial"])

  C1 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / urgência clínica sobe"| C5(["Antecipar retorno 24 h ou<br/>escalar suporte institucional<br/>Preservar segurança clínica"])
  D4 -->|"Sim"| C6(["Retorno 24–72 h para reavaliar<br/>capacidade e retomar SDM"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate Appelbaum (PMID 18003940) + ambiente.
- **D2** = framing ambulatorial de má notícia: não forçar *decision talk* sob choque.
- **D3** = SDM quando há verdadeira escolha (Elwyn PMID 22618581 / AHRQ SHARE).
- Não decide incapacidade legal, substituto, doses nem teach-back de alta.
