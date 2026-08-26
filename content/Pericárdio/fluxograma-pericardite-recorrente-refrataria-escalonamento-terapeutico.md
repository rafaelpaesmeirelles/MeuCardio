---
title: "Fluxograma: Pericardite recorrente refratária — escalonamento terapêutico (ESC 2025)"
slug: fluxograma-pericardite-recorrente-refrataria-escalonamento-terapeutico
theme: "Pericárdio"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído em 26/08/2026 sobre um recorte ainda não coberto por fluxograma nesta pasta: o escalonamento terapêutico passo a passo da pericardite recorrente que já falhou à primeira linha (colchicina + AAS/AINE), incluindo a escolha entre associar corticoide ou avançar direto para anti-IL-1 conforme evidência objetiva de inflamação, e a pergunta prática de quando e como tentar suspender o anti-IL-1 após remissão prolongada — nenhum fluxograma existente na pasta cobre esse último ponto. Os 5 PMIDs foram verificados nesta sessão via PubMed E-utilities (esummary), conferindo revista, volume, páginas e título contra o texto: 40878297 (ESC 2025), 27825009 (AIRTRIP), 33200890 (RHAPSODY), 42517437 (Trotta 2026, suspensão do rilonacepte de longo prazo) e 23992557 (ICAP, colchicina na pericardite aguda). Os números do AIRTRIP, RHAPSODY e do estudo de suspensão de 2026 já haviam sido lidos e verificados linha a linha em documento publicado desta mesma pasta (inibidores de IL-1 na pericardite recorrente); nenhum número novo foi introduzido além dos já conferidos ali."
source_refs: ["Schulz-Menger J, Collini V, Gröschel J, Adler Y, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. European Heart Journal. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297 — escalonamento terapêutico da pericardite recorrente/incessante, posição do anti-IL-1 antes do corticoide para permitir sua retirada.", "Brucato A, Imazio M, Gattorno M, et al. Effect of Anakinra on Recurrent Pericarditis Among Patients With Colchicine Resistance and Corticosteroid Dependence: The AIRTRIP Randomized Clinical Trial. JAMA. 2016;316(18):1906-1912. DOI: 10.1001/jama.2016.15826. PMID: 27825009.", "Klein AL, Imazio M, Cremer P, et al. Phase 3 Trial of Interleukin-1 Trap Rilonacept in Recurrent Pericarditis (RHAPSODY). New England Journal of Medicine. 2021;384(1):31-41. DOI: 10.1056/NEJMoa2027892. PMID: 33200890.", "Trotta L, Imazio M, Bizzi E, et al. Multiyear Recurrent Pericarditis Disease Duration: Clinical Outcomes After Cessation of Long-Term Interleukin-1 Pathway Inhibition Provide Insights for Chronic Management. Journal of the American Heart Association. 2026;15(15):e044021. DOI: 10.1161/JAHA.125.044021. PMID: 42517437 — 82% de recorrência em mediana de 8 semanas após suspensão do rilonacepte de uso prolongado.", "Imazio M, Brucato A, Cemin R, et al. A randomized trial of colchicine for acute pericarditis (ICAP). New England Journal of Medicine. 2013;369(16):1522-1528. DOI: 10.1056/NEJMoa1208536. PMID: 23992557."]
---

# Fluxograma: Pericardite recorrente refratária — escalonamento terapêutico (ESC 2025)

Os fluxogramas já publicados nesta pasta cobrem o diagnóstico e a primeira
linha de tratamento da pericardite aguda, e tocam de passagem no anti-IL-1 na
doença recorrente. Este fluxograma parte de onde aqueles terminam: o paciente
que **já recorreu apesar da colchicina**, e cuja pergunta deixou de ser "como
tratar o episódio" e passou a ser **"qual o próximo degrau da escalada, e até
quando mantê-lo"**. A ESC 2025 reorganizou essa escada de forma explícita —
o anti-IL-1 passou a vir **antes** do corticoide crônico, não depois dele —,
e um estudo de 2026 respondeu, pela primeira vez com número real, à pergunta
que fica em aberto quando o paciente já está estável havia anos: **o que
acontece se a droga for suspensa?**

## Árvore de decisão

