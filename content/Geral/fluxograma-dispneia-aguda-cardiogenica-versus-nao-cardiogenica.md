---
title: "Fluxograma: Dispneia aguda cardiogênica versus não cardiogênica — primeira hora"
slug: fluxograma-dispneia-aguda-cardiogenica-versus-nao-cardiogenica
theme: "Geral"
kind: fluxograma
summary: "Árvore da primeira hora no PS, enfermaria ou UCO: via aérea, ECG em 10 minutos, hipoperfusão com ou sem POCUS, edema pulmonar cardiogênico com VNI, e o ramo de peptídeo abaixo do corte agudo que reabre pneumonia, TEP, anemia e ansiedade só como exclusão — sem tratar hipótese alguma como certeza."
review_status: pendente_revisao
fonte_producao: grok
review_note: "Produção científica assistida em 29/08/2026. Árvore de decisão estrita (raiz única, um pai por nó, conduta só em folha). Recorte agudo (minutos a horas); o fluxograma crônico ambulatorial já publicado nesta pasta não é substituído. Classes de oxigênio (I C) e VNI (IIa B) vêm da ESC 2021 já fichadas no corpus; cortes agudos de peptídeo (NT-proBNP <300, BNP <100) da mesma diretriz; ECG em 10 minutos do fluxograma de SCA ESC 2023 da casa. Publicação sujeita à aprovação do responsável técnico."
source_refs:
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992."
  - "McDonagh TA, Metra M, Adamo M, et al. 2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666."
  - "European Society of Cardiology. 2026 ESC Guidelines for the management of heart failure. Eur Heart J. 2026. DOI: 10.1093/eurheartj/ehag100."
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654."
  - "Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. Circulation. 2022;145(18):e895-e1032. DOI: 10.1161/CIR.0000000000001063. PMID: 35363499."
  - "Maisel AS, Krishnaswamy P, Nowak RM, et al. Rapid measurement of B-type natriuretic peptide in the emergency diagnosis of heart failure. N Engl J Med. 2002;347(3):161-167. DOI: 10.1056/NEJMoa020233. PMID: 12124404."
  - "Januzzi JL Jr, Camargo CA, Anwaruddin S, et al. The N-terminal Pro-BNP investigation of dyspnea in the emergency department (PRIDE) study. Am J Cardiol. 2005;95(8):948-954. DOI: 10.1016/j.amjcard.2004.12.032. PMID: 15820160."
  - "Atkinson PR, Milne J, Diegelmann L, et al; SHoC-ED Investigators. Does Point-of-Care Ultrasonography Improve Clinical Outcomes in Emergency Department Patients With Undifferentiated Hypotension? Ann Emerg Med. 2018;72(4):478-489. DOI: 10.1016/j.annemergmed.2018.04.002. PMID: 29866583."
  - "Rohde LEP, Montera MW, Bocchi EA, et al. Diretriz Brasileira de Insuficiência Cardíaca Crônica e Aguda. Arq Bras Cardiol. 2018;111(3):436-539. DOI: 10.5935/abc.20180190. PMID: 30379264."
---

# Fluxograma: Dispneia aguda cardiogênica versus não cardiogênica — primeira hora

Árvore de reconhecimento e primeira decisão no **adulto com dispneia de minutos a horas** no pronto-socorro, na enfermaria ou na UCO. Não substitui o fluxograma de dispneia crônica ambulatorial, o manejo diurético da IC descompensada, o protocolo de SCA, o de TEP nem o de tamponamento. As folhas são **próximos caminhos**, não atestados.

