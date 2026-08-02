---
title: "Fluxograma: Cuidado pós-parada e decisão de coronariografia"
slug: fluxograma-cuidado-pos-parada-e-coronariografia
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão do primeiro ECG pós-RCE: com supra de ST, cateterismo imediato sem discussão; sem supra, a evidência de COACT e TOMAHAWK não sustenta urgência — a prioridade passa a ser o cuidado pós-parada, com angiografia adiada ou seletiva."
review_status: revisado
source_refs: ["Lemkes JS, Janssens GN, van der Hoeven NW, Jewbali LSD, Dubois EA, et al. Coronary Angiography after Cardiac Arrest without ST-Segment Elevation. N Engl J Med. 2019;380(15):1397-1407. DOI: 10.1056/NEJMoa1816897. PMID: 30883057 — ensaio COACT, Netherlands Trial Register NTR4973, 552 randomizados. Financiamento: Netherlands Heart Institute e outros", "Desch S, Freund A, Akin I, Behnes M, Preusch MR, et al. Angiography after Out-of-Hospital Cardiac Arrest without ST-Segment Elevation. N Engl J Med. 2021;385(27):2544-2553. DOI: 10.1056/NEJMoa2101909. PMID: 34459570 — ensaio TOMAHAWK, NCT02750462, 554 randomizados. Financiamento: German Center for Cardiovascular Research"]
---

# Fluxograma: Cuidado pós-parada e decisão de coronariografia

O paciente teve retorno de circulação espontânea (RCE) após parada cardíaca
extra-hospitalar. O primeiro ECG pós-ressuscitação decide o ramo: com supra
de ST não há discussão, mas **sem supra de ST** — o cenário mais comum — a
decisão entre coronariografia imediata e adiada/seletiva é o que os ensaios
COACT e TOMAHAWK responderam, e nenhum dos dois favoreceu a estratégia
imediata.

## Árvore de decisão

```mermaid
flowchart TD
  R0["RCE após parada cardíaca<br/>extra-hospitalar"]
  P1["Realizar ECG de 12 derivações<br/>pós-ressuscitação"]
  D1{"ECG mostra supra de ST?"}
  C1(["Coronariografia imediata"])
  D2{"Instabilidade hemodinâmica ou elétrica<br/>persistente (choque refratário,<br/>tempestade elétrica)?"}
  C2(["COACT/TOMAHAWK não respondem por este paciente<br/>(critério de exclusão dos dois ensaios):<br/>indicação de cateterismo avaliada por outro raciocínio —<br/>seguir via de choque cardiogênico (estágios SCAI<br/>e suporte circulatório mecânico, se indicado)"])
  C3(["Sem urgência demonstrada para coronariografia:<br/>priorizar cuidado pós-parada (temperatura-alvo,<br/>ventilação, hemodinâmica, avaliação neurológica).<br/>Angiografia adiada ou seletiva,<br/>quando o quadro se definir ou houver indicação específica"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Cuidados gerais pós-parada, presentes nos dois ramos sem supra de ST

**Controle de temperatura-alvo.** Nem TTM nem TTM2 mostraram benefício de
hipotermia induzida sobre a alternativa comparada — o que a evidência atual
sustenta é **evitar febre**, não necessariamente induzir frio. O COACT ainda
mostrou que a estratégia de coronariografia imediata **atrasa** o tempo até
atingir a temperatura-alvo, um custo a considerar antes de levar o paciente à
hemodinâmica. Ver `controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2.md`,
nesta mesma pasta.

**Metas hemodinâmicas e de oxigenação, ventilação e avaliação neurológica
seriada** seguem em paralelo, independente do ramo da coronariografia — são
cuidado de suporte contínuo, não uma decisão binária única, e por isso não
entram como ramo da árvore.

## Por que a instabilidade muda a via

COACT e TOMAHAWK testaram pacientes ressuscitados sem sinais de instabilidade
que exigisse outra conduta imediata. **Nenhum dos dois respondeu sobre o
paciente em choque refratário ou tempestade elétrica** — nesses casos, a
indicação de cateterismo pode vir de outro raciocínio clínico, e o caminho é
o do choque cardiogênico (`classificacao-scai-de-estagios-do-choque-cardiogenico.md`
e `choque-cardiogenico-suporte-circulatorio-mecanico-temporario.md`, nesta
mesma pasta), não o desta árvore.

## Armadilha a evitar

Tratar o TOMAHAWK como neutro. O desfecho primário teve HR 1,28 (IC95%
1,00-1,63; p=0,06): formalmente não significativo, mas com os dois pontos
estimados acima de 1 e o intervalo tocando exatamente 1. A leitura correta
é **ausência de benefício da estratégia imediata, com um sinal desfavorável
que não se pode descartar** — não "tanto faz".
