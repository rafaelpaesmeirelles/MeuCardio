#!/usr/bin/env bash
# Backup diário/pré-deploy do PostgreSQL, ampliado em 06/08/2026 (pedido do
# Rafael: "criar backup automatico de todas as informacoes, selfies,
# documentos pessoais e profissionais enviados pelos assinantes [...] e
# tambem dos docs e prescricoes geradas") para também cobrir os volumes
# Docker que guardam arquivo — o dump do Postgres sozinho não leva os bytes
# do selfie/documento/PDF, só metadado e nome de arquivo cifrado.
#
# Volumes cobertos, todos já cifrados por dentro (cofre AES-256-GCM,
# `app/services/cofre.py`) — o tar não decifra nada, só empacota o que já
# está protegido:
#   kycfiles         selfie + documento pessoal/profissional do KYC (Trabalho 11)
#   documentofiles    PDF de receituário/documento assinado
#   certificadosfiles certificado digital A1 do médico (Trabalho 7)
#   examefiles        exame de telediagnóstico
# `userfiles` (foto de perfil) e `cursofiles` (material de curso parceiro)
# ficam de fora de propósito — não são PII sensível na mesma categoria, e
# cursofiles pode ser grande sem ganho equivalente de risco evitado.
#
# Roda no host, sem expor credenciais adicionais fora do .env.
set -Eeuo pipefail

# O cron pode continuar definindo /opt/meucardio. Durante deploy e testes, o
# projeto é derivado do próprio script ou informado explicitamente por PROJETO.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJETO="${PROJETO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
DESTINO="${BACKUP_DESTINO:-$PROJETO/infra/backup/dumps}"
RETENCAO_DIAS="${BACKUP_RETENCAO_DIAS:-14}"
COMPOSE=(docker compose -f "$PROJETO/docker-compose.prod.yml")

mkdir -p "$DESTINO"
cd "$PROJETO"

if [[ ! -f .env ]]; then
  echo "Arquivo .env não encontrado em $PROJETO." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .env
: "${POSTGRES_USER:?Defina POSTGRES_USER no .env.}"
: "${POSTGRES_DB:?Defina POSTGRES_DB no .env.}"

DATA="$(date +%Y-%m-%d_%H%M%S)"
ARQUIVO="$DESTINO/meucardio_${DATA}.dump"
TEMPORARIO="${ARQUIVO}.tmp"

umask 077
trap 'rm -f "$TEMPORARIO"' EXIT

echo "[$(date -Is)] Iniciando backup custom em $ARQUIVO"

if ! "${COMPOSE[@]}" exec -T db pg_dump \
  -U "$POSTGRES_USER" \
  --format=custom \
  --compress=9 \
  --no-owner \
  --no-privileges \
  "$POSTGRES_DB" > "$TEMPORARIO"; then
  echo "[$(date -Is)] ERRO: pg_dump falhou. Removendo arquivo parcial." >&2
  exit 1
fi

# Verifica o catálogo com a mesma ferramenta usada na restauração antes de
# publicar o arquivo no diretório de backups.
if ! "${COMPOSE[@]}" exec -T db pg_restore --list < "$TEMPORARIO" >/dev/null; then
  echo "[$(date -Is)] ERRO: pg_restore não reconheceu o catálogo do backup." >&2
  exit 1
fi

mv "$TEMPORARIO" "$ARQUIVO"
chmod 600 "$ARQUIVO"
(
  cd "$DESTINO"
  sha256sum "$(basename "$ARQUIVO")" > "$(basename "$ARQUIVO").sha256"
  chmod 600 "$(basename "$ARQUIVO").sha256"
)
trap - EXIT

TAMANHO="$(du -h "$ARQUIVO" | cut -f1)"
echo "[$(date -Is)] Backup concluído: $ARQUIVO ($TAMANHO)"

