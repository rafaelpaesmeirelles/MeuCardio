---
title: "Fluxograma: Estenose pulmonar no adulto — indicação de intervenção (ESC 2020)"
slug: fluxograma-estenose-pulmonar-obstrucao-via-saida-vd-indicacao-intervencao-esc-2020
theme: "Cardiopatias congênitas"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Fonte é a diretriz ESC 2020 de cardiopatia congênita do adulto (Baumgartner H, De Backer J, Babu-Narayan SV, et al. 2020 ESC Guidelines for the management of adult congenital heart disease. Eur Heart J. 2021;42(6):563-645. DOI: 10.1093/eurheartj/ehaa554. PMID: 32860028), já lida e usada no documento em prosa 'Obstrução da Via de Saída do Ventrículo Direito (Estenose Pulmonar) no Adulto — ESC 2020' publicado nesta mesma pasta — todas as classes, níveis e cortes numéricos deste fluxograma foram conferidos contra aquele documento (que já tinha o texto integral da seção 4.8 obtido e conferido em 30/07/2026), sem alterar nenhum valor. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Baumgartner H, De Backer J, Babu-Narayan SV, et al. 2020 ESC Guidelines for the management of adult congenital heart disease. European Heart Journal. 2021;42(6):563-645. DOI: 10.1093/eurheartj/ehaa554. PMID: 32860028 — seção 4.8 (Right ventricular outflow tract obstruction) e tabela de recomendações de intervenção."]
---

# Fluxograma: Estenose pulmonar no adulto — indicação de intervenção (ESC 2020)

