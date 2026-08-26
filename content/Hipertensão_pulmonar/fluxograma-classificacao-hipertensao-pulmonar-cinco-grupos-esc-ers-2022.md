---
title: "Fluxograma: Hipertensão Pulmonar — do achado hemodinâmico do cateterismo à classificação nos cinco grupos clínicos (ESC/ERS 2022)"
slug: fluxograma-classificacao-hipertensao-pulmonar-cinco-grupos-esc-ers-2022
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir do documento já publicado e revisado 'hipertensao-pulmonar-diagnostico-e-tratamento-escers-2022.md' desta pasta, cujo review_note original registra texto integral conferido em 01/08/2026 (PDF completo via Oxford Academic/Silverchair) contra a diretriz ESC/ERS 2022 (PMID 36017548). Os quatro subtipos hemodinâmicos (pré-capilar, pós-capilar isolada, combinada pré e pós-capilar, não classificável, com os cortes de PAPm/POCP/RVP) e a composição dos cinco grupos clínicos foram conferidos de novo nesta sessão em 26/08/2026 por WebFetch direto ao texto da diretriz em academic.oup.com/eurheartj/article/43/38/3618/6673929, que devolveu os mesmos cinco grupos e os mesmos três cortes hemodinâmicos (PAPm >20 mmHg; pré-capilar POCP ≤15 mmHg e RVP >2 UW; pós-capilar isolada POCP >15 mmHg e RVP ≤2 UW; combinada POCP >15 mmHg e RVP >2 UW) já registrados no documento-fonte — sem divergência. Nenhum PMID ou DOI novo foi usado; a árvore não repete os ângulos já cobertos pelos quatro fluxogramas existentes desta pasta (algoritmo diagnóstico em três passos, vasorreatividade aguda/bloqueador de canal de cálcio, estratificação de risco/terapia combinada inicial na HAP, e CTEPH/operabilidade/BPA/riociguate) — este fluxograma cobre especificamente o passo intermediário que os demais citam mas não detalham: como o padrão hemodinâmico do cateterismo e o contexto clínico levam a um dos cinco grupos."
source_refs: ["Humbert M, Kovacs G, Hoeper MM, et al. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548 — já citado e com texto integral conferido em 'hipertensao-pulmonar-diagnostico-e-tratamento-escers-2022.md' desta pasta; classificação hemodinâmica e clínica em cinco grupos reconferida nesta sessão contra o texto da diretriz via academic.oup.com/eurheartj/article/43/38/3618/6673929.", "Brasil. Ministério da Saúde. Secretaria de Atenção Especializada à Saúde; Secretaria de Ciência, Tecnologia, Inovação e Complexo da Saúde. Portaria Conjunta nº 10, de 18 de julho de 2023. Aprova o Protocolo Clínico e Diretrizes Terapêuticas da Hipertensão Pulmonar — citada em 'hipertensao-pulmonar-diagnostico-e-tratamento-escers-2022.md' desta pasta como fonte do critério de acesso ao tratamento pelo SUS (PAPm ≥25 mmHg para custeio, distinto do corte diagnóstico de 20 mmHg), mencionado na seção de armadilhas clínicas deste fluxograma."]
---

# Fluxograma: Hipertensão Pulmonar — classificação em cinco grupos clínicos (ESC/ERS 2022)

