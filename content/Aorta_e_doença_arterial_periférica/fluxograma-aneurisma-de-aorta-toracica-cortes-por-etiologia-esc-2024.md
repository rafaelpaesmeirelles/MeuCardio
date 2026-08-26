---
title: "Fluxograma: Aneurisma de Aorta Torácica — Corte de Reparo por Etiologia e Vigilância (ESC 2024)"
slug: fluxograma-aneurisma-de-aorta-toracica-cortes-por-etiologia-esc-2024
theme: "Aorta e doença arterial periférica"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Conferido o corpus antes de escrever: os 6 fluxogramas já publicados no tema (rastreio/seguimento de AAA, diagnóstico de DAP por ITB, dor de membro/claudicação/CLTI/isquemia aguda, revascularização em CLTI por BASIL-2/BEST-CLI, isquemia aguda de membro por Rutherford, síndrome aórtica aguda) cobrem aorta abdominal, doença arterial periférica de membro e síndrome aórtica AGUDA (dissecção/hematoma/úlcera penetrante) — nenhum endereça a decisão ELETIVA de reparo versus vigilância no aneurisma de aorta TORÁCICA (raiz/ascendente), que é etapa central e distinta da síndrome aguda. Este fluxograma preenche essa lacuna. Todo o conteúdo numérico (cortes de diâmetro por etiologia, faixas de vigilância, fatores de risco adicionais) foi extraído do documento já publicado e revisado neste mesmo tema, `aneurisma-de-aorta-toracica-cortes-por-etiologia-e-seguimento-esc-2024.md` (que já cita as Recommendation Tables 34, 35, 38, 40, 56, 62, 66, 67 e 68 da diretriz), sem introduzir nenhum valor novo não presente naquele documento. A fonte primária — 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases, Eur Heart J. 2024;45(36):3538-3700, DOI 10.1093/eurheartj/ehae179 — foi reconferida nesta sessão via PubMed esummary (PMID 39210722): título, periódico, volume, páginas e data de publicação batendo exatamente. É a mesma diretriz já usada nos outros 6 fluxogramas do tema."
source_refs: ["2024 ESC Guidelines for the management of peripheral arterial and aortic diseases · European Heart Journal · 2024 · 45(36):3538-3700 · PMID 39210722 · DOI 10.1093/eurheartj/ehae179 — Recommendation Tables 34, 35, 38, 40, 56, 62, 66, 67 e 68", "Documento-base já publicado no mesmo tema: aneurisma-de-aorta-toracica-cortes-por-etiologia-e-seguimento-esc-2024.md"]
---

# Fluxograma: Aneurisma de Aorta Torácica — Corte de Reparo por Etiologia e Vigilância (ESC 2024)

