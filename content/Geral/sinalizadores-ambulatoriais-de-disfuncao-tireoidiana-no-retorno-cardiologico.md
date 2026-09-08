---
title: "Sinalizadores ambulatoriais de disfunção tireoidiana no retorno cardiológico"
slug: sinalizadores-ambulatoriais-de-disfuncao-tireoidiana-no-retorno-cardiologico
theme: "Geral"
kind: protocolo
fonte_producao: grok
summary: "Consultório de cardiologia: quando pedir TSH (e T4 livre), quais pistas de hiper vs hipotireoidismo mudam o plano de FA/HAS/IC/dislipidemia, e o que encaminhar já — sem doses de levotiroxina/tionamidas e sem duplicar amiodarona (#838) nem o verbete longo de hipotireoidismo."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR879 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Garber JR et al. Clinical practice guidelines for hypothyroidism in adults. Endocr Pract. 2012;18:988-1028. DOI: 10.4158/EP12280.GL. PMID: 23246686."
  - "Klein I, Danzi S. Thyroid disease and the heart. Circulation. 2007;116(15):1725-1735. DOI: 10.1161/CIRCULATIONAHA.106.678326. PMID: 17923583"
  - "Jabbar A, Pingitore A, Pearce SH, Zaman A, Iervasi G, Razvi S. Thyroid hormones and cardiovascular disease. Nat Rev Cardiol. 2017;14(1):39-55. DOI: 10.1038/nrcardio.2016.174. PMID: 27811932"
  - "Ross DS, Burch HB, Cooper DS, et al. 2016 American Thyroid Association Guidelines for Diagnosis and Management of Hyperthyroidism and Other Causes of Thyrotoxicosis. Thyroid. 2016;26(10):1343-1421. DOI: 10.1089/thy.2016.0229. PMID: 27521067"
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176"
---

# Sinalizadores ambulatoriais de disfunção tireoidiana no retorno cardiológico

Pergunta de **consultório**: diante de FA, HAS, IC, bradicardia, dislipidemia ou sintomas inespecíficos, **quando a tireoide deve sair do “já pedi TSH alguma vez” e virar filtro ativo**, e quando o achado pede endocrino/urgência — sem protocolar doses.

