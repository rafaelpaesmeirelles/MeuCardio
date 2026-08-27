---
title: "Classificação SCAI de Estágios do Choque Cardiogênico"
slug: classificacao-scai-de-estagios-do-choque-cardiogenico
theme: "Terapia intensiva"
kind: protocolo
review_status: revisado
source_refs: ["SCAI clinical expert consensus statement on the classification of cardiogenic shock · SCAI/ACC/AHA/SCCM/STS · 2019 · 10.1002/ccd.28329", "Criteria for Defining Stages of Cardiogenic Shock Severity · JACC · 2022 · 10.1016/j.jacc.2022.04.049", "Proposta 2026 SCAI SHOCK Classification Expert Consensus Update · consulta pública SCAI encerrada em 27/07/2026; não adotada aqui como padrão final · status revalidado em 27/08/2026", "SCAI SHOCK Bedside Checklist 2022 — scai.org, endossado por ACC/ACEP/AHA/ESC-ACVC/ISHLT/SCCM/STS", "Naidu SS et al. SCAI SHOCK Stage Classification Expert Consensus Update. J Soc Cardiovasc Angiogr Interv. 2022. doi:10.1016/j.jscai.2021.100008."]
legacy_source: "Fusão de dois documentos sobre a mesma classificação, na mesma pasta, com zero seções em comum entre 7 e 11: este e choque-cardiogenico-classificacao-scai-shock-complemento.md. O absorvido trazia dois defeitos de forma que o desqualificavam como base: dicionário de Python serializado vazado no corpo do texto, em vez de markdown, e uma referência a 'thai source' deixada dentro de um critério clínico. O conteúdo clínico dele foi preservado aqui."
---

# Classificação SCAI de Estágios do Choque Cardiogênico

## Origem
Sistema desenvolvido por grupo multidisciplinar de especialistas convocado pela Society for Cardiovascular Angiography and Interventions (SCAI), com representantes de cardiologia intervencionista, IC avançada, cardiologia não invasiva, medicina de emergência, terapia intensiva e enfermagem cardíaca; endossado por ACC, AHA, SCCM e STS em abril de 2019

## Justificativa
Apesar do desenvolvimento de várias opções de suporte circulatório mecânico percutâneo, o desfecho do choque cardiogênico complicando infarto do miocárdio não mudou apreciavelmente nos últimos 30 anos; ficou claro que existem graus variáveis de choque cardiogênico, mas não havia esquema de classificação robusto para categorizar esse estado de doença

## Estagios

- **A em risco**: Paciente 'em risco' para choque cardiogênico — não apresentando atualmente sinais ou sintomas de choque, mas em risco de desenvolvê-lo (ex.: IAM extenso ou IC descompensada prévia)
- **B inicio**: Choque 'iniciando' (beginning) — evidência de instabilidade hemodinâmica relativa (hipotensão ou taquicardia) sem hipoperfusão
- **C classico**: Choque cardiogênico 'clássico' — hipoperfusão presente, requerendo intervenção inicial (farmacológica ou mecânica) além de reposição volêmica para restaurar perfusão
- **D deterioracao**: Choque 'deteriorando' (deteriorating) — paciente que não respondeu ao conjunto inicial de intervenções escolhidas, permanecendo instável e hipoperfundido após pelo menos 30 minutos de observação
- **E extremis**: Paciente 'in extremis' — altamente instável, frequentemente com colapso cardiovascular, geralmente em parada cardíaca em curso ou suporte circulatório mecânico múltiplo com suporte de RCP
- **criterio diferenciador B C**: Diferença entre estágios B e C é a presença de hipoperfusão, presente nos estágios C e superiores
- **fonte**: SCAI Consensus Statement 2019, com critérios numéricos formalizados na atualização de 2022

## Criterios numericos por estagio (checklist oficial SCAI 2022)

Cada estágio combina exame físico, marcador bioquímico e hemodinâmica. Não é preciso ter todos os itens de uma linha — a classificação usa o padrão predominante.

| Estágio | Exame físico | Bioquímica | Hemodinâmica |
|---|---|---|---|
| **A** | Bem perfundido, pulsos fortes, mentação normal | Lactato normal, função renal normal | PAS > 100 mmHg, IC > 2,5 (se agudo), PVC < 10, POAP < 15 |
| **B** | Turgência jugular elevada, ainda bem perfundido, estertores | Lactato normal, disfunção renal mínima, BNP elevado | PAS < 90 mmHg **ou** PAM < 60 **ou** queda > 30 mmHg da PA basal; FC > 100 bpm |
| **C** | Sobrecarga volêmica, alteração de mentação, extremidades frias, estertores extensos, diurese < 30 mL/h | Lactato > 2 mmol/L, creatinina 1,5× basal ou queda de TFG > 50%, transaminases elevadas | IC < 2,2 (se hemodinâmica invasiva disponível — fortemente recomendada), POAP > 15 |
| **D** | Qualquer achado do C, sem melhora apesar do tratamento inicial | Lactato persistentemente > 2 e subindo, função renal e hepática piorando | Necessidade de doses crescentes ou de mais de um vasopressor, ou adição de dispositivo de suporte circulatório mecânico |
| **E** | Inconsciente, quase sem pulso, colapso cardíaco, múltiplas desfibrilações | Lactato > 8 mmol/L, acidose grave (pH < 7,2) | Hipotensão profunda apesar de suporte hemodinâmico máximo; RCP em curso |

