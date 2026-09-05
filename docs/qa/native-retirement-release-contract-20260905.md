# Retirada de apps nativos e contrato de publicação

Base: `bb13cf23f114aaf5e0791f1d7403c300a2522f9f`.
Este lote é independente do PR #819, dedicado ao Tudo com Tudo e cache clínico.
Não altera frontend visual, dados, corpus, migrations, credenciais ou política
editorial. Nenhum deploy, reload de proxy ou mudança de banco foi executado.

## Correções

O Caddy passa a responder HTTP 410, com `Cache-Control: no-store`, para os
instaladores Android/Windows das famílias CorVIA OS e Cardiology Spaces,
incluindo versões e checksums. Os redirects e handlers que serviam os APKs
foram removidos. Outros downloads e assets não pertencentes a essas famílias
não são interceptados por essa regra.

A documentação de API é negada dentro do handler `/api/*`, antes do proxy.
As variantes públicas de documentação e `/.vite/*` recebem HTTP 404 sem cache.
Essa é uma contenção no proxy; o OpenAPI interno da aplicação não é removido.

O validador de artefatos ganha o modo explícito `--retired android windows`.
Ele exige 410/no-store para 16 URLs conhecidas (8 instaladores/aliases e seus
checksums), rejeita redirects e testa URLs originais e com marcador de release
quando este é informado (32 verificações). Nunca baixa o corpo do binário.
O modo antigo de verificar binários publicados permanece compatível, mas o
workflow de produção usa agora o modo de retirada dos dois aplicativos.

O contrato de CI deixa de exigir a mensagem antiga de Windows pendente e passa
a exigir a chamada real de retirada. Permanecem todas as verificações de SHA,
risk gate, workflows científicos, health e readiness. O pós-deploy também
exige 404 nos endpoints públicos de documentação e no manifest interno.

## Validação executada

24 testes unitários locais aprovados, somente biblioteca padrão Python, com
respostas HTTP simuladas. Incluem seleção/aliases/sidecars, URL original e
cache-buster, redirects, erro de rede, TLS verificado, cache-control, modos CLI,
relatório JSON, regras textuais do proxy e o método real do contrato de deploy.

YAML analisado e todos os blocos shell do workflow aprovados por `bash -n`.
Os arquivos-base foram conferidos contra os respectivos blobs GitHub.

Isso NÃO é um teste de Caddy real, uma prova de resposta HTTP pública, uma
restauração de backup, nem a execução completa dos 22 testes da política de CI.
O teste de contrato específico foi executado isoladamente; os demais testes de
risco dependem do inventário completo do repositório.

## Antes de liberar publicação

Conciliar a alteração do Caddyfile com qualquer edição paralela ainda não
commitada. Executar `caddy adapt --validate` com as variáveis e a versão do
ambiente de QA, validar as rotas HTTP reais e recarregar o proxy de forma
controlada. O deploy web por si só não comprova que o Caddyfile foi recarregado.

Revalidar URLs antigas diretamente e providenciar expurgo do cache da CDN
quando necessário: um 410 no origin não prova a remoção de objetos que já
ficaram armazenados em caches intermediários ou de arquivos já baixados.

Executar no ambiente do projeto:

```sh
python -m unittest scripts.tests.test_public_app_retirement -v
python -m unittest scripts.tests.test_ci_backend_policy -v
```

A falha científica de 11.577 itens autorizados versus 11.581 presentes permanece
fora deste lote. Não se atualizou o manifesto nem se relaxou o gate para aceitar
conteúdo novo sem revisão. As demais pendências de infraestrutura e conteúdo
continuam exigindo validação própria.
