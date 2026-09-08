# Integração transversal — 8 de setembro de 2026

Base: `e7b7c35def95831f2745f5e5810f477de6a6da28`. Corpus: 11.581 itens canônicos. Os 3.054 vínculos explícitos de doenças anteriores permanecem preservados.

## Resultado da revisão

Manifesto novo: 728 relações editoriais explícitas revisadas, com fonte e nota individual. Tipos: 323 `studied_in`, 200 `associated_with`, 181 `recommended_by`, 14 `monitor_with` e 10 `used_in_case`. Origens: 671 medicamento, 22 exame, 33 doença e 2 galeria. Destinos: 372 estudo, 312 evidência, 17 exame, 10 caso, 8 medicamento, 5 checklist, 3 galeria e 1 trilha.

O parser passa a resolver dez referências Markdown existentes de calculadoras em documentos; essas dez referências não estão incluídas nas 728 do manifesto. A importação exige publicação atual dos dois nós, aplica a política semântica existente e reutiliza o upsert e o mecanismo de desativação. Rejeições humanas permanecem preservadas.

A relação rivaroxabana–digoxina fica explicitamente marcada como ausência de interação na fonte e é omitida das interações positivas da API e do grafo. A negação não é inferida por palavras. A interação farmacodinâmica digoxina–furosemida permanece.

Os reforços de hubs incluem 20 relações de embolia pulmonar aguda e 13 de hipertensão arterial sistêmica. Seis relações de estudos foram limitadas a contexto, sem alegar intervenção estudada. As exclusões e os limites editoriais estão documentados nos relatórios das frentes.

## Validação local

Passaram 93 testes de scripts, 49 testes da política clínica e 25 testes de navegação direta entre frentes (167 no total). Auditoria integral: 11.581 itens, nenhum bloqueio editorial ou de autorização, nenhuma referência quebrada; os 728 pares resolvem para fontes canônicas. Auditoria semântica com mecanismos reais: zero erros de invariantes e residuais, graph F1 1,0 e contextual F1 1,0. O inventário de calculadoras agora usa o registro executável real, incluindo segurança da hipercalemia e BRASH.

Quatro testes novos de persistência PostgreSQL cobrem idempotência, navegação bidirecional, despublicação, remoção/reinserção e rejeição humana. Sua execução em banco ainda é necessária. A política de CI existente classifica alterações do grafo e dos dados clínicos como risco que exige validação integral; não foi modificada para reduzir gates.

O manifesto de autorização conserva contagens, slugs e estados editoriais. Apenas o fingerprint da fonte de doenças (que contém o novo manifesto), o agregado derivado e a justificativa da revisão são atualizados. Nenhuma alteração de UI, infraestrutura, login, embeddings ou conteúdo de PRs pendentes do Grok.

## Produção antes da publicação

Produção observada no SHA da base, com health e ready saudáveis. Após autenticação pelo próprio usuário, 20 consultas em linguagem humana abriram resultados: Holter, Holter 24h, CHA2DS2-VASc, HAS-BLED e os 16 assuntos clínicos obrigatórios. O Holter canônico foi observado em `/exames/holter-24h`. As ferramentas CHA2DS2-VASc, HAS-BLED/ORBIT, GRACE/CRUSADE/TIMI, Wells TEP, Genebra, PESI/sPESI, Wells TVP e SCAI/vasoativos apareceram nos respectivos resultados.

Essas observações são da versão anterior à mudança. A presença de grupos não certifica diagnóstico, seguimento ou contraindicações; cada relação precisa de avaliação semântica. TEP e HAS mostraram menor diversidade de grupos e motivaram o reforço revisado acima. Os números mostrados no cabeçalho são resultados por frente da busca, não totais do ecossistema.

## Condição de fechamento

Este documento registra um candidato validado localmente, não uma certificação pós-publicação. Ainda são necessários CI com PostgreSQL, merge preservando a main atual, deploy, reconcile com publicação dos revisados, zero explicit unresolved/automatic invalid e repetição das sentinelas na versão final. Nenhum total de arestas novas persistidas ou certificado de 100% é afirmado antes desses passos.
