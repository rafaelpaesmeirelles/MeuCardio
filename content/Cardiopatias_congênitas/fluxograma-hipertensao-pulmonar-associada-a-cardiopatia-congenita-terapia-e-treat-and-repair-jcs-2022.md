---
title: "Fluxograma: Hipertensão arterial pulmonar associada à cardiopatia congênita — terapia farmacológica e estratégia Treat and Repair (JCS 2022)"
slug: fluxograma-hipertensao-pulmonar-associada-a-cardiopatia-congenita-terapia-e-treat-and-repair-jcs-2022
theme: "Cardiopatias congênitas"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "PMID 36047167 conferido via PubMed E-utilities (esearch/esummary): autor, revista (Circ J 2022;86(10):1591-1690), data (22/09/2022) e DOI (10.1253/circj.CJ-22-0134) batem exatamente. Texto integral obtido em acesso aberto no J-STAGE (resolução do DOI para jstage.jst.go.jp, PDF de 2,7 MB baixado e convertido com pdftotext -layout), não só o resumo indexado no PubMed — necessário porque as classes de recomendação (Classe/nível) da Seção 4.2 'Pulmonary Hypertension' não aparecem no abstract. Cada nó de conduta reproduz literalmente a classe e o nível de evidência do trecho correspondente da Seção 4.2.2 (Drug Therapy) e 4.2.3 (Unique Pathology in PH in CHD), sem arredondar nem inferir classe onde o texto não a atribui — os critérios de RVP <4 UW (fechar) e >8 UW (contraindicar) aparecem no texto sem rótulo Classe/Nível explícito e foram marcados como 'critério desta diretriz', não como recomendação graduada. Conferido contra o corpus de Cardiopatias_congênitas antes de escrever: os fluxogramas já publicados de CIA (fechar/não fechar por shunt) e de descompensação aguda de Eisenmenger (flebotomia/anticoagulação/hipoxemia na crise) não cobrem a escalada de terapia farmacológica crônica para HAP-CC nem a estratégia 'Treat and Repair' de fechamento tardio de shunt após controle medicamentoso — recorte novo, sem sobreposição."
source_refs: ["Ohuchi H, Kawata M, Uemura H, Akagi T, Yao A, et al. JCS 2022 Guideline on Management and Re-Interventional Therapy in Patients With Congenital Heart Disease Long-Term After Initial Repair. Circulation Journal. 2022;86(10):1591-1690. DOI: 10.1253/circj.CJ-22-0134. PMID: 36047167 — Seção 4.2 'Pulmonary Hypertension' (4.2.1 a 4.2.3) e Tabela 15 'Clinical Categories of PAH in the Distant Postoperative Period of Congenital Heart Disease'."]
---

# Fluxograma: Hipertensão arterial pulmonar associada à cardiopatia congênita — terapia farmacológica e estratégia Treat and Repair (JCS 2022)

A diretriz japonesa de 2022 organiza o manejo da hipertensão arterial pulmonar
associada a shunt (HAP-CC) por **categoria fisiopatológica**, não por um único
algoritmo genérico de hipertensão pulmonar. A Tabela 15 do documento distingue
quatro situações que exigem conduta farmacológica diferente:

- **1.1** — HAP residual, sem shunt residual significativo, depois do
  fechamento do defeito (pode surgir logo após a cirurgia ou décadas depois);
- **1.2** — HAP essencialmente idiopática, com um shunt pequeno ou restritivo
  coincidente, que não é a causa da HAP;
- **1.3** — HAP por shunt grande e não restritivo, ainda não fechado, que
  **ainda não** atingiu a fisiologia de Eisenmenger;
- **1.4** — síndrome de Eisenmenger propriamente dita: RVP tão elevada que o
  shunt inverte, predominantemente direita-esquerda, com hipoxemia e cianose.

A definição de hipertensão pulmonar usada é a do 6º Simpósio Mundial (Nice,
2018): pressão arterial pulmonar média (PAPm) acima de 20 mmHg, com resistência
vascular pulmonar (RVP) de 3 unidades Wood ou mais como critério adicional para
HP pré-capilar.

Três pontos que a árvore torna difíceis de contornar:

- **Nem todo shunt residual deve ser fechado.** No shunt pequeno coincidente
  com HAP essencialmente idiopática (categoria 1.2), a diretriz trata o defeito
  como **válvula de segurança contra a falência do ventrículo direito** — fechar
  esse shunt residual pode ser prejudicial, não benéfico.
