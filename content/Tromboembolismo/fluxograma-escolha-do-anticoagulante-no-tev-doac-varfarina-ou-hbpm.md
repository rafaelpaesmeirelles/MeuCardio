---
title: "Fluxograma: Escolha do anticoagulante no tromboembolismo venoso — DOAC, varfarina ou HBPM"
slug: fluxograma-escolha-do-anticoagulante-no-tev-doac-varfarina-ou-hbpm
theme: "Tromboembolismo"
kind: fluxograma
summary: "Árvore para escolher o anticoagulante do TEV agudo: HNF na instabilidade com reperfusão possível, HBPM na gestação e no câncer com mucosa luminal ou alto risco de sangramento, varfarina na síndrome antifosfolípide e no clearance abaixo de 30 mL/min, e DOAC como padrão para todos os demais — com ou sem fase parenteral conforme o fármaco."
review_status: revisado
review_note: "Produção científica assistida (Claude) e revisão editorial e científica independente (Codex), concluídas em 26/08/2026. Fontes primárias, coerência clínica, lógica dos fluxos, metadados e links foram conferidos; correções incorporadas."
source_refs:
  - "Ortel TL, Neumann I, Ageno W, et al. American Society of Hematology 2020 guidelines for management of venous thromboembolism: treatment of deep vein thrombosis and pulmonary embolism. Blood Adv. 2020;4(19):4693-4738. DOI: 10.1182/bloodadvances.2020001830. PMCID: PMC7556153. https://pmc.ncbi.nlm.nih.gov/articles/PMC7556153/ — texto integral lido: recomendações 3, 4 e 6 e remarks."
  - "Amado VM, Fernandes CJCDS, Salibe-Filho W, et al. Brazilian guidelines for the pharmacological treatment of pulmonary embolism. Official document of the Brazilian Thoracic Association based on the GRADE methodology. J Bras Pneumol. 2025;51(2):e20240314. DOI: 10.36416/1806-3756/e20240314. PMCID: PMC12401105. https://pmc.ncbi.nlm.nih.gov/articles/PMC12401105/ — texto integral lido."
  - "Stevens SM, Woller SC, Kreuziger LB, et al. Antithrombotic Therapy for VTE Disease: Second Update of the CHEST Guideline and Expert Panel Report. Chest. 2021;160(6):e545-e608. DOI: 10.1016/j.chest.2021.07.055. PMID: 34352278. https://pubmed.ncbi.nlm.nih.gov/34352278/ — apenas o resumo foi lido; texto integral bloqueado."
  - "Konstantinides SV, Meyer G, Becattini C, et al. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS). Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429. https://academic.oup.com/eurheartj/article/41/4/543/5556136 — página aberta apenas até a seção 6; tabelas de recomendação usadas via o protocolo do acervo tromboembolismo-pulmonar-agudo-diagnostico-e-manejo-escers-2019."
  - "Derivado de doac-no-tratamento-do-tev-agudo-amplify-einstein-pe-re-cover-e-hokusai-vte.md (AMPLIFY, EINSTEIN-PE, RE-COVER, HOKUSAI-VTE), já publicado no acervo (Tromboembolismo)."
  - "Derivado de trombofilia-hereditaria-e-adquirida-risco-de-recorrencia-e-doac-na-sindrome-antifosfolipide.md (TRAPS, Pengo 2018), já publicado no acervo (Tromboembolismo)."
  - "Derivado de tev-com-insuficiencia-renal-grave-e-dialise-doac-fora-dos-ensaios-pivotais.md (Cheung 2021; Almajdi 2023), já publicado no acervo (Tromboembolismo)."
  - "Derivado de trombose-associada-ao-cancer-escore-de-khorana-e-escolha-de-anticoagulante.md (ITAC 2022; CARAVAGGIO; Hokusai VTE Cancer), já publicado no acervo (Tromboembolismo)."
  - "Derivado de aha-acc-2026-tep-agudo-categorias-clinicas-anticoagulacao-e-terapias-avancadas.md (Creager MA et al., 2026 AHA/ACC guideline for acute PE, JACC/Circulation 2026), já publicado no acervo (Tromboembolismo) — usado apenas para a preferência de HBPM sobre HNF na fase parenteral."
---

# Fluxograma: Escolha do anticoagulante no TEV — DOAC, varfarina ou HBPM

