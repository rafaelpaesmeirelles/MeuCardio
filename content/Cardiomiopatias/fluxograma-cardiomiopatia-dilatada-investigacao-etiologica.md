---
title: "Fluxograma: Cardiomiopatia dilatada — investigação etiológica sistemática (ESC 2023)"
slug: fluxograma-cardiomiopatia-dilatada-investigacao-etiologica
theme: "Cardiomiopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Baseado na diretriz ESC 2023 de cardiomiopatias (Arbelo E et al., Eur Heart J 2023;44(37):3503-3626, DOI 10.1093/eurheartj/ehad194, PMID 37622657), cuja estrutura de exclusão de causa secundária (DAC/hipertensão/valvopatia/cardiopatia congênita) antes de investigar etiologia primária foi conferida via WebFetch direto no texto da diretriz nesta sessão (academic.oup.com/eurheartj/article/44/37/3503/7246608) — o texto confirma literalmente que a CMD é definida por 'dilatação do VE e disfunção sistólica global ou regional não explicada apenas por condições de sobrecarga (ex. hipertensão, valvopatia, cardiopatia congênita) ou DAC', e que essas causas devem ser sistematicamente excluídas antes do teste genético. Os documentos já publicados nesta pasta 'Cardiomiopatia Dilatada (CMD): Diagnóstico Genético e Manejo (ESC 2023)' e 'Manejo das Cardiomiopatias: Primeira Diretriz Abrangente ESC 2023' cobrem a mesma diretriz em profundidade e foram usados como referência cruzada de consistência. Os critérios de cardiomiopatia periparto (janela do último mês de gestação a 5 meses pós-parto, diagnóstico de exclusão) foram conferidos contra o documento já verificado desta pasta 'Cardiomiopatia Periparto: Critérios Diagnósticos, Recuperação e Manejo Atual' (Bauersachs J et al., Eur J Heart Fail 2019, PMID 31243866). Os critérios de taquicardiomiopatia (reversibilidade com controle da arritmia causadora, ausência de outra causa estrutural, cronicidade/magnitude da taquiarritmia) foram conferidos contra o documento já verificado desta pasta 'Taquicardiomiopatia (Cardiomiopatia Induzida por Taquicardia): Reconhecimento e Reversibilidade' (Sato N et al., Heart Fail Rev 2026, PMID 42412249). A calculadora de risco de LMNA para indicação individualizada de CDI (Wahbi K et al., Circulation 2019, PMID 31155932, lmna-risk-vta.fr) e o mecanismo de trombo de VE mediando 63,3% do risco de AVC cardioembólico associado a aneurisma apical na cardiomiopatia chagásica (Teixeira Tupinambás J et al., Heart 2026, PMID 42521491) já estavam verificados em documentos publicados desta mesma pasta e foram reaproveitados sem alteração de número. Nenhum PMID/DOI novo foi gerado nesta sessão — todos os números citados já haviam sido conferidos contra a fonte primária em documentos publicados desta mesma pasta antes desta redação."
source_refs: ["Arbelo E, Protonotarios A, Gimeno JR, et al. 2023 ESC Guidelines for the management of cardiomyopathies. Eur Heart J. 2023;44(37):3503-3626. DOI 10.1093/eurheartj/ehad194. PMID 37622657.", "Bauersachs J, König T, van der Meer P, et al. Pathophysiology, diagnosis and management of peripartum cardiomyopathy: a position statement from the Heart Failure Association of the European Society of Cardiology Study Group on PPCM. Eur J Heart Fail. 2019;21(7):827-843. DOI 10.1002/ejhf.1493. PMID 31243866.", "Sato N, et al. Tachycardia-induced cardiomyopathy: evolution of the concept and contemporary insights. Heart Fail Rev. 2026 Jul 7. DOI 10.1007/s10741-026-10650-2. PMID 42412249.", "Wahbi K, Ben Yaou R, Gandjbakhch E, et al. Development and Validation of a New Risk Prediction Score for Life-Threatening Ventricular Tachyarrhythmias in Laminopathies. Circulation. 2019;140(4):293-302. DOI 10.1161/CIRCULATIONAHA.118.039410. PMID 31155932.", "Teixeira Tupinambás J, Rocha MOC, Lage TAR, et al. Cardioembolic stroke in Chagas cardiomyopathy: the interplay between apical aneurysm, left ventricular thrombus and clinical outcomes. Heart. 2026 Jul 28:heartjnl-2026-328159. DOI 10.1136/heartjnl-2026-328159. PMID 42521491."]
---