**Modificador "+A" (Arrest)**: reservado à parada com potencial lesão cerebral
anóxica — por exemplo, coma/GCS <9 ou ausência de resposta a comandos após RCE —
e pode ser acrescentado ao estágio hemodinâmico (ex.: "C+A"). Uma desfibrilação
breve, sem RCP relevante e com função neurológica normal, não basta para aplicar o
modificador.

Fonte: SCAI SHOCK Bedside Checklist 2022, documento endossado por ACC, ACEP, AHA, ESC/ACVC, ISHLT, SCCM e STS.

**Proximidade temática, não regra de estadiamento:** quando houver acidose
metabólica já estabelecida, a [calculadora de compensação respiratória e ânion gap
na UCO](/calculadoras/acidose-metabolica-winter-anion-gap-uco) pode
organizar a gasometria. Seu resultado não define estágio SCAI nem a etiologia do
choque; mantém-se apenas como apoio contextual ao pH registrado no estágio.

## Validacao criterios objetivos
Estudo subsequente (2022) desenvolveu critérios formais objetivos para cada estágio, usando parâmetros de pressão arterial sistólica, nível de lactato, alanina transaminase (ALT) e pH sistêmico, associados de forma significativa à mortalidade em coorte de 3.455 pacientes (registro CS Working Group, 2016-2021)

## Dados mortalidade coorte validacao
Mortalidade geral de 35% na coorte total, mais elevada entre pacientes com infarto do miocárdio, parada cardíaca extra-hospitalar, e tratamento com número crescente de fármacos e dispositivos. Estágio inicial e estágio máximo alcançado foram significativamente associados à mortalidade

## Etiologia predominante coorte
Choque cardiogênico causado por insuficiência cardíaca (52%) ou infarto do miocárdio (32%)

## Trajetoria clinica
Estágio basal mais baixo foi associado a maior incidência de escalonamento de estágio e menor tempo até atingir o estágio máximo, reforçando importância de reavaliação dinâmica contínua

## Aplicabilidade
Sistema simples e clinicamente aplicável ao longo de todo o espectro assistencial, desde provedores pré-hospitalares até equipe de terapia intensiva

## Atualizacao 2026
A SCAI submeteu uma proposta de atualização 2026 a consulta pública, com prazo de
comentários encerrado em 27 de julho de 2026. Na verificação de 27 de agosto de
2026, ela ainda não constituía consenso final publicado/endossado; por isso este
conteúdo e o assistente operacional permanecem ancorados na atualização
multissocietária publicada em 2022.

## Limitacoes
Sistema original careceu de critérios uniformes definindo cada estágio até a publicação de critérios formais objetivos em 2022; utilidade clínica e implicações prognósticas potenciais continuam sendo validadas em estudos adicionais

## Modificador A: parada cardiaca
O sufixo **+A** pode ser acrescentado ao estágio hemodinâmico quando a parada
traz potencial lesão cerebral anóxica. O consenso 2022 propõe como marcadores
práticos coma/GCS <9 ou ausência de resposta motora a comandos após RCE. Episódio
breve, rapidamente revertido e com recuperação neurológica não recebe o
modificador automaticamente.

## Relevancia prognostica
A mortalidade cresce progressivamente de A para E. Os estágios D e E sinalizam necessidade de suporte circulatório mecânico avançado e pior prognóstico.

## Suporte circulatorio mecanico
Balão intra-aórtico, dispositivo percutâneo de fluxo axial e ECMO venoarterial são as principais opções, consideradas progressivamente a partir do estágio C, com uso mais frequente em D e praticamente incontornável em E.

## Aplicacao em cirurgia cardiaca
Nos pacientes cirúrgicos, os estágios A a D concentram 66 a 78% de procedimentos eletivos, contra apenas 31% no estágio E — o choque extremo se associa a proporção muito maior de cirurgia de urgência ou emergência.

## Divergencia resolvida no criterio bioquimico do estagio C
**Resolvido em 30/07/2026, conferindo diretamente o checklist oficial** (SCAI SHOCK Bedside Checklist 2022, scai.org, texto completo lido). Os dois documentos consolidados aqui discordavam do corte de creatinina do estágio C: um exigia creatinina dobrada, o outro 1,5 vez o basal. **O checklist oficial confirma 1,5× o basal (ou queda de TFG > 50%)** — a tabela acima já estava certa, a divergência era do documento fundido que exigia dobrada, não da tabela publicada.

O mesmo par divergia no lactato do estágio E, com um deles registrando "≥8 mmol/L" e anotando entre parênteses que outra fonte citava ≥5. **O checklist oficial confirma lactato > 8 mmol/L no estágio E** — a anotação entre parênteses sobre "≥5" não corresponde a nenhum critério oficial de nenhum estágio (o lactato > 2 mmol/L pertence ao estágio C, não é alternativa ao > 8 do estágio E) e foi removida.
