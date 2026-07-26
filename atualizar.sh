#!/usr/bin/env bash
# Aplica uma atualização do MeuCardio com um comando só.
# Detecta sozinho se precisa reconstruir os containers (mudou código),
# reimportar conteúdo (mudou algum .md em content/), e publicar os
# documentos já revisados — só roda o que precisa.
#
# Modo pacote (scp de um .tar.gz):
#   ./atualizar.sh meucardio-pacote.tar.gz
#
# Modo git (depois de "git pull"):
#   git pull && ./atualizar.sh --git
#
# Opções (nos dois modos):
#   --rebuild        força reconstrução dos containers mesmo sem detectar mudança
#   --sem-index      pula a reindexação da IA
#   --sem-publicar   importa e indexa mas não publica automaticamente
set -euo pipefail

PROJETO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE="docker compose -f docker-compose.prod.yml"
MODO_GIT=false
FORCAR_REBUILD=false
PULAR_INDEX=false
PULAR_PUBLICACAO=false
PACOTE=""

for arg in "$@"; do
  case "$arg" in
    --git) MODO_GIT=true ;;
    --rebuild) FORCAR_REBUILD=true ;;
    --sem-index) PULAR_INDEX=true ;;
    --sem-publicar) PULAR_PUBLICACAO=true ;;
    *.tar.gz) PACOTE="$arg" ;;
  esac
done

cd "$PROJETO"
DB_USER="$(grep -E '^POSTGRES_USER=' .env | cut -d= -f2)"

echo "[1/10] Descobrindo o que mudou..."
MUDOU_CODIGO=false
MUDOU_CONTEUDO=false
MUDOU_GALERIA=false
MUDOU_EXAMES=false
MUDOU_EVIDENCIAS=false
MUDOU_ESTUDOS=false

if [ "$MODO_GIT" = true ]; then
  if ! git rev-parse ORIG_HEAD &>/dev/null; then
    echo "Sem ORIG_HEAD — parece que não teve 'git pull' recente com mudança. Assumindo primeira instalação: checando tudo."
    LISTA=$(git ls-files)
  else
    LISTA=$(git diff --name-only ORIG_HEAD HEAD)
  fi
else
  if [ -z "$PACOTE" ] || [ ! -f "$PACOTE" ]; then
    echo "Uso: $0 <pacote.tar.gz> [--rebuild] [--sem-index]"
    echo "  ou: $0 --git [--rebuild] [--sem-index]   (depois de git pull)"
    exit 1
  fi
  LISTA=$(tar tzf "$PACOTE")
fi

echo "$LISTA" | grep -qE '^(backend|frontend)/' && MUDOU_CODIGO=true
echo "$LISTA" | grep -qE '^content/' && MUDOU_CONTEUDO=true
echo "$LISTA" | grep -qE '^galeria/' && MUDOU_GALERIA=true
echo "$LISTA" | grep -qE '^exames/' && MUDOU_EXAMES=true
echo "$LISTA" | grep -qE '^evidencias/' && MUDOU_EVIDENCIAS=true
echo "$LISTA" | grep -qE '^estudos/' && MUDOU_ESTUDOS=true

echo "   código (backend/frontend): $MUDOU_CODIGO"
echo "   conteúdo (content/):       $MUDOU_CONTEUDO"
echo "   galeria de imagens:        $MUDOU_GALERIA"
echo "   banco de exames:           $MUDOU_EXAMES"
echo "   evidências:                $MUDOU_EVIDENCIAS"
echo "   estudos:                   $MUDOU_ESTUDOS"

if [ "$MODO_GIT" = false ]; then
  echo "[2/10] Extraindo pacote..."
  tar xzf "$PACOTE"
else
  echo "[2/10] Modo git — arquivos já atualizados pelo 'git pull'."
fi

if [ "$MUDOU_CODIGO" = true ] || [ "$FORCAR_REBUILD" = true ]; then
  echo "[3/10] Código mudou — reconstruindo containers..."
  $COMPOSE up -d --build --force-recreate backend frontend-build caddy
  echo "   aguardando o backend responder..."
  for _ in $(seq 1 30); do
    $COMPOSE exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" &>/dev/null && break
    sleep 2
  done
else
  echo "[3/10] Nenhum arquivo de código no pacote — pulando rebuild."
fi

if [ "$MUDOU_CONTEUDO" = true ]; then
  echo "[4/10] Conteúdo científico mudou — importando..."
  $COMPOSE exec -T backend python -m app.services.importer

  if [ "$PULAR_INDEX" = false ]; then
    echo "       indexando pra IA..."
    $COMPOSE exec -T backend python -m app.services.indexar
  else
    echo "       (indexação pulada por --sem-index)"
  fi

  if [ "$PULAR_PUBLICACAO" = false ]; then
    echo "[5/10] Publicando documentos já revisados..."
    $COMPOSE exec -T db psql -U "$DB_USER" -c \
      "UPDATE documents SET published = true WHERE review_status = 'revisado' AND published = false;"
    $COMPOSE exec -T db psql -U "$DB_USER" -c \
      "SELECT published, count(*) FROM documents GROUP BY published;"
  else
    echo "[5/10] Publicação pulada por --sem-publicar."
  fi
else
  echo "[4/10] Nenhum arquivo em content/ — pulando importação."
  echo "[5/10] Nada a publicar."
fi

if [ "$MUDOU_GALERIA" = true ]; then
  echo "[6/10] Galeria de imagens mudou — carregando metadados..."
  $COMPOSE exec -T backend python -m app.services.carregar_galeria /galeria/metadados.json
  if [ "$PULAR_PUBLICACAO" = false ]; then
    $COMPOSE exec -T db psql -U "$DB_USER" -c \
      "UPDATE gallery_images SET published = true WHERE review_status = 'revisado' AND published = false;"
  fi
else
  echo "[6/10] Nenhuma imagem nova na galeria."
fi

if [ "$MUDOU_EXAMES" = true ]; then
  echo "[7/10] Banco de exames mudou — carregando metadados..."
  $COMPOSE exec -T backend python -m app.services.carregar_exames /exames/metadados.json
  if [ "$PULAR_PUBLICACAO" = false ]; then
    $COMPOSE exec -T db psql -U "$DB_USER" -c \
      "UPDATE lab_tests SET published = true WHERE review_status = 'revisado' AND published = false;"
  fi
else
  echo "[7/10] Nenhum exame novo."
fi

if [ "$MUDOU_EVIDENCIAS" = true ]; then
  echo "[8/10] Evidências mudaram — carregando metadados..."
  $COMPOSE exec -T backend python -m app.services.carregar_evidencias /evidencias/metadados.json
  if [ "$PULAR_PUBLICACAO" = false ]; then
    $COMPOSE exec -T db psql -U "$DB_USER" -c \
      "UPDATE evidence_records SET published = true WHERE review_status = 'revisado' AND published = false;"
  fi
else
  echo "[8/10] Nenhuma evidência nova."
fi

if [ "$MUDOU_ESTUDOS" = true ]; then
  echo "[9/10] Estudos mudaram — carregando metadados..."
  $COMPOSE exec -T backend python -m app.services.carregar_estudos /estudos/metadados.json
  if [ "$PULAR_PUBLICACAO" = false ]; then
    $COMPOSE exec -T db psql -U "$DB_USER" -c \
      "UPDATE scientific_studies SET published = true WHERE review_status = 'revisado' AND published = false;"
  fi
else
  echo "[9/10] Nenhum estudo novo."
fi

echo "[10/10] Feito."
echo
echo "Confere em https://meucardio.med.br"
