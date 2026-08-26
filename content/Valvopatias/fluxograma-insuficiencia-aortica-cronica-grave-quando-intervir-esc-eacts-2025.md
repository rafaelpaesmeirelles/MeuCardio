---
title: "Fluxograma: Insuficiência aórtica crônica grave — quando intervir (ESC/EACTS 2025)"
slug: fluxograma-insuficiencia-aortica-cronica-grave-quando-intervir-esc-eacts-2025
theme: "Valvopatias"
kind: fluxograma
summary: "Árvore de decisão da ESC/EACTS 2025 para insuficiência aórtica crônica grave: sintoma ou outra cirurgia cardíaca levam à cirurgia, aorta dilatada decide por si, os cortes de FEVE e de dimensão sistólica do VE definem a indicação Classe I e a nova zona IIb em baixo risco, e o restante segue com eco anual ou a cada 3 a 6 meses."
review_status: revisado
review_note: "Produção científica assistida (Claude) e revisão editorial e científica independente (Codex), concluídas em 26/08/2026. Fontes primárias, coerência clínica, lógica dos fluxos, metadados e links foram conferidos; correções incorporadas. Publicação sujeita à aprovação do responsável técnico."
source_refs:
  - "Praz F, Borger MA, Lanz J, Marin-Cuartas M, et al.; ESC/EACTS Scientific Document Group. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4736. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295. Seção 7 e Recommendation Table 3, lidas na republicação integral Eur Heart J Valvular Struct Heart Dis 2025;1(1):xwag001, DOI: 10.1093/ehjvshd/xwag001, URL https://academic.oup.com/ehjvshd/article-pdf/1/1/xwag001/66461435/xwag001.pdf"
  - "Vahanian A, Beyersdorf F, Praz F, et al.; ESC/EACTS Scientific Document Group. 2021 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2022;43(7):561-632. DOI: 10.1093/eurheartj/ehab395. PMID: 34453165 — citada por meio do documento já publicado e verificado no acervo regurgitacao-aortica-cronica-e-aguda-indicacao-cirurgica-esceacts-2021.md, usado apenas para a comparação 2021 versus 2025."
---

# Fluxograma: Insuficiência aórtica crônica grave — quando intervir (ESC/EACTS 2025)

