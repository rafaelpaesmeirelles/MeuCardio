---
title: "Escore VTE-BLEED: Risco de Sangramento sob Anticoagulação por TEV"
slug: escore-vte-bleed-risco-de-sangramento-sob-anticoagulacao-por-tev
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Klok FA, Hösel V, Clemens A, Yollo WD, Tilke C, Schulman S, Lankeit M, Konstantinides SV. Prediction of bleeding events in patients with venous thromboembolism on stable anticoagulation treatment. Eur Respir J. 2016;48(5):1369-1376. DOI: 10.1183/13993003.00280-2016. PMID: 27471209 — ARTIGO ORIGINAL do escore. ATENÇÃO: este registro NÃO tem resumo no PubMed e o texto completo devolve 403 em publications.ersnet.org; a tabela de pontos abaixo foi obtida de fontes secundárias que reproduzem o escore original (ver observação de procedência no corpo do documento)", "Nishimoto Y, Yamashita Y, Morimoto T, Saga S, Amano H, Takase T, et al; COMMAND VTE Registry Investigators. Validation of the VTE-BLEED score's long-term performance for major bleeding in patients with venous thromboembolisms: From the COMMAND VTE registry. J Thromb Haemost. 2020;18(3):624-632. DOI: 10.1111/jth.14691. PMID: 31785073 — validação externa em coorte NÃO selecionada, 2.124 pacientes, 29 centros no Japão. Esta fonte foi lida no PubMed e é a origem dos números de desfecho citados"]
legacy_source: "Documento novo, escrito em 31/07/2026, fechando um item que ficou explicitamente pendente do ciclo anterior por não localização segura do artigo original. Completa o par de escores de TEV da pasta: o DASH estima recorrência (o benefício de manter anticoagulação) e o VTE-BLEED estima sangramento (o custo) — os dois lados da mesma decisão."
---

# Escore VTE-BLEED: Risco de Sangramento sob Anticoagulação por TEV

## O lado que faltava da balança
Decidir por quanto tempo anticoagular após tromboembolismo venoso exige comparar **duas estimativas**: o risco de **recorrência** se parar, e o risco de **sangramento** se continuar. O escore **DASH** cobre o primeiro — ver `escore-dash-risco-de-recorrencia-apos-tev-nao-provocado.md`, nesta mesma pasta. O **VTE-BLEED** cobre o segundo.

Note o recorte: o escore foi desenhado para **pacientes sob anticoagulação estável**, ou seja, para a fase de manutenção — depois da fase aguda, que tem risco hemorrágico próprio e maior.

## Componentes e pontuacao
| Variável | Pontos |
|---|---|
| **Câncer ativo** | **2** |
| **Homem com hipertensão arterial não controlada** | **1** |
| **Anemia** | **1,5** |
| **História de sangramento** | **1,5** |
| **Idade ≥ 60 anos** | **1,5** |
| **Disfunção renal** | **1,5** |

**Ponto de corte: escore < 2 = baixo risco · escore ≥ 2 = alto risco de sangramento.**

**Definições operacionais** que acompanham o escore original:
- **Câncer ativo**: câncer diagnosticado nos 6 meses anteriores ao diagnóstico do TEV (excluindo carcinoma basocelular ou espinocelular de pele), câncer recorrente ou progressivo recente, ou qualquer câncer que exigiu tratamento antineoplásico nos 6 meses anteriores ao TEV
- **Homem com hipertensão não controlada**: **pressão sistólica ≥ 140 mmHg** no basal
- **Anemia**: hemoglobina **< 13 g/dL em homens** ou **< 12 g/dL em mulheres**

> ⚠️ **Procedência desta tabela — leia antes de usar em decisão crítica.** O **artigo original
> (PMID 27471209) não tem resumo no PubMed**, e o texto completo devolve **403**. A tabela de pontos
> e as definições acima foram obtidas de **fontes secundárias que reproduzem o escore original**, e
> **não foram lidas diretamente no artigo**. O que **foi** verificado em fonte primária lida no
> PubMed é o **ponto de corte ≥ 2** e os desfechos da validação COMMAND VTE, abaixo — e o corte
> obtido das fontes secundárias **coincide** com o da validação, o que corrobora a tabela.
> **Antes de usar o escore em decisão de peso, confira os pesos contra o artigo original.**

## Validacao externa em coorte nao selecionada
Nishimoto Y et al., J Thromb Haemost. 2020;18(3):624-632 (PMID 31785073). É a validação mais útil, porque testa o escore **fora do ambiente de ensaio clínico**:
- **Registro COMMAND VTE**, multicêntrico e retrospectivo, **29 centros no Japão**, com pacientes consecutivos com TEV agudo sintomático
- **2.124 pacientes** em anticoagulação prolongada além de 30 dias — **95% em primeiro episódio de TEV** e **51% com TEV não provocado**
- Divididos em **1.445 (68%) com escore ≥ 2** (alto risco) e **679 (32%) com escore < 2** (baixo risco)
- Seguimento mediano de **672 dias**; **121 sangramentos maiores**

**Resultado:**
- **Incidência cumulativa de sangramento maior em 5 anos (além dos 30 dias): 13,2% no alto risco vs. 5,4% no baixo risco** (p < 0,001)
- As curvas de função de risco mostraram que **o risco do grupo de alto risco permaneceu consistentemente maior ao longo do tempo** — ou seja, a capacidade preditiva **se sustenta a longo prazo**, e não só nos primeiros meses

**Conclusão dos autores:** num registro de mundo real, o VTE-BLEED teve capacidade preditiva de longo prazo para identificar pacientes de alto risco de sangramento maior durante anticoagulação prolongada, o que **pode ser útil para determinar a duração ótima da anticoagulação** em cada paciente.

## Como usar junto com o DASH
A decisão de manter ou parar a anticoagulação após TEV **precisa dos dois números**:

| | estima | escore |
|---|---|---|
| **Se eu parar**, qual o risco de recorrência? | recorrência | **DASH** |
| **Se eu continuar**, qual o risco de sangramento? | sangramento maior | **VTE-BLEED** |

Repare que o **desequilíbrio da coorte de validação é informativo por si**: **68% dos pacientes ficaram no grupo de alto risco**. O escore não seleciona uma minoria — ele separa um grupo grande com risco cerca de **2,4 vezes maior** (13,2% vs. 5,4% em 5 anos). Isso o torna útil para **graduar**, não para excluir.

## Armadilhas clinicas
- **Usar os pesos deste documento em decisão crítica sem conferir o artigo original** — a tabela veio de fonte secundária, e isso está declarado acima
- **Aplicar na fase aguda do TEV** — o escore foi desenhado para anticoagulação **estável**, de manutenção
- **Decidir só pelo VTE-BLEED** — ele estima um lado; o outro é a recorrência, e para isso existe o DASH
- **Tratar "alto risco" como contraindicação a anticoagular** — 68% da coorte de validação caiu nessa faixa; o escore gradua risco, não proíbe tratamento
- **Esquecer que o item de hipertensão é específico de homens** — é assim no escore, e não é erro de transcrição
- **Extrapolar a incidência absoluta de 13,2% para qualquer população** — vem de um registro japonês; a magnitude relativa transporta melhor que a absoluta
