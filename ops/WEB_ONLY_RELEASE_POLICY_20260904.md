# Política de release web-only — 04/09/2026

Por decisão operacional explícita, as publicações de produção do CorVIA ficam restritas ao **web**.

- Não construir, assinar, promover ou validar APK Android.
- Não construir, promover ou validar instalador Windows.
- O protocolo remoto autorizado passa a ser `deploy-web <SHA-da-main>`.
- O deploy continua usando `deploy.sh` para backup, migrations, backend, frontend, corpus, health/readiness e HTTPS.
- A mudança não altera o layout aprovado do login nem qualquer conteúdo funcional da aplicação.

O forced-command do servidor precisa ser atualizado uma única vez com `ops/bootstrap-release-entrypoint.sh` antes do primeiro deploy usando `deploy-web`.
