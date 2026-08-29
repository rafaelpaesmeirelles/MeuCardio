---
title: "Fluxograma: complicação mecânica pós-IAM — CIV versus ruptura papilar, IABP e timing da correção"
slug: fluxograma-complicacao-mecanica-pos-iam-civ-e-ruptura-papilar
theme: "Doença coronariana"
kind: fluxograma
summary: "Árvore à beira do leito da deterioração pós-infarto: eco imediato, separação entre choque de bomba, CIV, ruptura papilar e tamponamento, IABP como ponte na complicação mecânica, e Heart Team entre cirurgia de emergência, adiamento selecionado e fechamento percutâneo."
review_status: pendente_revisao
source_refs:
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654."
  - "Damluji AA, van Diepen S, Katz JN, et al. Mechanical Complications of Acute Myocardial Infarction: A Scientific Statement From the American Heart Association. Circulation. 2021;144(2):e16-e35. DOI: 10.1161/CIR.0000000000000985. PMID: 34126755."
  - "Schlotter F, Huber K, Hassager C, et al. Ventricular septal defect complicating acute myocardial infarction: diagnosis and management. Eur Heart J. 2024;45(28):2478-2492. DOI: 10.1093/eurheartj/ehae363. PMID: 38888906."
  - "Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes. J Am Coll Cardiol. 2025;85(22):2135-2237. DOI: 10.1016/j.jacc.2024.11.009. PMID: 40013746."
  - "Møller JE, Engstrøm T, Jensen LO, et al. Microaxial Flow Pump or Standard Care in Infarct-Related Cardiogenic Shock. N Engl J Med. 2024;390(15):1382-1393. DOI: 10.1056/NEJMoa2312572. PMID: 38587239."
review_note: "Produção científica original (Grok) em 29/08/2026. Fluxograma decisório do cardiologista, complementar ao protocolo `comunicacao-interventricular-pos-infarto-diagnostico-e-decisao` e ao catálogo de UCO `complicacoes-mecanicas-pos-infarto-na-uco-ruptura-septo-papilar-parede-livre`. Classes ESC 2023 (I C reparo emergencial; IIa C IABP na complicação mecânica; III B IABP rotineiro no choque sem ruptura) conferidas no PDF da diretriz. DanGer-Shock citado só como exclusão de VSR. COR/LOE numéricos da ACC/AHA 2025 não transcritos. Publicação condicionada a revisão humana."
---

# Fluxograma: complicação mecânica pós-IAM (CIV e ruptura papilar)

A deterioração súbita após infarto não é “choque de bomba” até o eco dizer o contrário. Este fluxograma cobre o caminho do cardiologista: **eco agora**, separação dos quatro mecanismos (bomba, CIV, papilar, parede livre), **IABP como ponte se a ruptura estiver confirmada**, e Heart Team entre cirurgia de emergência, adiamento selecionado e percutâneo. O texto de suporte está em `comunicacao-interventricular-pos-infarto-diagnostico-e-decisao`. O catálogo de UCO das três rupturas está em `complicacoes-mecanicas-pos-infarto-na-uco-ruptura-septo-papilar-parede-livre`.