Os seis fluxogramas já publicados no tema cobrem o aneurisma de aorta **abdominal**, a
doença arterial periférica de membro e a síndrome aórtica **aguda** — dissecção, hematoma
intramural e úlcera aterosclerótica penetrante, sempre em cenário de emergência. Faltava a
árvore de decisão do cenário **eletivo e crônico** do aneurisma de aorta **torácica**
(raiz/ascendente): uma vez identificado, sem sinais de síndrome aórtica aguda, em que ponto
a vigilância por imagem cede lugar à indicação de reparo. A ESC 2024 respondeu a essa
pergunta de forma **não uniforme** — o corte de diâmetro muda conforme a etiologia, não só
conforme o tamanho —, e é exatamente essa dependência de etiologia que esta árvore organiza.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Aneurisma de aorta torácica (raiz ou ascendente)<br/>identificado por imagem"] --> D0{"Dor torácica aguda, sinais de<br/>dissecção ou ruptura?"}
  D0 -->|"Sim"| C0(["Emergência — conduzir como síndrome aórtica aguda<br/>não usar os cortes eletivos desta árvore<br/>ver fluxograma dedicado de síndrome aórtica aguda"])
  D0 -->|"Não"| P1["Confirmar por TC ou RM sincronizada ao ECG<br/>avaliar a aorta inteira e a valva aórtica na linha de base"]
  P1 --> D1{"Etiologia identificada?"}
  D1 -->|"Síndrome de Marfan, Loeys-Dietz<br/>ou doença por gene ACTA2 (fenótipo de raiz)"| D2{"Diâmetro atinge o corte da síndrome específica?<br/>Marfan ≥50mm (ou ≥45mm com fator de risco adicional)<br/>Loeys-Dietz/ACTA2 ≥45mm, ajustável por gene"}
  D2 -->|"Sim"| C1(["Reparo cirúrgico indicado<br/>Classe I/IIa, Nível B/C conforme síndrome"])
  D2 -->|"Não"| C2(["Vigilância por TC/RM a cada 6-12 meses<br/>intervalo não deve alongar-se, por ser etiologia genética de alto risco<br/>+ rastreamento familiar de 3 gerações e aconselhamento genético"])
  D1 -->|"Valva aórtica bicúspide,<br/>fenótipo de RAIZ"| D3{"Diâmetro da raiz ≥50mm?"}
  D3 -->|"Sim"| C3(["Reparo cirúrgico indicado<br/>Classe I, Nível B"])
  D3 -->|"Não"| C4(["TC/RM basal + TTE em 1 ano<br/>depois a cada 2-3 anos se crescimento menor que 3mm/ano<br/>ou semestral, confirmado por TC/RM, se maior ou igual a 3mm/ano<br/>a partir de 45mm: característica de alto risco direciona a reimagem semestral"])
  D1 -->|"Valva aórtica bicúspide,<br/>fenótipo ASCENDENTE"| D4{"Diâmetro maior ou igual a 55mm<br/>(ou maior que 52mm em centro experiente, baixo risco)?"}
  D4 -->|"Sim"| C5(["Reparo cirúrgico indicado<br/>Classe I, Nível B / IIa, Nível B"])
  D4 -->|"Não"| C6(["TC/RM basal + TTE em 1 ano se 40-44mm<br/>confirmação por TC/RM e reimagem semestral<br/>a partir de 45mm até atingir o limiar cirúrgico"])
  D1 -->|"Tricúspide,<br/>sem doença genética conhecida"| D5{"Diâmetro maior ou igual a 55mm<br/>(ou maior que 52mm em centro experiente, baixo risco)?"}
  D5 -->|"Sim"| C7(["Reparo cirúrgico indicado<br/>Classe I, Nível B / IIa, Nível B"])
  D5 -->|"Não"| D6{"Diâmetro 50-54mm E fator de risco adicional?<br/>crescimento maior ou igual a 3mm/ano, hipertensão resistente,<br/>estatura baixa, fenótipo de raiz, comprimento aórtico maior que 11cm,<br/>idade menor que 50 anos ou desejo de gestação"}
  D6 -->|"Sim"| C8(["Reparo cirúrgico pode ser considerado<br/>já a partir de 50mm — Classe IIb, Nível B"])
  D6 -->|"Não"| C9(["TC/RM basal + TTE em 1 ano se 40-44mm<br/>confirmação por TC/RM e reimagem semestral<br/>a partir de 45mm até atingir o limiar cirúrgico"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## Por que a etiologia decide o corte, não só o diâmetro

O erro mais comum na leitura rápida da diretriz é tratar "55 mm" como um número único e
universal. Ele é, na verdade, o corte-padrão de **um** cenário — aorta ascendente tubular,
valva tricúspide, sem doença genética. Nos demais cenários o corte é mais baixo, porque o
risco de dissecção em diâmetros menores é maior:

- na síndrome de Marfan e no fenótipo de raiz da valva bicúspide, o corte cai para **50 mm**;
- na síndrome de Loeys-Dietz e na doença por gene ACTA2, cai para **45 mm**, com a ressalva
  de que dissecção pode ocorrer com diâmetros ainda menores nessas duas condições.

## O corte de 50 mm por fator de risco, sem síndrome genética nem valva bicúspide

Mesmo no cenário mais "benigno" — tricúspide, sem doença genética —, a substituição da
aorta ascendente **pode ser considerada já a partir de 50 mm** (Classe IIb, Nível B) quando o
paciente reúne fatores de risco adicionais: crescimento ≥3 mm/ano, hipertensão resistente,
estatura baixa, fenótipo de raiz, comprimento aórtico >11 cm, idade <50 anos ou desejo de
gestação. A justificativa numérica está na própria diretriz: **mais de 60% das dissecções
agudas tipo A** em pacientes sem síndrome genética e sem valva bicúspide ocorrem com aorta
que ainda não atingiu o corte clássico de 55 mm, e o risco de evento já ultrapassa 1% ao ano
na faixa de 50-54 mm. Esta árvore mantém essa recomendação restrita ao ramo tricúspide sem
doença genética — a diretriz não estende esse mesmo corte de 50 mm ao fenótipo ascendente da
valva bicúspide, que segue pelo corte-padrão de 55 mm (ou 52 mm em centro experiente).

## Por que TTE não substitui TC/RM no seguimento

A ecocardiografia transtorácica é o método inicial válido para **raiz e ascendente**, mas é
**formalmente contraindicada (Classe III, Nível C)** para vigilância de aorta ascendente
distal, arco e descendente — segmentos onde o método obrigatório é TC ou RM. Essa regra vale
para todos os ramos desta árvore e por isso não está desenhada como decisão: aplica-se
igualmente à confirmação inicial e a cada reavaliação de vigilância, qualquer que seja a
etiologia.

## Antes de entrar nesta árvore

Identificado um aneurisma torácico em qualquer segmento, a avaliação da **aorta inteira** é
recomendada, na linha de base e no seguimento (Classe I, Nível C), assim como a avaliação da
**valva aórtica** — sobretudo para bicúspide (Classe I, Nível C), porque 20-30% dos
aneurismas de raiz surgem em portador de valva bicúspide. É essa avaliação inicial que define
em qual dos quatro ramos etiológicos desta árvore o paciente se encaixa.

## Limites

- esta árvore cobre reparo eletivo da raiz e da aorta ascendente; a aorta descendente e
  toracoabdominal têm cortes próprios e mais altos (DTA sem doença hereditária ≥55 mm, TAAA
  degenerativo ≥60 mm), não representados aqui por serem um recorte anatômico distinto;
- não substitui a avaliação de risco cirúrgico formal nem a decisão compartilhada com o
  paciente sobre durabilidade e via de reparo (aberta versus endovascular);
- rastreamento familiar (história de três gerações, teste em cascata, aconselhamento
  genético) é recomendado nos ramos de doença hereditária mas não está desdobrado nesta
  árvore, que é sobre limiar de reparo — ver o documento-base para o detalhe do rastreamento;
- este fluxograma não cobre síndrome aórtica aguda (ver `fluxograma-sindrome-aortica-aguda-esc-2024`)
  nem aneurisma de aorta abdominal (ver `fluxograma-aneurisma-de-aorta-abdominal-seguimento-e-indicacao-de-reparo`).

## Conexões no CorVIA

- documento-base, com o detalhe completo de tabelas e rastreamento familiar:
  `aneurisma-de-aorta-toracica-cortes-por-etiologia-e-seguimento-esc-2024`;
- fluxogramas relacionados do mesmo tema: `fluxograma-sindrome-aortica-aguda-esc-2024`,
  `fluxograma-aneurisma-de-aorta-abdominal-seguimento-e-indicacao-de-reparo`;
- diretriz combinada: 2024 ESC Guidelines for the management of peripheral arterial and
  aortic diseases (PMID 39210722).
