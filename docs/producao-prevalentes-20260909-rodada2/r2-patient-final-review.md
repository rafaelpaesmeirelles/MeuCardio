# Revisão final de linguagem e segurança — materiais ao paciente — 09/09/2026

Escopo: leitura integral dos seis registros de `round2-records.json` → `new` → `material-paciente`. Revisão assistida de linguagem, autonomia, sinais de alarme e coerência do material destinado ao paciente; sem repetição da pesquisa científica já realizada e sem alteração do arquivo consolidado.

## Parecer

**Dois ajustes pontuais de segurança devem ser aplicados antes do fechamento editorial.** Os demais materiais não apresentam bloqueio identificado neste escopo. Nenhum dos seis oferece posologia nova, dose de resgate, troca de fármaco, suspensão autônoma, automedicação ou desafio de esforço domiciliar. Referências à dose/horário referem-se a registrar a prescrição existente, não a prescrever ao leitor.

### 1. Pós-infarto — urgência de possível melena

Slug: `primeiro-retorno-apos-infarto-leve-remedios-receitas-e-duvidas`

Campo: `sinais_de_alerta[2]`.

Atual: “Sangramento importante, vômito com sangue ou fezes negras acompanhadas de fraqueza ou tontura: atendimento imediato.”

Problema: a conjunção pode fazer o leitor esperar fraqueza/tontura para procurar atendimento por possível melena, especialmente relevante em uso de antitrombóticos. A ausência desses sintomas não afasta hemorragia digestiva.

Substituição proposta:

> Sangramento importante, vômito com sangue ou fezes negras, pegajosas, como piche: procure atendimento imediatamente, mesmo sem fraqueza ou tontura.

Preserva o restante do material, que corretamente não orienta interromper antitrombótico sozinho e direciona o ajuste à equipe assistencial.

### 2. Colesterol — sinais neurológicos alternativos

Slug: `preparar-retorno-colesterol-exames-remedios-e-duvidas`

Campo: `sinais_de_alerta[1]`.

Atual: “Dor forte no peito, falta de ar intensa ou dificuldade súbita para falar e movimentar um lado do corpo: acione o SAMU pelo 192.”

Problema: “falar e movimentar” pode ser interpretado como necessidade de ambos os sinais neurológicos simultaneamente. Um sinal súbito isolado já deve acionar o fluxo de emergência.

Substituição proposta:

> Dor forte no peito, falta de ar intensa, dificuldade súbita para falar ou perda súbita de força em um lado do corpo: acione o SAMU pelo 192.

O outro alerta desse material já está adequado, com fraqueza muscular, urina escura e redução da urina como possibilidades alternativas, sem exigir combinação.

## Demais resultados

| Material | Resultado |
|---|---|
| Troca de remédio da pressão | Receita única, prevenção de duplicidade, não dobrar por conta própria, não acrescentar diurético e alerta para edema unilateral doloroso são claros. Sem bloqueio. |
| Coração/FEVE melhorada | Define fração de ejeção em linguagem acessível, não promete cura nem extrapola TRED-HF para todas as etiologias; alerta e continuidade adequados. Sem bloqueio. |
| Diário de palpitações/Holter | Modelo prático e curto; orienta não modificar tratamento para provocar crise e não aguardar devolução do aparelho diante de alarme. Sem bloqueio. |
| Primeiro retorno após infarto | Segurança de conciliação e de antitrombóticos adequada; aplicar ajuste de melena acima. |
| Retorno do colesterol | Preparo individual do jejum, especialmente no diabetes, e prevenção de suspensão por exame melhor são adequados; aplicar ajuste dos sinais neurológicos acima. |
| Laudos de estenose aórtica | Não induz decisão de operar pelo número nem esforço para testar sintomas; diferencia emergência e antecipação do retorno. Sem bloqueio. |

## Limites e encerramento

O texto científico nas referências pode manter terminologia técnica: não faz parte do comando clínico dirigido ao paciente. Metadados `review_note` distinguem revisão por IA de revisão humana. O material de valvopatia tem repetição editorial nessa nota, sem impacto clínico; pode ser unificado na consolidação.

Parecer não equivale a validação humana, publicação ou comprovação de exibição dos alertas na interface/PDF. Após as duas substituições, não há outro impedimento identificado nesta revisão de linguagem e segurança. Não modifiquei autoria, estado editorial ou conteúdo consolidado.
