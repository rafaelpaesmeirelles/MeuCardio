---
title: "Sinalizadores ambulatoriais de disfunção tireoidiana no retorno cardiológico"
slug: sinalizadores-ambulatoriais-de-disfuncao-tireoidiana-no-retorno-cardiologico
theme: "Geral"
kind: protocolo
fonte_producao: grok
summary: "Consultório de cardiologia: quando pedir TSH (e T4 livre), quais pistas de hiper vs hipotireoidismo mudam o plano de FA/HAS/IC/dislipidemia, e o que encaminhar já — sem doses de levotiroxina/tionamidas e sem duplicar amiodarona (#838) nem o verbete longo de hipotireoidismo."
review_status: pendente_revisao
review_note: "Pacote Tudo-com-Tudo tireoide ambulatorial (07/09/2026). Lacuna: hipotireoidismo-CV já revisado é fisiopatologia; FA+hipertireoidismo subclínico cobre só cardioversão; #838 é vigilância de amiodarona. Este pacote é o filtro de consultório (quando dosar / quando escalar). Fontes: Klein/Danzi PMID 17923583; Jabbar PMID 27811932; ATA hiper PMID 27521067; ESC 2024 FA. Sem doses."
source_refs:
  - "Klein I, Danzi S. Thyroid disease and the heart. Circulation. 2007;116(15):1725-1735. DOI: 10.1161/CIRCULATIONAHA.106.678625. PMID: 17923583"
  - "Jabbar A, Pingitore A, Pearce SH, Zaman A, Iervasi G, Razvi S. Thyroid hormones and cardiovascular disease. Nat Rev Cardiol. 2017;14(1):39-55. DOI: 10.1038/nrcardio.2016.174. PMID: 27811932"
  - "Ross DS, Burch HB, Cooper DS, et al. 2016 American Thyroid Association Guidelines for Diagnosis and Management of Hyperthyroidism and Other Causes of Thyrotoxicosis. Thyroid. 2016;26(10):1343-1421. DOI: 10.1089/thy.2016.0229. PMID: 27521067"
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176"
---

# Sinalizadores ambulatoriais de disfunção tireoidiana no retorno cardiológico

Pergunta de **consultório**: diante de FA, HAS, IC, bradicardia, dislipidemia ou sintomas inespecíficos, **quando a tireoide deve sair do “já pedi TSH alguma vez” e virar filtro ativo**, e quando o achado pede endocrino/urgência — sem protocolar doses.

Não substitui:
- fisiopatologia e espectro do hipotireoidismo — [`hipotireoidismo-sistema-cardiovascular-bradicardia-dislipidemia`](hipotireoidismo-sistema-cardiovascular-bradicardia-dislipidemia.md);
- FA + hipertireoidismo subclínico antes da cardioversão — [`fa-e-hipertireoidismo-subclinico-quando-tratar-a-tireoide-antes-de-decidir-a-cardioversao`](../Fibrilação_atrial/fa-e-hipertireoidismo-subclinico-quando-tratar-a-tireoide-antes-de-decidir-a-cardioversao.md);
- vigilância tireoidiana **da amiodarona** — pacote [#838](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/838).

Árvore: [`fluxograma-ambulatorial-tireoide-quando-pedir-tsh-e-escalar`](fluxograma-ambulatorial-tireoide-quando-pedir-tsh-e-escalar.md). Checklist de retorno: [`checklist-ambulatorial-tireoide-no-paciente-cardiologico`](checklist-ambulatorial-tireoide-no-paciente-cardiologico.md).

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
2. TSH; se anormal → T4 livre (e T3 livre quando tireotoxicose clínica com T4 livre não esclarecedor — decisão com endocrino).
3. Se hipertireoidismo → **destino endocrino** + plano de ritmo/frequência/anticoagulação conforme FA (ESC 2024); cardiversão: ver doc FA+subclínico.
4. Se hipotireoidismo → reposição sob endocrino/clínico; ajustar expectativas de bradicardia/LDL/derrame (verbete revisado).
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
