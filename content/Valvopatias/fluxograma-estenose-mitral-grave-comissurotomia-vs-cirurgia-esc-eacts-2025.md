---
title: "Fluxograma: Estenose Mitral Reumática Grave — Comissurotomia Percutânea versus Cirurgia (ESC/EACTS 2025)"
slug: fluxograma-estenose-mitral-grave-comissurotomia-vs-cirurgia-esc-eacts-2025
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir da Recommendation Table 8 e da lista de contraindicações da diretriz ESC/EACTS 2025 (PMID 40878295). A elegibilidade técnica para CMP é verificada antes de usar alto risco cirúrgico como razão para escolhê-la: trombo em AE, IM mais que leve, calcificação grave/bicomissural, ausência de fusão comissural ou outra doença que exija cirurgia continuam sendo contraindicações. Trombo restrito ao apêndice atrial esquerdo só permite reconsiderar CMP após 1–3 meses de anticoagulação e confirmação de resolução por ETE. A árvore preserva as recomendações: CMP em sintomático sem características desfavoráveis (I/B), CMP em sintomático com contraindicação/alto risco cirúrgico quando tecnicamente elegível (I/C), cirurgia em sintomático não elegível para CMP (I/C), CMP em anatomia subótima isolada (IIa/C) e em assintomático de alto risco sem características desfavoráveis (IIa/C)."
source_refs: ["Praz F, Borger MA, Lanz J, et al.; ESC/EACTS Scientific Document Group. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4747. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295 — Seção 10 (Mitral stenosis), Figura 14, Recommendation Table 8 e Tabela suplementar S3 (escore de Wilkins), já reproduzidas no documento 'estenose-mitral-diagnostico-e-manejo-esc-eacts-2025.md' desta pasta; título/revista/ano reconferidos nesta sessão via PubMed E-utilities."]
---

# Fluxograma: Estenose Mitral Reumática Grave — Comissurotomia Percutânea versus Cirurgia (ESC/EACTS 2025)

A estenose mitral é a valvopatia mais associada à febre reumática e uma causa
importante de morbimortalidade em países de baixa e média renda — e, ao
contrário da estenose aórtica, a decisão entre tratamento percutâneo
(comissurotomia mitral percutânea, CMP) e cirurgia depende tanto da anatomia da
valva quanto da presença de sintomas. Este fluxograma organiza essa decisão para
a estenose mitral **reumática**; a forma degenerativa por calcificação do anel
mitral (MAC) não é candidata a CMP e segue conduta própria, descrita ao final.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Estenose mitral reumática<br/>clinicamente grave confirmada<br/>(área valvar mitral ≤1,5 cm²)"] --> D1{"Sintomática?"}

  D1 -->|"Não"| D2{"Alto risco tromboembólico (embolia<br/>sistêmica prévia, contraste espontâneo<br/>denso em átrio esquerdo, fibrilação<br/>atrial nova/paroxística) e/ou alto risco<br/>de descompensação hemodinâmica<br/>(PSAP >50 mmHg em repouso, cirurgia<br/>não cardíaca de grande porte planejada,<br/>gestante ou desejo de gestar), sem<br/>características clínicas e anatômicas<br/>desfavoráveis?"}

  D2 -->|"Sim"| C1(["CMP deve ser considerada —<br/>Classe IIa, Nível C"])

  D2 -->|"Não"| C2(["Vigilância clínica e<br/>ecocardiográfica anual"])

  D1 -->|"Sim"| D3{"Contraindicação formal à CMP:<br/>trombo em AE, IM mais que leve,<br/>calcificação grave/bicomissural,<br/>ausência de fusão comissural ou<br/>outra doença que exija cirurgia?"}

  D3 -->|"Sim"| D3b{"Risco cirúrgico aceitável?"}

  D3b -->|"Sim"| C6(["Cirurgia da valva mitral —<br/>Classe I, Nível C"])

  D3b -->|"Não"| C7(["Heart Team: tratar sintomas e risco<br/>tromboembólico, avaliar reversibilidade<br/>da contraindicação e alternativas;<br/>alto risco cirúrgico não torna uma CMP<br/>tecnicamente contraindicada segura"])

  D3 -->|"Não"| D4{"Contraindicação a cirurgia,<br/>ou alto risco cirúrgico?"}

  D4 -->|"Sim"| C3(["CMP recomendada se tecnicamente<br/>viável, mesmo com características<br/>desfavoráveis não impeditivas —<br/>Classe I, Nível C"])

  D4 -->|"Não"| D5{"Características clínicas/anatômicas<br/>desfavoráveis não impeditivas —<br/>Wilkins >8, Cormier 3, IT grave,<br/>idade avançada, FA permanente,<br/>NYHA IV ou HP grave?"}

  D5 -->|"Nenhuma presente"| C4(["CMP recomendada —<br/>Classe I, Nível B"])

  D5 -->|"Anatomia subótima isolada,<br/>sem característica clínica<br/>desfavorável"| C5(["CMP deve ser considerada<br/>como tratamento inicial —<br/>Classe IIa, Nível C"])

  D5 -->|"Outras características<br/>desfavoráveis"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O escore de Wilkins, resumido

