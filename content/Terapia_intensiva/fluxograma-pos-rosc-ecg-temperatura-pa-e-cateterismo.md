---
title: "Fluxograma: pós-ROSC nas primeiras 24 horas — ECG, temperatura, pressão e cateterismo"
slug: fluxograma-pos-rosc-ecg-temperatura-pa-e-cateterismo
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore do cardiologista nas primeiras 24 horas após RCE: ECG de 12 derivações; supra versus não; cateterismo imediato só no supra ou no alto risco em curso com etiologia cardíaca; em paralelo, evitar febre (não induzir 33 °C por rotina), piso de PAM e de oxigenação, eco para causa mecânica, antitrombótico só se indicado, e não prognosticar o cérebro neste intervalo."
review_status: revisado
fonte_producao: grok
review_note: "Árvore original das primeiras 24 h do cardiologista. Não clona o fluxograma-cuidado-pos-parada-e-coronariografia (só cateterismo) nem o protocolo AHA 2025 de cuidados na UCO. Nós de cateterismo apontam para o fluxograma canônico quando o ramo exige detalhe. Números só dos abstracts TTM2/COACT/TOMAHAWK/BOX lidos via PubMed E-utilities nesta revisão editorial. COR/LOE AHA 2025 e ESC 2023 Table 8: LIMITE DA EVIDÊNCIA DISPONÍVEL — tabelas não abertas."
source_refs:
  - "Dankiewicz J, Cronberg T, Lilja G, et al. Hypothermia versus normothermia after out-of-hospital cardiac arrest (TTM2). N Engl J Med. 2021;384(24):2283-2294. DOI: 10.1056/NEJMoa2100591. PMID: 34133859"
  - "Lemkes JS, Janssens GN, van der Hoeven NW, et al. Coronary Angiography after Cardiac Arrest without ST-Segment Elevation. N Engl J Med. 2019;380(15):1397-1407. DOI: 10.1056/NEJMoa1816897. PMID: 30883057"
  - "Desch S, Freund A, Akin I, et al. Angiography after Out-of-Hospital Cardiac Arrest without ST-Segment Elevation. N Engl J Med. 2021;385(27):2544-2553. DOI: 10.1056/NEJMoa2101909. PMID: 34459570"
  - "Kjaergaard J, Møller JE, Schmidt H, et al. Blood-Pressure Targets in Comatose Survivors of Cardiac Arrest. N Engl J Med. 2022;387(16):1456-1466. DOI: 10.1056/NEJMoa2208687. PMID: 36027564"
  - "Schmidt H, Kjaergaard J, Hassager C, et al. Oxygen Targets in Comatose Survivors of Cardiac Arrest. N Engl J Med. 2022;387(16):1467-1476. DOI: 10.1056/NEJMoa2208686. PMID: 36027567"
  - "Hirsch KG, Amorim E, Coppler PJ, et al. Part 11: Post-Cardiac Arrest Care: 2025 American Heart Association Guidelines. Circulation. 2025;152(16_suppl_2):S673-S718. DOI: 10.1161/CIR.0000000000001375. PMID: 41122894. Tabelas de COR/LOE não abertas nesta revisão editorial."
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654. Table 8 não reaberta."
---

# Fluxograma: pós-ROSC nas primeiras 24 horas — ECG, temperatura, pressão e cateterismo

A pergunta desta árvore não é “o paciente vai acordar?”. É: **nas próximas 24 horas, o cardiologista já decidiu ECG, cateterismo, temperatura, PAM/oxigênio, eco e antitrombótico — e já recusou prognosticar o cérebro?**

O playbook em prosa está em `pos-rosc-primeiras-24-horas-o-que-o-cardiologista-decide.md`. O ramo isolado de coronariografia, com a nuance AHA 2025 de alto risco sem supra, está em `fluxograma-cuidado-pos-parada-e-coronariografia.md` — esta árvore não o substitui.

Temperatura, PAM e oxigênio **não ramificam o cateterismo**: correm em paralelo nos dois lados do ECG. Entraram no diagrama de propósito, porque o erro clássico é tratar o pós-RCE como uma única decisão (ir ou não à hemodinâmica).

## Árvore de decisão

