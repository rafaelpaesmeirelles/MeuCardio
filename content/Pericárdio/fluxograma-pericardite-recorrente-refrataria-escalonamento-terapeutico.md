---
title: "Fluxograma: Pericardite recorrente refratária — escalonamento terapêutico (ESC 2025)"
slug: fluxograma-pericardite-recorrente-refrataria-escalonamento-terapeutico
theme: "Pericárdio"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Revisão adicional Codex 2026-09-08: coorte de suspensão conferida no abstract primário; corrigida confusão entre washout passivo e desmame, removida equivalência entre agentes e indicação indefinida universal. Construído em 26/08/2026 sobre um recorte ainda não coberto por fluxograma nesta pasta: o escalonamento terapêutico passo a passo da pericardite recorrente que já falhou à primeira linha (colchicina + AAS/AINE), incluindo a escolha entre associar corticoide ou avançar direto para anti-IL-1 conforme evidência objetiva de inflamação, e a pergunta prática de quando e como tentar suspender o anti-IL-1 após remissão prolongada — nenhum fluxograma existente na pasta cobre esse último ponto. Os 5 PMIDs foram verificados nesta sessão via PubMed E-utilities (esummary), conferindo revista, volume, páginas e título contra o texto: 40878297 (ESC 2025), 27825009 (AIRTRIP), 33200890 (RHAPSODY), 42517437 (Trotta 2026, suspensão do rilonacepte de longo prazo) e 23992557 (ICAP, colchicina na pericardite aguda). Os números do AIRTRIP, RHAPSODY e do estudo de suspensão de 2026 já haviam sido lidos e verificados linha a linha em documento publicado desta mesma pasta (inibidores de IL-1 na pericardite recorrente); nenhum número novo foi introduzido além dos já conferidos ali."
source_refs: ["Schulz-Menger J, Collini V, Gröschel J, Adler Y, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. European Heart Journal. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297 — escalonamento terapêutico da pericardite recorrente/incessante, posição do anti-IL-1 antes do corticoide para permitir sua retirada.", "Brucato A, Imazio M, Gattorno M, et al. Effect of Anakinra on Recurrent Pericarditis Among Patients With Colchicine Resistance and Corticosteroid Dependence: The AIRTRIP Randomized Clinical Trial. JAMA. 2016;316(18):1906-1912. DOI: 10.1001/jama.2016.15826. PMID: 27825009.", "Klein AL, Imazio M, Cremer P, et al. Phase 3 Trial of Interleukin-1 Trap Rilonacept in Recurrent Pericarditis (RHAPSODY). New England Journal of Medicine. 2021;384(1):31-41. DOI: 10.1056/NEJMoa2027892. PMID: 33200890.", "Trotta L, Imazio M, Bizzi E, et al. Multiyear Recurrent Pericarditis Disease Duration: Clinical Outcomes After Cessation of Long-Term Interleukin-1 Pathway Inhibition Provide Insights for Chronic Management. Journal of the American Heart Association. 2026;15(15):e044021. DOI: 10.1161/JAHA.125.044021. PMID: 42517437 — 82% de recorrência em mediana de 8 semanas após suspensão do rilonacepte de uso prolongado.", "Imazio M, Brucato A, Cemin R, et al. A randomized trial of colchicine for acute pericarditis (ICAP). New England Journal of Medicine. 2013;369(16):1522-1528. DOI: 10.1056/NEJMoa1208536. PMID: 23992557."]
---

# Fluxograma: Pericardite recorrente refratária — escalonamento terapêutico (ESC 2025)