O nó D5 usa o escore de Wilkins como um dos critérios de anatomia desfavorável.
São quatro componentes avaliados por ecocardiograma — mobilidade do folheto,
espessamento do folheto, calcificação, e espessamento/calcificação do aparato
subvalvular —, cada um pontuado de 1 a 4, somando de 4 a 16. Escore ≤8 prediz
sucesso do tratamento percutâneo; a própria diretriz usa **escore >8** como um
dos critérios que definem anatomia desfavorável, junto com Cormier grupo 3 e
insuficiência tricúspide grave — não é o único critério, e por isso a árvore o
trata como parte de um conjunto no nó D5, não como pergunta isolada.

## Por que sintoma decide antes da anatomia

Repare que a árvore pergunta primeiro se o paciente é sintomático (D1) e então
separa contraindicação **à CMP** (D3) de contraindicação ou alto risco
**cirúrgico** (D4). Em paciente de alto risco cirúrgico, a CMP pode ser usada
mesmo com características desfavoráveis não impeditivas; isso não supera uma
contraindicação técnica formal, como IM mais que leve ou ausência de fusão
comissural.

**Trombo no apêndice atrial esquerdo é uma exceção condicionada.** A CMP só
pode ser reconsiderada após 1–3 meses de anticoagulação e ETE demonstrando
resolução; trombo persistente continua contraindicação.

## O que a árvore não mostra

- **Estenose mitral degenerativa (calcificação do anel mitral) não está aqui.**
  Não há fusão comissural para tratar, então CMP **não é uma opção** nessa
  forma da doença — a conduta é terapia clínica, e cirurgia (tecnicamente mais
  desafiadora, mas com mortalidade <5% relatada em centros experientes) ou
  implante transcateter de valva mitral (TMVI) em paciente sintomático
  refratário e de alto risco. Detalhado no mesmo documento de origem desta
  árvore, seção de estenose mitral degenerativa.
- **Doença valvar múltipla exige avaliação separada do Heart Team** — cirurgia
  é preferida à CMP quando há doença aórtica grave associada; em doença
  aórtica moderada, a CMP pode postergar o tratamento cirúrgico das duas
  valvas.
- **DOAC deve ser evitado com área valvar mitral ≤2,0 cm²** — corte diferente do
  usado para definir gravidade clínica (≤1,5 cm²), e não representado nesta
  árvore por não ser uma decisão de intervenção.
- **Seguimento pós-CMP não está na árvore.** Reestenose assintomática pode
  ocorrer, e a área valvar e o gradiente médio pós-procedimento continuam
  sendo acompanhados por ecocardiograma.
