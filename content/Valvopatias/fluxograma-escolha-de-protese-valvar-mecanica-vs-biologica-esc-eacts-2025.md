---
title: "Fluxograma: Escolha de Prótese Valvar — Mecânica versus Biológica, por Idade e Comorbidade (ESC/EACTS 2025)"
slug: fluxograma-escolha-de-protese-valvar-mecanica-vs-biologica-esc-eacts-2025
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir do documento já publicado e revisado nesta pasta 'protese-valvar-escolha-mecanica-vs-biologica-e-alvo-de-inr-esc-eacts-2025.md', que reproduz a Recommendation Table 13 da diretriz ESC/EACTS 2025 (PMID 40878295). Corrigida em 26/08/2026 a mistura de duas recomendações distintas: já ter prótese mecânica em outra posição favorece nova prótese mecânica como Classe IIa/C, enquanto ter outra indicação clara de anticoagulação de longo prazo permite considerá-la como Classe IIb/C. Mantidas separadamente contraindicação/risco de sangramento, planejamento gestacional, preferência informada e cortes etários por posição; a zona intermediária (60-65 anos em posição aórtica, 65-70 em posição mitral) permanece como decisão individualizada, sem classe inventada. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Praz F, Borger MA, Lanz J, et al.; ESC/EACTS Scientific Document Group. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4747. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295 — Recommendation Table 13 (escolha de prótese) e Tabela 10 (alvo de INR), já reproduzidas no documento 'protese-valvar-escolha-mecanica-vs-biologica-e-alvo-de-inr-esc-eacts-2025.md' desta pasta; título/revista/ano reconferidos nesta sessão via PubMed E-utilities."]
---

# Fluxograma: Escolha de Prótese Valvar — Mecânica versus Biológica, por Idade e Comorbidade (ESC/EACTS 2025)

A escolha entre prótese mecânica e biológica não é uma equação só de idade. A
diretriz ESC/EACTS 2025 pondera, na ordem que este fluxograma reproduz: uso
prévio de anticoagulante por outro motivo, contraindicação à anticoagulação de
longo prazo, planejamento de gestação, e só então — na ausência de qualquer um
desses e sem preferência clara do paciente informado — o corte etário por
posição da valva. Tratar a decisão só pela idade cronológica é o erro mais
comum, e a própria diretriz coloca a preferência do paciente informado no mesmo
nível de recomendação (Classe I) que os cortes etários.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Indicação de troca valvar cirúrgica<br/>estabelecida — posição aórtica<br/>ou mitral"] --> D1{"Já existe prótese mecânica<br/>em outra posição?"}

  D1 -->|"Sim"| C1(["Prótese mecânica deve ser<br/>considerada — Classe IIa, Nível C"])

  D1 -->|"Não"| D1B{"Indicação clara de anticoagulação<br/>de longo prazo por outro motivo?"}

  D1B -->|"Sim"| C1B(["Prótese mecânica pode ser<br/>considerada — Classe IIb, Nível C"])

  D1B -->|"Não"| D2{"Contraindicação à anticoagulação<br/>de longo prazo, anticoagulação com<br/>AVK de qualidade improvável, alto<br/>risco de sangramento, ou expectativa<br/>de vida curta?"}

  D2 -->|"Sim"| C2(["Prótese biológica —<br/>Classe I, Nível C"])

  D2 -->|"Não"| D3{"Mulher que planeja engravidar?"}

  D3 -->|"Sim"| C3(["Prótese biológica deve ser<br/>considerada — Classe IIa, Nível C"])

  D3 -->|"Não"| D4{"Paciente informado tem<br/>preferência explícita, sem<br/>contraindicação à opção escolhida?"}

  D4 -->|"Deseja mecânica e aceita<br/>anticoagulação de longo prazo"| C4(["Prótese mecânica —<br/>Classe I, Nível C"])

  D4 -->|"Deseja biológica"| C5(["Prótese biológica —<br/>Classe I, Nível C"])

  D4 -->|"Sem preferência definida"| D5{"Idade e posição da prótese:<br/><60 anos em posição aórtica,<br/>ou <65 anos em posição mitral?"}

  D5 -->|"Sim"| C6(["Prótese mecânica deve ser<br/>considerada — Classe IIa, Nível C"])

  D5 -->|"Não"| D6{">65 anos em posição aórtica,<br/>ou >70 anos em posição mitral?"}

  D6 -->|"Sim"| C7(["Prótese biológica deve ser<br/>considerada — Classe IIa, Nível C"])

  D6 -->|"Não — faixa etária<br/>intermediária (60-65 anos aórtica,<br/>65-70 anos mitral)"| C8(["Decisão individualizada pelo<br/>Heart Team, ponderando expectativa<br/>de vida ajustada por comorbidade,<br/>sexo e etnia — a diretriz não fixa<br/>classe de recomendação nesta faixa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C1B,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Por que a preferência do paciente vem antes do corte etário

As duas recomendações de Classe I mais fortes da tabela não são cortes
numéricos — são "segundo o desejo do paciente informado", tanto para mecânica
quanto para biológica. O corte etário (nós D5/D6) só decide quando **não há**
contraindicação, planejamento gestacional, nem preferência clara já
manifestada. Isso inverte a ordem que a prática costuma seguir — decidir pela
idade e informar o paciente depois — e é deliberado: a diretriz reconhece que a
melhor prótese é a que o paciente aceita conviver, com anticoagulação de longo
prazo ou com o risco de reoperação futura.

## Por que existe uma faixa etária sem recomendação de classe

Entre 60 e 65 anos em posição aórtica (e entre 65 e 70 em posição mitral), a
diretriz simplesmente não atribui Classe I/IIa a nenhuma das duas próteses — a
tabela de recomendação salta do corte "<60/<65" para o corte ">65/>70". Nessa
faixa a decisão depende mais de expectativa de vida ajustada por comorbidade,
sexo e etnia (que costuma alterar a idade "biológica" efetiva) do que de um
número isolado, e por isso a árvore não inventa um corte que a fonte não dá —
registra a lacuna como decisão do Heart Team.

Já portar prótese mecânica em outra posição não é equivalente a apenas ter uma
indicação independente de anticoagulação crônica. A ESC/EACTS 2025 atribui
**IIa/C** ao primeiro cenário e **IIb/C** ao segundo; por isso eles aparecem em
nós separados, sem reduzir indevidamente a força da primeira recomendação.

## O que a árvore não mostra

- **O alvo de INR por tipo e posição da prótese mecânica não está aqui** — vale
  de 2 a 4 conforme a combinação de fator pró-trombótico adicional, tipo de
  prótese e posição, e está detalhado na Tabela 10 do documento
  `protese-valvar-escolha-mecanica-vs-biologica-e-alvo-de-inr-esc-eacts-2025.md`,
  nesta mesma pasta.
- **DOAC e dupla antiagregação são formalmente contraindicados** (Classe III,
  Nível A) para prevenir trombose em qualquer prótese mecânica, independente do
  ramo desta árvore que levou à escolha — não é uma alternativa ao AVK a ser
  considerada em nenhum ponto do fluxograma.
- **Esta árvore não cobre a troca de prótese já implantada** — reoperação por
  disfunção de bioprótese (estrutural ou não estrutural, com a classificação
  VARC-3) e o manejo perioperatório de anticoagulação em portador de prótese
  mecânica submetido a procedimento não cardíaco têm documentos próprios nesta
  pasta e em Perioperatório.
- **A decisão continua exigindo o Heart Team e a discussão explícita do risco de
  sangramento versus risco de reoperação** — a árvore organiza os critérios da
  diretriz, mas não substitui essa conversa.