Não substitui:
- fisiopatologia e espectro do hipotireoidismo — [`hipotireoidismo-sistema-cardiovascular-bradicardia-dislipidemia`](/biblioteca/hipotireoidismo-sistema-cardiovascular-bradicardia-dislipidemia);
- FA + hipertireoidismo subclínico antes da cardioversão — [`fa-e-hipertireoidismo-subclinico-quando-tratar-a-tireoide-antes-de-decidir-a-cardioversao`](/biblioteca/fa-e-hipertireoidismo-subclinico-quando-tratar-a-tireoide-antes-de-decidir-a-cardioversao);
- vigilância tireoidiana **da amiodarona** — pacote [#838](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/838).

Árvore: [`fluxograma-ambulatorial-tireoide-quando-pedir-tsh-e-escalar`](/biblioteca/fluxograma-ambulatorial-tireoide-quando-pedir-tsh-e-escalar). Checklist de retorno: [`checklist-ambulatorial-tireoide-no-paciente-cardiologico`](/biblioteca/checklist-ambulatorial-tireoide-no-paciente-cardiologico).

## Princípio

Hormônio tireoidiano modula cronotropismo, inotropismo, RVP e lipídios (Klein & Danzi, PMID 17923583; Jabbar et al., PMID 27811932). No ambulatorial cardiológico o rendimento é alto quando há **pista clínica ou fenótipo CV clássico** — não TSH de rotina em todo retorno estável sem indicação.

A ATA 2016 (PMID 27521067) ancora a tireotoxicose como causa tratável de FA e de descompensação; a ESC 2024 de FA reforça investigar causas reversíveis/precipitantes, incluindo disfunção tireoidiana, no manejo etiológico.

## Quem merece TSH (e T4 livre quando TSH anormal) neste retorno

| Contexto cardiológico | Pistas que disparam dosagem |
|---|---|
| FA nova, recorrente ou de difícil controle | Palpitações + intolerância ao calor, perda de peso, tremor, ansiedade; idoso “só com FA” (hipertireoidismo pode ser oligosintomático) |
| Bradicardia sinusal / necessidade precoce de MP | Fadiga, ganho de peso, pele seca, mixedema; sem cronotrópico negativo proporcional |
| HAS com padrão atípico | Diastólica predominante + pistas de hipo; sistólica/pulso alargado + pistas de hiper |
| Dislipidemia LDL nova / refratária | Antes de rotular falha de estatina — ver verbete de hipotireoidismo |
| IC / alto débito suspeito | Taquicardia persistente, FA, perda de peso, sopro de alto fluxo |
| Derrame pericárdico crônico sem causa | Instalação lenta, sem inflamação óbvia |
| Amiodarona | **Não usar este pacote** — seguir [#838](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/838) |

## Encaminhar agora (não “aguardar o próximo TSH de rotina”)

1. **Suspeita de tireotoxicose** com FA rápida, angina, IC descompensada ou síncope — estabilizar CV; laboratório tireoidiano urgente; articular endocrino; não “só aumentar betabloqueador e ver".
2. **Sinais de gravidade de hipo** (hipotermia, rebaixamento, hipoventilação, hipotensão) — via de emergência (coma mixedematoso); ver verbete de hipotireoidismo.
3. **TSH suprimido + T4 livre alto** em paciente com FA/IC — tipagem etiológica (Basedow vs nódulo vs tireoidite) com endocrino; cardiologia não inicia tionamida “no escuro” neste protocolo.
4. **Clonalidade / amiloide** não é tema deste pacote — se hipertrofia/IC com red flags de amiloide, ver [#844](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/844).

## Pode permanecer no plano habitual (com pergunta explícita)

- Sem pistas de disfunção e sem fenótipo disparador.
- TSH recente normal e quadro estável.
- Hipotireoidismo já em reposição com TSH no alvo e sintomas CV explicados por outra causa.

## Conduta ambulatorial mínima (sem doses)

1. História dirigida (hiper vs hipo) + exame (FC, tremor, bócio, reflexos, pele).
2. TSH; se anormal → T4 livre (e T3 total quando tireotoxicose clínica com T4 livre não esclarecedor — decisão com endocrino).
3. Se hipertireoidismo → **destino endocrino** + plano de ritmo/frequência/anticoagulação conforme FA (ESC 2024); cardiversão: ver doc FA+subclínico.
4. Se hipotireoidismo → reposição sob endocrino/clínico; ajustar expectativas de bradicardia/LDL/derrame pericárdico (verbete revisado).
5. **Não** suspender GDMT “porque a tireoide vai resolver tudo” sem plano.

## Checklist de 90 segundos

1. FA / bradicardia / LDL refratário / HAS atípica / derrame / IC sem causa clara **e** pista tireoidiana? → dosar.
2. Tireotoxicose com instabilidade? → urgente, não rotina.
3. Amiodarona? → pacote #838.
4. Sem doses de T4/tionamida neste documento.

## Armadilhas

- Atribuir toda FA do idoso a “idade” sem TSH.
- Tratar só a frequência e esquecer a causa tireoidiana.
- Pedir cintilografia/ionizantes sem endocrino e sem contexto.
- Usar o calendário de amiodarona em quem **não** usa amiodarona (e o inverso).

## Limite da evidência

Este texto é **filtro ambulatorial**. Metas de TSH sob reposição, escolha de tionamida/radioiodo/cirurgia e doses ficam com endocrinologia e com os documentos já revisados do corpus.

## Interpretar a síndrome, não o TSH isolado

TSH baixo com FA estável não é tempestade tireotóxica; esta exige tireotoxicose grave com disfunção sistêmica, incluindo hipertermia, alteração mental e manifestações GI/hepáticas/cardíacas. TSH alto isolado não é coma mixedematoso: suspeitar pela síndrome de hipotermia, alteração de consciência, hipoventilação, hipotensão/bradicardia grave em contexto apropriado. Não esperar laboratório para estabilizar suspeita clínica grave.

TSH anormal exige T4 livre; em TSH suprimido com T4 livre normal/inconclusivo, considerar T3 total. Doença sistêmica aguda e fármacos alteram exames; não iniciar tratamento crônico por resultado isolado sem contexto. Bradicardia, LDL alto e derrame pericárdico são inespecíficos. Repetir exames recentes se mudança clínica, gestação, amiodarona/lítio ou interferentes. FA segue seu algoritmo de ritmo/frequência e anticoagulação: não atrasar OAC indicada esperando eutireoidismo; cardioversão eletiva é individualizada.

[Disfunção tireoidiana por amiodarona](/biblioteca/disfuncao-tireoidiana-associada-a-amiodarona-diferenciar-tipo-1-de-tipo-2-e-decidir-sobre-suspender).
