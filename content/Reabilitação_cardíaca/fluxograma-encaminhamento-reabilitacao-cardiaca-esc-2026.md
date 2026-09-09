---
kind: fluxograma
published: true
review_note: 'Conferência individual: tabelas oficiais ESC RC 2026 por condição, modalidade
  e manejo psicossocial; consenso ESC 2025 Tables 4–5; ensaios STEP-HFpEF/SUMMIT/REDUCE-AMI
  e tabelas ESC IC/DRC para as trilhas. Corrigidas classes, limites de extrapolação,
  instrumentos e árvores sem convergência; identificadores não localizados substituídos
  por DOI verificado, sem inventar PMID.'
review_status: revisado
slug: fluxograma-encaminhamento-reabilitacao-cardiaca-esc-2026
source_refs:
- 'Bäck M, Wilhelm M, Hansen D, et al. 2026 ESC Guidelines on cardiac rehabilitation.
  Eur Heart J. 2026. DOI: 10.1093/eurheartj/ehag099.'
- ESC press release, 28 August 2026.
- Bäck M, Wilhelm M, Hansen D, et al. 2026 ESC Guidelines on cardiac rehabilitation.
  DOI 10.1093/eurheartj/ehag099. Official ESC slides, recommendation tables by condition,
  psychosocial management and delivery models.
theme: Cardiologia do Esporte e do Exercício
title: 'Fluxograma: encaminhamento para reabilitação cardíaca — ESC 2026'
---

# Fluxograma: encaminhamento para reabilitação cardíaca — ESC 2026

Avaliar condição índice, risco e objetivos. A classe abaixo se refere ao desfecho indicado, não a qualquer benefício em qualquer paciente.

```mermaid
flowchart TD
  R0["Avaliação para programa de reabilitação cardíaca"] --> D1{"Condição clínica e objetivo"}
  D1 -->|"SCA ou síndrome coronariana crônica"| C1(["RC I A: mortalidade CV e infarto; I B1: hospitalização, função e qualidade de vida"])
  D1 -->|"IC crônica com FE reduzida"| C2(["RC I B1: hospitalização por qualquer causa, função e qualidade de vida"])
  D1 -->|"IC com FE preservada"| C3(["RC I B1: função e qualidade de vida; IIa B1: hospitalização por qualquer causa"])
  D1 -->|"Estenose aórtica após SAVR ou TAVI"| C4(["RC I B1: função física, mental e qualidade de vida"])
  D1 -->|"FA selecionada"| C5(["Considerar RC IIa B1: sintomas, recorrência, função e qualidade de vida"])
  D1 -->|"Congênita adulta/transição com baixa capacidade ou após cirurgia"| C6(["RC I B1: função física e qualidade de vida"])
  D1 -->|"Cardio-oncologia: alto risco de cardiotoxicidade"| C7(["Considerar reabilitação cardio-oncológica IIa B1: função, qualidade de vida e fatores de risco"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Escolha da modalidade e segurança

Na ESC 2026, telereabilitação em DAC ou IC é IIa B1; em cardiopatia congênita, FA ou cardio-oncologia, IIa B2; após intervenção/cirurgia valvar, IIb B2. A seleção depende do risco, da capacidade de participação e dos recursos do programa. RC hospitalar para pacientes de alto risco ou instáveis é I C; isso não autoriza exercício durante instabilidade clínica.

O início de treinamento exige estabilidade e prescrição individualizada. A reabilitação precoce durante internação por IC descompensada pode ser considerada após estabilização. Outras indicações, como dispositivos, fragilidade e hipertensão pulmonar, exigem a avaliação específica da diretriz.

## Tudo com Tudo

Reabilitação cardíaca · Doença coronariana · Insuficiência cardíaca · Valvopatias · Fibrilação atrial · Cardiopatias congênitas · Cardio-oncologia.

## Conteúdo clínico relacionado

- [Indicações de reabilitação cardíaca pela ESC 2026 — portas de entrada por condição](/biblioteca/indicacoes-de-reabilitacao-cardiaca-esc-2026-por-condicao)
- [Reabilitação cardíaca após SCA: porta de entrada ESC 2026](/biblioteca/reabilitacao-cardiaca-apos-sca-porta-de-entrada-esc-2026)
