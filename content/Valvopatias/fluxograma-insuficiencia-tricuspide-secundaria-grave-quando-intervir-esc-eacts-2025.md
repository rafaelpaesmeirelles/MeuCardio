---
title: "Fluxograma: Insuficiência Tricúspide Secundária Grave — Quando Intervir (ESC/EACTS 2025 e TRILUMINATE Pivotal)"
slug: fluxograma-insuficiencia-tricuspide-secundaria-grave-quando-intervir-esc-eacts-2025
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir do documento já publicado e revisado nesta pasta 'insuficiencia-tricuspide-grave-triluminate-e-reparo-transcateter-borda-a-borda.md', da Recommendation Table 9 da ESC/EACTS 2025 e do TRILUMINATE Pivotal (PMID 36876753). Corrigida em 26/08/2026 a omissão da cirurgia tricúspide isolada: em paciente sintomático com IT secundária grave, operável e sem disfunção grave de VD/VE ou hipertensão pulmonar impeditiva, cirurgia deve ser considerada (IIa/B), mesmo sem outra cirurgia cardíaca concomitante. Tratamento transcateter (IIa/A) permanece para alto risco cirúrgico e anatomia apropriada; T-TEER é uma modalidade, não sinônimo de toda intervenção transcateter. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Sorajja P, Whisenant B, Hamid N, et al. Transcatheter Repair for Patients with Tricuspid Regurgitation. N Engl J Med. 2023;388(20):1833-1842. DOI: 10.1056/NEJMoa2300525. PMID: 36876753 — já citada e verificada em 'insuficiencia-tricuspide-grave-triluminate-e-reparo-transcateter-borda-a-borda.md' desta pasta; título/revista/ano reconferidos nesta sessão via PubMed E-utilities.", "Praz F, Borger MA, Lanz J, et al.; ESC/EACTS Scientific Document Group. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4747. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295 — Recommendation Table 9, texto integral já conferido em 30/07/2026 por sessão anterior; título/revista/ano reconferidos nesta sessão via PubMed E-utilities."]
---

# Fluxograma: Insuficiência Tricúspide Secundária Grave — Quando Intervir (ESC/EACTS 2025 e TRILUMINATE Pivotal)

