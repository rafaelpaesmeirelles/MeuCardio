---
title: "Fluxograma: Endocardite infecciosa — da suspeita à indicação cirúrgica (ESC 2023)"
slug: fluxograma-endocardite-infecciosa-esc-2023
theme: "Endocardite"
kind: fluxograma
summary: "Caminho decisório da endocardite infecciosa suspeita: hemoculturas e ecocardiograma como primeira linha, o papel da TC cardíaca e do PET/CT com 18F-FDG quando a ecocardiografia é inconclusiva, e as três indicações cirúrgicas com seus prazos (emergência, urgência)."
review_status: revisado
source_refs: ["2023 ESC Guidelines for the management of endocarditis · European Heart Journal · 2023 · 44(39):3948-4042 · https://academic.oup.com/eurheartj/article/44/39/3948/7243107", "2023 ESC Guidelines for Management of Endocarditis: Key Points · American College of Cardiology · 2023 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2023/08/29/20/49/2023-esc-guidelines-for-endocarditis-esc-2023", "2023 Duke-International Society for Cardiovascular Infectious Diseases Criteria for Infective Endocarditis: Updating the Modified Duke Criteria · Clinical Infectious Diseases · 2023 · 77(4):518-526 · https://academic.oup.com/cid/article/77/4/518/7151107"]
---

# Fluxograma: Endocardite infecciosa (ESC 2023)

A diretriz ESC 2023 reorganizou o diagnóstico em torno de três pilares que
caminham juntos desde a primeira hora — **quadro clínico, hemoculturas e
imagem** — e ampliou a imagem para além da ecocardiografia. A mudança prática
mais importante é que o ecocardiograma transesofágico deixou de ser exame de
resgate: passou a ser recomendação Classe I mesmo quando o transtorácico já é
positivo, com uma única exceção.

## Caminho diagnóstico