# Fluxograma: Cardiomiopatia dilatada — investigação etiológica sistemática (ESC 2023)

A diretriz ESC 2023 de cardiomiopatias organiza a cardiomiopatia dilatada (CMD)
por **fenótipo primeiro, etiologia depois**: uma vez reconhecido o padrão de
ventrículo esquerdo dilatado com disfunção sistólica, o passo seguinte não é o
teste genético — é **excluir sistematicamente as causas secundárias** (doença
arterial coronariana, hipertensão, valvopatia, cardiopatia congênita) que por
definição afastam o diagnóstico de CMD primária. Só depois dessa exclusão a
investigação percorre, em ordem, as etiologias adquiridas potencialmente
reversíveis — tóxica, taquicardia-induzida, periparto, chagásica, inflamatória —
antes de chegar à hipótese genética/familiar ou à CMD idiopática. Esta árvore
formaliza esse percurso, sem repetir o que os documentos de diagnóstico
genético e estratificação de risco de morte súbita desta mesma pasta já cobrem
em profundidade.

## Árvore de decisão

```mermaid
flowchart TD
  A["Fenótipo de cardiomiopatia dilatada:<br/>VE dilatado + disfunção sistólica<br/>à ecocardiografia"] --> D1{"DAC, hipertensão, valvopatia ou<br/>cardiopatia congênita explicam<br/>sozinhas o achado?"}

  D1 -->|"Sim, explicam"| C1(["Não é CMD primária: tratar a causa<br/>identificada (DAC/HAS/valvopatia/CC)<br/>e reavaliar o remodelamento"])

  D1 -->|"Não explicam"| D2{"História de consumo importante<br/>de álcool ou exposição a cardiotóxico<br/>(antraciclina, trastuzumabe,<br/>radioterapia torácica)?"}

  D2 -->|"Sim"| C2(["CMD tóxica: suspender/reduzir a<br/>exposição, TMO para IC, reavaliar<br/>FEVE em 3 a 6 meses"])

  D2 -->|"Não"| D3{"Taquiarritmia sustentada de longa<br/>duração precede a disfunção (FA/flutter<br/>de alta resposta, taquicardia atrial<br/>incessante, extrassistolia ventricular<br/>de alta carga)?"}

  D3 -->|"Sim"| C3(["Taquicardiomiopatia: controle de<br/>frequência/ritmo, ablação por cateter<br/>quando indicada, TMO para IC em<br/>paralelo, reavaliar FEVE após controle<br/>da arritmia"])

  D3 -->|"Não"| D4{"Mulher no último mês de gestação<br/>até 5 meses pós-parto, sem<br/>cardiopatia prévia conhecida?"}

  D4 -->|"Sim"| C4(["Cardiomiopatia periparto: TMO para IC<br/>com ajuste gestacional/lactação,<br/>anticoagulação profilática se disfunção<br/>importante, avaliar bromocriptina<br/>conforme protocolo"])

  D4 -->|"Não"| D5{"Sorologia positiva para Chagas ou<br/>procedência de área endêmica<br/>com sorologia a confirmar?"}

  D5 -->|"Sim"| C5(["CMD chagásica: rastrear aneurisma<br/>apical e trombo de VE ao<br/>ecocardiograma, anticoagular se<br/>trombo confirmado, avaliar<br/>benznidazol e TMO para IC"])

  D5 -->|"Não"| D6{"RM cardíaca com realce tardio<br/>subepicárdico/mesocárdico ou quadro<br/>clínico sugestivo de miocardite (dor<br/>torácica, troponina elevada, infecção<br/>viral recente)?"}

  D6 -->|"Sim"| D7{"Instabilidade hemodinâmica, arritmia<br/>ventricular maligna ou bloqueio<br/>atrioventricular avançado?"}

  D7 -->|"Sim"| C6(["Miocardite complicada: internar em<br/>UTI, considerar biópsia<br/>endomiocárdica, suporte circulatório<br/>mecânico se choque"])

  D7 -->|"Não"| C7(["Miocardite não complicada: TMO para<br/>IC, restrição de exercício físico, RM<br/>cardíaca de controle em 3 a 6 meses"])

  D6 -->|"Não"| D8{"História familiar de CMD ou morte<br/>súbita precoce, ou achados<br/>extracardíacos sugestivos (doença<br/>neuromuscular, distúrbio de<br/>condução)?"}

  D8 -->|"Sim"| D9{"Painel genético identifica variante de<br/>alto risco (LMNA, FLNC, RBM20, PLN,<br/>DES, TMEM43)?"}

  D9 -->|"Sim"| C8(["CMD genética de alto risco:<br/>aconselhamento genético,<br/>rastreamento em cascata familiar,<br/>aplicar calculadora de risco específica<br/>(ex.: lmna-risk-vta.fr para LMNA)<br/>na decisão de CDI"])

  D9 -->|"Não"| C9(["CMD genética/familiar: teste genético<br/>em painel, aconselhamento genético,<br/>rastreamento em cascata familiar,<br/>seguimento com imagem seriada"])

  D8 -->|"Não"| C10(["CMD idiopática: TMO guiada por<br/>diretriz de IC, considerar teste<br/>genético mesmo sem história familiar,<br/>reavaliar FEVE em 3 a 6 meses"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10 conduta;
```

