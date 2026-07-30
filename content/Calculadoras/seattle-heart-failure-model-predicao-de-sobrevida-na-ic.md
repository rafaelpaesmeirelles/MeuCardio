---
title: "Seattle Heart Failure Model: Predição de Sobrevida na IC"
slug: seattle-heart-failure-model-predicao-de-sobrevida-na-ic
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Levy WC, Mozaffarian D, Linker DT, et al. The Seattle Heart Failure Model: prediction of survival in heart failure. Circulation. 2006;113(11):1424-1433. DOI: 10.1161/CIRCULATIONAHA.105.584102. PMID: 16534009"]
legacy_source: "Documento novo — as calculadoras já existentes cobrem risco em SCA (TIMI, GRACE 2.0), sangramento em FA (HAS-BLED), TEV (PESI/sPESI, Wells), mortalidade cirúrgica (EuroSCORE II, STS) e complexidade coronariana (SYNTAX), mas não estimativa de sobrevida especificamente em insuficiência cardíaca — lacuna real, dado que a mortalidade anual da IC varia de 5% a 75% conforme o perfil do paciente."
---

# Seattle Heart Failure Model: Predição de Sobrevida na IC

## Aplicacao
A mortalidade anual da insuficiência cardíaca (IC) varia de **5% a 75%** conforme o perfil do paciente — faixa enorme que evidencia a necessidade de uma ferramenta de estratificação de risco individualizada. O Seattle Heart Failure Model foi desenvolvido para prever sobrevida em 1, 2 e 3 anos usando características clínicas, farmacológicas (incluindo dispositivos) e laboratoriais facilmente obtidas na prática.

## O estudo de desenvolvimento e validacao (levy, circulation 2006)
Levy WC et al. Circulation. 2006;113(11):1424-1433 (PMID 16534009). Modelo derivado por regressão de Cox multivariada numa coorte de **1.125 pacientes com IC**. Para medicamentos e dispositivos não disponíveis na base de derivação, razões de risco foram estimadas a partir da literatura publicada. O modelo foi **validado prospectivamente em 5 coortes adicionais**, totalizando **9.942 pacientes com IC e 17.307 pacientes-ano de seguimento**:
- **Precisão excelente**: sobrevida em 1 ano predita vs. real de **73,4% vs. 74,3%** na coorte de derivação, e **90,5% vs. 88,5%**, **86,5% vs. 86,5%**, **83,8% vs. 83,3%**, **90,9% vs. 91,0%**, e **89,6% vs. 86,7%** nas 5 coortes de validação — concordância muito próxima em todas
- **Discriminação por faixa de escore**: sobrevida em 2 anos de **92,8%** para o escore mais baixo, comparada a **88,7%, 77,8%, 58,1%, 29,5% e 10,8%** para escores de 0, 1, 2, 3 e 4, respectivamente — gradiente de risco muito acentuado entre as categorias
- **Área sob a curva ROC geral**: **0,729** (IC95% 0,714-0,744)
- O modelo também permite **estimar o benefício** de acrescentar medicamento ou dispositivo específico ao esquema terapêutico individual do paciente

## Conclusao do proprio estudo
**"O Seattle Heart Failure Model fornece uma estimativa precisa de sobrevida em 1, 2 e 3 anos, usando características clínicas, farmacológicas, de dispositivo e laboratoriais facilmente obtidas."**

## Sintese pratica
O Seattle Heart Failure Model preenche uma lacuna real na avaliação de risco desta biblioteca — nenhuma das calculadoras já registradas estima sobrevida especificamente em insuficiência cardíaca crônica. Sua validação em 5 coortes independentes (quase 10 mil pacientes, mais de 17 mil pacientes-ano) com concordância consistente entre predição e realidade é evidência robusta de generalização. A funcionalidade que mais diferencia este modelo das demais calculadoras de risco já registradas é a capacidade de **estimar o benefício de adicionar uma terapia específica** (medicamento ou dispositivo) ao esquema do paciente individual — útil na consulta de otimização terapêutica, não só na estratificação de risco basal, permitindo mostrar concretamente ao paciente o ganho esperado de sobrevida com uma intervenção proposta.

## Armadilhas clinicas
- Usar o Seattle Heart Failure Model isoladamente para decisões de fim de vida ou elegibilidade a transplante/suporte circulatório mecânico — é ferramenta de estimativa de sobrevida, não substituto de avaliação multidisciplinar completa nessas decisões de alto impacto
- Ignorar que os coeficientes para alguns medicamentos/dispositivos vieram de estimativa da literatura publicada, não da coorte de derivação direta — a precisão desses componentes específicos depende da qualidade dos estudos de origem usados para essa estimativa
- Aplicar o modelo sem atualizar as variáveis clínicas, farmacológicas e laboratoriais do paciente ao longo do tempo — é ferramenta que reflete o estado no momento da avaliação, e mudanças terapêuticas relevantes (novo fármaco, novo dispositivo) devem ser refletidas em nova estimativa
- Tratar a área sob a curva ROC de 0,729 como discriminação excepcionalmente alta — é discriminação adequada e válida, mas não excepcional; a força real deste modelo está mais na calibração (predição próxima da realidade em todas as coortes de validação) que na discriminação isolada