REMOVIDOS="$(find "$DESTINO" -name 'meucardio_*.dump' -mtime "+${RETENCAO_DIAS}" -print -delete | wc -l)"
find "$DESTINO" -name 'meucardio_*.dump.sha256' -mtime "+${RETENCAO_DIAS}" -delete
if [[ "$REMOVIDOS" -gt 0 ]]; then
  echo "[$(date -Is)] Removidos $REMOVIDOS backup(s) com mais de ${RETENCAO_DIAS} dias."
fi

# --- Volumes sensíveis (arquivo cifrado por dentro — ver cabeçalho) -------
# Roda `docker compose run` sobre o próprio serviço `backend`, que já tem
# cada volume montado no caminho certo — evita ter que descobrir o nome
# real do volume Docker (que carrega um prefixo de projeto Compose não
# garantido). `run --rm` substitui o `command` do serviço pelo `tar`, então
# nada de migração ou uvicorn roda nesse container efêmero.
declare -A CAMINHO_NO_CONTAINER=(
  [kycfiles]="/kyc-documentos"
  [documentofiles]="/documentos-emitidos"
  [certificadosfiles]="/certificados-a1"
  [examefiles]="/exames-pacientes"
)
DESTINO_VOLUMES="${BACKUP_DESTINO_VOLUMES:-$DESTINO}"
mkdir -p "$DESTINO_VOLUMES"

for nome in "${!CAMINHO_NO_CONTAINER[@]}"; do
  caminho="${CAMINHO_NO_CONTAINER[$nome]}"
  arquivo_vol="$DESTINO_VOLUMES/${nome}_${DATA}.tar.gz"
  temporario_vol="${arquivo_vol}.tmp"
  if ! "${COMPOSE[@]}" run --rm -T --no-deps \
      -v "$DESTINO_VOLUMES:/backup-saida" \
      backend \
      tar -czf "/backup-saida/$(basename "$temporario_vol")" -C "$caminho" .; then
    echo "[$(date -Is)] ERRO: falha ao empacotar o volume '$nome' ($caminho)." >&2
    rm -f "$temporario_vol"
    exit 1
  fi
  mv "$temporario_vol" "$arquivo_vol"
  chmod 600 "$arquivo_vol"
  (
    cd "$DESTINO_VOLUMES"
    sha256sum "$(basename "$arquivo_vol")" > "$(basename "$arquivo_vol").sha256"
    chmod 600 "$(basename "$arquivo_vol").sha256"
  )
  echo "[$(date -Is)] Volume '$nome' empacotado: $arquivo_vol ($(du -h "$arquivo_vol" | cut -f1))"
done

REMOVIDOS_VOL="$(find "$DESTINO_VOLUMES" -maxdepth 1 \( -name 'kycfiles_*.tar.gz' -o -name 'documentofiles_*.tar.gz' -o -name 'certificadosfiles_*.tar.gz' -o -name 'examefiles_*.tar.gz' \) -mtime "+${RETENCAO_DIAS}" -print -delete | wc -l)"
find "$DESTINO_VOLUMES" -maxdepth 1 \( -name 'kycfiles_*.tar.gz.sha256' -o -name 'documentofiles_*.tar.gz.sha256' -o -name 'certificadosfiles_*.tar.gz.sha256' -o -name 'examefiles_*.tar.gz.sha256' \) -mtime "+${RETENCAO_DIAS}" -delete
if [[ "$REMOVIDOS_VOL" -gt 0 ]]; then
  echo "[$(date -Is)] Removidos $REMOVIDOS_VOL pacote(s) de volume com mais de ${RETENCAO_DIAS} dias."
fi

# Continua imprimindo só o caminho do dump do banco como ÚLTIMA linha de
# stdout — `deploy.sh::criar_backup_pre_deploy()` faz `tail -n 1` sobre a
# saída deste script para achar o arquivo de rollback. Qualquer eco novo
# tem que vir ANTES desta linha, nunca depois.
printf '%s\n' "$ARQUIVO"