Confirmar hipertensão pulmonar por cateterismo cardíaco direito (PAPm acima de
20 mmHg em repouso) é só a metade do trabalho diagnóstico — a diretriz ESC/ERS
2022 exige, na sequência, classificar o paciente em um dos **cinco grupos
clínicos**, porque tratamento, prognóstico e o próprio risco de vasodilatador
pulmonar mudam radicalmente de um grupo para outro. Esse passo é citado pelo
fluxograma diagnóstico desta pasta ("classificar o grupo hemodinâmico") sem
ser detalhado — é o que este fluxograma resolve, a partir dos três cortes
hemodinâmicos do cateterismo (POCP e RVP) e do contexto clínico que separa,
dentro do padrão pré-capilar, os grupos 1, 3, 4 e 5.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Hipertensão pulmonar confirmada por cateterismo direito<br/>PAPm > 20 mmHg em repouso (ESC/ERS 2022)"] --> D1{"POCP e RVP no mesmo cateterismo?"}

  D1 -->|"POCP ≤15 mmHg e RVP >2 UW"| P1["Padrão pré-capilar<br/>presente nos grupos 1, 3, 4 e 5"]

  D1 -->|"POCP >15 mmHg e RVP ≤2 UW"| C1(["Hipertensão pós-capilar isolada (IpcPH)<br/>predominantemente grupo 2 — doença cardíaca esquerda<br/>tratar a doença de base; vasodilatador pulmonar pode piorar a congestão"])

  D1 -->|"POCP >15 mmHg e RVP >2 UW"| C2(["Hipertensão combinada pré e pós-capilar (CpcPH)<br/>componente vascular pulmonar sobreposto à congestão venosa<br/>avaliar em centro de referência antes de tratar como grupo 1"])

  D1 -->|"POCP ≤15 mmHg e RVP ≤2 UW"| C3(["Não classificável hemodinamicamente<br/>reavaliar contexto clínico e considerar repetir a medida"])

  P1 --> D2{"Doença pulmonar, tromboembólica ou multifatorial associada?"}

  D2 -->|"defeito de perfusão na cintilografia V/Q + trombo crônico organizado na angioTC, após 3 meses ou mais de anticoagulação terapêutica"| C4(["Grupo 4 — hipertensão pulmonar tromboembólica crônica (CTEPH)<br/>ou obstrução arterial pulmonar por outra causa<br/>único grupo com tratamento potencialmente curativo (endarterectomia)"])

  D2 -->|"doença pulmonar obstrutiva, restritiva ou hipóxia significativa (inclui grande altitude)"| C5(["Grupo 3 — hipertensão pulmonar por doença pulmonar ou hipóxia<br/>otimizar a doença de base antes de considerar fármaco específico"])

  D2 -->|"doença hematológica, sistêmica, metabólica, renal crônica ou mecanismo não esclarecido/multifatorial"| C6(["Grupo 5 — hipertensão pulmonar multifatorial<br/>tratar a condição associada; sem terapia específica de HAP validada"])

  D2 -->|"sem doença pulmonar, tromboembólica ou multifatorial significativa"| D3{"Fator associado identificável?"}

  D3 -->|"idiopática, hereditária (ex.: mutação BMPR2) ou induzida por droga/toxina"| C7(["Grupo 1 — HAP idiopática, hereditária ou induzida por droga/toxina<br/>avaliar teste de vasorreatividade aguda antes da terapia combinada"])

  D3 -->|"associada a doença do tecido conjuntivo, HIV, hipertensão portal, cardiopatia congênita ou esquistossomose"| C8(["Grupo 1 — HAP associada<br/>tratar a condição de base em paralelo à terapia específica de HAP"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

Os quatro subtipos hemodinâmicos da primeira decisão não são compartimentos
estanques: o padrão pré-capilar aparece nos grupos 1, 3, 4 e 5, e é só o
contexto clínico da segunda decisão que separa esses quatro entre si. Já a
hipertensão pós-capilar isolada e a combinada apontam predominantemente para
o grupo 2 — doença cardíaca esquerda —, mas a diretriz não trata isso como
automático: a forma combinada, em particular, tem componente vascular
pulmonar sobreposto à congestão venosa e exige avaliação em centro de
referência antes de se descartar HAP concomitante.

## Os três cortes que definem o subtipo hemodinâmico

- **pré-capilar**: PAPm acima de 20 mmHg, POCP igual ou abaixo de 15 mmHg,
  RVP acima de 2 unidades Wood (UW)
- **pós-capilar isolada (IpcPH)**: PAPm acima de 20 mmHg, POCP acima de
  15 mmHg, RVP igual ou abaixo de 2 UW
- **combinada pré e pós-capilar (CpcPH)**: PAPm acima de 20 mmHg, POCP acima
  de 15 mmHg, RVP acima de 2 UW
- **não classificável**: PAPm acima de 20 mmHg, POCP igual ou abaixo de
  15 mmHg e RVP igual ou abaixo de 2 UW — combinação rara que não se encaixa
  em nenhum dos três padrões acima e pede reavaliação

## Por que a classificação em grupo muda a conduta

Tratar hipertensão pulmonar do grupo 2 como se fosse do grupo 1 é uma das
armadilhas clínicas mais citadas da diretriz: a conduta correta é tratar a
doença cardíaca esquerda de base, e um vasodilatador pulmonar específico de
HAP pode piorar a congestão em vez de ajudar. O mesmo raciocínio de
especificidade vale para os outros grupos — o grupo 4 (CTEPH) é o único com
possibilidade de cura cirúrgica pela endarterectomia pulmonar; o grupo 3 exige
otimizar a doença pulmonar antes de qualquer fármaco específico, com uso
restrito e individualizado em centro de referência; e o grupo 5 não tem
terapia específica de HAP validada, sendo o tratamento direcionado à condição
associada.

## Nota sobre o corte de acesso ao tratamento no Brasil

O corte diagnóstico de PAPm acima de 20 mmHg desta árvore é o da ESC/ERS 2022.
O Protocolo Clínico e Diretrizes Terapêuticas brasileiro (Portaria Conjunta
SAES/SECTICS nº 10/2023) reconhece esse limiar para diagnóstico, mas mantém
PAPm igual ou acima de 25 mmHg como critério para **custear** o tratamento
medicamentoso específico do grupo 1 pelo SUS — um paciente com PAPm entre 21 e
24 mmHg é hipertenso pulmonar pela definição atual, mas fica fora do critério
de acesso a esse tratamento pelo protocolo público, e deve ser monitorizado
com cautela em vez de tratado por ele. São dois limiares com propósitos
diferentes — diagnosticar e custear —, e confundir um pelo outro é o erro.
