#!/usr/bin/env bash
# Restaura um dos volumes sensíveis (kycfiles/documentofiles/certificadosfiles/
# examefiles) a partir de um pacote gerado por backup.sh. USO RARO E
# DESTRUTIVO: apaga o conteúdo atual do volume antes de extrair o backup —
# mesma cautela do restaurar.sh (checksum antes de qualquer escrita,
# confirmação explícita, backend parado durante a operação).
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJETO="${PROJETO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
COMPOSE=(docker compose -f "$PROJETO/docker-compose.prod.yml")
ARQUIVO="${1:-}"

declare -A CAMINHO_NO_CONTAINER=(
  [kycfiles]="/kyc-documentos"
  [documentofiles]="/documentos-emitidos"
  [certificadosfiles]="/certificados-a1"
  [examefiles]="/exames-pacientes"
)

if [[ -z "$ARQUIVO" || ! -f "$ARQUIVO" ]]; then
  echo "Uso: $0 <volume_AAAAMMDD-HHMMSS.tar.gz>"
  echo "Pacotes disponíveis:"
  ls -lh "$PROJETO/infra/backup/dumps/"*.tar.gz 2>/dev/null || echo "  (nenhum encontrado)"
  exit 1
fi

NOME_BASE="$(basename "$ARQUIVO")"
NOME_VOLUME="${NOME_BASE%%_*}"
CAMINHO="${CAMINHO_NO_CONTAINER[$NOME_VOLUME]:-}"
if [[ -z "$CAMINHO" ]]; then
  echo "Não reconheço '$NOME_VOLUME' como volume sensível conhecido (esperado: ${!CAMINHO_NO_CONTAINER[*]})." >&2
  exit 1
fi

CHECKSUM="${ARQUIVO}.sha256"
if [[ ! -f "$CHECKSUM" ]]; then
  echo "Checksum obrigatório não encontrado: $CHECKSUM" >&2
  exit 1
fi
(cd "$(dirname "$ARQUIVO")" && sha256sum -c "$(basename "$CHECKSUM")") || {
  echo "Checksum inválido para $ARQUIVO — arquivo corrompido ou adulterado." >&2
  exit 1
}
gzip -t "$ARQUIVO"

echo "ATENÇÃO: isso vai APAGAR o conteúdo atual do volume '$NOME_VOLUME' (caminho $CAMINHO no backend)"
echo "e substituir pelo conteúdo de:"
echo "  $ARQUIVO"
read -r -p "Digite RESTAURAR para confirmar: " confirmacao
[[ "$confirmacao" == "RESTAURAR" ]] || { echo "Cancelado."; exit 1; }

cd "$PROJETO"
BACKEND_CONTAINER="$("${COMPOSE[@]}" ps -a -q backend)"
if [[ -n "$BACKEND_CONTAINER" ]]; then
  echo "Parando o backend para evitar escrita durante a restauração..."
  "${COMPOSE[@]}" stop backend
fi

ARQUIVO_ABS="$(cd "$(dirname "$ARQUIVO")" && pwd)/$(basename "$ARQUIVO")"
echo "Limpando e restaurando '$CAMINHO'..."
"${COMPOSE[@]}" run --rm -T --no-deps \
  -v "$(dirname "$ARQUIVO_ABS"):/backup-entrada:ro" \
  backend \
  sh -c "find '$CAMINHO' -mindepth 1 -delete && tar -xzf '/backup-entrada/$(basename "$ARQUIVO_ABS")' -C '$CAMINHO'"

echo "Religando o backend..."
"${COMPOSE[@]}" up -d backend
echo "Restauração de '$NOME_VOLUME' concluída. Confira o volume e o comportamento do KYC/receituário antes de encerrar o incidente."
