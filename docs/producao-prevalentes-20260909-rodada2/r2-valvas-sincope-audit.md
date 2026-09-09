# Rodada 2 — valvopatias e síncope

Data: 09/09/2026. Base informada: main cb750689b94f7888b18133e68ff8293bff55d742. Lidos os quatro documentos de produção 1 e sua auditoria; inventariados os títulos/slugs dos catálogos completos (915 casos, 448 materiais e 473 checklists). Lidos integralmente os registros legados afetados. Não se afirma revisão integral de todos os itens do catálogo.

## Lacunas e entregas

Os casos existentes concentram escolhas de intervenção, indicações de dispositivos e resultados de estudos. Este lote acrescenta dois exercícios originais sobre incerteza clínica e dados incompletos: laudo aórtico discordante com redução não reconhecida da atividade e recorrência pós-marca-passo com queda pressórica e horário de interrogação ainda não reconciliado. Há materiais gerais de estenose, porém não um roteiro específico para preparar consulta com exames divergentes; há checklists gerais de síncope, porém não um roteiro específico pós-marca-passo.

- `round2/valvas-sincope/casos-clinicos.json`: dois casos explicitamente fictícios, quatro alternativas, resposta base zero e análise de cada alternativa.
- `round2/valvas-sincope/material-paciente.json`: organização da consulta com laudos discrepantes, sem autoteste de esforço ou suspensão autônoma de medicamentos.
- `round2/valvas-sincope/checklists.json`: avaliação dirigida pós-MP; sem exame em bloco nem indicação universal.
- `round2/valvas-sincope/material-paciente-corrections.json`: registro legado completo com correção focal da falsa regra de suspensão dos antitrombóticos aos três meses. Diferenciados tipos de prótese, procedimentos e outras indicações de anticoagulação; sem impor novo esquema universal.
- `round2/valvas-sincope/checklists-corrections.json`: registro legado completo com correções de DSE diagnóstica em baixa dose versus esforço e de encaminhamento. IDs preservados por compatibilidade histórica; o texto do antigo item cujo ID contém `preservada-eco-estresse` agora diferencia os fenótipos. Nenhuma migração de IDs foi realizada.

Todos os registros entregues permanecem `pendente_revisao`, sem `published: true`. Nas correções, revisão é explicitamente focal; os demais parágrafos legados não foram reclassificados como integralmente validados.

## Fontes efetivamente acessadas e limites

- [EACVI/ASE 2017 — estenose aórtica](https://www.asecho.org/wp-content/uploads/2017/04/2017ValveStenosisGuideline.pdf), DOI 10.1016/j.echo.2017.02.009: texto integral aberto; abordagem integrada e aquisição Doppler consultadas. Fonte de consenso de imagem, sem inventar classe terapêutica.
- [ESC/EACTS 2025 — portal oficial](https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/valvular-heart-disease/): portal acessado; link do texto integral não produziu texto utilizável. Nenhuma classe ou nova duração de antitrombótico de 2025 foi extraída.
- [ESC/EACTS 2021 — texto integral](https://pmc.ncbi.nlm.nih.gov/articles/PMC9725093/), DOI 10.1093/eurheartj/ehab395: seções 5.1 e 11.3 abertas e verificadas para correções focais. A correção antitrombótica remove generalização insegura; não afirma reproduzir a tabela vigente de 2025.
- [Rocha et al. — Syncope in Patients with Cardiac Pacemakers](https://pmc.ncbi.nlm.nih.gov/articles/PMC7918387/), PMID 33594860: estudo primário prospectivo brasileiro; métodos e discussão lidos para avaliação e seleção de exames. Não usado como ensaio de eficácia ou escore validado.
- [BIOSync CLS — abstract original](https://pubmed.ncbi.nlm.nih.gov/33279955/), DOI 10.1093/eurheartj/ehaa936: população, desenho e direção de benefício conferidos; nenhum efeito de mortalidade ou programação universal inferido.
- ISSUE-3 subanálise (PMID 24336948): acesso tentado, mas retorno vazio nesta rodada. Por isso os novos casos não reproduzem seus números nem alegam revisão direta dessa fonte. A correção da produção 1, previamente documentada, foi preservada.
- ESC 2018 síncope e ESC 2021 pacing: portais/links tentados; texto integral OUP não utilizável. Não acrescidas classes dessas fontes na rodada 2.

Casos, opções, perguntas ao paciente e organização dos roteiros são originais. Sínteses de evidência são breves, sem tradução extensa de tabelas ou figuras. A informação de ESC/EACTS 2021 nas alterações focais não substitui consulta à versão atual para prescrição individual.

## Tudo com Tudo — relações para integração pelo coordenador

Caso `estenose-aortica-area-pequena-gradiente-baixo-e-laudos-nao-comparaveis` e material `estenose-aortica-laudos-diferentes-preparar-a-consulta`:
- documento `estenose-aortica-do-laudo-discordante-a-consulta-longitudinal` (material documento_slug já preenchido e caso com link interno).
- doença `estenose-aortica`.
- trilha `trilha-consulta-progressiva-valvopatias`.
- exame `escore-de-calcio-da-valva-aortica-na-estenose-aortica-de-baixo-fluxo-baixo-gradiente`, como estudo dirigido se persistir dúvida, sem ordem automática.
- checklist legado corrigido `estenose-aortica-de-baixo-fluxo-e-baixo-gradiente-avaliacao`.

Caso `sincope-apos-marca-passo-registros-temporais-e-queda-pressoria` e checklist `sincope-recorrente-apos-marca-passo-correlacao-clinica-e-dispositivo`:
- documento `sincope-recorrente-apos-marca-passo-interpretacao-do-tilt-e-reavaliacao` (documento_origem já preenchido e caso com link interno).
- documento `sincope-diagnostico-e-manejo-esc-2018`.
- doença `sincope`.
- trilha `trilha-consulta-progressiva-sincope`.
- material `sincope-desmaio`.
- documento `estimulacao-em-malha-fechada-closed-loop-stimulation-na-sincope-vasovagal-cardioinibitoria` (confirmado em round2-paths.txt).

Slugs de doença, exames e trilhas reaproveitam relações já verificadas na produção 1. Relações propostas não foram gravadas no grafo central nesta frente. O coordenador deve integrar reciprocamente e validar os destinos contra sua base antes da publicação. Não há calculadora validada específica a acrescentar por analogia.

## Verificação

JSONs parseados; campos comparados à união dos campos efetivos dos catálogos atuais; quatro slugs novos sem colisão; duas correções resolvem slugs já existentes; todos os casos têm quatro alternativas e índice válido; checklist sem IDs duplicados. Sem commit, push ou deploy. Produção 1 e catálogos-base preservados.

## Conferência adicional do documento de origem do checklist

Após solicitação do coordenador, recuperado por GitHub `content/Valvopatias/valvopatias-estenose-aortica-e-atualizacoes-gerais-esceacts-2021.md` na referência `cb750689b94f7888b18133e68ff8293bff55d742` (blob SHA `4d323b1197df9a005439b8d21dbed6ff612f9afb`). Leitura integral: não contém proibição genérica de dobutamina nem solicitação de Heart Team para todo fenótipo de área discordante. Não há sequer seção de estresse com dobutamina nesse texto. A seção de casos intermediários discute escolha entre procedimentos, e não encaminhamento universal de discordâncias ecocardiográficas. Portanto, os dois erros do checklist não são reproduzidos nesse documento de origem; não criada cópia corrigida do Markdown nesta frente. Essa conferência focal não revalida as demais afirmações históricas de intervenção ou classes do documento.