## Por que esta ordem, e o que fica de fora do diagrama

A sequência de exclusão segue a lógica da própria definição da ESC 2023: CMD é
dilatação e disfunção sistólica **não explicadas por** sobrecarga hemodinâmica
ou DAC — logo, excluir essas causas é o primeiro passo, não um item entre
outros. As etiologias adquiridas potencialmente **reversíveis** (tóxica,
taquicardia-induzida, periparto, chagásica com trombo tratável, miocardítica)
vêm antes da investigação genética porque mudam o prognóstico e a urgência da
conduta de forma mais imediata do que a etiologia genética — e porque
identificar uma causa reversível não impede, em paralelo, considerar teste
genético quando a suspeita clínica também apontar nessa direção (ver o ramo
final, CMD idiopática).

**Não entram como ramos da árvore, por valerem transversalmente a qualquer
etiologia identificada:** o rastreamento familiar em cascata (recomendado em
toda cardiomiopatia hereditária ou suspeita de ser, independentemente de o
teste genético estar em curso), o aconselhamento genético estruturado antes de
qualquer teste, e a reavaliação periódica de FEVE — todos citados dentro dos
nós de conduta correspondentes, mas não desenhados como decisão própria para
não inflar a árvore com passos que não bifurcam a conduta.

A cardiomiopatia chagásica, uma vez confirmada, tem uma armadilha específica já
documentada nesta pasta: o aneurisma apical **não é**, isoladamente, o
preditor mais forte de AVC cardioembólico — **63,3%** do seu efeito é mediado
pelo trombo de ventrículo esquerdo que ele favorece formar, não por mecanismo
direto independente. Por isso o nó de conduta desta árvore para CMD chagásica
especifica rastrear **trombo**, não apenas registrar a presença do aneurisma.

A estratificação de risco de morte súbita e a indicação formal de CDI por
fenótipo — incluindo a calculadora de risco específica para portador de
mutação LMNA (índice C de 0,776, limiar de risco em 5 anos ≥7%) — são tratadas
em profundidade no documento "Cardiomiopatia Dilatada (CMD): Diagnóstico
Genético e Manejo (ESC 2023)" desta mesma pasta, e não foram redesenhadas aqui
para evitar duplicar a árvore de decisão.