```mermaid
flowchart TD
  R0["Pericardite recorrente confirmada:<br/>recorrência de dor pericárdica típica<br/>após período livre de sintomas de pelo<br/>menos 4 a 6 semanas do episódio índice"] --> P1["Confirmar critério objetivo de<br/>recorrência: pelo menos 1 achado<br/>adicional — atrito pericárdico, alteração<br/>eletrocardiográfica típica, derrame<br/>pericárdico novo ou em piora, ou PCR<br/>elevada — ESC 2025"]

  P1 --> D1{"Qual a situação atual do tratamento<br/>anti-inflamatório desta pericardite<br/>recorrente?"}

  D1 -->|"Primeira recorrência, sem colchicina<br/>prévia em dose e duração adequadas"| C1(["Iniciar colchicina em dose ajustada<br/>por peso e função renal, associada a<br/>AAS/AINE em dose plena (ou corticoide<br/>se contraindicado), por pelo menos<br/>6 meses, com desmame lento —<br/>Classe I, nível A ESC 2025"])

  D1 -->|"Recorreu apesar de colchicina em dose<br/>e duração adequadas; corticoide ainda<br/>não tentado e sem contraindicação<br/>relevante"| C2(["Associar corticoide em dose baixa a<br/>média à colchicina — Classe IIa;<br/>desmame lento por pelo menos 6 meses,<br/>nunca suspensão abrupta"])

  D1 -->|"Recorreu apesar de colchicina, com<br/>corticoide já tentado (dependência ou<br/>refratariedade) ou corticoide<br/>contraindicado"| D2{"Há evidência objetiva de inflamação<br/>pericárdica ativa agora — PCR elevada<br/>e/ou RM com edema ou realce tardio<br/>pericárdico?"}

  D1 -->|"Em uso de anti-IL-1 (anakinra ou<br/>rilonacepte) há uso prolongado, em<br/>remissão sustentada, com<br/>indisponibilidade do fármaco ou<br/>decisão compartilhada de tentar<br/>suspender em pauta"| D3{"A suspensão do anti-IL-1 será<br/>tentada agora, por indisponibilidade<br/>do fármaco ou decisão compartilhada<br/>com o paciente?"}

  D1 -->|"Refratária apesar de colchicina,<br/>corticoide e anti-IL-1 em doses<br/>adequadas"| C7(["Hidroxicloroquina pode ser<br/>considerada — Classe IIb, nível B<br/>ESC 2025"])

  D2 -->|"PCR elevada"| C3(["Agente anti-IL-1 — anakinra ou<br/>rilonacepte, associado à colchicina —<br/>Classe I, nível A ESC 2025, para<br/>reduzir recorrências e permitir a<br/>retirada do corticoide"])

  D2 -->|"PCR normal, mas RM com inflamação<br/>pericárdica persistente"| C4(["Agente anti-IL-1 — anakinra ou<br/>rilonacepte — Classe IIa ESC 2025,<br/>indicado pela inflamação à RM<br/>independentemente da PCR"])

  D2 -->|"PCR normal e RM sem edema ou realce<br/>pericárdico"| C5(["Reavaliar o diagnóstico antes de<br/>escalonar para anti-IL-1: considerar<br/>causa não inflamatória de dor<br/>torácica recorrente e reservar a<br/>escalada para recorrência com<br/>inflamação objetivamente<br/>documentada"])

  D3 -->|"Sim — suspensão tentada, com<br/>desmame gradual"| C6(["Suspender com desmame gradual, mas<br/>orientar que a recorrência é o<br/>desfecho mais provável — 82% dos<br/>pacientes recorrem em mediana de<br/>8 semanas após suspensão do<br/>rilonacepte de uso prolongado<br/>(Trotta 2026); programar reavaliação<br/>precoce e plano pronto de retomada<br/>da inibição de IL-1"])

  D3 -->|"Não — manter terapia contínua"| C8(["Manter a inibição da via de IL-1<br/>continuamente: a doença permanece<br/>autoinflamatoriamente ativa mesmo<br/>após anos de controle, e a maioria<br/>recorre poucas semanas após a<br/>suspensão"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que sustenta cada degrau da escada

**A colchicina não é resgate — é a base que precisa estar bem-feita antes de
qualquer coisa.** O ICAP (Imazio et al., NEJM 2013, PMID 23992557) é o
ensaio que consolidou a colchicina como redutora de recorrência quando
associada a AAS/AINE no primeiro episódio, e a ESC 2025 manteve essa
recomendação como Classe I, nível A. Antes de rotular alguém como
"colchicina-resistente", vale confirmar que a dose foi ajustada por peso e
função renal e que a duração — pelo menos 6 meses no episódio incessante ou
recorrente — foi de fato cumprida. Suspensão precoce, por melhora do sintoma,
é uma causa comum e evitável de "falha" que na verdade é subtratamento.

**O corticoide entra como ponte, não como destino.** A ESC 2025 o mantém como
Classe IIa para quem já esgotou colchicina + AAS/AINE, mas o texto da própria
diretriz é explícito sobre o motivo de o anti-IL-1 ter subido de posição na
escada: ele existe **especificamente para permitir a retirada do
corticoide**, não apenas como mais uma opção paralela. É por isso que a
árvore trata "já em corticoide, dependente ou refratário" como o gatilho que
abre a porta para o anti-IL-1, e não como um beco sem saída.

**Anakinra e rilonacepte têm o mesmo lugar na escada, com evidência de
ensaios diferentes.** O AIRTRIP (Brucato et al., JAMA 2016, PMID 27825009)
testou anakinra especificamente na população resistente à colchicina e
dependente de corticoide — a mesma população-alvo desta árvore — com
recorrência de 90% no grupo placebo contra 18,2% no grupo anakinra. O
RHAPSODY (Klein et al., NEJM 2021, PMID 33200890) testou rilonacepte em
desenho randomizado-com-retirada e mostrou HR 0,04 para a primeira
recorrência (recorrência bruta de 7% com rilonacepte contra 74% com
placebo). Os dois ensaios, juntos, são o motivo pelo qual a ESC 2025 deu
Classe I, nível A ao anti-IL-1 nesse cenário — não é extrapolação de
mecanismo, é replicação em dois fármacos da mesma classe.

**A pergunta que a árvore de tratamento da ESC 2025 não responde, e que este
fluxograma cobre: o que fazer quando a droga precisa parar.** Nem toda
suspensão de anti-IL-1 é escolha médica — o rilonacepte não é comercializado
em todos os países, inclusive na Itália, de onde vem a maior parte da
casuística de pericardite recorrente refratária. O estudo de Trotta et al.
(J Am Heart Assoc. 2026, PMID 42517437) acompanhou 17 pacientes que tiveram
de suspender o rilonacepte após anos de controle (duração mediana de uso
contínuo de 28 meses) e mostrou que **82% recorreram**, em mediana de 8
semanas — praticamente o mesmo intervalo do grupo placebo do RHAPSODY
original (8,6 semanas). Isso não significa "a droga falhou": significa que a
doença autoinflamatória de base permanece ativa por baixo do controle
farmacológico, e que suspensão deve vir sempre acompanhada da expectativa
explícita de recorrência precoce, não da esperança de remissão definitiva.
No mesmo estudo, a maioria dos que recorreram (8 de 14) precisou retomar a
inibição da via de IL-1; só 2 de 17 controlaram com AINE/colchicina
isolados — um lembrete de que, na doença já avançada a esse ponto, a
terapia de base isolada raramente basta.

## O que a árvore não mostra

**Restrição de exercício e vigilância de efeitos adversos acompanham todos
os ramos**, por isso não aparecem como nó — valem igualmente do primeiro
episódio ao anti-IL-1 de longo prazo.

**A escolha entre anakinra e rilonacepte não é uma bifurcação clínica
codificada em diretriz** — os dados disponíveis sugerem eficácia e segurança
semelhantes entre os dois, e a escolha na prática depende de disponibilidade
local, via de aplicação preferida pelo paciente (anakinra é diária;
rilonacepte, semanal) e custo. Por isso os dois aparecem juntos em cada nó de
conduta, e não como ramos separados da árvore.

**Reação cutânea local é o efeito adverso mais comum dos dois agentes**, quase
sempre transitória: 95,2% dos pacientes no braço ativo do AIRTRIP tiveram
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
