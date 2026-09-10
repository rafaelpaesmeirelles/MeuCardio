# Revisão cruzada independente — FA e palpitações — 09/09/2026

Revisor: agente da frente HAS, diferente do autor. Revisados integralmente os quatro registros em round2/fa/{casos-clinicos,checklists,material-paciente}.json. Sem edição dos arquivos de autoria. Revisão clínica assistida por IA; não representa validação humana. Schema/posologia e resolução final dos links sob validação da coordenação.

## Veredito por slug

| Slug | Veredito | Fundamentação e ajustes |
|---|---|---|
| palpitacoes-dois-tipos-de-sintoma-e-correlacao-parcial-no-holter | Aprovável sem ajuste clínico obrigatório | Enunciado distingue claramente dois fenótipos, exclui sinais de risco imediato relevantes e informa ausência da crise longa durante registro. Resposta C inequívoca, índice 2. Não encerra investigação por correlação parcial, não diagnostica ansiedade por exclusão indevida e não prescreve antiarrítmico empírico. Monitorização externa mais longa condiz com crises a cada 2–3 semanas. |
| fa-cardioversao-eletiva-omissoes-doac-reveladas-na-reconciliacao | Aprovável sem ajuste obrigatório; conferência documental concluída | Paciente estável, FA persistente há seis semanas e quatro tomadas omitidas com ausência de imagem tornam inadequada cardioversão eletiva naquele dia. Resposta A inequívoca, índice 0. Não propõe compensação por dose extra; mantém anticoagulação periprocedimento e explica continuidade posterior pelo risco. CHA2DS2-VASc 3 é aritmeticamente correto: 1 idade + 1 HAS + 1 DM. Referencial AHA/ACC 2023 está explicitamente delimitado, sem confundir seu corte de 48 horas com outro referencial. Nenhum dado do caso se aproxima de uma zona limítrofe temporal. |
| retorno-das-palpitacoes-auditoria-da-correlacao-sintoma-ritmo | Aprovável sem ajuste clínico obrigatório | Diferencia ausência de captura, captura parcial, sintoma com ritmo sinusal e arritmia incidental. Inclui qualidade do traçado, avaliação própria de achados assintomáticos e adaptação da duração do registro. Não confunde ausência de sintomas com ausência de doença. Instabilidade leva à emergência. |
| diario-de-palpitacoes-e-retorno-do-holter-como-participar | Aprovável sem ajuste clínico obrigatório | Linguagem acessível, exemplo explicitamente fictício, horários/contexto/duração úteis. Recomenda seguir instruções próprias do aparelho e não mudar tratamento para provocar evento. Explicita emergência por sintomas de alarme e não esperar devolução do monitor. Não promete captura, diagnóstico ou monitorização de segurança em tempo real. |

## Verificação independente de fontes

O consenso original ISHNE-HRS 2017 foi acessado e conferido, especialmente seleção de dispositivo e seção de palpitações: frequência e natureza dos episódios orientam a janela. O raciocínio dos dois itens profissionais de palpitações corresponde a esse princípio; não exige que uma extrassístole capturada explique episódios de outra natureza. Fonte: https://pmc.ncbi.nlm.nih.gov/articles/PMC6931745/ .

A orientação AHA sobre Holter foi conferida: diário de sintomas e atividade permite comparação com registro; data de revisão 25/02/2025 confirma a referência. AHA Event Recorder também foi acessada. Fontes: https://www.heart.org/en/health-topics/arrhythmia/symptoms-diagnosis--monitoring-of-arrhythmia/holter-monitor e https://www.heart.org/en/health-topics/arrhythmia/symptoms-diagnosis--monitoring-of-arrhythmia/cardiac-event-recorder . A formulação no material é original e não copia instruções específicas de um modelo de monitor.

Histórico da primeira consulta: a URL PMC11104284 da diretriz de FA retornou verificação de navegador nesta revisão independente; o espelho PMC11095842 também, e o artigo oficial AHA retornou 403. Não afirmo leitura independente das tabelas de classe/nível da diretriz nesta rodada. Os rótulos I/B-R para preparo e I/B-NR para quatro semanas devem permanecer associados à conferência primária do autor, que a coordenação está recuperando. Não foi detectada contradição clínica na formulação. O relatório r2-fa-audit.md ainda não existia no momento desta primeira gravação do parecer.

## Sugestão opcional, sem bloquear

No caso de cardioversão, pode-se explicitar que a anticoagulação prolongada se mantém conforme risco mesmo se houver restauração do ritmo sinusal. O texto já indica continuidade de longo prazo, portanto a ausência dessa frase não torna a resposta insegura. Não é necessário adicionar comparação ESC/AHA ao enunciado, pois ele já delimita a fonte e dura seis semanas.

## Resultado

Nenhum bloqueio clínico ou documental remanescente nos quatro itens, após a conferência complementar abaixo. Não alterar status para revisão humana. Revisão cruzada assistida pode ser documentada após integração pela coordenação.

## Conferência complementar encerrada

Lidos r2-fa-audit.md e os caches temporários round2/aha-source.txt e round2/consensus-source.txt. O cache primário obtido pelo autor permite conferir diretamente a tabela 8.2.1 da AHA/ACC2023: classe I, B-R no preparo para cardioversão eletiva; classe I, B-NR para continuidade por ao menos quatro semanas após o procedimento. A informação de classe/nível dos itens corresponde à fonte. Trata-se de leitura independente do trecho primário por este revisor, usando material compartilhado pelo autor, não de nova obtenção independente da página. Ressalva documental resolvida. Os caches integrais devem continuar fora da publicação e do commit.