A insuficiência aórtica (IA) crônica grave é tolerada por anos porque o ventrículo esquerdo se adapta com dilatação e aumento de complacência — e é justamente essa adaptação que esconde o dano. Operar tarde deixa disfunção residual que a troca valvar não reverte; operar cedo expõe um paciente assintomático ao risco cirúrgico e à prótese. A ESC/EACTS 2025 manteve os pilares de 2021 (sintoma manda; FEVE, diâmetro sistólico e aorta decidem no assintomático) e mexeu na zona cinzenta: o corte indexado da recomendação IIb subiu de 20 para 22 mm/m2, o volume sistólico final indexado entrou como critério, o reparo valvar subiu para Classe IIa e o TAVI para IA nativa ganhou entrada formal na tabela. Esta árvore organiza essa sequência para o paciente com IA crônica grave já confirmada por avaliação integrada ao ecocardiograma (com RM cardíaca ou eco 3D nos casos limítrofes). A IA aguda — endocardite, dissecção — não entra aqui: a própria diretriz remete às diretrizes específicas.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Insuficiência aórtica crônica grave confirmada<br/>com FEVE, DSFVE, DSFVE indexado, VSFVE indexado<br/>e diâmetros da raiz e da aorta ascendente medidos"]
  D1{"Sintomas atribuíveis à IA?"}
  D2{"Risco cirúrgico proibitivo<br/>segundo o Heart Team?"}
  D3{"Anatomia adequada a TAVI<br/>em centro experiente?"}
  D4{"Indicação de outra cirurgia cardíaca<br/>como CABG, aorta ascendente<br/>ou outra valva?"}
  D5{"Raiz ou aorta ascendente com<br/>diâmetro máximo de 55 mm ou mais<br/>ou de 50 mm com fator de risco adicional?"}
  D6{"FEVE de repouso de 50% ou menos<br/>ou DSFVE acima de 50 mm<br/>ou DSFVE indexado acima de 25 mm/m2?"}
  D7{"FEVE de repouso de 55% ou menos<br/>ou DSFVE indexado acima de 22 mm/m2<br/>ou VSFVE indexado acima de 45 mL/m2?"}
  D8{"Risco cirúrgico baixo?"}
  D9{"DDVE acima de 65 mm com dilatação<br/>progressiva do VE ou queda de FEVE<br/>no seguimento?"}
  C1(["Cirurgia da valva aórtica<br/>independentemente da FEVE — Classe I"])
  C2(["TAVI pode ser considerado — Classe IIb<br/>preferir dispositivo dedicado à IA"])
  C3(["Tratamento clínico para alívio de sintomas<br/>com IECA ou diidropiridínico<br/>e reavaliação periódica pelo Heart Team"])
  C4(["Cirurgia da valva aórtica concomitante<br/>à outra cirurgia cardíaca — Classe I"])
  C5(["Cirurgia pela aorta com tratamento da valva<br/>recomendada se 55 mm ou mais — pode ser considerada<br/>se 50 mm com fator de risco em baixo risco e centro experiente<br/>reimplante com preservação valvar se raiz dilatada<br/>em jovem com tecido bom e centro experiente — Classe I"])
  C6(["Cirurgia da valva aórtica — Classe I<br/>reparo em centro experiente se durável — Classe IIa"])
  C7(["Cirurgia pode ser considerada — Classe IIb<br/>decisão no Heart Team com eco 3D ou RM"])
  C8(["Seguimento estreito a cada 3 a 6 meses<br/>com eco e RM cardíaca quando útil"])
  C9(["Discutir cirurgia se baixo risco e selecionado<br/>sem classe formal — senão seguir a cada 3 a 6 meses"])
  D10{"Aproximando-se dos cortes cirúrgicos<br/>ou dilatação progressiva do VE<br/>ou queda de FEVE no seguimento?"}
  C10(["Seguimento anual com eco e teste de esforço<br/>se factível — aorta acima de 45 mm exige<br/>novo eco em 6 meses e depois anual"])
  C11(["Seguimento a cada 3 a 6 meses com eco<br/>e RM cardíaca quando útil"])

  R0 --> D1
  D1 -->|"Sim"| D2
  D1 -->|"Não"| D4
  D2 -->|"Não"| C1
  D2 -->|"Sim"| D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  D4 -->|"Sim"| C4
  D4 -->|"Não"| D5
  D5 -->|"Sim"| C5
  D5 -->|"Não"| D6
  D6 -->|"Sim"| C6
  D6 -->|"Não"| D7
  D7 -->|"Sim"| D8
  D7 -->|"Não"| D9
  D8 -->|"Sim"| C7
  D8 -->|"Não"| C8
  D9 -->|"Sim"| C9
  D9 -->|"Não"| D10
  D10 -->|"Sim"| C11
  D10 -->|"Não"| C10

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11 conduta;
```

## Sintomático: cirurgia, e TAVI só quando a cirurgia é inviável

Em IA grave sintomática a cirurgia da valva aórtica é recomendada **independentemente da função ventricular** (Classe I, Nível B), a menos que o risco cirúrgico estimado seja proibitivo. A novidade de 2025 é que o TAVI, que em 2021 aparecia apenas em prosa, agora tem entrada própria na tabela: **pode ser considerado em paciente sintomático inelegível para cirurgia segundo o Heart Team, se a anatomia for adequada** (Classe IIb, Nível B). A diretriz é explícita sobre o preço: com próteses não dedicadas o uso é off-label, com mais malposicionamento e IA residual e cerca de 10% de segunda valva ou conversão cirúrgica; os dispositivos dedicados reduzem migração e IA residual, mas com taxa de marcapasso definitivo novo de 24%. Quando nem cirurgia nem TAVI são possíveis, IECA ou diidropiridínico podem aliviar sintomas — a diretriz não recomenda esses fármacos para adiar cirurgia no assintomático, e pede cautela com betabloqueador, que alonga a diástole e aumenta o volume regurgitante.

## Assintomático: outra cirurgia cardíaca e aorta dilatada decidem antes do ventrículo

Dois ramos precedem os cortes ventriculares. Primeiro: se o paciente com IA grave vai ser operado por outro motivo — revascularização, aorta ascendente ou outra valva —, a valva aórtica é tratada na mesma cirurgia, sintomático ou não (Classe I, Nível C). Segundo: a **dilatação da aorta dita a cirurgia independentemente da gravidade da IA**. O texto de 2025 repete os cortes da diretriz de aorta de 2024: cirurgia recomendada com diâmetro máximo de raiz ou aorta ascendente **≥ 55 mm**, e **50 mm pode ser considerado** em paciente selecionado de baixo risco, com fator de risco adicional, em centro experiente — os cortes por etiologia (Marfan, bicúspide, Loeys-Dietz) estão no fluxograma de aneurisma torácico do acervo. Nesse cenário, o reimplante com preservação valvar é recomendado em paciente jovem com dilatação de raiz, em centro experiente e com resultado durável esperado (Classe I, Nível B), e o texto o coloca como superior ao tubo valvado tipo Bentall em mortalidade e morbidade de longo prazo quando as cúspides são maleáveis e de boa qualidade.

O que vale para qualquer ramo cirúrgico: quando a cirurgia valvar já está indicada e o risco cirúrgico previsto é baixo, a substituição concomitante da raiz ou da aorta ascendente **deve ser considerada a partir de 45 mm** (Classe IIa, Nível C), pesando idade, superfície corporal, etiologia, valva bicúspide e o aspecto intraoperatório da parede — limiar mais bem demonstrado na bicúspide.

## Os dois patamares ventriculares

| Patamar | Critério (assintomático, IA grave) | Classe/Nível 2025 | Como era em 2021 |
|---|---|---|---|
| Indicação firme | FEVE de repouso ≤ 50%, ou DSFVE > 50 mm, ou DSFVEi > 25 mm/m2 (sobretudo se SC < 1,68 m2) | I, B | Igual (I, B) |
| Zona IIb, só em baixo risco cirúrgico | FEVE de repouso ≤ 55%, ou DSFVEi > 22 mm/m2, ou VSFVEi > 45 mL/m2 por eco ou RM (sobretudo se SC < 1,68 m2) | IIb, B | DSFVEi > 20 mm/m2 ou FEVE ≤ 55% (IIb, C); sem critério volumétrico |
| Sem classe formal | DDVE > 65 mm com aumento progressivo dos diâmetros e/ou queda de FEVE no seguimento | Prosa, "pode ser discutida" em baixo risco selecionado | Prosa, igual |

DSFVE, diâmetro sistólico final do VE; DSFVEi e VSFVEi, diâmetro e volume sistólicos finais indexados à superfície corporal (SC). A base do patamar IIb continua observacional — estudos ecocardiográficos que sugerem melhor prognóstico com intervenção precoce —, e por isso só se aplica quando a cirurgia é de baixo risco; o nível subiu de C para B. A diretriz cita ainda um corte volumétrico por RM de VSFVEi ≥ 43 mL/m2 proposto recentemente, com valor preditivo aparentemente superior ao do diâmetro, mas ele não entrou na tabela de recomendações. Strain longitudinal reduzido, reserva contrátil ao estresse, BNP elevado e fibrose por RM entram como modificadores na discussão do Heart Team, sem corte próprio.

## Reparo versus troca

A troca valvar continua sendo a abordagem padrão na maioria dos casos de IA. O reparo, porém, subiu de IIb para **IIa (Nível B)**: deve ser considerado em paciente selecionado, em centro experiente, quando se espera resultado durável. Na valva bicúspide, o grau de simetria do fenótipo prediz a reparabilidade e o resultado tardio, e preservação ou reparo devem ser considerados conforme idade, anatomia e experiência do centro. Em jovens bem selecionados, o autoenxerto pulmonar (Ross) é citado como alternativa razoável à prótese. A escolha entre prótese mecânica e biológica, quando se opta pela troca, segue a árvore própria do acervo.

## Quem segue em observação

| Situação | Intervalo de seguimento (ESC/EACTS 2025) |
|---|---|
| IA grave assintomática fora dos cortes | Anual, com ecocardiograma |
| Aproximando-se dos cortes, ou dilatação progressiva do VE ou queda de FEVE | A cada 3 a 6 meses; RM cardíaca especialmente útil |
| IA moderada | Consulta anual, ecocardiograma a cada 2 anos |
| Aorta ascendente dilatada ao primeiro eco | TC ou RM sincronizada ao ECG para confirmar o diâmetro máximo; se > 45 mm, novo eco em 6 meses e depois anual; aumento > 3 mm confirmado por angio-TC ou RM |

No assintomático sem critério cirúrgico, o teste de esforço deve ser feito quando factível — para desmascarar sintoma e medir capacidade funcional, não para quantificar a regurgitação (ver ecocardiograma-sob-estresse-nas-valvopatias-indicacoes-sbc-2024). Em IA moderada com indicação de revascularização ou cirurgia mitral, a decisão de tratar a valva aórtica é do Heart Team, porque a progressão da IA moderada pode ser muito lenta.

## Limitações e o que confirmar

- Todos os cortes, classes e níveis acima foram lidos na seção 7 e na Recommendation Table 3 do texto integral de 2025; nenhum valor ficou sem confirmação, e por isso não há marcação de verificação pendente nesta árvore.
- A ordem dos ramos é uma escolha didática: a Figura 5 da diretriz começa pela dilatação da raiz e só depois pergunta por sintomas e elegibilidade cirúrgica; aqui o sintoma vem primeiro. Um paciente pode satisfazer vários ramos ao mesmo tempo (aorta dilatada e FEVE baixa, por exemplo); a árvore para no primeiro que já define cirurgia.
- "Fator de risco adicional" para o corte de 50 mm de aorta e os cortes específicos de Marfan, bicúspide e Loeys-Dietz vêm da diretriz de aorta ESC 2024, não desta; use o fluxograma de aneurisma torácico do acervo para essa parte.
- O ramo "risco cirúrgico proibitivo" e o ramo "risco cirúrgico baixo" não têm valor numérico de escore na diretriz: são julgamentos do Heart Team, não cortes de STS ou EuroSCORE.
- O corte volumétrico por RM (VSFVEi ≥ 43 mL/m2) e os marcadores de disfunção subclínica (strain, BNP, fibrose) estão em prosa na diretriz, sem classe; a árvore não os usa como ramo.
- A IA aguda fica fora desta árvore; endocardite e dissecção seguem as diretrizes específicas, e o ramo de dissecção está no fluxograma de síndrome aórtica aguda.

## Tudo com Tudo

- [Regurgitação Aórtica Crônica e Aguda: Indicação Cirúrgica (ESC/EACTS 2021)](/biblioteca/regurgitacao-aortica-cronica-e-aguda-indicacao-cirurgica-esceacts-2021)
- [Valvopatias: Atualização Diretriz ESC/EACTS 2025](/biblioteca/valvopatias-atualizacao-diretriz-esceacts-2025)
- [Regurgitação Aórtica Nativa Grave: Tratamento Transcateter Dedicado — ALIGN-AR e o Sistema Trilogy](/biblioteca/regurgitacao-aortica-nativa-grave-tratamento-transcateter-dedicado-align-ar-trilogy)
- [Fluxograma: Aneurisma de Aorta Torácica — Corte de Reparo por Etiologia e Vigilância (ESC 2024)](/biblioteca/fluxograma-aneurisma-de-aorta-toracica-cortes-por-etiologia-esc-2024)
- [Fluxograma: Escolha de Prótese Valvar — Mecânica versus Biológica, por Idade e Comorbidade (ESC/EACTS 2025)](/biblioteca/fluxograma-escolha-de-protese-valvar-mecanica-vs-biologica-esc-eacts-2025)
- [Ecocardiograma sob estresse nas valvopatias: indicações lesão a lesão (SBC 2024)](/biblioteca/ecocardiograma-sob-estresse-nas-valvopatias-indicacoes-sbc-2024)
- [Fluxograma: Síndrome aórtica aguda — da dor torácica ao tratamento (ESC 2024)](/biblioteca/fluxograma-sindrome-aortica-aguda-esc-2024)
