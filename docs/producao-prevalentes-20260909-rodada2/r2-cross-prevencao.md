# Revisão cruzada — prevenção/lipídios e DM2 — 09/09/2026

Revisor: agente da frente IC, independente da autoria destes quatro registros. Revisão assistida por IA; não representa revisão humana. Não foram editados os arquivos de autoria.

## Resultado

Os dois casos e o material ao paciente são clinicamente coerentes e têm respostas corretas únicas. O checklist exige **uma correção localizada de escopo** antes de marcar como revisado: o item sobre ALT deve especificar estatina, pois a afirmação genérica se estende indevidamente a fibratos.

Não identifiquei bloqueio clínico grave, dose perigosa ou erro de aritmética. Os quatro registros permanecem pendentes de consolidação pela coordenação.

## Correção necessária

Arquivo `round2/prevencao/checklists.json`, item `ret-lip-enzimas`.

Problema: “evitada repetição indefinida de CK/ALT no usuário estável assintomático” é amplo demais em um checklist de dislipidemia que admite diferentes hipolipemiantes. A apresentação oficial ESC/EAS 2019, página 125, diferencia o acompanhamento de estatina daquele de fibratos.

Substituição proposta para `texto`:

> CK e ALT solicitadas conforme indicação clínica e fase de início/ajuste; no usuário estável assintomático de estatina, evitada monitorização seriada de CK e ALT sem indicação. Para fibratos e outros hipolipemiantes, seguido o monitoramento específico do medicamento.

Fonte diretamente conferida: [tabelas oficiais ESC/EAS 2019, páginas 124–128](https://eas-society.org/wp-content/uploads/2022/11/2019_dyslipidaemias_guidelin.pdf). O restante da orientação sobre exames e o intervalo lipídico de 8 ±4 semanas estão compatíveis com esse referencial.

## Avaliação por registro

| Recurso | Parecer |
|---|---|
| `primeiro-lipidograma-triglicerideos-altos-ldl-calculado-nao-interpretavel` | Correto. TG 460 e Friedewald inválido para decisão; conta do LDL 114 e não-HDL 206 corretas. Jejum não é obrigatório universalmente, mas repetir com preparo é pertinente neste resultado. Não diagnostica pancreatite por laboratório isolado. Não inicia tratamento sem estratificar. |
| `dm2-drc-queda-inicial-tfge-apos-isglt2-retorno-com-seguranca` | Correto. DM2/DRC documentadas ao longo de meses; declínio 20,7% após início, sem dados de hipovolemia/intercorrência. Continuidade de 10 mg, avaliação da tendência e plano de pausa em doença/jejum são adequados. Não promete que toda queda seja benigna nem exige exames extras universais. |
| `preparar-retorno-colesterol-exames-remedios-e-duvidas` | Apto. Linguagem acessível, preparo individual, reconciliação e contato antecipado. Sem orientação de automedicação ou suspensão por melhora. |
| `retorno-dislipidemia-uso-real-resposta-meta-e-continuidade` | Apto após restringir o item ALT/CK ao contexto apropriado. Fórmula de redução adicional usa o denominador atual corretamente e é identificada como planejamento, não promessa farmacológica. Não mistura metas entre diretrizes. |

## Fontes primárias verificadas na revisão

- [KDIGO 2024](https://kdigo.org/wp-content/uploads/2024/03/KDIGO-2024-CKD-Guideline.pdf), página 43: recomendação 3.7.1, nível 1A em DM2/DRC/TFGe ≥20, e pontos de prática de pausa/declínio inicial. O texto da autoria diferencia corretamente recomendação graduada e ponto de prática. A UACR abaixo de 200 mg/g não invalida a recomendação específica para DM2 com DRC; não se alegou que o paciente reproduza os critérios do EMPA-KIDNEY.
- [Consenso EAS/EFLM, registro institucional dos autores](https://research.regionh.dk/en/publications/fasting-is-not-routinely-required-for-determination-of-a-lipid-pr/): confirmado o limiar >440 mg/dL sem jejum para considerar repetição. Acesso DOI/PMC do estudo analítico adicional não foi suficiente nesta revisão; a conduta não depende de adotar a equação nova de Sampson.
- [ESC/EAS 2019, apresentação oficial](https://eas-society.org/wp-content/uploads/2022/11/2019_dyslipidaemias_guidelin.pdf): páginas 124–128 e diferenciação do monitoramento hepático que motivou a correção.
- [AHA 2026, síntese oficial](https://professional.heart.org/en/science-news/2026-guideline-on-the-management-of-dyslipidemia/top-things-to-know): metas e redução percentual individualizadas; publicação/atualização de 13/03/2026 confirmada. Os registros não inventam alvos próprios nem atribuem essa publicação à ESC/SBC.

## Verificações estruturais e integração

JSON parseado; chaves superiores idênticas aos exemplos; slugs novos nos catálogos; casos com quatro opções e índices 1/2; status pendente. Documento pai do material/checklist existe na produção anterior. Seções do checklist correspondem aos títulos reais do documento. A auditoria autoral fornece as relações de documentos/exames/fármacos/trilhas; reciprocidade e funcionamento da navegação precisam ser verificados pela integração, não são presumidos desta leitura clínica.

## Refinamento opcional

No material, o primeiro alerta poderia trocar “fraqueza muscular importante com urina muito escura ou redução da urina” por “fraqueza muscular importante, urina muito escura ou redução importante da urina”, para deixar mais claro que não é necessário apresentar todos os sinais juntos. Não altera o gabarito nem constitui impedimento clínico grave.
