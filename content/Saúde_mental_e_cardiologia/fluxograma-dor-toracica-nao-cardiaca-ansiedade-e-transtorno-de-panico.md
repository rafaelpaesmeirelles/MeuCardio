---
title: "Fluxograma: Dor Torácica Não Cardíaca com Ansiedade — Suspeita de Transtorno de Pânico e Encaminhamento"
slug: fluxograma-dor-toracica-nao-cardiaca-ansiedade-e-transtorno-de-panico
theme: "Saúde mental e cardiologia"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Fleet RP, Dupuis G, Marchand A, Burelle D, Arsenault A, Beitman BD. Panic disorder in emergency department chest pain patients: prevalence, comorbidity, suicidal ideation, and physician recognition. Am J Med. 1996;101(4):371-380. DOI: 10.1016/S0002-9343(96)00224-0. PMID: 8873507."
  - "Huffman JC, Pollack MH. Predicting panic disorder among patients with chest pain: an analysis of the literature. Psychosomatics. 2003;44(3):222-236. DOI: 10.1176/appi.psy.44.3.222. PMID: 12724504."
  - "Thesen T, Himle JA, Martinsen EW, Walseth LT, Thorup F, Gallefoss F, Jonsbu E. Effectiveness of Internet-Based Cognitive Behavioral Therapy With Telephone Support for Noncardiac Chest Pain: Randomized Controlled Trial. J Med Internet Res. 2022;24(1):e33631. DOI: 10.2196/33631. PMID: 35072641."
  - "Derivado de transtorno-de-panico-como-diagnostico-diferencial-de-dor-toracica-cardiaca.md e terapia-cognitivo-comportamental-para-ansiedade-cardiaca-e-dor-toracica-nao-cardiaca.md, já publicados no acervo (Saúde mental e cardiologia)."
---

# Fluxograma: Dor Torácica Não Cardíaca com Ansiedade — Suspeita de Transtorno de Pânico e Encaminhamento

Cerca de 25% de quem procura o pronto-socorro com dor torácica tem transtorno de pânico — e, no estudo que mediu isso, **98% desses casos passaram despercebidos** pelos próprios cardiologistas plantonistas. Este fluxograma parte de onde o documento de diagnóstico diferencial já publicado nesta pasta termina — a suspeita do transtorno — e segue até a decisão de encaminhamento para intervenção estruturada da ansiedade cardíaca, juntando os dois documentos já existentes sobre o tema (diagnóstico diferencial e tratamento por terapia cognitivo-comportamental).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com dor torácica avaliado no pronto-socorro<br/>ou consultório, com causa cardíaca aguda já<br/>razoavelmente excluída"] --> D1{"Dor torácica atípica ou não anginosa, em paciente<br/>mais jovem, do sexo feminino, sem doença coronariana<br/>conhecida, e com ansiedade autorreferida elevada?<br/>(variáveis associadas a maior prevalência de<br/>transtorno de pânico — Huffman e Pollack, 2003)"}

  D1 -->|"Não"| C1(["Manter avaliação e conduta padrão da causa não<br/>cardíaca identificada; risco de transtorno de<br/>pânico não especificamente sinalizado por<br/>estas variáveis"])

  D1 -->|"Sim"| P1["Considerar ativamente transtorno de pânico no<br/>diagnóstico diferencial — não descartado por<br/>história de doença coronariana prévia: 44% dos<br/>pacientes com transtorno de pânico no estudo de<br/>Fleet et al. (1996) também tinham doença<br/>arterial coronariana"]
  P1 --> D2{"Avaliação clínica direcionada confirma<br/>critérios para transtorno de pânico?"}
  D2 -->|"Não"| C2(["Diagnóstico de transtorno de pânico não<br/>confirmado nesta avaliação; prosseguir a<br/>investigação da causa da dor torácica<br/>não cardíaca por outra via"])
  D2 -->|"Sim"| P2["Perguntar ativamente sobre ideação suicida —<br/>25% dos pacientes com transtorno de pânico<br/>relatam ideação suicida na semana anterior à<br/>consulta, contra 5% de quem não tem o<br/>transtorno (Fleet et al., 1996; p=0,0001)"]
  P2 --> D3{"Ideação suicida presente?"}
  D3 -->|"Sim"| C3(["Encaminhamento psiquiátrico urgente para<br/>avaliação de risco de suicídio"])
  D3 -->|"Não"| D4{"Dor torácica recorrente e/ou ansiedade cardíaca<br/>persistem após o diagnóstico e a orientação<br/>inicial, já excluída a causa aguda?"}
  D4 -->|"Não, resolveu com orientação/esclarecimento"| C4(["Manter seguimento clínico habitual; reforçar<br/>ao paciente que a causa cardíaca aguda<br/>foi excluída"])
  D4 -->|"Sim, sintomas persistem"| C5(["Encaminhar para intervenção psicoeducacional<br/>ou cognitivo-comportamental estruturada dirigida<br/>à ansiedade cardíaca — evidência heterogênea<br/>entre ensaios quanto ao desfecho psicométrico<br/>principal, mas com sinal favorável em frequência<br/>de dor torácica, qualidade de vida e/ou<br/>utilização de serviço de saúde em vários deles"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**A presença de doença coronariana não descarta transtorno de pânico**, e o inverso também não é verdade — as duas condições coexistem em quase metade dos casos do estudo de Fleet et al. A suspeita de transtorno de pânico orienta investigação psiquiátrica em paralelo, nunca substitui avaliação cardíaca quando ela é clinicamente indicada.

**O comparador importa tanto quanto a intervenção** no encaminhamento para terapia estruturada: contra cuidado habitual sem estrutura, a terapia cognitivo-comportamental pela internet reduziu ansiedade cardíaca com significância; contra psicoeducação já estruturada, não mostrou superioridade no desfecho psicométrico principal, ainda que tenha favorecido frequência de dor e qualidade de vida no seguimento mais longo. Isso não é razão para deixar de encaminhar — é razão para não prometer resposta garantida no instrumento de ansiedade especificamente.

**Nenhum dos ensaios de terapia cognitivo-comportamental aqui usados testou pacientes com angina por isquemia documentada** — a população de referência é dor torácica já classificada como não cardíaca, ou ansiedade de saúde/dor torácica recorrente sem achado físico.