Por décadas a insuficiência tricúspide (IT) grave isolada foi tratada quase só
com diurético — a cirurgia isolada de valva tricúspide tem mortalidade
operatória elevada em paciente já com disfunção de ventrículo direito, e a
maioria nunca chegava a ser operada. O reparo transcateter borda a borda mudou
esse cenário a partir de 2023, mas nem todo paciente com IT grave sintomática é
candidato — a seleção correta, mais do que a gravidade da regurgitação, é o que
determina se o procedimento vale a pena. Este fluxograma organiza essa seleção
para a IT **secundária** (dilatação do anel/ventrículo direito, em geral por
hipertensão pulmonar, fibrilação atrial ou doença do coração esquerdo).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Insuficiência tricúspide secundária<br/>grave, confirmada por ecocardiograma"] --> D1{"Sintomática apesar de terapia<br/>clínica otimizada — diurético e<br/>tratamento da causa: controle de<br/>ritmo da fibrilação atrial,<br/>tratamento da insuficiência cardíaca<br/>esquerda, manejo da hipertensão<br/>pulmonar?"}

  D1 -->|"Não"| C1(["Manter tratamento clínico<br/>otimizado e reavaliar<br/>periodicamente"])

  D1 -->|"Sim"| D2{"Disfunção grave de ventrículo<br/>direito, ou disfunção grave de<br/>ventrículo esquerdo, ou hipertensão<br/>pulmonar pré-capilar?"}

  D2 -->|"Sim"| C2(["Tratamento clínico otimizado<br/>preferido — risco de futilidade<br/>do procedimento; considerar<br/>manejo avançado de insuficiência<br/>cardíaca"])

  D2 -->|"Não"| D3{"Risco cirúrgico aceitável e<br/>indicação concomitante de cirurgia<br/>cardíaca — por exemplo, cirurgia<br/>de valva mitral?"}

  D3 -->|"Sim"| C3(["Cirurgia da valva tricúspide,<br/>concomitante à cirurgia<br/>já indicada"])

  D3 -->|"Não"| D3B{"Cirurgia tricúspide isolada:<br/>paciente operável, com risco aceitável<br/>após avaliação pelo Heart Team?"}

  D3B -->|"Sim"| C3B(["Cirurgia tricúspide isolada deve ser<br/>considerada — Classe IIa, Nível B;<br/>preferir reparo quando tecnicamente viável"])

  D3B -->|"Não — alto risco cirúrgico"| D4{"Anatomia adequada a tratamento<br/>transcateter selecionado pelo Heart Team,<br/>em Centro de Válvula Cardíaca<br/>experiente?"}

  D4 -->|"Sim"| C4(["Tratamento transcateter da valva<br/>tricúspide — T-TEER quando a anatomia<br/>é adequada — para melhorar qualidade<br/>de vida e promover remodelamento de VD:<br/>Classe IIa, Nível A"])

  D4 -->|"Não"| C5(["Tratamento clínico otimizado<br/>e reavaliação — sem opção<br/>segura de intervenção<br/>no momento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C3B,C4,C5 conduta;
```

## O que o TRILUMINATE Pivotal realmente mostrou

O ensaio que sustenta a Classe IIa/A do nó C4 (350 pacientes, TriClip mais
terapia clínica versus terapia clínica isolada) teve desfecho primário positivo
por *win ratio* (1,48; IC95% 1,06-2,13; p=0,02) — mas o componente que carregou
esse resultado foi **qualidade de vida**, não desfecho duro: morte por qualquer
causa ou cirurgia da valva tricúspide (9,4% vs. 10,6%) e hospitalização por
insuficiência cardíaca (0,21 vs. 0,17 evento por paciente-ano) foram
praticamente iguais entre os grupos. A melhora de qualidade de vida pelo KCCQ
foi grande e consistente (+11,7 pontos de diferença, p<0,001). Dizer ao
paciente que o procedimento "melhora sintomas e qualidade de vida" é o que o
ensaio sustenta; dizer que "reduz mortalidade ou internação" não é.

## Por que a disfunção grave de VD interrompe o caminho

O nó D2 não é uma checagem de segurança genérica — é a qualificação explícita
que a própria diretriz coloca ao lado da recomendação Classe IIa: em disfunção
grave de ventrículo direito, disfunção grave de ventrículo esquerdo, ou
hipertensão pulmonar pré-capilar, tratar a válvula tende a não mudar o curso da
doença, porque o problema principal não é mais a regurgitação — é a falência
que ela deixou para trás. Intervir nesse cenário arrisca o procedimento sem
benefício real, e a diretriz é explícita em preferir manejo clínico.

## Por que a cirurgia isolada não pode desaparecer da árvore

Ausência de outra cirurgia cardíaca indicada não equivale a inoperabilidade.
Na IT secundária grave, a ESC/EACTS 2025 orienta considerar cirurgia isolada no
paciente sintomático e operável, antes que disfunção avançada de VD/VE ou
hipertensão pulmonar tornem a intervenção fútil. A mortalidade historicamente
alta da cirurgia tricúspide isolada reflete em parte encaminhamento tardio; ela
não justifica desviar automaticamente todo paciente para tratamento
transcateter.

## O que a árvore não mostra

- **IT primária segue algoritmo diferente**, não coberto aqui — endocardite de
  valva tricúspide, lesão de folheto por cabo de marca-passo/CDI e doença
  carcinoide têm mecanismo e conduta próprios, tratados em documentos dedicados
  desta pasta.
- **Estenose tricúspide reumática** é outra doença, com conduta distinta
  (documentada em `estenose-tricuspide-reumatica-diagnostico-e-manejo.md`,
  nesta pasta) — não confundir com a insuficiência secundária desta árvore.
- **Substituição valvar tricúspide transcateter e anuloplastia transcateter**
  são opções além do reparo borda a borda, com corpo de evidência próprio
  (sistema Evoque, estudado no TRISCEND II), ainda não incorporadas nesta
  árvore.
- **A árvore não substitui a avaliação do Heart Team.** Anatomia do anel,
  tamanho e mobilidade dos folhetos, e a relação entre gravidade da IT e o
  grau de remodelamento do VD são avaliados caso a caso antes de qualquer
  intervenção.
