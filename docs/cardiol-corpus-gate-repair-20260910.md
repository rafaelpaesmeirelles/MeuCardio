# Reparo dos gates do acervo Cardiol

Base c7b57852: CI aprovado com ambas as suítes backend skipped. Corpus inventory encontrou mock legado PR918 sem isolamento dos novos escopos e provas de indisponibilidade desatualizadas; RC2 encontrou evidência não acessível no container. Correções focais e evidências registradas abaixo. Nenhuma alteração clínica autorizada por este documento.

## Reconciliação das 17 supressões de links clínicos

A falha não era apenas uma expectativa antiga do teste. O registro de apresentação ainda removia os links de 17 destinos: dez classificados como quarentena e sete como ausência de equivalente integral. Entretanto, o commit de autorização existente `2306ac71` já havia incorporado todos esses documentos sob seus mesmos slugs, com proveniência `approved_package`.

Conferência realizada nesta correção:

- Os 17 slugs constam em `approved.documentos` do snapshot atual; nenhum consta em `quarantined.documentos`.
- Os 17 arquivos canônicos existem. Em todos eles, o SHA256 dos bytes confere com `provenance.documentos[slug].source_sha256`.
- Os 17 registros de proveniência apontam para evidência versionada cujo SHA256 também confere.
- O snapshot atual tem SHA256 `a342b3d722b11987ab2025fbb5730c7699bec8b7c9c53a885fa5c638329e057c`; as dez disposições antigas ainda exigiam `a528b0090743558b5ce828ecd1b98ef9260c99fb59089fd0267bd7466b9f24a0`. Atualizar apenas esse hash manteria uma falsa indicação de quarentena.
- Os sete registros antigos de lacuna apontavam para uma análise histórica válida naquele momento, mas seus destinos canônicos já existem e estão autorizados. Não foi criado alias aproximado para substituí-los.

A correção remove somente essas 17 supressões ativas de `clinical_link_availability.json`; `references` fica vazio. O bloco `restoration` preserva o motivo anterior de cada supressão, os caminhos de origem, o destino exato, seus hashes e as evidências de autorização já existentes. Não constitui nova aprovação editorial e não altera nenhum texto clínico.

O serviço `clinical_link_availability.py` e seus bloqueios por fonte, hash, quarentena e lacuna permanecem sem alterações. Seus testes usam agora provas temporárias isoladas, conservando os casos negativos sem exigir que a produção continue com documentos ausentes. Uma regressão adicional verifica os 17 destinos reais contra os arquivos/proveniências atuais e confirma que voltam a produzir links e destinos no grafo.

Validação focal: `python3 -m pytest --noconftest -q scripts/tests/test_clinical_link_availability.py` — **9 testes e 19 subtestes aprovados em 0,52 s**. Sem banco, chamadas pagas, alteração de autorização, execução de CI backend ou publicação.

## Registro de CI e fixture histórica

PR928 selado no manifesto, base c7b57852 e branch codex/cardiol-gate-fixtures-20260910; chave nominal incluída no gate. Dez contratos locais aprovados em 0,170 s, incluindo shell real e seus casos de recusa. O teste isolado de associação incompleta PR918 voltou a passar em 0,113 s, preservando ambos os cenários de recusa e seus asserts; apenas os escopos independentes foram isolados. Nenhuma suíte backend foi iniciada.


## RC2: montagem das provas transitivas do corpus

A execução RC2 34542463874 falhou em `Reconcile clean canonical corpus` com `Fonte de evidência ausente ou fora do repositório.` A autorização existente passou a referenciar 466 arquivos de prova, mas o contêiner RC2 e o compose de produção disponibilizavam apenas 447. Os mesmos 19 arquivos faltavam nos dois ambientes: o registro de supersessões e 18 artefatos dos lotes scientific-20260910/scientific-20260910-unpublished, incluindo fontes e revisões do suplemento sobre benzatina. Todos já existiam e estavam rastreados no Git.

Correção restrita: adicionadas as 19 cópias exatas à etapa de materialização de `.github/workflows/rc2-acceptance.yml` e os 19 bind mounts exatos, todos `:ro`, em `docker-compose.prod.yml`. Nenhuma autorização, prova, checksum, validação científica ou conteúdo foi modificado. O compose de desenvolvimento não precisou mudar: o RC2 já possui etapa explícita de cópia do corpus.

Verificação estática aprovada: cobertura 447 + 19 = 466, sem caminho pendente nos dois ambientes; os 19 arquivos são regulares, rastreados e têm SHA-256 idêntico à referência na prova autorizada. YAML analisado e shell da etapa RC2 aprovado em `bash -n`. Relatório completo em `docs/qa/cardiol-corpus-gate-repair-20260910/evidence-mount-coverage.json`.

Consumidores adicionais verificados: `deploy.sh` usa `docker-compose.prod.yml` e executa a reconciliação no contêiner backend, portanto recebe os mesmos mounts corrigidos; não há segunda lista de 19 fontes a atualizar no deploy. O workflow `corpus-database.yml` executa a reconciliação no checkout completo, sem essa lacuna de montagem. Não foram executados backend CI, banco, deploy ou chamada paga durante esta correção.