```mermaid
flowchart TD
  R0["RCE confirmado<br/>adulto, primeiras 24 horas"]
  P1["ECG de 12 derivações agora<br/>sem esperar o leito da UCO"]
  D1{"Supra de ST persistente<br/>ou equivalente de oclusão?"}

  C_stemi(["IAMCST: coronariografia emergente.<br/>COACT/TOMAHAWK não se aplicam.<br/>DAPT e anticoagulação pela via da ICP,<br/>não 'porque houve PCR'.<br/>Temperatura, PAM e O2 em paralelo —<br/>não depois da sala"])

  D2{"Sem supra: a causa da parada<br/>é claramente NÃO cardíaca?"}
  C_nao(["Tratar a etiologia.<br/>Não indicar cateterismo emergente<br/>só por choque ou arritmia.<br/>ECG e eco ainda valem se surgir<br/>indicação coronária independente"])

  D3{"Etiologia cardíaca suspeita E<br/>choque, tempestade elétrica<br/>ou isquemia em curso?"}
  C_alto(["Alto risco em curso:<br/>cateterismo emergente pode ser razoável.<br/>Detalhe: fluxograma de coronariografia<br/>desta pasta — não inventar classe aqui.<br/>LIMITE DA EVIDÊNCIA DISPONÍVEL<br/>da tabela AHA 2025"])

  C_estavel(["Estável, sem supra:<br/>NÃO cateterismo imediato de rotina.<br/>COACT: sobrevida 90 d 64,5% vs 67,2%, p=0,51;<br/>atrasou temperatura 5,4 h vs 4,7 h.<br/>TOMAHAWK: óbito 30 d HR 1,28<br/>IC95% 1,00-1,63, p=0,06.<br/>Angiografia adiada ou seletiva"])

  P2["Em TODOS os ramos, nas primeiras 24 h:<br/>1. Temperatura — evitar febre, não 33 °C de rotina<br/>2. PAM — tratar hipotensão; BOX 63 vs 77 mmHg neutro<br/>3. O2 — titular; BOX 9-10 vs 13-14 kPa neutro<br/>4. Eco/POCUS — mecânica, tamponamento, VE/VD<br/>5. DAPT/anticoag — só se houver indicação<br/>6. NÃO prognosticar o cérebro"]

  R0 --> P1 --> D1
  D1 -->|"Sim"| C_stemi
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C_nao
  D2 -->|"Não / incerta"| D3
  D3 -->|"Sim"| C_alto
  D3 -->|"Não"| C_estavel
  C_stemi --> P2
  C_nao --> P2
  C_alto --> P2
  C_estavel --> P2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef paralelo fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C_stemi,C_alto,C_estavel,C_nao conduta;
  class P2 paralelo;
```

## Subárvore paralela — o que não espera o resultado do cateterismo

```mermaid
flowchart TD
  S0["Mesmo turno, independente do ramo do ECG"] --> S1{"Temperatura:<br/>há alvo protocolizado<br/>e febre sendo tratada?"}

  S1 -->|"Não — ou 'vamos esfriar a 33' sem protocolo"| T1(["Nomear alvo agora.<br/>TTM2: 33 °C vs tratar febre ≥37,8 °C<br/>morte 6 m 50% vs 48%, RR 1,04, p=0,37.<br/>Rankin ≥4: 55% vs 55%.<br/>Arritmia hemodinâmica 24% vs 17%, p<0,001.<br/>Não dogmatizar 33 °C.<br/>Ver documento TTM/TTM2"])

  S1 -->|"Sim"| S2{"Hipotensão franca<br/>ou hipoxemia franca?"}

  S2 -->|"Sim"| T2(["Tratar agora.<br/>Piso operacional AHA 2025 Highlights:<br/>PAM ≥65 mmHg; SpO2 90-98%<br/>depois de medida confiável.<br/>COR/LOE: LIMITE DA EVIDÊNCIA DISPONÍVEL.<br/>BOX não autoriza perseguir 77 mmHg<br/>nem PaO2 13-14 kPa como ganho"])

  S2 -->|"Não"| S3{"Eco ou POCUS feito<br/>ou documentado como indisponível?"}

  S3 -->|"Não pensaram nisso"| T3(["Fazer agora se o aparelho existe:<br/>tamponamento, papilar, CIV,<br/>VE/VD, hipovolemia vs vasoplegia.<br/>Highlights AHA 2025: pode ser razoável.<br/>Sem classe inventada.<br/>Complicação mecânica: documento próprio"])

  S3 -->|"Sim"| S4{"Há indicação REAL de DAPT<br/>ou anticoagulação plena?"}

  S4 -->|"Só 'porque PCR'"| T4(["Não carregar.<br/>Parada não é SCA.<br/>DAPT se IAMCST/ICP/NSTE-ACS definido.<br/>Heparina plena se TEP, trombo<br/>ou procedimento — não por reflexo"])

  S4 -->|"Indicação nomeada"| S5{"Alguém já falou em prognóstico<br/>neurológico, limitação de suporte<br/>ou 'o cérebro não volta'?"}

  S5 -->|"Sim, nesta janela"| T5(["Parar a conversa.<br/>ESC 2023: não prognosticar antes de 72 h<br/>Classe I C — evidência já fichada no corpus.<br/>Algoritmo: documento de neuroprognóstico.<br/>Registrar exame; não julgar"])

  S5 -->|"Não"| T6(["24 h alinhadas com a evidência:<br/>ECG lido, cateterismo justificado,<br/>febre evitada, PAM/O2 no piso,<br/>eco pensado, antitrombótico indicado,<br/>cérebro ainda sem veredito"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class T1,T2,T3,T4,T5,T6 conduta;
```