A estenose pulmonar é a lesão congênita isolada mais comum, e a diretriz
europeia de 2020 organiza a indicação de intervir em torno de três eixos:
**o nível anatômico da obstrução** (que decide a técnica), **o gradiente de
pico ao Doppler** (que decide se é Classe I independente de sintomas) e, só
quando o gradiente não é grave o suficiente para justificar sozinho, **um
conjunto de critérios acessórios** — sintoma, função de VD, regurgitação
tricúspide, shunt residual. O gradiente vale como medida direta de gravidade
apenas com função de VD normal e fluxo transvalvar normal; havendo mais de
uma estenose em série ou estreitamento alongado, a equação de Bernoulli
superestima o gradiente, e a velocidade de regurgitação tricúspide passa a
ser a estimativa mais confiável.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto com estenose pulmonar (obstrução<br/>da via de saída do ventrículo direito)<br/>diagnosticada ao ecocardiograma"] --> D1{"Qual o nível anatômico<br/>predominante da obstrução?"}

  D1 -->|"Periférico (ramos<br/>da artéria pulmonar)"| D2{"Há estreitamento acima de 50% do<br/>diâmetro, com pressão sistólica de VD<br/>acima de 50 mmHg e/ou redução de<br/>perfusão pulmonar relacionada?"}

  D2 -->|"Sim"| C1(["Tratamento intervencionista por cateter<br/>deve ser considerado, com implante de<br/>stent, com frequência — Classe IIa,<br/>nível C"])

  D2 -->|"Não"| C2(["Observação clínica, com reavaliação<br/>periódica — sem indicação de<br/>intervenção no momento"])

  D1 -->|"Valvular, sub-infundibular<br/>ou infundibular"| D3{"O gradiente de pico ao Doppler é<br/>grave — acima de 64 mmHg —, com função<br/>de VD normal e fluxo transvalvar normal?"}

  D3 -->|"Sim"| D4{"A correção exige substituição<br/>valvar, ou pode aliviar a obstrução<br/>sem implantar uma prótese?"}

  D4 -->|"Pode corrigir sem<br/>substituição valvar"| C3(["Intervenção recomendada independente<br/>de sintomas — Classe I, nível C.<br/>Na estenose valvar adequada: balão;<br/>na sub/infundibular: ressecção<br/>cirúrgica em centro especializado"])

  D4 -->|"Exige substituição<br/>valvar cirúrgica"| D5{"O paciente é sintomático, ou<br/>assintomático com pelo menos um<br/>destes: queda objetiva da capacidade<br/>de exercício; queda de função de VD<br/>e/ou progressão de regurgitação<br/>tricúspide para pelo menos moderada;<br/>pressão sistólica de VD acima de<br/>80 mmHg; shunt direita-esquerda<br/>via CIA/CIV?"}

  D5 -->|"Sim"| C4(["Troca valvar cirúrgica indicada —<br/>Classe I, nível C. Cirurgia também é<br/>a via para estenose sub-infundibular/<br/>infundibular e para anel pulmonar<br/>hipoplásico"])

  D5 -->|"Não — assintomático, sem<br/>nenhum desses critérios"| C5(["Observação clínica, com reavaliação<br/>periódica — sem indicação de<br/>intervenção no momento"])

  D3 -->|"Não — gradiente abaixo de<br/>64 mmHg, ou avaliação direta pelo<br/>gradiente não é confiável"| D6{"Há pelo menos um destes: sintoma<br/>relacionado à estenose pulmonar;<br/>queda de função de VD e/ou<br/>progressão de regurgitação tricúspide<br/>para pelo menos moderada; shunt<br/>direita-esquerda via CIA/CIV?"}

  D6 -->|"Sim"| C6(["Intervenção deve ser considerada —<br/>Classe IIa, nível C"])

  D6 -->|"Não"| C7(["Observação clínica, com reavaliação<br/>periódica — sem indicação de<br/>intervenção no momento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## A escolha da técnica, que a árvore não repete a cada folha

**Valvuloplastia por balão via cateter** é a via recomendada para estenose
pulmonar **valvar** não displásica. Na estenose **periférica dos ramos da
artéria pulmonar**, a técnica é angioplastia por balão, frequentemente com
implante de stent; o procedimento não envolve a valva. **Cirurgia** é a via
para estenose sub-infundibular
ou infundibular, para anel pulmonar hipoplásico, e para a valva **displásica**
(cúspides pouco móveis, espessamento mixomatoso, frequentemente parte da
síndrome de Noonan) — a literatura mostra taxa de sucesso menor da
valvuloplastia por balão nesse subtipo, o que antecipa a indicação cirúrgica.

## O que a árvore não mostra

**A armadilha de medida do gradiente em série.** Se houver mais de uma
estenose em série (por exemplo subvalvular e valvular associadas) ou
estreitamento alongado, a equação de Bernoulli superestima o gradiente de
pico — nesse cenário, a velocidade de regurgitação tricúspide ao Doppler é
estimativa mais confiável da pressão de VD, e portanto da gravidade real da
obstrução, do que o número lido direto na via de saída.

**O corte para troca valvar é mais alto de propósito.** Quando a troca valvar
cirúrgica é a única opção — não a valvuloplastia por balão —, o limiar de
intervenção no paciente assintomático soma vários critérios acessórios em vez
de bastar o gradiente isoladamente: é assim porque os riscos de longo prazo
de uma prótese (endocardite, reintervenção por falência protética) entram na
conta antes de indicar cirurgia em quem não tem sintoma.

**Exercício e gestação têm considerações próprias, fora da árvore.** Estenose
leve residual não restringe esporte; a moderada deve evitar esporte estático e
de alta intensidade; a grave fica restrita a esporte de baixa intensidade. Na
gestação, a estenose costuma ser bem tolerada — exceto se extremamente grave
ou com falência de VD relevante —, e a valvuloplastia por balão transcateter
pode ser realizada durante a gravidez se necessário.

**Este fluxograma não cobre a regurgitação pulmonar pós-reparo de Tetralogia
de Fallot**, incluindo a indicação de troca valvar pulmonar (PVRep) e de
intervenção por cateter (TPVI) — tema com tratamento próprio no documento de
seguimento tardio de Tetralogia de Fallot e coarctação de aorta desta pasta.
