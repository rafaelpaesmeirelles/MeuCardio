---
title: "Fluxograma: Perfis Hemodinâmicos na IC Aguda e Escolha entre Vasodilatador e Inotrópico"
slug: fluxograma-perfis-hemodinamicos-vasodilatador-inotropico-ic-aguda
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Zoom decisório sobre um recorte que o fluxograma geral já publicado ('fluxograma-insuficiencia-cardiaca-aguda-descompensada.md') não detalha — os quatro perfis hemodinâmicos completos de Nohria-Stevenson (quente/frio × úmido/seco) e a escolha entre vasodilatador e inotrópico dentro deles, em vez de só o eixo de perfusão associado à escalada diurética. Nenhum PMID/DOI novo foi introduzido: Nohria-Stevenson PMID 12767667, os três ensaios de vasodilatador (ASCEND-HF/nesiritida PMID 21732835, RELAX-AHF-2/serelaxina PMID 31433919, TRUE-AHF/ularitida PMID 28402745) e o OPTIME-CHF com a subanálise por etiologia (PMID 11911756 e PMID 12651048) já estavam verificados e publicados nesta mesma pasta antes desta sessão, em 'vasodilatadores-endovenosos-na-ic-aguda-por-que-nesiritida-serelaxina-e-ularitida-falharam.md' e 'suporte-inotropico-na-ic-aguda-descompensada-optime-chf-e-o-sinal-na-etiologia-isquemica.md'. Consistente com o documento-fonte de vasodilatadores, este fluxograma é explícito que nenhum dos três ensaios de vasodilatador demonstrou benefício em desfecho clínico duro — o vasodilatador aqui é posicionado para alívio sintomático em congestão hipertensiva, não como terapia modificadora de prognóstico, para não repetir o erro de leitura que os próprios ensaios corrigiram. O ramo de choque cardiogênico franco não é detalhado aqui de propósito — remete ao fluxograma dedicado já publicado em Terapia Intensiva ('fluxograma-choque-cardiogenico-estagios-scai.md'), evitando duplicar seu conteúdo."
source_refs: ["Nohria A, Tsang SW, Fang JC, et al. Clinical assessment identifies hemodynamic profiles that predict outcomes in patients admitted with heart failure. J Am Coll Cardiol. 2003;41(10):1797-1804. DOI: 10.1016/s0735-1097(03)00309-7. PMID: 12767667", "O'Connor CM, Starling RC, Hernandez AF, et al; ASCEND-HF Investigators. Effect of nesiritide in patients with acute decompensated heart failure. N Engl J Med. 2011;365(1):32-43. DOI: 10.1056/NEJMoa1100171. PMID: 21732835", "Metra M, Teerlink JR, Cotter G, et al; RELAX-AHF-2 Committees Investigators. Effects of Serelaxin in Patients with Acute Heart Failure. N Engl J Med. 2019;381(8):716-726. DOI: 10.1056/NEJMoa1801291. PMID: 31433919", "Packer M, O'Connor C, McMurray JJV, et al; TRUE-AHF Investigators. Effect of Ularitide on Cardiovascular Mortality in Acute Heart Failure. N Engl J Med. 2017;376(20):1956-1964. DOI: 10.1056/NEJMoa1601895. PMID: 28402745", "Cuffe MS, Califf RM, Adams KF Jr, et al; OPTIME-CHF Investigators. Short-term intravenous milrinone for acute exacerbation of chronic heart failure: a randomized controlled trial. JAMA. 2002;287(12):1541-1547. DOI: 10.1001/jama.287.12.1541. PMID: 11911756", "Felker GM, Benza RL, Chandler AB, et al; OPTIME-CHF Investigators. Heart failure etiology and response to milrinone in decompensated heart failure: results from the OPTIME-CHF study. J Am Coll Cardiol. 2003;41(6):997-1003. DOI: 10.1016/S0735-1097(02)02968-6. PMID: 12651048", "2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726."]
---

# Fluxograma: Perfis Hemodinâmicos na IC Aguda e Escolha entre Vasodilatador e Inotrópico

O fluxograma geral de IC aguda descompensada, já publicado nesta pasta,
detalha a escalada diurética no eixo quente-frio associado à congestão
("úmido"). Este documento faz o zoom que faltava: os **quatro perfis
completos** de Nohria-Stevenson — cruzando congestão (úmido/seco) com
perfusão (quente/frio) — e a escolha entre **vasodilatador** e **inotrópico**
dentro de cada um. O ponto mais importante para não repetir aqui é o que os
três grandes ensaios de vasodilatador (nesiritida, serelaxina, ularitida)
ensinaram: nenhum demonstrou benefício em desfecho clínico duro — o
vasodilatador tem lugar para **alívio sintomático em congestão hipertensiva**,
não como terapia que muda prognóstico.

## Árvore de decisão