## O que as árvores não mostram — de propósito

- **Como** prognosticar (EEG, NSE, SSEP, RM, mioclonia). Isso começa depois das 24 horas e mora no algoritmo ERC-ESICM / AHA 2025 desta pasta.
- **Qual** dispositivo de temperatura e **qual** vasopressor. Nenhum ensaio citado aqui comparou método de resfriamento nem noradrenalina versus outro no pós-RCE.
- **Parada intra-hospitalar e criança.** TTM2, COACT, TOMAHAWK e BOX são extra-hospitalares em adultos.
- **Classe da angiografia emergente no sem-supra de alto risco.** O fluxograma canônico de coronariografia desta pasta já discute o ramo; a tabela AHA 2025 não foi aberta nesta revisão editorial.

## Números que a árvore usa — e de onde vêm

Todos extraídos dos abstracts lidos via PubMed E-utilities nesta revisão editorial, não de memória:

| Ensaio | PMID | Comparação | Primário | O que muda a 24 h |
|---|---|---|---|---|
| TTM2 | 34133859 | 33 °C vs tratar febre ≥37,8 °C | Morte 6 m 50% vs 48%, RR 1,04, p=0,37 | Evitar febre; 33 °C soma arritmia (24% vs 17%) |
| COACT | 30883057 | Angio imediata vs adiada, sem IAMCST | Sobrevida 90 d 64,5% vs 67,2%, p=0,51 | Não ir de rotina; imediata atrasou temperatura |
| TOMAHAWK | 34459570 | Angio imediata vs adiada/seletiva, sem supra | Óbito 30 d 54% vs 46%, HR 1,28, p=0,06 | Ausência de benefício; sinal desfavorável não descartado |
| BOX-PAM | 36027564 | PAM 77 vs 63 mmHg | Morte/CPC 3–4 34% vs 32%, p=0,56 | Não perseguir 77 mmHg |
| BOX-O2 | 36027567 | PaO2 9–10 vs 13–14 kPa | 32,0% vs 33,9%, p=0,69 | Não perseguir hiperóxia liberal |

## Tudo com Tudo

- [Protocolo: o que o cardiologista decide nas primeiras 24 h](pos-rosc-primeiras-24-horas-o-que-o-cardiologista-decide.md)
- [Fluxograma: cuidado pós-parada e coronariografia](fluxograma-cuidado-pos-parada-e-coronariografia.md)
- [COACT e TOMAHAWK](coronariografia-imediata-apos-parada-cardiaca-sem-supra-de-st-coact-e-tomahawk.md)
- [TTM e TTM2](controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2.md)
- [BOX](metas-de-pressao-arterial-e-de-oxigenacao-pos-parada-cardiorrespiratoria-o-ensaio-box.md)
- [Neuroprognóstico](neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025.md)
