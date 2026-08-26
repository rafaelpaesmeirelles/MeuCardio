---
title: "Fluxograma: Estenose Mitral Reumática Grave — Comissurotomia Percutânea versus Cirurgia (ESC/EACTS 2025)"
slug: fluxograma-estenose-mitral-grave-comissurotomia-vs-cirurgia-esc-eacts-2025
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída inteiramente a partir do documento já publicado e revisado nesta pasta 'estenose-mitral-diagnostico-e-manejo-esc-eacts-2025.md', que já reproduz a Recommendation Table 8 e a lista de contraindicações da diretriz ESC/EACTS 2025 (fonte primária: Praz F, Borger MA, Lanz J, et al. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4747. PMID 40878295, texto integral conferido em 30/07/2026). Nesta sessão reconferi PMID 40878295 via PubMed E-utilities (esummary): título, revista e ano batem exatamente com o já citado. A árvore reproduz as seis linhas de recomendação da tabela (CMP em sintomático sem características desfavoráveis, I/B; CMP em sintomático com contraindicação/alto risco cirúrgico, I/C; cirurgia em sintomático não elegível para CMP, I/C; CMP como tratamento inicial em anatomia subótima isolada, IIa/C; CMP em assintomático de alto risco tromboembólico/hemodinâmico sem características desfavoráveis, IIa/C) sem acrescentar classe/nível não presente na fonte. O corte de gravidade (AVM ≤1,5 cm²) e as contraindicações formais à CMP (trombo em AE fora do apêndice, IM mais que leve, calcificação grave/bicomissural) vêm do mesmo documento já revisado."
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

  D1 -->|"Sim"| D3{"Contraindicação a cirurgia,<br/>ou alto risco cirúrgico?"}

  D3 -->|"Sim"| C3(["CMP recomendada mesmo com<br/>anatomia desfavorável, se<br/>tecnicamente viável —<br/>Classe I, Nível C"])

  D3 -->|"Não"| D4{"Características desfavoráveis<br/>presentes — escore de Wilkins >8,<br/>Cormier grupo 3 (calcificação de<br/>qualquer extensão à fluoroscopia),<br/>insuficiência tricúspide grave,<br/>trombo em átrio esquerdo, ou<br/>insuficiência mitral mais que leve?"}

  D4 -->|"Nenhuma presente"| C4(["CMP recomendada —<br/>Classe I, Nível B"])

  D4 -->|"Anatomia subótima isolada<br/>(Wilkins >8 ou Cormier grupo 3),<br/>sem as demais contraindicações"| C5(["CMP deve ser considerada<br/>como tratamento inicial —<br/>Classe IIa, Nível C"])

  D4 -->|"Contraindicação formal presente<br/>— trombo em AE fora do apêndice,<br/>insuficiência mitral mais que leve,<br/>ou calcificação grave/bicomissural"| C6(["Cirurgia da valva mitral —<br/>Classe I, Nível C"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O escore de Wilkins, resumido

O nó D4 usa o escore de Wilkins como um dos critérios de anatomia desfavorável.
São quatro componentes avaliados por ecocardiograma — mobilidade do folheto,
espessamento do folheto, calcificação, e espessamento/calcificação do aparato
subvalvular —, cada um pontuado de 1 a 4, somando de 4 a 16. Escore ≤8 prediz
sucesso do tratamento percutâneo; a própria diretriz usa **escore >8** como um
dos critérios que definem anatomia desfavorável, junto com Cormier grupo 3 e
insuficiência tricúspide grave — não é o único critério, e por isso a árvore o
trata como parte de um conjunto no nó D4, não como pergunta isolada.

## Por que sintoma decide antes da anatomia

Repare que a árvore pergunta primeiro se o paciente é sintomático (D1), e só
depois avalia contraindicação cirúrgica (D3) e anatomia desfavorável (D4). Isso
espelha a própria estrutura da diretriz: em paciente sintomático sem
contraindicação a cirurgia, a anatomia é o que decide entre CMP e cirurgia; em
paciente sintomático **com** contraindicação ou alto risco cirúrgico, a CMP é
recomendada **mesmo com anatomia desfavorável**, porque a alternativa —
operar um paciente de alto risco — costuma ser pior do que aceitar um resultado
percutâneo subótimo.

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
