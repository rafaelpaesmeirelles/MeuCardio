# Aplicativos CorVIA Cardiology Spaces 1.2.0

O cliente Android usa o site certificado como fonte funcional. O cliente
Windows está marcado como pendente e não possui link de download na interface
até que sua identidade Authenticode esteja configurada e validada. Nenhum
segredo de assinatura pertence ao repositório.

## Android

- `applicationId`: `br.med.corvia`
- versão: `1.2.0` (`versionCode 4`)
- URL: `/downloads/corvia-cardiology-spaces-android-1.2.0.apk`

O servidor mantém `frontend/android/keystore.properties` e o keystore fora do
Git. O workflow fixa somente o fingerprint SHA-256 público do certificado de
release existente. A variável `CORVIA_ANDROID_CERT_SHA256` pode substituir
esse valor durante uma rotação controlada; nenhuma chave ou senha é versionada.
`apksigner` e `aapt` bloqueiam APK sem assinatura, chave trocada, appId ou
versão incorretos.

## Windows — pendência registrada

- Electron/NSIS x64 para Windows 10/11
- versão planejada: `1.2.0`
- estado: **pendente de assinatura**
- download na interface: **desativado**

O workflow exige Authenticode válido, certificado fixado e gera o digest, o
`source-sha.txt` e o fingerprint do signatário. Configuração obrigatória:

- secret `CORVIA_WINDOWS_CODE_SIGNING_CERT` (PFX/base64 aceito pelo electron-builder);
- secret `CORVIA_WINDOWS_CODE_SIGNING_PASSWORD`;
- variable `CORVIA_WINDOWS_SIGNING_CERT_SHA256`.

O Android usa o fingerprint público fixado no workflow; a variável
`CORVIA_ANDROID_CERT_SHA256` é um override opcional para rotação controlada.
Enquanto o Windows estiver pendente, as verificações públicas agendadas exigem
somente `CORVIA_ANDROID_EXPECTED_SHA256`. A validação Windows continua
disponível quando selecionada explicitamente e permanece fail-closed.

## Release web e Android enquanto Windows está pendente

1. Todos os gates são certificados no mesmo SHA atual da `main`.
2. `Native installers` permanece manual e rigoroso; não é gate automático.
3. Android é construído, assinado e validado em um worktree temporário do SHA;
   o checkout de produção ainda não é alterado.
4. Só então `deploy.sh` pode alterar web/banco.
5. Após sucesso, APK e sidecar são promovidos; falha restaura os anteriores.
6. O pós-deploy baixa o APK com cache-buster e compara o hash da execução.
7. O protocolo legado `deploy-release` continua exigindo EXE certificado; não
   foi relaxado e só será reativado com autorização e credenciais válidas.

## Bootstrap único do protocolo Android-only

O forced command estável precisa conhecer `deploy-web-android` antes do primeiro
deploy neste modo. O bootstrap abaixo não faz checkout nem deploy.

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

Override opcional para rotação Android: `CORVIA_ANDROID_CERT_SHA256`. Quando
o Windows for reativado, também serão exigidos
`CORVIA_WINDOWS_SIGNING_CERT_SHA256` e os secrets de assinatura:
`CORVIA_WINDOWS_CODE_SIGNING_CERT` e
`CORVIA_WINDOWS_CODE_SIGNING_PASSWORD`.

O workflow valida SSH e o fingerprint Android antes do primeiro envio. O
workflow manual `Native installers` reprova qualquer Windows sem chave, senha,
assinatura Authenticode e fingerprint fixado.
