# Aplicativos CorVIA Cardiology Spaces 1.2.0

Os clientes Android e Windows usam o site certificado como fonte funcional,
mas seus binários têm identidade, versão, origem e assinatura verificadas.
Nenhum segredo de assinatura pertence ao repositório.

## Android

- `applicationId`: `br.med.corvia`
- versão: `1.2.0` (`versionCode 4`)
- URL: `/downloads/corvia-cardiology-spaces-android-1.2.0.apk`

O servidor mantém `frontend/android/keystore.properties` e o keystore fora do
Git. A variável protegida `CORVIA_ANDROID_CERT_SHA256` contém o fingerprint
público da chave de release existente. `apksigner` e `aapt` bloqueiam APK sem
assinatura, chave trocada, appId ou versão incorretos.

## Windows

- Electron/NSIS x64 para Windows 10/11
- versão: `1.2.0`
- URL: `/downloads/corvia-cardiology-spaces-windows-1.2.0.exe`

O workflow exige Authenticode válido, certificado fixado e gera o digest, o
`source-sha.txt` e o fingerprint do signatário. Configuração obrigatória:

- secret `CORVIA_WINDOWS_CODE_SIGNING_CERT` (PFX/base64 aceito pelo electron-builder);
- secret `CORVIA_WINDOWS_CODE_SIGNING_PASSWORD`;
- variable `CORVIA_WINDOWS_SIGNING_CERT_SHA256`.

O Android exige a variable protegida `CORVIA_ANDROID_CERT_SHA256`. As
verificações públicas agendadas exigem ainda os hashes dos últimos binários
publicados em `CORVIA_ANDROID_EXPECTED_SHA256` e
`CORVIA_WINDOWS_EXPECTED_SHA256`; sem ambos o gate de deriva falha fechado.

## Release sem publicação parcial

1. Todos os gates são certificados no mesmo SHA atual da `main`.
2. O `run_id` exato de `Native installers` é preservado.
3. Windows é enviado para staging com timeout, limite de 350 MiB, MZ e SHA.
4. Android é construído, assinado e validado em um worktree temporário do SHA;
   o checkout de produção ainda não é alterado.
5. Só então `deploy.sh` pode alterar web/banco.
6. Após sucesso, APK/EXE e sidecars são promovidos; falha restaura os anteriores.
7. O pós-deploy baixa ambos com cache-buster e compara os hashes esperados da execução.

## Bootstrap único obrigatório

O `authorized_keys` antigo chama diretamente o entrypoint dentro do checkout e
ele não conhece `windows-stage`/`deploy-release`. O comando antigo `deploy`
atualizaria o arquivo, porém também executaria imediatamente o deploy web. Isso
não é um bootstrap seguro.

Em uma sessão administrativa autenticada, execute **sem checkout e sem deploy**:

```bash
cd /opt/meucardio
git fetch --prune origin main
SHA="$(git rev-parse origin/main)"
BOOTSTRAP="$(mktemp)"
git show "$SHA:ops/bootstrap-release-entrypoint.sh" > "$BOOTSTRAP"
bash -n "$BOOTSTRAP"
bash "$BOOTSTRAP" "$SHA"
rm -f "$BOOTSTRAP"
```

Extrair também o bootstrap do objeto Git é indispensável quando o checkout
ainda aponta para a versão antiga, que não contém esse arquivo. O script
extrai o entrypoint diretamente do objeto Git daquele SHA, valida a
sintaxe, instala root:root `0755` em
`/usr/local/libexec/corvia-remote-deploy-entrypoint` e altera somente a linha
restrita já marcada no `authorized_keys`. Depois de uma release bem-sucedida,
o entrypoint estável é atualizado pelo próprio protocolo certificado.

## Variáveis SSH já exigidas pelo deploy

Secrets: `PRODUCTION_SSH_HOST`, `PRODUCTION_SSH_PORT`,
`PRODUCTION_SSH_USER`, `PRODUCTION_SSH_PRIVATE_KEY` e
`PRODUCTION_SSH_KNOWN_HOSTS`.

Variables: `CORVIA_ANDROID_CERT_SHA256` e
`CORVIA_WINDOWS_SIGNING_CERT_SHA256`. Secrets de assinatura Windows:
`CORVIA_WINDOWS_CODE_SIGNING_CERT` e
`CORVIA_WINDOWS_CODE_SIGNING_PASSWORD`.

O workflow valida todos os valores de SSH e os fingerprints antes do primeiro
envio. Ausência de chave de assinatura Windows já reprova `Native installers`,
antes que o job de produção possa existir.
