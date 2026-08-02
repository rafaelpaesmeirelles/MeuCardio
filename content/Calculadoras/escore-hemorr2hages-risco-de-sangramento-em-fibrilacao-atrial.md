---
title: "Escore HEMORR2HAGES — risco de sangramento maior em fibrilação atrial anticoagulada"
slug: escore-hemorr2hages-risco-de-sangramento-em-fibrilacao-atrial
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Gage BF, Yan Y, Milligan PE, Waterman AD, Culverhouse R, Rich MW, Radford MJ. Clinical classification schemes for predicting hemorrhage: results from the National Registry of Atrial Fibrillation (NRAF). Am Heart J. 2006;151(3):713-719. DOI: 10.1016/j.ahj.2005.04.017. PMID: 16504638"]
legacy_source: "Documento novo, escrito em 01/08/2026. O tema Calculadoras já tinha três escores de sangramento em FA anticoagulada — HAS-BLED, ORBIT e ATRIA (este último cobrindo risco de AVC e de sangramento juntos) —, mas nenhum documento cobria o HEMORR2HAGES, que é historicamente o primeiro dos quatro e o que mais aparece em estudo comparativo como contraponto ao HAS-BLED. Fecha a lacuna e serve de base para comparar os quatro."
---

# Escore HEMORR2HAGES — risco de sangramento maior em fibrilação atrial anticoagulada

## Origem
O HEMORR2HAGES nasceu do National Registry of Atrial Fibrillation (NRAF), coorte de 3.791 beneficiários do Medicare com fibrilação atrial, publicada por Gage BF et al. em 2006 no American Heart Journal. É **anterior ao HAS-BLED** (2010) e ao ATRIA e ORBIT (ambos posteriores) — o primeiro esquema de classificação clínica desenhado especificamente para estimar sangramento maior em paciente anticoagulado por FA, num momento em que a varfarina era praticamente a única opção terapêutica disponível. O artigo comparou o esquema novo contra classificações de risco já existentes na época e mostrou capacidade discriminativa superior a elas, com estatística c de 0,67.

## O que o nome descreve
HEMORR2HAGES é um acrônimo mnemônico em que cada letra corresponde a um fator de risco, com o "R2" sinalizando que aquele componente vale o dobro dos demais:

- **H** — Doença **h**epática ou renal (**um único item**, não dois — hepatopatia e nefropatia somam apenas 1 ponto juntas, ao contrário de escores posteriores que as separam)
- **E** — Abuso de **e**tanol
- **M** — História de **m**alignidade
- **O** — Idade avançada (**o**lder), acima de 75 anos
- **R** — Contagem ou função plaquetária **r**eduzida
- **R2** — **R**essangramento — história de sangramento prévio, **único componente que vale 2 pontos**, todos os outros valem 1
- **H** — **H**ipertensão não controlada
- **A** — **A**nemia
- **G** — Fatores **g**enéticos (o artigo original cita especificamente polimorfismos do CYP2C9, relacionados ao metabolismo da varfarina)
- **E** — Risco **e**xcessivo de queda
- **S** — **S**troke (AVC prévio)

Somando os dez componentes de 1 ponto mais o de ressangramento com 2 pontos, o escore total varia de **0 a 12**.

## O que o escore estima
Taxa de sangramento maior por 100 pacientes-ano em uso de varfarina, crescente e não linear conforme a pontuação. No artigo de derivação: **1,9** para escore 0, **2,5** para 1 ponto, **5,3** para 2 pontos, **8,4** para 3 pontos, **10,4** para 4 pontos e **12,3** para 5 pontos ou mais. O salto mais expressivo está entre 1 e 2 pontos — mais que dobra a taxa —, o que sugere que já o segundo fator de risco presente muda de forma relevante a categoria de vigilância do paciente.

## Categorias de variáveis
Diferente de escores puramente hemodinâmicos, o HEMORR2HAGES mistura três tipos de informação clínica: **doença de órgão-alvo já estabelecida** (hepatopatia, nefropatia, malignidade, anemia), **hábito e exposição** (etanol, fatores farmacogenéticos ligados ao próprio anticoagulante) e **risco físico e funcional do paciente idoso** (queda, plaquetopenia, AVC prévio). Essa mistura é o que torna o escore mais trabalhoso de aplicar à beira do leito do que o HAS-BLED, que se concentra em variáveis clínicas e laboratoriais objetivas.

## Como se compara ao HAS-BLED, já cadastrado nesta base
O HAS-BLED (Pisters et al., 2010) tem 9 itens e escore máximo de 9, com cada componente valendo exatamente 1 ponto — desenho deliberadamente mais simples, e é hoje o escore citado pela diretriz ESC 2024 de fibrilação atrial. O HEMORR2HAGES tem mais componentes (12 no total de pontos possíveis), inclui um item de peso duplo e traz uma variável — fatores genéticos — que na prática clínica corrente **quase nunca é obtida**, porque genotipagem de CYP2C9 não é exame de rotina, mesmo em serviço que ainda usa varfarina. Estudos de validação comparando os dois esquemas de forma direta, em populações mais recentes, tendem a favorecer o HAS-BLED em capacidade discriminativa e em praticidade de aplicação — o HEMORR2HAGES foi construído numa época em que os anticoagulantes de ação direta (DOAC) não existiam, e sua coorte de derivação era 100% de usuários de varfarina.

