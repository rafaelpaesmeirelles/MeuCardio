---
title: 'Fluxograma: dor torácica na gestação — ESC 2025'
slug: fluxograma-dor-toracica-na-gestacao-esc-2025
theme: Gravidez
kind: fluxograma
review_status: revisado
review_note: Figura 11 e seção SCAD originais lidas. Corrigida confusão entre causa de SCA e causa de toda dor torácica; acrescentada
  estratégia conservadora da SCAD estável e removida implicação de ICP universal. Conexões temáticas selecionadas e links
  por slugs da fila conferidos.
source_refs:
- 'De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy.
  Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294. Figura 11: manejo da dor torácica na
  gravidez e até 6 meses pós-parto.'
- ESC. 2025 Essential Messages from the Guidelines for the management of Cardiovascular Disease and Pregnancy.
- ESC. 2025 official slides, Guidelines for the management of cardiovascular disease and pregnancy (DOI 10.1093/eurheartj/ehaf193).
  Tabela de doença coronária e gravidez.
legacy_source: Porta clínica de sca-na-gestacao-incluindo-scad-esc-2025.md. Equipe e mWHO 2.0 em esc-2025-doenca-cardiovascular-e-gravidez-equipe-e-mwho-20.md.
summary: 'A avaliação da dor torácica na gestante segue o mesmo protocolo da mulher não grávida: exame clínico, ECG, biomarcadores
  e ecocardiograma (Figura 11, até 6 meses pós-parto). A SCAD é uma causa importante de SCA associada à gestação e ao pós-parto;
  isso não significa que seja a principal causa de toda dor torácica.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: dor torácica na gestação — ESC 2025

A avaliação da dor torácica na gestante segue o mesmo protocolo da mulher não grávida: exame clínico, ECG, biomarcadores e ecocardiograma (Figura 11, até 6 meses pós-parto). A SCAD é uma causa importante de SCA associada à gestação e ao pós-parto; isso não significa que seja a principal causa de toda dor torácica.

Árvore: gestante com dor torácica → excluir TEP, SCA (incluindo SCAD) e síndrome aórtica aguda (**I C**) → se SCA, manejar como não gestante, incluindo investigação e intervenção (**I C**).

Parto vaginal é a primeira escolha na maioria das mulheres com DCV (**I B**). **Não** é o nó deste fluxograma: não usar via de parto para autorizar ou recusar angiografia, ICP ou tratamento de TEP/aorta.

```mermaid
flowchart TD
  R0["Gestante com dor torácica"]
  C0(["Excluir TEP, SCA incluindo SCAD<br/>e síndrome aórtica aguda — I C"])
  D1{"SCA confirmada<br/>ou altamente suspeita?"}
  C1(["Manejar como não gestante<br/>investigação e estratégia conforme risco e mecanismo — I C"])
  C2(["Seguir o diagnóstico diferencial<br/>TEP e síndrome aórtica aguda<br/>não saem da lista enquanto não excluídos"])
  N1["Parto vaginal: 1ª escolha na maioria das DCV — I B<br/>Não decide a SCA"]

  R0 --> C0
  C0 --> D1
  D1 -->|Sim| C1
  D1 -->|Não| C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2 conduta;
```

## Âncoras (só o verificado)

**Exclusão (I C).** Investigar as ameaças conforme a apresentação sem atrasar o tratamento urgente indicado. Não encerrar como “refluxo” ou “ansiedade” antes de afastar os três.

**SCA (I C).** Diagnóstico e intervenção iguais aos da não gestante. Estratégia invasiva **deve ser considerada** no NSTE-ACS de alto risco — **IIa C**. AAS em baixa dose quando antiagregação simples indicada — **I B**. Se DAP: clopidogrel é o P2Y12 de escolha — **I C**. Duração da DAP após stent: a mesma da não gestante, individualizando isquemia e sangramento no parto — **I C**.

**Via de parto.** Na DCV em geral: vaginal na maioria — **I B**. Na SCA: vaginal **deve ser considerado** na maioria, conforme FEVE e sintomas — **IIa C**. Essa linha **não** atrasa ICP.

**Ameaça à vida** (mensagem essencial, sem Classe/Nível extraído): desfibrilação, intervenções, revascularização coronária aguda, suporte circulatório mecânico e medicação iguais aos da não grávida, quando necessárias para salvar a vida, com avaliação emergencial de risco e benefício.

## O que a árvore não mostra

Na SCAD estável, sem isquemia persistente, geralmente se favorece tratamento conservador; instabilidade, isquemia em curso ou anatomia de alto risco podem exigir revascularização. A existência de lacunas de evidência não elimina essa orientação clínica. Não trata TEP nem síndrome aórtica — só obriga a excluí-los. Não substitui a *Pregnancy Heart Team* em mWHO 2.0 ≥ II–III.

## Tudo com Tudo

- [SCA na gestação, incluindo SCAD — ESC 2025](/biblioteca/sca-na-gestacao-incluindo-scad-esc-2025)
- [AAS e antiplaquetário na SCA gestacional — ESC 2025](/biblioteca/aas-e-antiplaquetario-na-sca-gestacional-esc-2025)
- [ESC 2025: doença cardiovascular e gravidez — Pregnancy Heart Team e mWHO 2.0](/biblioteca/esc-2025-doenca-cardiovascular-e-gravidez-equipe-e-mwho-20)
- [ESC 2025: insuficiência cardíaca aguda e choque na gestação](/biblioteca/esc-2025-ic-aguda-e-choque-na-gestacao)