```mermaid
flowchart TD
  R0["Suspeita clínica de<br/>endocardite infecciosa"] --> P1["Hemoculturas antes do antibiótico<br/>e ecocardiograma transtorácico"]

  P1 --> D1{"Endocardite de valva nativa direita<br/>isolada, com ETT de boa qualidade<br/>e achado inequívoco?"}

  D1 -->|Sim| C1(["ETE dispensável — classificar<br/>pelos critérios da ESC 2023"])

  D1 -->|Não| P2["Ecocardiograma transesofágico<br/>Classe I mesmo com ETT positivo"]

  P2 --> D2{"Achado ecocardiográfico<br/>conclusivo?"}

  D2 -->|Sim| D3{"Classificação pelos<br/>critérios da ESC 2023"}

  D3 -->|Definida| C2(["Tratar como endocardite, encaminhar ao<br/>Time de Endocardite e solicitar imagem<br/>cerebral e de corpo inteiro se<br/>houver sintomas"])
  D3 -->|Possível| C3(["Manter investigação e repetir o ETE em<br/>5 a 7 dias se a suspeita clínica<br/>permanecer alta, reclassificando depois"])
  D3 -->|Rejeitada| C4(["Buscar diagnóstico alternativo"])

  D2 -->|"Não — valva nativa"| C5(["Angio-TC cardíaca e, com o resultado,<br/>classificar pelos critérios da ESC 2023"])

  D2 -->|"Não — valva protética"| C6(["Angio-TC cardíaca e PET/TC com 18F-FDG;<br/>se o PET não estiver disponível, SPECT/TC<br/>com leucócitos marcados deve ser<br/>considerado. Classificar em seguida"])

  D2 -->|"Não — dispositivo<br/>cardíaco implantável"| C7(["PET/TC com 18F-FDG pode ser considerado;<br/>se indisponível, SPECT/TC com leucócitos<br/>marcados. Classificar em seguida"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Onde tratar

A diretriz separa o destino do paciente pela complexidade do quadro:

- **endocardite não complicada** — pode ser conduzida no centro de origem,
  com comunicação regular com um Heart Valve Center;
- **endocardite complicada** — deve ser tratada em Heart Valve Center que
  disponha de Time de Endocardite e de estrutura para cirurgia imediata.

O Time de Endocardite reúne cardiologista, especialista em imagem, cirurgião
cardiovascular, infectologista, microbiologista e o responsável pelo regime
antibiótico parenteral ambulatorial.

## Indicação e prazo da cirurgia

São três as famílias de indicação — insuficiência cardíaca, infecção não
controlada e prevenção de embolia. O que muda entre elas é o prazo.

```mermaid
flowchart TD
  R0["Endocardite confirmada"] --> D1{"Regurgitação, obstrução ou fístula<br/>com edema agudo de pulmão refratário<br/>ou choque cardiogênico?"}

  D1 -->|Sim| C1(["Cirurgia de emergência<br/>em até 24 horas"])

  D1 -->|Não| D2{"Insuficiência cardíaca<br/>sem refratariedade?"}

  D2 -->|Sim| C2(["Cirurgia de urgência<br/>em 3 a 5 dias"])

  D2 -->|Não| D3{"Infecção localmente não controlada?<br/>abscesso, falso aneurisma, fístula,<br/>vegetação crescente, bloqueio AV novo"}

  D3 -->|Sim| C3(["Cirurgia de urgência<br/>em 3 a 5 dias"])

  D3 -->|Não| D4{"Vegetação persistente maior ou igual<br/>a 10 mm após ao menos um episódio<br/>embólico, ou maior ou igual a 10 mm com<br/>outra indicação cirúrgica?"}

  D4 -->|Sim| C4(["Cirurgia de urgência<br/>em 3 a 5 dias"])

  D4 -->|Não| D5{"Endocardite fúngica ou por<br/>germe multirresistente?"}

  D5 -->|Sim| C5(["Cirurgia urgente ou eletiva<br/>conforme a hemodinâmica"])
  D5 -->|Não| C6(["Tratamento clínico<br/>com vigilância ativa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Situações que têm regra própria

- **Endocardite precoce de prótese** (nos primeiros 6 meses): desbridamento
  completo e troca valvar.
- **Endocardite relacionada a dispositivo cardíaco implantável**: extração
  completa do sistema, sem adiamento, já durante a antibioticoterapia
  empírica inicial.
- **Endocardite de câmaras direitas**: cirurgia na regurgitação tricúspide
  aguda grave com disfunção de ventrículo direito, embolia pulmonar
  recorrente ou vegetação residual maior que 20 mm. Nesse cenário, o reparo
  da valva tricúspide deve ser considerado em vez da troca.
- **Complicação neurológica**: após ataque isquêmico transitório ou acidente
  vascular cerebral não hemorrágico, a cirurgia não deve ser adiada quando há
  insuficiência cardíaca, infecção não controlada ou abscesso. Depois de
  acidente vascular hemorrágico, o adiamento por pelo menos 4 semanas é a
  conduta usual.

## Antibioticoterapia: o desenho em duas fases

A ESC 2023 consolidou o tratamento em duas fases — cerca de 2 semanas
iniciais de terapia parenteral hospitalar, seguidas de até 6 semanas de
tratamento oral ou parenteral ambulatorial em pacientes selecionados. A
duração total é de 2 a 6 semanas na valva nativa e de pelo menos 6 semanas na
prótese valvar.

A troca para via oral só é feita depois que o ecocardiograma transesofágico
documenta ausência de progressão local e de complicações — é por isso que o
ETE também é recomendação Classe I antes da transição de via.

Outros pontos do regime: aminoglicosídeo não é recomendado na endocardite
estafilocócica de valva nativa; rifampicina entra apenas quando há material
protético envolvido; e a daptomicina, quando usada, é em dose alta —
10 mg/kg uma vez ao dia.

## Critérios diagnósticos: o que mudou

Os critérios de Duke foram atualizados em 2023 em duas versões próximas — a
Duke-ISCVID, publicada em *Clinical Infectious Diseases*, e a versão da
própria ESC, incorporada a esta diretriz. As duas ampliaram a lista de
microrganismos considerados típicos, incorporaram TC cardíaca e PET/TC com
18F-FDG aos critérios de imagem e acrescentaram a presença de dispositivo
cardíaco implantável como critério menor de predisposição. A Duke-ISCVID
também elevou a inspeção intraoperatória a critério clínico maior.

O ganho é de sensibilidade: a versão de 2023 alcançou 84% de sensibilidade
clínica contra 70% da versão anterior. Os critérios da ESC 2023 tiveram
sensibilidade de 82,7% e especificidade de 92,3%, contra 84,2% e 93,9% da
Duke-ISCVID na mesma coorte.

## Profilaxia antibiótica

A profilaxia é recomendada para pacientes de alto risco submetidos a
procedimentos odontológicos. Deve ser considerada em quem tem reparo
transcateter prévio de valva mitral ou tricúspide, e pode ser considerada em
transplantados cardíacos e em pacientes de alto risco submetidos a
procedimentos invasivos. Não há indicação de profilaxia antes de
procedimento odontológico com o objetivo de prevenir endocardite associada a
dispositivo cardíaco implantável.