## Limitações do próprio desenho
Duas críticas recorrentes ao HEMORR2HAGES, ambas decorrentes de como os componentes foram agrupados: primeiro, **agrupar hepatopatia e nefropatia num único ponto** obscurece o peso real de cada uma — um paciente com doença renal terminal e outro com hepatopatia leve recebem a mesma pontuação nesse item, apesar de o risco de sangramento ser bem diferente entre os dois cenários. Segundo, **"risco excessivo de queda" é um julgamento subjetivo**, sem corte operacional definido no artigo original, o que introduz variabilidade entre quem aplica o escore.

## Armadilhas clínicas
- **Não reproduza a fórmula de regressão** deste escore — o HEMORR2HAGES é soma direta de pontos, não regressão logística, mas seu detalhamento numérico completo (tabelas de subgrupo, intervalos de confiança por componente) está no artigo original e não foi transcrito aqui: quem precisar do detalhamento completo deve consultar Gage et al., Am Heart J 2006;151(3):713-719.
- **O item "fatores genéticos" não deve ser deixado em branco por padrão sem registro** — se a genotipagem não foi feita, o correto é considerar o item ausente/zero explicitamente, e não simplesmente ignorá-lo, porque isso muda a interpretação de "risco não avaliado" para "risco avaliado e ausente".
- **Escore de sangramento alto nunca é motivo isolado para negar ou suspender anticoagulação** em paciente com indicação clara — o mesmo princípio já registrado no documento de HAS-BLED desta biblioteca vale aqui: a função do escore é identificar o que é modificável (hipertensão não controlada, etilismo, anemia a corrigir) e calibrar a frequência de acompanhamento, não excluir o paciente do tratamento.
- **A coorte de derivação é inteiramente de usuários de varfarina em beneficiários do Medicare.** Extrapolar diretamente para paciente jovem, para populações fora dos Estados Unidos ou para quem usa DOAC deve ser feito com cautela — nenhuma dessas situações foi objeto do estudo original.
- **VERIFICAÇÃO HUMANA NECESSÁRIA**: o artigo original (Gage BF et al., Am Heart J 2006;151(3):713-719, DOI 10.1016/j.ahj.2005.04.017, PMID 16504638, confirmado via PubMed) **não contém, no resumo oficial indexado no PubMed, nenhum corte de pontuação associado a uma recomendação explícita de conduta** — nem um valor a partir do qual os autores sugiram reavaliação obrigatória, nem uma estratificação categórica formal (por exemplo, "baixo/intermediário/alto risco"). O resumo relata apenas a tabela de incidência de sangramento por ponto (0 a ≥5), já registrada acima, e conclui de forma genérica que o escore "pode... auxiliar no manejo da terapia antitrombótica", sem especificar como. **O texto completo não pôde ser lido nesta sessão**: o artigo está atrás de paywall da Elsevier (`sciencedirect.com`, HTTP 403) e não tem cópia de acesso aberto em nenhuma fonte legítima verificada — Unpaywall (`is_oa: false`, nenhum `oa_location`) e Semantic Scholar (`isOpenAccess: false`, PDF fechado) confirmam ausência de versão aberta, e o `elink` do PubMed mostra que o PMID **não** está depositado no PMC (só aparece como referência citada por outros artigos, não como texto próprio indexado). Diante disso, **a ausência de corte formal de conduta no resumo é tratada como achado da própria fonte, não como lacuna de busca** — a busca foi completa dentro do que está abertamente acessível. O que permanece genuinamente não verificado, e por isso a marcação segue de pé, é se a seção de Discussão do artigo (não incluída no resumo) propõe informalmente algum ponto de corte sem tê-lo formalizado como resultado — isso só se resolve com acesso pago ao American Heart Journal ou com alguém abrindo o PDF integral.
  **Reconferência independente em 02/08/2026, sem novo resultado que mude a conclusão acima, registrada para não repetir a mesma busca:** o abstract foi lido de novo, na íntegra e verbatim, direto da página do PubMed — confirma que não há categoria de risco nem ponto de corte de conduta, só a tabela de incidência por pontuação já transcrita neste documento. `Unpaywall`, `Semantic Scholar` e o `elink` do PubMed foram reconsultados de forma independente (não reaproveitando a checagem anterior) e devolveram o mesmo resultado: acesso fechado, sem cópia aberta, sem depósito de texto completo no PMC. Duas calculadoras de terceiros com prática de citar fonte primária (MDCalc e practical-haemostasis) foram conferidas especificamente atrás de uma estratificação "baixo/intermediário/alto risco" atribuída a Gage et al. — **nenhuma das duas apresenta essa categorização**; ambas mostram só a mesma tabela de incidência por ponto do artigo original, sem cortes de conduta. Isso não resolve a lacuna (a Discussão do artigo continua ilegível nesta sessão), mas é evidência adicional, de duas fontes independentes que normalmente citariam a origem se ela existisse publicamente, de que tal estratificação formal não circula na literatura secundária confiável — reforça, em vez de contradizer, a leitura já registrada acima. Uma estratificação "0-1 baixo / 2-3 intermediário / 4-12 alto" aparece em resumos de busca automatizada de origem não rastreável (sem citação à fonte primária) e **não foi incorporada a este documento** por não atender à régua de fonte verificável desta biblioteca.

## Fonte
Gage BF et al. Am Heart J. 2006;151(3):713-719 (artigo de derivação e única fonte primária usada neste documento).
