---
title: "Fluxograma: Dor torácica aguda — ECG, troponina e via de SCA na primeira hora"
slug: fluxograma-dor-toracica-aguda-ecg-troponina-e-via-de-sca
theme: "Geral"
kind: fluxograma
summary: "Árvore da primeira hora no PS, enfermaria ou UCO: ECG em 10 minutos, ramos que não esperam troponina (STEMI, equivalente de oclusão, NSTE de risco muito alto), desvio para a via da cocaína, e só então hs-cTn 0/1 h ou 0/2 h, zona de observação em 3 h e HEART/EDACS como apoio à alta — sem clonar o dump de SCA nem a tabela de cortes por ensaio."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica assistida em 29/08/2026. Árvore estrita (raiz única, um pai por nó, conduta só em folha). Recorte: adulto com dor torácica aguda ou equivalente isquêmico. Não substitui o fluxograma SCA ESC 2023, o 0/1 h, o HEART, a cocaína nem o ambulatorial de baixo risco. ECG ≤10 min I B e 0/1 h ou 0/2 h I B da Recommendation Table 1 ESC 2023 (PMID 37622654); invasiva imediata no risco muito alto I C da Table 4. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654."
  - "Diretriz Brasileira de Atendimento à Dor Torácica na Unidade de Emergência – 2025. Arq Bras Cardiol. 2025. PMC12981354."
  - "Six AJ, Backus BE, Kelder JC. Chest pain in the emergency room: value of the HEART score. Neth Heart J. 2008;16(6):191-196. PMID: 18665203."
  - "Backus BE, Six AJ, Kelder JC, et al. A prospective validation of the HEART score. Int J Cardiol. 2013;168(3):2153-2158. PMID: 23465250."
  - "Than M, Flaws D, Sanders S, et al. Development and validation of the Emergency Department Assessment of Chest pain Score and 2 h accelerated diagnostic protocol. Emerg Med Australas. 2014;26(1):34-44. DOI: 10.1111/1742-6723.12164. PMID: 24428678."
  - "Thygesen K, Alpert JS, Jaffe AS, et al. Fourth universal definition of myocardial infarction (2018). Eur Heart J. 2019;40(3):237-269. PMID: 30165617."
---

# Fluxograma: Dor torácica aguda — ECG, troponina e via de SCA na primeira hora

Árvore da **primeira hora** no adulto com dor torácica ou equivalente isquêmico (dispneia, epigástrio, irradiação) de minutos a horas, no pronto-socorro, na enfermaria ou na UCO. Não substitui o fluxograma de SCA, o algoritmo 0/1 h, o HEART, a via da cocaína nem a investigação ambulatorial. As folhas são **próximos caminhos**, não atestados.

