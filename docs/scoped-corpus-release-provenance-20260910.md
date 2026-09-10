# Reconciliação documental da release científica — 10/09/2026

Reconciliação de autorizações existentes, solicitada expressamente pelo proprietário: baseline imutável vinculado ao manifesto válido fedf818c; pacote científico de 09/09 com hash autorizado e exclusões preservadas; PR915 e rodada2 reproduzidos em c1eafa1e, cuja inclusão/deploy foi expressamente solicitada ao coordenador. Demais itens ficam em quarentena. A normalização estrita do único campo theme em 304 fichas no anchor 800a159e também integra a correção técnica Tudo com Tudo expressamente autorizada nesta sessão. Inclui ainda a publicação emergencial expressamente autorizada dos 391 rascunhos revisados em 10/09 e dos sete registros do suplemento Claude sobre benzatina, vinculados aos pacotes e às fontes canônicas finais por hashes exatos. Não constitui nova revisão clínica nem assinatura humana de revisão.

Snapshot: **12549** itens; **12549** autorizados; **0** em quarentena.

| Frente | Total | Autorizados | Quarentena |
|---|---:|---:|---:|
| casos_clinicos | 929 | 929 | 0 |
| checklists | 479 | 479 | 0 |
| documentos | 3364 | 3364 | 0 |
| doencas_especializadas | 326 | 326 | 0 |
| emergencia | 77 | 77 | 0 |
| estudos | 2061 | 2061 | 0 |
| evidencias | 3363 | 3363 | 0 |
| exames | 423 | 423 | 0 |
| galeria | 281 | 281 | 0 |
| material_paciente | 454 | 454 | 0 |
| medicamentos | 206 | 206 | 0 |
| triagem_sintomas | 23 | 23 | 0 |
| trilhas | 563 | 563 | 0 |

O baseline foi reconstruído de objetos Git e seu manifesto v1 validado integralmente antes de reutilizar somente registros imutáveis. Alterações do PR915 são calculadas por registro entre seu pai e o resultado da rodada2; alterações em catálogos agregados não aprovam outros registros desses arquivos. O pacote de 09/09 exige seu SHA-256 fixo e correspondência exata da fonte. Exclusões de duplicatas prevalecem, salvo as duas fichas kind=estudo reavaliadas expressamente em 10/09, complementares às sínteses multifuentes e vinculadas aos novos hashes no registro separado de supersessões.

As 304 fichas normalizadas pelo commit800a159e receberam prova separada: somente theme mudou, todos os demais campos são idênticos ao baseline válido e o registro final inteiro bate com o anchor autorizado. 138 temas anteriores foram enquadrados no domínio de 30 temas canônicos. Nenhum campo foi ignorado na comparação.

A extensão de 10/09 autoriza exatamente 398 registros revisados: 391 rascunhos e sete itens do suplemento Claude sobre benzatina. Pacotes e manifestos de integração têm hashes fixos; corpos e metadados correspondem às fontes finais com published=true. Em JSON agregado, somente os três registros do suplemento recebem a nova aprovação. Aprovações e quarentenas anteriores fora desses 398 são preservadas.

Os arquivos auxiliares, inclusive mídias da galeria e relações explícitas, também foram comparados contra baseline ou delta exato PR915 e vinculados por hash no índice de evidências. As 3054 relações anteriores permanecem intactas, com 105 novas relações do PR915/rodada2, total 3159.

Documentos usam SHA-256 dos bytes completos. Registros JSON usam serialização canônica do registro completo; doenças e triagem usam seus compositores canônicos. O overlay de material ao paciente foi confirmado imutável desde o baseline e seus arquivos são referências hashadas obrigatórias. Nenhum conteúdo ou status foi editado; `revisado` isoladamente não concede autorização.

A evidência registra autorização de publicação existente e revisão assistida por IA dos pacotes; não declara nova revisão médica nem assinatura humana. Slugs runtime-only não pertencem a este inventário.

Reprodução: `python3 scripts/build_scoped_corpus_release.py --check` (Git e PyYAML; sem banco ou IA paga). O ledger JSON ao lado registra a fonte de autorização ou o motivo de quarentena de cada identidade.
