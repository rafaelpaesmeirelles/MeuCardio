---
title: 'Fluxograma: pericardite recorrente — ESC 2025, AIRTRIP e RHAPSODY'
slug: fluxograma-pericardite-recorrente-esc-2025
theme: Pericárdio
kind: fluxograma
review_status: revisado
source_refs:
- 'Schulz-Menger J, Collini V, Gröschel J, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis.
  Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297.'
- 'Brucato A, Imazio M, Gattorno M, et al. Effect of Anakinra on Recurrent Pericarditis Among Patients With Colchicine Resistance
  and Corticosteroid Dependence: The AIRTRIP Randomized Clinical Trial. JAMA. 2016;316(18):1906-1912. DOI: 10.1001/jama.2016.15826.
  PMID: 27825009.'
- 'Klein AL, Imazio M, Cremer P, et al. Phase 3 Trial of Interleukin-1 Trap Rilonacept in Recurrent Pericarditis. N Engl J
  Med. 2021;384(1):31-41. DOI: 10.1056/NEJMoa2027892. PMID: 33200890. NCT03737110.'
- ESC2025 official slides, Myocarditis and Pericarditis, pp.50,53,77. https://www.escardio.org/static-file/Escardio/Guidelines/Products/Slide%20sets/2025/2025%20official%20slides_MyoPeri.pdf
review_note: 'Leitura integral e AIRTRIP/RHAPSODY primários conferidos. Árvore corrigida para explicitar linha de corticoide
  antes antiIL1, IIa C com RMC e drenagem cirúrgica purulenta independentemente de factibilidade de punção. Dúvida regulatória
  preservada como limite de aplicação, sem afirmar aprovação. Tema canônico e links clinicamente pertinentes conferidos: esc-2025-miocardite-e-pericardite-o-que-muda-na-porta-pericardio,
  icap-colchicina-no-primeiro-episodio-nao-e-corp, tamponamento-nao-e-pericardite-do-icap.'
summary: A avaliação deve confirmar atividade inflamatória e investigar causas específicas. Tamponamento, suspeita bacteriana
  ou neoplásica exigem abordagem própria; não devem aguardar escalada de anti-inflamatórios.
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: pericardite recorrente — ESC 2025

A avaliação deve confirmar atividade inflamatória e investigar causas específicas. Tamponamento, suspeita bacteriana ou neoplásica exigem abordagem própria; não devem aguardar escalada de anti-inflamatórios.

```mermaid
flowchart TD
 R["Pericardite inflamatória: episódio recorrente"] --> A{"Tamponamento ou suspeita bacteriana/neoplásica?"}
 A -->|Sim| B["Avaliação urgente e drenagem conforme indicação; tratar a causa"]
 A -->|Não| C{"Primeira linha adequada e tolerada?"}
 C -->|Ainda não| D["AAS/AINE com gastroproteção e colchicina; ajustar ao contexto"]
 C -->|Falha, contraindicação ou intolerância| E["Reavaliar diagnóstico e considerar corticoide em dose baixa/moderada ou indicação específica"]
 E --> F{"Falha da primeira linha e dos corticoides; PCR elevada?"}
 F -->|Sim| G["Anti-IL-1 para reduzir recorrências e retirar corticoide: I A"]
 F -->|Não| H{"Inflamação pericárdica na RMC e falha/contraindicação/intolerância às linhas anteriores?"}
 H -->|Sim| I["Considerar anti-IL-1 independentemente da PCR: IIa C"]
 H -->|Não| J["Reavaliar fenótipo, causa e dor residual; centro especializado"]
```

Colchicina é adjunta de primeira linha (I A); AAS/AINE com gastroproteção, I B. Corticoide não é primeira escolha sem indicação específica (III C). As decisões dependem de resposta, contraindicações, função renal/hepática e interações. Recomendação europeia de anti-IL-1 não demonstra registro dessa indicação no Brasil.

## Ensaios que sustentam a escalada

AIRTRIP (PMID 27825009) incluiu 21 pessoas com pelo menos três recorrências, PCR elevada, resistência à colchicina e dependência de corticoide. Após fase aberta, houve recorrência em 2/11 com anakinra e 9/10 com placebo. É estudo pequeno de retirada randomizada em respondedores; reações locais foram frequentes.

RHAPSODY (PMID 33200890) incluiu 86 pessoas na fase inicial e randomizou 61 respondedores após 12 semanas de run-in. Recorrência ocorreu em 2/30 com rilonacept e 23/31 com placebo; HR 0,04 (IC95% 0,01–0,18). Esses resultados não representam todos os pacientes no primeiro episódio nem um confronto direto entre os dois anti-IL-1. Reações no local de aplicação e infecções respiratórias estiveram entre os eventos mais comuns.

No derrame purulento, drenagem cirúrgica é recomendada mesmo quando punção seria tecnicamente possível. No tamponamento instável, a descompressão não deve ser adiada para testar colchicina ou anti-IL-1.

## Tudo com Tudo

- [ESC 2025: miocardite e pericardite — o que muda na porta do pericárdio](/biblioteca/esc-2025-miocardite-e-pericardite-o-que-muda-na-porta-pericardio)
- [ICAP: colchicina no primeiro episódio — não é CORP](/biblioteca/icap-colchicina-no-primeiro-episodio-nao-e-corp)
- [Tamponamento não é a pericardite do ICAP](/biblioteca/tamponamento-nao-e-pericardite-do-icap)