ECG em até 10 minutos é Classe I B (ESC 2023, Table 1). STEMI, equivalente de oclusão e NSTE de risco muito alto **não esperam** troponina. Algoritmos 0/1 h ou 0/2 h são Classe I B só depois desses ramos. HEART/EDACS não são o primeiro nó.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto com dor torácica aguda<br/>ou equivalente isquêmico<br/>(dispneia, epigástrio, quebra de padrão)<br/>no PS, enfermaria ou UCO"] --> D1{"Via aérea comprometida,<br/>gasping ou PCR iminente?"}
  D1 -->|"Sim"| C1(["ABC e reanimação;<br/>o diagnóstico corre em paralelo,<br/>não depois"])
  D1 -->|"Não"| P1["ECG de 12 derivações em até 10 min<br/>(ESC 2023 I B). Sinais vitais, SpO2,<br/>acesso, glicemia, monitorização.<br/>Colher hs-cTn 0 h — não esperar<br/>o resultado para decidir STEMI/choque"]
  P1 --> D2{"O ECG ou a hemodinâmica<br/>mudam o destino agora?"}
  D2 -->|"Supra persistente de ST"| C2(["Via STEMI: reperfusão agora.<br/>Não esperar troponina"])
  D2 -->|"Equivalente de oclusão:<br/>posterior V7-V9 / V1-V3,<br/>VD V3R-V4R, aVR+depressão<br/>difusa, BRE/BRD/MP com<br/>alta suspeita de isquemia"| C3(["Via de oclusão / reperfusão.<br/>Não procurar só o supra clássico.<br/>Não esperar troponina"])
  D2 -->|"Choque, dor refratária,<br/>IC isquêmica, arritmia ameaçadora<br/>ou parada, complicação mecânica,<br/>ST/T dinâmico recorrente"| C4(["NSTE de risco muito alto:<br/>angiografia imediata (I C).<br/>Não esperar troponina.<br/>GRACE não é critério desta porta"])
  D2 -->|"Taquiarritmia instável ou BAV<br/>avançado com hipoperfusão,<br/>sem supra nem equivalente"| C5(["Tratar o ritmo primeiro;<br/>o restante do diferencial corre junto"])
  D2 -->|"Sem emergência elétrica<br/>nem risco muito alto"| P2["Anamnese dirigida: equivalentes<br/>em mulher/diabetes/idoso, cocaína,<br/>dissecção, TEP, tamponamento,<br/>pneumotórax, esôfago. Repetir ECG<br/>a cada 10-20 min se limítrofe"]
  P2 --> D3{"Uso recente confirmado<br/>ou suspeito de cocaína?"}
  D3 -->|"Sim"| C6(["Via da cocaína: ECG e hs-cTn<br/>continuam; não betabloqueador puro<br/>na intoxicação aguda. Ver o fluxograma<br/>dedicado — não clonar aqui"])
  D3 -->|"Não"| D4{"O laboratório tem hs-cTn<br/>com algoritmo 0/1 h validado?"}
  D4 -->|"Sim"| P3["Colher 0 h e 1 h de forma sistemática<br/>(janela ±10 min). Cortes do ensaio<br/>local — não de outro fabricante"]
  P3 --> D5{"O que o algoritmo 0/1 h diz?"}
  D5 -->|"Confirmação: 0 h alta<br/>ou delta 1 h de rule-in"| C7(["Via NSTE: internar. Distinguir<br/>tipo 1 de tipo 2 / lesão.<br/>Timing invasivo no fluxograma<br/>dedicado — DAPT não é automática<br/>se o quadro for desequilíbrio"])
  D5 -->|"Zona de observação"| C8(["Terceira hs-cTn em 3 h (I B)<br/>+ eco/escore. Não é<br/>indeterminado inofensivo"])
  D5 -->|"Descarte: 0 h muito baixa<br/>e dor há mais de 3 h,<br/>ou 0 h baixa + delta sem variação"| D6{"Clínica e ECG concordam<br/>com baixo risco? HEART pode<br/>apoiar (SBC 2025 I B).<br/>EDACS é opção, não atalho"}
  D6 -->|"Sim: ECG não isquêmico,<br/>sem dor recorrente,<br/>HEART baixo se usado"| C9(["Candidato a alta precoce<br/>e investigação ambulatorial<br/>se o protocolo local concordar.<br/>Escore não substitui o algoritmo"])
  D6 -->|"Não: dor recorrente, ECG<br/>preocupante, HEART intermediário<br/>ou alto, chegada muito precoce"| C10(["Não alta nesta hora:<br/>observação, repetir ECG,<br/>considerar terceira hs-cTn em 3 h<br/>se apresentação precoce"])
  D4 -->|"Não"| D7{"Há algoritmo 0/2 h<br/>validado para o ensaio?"}
  D7 -->|"Sim"| C11(["Usar 0/2 h — também I B.<br/>Mesma lógica descarte / confirmação<br/>/ observação. Não misturar cortes<br/>de 1 h com janela de 2 h"])
  D7 -->|"Não"| C12(["0/3 h só como alternativa<br/>quando 0/1 h e 0/2 h não são viáveis;<br/>menos eficaz e menos seguro.<br/>Sem classe própria na Table 1 de 2023.<br/>Não inventar cortes"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12 conduta;
```

## Como ler a árvore

- **ECG em 10 minutos** não é um “se”: é o passo P1, Classe I B. Dispneia, epigástrio e apresentação em mulher ou diabetes **não** abrem um atalho que pule o traçado.
- **Três folhas recusam a troponina como pedágio:** C2 (STEMI), C3 (equivalente de oclusão), C4 (NSTE de risco muito alto). Colher 0 h sim; esperar o número para ativar reperfusão ou angiografia de emergência, não.
- **GRACE não aparece em nenhum nó.** É critério de alto risco para a estratégia na internação, já fichado em outro documento. Recitá-lo nesta porta atrasa quem precisa de cateter agora.
- **Cocaína** é desvio de pacote farmacológico, não de ECG. A folha C6 manda ao fluxograma dedicado.
- **0/1 h e 0/2 h** têm a mesma classe (I B). A zona de observação exige terceira amostra em 3 h (I B). 0/3 h como estratégia **primária** é o último recurso da árvore, sem classe na Table 1.
- **HEART** só entra depois do descarte pelo algoritmo. SBC 2025 o prefere (I B). EDACS (PMID 24428678) é opção, não substituto do ECG. O “T” original do HEART é troponina convencional — não pontuar hs-cTn como se fosse o ensaio de 2008.
- **Tipo 1 versus tipo 2** não é nó precoce: supra e choque não esperam o rótulo. A folha C7 lembra que rule-in ≠ aterotrombose automática.

## Limites do diagrama

O fluxo não reproduz cortes numéricos por ensaio, critérios de fibrinólise, doses de antitrombótico, pontuação item a item do HEART/EDACS nem o corte de GRACE. Não cobre gestante, criança, SCAD nem MINOCA após a angiografia. Dissecção, TEP e tamponamento são lembretes em P2; cada um tem fluxograma próprio se a hipótese subir de posto. Ansiedade não é folha.

## Tudo com Tudo

- [Protocolo: Dor torácica aguda — primeira hora](/biblioteca/dor-toracica-aguda-primeira-hora-no-pronto-socorro)
- [Protocolo HEART e porta-ECG (SBC 2025)](/biblioteca/protocolo-de-dor-toracica-na-emergencia-escore-heart-e-tempo-porta-ecg-sbc-2025)
- [Algoritmo 0/1 h de hs-cTn](/biblioteca/fluxograma-algoritmo-0-1h-troponina-de-alta-sensibilidade-esc-2023)
- [Fluxograma SCA ESC 2023](/biblioteca/fluxograma-sindrome-coronariana-aguda-esc-2023)
- [Timing invasivo no NSTE](/biblioteca/fluxograma-sca-sem-supra-timing-da-estrategia-invasiva-esc-2023)
- [Infarto tipo 2 versus lesão](/biblioteca/infarto-tipo-2-versus-lesao-miocardica-nao-isquemica)
- [Cocaína — via aguda](/biblioteca/fluxograma-dor-toracica-aguda-com-uso-recente-confirmado-ou-suspeito-de-cocaina)
- [Cocaína — vasoespasmo](/biblioteca/fluxograma-dor-toracica-e-sca-por-vasoespasmo-coronariano-induzido-por-cocaina)
- [Dispneia aguda — primeira hora](/biblioteca/fluxograma-dispneia-aguda-cardiogenica-versus-nao-cardiogenica)
- [Dor torácica ambulatorial estável](/biblioteca/fluxograma-dor-toracica-ambulatorial-estavel-baixo-risco)
- [Escore HEART](/biblioteca/fluxograma-heart-dor-toracica-pronto-socorro)
