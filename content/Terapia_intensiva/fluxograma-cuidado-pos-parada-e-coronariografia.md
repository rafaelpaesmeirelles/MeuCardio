---
title: "Fluxograma: Cuidado pós-parada e decisão de coronariografia"
slug: fluxograma-cuidado-pos-parada-e-coronariografia
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão do primeiro ECG pós-RCE: angiografia emergente no supra persistente; sem supra, seleção individual exige etiologia cardíaca suspeita e choque, instabilidade elétrica recorrente ou isquemia em curso; estratégia adiada/seletiva no paciente estável."
review_status: revisado
review_note: "Atualizado em 26/08/2026 contra o cuidado pós-parada AHA 2025 (PMID 41122894). Removido o absoluto 'com supra, sem discussão': angiografia emergente é recomendada no supra persistente e pode ser razoável, sem supra, em paciente selecionado de etiologia cardíaca suspeita com choque, instabilidade elétrica recorrente ou isquemia em curso. Paradas de causa claramente não cardíaca não entram nesse ramo apenas pela instabilidade. COACT/TOMAHAWK continuam sustentando não usar angiografia imediata de rotina no paciente estável sem supra."
source_refs: ["Hirsch KG, Amorim E, Coppler PJ, et al. Part 11: Post-Cardiac Arrest Care: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16 Suppl 2):S673-S718. DOI: 10.1161/CIR.0000000000001375. PMID: 41122894.", "Lemkes JS, Janssens GN, van der Hoeven NW, Jewbali LSD, Dubois EA, et al. Coronary Angiography after Cardiac Arrest without ST-Segment Elevation. N Engl J Med. 2019;380(15):1397-1407. DOI: 10.1056/NEJMoa1816897. PMID: 30883057 — ensaio COACT, Netherlands Trial Register NTR4973, 552 randomizados. Financiamento: Netherlands Heart Institute e outros", "Desch S, Freund A, Akin I, Behnes M, Preusch MR, et al. Angiography after Out-of-Hospital Cardiac Arrest without ST-Segment Elevation. N Engl J Med. 2021;385(27):2544-2553. DOI: 10.1056/NEJMoa2101909. PMID: 34459570 — ensaio TOMAHAWK, NCT02750462, 554 randomizados. Financiamento: German Center for Cardiovascular Research"]
---

# Fluxograma: Cuidado pós-parada e decisão de coronariografia

O paciente teve retorno de circulação espontânea (RCE) após parada cardíaca
extra-hospitalar. O primeiro ECG pós-ressuscitação decide o ramo: com supra
persistente, angiografia emergente é recomendada; **sem supra de ST**, primeiro
é necessário haver **etiologia cardíaca suspeita**. Nesse grupo, choque,
instabilidade elétrica recorrente e isquemia em curso separam o paciente que
pode precisar de avaliação invasiva emergente daquele estável em que COACT e
TOMAHAWK não demonstraram benefício da estratégia imediata de rotina.

## Árvore de decisão

```mermaid
flowchart TD
  R0["RCE após parada cardíaca<br/>extra-hospitalar"]
  P1["Realizar ECG de 12 derivações<br/>pós-ressuscitação"]
  D1{"ECG mostra supra de ST?"}
  C1(["Supra persistente:<br/>coronariografia emergente recomendada"])
  D2{"Sem supra: há etiologia cardíaca<br/>suspeita para a parada?"}
  D3{"Choque cardiogênico, instabilidade elétrica<br/>recorrente ou evidência de isquemia<br/>miocárdica significativa em curso?"}
  C2(["Sem supra, mas alto risco em curso:<br/>coronariografia emergente pode ser razoável<br/>em paciente selecionado; ponderar probabilidade<br/>de lesão culpada, risco do procedimento e prognóstico global"])
  C3(["Estável e sem supra:<br/>não indicar coronariografia imediata de rotina;<br/>priorizar cuidado pós-parada e usar estratégia<br/>adiada ou seletiva quando houver indicação específica"])
  C4(["Causa claramente não cardíaca<br/>(afogamento, overdose, falência respiratória etc.):<br/>tratar a etiologia e não indicar coronariografia<br/>emergente apenas por choque ou arritmia;<br/>reavaliar se surgir indicação coronária independente"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Não — causa não cardíaca definida"| C4
  D2 -->|"Sim"| D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Cuidados gerais pós-parada, presentes nos dois ramos sem supra de ST

**Controle protocolizado de temperatura.** TTM e TTM2 não demonstraram
superioridade da hipotermia induzida sobre os comparadores estudados; isso não
autoriza abandonar o controle de temperatura nem tolerar febre. O COACT ainda
mostrou que a estratégia de coronariografia imediata atrasou o tempo até a
temperatura-alvo. Ver
[Controle de temperatura pós-parada: TTM e TTM2](controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2.md).

**Metas hemodinâmicas e de oxigenação, ventilação e avaliação neurológica
seriada** seguem em paralelo, independente do ramo da coronariografia — são
cuidado de suporte contínuo, não uma decisão binária única, e por isso não
entram como ramo da árvore.

## Por que a instabilidade muda a via

COACT e TOMAHAWK testaram pacientes ressuscitados sem sinais de instabilidade
que exigissem outra conduta imediata. Portanto, seus resultados não devem ser
extrapolados ao choque, à instabilidade elétrica recorrente ou à isquemia em
curso. A AHA 2025 admite angiografia emergente como opção razoável em pacientes
selecionados **com etiologia cardíaca suspeita** desse ramo. Choque ou arritmia
após afogamento, overdose, falência respiratória ou outra causa claramente não
cardíaca não satisfazem isoladamente esse requisito. A estabilização segue conectada à
[classificação SCAI do choque](classificacao-scai-de-estagios-do-choque-cardiogenico.md)
e ao [suporte circulatório mecânico temporário](choque-cardiogenico-suporte-circulatorio-mecanico-temporario.md).

## Armadilha a evitar

Tratar o TOMAHAWK como neutro. O desfecho primário teve HR 1,28 (IC95%
1,00-1,63; p=0,06): formalmente não significativo, mas com os dois pontos
estimados acima de 1 e o intervalo tocando exatamente 1. A leitura correta
é **ausência de benefício da estratégia imediata, com um sinal desfavorável
que não se pode descartar** — não "tanto faz".
