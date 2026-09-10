# Revisão independente do Tudo com Tudo — rodada 2

Revisão assistida por IA em 09/09/2026 sobre `round2-production/` e `round2-integration-result.json`. Nenhum catálogo global foi alterado. Escopo: os 24 recursos novos e sua integração documental, editorial e nas oito trilhas afetadas.

## Parecer

**Integração estática consistente, sem órfãos no lote e sem bloqueio clínico identificado nas novas relações.** Os números do relatório de integração foram recalculados a partir dos catálogos e confrontados com `production/`, sem depender somente dos totais declarados.

| Verificação | Resultado observado |
|---|---:|
| Novos casos | 12 |
| Novos materiais ao paciente | 6 |
| Novos checklists | 6 |
| Recursos novos com backlink de documento | 24/24 |
| Recursos novos com vínculo de retorno ao documento pai | 24/24 |
| Documentos pais distintos | 14 |
| Trilhas atualizadas | 8 |
| Etapas adicionadas | 18 |
| Novas relações explícitas doença → recurso | 24 |
| Doenças distintas com destinos novos | 9 |
| Órfãos entre os 24 novos recursos | 0 |
| Divergências de tipo, ausência ou duplicação nas arestas esperadas | 0 |

## Como a reciprocidade foi verificada

- Cada caso está no catálogo `casos-clinicos`, tem retorno ao documento em `explicacao`, e o documento contém link `/casos-clinicos/<slug>`.
- Cada material está no catálogo `material-paciente`, referencia o pai por `documento_slug`, e o pai contém link `/material-paciente/<slug>`.
- Cada checklist está no catálogo `checklists`, referencia o pai por `documento_origem`, e o pai contém link `/checklists/<slug>`.
- Cada relação explícita possui origem e destino correspondentes ao mapeamento, sem tratar material como documento ou checklist como caso. As nove doenças foram localizadas nos metadados/fragmentos/correções canônicos disponíveis; dislipidemia, DM2 e estenose aórtica não foram julgadas ausentes só por dependerem de fragmentos.
- Cada um dos 12 casos e seis checklists aparece uma única vez na trilha designada, com `item_type` correto. As seis orientações ao paciente são alcançáveis pelos documentos e relações de doença; não foram falsamente contabilizadas entre as 18 etapas.
- A ordem das etapas das oito trilhas é contínua, de 1 até N. O delta real é +18 etapas e +24 relações em comparação à produção anterior.

Rotas de biblioteca, casos, materiais, checklists e trilhas correspondem às definições React disponíveis em `base/frontend/src/App.tsx`. Links diretos novos de medicamentos e exames foram confrontados com os respectivos catálogos: nenhum slug inexistente identificado. Não houve vínculo indevido à combinação furosemida/cloreto de potássio.

## Pertinência clínica

HAS conecta uso real, intolerância, investigação de hipocalemia e fechamento do retorno. IC conecta elegibilidade ao ARM, volemia pós-alta e manutenção após melhora da FEVE. Coronária distingue investigação de sintomas estáveis de acompanhamento de SCA. Dislipidemia e DM2 encaminham a seus próprios eixos clínicos. Valvopatia e síncope têm relações diferentes, coerentes com o diagnóstico investigado ou o seguimento.

Não encontrei relação nova que, por si, determine prescrição, exame ou confirmação diagnóstica. As relações usam `associated_with` e registram no `review_note` que não estabelecem diagnóstico nem indicação automática. A relevância numérica 0,95 é editorial; não deve ser interpretada como probabilidade clínica ou medida de desempenho de exame.

### Palpitações e fibrilação atrial

Os três recursos de palpitações são pertinentes **como investigação e diagnóstico diferencial** no percurso de arritmias/FA. O caso documenta extrassístoles correlacionadas às queixas breves, mas mantém as crises prolongadas sem diagnóstico; não confirma FA nem autoriza amiodarona ou anticoagulação. Material/checklist ensinam captura do sintoma e interpretação contextual.

A ancoragem no tema FA é aceitável com esse contexto, mas a interface e a busca não devem apresentar o caso como “FA confirmada”. O `review_note` atual já exclui confirmação automática. Refinamento editorial sugerido: nas três relações de palpitações, acrescentar “Vínculo para investigação e diagnóstico diferencial de palpitações; não representa fibrilação atrial documentada”. A mesma explicitação pode enriquecer `por_que` das duas etapas de palpitações na trilha FA. Não é necessário remover os vínculos para isso.

### Progressão da trilha IC

O checklist de retorno após melhora da FEVE ficou na etapa 2, imediatamente após o guia central. O destino é válido e clinicamente pertinente, mas a progressão do básico ao complexo ficaria melhor se ele viesse depois dos casos de segurança/titulação e pós-alta. Isso é um refinamento didático, não um órfão ou erro terapêutico. Reordenar exige preservar a numeração contínua; não requer novo recurso.

## Limites da conclusão

O parecer confirma a estrutura persistida neste lote. Não comprova que o banco de produção importou essas relações, que o mecanismo de relações inversas já as retornou em execução ou que as páginas foram testadas no navegador. A reciprocidade documental está representada por links e campos nativos; a relação doença → recurso é explícita e sua consulta no sentido inverso depende do serviço de grafo. Tampouco atesta completude de todos os temas ou das relações históricas do CorVIA.

Não foram introduzidos nomes de calculadoras por inferência. As etapas históricas de calculadoras não foram convertidas em documentos nem alteradas neste delta. A integração do lote pode seguir com os refinamentos editoriais sugeridos, mantendo separadas a validação estática realizada e a futura verificação de importação/navegação.
