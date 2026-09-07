---
title: "Fluxograma ambulatorial: cascata familiar na HF — destino e porta para lipidologia"
slug: fluxograma-ambulatorial-cascata-hf-destino-e-lipidologia
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: caso-índice HF/HoFH → cascata de 1º grau vs não cascata; parente positivo → novo índice; portas para clínica de lipídios. Sem doses."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-rastreio-familiar-cascata-hf-quando-iniciar (07/09/2026). ESC/EAS 2019 PMID 31504418; ESC/EAS 2025 PMID 40878289; Nordestgaard PMID 23956253; Cuchel PMID 37130090. Anti-colisão #854/#875 e docs DLCN/Lp(a) já revisados."
source_refs:
  - "Mach F, Baigent C, Catapano AL, et al. 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2020;41(1):111-188. DOI: 10.1093/eurheartj/ehz455. PMID: 31504418"
  - "Mach F, Koskinas KC, Roeters van Lennep J, et al. 2025 Focused Update of the 2019 ESC/EAS Guidelines for the management of dyslipidaemias. Eur Heart J. 2025;46(42):4359-4378. DOI: 10.1093/eurheartj/ehaf190. PMID: 40878289"
  - "Nordestgaard BG, Chapman MJ, Humphries SE, et al. Familial hypercholesterolaemia is underdiagnosed and undertreated: EAS consensus. Eur Heart J. 2013;34(45):3478-3490. DOI: 10.1093/eurheartj/eht273. PMID: 23956253"
  - "Cuchel M, Raal FJ, Hegele RA, et al. 2023 Update on EAS Consensus Statement on Homozygous Familial Hypercholesterolaemia. Eur Heart J. 2023;44(25):2277-2291. DOI: 10.1093/eurheartj/ehad197. PMID: 37130090"
---

# Fluxograma ambulatorial: cascata HF — destino e lipidologia

Prosa: [`sinalizadores-ambulatoriais-rastreio-familiar-cascata-hf-quando-iniciar`](sinalizadores-ambulatoriais-rastreio-familiar-cascata-hf-quando-iniciar.md). Encaminhar lipidologia: [`checklist-ambulatorial-encaminhar-clinica-de-lipidios-ldl-refratario-hofh`](checklist-ambulatorial-encaminhar-clinica-de-lipidios-ldl-refratario-hofh.md). Diagnóstico DLCN: [`fluxograma-hipercolesterolemia-familiar-diagnostico-dlcn-e-manejo-esc-eas-2025`](fluxograma-hipercolesterolemia-familiar-diagnostico-dlcn-e-manejo-esc-eas-2025.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: caso-índice com suspeita\nou diagnóstico de HF"] --> D1{"DLCN ≥6\n(HF definitiva/provável)\nOU mutação patogênica\nOU critérios de HoFH?"}

  D1 -->|"Não — DLCN 3–5"| C1(["Ainda não expandir cascata\nExcluir secundárias + repetir LDL\nConsiderar DNA antes de alargar"])

  D1 -->|"Não — DLCN ≤2"| C2(["Não iniciar cascata de HF\nInvestigar outra dislipidemia"])

  D1 -->|"Sim"| D2{"Há critérios de HoFH?\nLDL extremo + xantomas precoces\nou ambos os pais com HF"}

  D2 -->|"Sim"| C3(["Cascata URGENTE: pais e irmãos\n+ encaminhar lipidologia/centro\n(ver checklist irmão)\nSem doses neste fluxograma"])

  D2 -->|"Não"| P1["Oferecer cascata de 1º grau\npais, irmãos, filhos\nESC/EAS Classe I Nível C"]
  P1 --> D3{"Parente aceitou\navaliação?"}

  D3 -->|"Não / recusa"| C4(["Documentar oferta e recusa\nReoferecer em retornos\nNão pressionar DNA sem consentimento"])

  D3 -->|"Sim"| P2["LDL (± DNA dirigido à\nvariante do índice)\nRegistrar terapia em uso"]
  P2 --> D4{"Parente positivo\n(LDL muito alto / mesma\nmutação / DLCN alto)?"}

  D4 -->|"Não"| C5(["Excluir da cascata ativa\nOrientar fatores de risco usuais\nLp(a) uma vez se adulto"])

  D4 -->|"Sim"| C6(["Tratar como NOVO caso-índice\nAbrir protocolo DLCN/HF\nOferecer cascata do novo anel\nLipidologia se refratário/HoFH"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C3 alerta;
  class C1,C2,C4,C5,C6 conduta;
```

## Notas

- **D1**: gate — só cascata de HF com probabilidade clínica suficiente (Nordestgaard/ESC).
- **D2/C3**: HoFH não espera o mesmo prazo da HeFH estável (Cuchel 2023).
- **D3**: oferta documentada > “fale com sua família” sem registro.
- **D4/C6**: cada positivo reinicia o anel — essência da cascata.
- Não decide doses, aférese nem esquema de iPCSK9.