- **A escolha do fármaco de primeira linha depende da gravidade, não de
  preferência.** Prostaciclina injetável só é terapia de primeira linha na HAP
  residual grave, com classe funcional da OMS igual ou acima de III e falência
  de ventrículo direito — Classe I, nível C. Fora desse cenário, ela é
  reservada para quando a combinação oral já otimizada falhar.
- **"Treat and Repair" inverte a lógica clássica de contraindicação cirúrgica
  no shunt grande.** RVP acima de 8 unidades Wood tradicionalmente contraindica
  o fechamento — mas a diretriz descreve tratamento agressivo com vasodilatador
  pulmonar seguido de reavaliação hemodinâmica em 3 a 6 meses, para verificar se
  o defeito passou a ser fechável.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto com cardiopatia congênita e hipertensão arterial pulmonar associada a shunt<br/>(HAP-CC), confirmada por cateterismo cardíaco direito: PAPm acima de 20 mmHg<br/>e resistência vascular pulmonar (RVP) igual ou acima de 3 unidades Wood"]
  D1{"Qual a categoria de HAP-CC, pela classificação desta diretriz<br/>— shunt já fechado, shunt pequeno coincidente, ou shunt grande ainda não fechado?"}
  C1(["Tratar como hipertensão arterial pulmonar idiopática isolada.<br/>Não fechar o defeito — ele funciona como válvula de segurança<br/>contra a falência do ventrículo direito"])
  P1["Tratar como hipertensão arterial pulmonar idiopática.<br/>Meta hemodinâmica: PAPm abaixo de 35 mmHg e RVP abaixo de 7,5 unidades Wood<br/>— Classe IIa, nível C"]
  D2{"Classe funcional da OMS e função do ventrículo direito?"}
  C3(["Prostaciclina injetável, intravenosa ou transdérmica, como terapia<br/>de primeira linha — Classe I, nível C. Preferir treprostinil transdérmico<br/>pelo menor risco infeccioso — Classe IIa, nível C; ou epoprostenol intravenoso<br/>se a via intravenosa for escolhida — Classe IIa, nível B"])
  P2["Terapia combinada agressiva desde o início — Classe IIa, nível C,<br/>preferencialmente por via oral combinada — Classe IIa, nível B.<br/>Beraprosta oral não deve ser usada como primeira linha isolada,<br/>só como fármaco de combinação — Classe IIb, nível C"]
  D3{"Resposta inadequada à combinação oral, com função residual<br/>de ventrículo direito baixa e regurgitação atrioventricular igual<br/>ou acima do 3º grau?"}
  C4(["Acrescentar iloprosto inalado como medicação adicional<br/>— Classe IIa, nível C. Iloprosto inalado não deve ser usado como<br/>primeira ou segunda linha isolada — Classe IIb, nível C"])
  C5(["Manter a combinação oral já otimizada,<br/>com reavaliação clínica e hemodinâmica periódica"])
  P3["Determinar, com equipe experiente em HAP associada a cardiopatia congênita,<br/>se o shunt direita-esquerda predominante decorre de síndrome de Eisenmenger,<br/>de causa estrutural/anatômica ou de disfunção da função cardíaca<br/>— Classe IIa, nível C"]
  D4{"Resistência vascular pulmonar (RVP) medida no cateterismo cardíaco direito?"}
  C6(["Fechamento cirúrgico ou percutâneo do defeito indicado<br/>(critério desta diretriz)"])
  C7(["Fechamento contraindicado. Tratar como HAP-CC já estabelecida<br/>(síndrome de Eisenmenger), sem fechar o defeito<br/>(critério desta diretriz)"])
  P4["Consultar especialista com experiência em HAP-CC sobre a estratégia<br/>'Treat and Repair' — Classe IIa, nível C. Terapia combinada agressiva<br/>só é pertinente quando o fechamento futuro for factível<br/>— Classe IIa, nível C"]
  P5["Reavaliar hemodinâmica por cateterismo cardíaco direito e função<br/>cardíaca por ressonância magnética ou ecocardiograma, 3 a 6 meses<br/>após o início da terapia — Classe IIa, nível C"]
  D5{"Critérios de 'Repair' atingidos: o fluxo pulmonar aumenta sem piorar<br/>a função cardíaca, sem elevar a pressão arterial pulmonar, e a RVP<br/>não ultrapassa 7,5 unidades Wood?"}
  C8(["Fechar o defeito após o controle da hipertensão pulmonar<br/>— estratégia Treat and Repair concluída — Classe IIb, nível C"])
  C9(["Não fechar o defeito. Manter tratamento clínico da HAP-CC.<br/>Uso inadequado da medicação já comprometeu a função cardíaca,<br/>o que contraindica o fechamento (critério desta diretriz)"])

  R0 --> D1
  D1 -->|"Categoria 1.2: HAP idiopática com shunt pequeno/restritivo coincidente"| C1
  D1 -->|"Categoria 1.1: HAP residual, sem shunt residual significativo, após fechamento prévio"| P1
  D1 -->|"Categorias 1.3/1.4: HAP por shunt grande ainda não fechado — sem ou já com síndrome de Eisenmenger"| P3
  P1 --> D2
  D2 -->|"Classe funcional OMS igual ou acima de III, com falência grave de ventrículo direito"| C3
  D2 -->|"Classe funcional OMS abaixo de III, sem falência grave de ventrículo direito"| P2
  P2 --> D3
  D3 -->|"Sim"| C4
  D3 -->|"Não"| C5
  P3 --> D4
  D4 -->|"Menor que 4 unidades Wood"| C6
  D4 -->|"Maior que 8 unidades Wood"| C7
  D4 -->|"Entre 4 e 8 unidades Wood — zona limítrofe"| P4
  P4 --> P5
  P5 --> D5
  D5 -->|"Sim"| C8
  D5 -->|"Não"| C9

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## O arsenal farmacológico citado pela diretriz