Este fluxograma aborda pericardite recorrente com resposta insuficiente ao tratamento. Antes de escalonar, confirmar atividade pericárdica, adesão, etiologia e segurança dos medicamentos. A tabela 10 da ESC 2025 distingue falha da primeira linha, indicação de corticosteroides e seleção de anti-IL-1 conforme atividade inflamatória; não estabelece anti-IL-1 universal antes de corticosteroides.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Pericardite recorrente confirmada:<br/>recorrência de dor pericárdica típica<br/>após período livre de sintomas de pelo<br/>menos 4 a 6 semanas do episódio índice"] --> P1["Confirmar critério objetivo de<br/>recorrência: pelo menos 1 achado<br/>adicional — atrito pericárdico, alteração<br/>eletrocardiográfica típica, derrame<br/>pericárdico novo ou em piora, ou PCR<br/>elevada — ESC 2025"]

  P1 --> D1{"Qual a situação atual do tratamento<br/>anti-inflamatório desta pericardite<br/>recorrente?"}

  D1 -->|"Primeira recorrência, sem colchicina<br/>prévia em dose e duração adequadas"| C1(["Iniciar colchicina em dose ajustada<br/>por peso e função renal, associada a<br/>AAS/AINE em dose plena (ou corticoide<br/>se contraindicado), por pelo menos<br/>6 meses, com desmame lento —<br/>Classe I, nível A ESC 2025"])

  D1 -->|"Recorreu apesar de colchicina em dose<br/>e duração adequadas; corticoide ainda<br/>não tentado e sem contraindicação<br/>relevante"| C2(["Considerar corticoide em dose baixa a<br/>média apenas após contraindicação ou<br/>falha de AAS/AINE e colchicina,<br/>ou indicação específica — IIa C.<br/>Desmame individualizado após remissão"])

  D1 -->|"Recorreu apesar de colchicina, com<br/>corticoide já tentado (dependência ou<br/>refratariedade) ou corticoide<br/>contraindicado"| D2{"Há evidência objetiva de inflamação<br/>pericárdica ativa agora — PCR elevada<br/>e/ou RM com edema ou realce tardio<br/>pericárdico?"}

  D1 -->|"Em uso de anti-IL-1 (anakinra ou<br/>rilonacepte) há uso prolongado, em<br/>remissão sustentada, com<br/>indisponibilidade do fármaco ou<br/>decisão compartilhada de tentar<br/>suspender em pauta"| D3{"A suspensão do anti-IL-1 será<br/>tentada agora, por indisponibilidade<br/>do fármaco ou decisão compartilhada<br/>com o paciente?"}

  D1 -->|"Refratária apesar de colchicina,<br/>corticoide e anti-IL-1 em doses<br/>adequadas"| C7(["Hidroxicloroquina pode ser<br/>considerada — Classe IIb, nível B<br/>ESC 2025"])

  D2 -->|"PCR elevada"| C3(["Agente anti-IL-1 — anakinra ou<br/>rilonacepte, associado à colchicina —<br/>Classe I, nível A ESC 2025, para<br/>reduzir recorrências e permitir a<br/>retirada do corticoide"])

  D2 -->|"PCR normal, mas RM com inflamação<br/>pericárdica persistente"| C4(["Agente anti-IL-1 — anakinra ou<br/>rilonacepte — Classe IIa C ESC 2025,<br/>considerar pela inflamação à RM<br/>independentemente da PCR"])

  D2 -->|"PCR normal e RM sem edema ou realce<br/>pericárdico"| C5(["Reavaliar o diagnóstico antes de<br/>escalonar para anti-IL-1: considerar<br/>causa não inflamatória de dor<br/>torácica recorrente e reservar a<br/>escalada para recorrência com<br/>inflamação objetivamente<br/>documentada"])

  D3 -->|"Sim — suspensão tentada, com<br/>plano especializado de seguimento"| C6(["Planejar suspensão e seguimento<br/>com especialista. Coorte retrospectiva:<br/>14/17 recorreram após retirada,<br/>mediana de 8 semanas entre os 14.<br/>Não é risco individual universal<br/>nem protocolo de desmame de dose.<br/>Programar reavaliação e plano de resgate"])

  D3 -->|"Não — manter terapia contínua"| C8(["Manter o esquema indicado e<br/>reavaliar periodicamente benefício,<br/>eventos adversos e necessidade.<br/>A coorte não demonstra necessidade<br/>universal de tratamento indefinido"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Base das decisões
Colchicina é adjuvante de primeira linha (I A) e deve ser mantida por pelo menos seis meses nas recorrências, conforme tolerância e evolução. Aspirina/AINE em dose anti-inflamatória exige avaliação renal, hemorrágica e de interações, com proteção gástrica quando indicada. Corticosteroide não é primeira opção sem indicação específica; pode ser considerado após falha ou contraindicação da primeira linha (IIa C).

A ESC 2025 recomenda anti-IL-1 em pericardite recorrente após falha da primeira linha e corticosteroides, com PCR elevada (I A). Na doença incessante/recorrente com inflamação na RMC, após falha, contraindicação ou intolerância dessas terapias, pode-se considerar anti-IL-1 independentemente da PCR (IIa C). Excluir infecção relevante antes de imunomodulação. Um resultado isolado de PCR ou realce não dispensa interpretação clínica e etiológica.

AIRTRIP e RHAPSODY demonstraram menos recorrências em ensaios de retirada de pacientes selecionados que haviam respondido inicialmente. Não comparam diretamente os dois agentes nem provam que toda primeira recorrência deva receber biológico.

**Suspensão após controle prolongado.** Trotta et al. (2026, PMID 42517437) avaliaram retrospectivamente 17 pacientes italianos após interrupção do rilonacepte. Houve recorrência em 14/17; a mediana até recorrência foi 8 semanas entre os 14 que recorreram. O estudo descreve suspensão com eliminação gradual passiva do medicamento, não um esquema validado de redução progressiva de dose. Oito recorrências foram manejadas com inibição de IL-1, quatro com corticosteroides e duas com AINE/colchicina. Essa escolha observacional não compara eficácia das estratégias. Os resultados justificam seguimento e plano de resgate, sem definir terapia indefinida para todos.

## O que a árvore não mostra

**Restrição de exercício e vigilância de efeitos adversos acompanham todos
os ramos**, por isso não aparecem como nó — valem igualmente do primeiro
episódio ao anti-IL-1 de longo prazo.

**A escolha entre anakinra e rilonacepte exige individualização.** Ensaios separados não estabelecem equivalência de eficácia ou segurança. Considerar perfil clínico, contraindicações, disponibilidade e preferência, com avaliação especializada.

**Reação cutânea local é o efeito adverso mais comum dos dois agentes**, geralmente transitória: 95,2% dos pacientes no braço ativo do AIRTRIP tiveram
reação no local da injeção, sem nenhuma descontinuação permanente por esse
motivo; o RHAPSODY relatou reação local e infecção de via aérea superior como
os eventos mais frequentes, com 4 suspensões por evento adverso já na fase de
rodagem aberta.

**A dose e a via de administração de cada fármaco não entram na árvore** —
são parâmetros de prescrição, não pontos de decisão ramificada, e variam
conforme o fármaco escolhido e a resposta individual.

O estudo de suspensão de 2026 (Trotta et al.) tem amostra pequena (n=17), é
retrospectivo, sem grupo controle, e toda a casuística vem de centros italianos
de referência. Por isso, a taxa de 82% não é estimativa populacional nem define
conduta; serve apenas como sinal exploratório de recorrência frequente e precoce
após a suspensão.
