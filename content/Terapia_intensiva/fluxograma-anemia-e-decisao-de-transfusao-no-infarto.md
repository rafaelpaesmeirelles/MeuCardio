---
title: "Fluxograma: Anemia e decisão de transfusão no infarto"
slug: fluxograma-anemia-e-decisao-de-transfusao-no-infarto
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão para transfusão no paciente com SCA/infarto em curso e anemia: quando sangramento ativo ou instabilidade hemodinâmica muda a conduta, o gatilho de hemoglobina que separa estratégia restritiva e liberal segundo MINT e REALITY, e quando isquemia refratária justifica transfundir acima do corte."
review_status: revisado
source_refs: ["Carson JL, Brooks MM, Hébert PC, Goodman SG, Bertolet M, et al; MINT Investigators. Restrictive or Liberal Transfusion Strategy in Myocardial Infarction and Anemia. N Engl J Med. 2023;389(26):2446-2456. DOI: 10.1056/NEJMoa2307983. PMID: 37952133. PMCID: PMC10837004 — NCT02981407, 3.504 pacientes na análise primária", "Ducrocq G, Gonzalez-Juanatey JR, Puymirat E, Lemesle G, Cachanado M, et al; REALITY Investigators. Effect of a Restrictive vs Liberal Blood Transfusion Strategy on Major Cardiovascular Events Among Patients With Acute Myocardial Infarction and Anemia: The REALITY Randomized Clinical Trial. JAMA. 2021;325(6):552-560. DOI: 10.1001/jama.2021.0135. PMID: 33560322. PMCID: PMC7873781 — NCT02648113, 668 randomizados, aberto, de não inferioridade, 35 hospitais na França e na Espanha. NOTA: existe Erratum em JAMA 2026;336(3):262, registrado mas NÃO lido nesta consulta", "Mazer CD, Whitlock RP, Fergusson DA, Hall J, Belley-Cote E, et al; TRICS Investigators. Restrictive or Liberal Red-Cell Transfusion for Cardiac Surgery. N Engl J Med. 2017;377(22):2133-2144. DOI: 10.1056/NEJMoa1711818. PMID: 29130845 — NCT02042898, 5.243 adultos com EuroSCORE I ≥ 6, aberto, de não inferioridade"]
---

# Fluxograma: Anemia e decisão de transfusão no infarto

No paciente com SCA/infarto em curso e hemoglobina baixa, a decisão de
transfundir não segue o corte restritivo do resto da medicina — o miocárdio
isquêmico depende de oferta de oxigênio, e MINT e REALITY, os dois ensaios que
testaram a pergunta no infarto agudo, terminam sem resposta firme. A árvore
abaixo organiza essa decisão; o que se repete em qualquer ramo está em prosa
logo depois.

## Árvore de decisão

```mermaid
flowchart TD
  R1["SCA/infarto em curso,<br/>com anemia (Hb baixa)"]
  D1{"Sangramento ativo ou<br/>instabilidade hemodinâmica associada?"}
  D2{"Contexto é cirurgia cardíaca<br/>(não IAM primário em curso)?"}
  D3{"Hb < 10 g/dL<br/>(população dos ensaios de IAM:<br/>MINT/REALITY)?"}
  D4{"Hb abaixo do gatilho restritivo<br/>(7 a 8 g/dL, MINT/REALITY)?"}
  D5{"Isquemia refratária ou sintomas<br/>persistentes apesar do gatilho<br/>restritivo não atingido?"}

  C1(["Decisão transfusional individualizada,<br/>guiada por controle do sangramento e<br/>estabilização hemodinâmica — nenhum dos<br/>três ensaios (MINT, REALITY, TRICS-III)<br/>avaliou este cenário.<br/>VERIFICAÇÃO HUMANA NECESSÁRIA<br/>quanto ao gatilho de Hb a aplicar"])
  C2(["Aplicar o limiar do TRICS-III:<br/>transfundir se Hb < 7,5 g/dL<br/>(a partir da indução anestésica).<br/>Estratégia restritiva é não inferior<br/>e reduz a exposição a sangue"])
  C3(["Não transfundir por critério<br/>de anemia agora — fora da população<br/>estudada em MINT/REALITY"])
  C4(["Transfundir — abaixo do gatilho<br/>restritivo, tanto a estratégia restritiva<br/>quanto a liberal indicam transfusão<br/>neste nível de Hb"])
  C5(["Considerar transfundir apesar de Hb<br/>acima do gatilho restritivo — miocárdio<br/>isquêmico depende de oferta de O2;<br/>decisão individualizada, nenhum dos<br/>ensaios testou gatilho por sintoma"])
  C6(["Manter estratégia restritiva<br/>(não transfundir agora) — nem MINT<br/>(p=0,07) nem REALITY (IC inclui<br/>possível dano) demonstram<br/>superioridade da liberal, mas o dano<br/>da restritiva não é excluído"])

  R1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim — cirurgia cardíaca, EuroSCORE I ≥ 6"| C2
  D2 -->|"Não — IAM/SCA primário"| D3
  D3 -->|"Não (Hb ≥ 10 g/dL)"| C3
  D3 -->|"Sim (Hb < 10 g/dL)"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| D5
  D5 -->|"Sim"| C5
  D5 -->|"Não"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que se repete em todo ramo, e por isso não está no diagrama

**Reavaliação periódica.** A hemoglobina e o quadro isquêmico (dor, alterações
de ECG, instabilidade) são checados de novo a cada nova unidade transfundida
ou a cada piora clínica — a decisão não é tomada uma única vez na admissão.

**Tratamento do infarto em curso segue em paralelo**, pela via já estabelecida
para SCA (antiplaquetário, anticoagulação, estratégia de reperfusão) — este
fluxograma cobre só a decisão transfusional, não substitui o protocolo de SCA.

**Não estender o limiar do TRICS-III ao IAM primário**, e vice-versa: os
cortes restritivos diferem (7,5 g/dL na cirurgia cardíaca; 7-8 g/dL no
infarto) e os cenários fisiopatológicos não são intercambiáveis — por isso a
árvore separa os dois logo no início (nó D2).

**Nenhum dos três ensaios avalia isquemia ativa com instabilidade
hemodinâmica ou sangramento ativo.** Onde a árvore chega em C1, a literatura
citada não define um número — a conduta é clínica, à beira do leito.
