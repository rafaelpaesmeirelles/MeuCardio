---
title: 'Fluxograma: estenose aórtica grave assintomática após EARLY TAVR'
slug: fluxograma-estenose-aortica-grave-assintomatica-apos-early-tavr
theme: Valvopatias
kind: fluxograma
review_status: revisado
source_refs:
- 'Généreux P et al. N Engl J Med. 2025;392:217-227. DOI: 10.1056/NEJMoa2405880. PMID: 39466903.'
- Praz F, Borger MA et al. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. DOI 10.1093/eurheartj/ehaf194.
  https://matcvs.org.my/documents/guidelines/2025%20ESC%20EACTS%20Valvular%20Heart%20Disease%20Guidelines.pdf
review_note: 'Corrigido ramo perigoso que encaminhava FE reduzida para vigilância por estar fora do EARLY TAVR. Incorporada
  diretriz primária2025IIaA para intervenção no assintomático selecionado e confirmação de sintomas; números do RCT conferidos.
  Tema canônico e links clinicamente pertinentes conferidos: early-tavr-estenose-aortica-grave-assintomatica, early-tavr-nao-e-partner-3-nem-e-mortalidade,
  early-tavr-o-que-nao-foi-mortalidade.'
summary: A ESC/EACTS 2025 recomenda considerar intervenção precoce como alternativa à vigilância ativa próxima em pacientes
  assintomáticos (teste de esforço normal quando viável), com estenose aórtica grave de alto gradiente, FEVE ≥50% e baixo
  risco do procedimento (IIa A). A escolha entre TAVI e cirurgia exige avaliação individual pelo Heart Team; esta classe não
  equivale a TAVI obrigatório para todos.
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: estenose aórtica grave assintomática após EARLY TAVR

## Contexto da decisão

A ESC/EACTS 2025 recomenda considerar intervenção precoce como alternativa à vigilância ativa próxima em pacientes assintomáticos (teste de esforço normal quando viável), com estenose aórtica grave de alto gradiente, FEVE ≥50% e baixo risco do procedimento (IIa A). A escolha entre TAVI e cirurgia exige avaliação individual pelo Heart Team; esta classe não equivale a TAVI obrigatório para todos.

Antes de classificar como assintomático, avaliar limitação de atividade e realizar teste de esforço quando viável. O fluxograma delimita a aplicação do ensaio e não substitui todas as indicações de tratamento da valvopatia.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Estenose aórtica grave"] --> D1{"Há sintomas?" }
  D1 -->|"Sim"| C1(["Intervenção conforme diretriz do sintomático — este ensaio não é sobre sintomático"])
  D1 -->|"Não"| D2{"FE preservada, idade compatível (>=65 no ensaio) e anatomia femoral para TAVI expansível por balão?"}
  D2 -->|"Não"| C2(["Fora do recorte EARLY TAVR: avaliar indicação de intervenção pela diretriz; FE reduzida pode indicar intervenção mesmo sem sintomas"])
  D2 -->|"Sim"| C3(["EARLY TAVR: composto morte/AVC/internação CV 26,8% vs 45,3%; HR 0,50. Morte isolada 8,4% vs 9,2% — decisão compartilhada no Heart Team, não automático"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Tudo com Tudo

- [EARLY TAVR: TAVI precoce na estenose aórtica grave assintomática](/biblioteca/early-tavr-estenose-aortica-grave-assintomatica)
- [EARLY TAVR e PARTNER 3: comparadores e desfechos diferentes](/biblioteca/early-tavr-nao-e-partner-3-nem-e-mortalidade)
- [EARLY TAVR: o que não foi mortalidade](/biblioteca/early-tavr-o-que-nao-foi-mortalidade)