Nos quatro ensaios pivotais que compararam anticoagulante oral direto (DOAC) com varfarina no
TEV agudo, o resultado se repetiu: eficácia igual, sangramento igual ou menor. Por isso ASH 2020,
ESC 2019 e a diretriz brasileira SBPT 2025 fazem do DOAC a primeira escolha. O erro clínico
frequente não está nesse padrão, e sim nas exceções — que são poucas, bem definidas e apontam
para fármacos diferentes: a síndrome antifosfolípide e o clearance de creatinina muito baixo
levam à varfarina; a gestação e o câncer com mucosa luminal exposta levam à heparina de baixo
peso molecular (HBPM); a instabilidade que pode exigir trombólise leva à heparina não fracionada
(HNF). A árvore abaixo percorre essas exceções na ordem em que se decidem à beira do leito,
antes de chegar ao padrão. Duração do tratamento e escolha entre estender ou suspender ficam em
outro fluxograma desta pasta (ver fluxograma-duracao-da-anticoagulacao-apos-tev-nao-provocado).

## Árvore de decisão

```mermaid
flowchart TD
  R0["TEV agudo confirmado, TVP proximal ou TEP,<br/>com indicação de anticoagulação terapêutica<br/>e sem contraindicação absoluta a anticoagular"]
  D1{"Instabilidade hemodinâmica, TEP de alto risco<br/>ou trombólise/intervenção possível<br/>nas próximas horas?"}
  C1(["HNF intravenosa em bolus e infusão ajustados ao peso<br/>enquanto se decide a reperfusão;<br/>transição para anticoagulante oral após estabilização"])
  D2{"Gestação?"}
  C2(["HBPM em dose terapêutica ajustada ao peso<br/>por toda a gestação; DOAC não recomendado;<br/>varfarina contraindicada na gestação"])
  D2B{"Lactação?"}
  C2B(["HBPM ou varfarina são compatíveis com a lactação;<br/>evitar DOAC durante a amamentação"])
  D3{"Síndrome antifosfolípide confirmada?"}
  C3(["Varfarina com INR alvo 2,0 a 3,0, iniciada sob<br/>HBPM ou HNF por no mínimo 5 dias e até INR<br/>terapêutico; evitar DOAC, sobretudo no perfil<br/>triplo-positivo ou com evento arterial"])
  D4{"Clearance de creatinina<br/>abaixo de 30 mL/min?"}
  C4(["Varfarina com lead-in parenteral, ou HNF<br/>com monitorização; apixabana só como exceção<br/>individualizada, com evidência observacional"])
  D5{"Câncer ativo?"}
  D6{"Tumor gastrointestinal ou geniturinário luminal<br/>não ressecado, alto risco de sangramento,<br/>absorção oral comprometida ou<br/>trombocitopenia relevante?"}
  C5(["HBPM em dose terapêutica ajustada ao peso<br/>por no mínimo 6 meses, prolongada<br/>enquanto o câncer estiver ativo"])
  D7{"Antineoplásico ou outro fármaco com interação<br/>forte por P-gp ou CYP3A4?"}
  C6(["HBPM em dose terapêutica por no mínimo 6 meses;<br/>reavaliar troca para DOAC quando a<br/>interação cessar"])
  C7(["DOAC por no mínimo 6 meses, prolongado enquanto<br/>o câncer estiver ativo: apixabana ou rivaroxabana<br/>sem fase parenteral; edoxabana após no mínimo<br/>5 dias de HBPM"])
  D8{"Inibidor ou indutor forte de P-gp ou CYP3A4,<br/>doença hepática moderada a grave, ou má absorção<br/>por cirurgia bariátrica ou intestino curto?"}
  C8(["Varfarina com lead-in parenteral e INR 2,0 a 3,0,<br/>ou HBPM se a varfarina também for inviável"])
  D9{"Fase parenteral inicial já em curso<br/>ou desejada antes do oral?"}
  C9(["Dabigatrana 150 mg 2x/dia ou edoxabana 60 mg 1x/dia<br/>após 5 a 10 dias de HBPM ou HNF;<br/>edoxabana 30 mg se peso de 60 kg ou menos<br/>ou clearance de 30 a 50 mL/min"])
  C10(["Apixabana 10 mg 2x/dia por 7 dias, depois 5 mg 2x/dia,<br/>ou rivaroxabana 15 mg 2x/dia por 21 dias,<br/>depois 20 mg 1x/dia, sem fase parenteral"])

  R0 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D2B
  D2B -->|"Sim"| C2B
  D2B -->|"Não"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| D5
  D5 -->|"Sim"| D6
  D5 -->|"Não"| D8
  D6 -->|"Sim"| C5
  D6 -->|"Não"| D7
  D7 -->|"Sim"| C6
  D7 -->|"Não"| C7
  D8 -->|"Sim"| C8
  D8 -->|"Não"| D9
  D9 -->|"Sim"| C9
  D9 -->|"Não"| C10

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C2B,C3,C4,C5,C6,C7,C8,C9,C10 conduta;
```

## Por que a instabilidade vem primeiro