Não usar este fluxo para CIV congênita do adulto.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Deterioração após IAM:<br/>choque novo, edema pulmonar súbito,<br/>sopro novo, dor recorrente,<br/>PEA ou necessidade crescente de vasopressor"]
  D0{"ECG: reoclusão ou reinfarto<br/>com indicação de sala agora?"}
  C0(["Tratar a artéria culpada em paralelo<br/>Não atrasar o eco por causa da sala"])
  P1["Eco transtorácico com Doppler colorido<br/>à beira do leito, imediato<br/>Inclui POCUS se o clínico for treinado"]
  D1{"Derrame pericárdico com tamponamento<br/>ou coágulo, ou PEA pós-IAM?"}
  C1(["Ruptura de parede livre até prova em contrário<br/>Emergência cirúrgica<br/>Não drenar o pericárdio de forma ampla<br/>se a cirurgia está disponível"])
  D2{"Jato transseptal E→D<br/>ou salto oximétrico AD→VD/AP?"}
  C2(["CIV pós-IAM"] )
  D3{"Flail mitral, cabeça papilar no AE<br/>ou IM aguda grave com VE hiperdinâmico?"}
  C3(["Ruptura de músculo papilar"] )
  C4(["Choque de bomba ou outra causa<br/>Ver CULPRIT-SHOCK / IABP-SHOCK II / DanGer-Shock<br/>IABP de rotina: Classe III"])
  D4{"Hospital com cirurgia cardíaca<br/>disponível agora?"}
  C5(["Transferir já, com suporte em trânsito<br/>ACC/AHA 2025: centro com expertise cirúrgica"])
  D5{"Instabilidade: choque, hipoperfusão,<br/>falência de órgão, edema refratário?"}
  P2["IABP agora como ponte<br/>ESC 2023 Classe IIa C<br/>Reduz pós-carga e shunt/IM<br/>Não fecha o defeito"]
  D6{"A ponte sustenta perfusão<br/>e a falência de órgão reverte?"}
  C6(["Heart Team agora:<br/>reparo cirúrgico ou por cateter de emergência<br/>ESC 2023 Classe I C"])
  D7{"CIV com anatomia favorável a oclusor<br/>E risco cirúrgico proibitivo?"}
  C7(["Fechamento percutâneo selecionado<br/>Não é substituto rotineiro da cirurgia"])
  C8(["Cirurgia de emergência:<br/>CIV → correção do septo ± revascularização<br/>Papilar → troca mitral; reparo só se parcial e favorável"])
  D8{"CIV estável com IABP/MCS,<br/>sem falência de órgão em curso?"}
  C9(["Adiamento de 1 a 2 semanas<br/>PODE ser considerado<br/>Não é regra universal"])
  C10(["Cirurgia urgente após Heart Team<br/>enquanto a ponte estiver de pé"])
  D9{"Suspeita de complicação mecânica<br/>em STEMI com choque, fora de centro de ICP,<br/>antes de fibrinólise?"}
  C11(["Não lisar até o eco excluir ruptura<br/>ESC 2023: lise no choque só se<br/>complicação mecânica afastada"])

  R0 --> D0
  D0 -->|"Sim"| C0
  C0 --> P1
  D0 -->|"Não"| P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| C4
  C2 --> D9
  C3 --> D9
  D9 -->|"Ainda não lisou e há sopro/tamponamento"| C11
  D9 -->|"Já reperfundido ou lise não está em pauta"| D4
  C11 --> D4
  D4 -->|"Não"| C5
  D4 -->|"Sim"| D5
  C5 --> D5
  D5 -->|"Sim: instável"| P2
  D5 -->|"Não: estável"| D8
  P2 --> D6
  D6 -->|"Não: refratário"| C6
  D6 -->|"Sim: ponte sustenta"| D8
  C6 --> D7
  D7 -->|"Sim"| C7
  D7 -->|"Não"| C8
  D8 -->|"Sim, CIV estável"| C9
  D8 -->|"Não: papilar, ou CIV que só se segura com MCS"| C10

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#a33b2b,color:#4a1410;
  class C0,C4,C7,C9,C10 conduta;
  class C1,C5,C6,C8,C11 alerta;
```

## Como usar os nós (sem reler o protocolo inteiro)

**Eco antes de batizar o choque.** A ESC 2023 manda eco imediato na suspeita de complicação mecânica. A ACC/AHA 2025 usa “is indicated” para eco urgente, inclusive POCUS, em choque, instabilidade ou suspeita de ruptura. Sopro ausente não encerra a árvore.

**Quatro saídas, não duas.** Bomba, CIV, papilar e parede livre. CIV e papilar compartilham sopro e choque “desproporcional” ao VE; o Doppler separa. Parede livre é tamponamento/PEA e sai deste fluxo para a sala de cirurgia, sem IABP como tratamento.

**IABP só no ramo mecânico instável.** Classe IIa C na ESC 2023 para instabilidade por complicação mecânica. Classe III B para uso rotineiro no choque **sem** ruptura. DanGer-Shock **excluiu** CIV, ruptura papilar e parede livre: não puxa Impella de rotina neste fluxo.

**Cirurgia de emergência é Classe I C** na instabilidade, por Heart Team, cirúrgica ou por cateter. Percutâneo é ramo de risco proibitivo e anatomia favorável, não atalho.

**Adiar 1 a 2 semanas** só existe no nó da CIV que **sustenta** a ponte. O consenso Schlotter 2024 admite esse adiamento; a AHA 2021 chama de decisão compartilhada. Paciente que desaba na ponte volta ao ramo de emergência. Ruptura papilar completa não entra nesse adiamento: a AHA trata troca mitral de emergência como padrão.

**Fibrinólise.** No STEMI com choque, a ESC 2023 só considera lise se ICP primária não for viável em 120 min **e** a complicação mecânica tiver sido afastada (Classe IIa C). Sopro novo, tamponamento ou eco ainda não feito: não lisar.

**Transferência.** ACC/AHA 2025: complicação mecânica em centro com cirurgia cardíaca. IABP no hospital sem cirurgião é ponte de transferência, não tratamento definitivo.

## O que este fluxograma não cobre

- CIV congênita do adulto (outros dois documentos desta biblioteca).
- Dose de nitroprussiato, noradrenalina ou parâmetros de IABP — protocolo institucional.
- Técnica cirúrgica do remendo, escolha do oclusor ou edge-to-edge transcateter passo a passo.
- Estadiamento SCAI: grada gravidade, não identifica o buraco.

## Conexões

- `comunicacao-interventricular-pos-infarto-diagnostico-e-decisao` — texto deste fluxo.
- `complicacoes-mecanicas-pos-infarto-na-uco-ruptura-septo-papilar-parede-livre` — catálogo de UCO.
- `choque-cardiogenico-na-sindrome-coronariana-aguda-culprit-shock-e-iabp-shock-ii` — ramo “choque de bomba”.
- `danger-shock-impella-choque-cardiogenico-stemi` — MCS no STEMI sem ruptura.
- `fluxograma-iamcsst-estrategia-de-reperfusao-icp-primaria-vs-fibrinolise-esc-2023` — reperfusão; este fluxo entra quando o paciente desaba depois (ou no meio) dela.