```mermaid
flowchart TD
  R0["IC aguda descompensada — perfil<br/>hemodinâmico por congestão (úmido/seco)<br/>e perfusão (quente/frio),<br/>Nohria-Stevenson"]
  D1{"Perfil de congestão: úmido<br/>(congestionado) ou seco (sem congestão<br/>evidente)?"}
  D2{"Perfil de perfusão, no paciente seco:<br/>quente ou frio?"}
  C1(["Quente-seco (perfil A) — geralmente<br/>não exige terapia intravenosa; ajustar a<br/>terapia oral crônica (GDMT),<br/>investigar e tratar a causa da<br/>descompensação e otimizar o<br/>acompanhamento ambulatorial"])
  C2(["Frio-seco (perfil L) — cautela com<br/>diurético e vasodilatador, que podem<br/>piorar a hipoperfusão; considerar prova<br/>de volume cautelosa se houver hipovolemia<br/>genuína, ou inotrópico se disfunção<br/>sistólica grave sustenta o baixo débito;<br/>evitar vasodilatador isolado neste<br/>perfil"])
  D3{"Perfil de perfusão, no paciente<br/>úmido: quente ou frio?"}
  D4{"Quente-úmido: PA sistólica<br/>elevada/preservada (perfil hipertensivo)?"}
  C3(["Vasodilatador IV (nitroglicerina ou<br/>nitroprussiato) associado a diurético —<br/>alívio sintomático rápido na congestão<br/>hipertensiva; nenhum dos grandes ensaios<br/>de vasodilatador (nesiritida ASCEND-HF,<br/>serelaxina RELAX-AHF-2, ularitida<br/>TRUE-AHF) demonstrou benefício em<br/>desfecho clínico duro — usar para o<br/>sintoma, não para o prognóstico"])
  C4(["Diurético IV isolado é a conduta<br/>central — ver fluxograma dedicado de<br/>resistência diurética se a resposta for<br/>inadequada; vasodilatador não indicado<br/>rotineiramente sem hipertensão"])
  D5{"Frio-úmido: choque cardiogênico franco<br/>(hipotensão persistente + hipoperfusão<br/>orgânica)?"}
  C5(["Priorizar suporte hemodinâmico e<br/>avaliação de suporte circulatório<br/>mecânico — seguir o fluxograma dedicado<br/>de choque cardiogênico (estágios SCAI);<br/>associar diurético IV assim que a<br/>perfusão permitir"])
  D6{"Sem choque franco — baixo débito<br/>persistente: etiologia isquêmica?"}
  C6(["Cautela com inotrópico (milrinone) —<br/>o OPTIME-CHF mostrou sinal de pior<br/>desfecho em etiologia isquêmica;<br/>considerar vasopressor ou suporte<br/>mecânico antes de inotrópico neste<br/>subgrupo, associando diurético IV assim<br/>que a perfusão permitir"])
  C7(["Inotrópico (ex. milrinone ou<br/>dobutamina) pode ser associado ao<br/>diurético para o baixo débito<br/>persistente — sem excesso de sinal<br/>desfavorável em etiologia não isquêmica<br/>(OPTIME-CHF); reavaliar continuamente a<br/>necessidade de escalonamento"])

  R0 --> D1
  D1 -->|"Seco — sem congestão"| D2
  D1 -->|"Úmido — com congestão"| D3
  D2 -->|"Quente — perfusão preservada"| C1
  D2 -->|"Frio — hipoperfundido"| C2
  D3 -->|"Quente — perfusão preservada"| D4
  D3 -->|"Frio — hipoperfundido"| D5
  D4 -->|"Sim — perfil hipertensivo"| C3
  D4 -->|"Não — PA normal/baixa-normal"| C4
  D5 -->|"Sim — choque cardiogênico franco"| C5
  D5 -->|"Não — baixo débito sem choque"| D6
  D6 -->|"Sim — etiologia isquêmica"| C6
  D6 -->|"Não — etiologia não isquêmica"| C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**Dose e titulação de cada vasoativo** — não são objeto deste fluxograma. Ver
`content/Farmacologia/choque-cardiogenico-vasoativos-acc-2025-arvore-de-dose.md`
para dose de vasopressor/inotrópico no choque.

**Estágios SCAI do choque cardiogênico**, incluindo o resultado negativo do
ECLS-SHOCK para ECMO venoarterial precoce de rotina, não são repetidos aqui —
ver `content/Terapia_intensiva/fluxograma-choque-cardiogenico-estagios-scai.md`.

**Escalada da estratégia diurética quando a resposta é inadequada** também não
é repetida — ver `fluxograma-resistencia-diuretica-e-congestao-refrataria-na-ic-aguda.md`,
nesta mesma pasta.

**Não há corte numérico validado** de PA sistólica que defina "perfil
hipertensivo" em D4 — a distinção é clínica, apoiada em tendência e sintoma,
não em um limiar único fixado pelas fontes revisadas.

**Monitorização hemodinâmica invasiva (cateter de artéria pulmonar)** para
confirmar o perfil quando o exame clínico é ambíguo não é discutida aqui — ver
`cateter-de-arteria-pulmonar-no-choque-cardiogenico-escape-e-o-limite-do-dado-observacional.md`
em Terapia Intensiva.