A ASH 2020 faz da trombólise seguida de anticoagulação a conduta recomendada no TEP com
comprometimento hemodinâmico (recomendação 6, forte apesar de certeza baixa), definido como
pressão sistólica abaixo de 90 mmHg ou queda de 40 mmHg ou mais em relação à basal. A SBPT 2025
sugere trombólise sistêmica no TEP de alto risco com choque obstrutivo. Nesse cenário, o
anticoagulante inicial é a HNF, porque tem meia-vida curta e é reversível, facilitando a
reperfusão — a estratificação de risco e a decisão de trombolisar estão em
fluxograma-tep-agudo-estratificacao-de-risco-e-decisao-de-trombolise. Para o TEP estável, a AHA/ACC 2026
recomenda HBPM em preferência à HNF quando há fase parenteral (ver
aha-acc-2026-tep-agudo-categorias-clinicas-anticoagulacao-e-terapias-avancadas); a ASH 2020 não
tem recomendação sobre HBPM versus HNF e trata as duas como equivalentes no lead-in.

## Gestação, síndrome antifosfolípide e rim: as três exceções que levam para fora do DOAC

A SBPT 2025 escreve de forma direta que o DOAC deve ser evitado na síndrome antifosfolípide
(SAF), em que a varfarina permanece a opção padrão, e na gestação e lactação. Na gestação, a
HBPM é preferida e a varfarina é contraindicada; na lactação, HBPM e varfarina são compatíveis.
A ESC 2019 dá classe III ao DOAC na gestação. A
ASH 2020 vai na mesma direção com linguagem mais cautelosa: a preferência por DOAC "pode não se
aplicar" a clearance de creatinina abaixo de 30 mL/min, doença hepática moderada a grave e SAF.

Na SAF, a evidência mais forte é o ensaio TRAPS, interrompido após 120 pacientes por excesso de
eventos tromboembólicos com rivaroxabana (12% contra nenhum com varfarina) em pacientes
triplo-positivos — ver trombofilia-hereditaria-e-adquirida-risco-de-recorrencia-e-doac-na-sindrome-antifosfolipide.
O ensaio testou o perfil triplo-positivo; para SAF com um ou dois anticorpos as diretrizes lidas
aqui ainda apontam para a varfarina, e qualquer uso de DOAC nesse subgrupo é decisão
individualizada, sem ensaio que a sustente.

No rim, o corte de 30 mL/min vem dos próprios ensaios: a ASH registra que os estudos
excluíram clearance abaixo de 25 mL/min (apixabana) ou 30 mL/min (demais DOAC), e a SBPT 2025
manda evitar DOAC com clearance de 30 mL/min ou menos, "com exceção da apixabana". Essa
exceção repousa em estudos observacionais reunidos em
tev-com-insuficiencia-renal-grave-e-dialise-doac-fora-dos-ensaios-pivotais — é ela que a
conduta C4 chama de individualizada.

## Câncer ativo: DOAC como padrão, HBPM onde a mucosa ou a interação mandam

A ITAC 2022 aceita DOAC para tratamento inicial e de manutenção no TEV do câncer em quem não
tem alto risco de sangramento gastrointestinal ou geniturinário, sem interação relevante e com
absorção preservada; a ESC 2019 sugere edoxabana ou rivaroxabana como alternativa à HBPM, com
cautela no câncer gastrointestinal; a SBPT 2025 sugere DOAC (condicional, baixa certeza) sem o
recorte de sítio tumoral. O recorte vem do Hokusai VTE Cancer, em que a edoxabana reduziu
recorrência mas aumentou sangramento maior (6,9% contra 4,0%), concentrado em tumores
gastrointestinais, enquanto o CARAVAGGIO não mostrou excesso de sangramento com apixabana
(3,8% contra 4,0%) — detalhes em
trombose-associada-ao-cancer-escore-de-khorana-e-escolha-de-anticoagulante. No Hokusai VTE
Cancer a edoxabana foi precedida de HBPM por no mínimo 5 dias, e a apixabana do CARAVAGGIO
foi dada sem fase parenteral — a conduta C7 reproduz esses regimes. A duração mínima é
de 6 meses. A conduta com plaquetas abaixo de 50.000/µL, que muda dose e fármaco, está em
fluxograma-tromboembolismo-pulmonar-agudo-associado-ao-cancer-e-trombocitopenia, e não é
repetida aqui.

| Ensaio | Comparação | TEV recorrente | Sangramento maior |
|---|---|---|---|
| CARAVAGGIO (2020) | apixabana vs dalteparina, 6 meses, 1.155 pacientes | 5,6% vs 7,9% | 3,8% vs 4,0% |
| Hokusai VTE Cancer (2018) | edoxabana vs dalteparina, 12 meses, 1.046 pacientes | 7,9% vs 11,3% | 6,9% vs 4,0% |