A ESC 2026 chama o episódio de deterioração de **IC descompensada**; a primeira hora continua sendo a da ESC 2021/2023: oxigênio se hipoxemia, VNI se edema cardiogênico com desconforto, ECG imediato, peptídeo para afastar mais do que para confirmar.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto com dispneia aguda<br/>(minutos a horas) no PS,<br/>enfermaria ou UCO"] --> D1{"Via aérea comprometida,<br/>gasping ou PCR iminente?"}
  D1 -->|"Sim"| C1(["ABC, via aérea e reanimação;<br/>o diagnóstico corre em paralelo,<br/>não depois"])
  D1 -->|"Não"| P1["ECG de 12 derivações em até<br/>10 min, sinais vitais, SpO2,<br/>acesso, glicemia e monitorização"]
  P1 --> D2{"O ECG muda o destino agora?"}
  D2 -->|"Supra de ST ou equivalente<br/>de oclusão"| C2(["Via de SCA: ativar reperfusão.<br/>Dispneia é equivalente isquêmico<br/>até prova em contrário"])
  D2 -->|"Taquiarritmia instável ou BAV<br/>avançado com hipoperfusão"| C3(["Tratar o ritmo primeiro:<br/>cardioversão ou estimulação<br/>conforme o traçado"])
  D2 -->|"Sem emergência elétrica"| P2["Exame dirigido: congestão vs<br/>hipoperfusão, assimetria pulmonar,<br/>TVP, palidez, sibilos, febre,<br/>pulso paradoxal, turgência jugular"]
  P2 --> D3{"Há hipoperfusão objetiva?<br/>pele fria, hipotensão, oligúria,<br/>lactato, alteração mental"}
  D3 -->|"Sim"| D4{"POCUS disponível agora<br/>com operador treinado?"}
  D4 -->|"Sim"| D5{"O que o POCUS sugere como<br/>hipótese principal?<br/>Não fecha o diagnóstico"}
  D5 -->|"Derrame com sinais<br/>de tamponamento"| C4(["Via de tamponamento:<br/>não diurético, não vasodilatador;<br/>drenagem urgente"])
  D5 -->|"VD dilatado, VE pequeno"| C5(["Suspeita de TEP de alto risco<br/>ou falência de VD: seguir o fluxo<br/>de TEP; volume não indiscriminado"])
  D5 -->|"VE hipocinético e linhas B<br/>bilaterais"| C6(["Choque cardiogênico: suporte de<br/>perfusão e descongestão quando<br/>a pressão permitir"])
  D5 -->|"VE hiperdinâmico, VCI colabável,<br/>sem congestão"| C7(["Choque distributivo ou hipovolêmico:<br/>tratar sepse ou sangramento;<br/>não VNI de edema cardiogênico"])
  D5 -->|"Inconclusivo"| C8(["Tratar hipoperfusão pela clínica;<br/>eco formal urgente; SHoC-ED não<br/>autoriza atraso nem exclusão pelo FOCUS"])
  D4 -->|"Não"| C9(["Sem POCUS: não atrasar suporte.<br/>Eco formal urgente e conduta pela<br/>clínica — SHoC-ED não mostrou ganho<br/>de sobrevida com o protocolo"])
  D3 -->|"Não"| D6{"Quadro de edema pulmonar<br/>cardiogênico com desconforto?<br/>ortopneia, estertores, PA alta,<br/>turgência, FR maior que 25<br/>ou SpO2 menor que 90 por cento"}
  D6 -->|"Sim"| C10(["Oxigênio se hipoxemia e VNI precoce<br/>como adjuvante; diurético IV se congestão;<br/>caçar precipitante — SCA, FA, HAS, infecção"])
  D6 -->|"Não"| P3["BNP ou NT-proBNP, troponina,<br/>gasometria, hemograma, função renal;<br/>radiografia ou ultrassom pulmonar"]
  P3 --> D7{"NT-proBNP menor que 300 pg/mL<br/>ou BNP menor que 100 pg/mL?"}
  D7 -->|"Sim — IC aguda pouco provável"| D8{"Febre, foco unilateral<br/>ou expectoração purulenta?"}
  D8 -->|"Sim"| C11(["Pneumonia ou exacerbação:<br/>tratar o foco; não encerrar se houver<br/>equivalente isquêmico ou misto"])
  D8 -->|"Não"| D9{"Início súbito com fator de TEV,<br/>pleuritismo, síncope ou hipoxemia<br/>desproporcional?"}
  D9 -->|"Sim"| C12(["Investigar TEP pela probabilidade<br/>pré-teste; não trombólise empírica<br/>e não usar peptídeo alto ou baixo<br/>como único árbitro"])
  D9 -->|"Não"| D10{"Palidez, taquicardia e hemoglobina<br/>baixa o bastante para o quadro?"}
  D10 -->|"Sim"| C13(["Anemia como agravante: corrigir<br/>conforme o contexto; não encerra<br/>SCA, IC ou TEP coexistentes"])
  D10 -->|"Não"| D11{"Exame, SpO2, ECG e biomarcadores<br/>sem alteração que explique?"}
  D11 -->|"Sim"| C14(["Ansiedade só como exclusão,<br/>depois da organicidade — nunca<br/>como primeira hipótese no idoso<br/>ou no cardiopata"])
  D11 -->|"Não"| C15(["Reavaliar quadro misto:<br/>DPOC mais IC, SCA sem dor,<br/>tamponamento incompleto ou sepse"])
  D7 -->|"Não — peptídeo alto ou indisponível"| D12{"Congestão clínica, linhas B bilaterais<br/>ou radiografia com edema,<br/>sem febre que explique sozinha?"}
  D12 -->|"Sim"| C16(["Tratar como IC descompensada / EAP:<br/>descongestão e precipitante em paralelo;<br/>peptídeo alto não exclui TEP nem SCA"])
  D12 -->|"Não"| D13{"Sibilos predominantes, DPOC ou asma<br/>conhecida, sem congestão?"}
  D13 -->|"Sim"| C17(["Broncoespasmo: tratar; reavaliar o<br/>coração se hipoxemia desproporcional,<br/>ortopneia ou peptídeo elevado"])
  D13 -->|"Não"| C18(["Manter TEP, SCA sem dor, anemia<br/>e quadro misto abertos; não rotular<br/>ansiedade nesta folha"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18 conduta;
```

## Como ler a árvore

- **Oxigênio** não é um nó porque vale em qualquer ramo com SpO2 < 90% ou PaO2 < 60 mmHg (ESC 2021, Classe I, C). O diagrama não autoriza oxigênio de rotina sem hipoxemia.
- **VNI** aparece só na folha do edema cardiogênico com desconforto (ESC 2021, Classe IIa, B). Escolha de CPAP versus bilevel, números do 3CPO e a discussão de mortalidade com a Cochrane estão no documento dedicado — este fluxo só manda iniciar cedo e não usar VNI como monoterapia.
- **POCUS** só entra no ramo de hipoperfusão. O SHoC-ED não mostrou ganho de sobrevida e não testou dispneia sem hipotensão; a folha “sem POCUS” e a “inconclusivo” existem para **não atrasar** suporte nem excluir choque cardiogênico por FOCUS “normal” (sensibilidade de 62,5% para disfunção de VE naquele subestudo).
- **Peptídeo abaixo do corte agudo** (NT-proBNP < 300 pg/mL ou BNP < 100 pg/mL) torna IC descompensada pouco provável; não torna o paciente “psiquiátrico”. Os cortes ambulatoriais (125 / 35) **não** se aplicam aqui — estão no fluxograma crônico.
- **Peptídeo alto** não fecha IC e não fecha TEP: embolia, SCA, FA, idade e rim também elevam o número.
- A ESC 2026 mudou o nome do episódio para **IC descompensada**; a folha C16 usa os dois termos de propósito, para casar o vocabulário novo com o fenótipo de EAP que o plantonista reconhece.

## Limites do diagrama

O fluxo não reproduz critérios de trombólise, pericardiocentese, reperfusão, dose de diurético nem parâmetros de VNI. Não cobre gestante, criança nem paciente já intubado. Ansiedade só aparece como folha de exclusão. Coexistência (DPOC + IC, infecção + edema, SCA + FA) é tratada como destino explícito, não como falha da árvore.

## Tudo com Tudo

- [Protocolo: Dispneia aguda de origem cardiovascular — abordagem inicial](/biblioteca/dispneia-aguda-de-origem-cardiovascular-abordagem-inicial)
- [Fluxograma: Dispneia crônica de origem indeterminada](/biblioteca/fluxograma-dispneia-cronica-de-origem-indeterminada-cardiaca-ou-pulmonar)
- [Insuficiência cardíaca aguda descompensada](/biblioteca/fluxograma-insuficiencia-cardiaca-aguda-descompensada)
- [Ventilação não invasiva no EAP cardiogênico](/biblioteca/ventilacao-nao-invasiva-no-edema-agudo-de-pulmao-cardiogenico-cpap-versus-bipap)
- [POCUS e o ensaio SHoC-ED](/biblioteca/pocus-na-triagem-do-choque-indiferenciado-o-ensaio-shoc-ed)
- [SCA — ESC 2023](/biblioteca/fluxograma-sindrome-coronariana-aguda-esc-2023)
- [TEP agudo](/biblioteca/fluxograma-tromboembolismo-pulmonar-diagnostico-esc-2019)
- [Tamponamento cardíaco](/biblioteca/fluxograma-tamponamento-cardiaco)
- [Bradicardia sintomática](/biblioteca/fluxograma-bradicardia-sintomatica-manejo-agudo)