Fármacos disponíveis no Japão e referidos como base da escada terapêutica:
antagonistas orais do receptor de endotelina (bosentana, ambrisentana,
macitentana), inibidores orais da fosfodiesterase-5 (sildenafila, tadalafila),
um estimulador oral da guanilato ciclase solúvel (riociguate) e derivados da
prostaciclina — epoprostenol intravenoso, treprostinil intravenoso ou
transdérmico, iloprosto inalado, beraprosta oral e selexipague oral. A regra
prática que a diretriz deixa clara: **cada fármaco em combinação mantém a
eficácia esperada de quando usado isolado** — Classe IIa, nível B —, o que
sustenta começar com combinação em vez de escalar um fármaco de cada vez.

## Por que a categoria muda a meta hemodinâmica

Na HAP residual sem shunt (categoria 1.1), a fisiopatologia e a resposta a
fármacos são consideradas equivalentes às da HAP idiopática — só que a HAP
progride mais devagar, porque o fluxo pulmonar elevado que a predispôs já não
existe mais. A meta hemodinâmica citada — PAPm abaixo de 35 mmHg e RVP abaixo
de 7,5 unidades Wood — vem de um relato sobre função ventricular direita
preservada em coração estruturalmente normal, e a diretriz a adota como alvo
de tratamento combinado (Classe IIa, nível C), distinta da meta de PAPm abaixo
de 42,5 mmHg citada para HAP idiopática em geral.

## O que a árvore não mostra

**A combinação inadvertida de vasodilatadores pode piorar o shunt grande
ainda aberto.** A diretriz alerta que, na categoria 1.3/1.4, associar
vasodilatadores pulmonares sem controle cuidadoso pode causar queda abrupta da
RVP com aumento do fluxo pulmonar esquerda-direita, sobrecarregando de volume
o coração e piorando a regurgitação atrioventricular — o oposto do efeito
pretendido. Por isso a diretriz insiste que a administração de fármacos nesse
grupo seja supervisionada por equipe experiente (Classe IIa, nível C).

**Falência de Fontan por RVP elevada é tratada como categoria à parte** (item
2 da Tabela 15, fora desta árvore): bosentana melhora tolerância ao exercício
e hemodinâmica em Fontan em falência, e sildenafila melhora a capacidade de
exercício por via da eficiência ventilatória — mas a diretriz não atribui
classe/nível explícitos a essas observações, e por isso não entraram como
conduta graduada nesta árvore.

**Uso perioperatório de prostaciclina injetável em crise de hipertensão
pulmonar** é conduta separada (Classe I, nível C) — quando a HP piora
abruptamente no perioperatório, o fármaco injetável é usado sem hesitação,
sendo reduzido ou suspenso assim que a fase aguda passa; esse cenário agudo
já está coberto pelo fluxograma de descompensação aguda de Eisenmenger/
cardiopatia cianótica publicado nesta mesma pasta, e não foi duplicado aqui.

**A meia-vida da decisão de fechar depende de uma reavaliação, não de um
único cateterismo.** Na estratégia Treat and Repair, o critério que autoriza o
fechamento — aumento do fluxo pulmonar sem piorar a função cardíaca, sem
elevar a pressão arterial pulmonar e sem que a RVP ultrapasse 7,5 unidades
Wood — só pode ser verificado depois de 3 a 6 meses de terapia (Classe IIa,
nível C), nunca no momento do diagnóstico inicial.