## O padrão: qual DOAC, com ou sem heparina antes

A ASH 2020 não sugere um DOAC sobre outro (recomendação 4, certeza muito baixa) e lista o que
deve guiar a escolha: necessidade de lead-in parenteral, posologia uma ou duas vezes ao dia,
custo, função renal, fármacos concomitantes metabolizados por CYP3A4 ou P-glicoproteína e
presença de câncer. A mesma diretriz acrescenta que SAF, cirurgia bariátrica, intestino curto e
extremos de peso tornam o paciente candidato não ideal a DOAC — daí o ramo D8 (ver
doac-pos-cirurgia-bariatrica-de-bypass-gastrico-farmacocinetica-alterada e
doac-em-obesidade-extrema-a-mudanca-de-orientacao-da-isth para os dois últimos cenários).

O ramo D9 traduz a diferença de desenho dos ensaios pivotais: apixabana e rivaroxabana foram
testadas sem heparina prévia, com dose de ataque; dabigatrana e edoxabana foram testadas após
fase parenteral, que a ASH descreve como "até 5 a 10 dias" de HNF ou HBPM. Iniciar dabigatrana
ou edoxabana sem essa fase é usar esquema que nenhum ensaio testou.

| Fármaco | Fase parenteral | Regime testado no ensaio pivotal |
|---|---|---|
| Apixabana (AMPLIFY) | Não | 10 mg 2x/dia por 7 dias, depois 5 mg 2x/dia |
| Rivaroxabana (EINSTEIN-PE) | Não | 15 mg 2x/dia por 3 semanas, depois 20 mg 1x/dia |
| Dabigatrana (RE-COVER) | Sim, mediana de 9 dias | 150 mg 2x/dia |
| Edoxabana (HOKUSAI-VTE) | Sim | 60 mg 1x/dia; 30 mg se clearance 30 a 50 mL/min ou peso de 60 kg ou menos |
| Varfarina | Sim, no mínimo 5 dias e INR terapêutico por 24 h | INR 2,0 a 3,0 |

A dose de HBPM nas condutas C2, C5 e C6 é a terapêutica ajustada ao peso conforme a bula
vigente do produto e a função renal. A dalteparina do CARAVAGGIO foi 200 UI/kg 1x/dia no primeiro mês e 150 UI/kg
1x/dia depois.

## Limitações

- A árvore usa 30 mL/min como limite operacional conservador, alinhado à ASH 2020 e à SBPT 2025; a rotulagem varia por fármaco e deve ser consultada antes da prescrição.
- A exceção da apixabana com clearance abaixo de 30 mL/min é observacional; não há ensaio
  randomizado dedicado.
- O ramo de interação medicamentosa (D7 e D8) é qualitativo; a lista de inibidores e indutores
  fortes de P-gp e CYP3A4 deve ser conferida na bula de cada DOAC antes de prescrever.
- Este fluxograma não decide duração nem dose reduzida na extensão; não cobre prótese valvar
  mecânica, trombo de ventrículo esquerdo nem trombose venosa cerebral, que têm documentos
  próprios no acervo.

## Tudo com Tudo

- [DOAC no Tratamento do TEV Agudo: AMPLIFY, EINSTEIN-PE, RE-COVER e HOKUSAI-VTE](/biblioteca/doac-no-tratamento-do-tev-agudo-amplify-einstein-pe-re-cover-e-hokusai-vte)
- [Trombofilia Hereditária e Adquirida: Risco de Recorrência e DOAC na Síndrome Antifosfolípide](/biblioteca/trombofilia-hereditaria-e-adquirida-risco-de-recorrencia-e-doac-na-sindrome-antifosfolipide)
- [TEV com Insuficiência Renal Grave e Diálise: DOAC Fora dos Ensaios Pivotais](/biblioteca/tev-com-insuficiencia-renal-grave-e-dialise-doac-fora-dos-ensaios-pivotais)
- [Trombose associada ao câncer: escore de Khorana e escolha de anticoagulante](/biblioteca/trombose-associada-ao-cancer-escore-de-khorana-e-escolha-de-anticoagulante)
- [Fluxograma: TEP agudo — estratificação de risco e decisão de trombólise](/biblioteca/fluxograma-tep-agudo-estratificacao-de-risco-e-decisao-de-trombolise)
- [Fluxograma: TEP agudo na gestação e no puerpério (ESC 2025)](/biblioteca/fluxograma-tromboembolismo-pulmonar-agudo-na-gestacao-e-puerperio-esc-2025)
- [Fluxograma: Duração da anticoagulação após primeiro episódio de TEV não provocado](/biblioteca/fluxograma-duracao-da-anticoagulacao-apos-tev-nao-provocado)
