#!/usr/bin/env bash
# Instala o CardioBene a partir do GitHub — roda UMA VEZ no servidor.
# Depois disso, atualizar é: git pull && ./atualizar.sh --git
set -euo pipefail

REPO="https://github.com/rafaelpaesmeirelles/CardioBeneRibeirao.git"
DESTINO="/opt/cardiobene"

if [ -d "$DESTINO/.git" ]; then
  echo "$DESTINO já é um repositório git — nada a instalar, use 'git pull' direto."
  exit 0
fi

if [ -d "$DESTINO" ] && [ "$(ls -A "$DESTINO")" ]; then
  echo "Aviso: $DESTINO já existe e não está vazio."
  echo "Isto é uma instalação nova (primeira vez) ou você já tem o projeto aqui?"
  read -rp "Mover o conteúdo atual para $DESTINO.antes-do-git e continuar? [y/N] " resp
  [ "$resp" = "y" ] || exit 1
  mv "$DESTINO" "${DESTINO}.antes-do-git"
fi

git clone "$REPO" "$DESTINO"
cd "$DESTINO"
chmod +x atualizar.sh deploy.sh migrations_setup.sh infra/backup/*.sh 2>/dev/null || true

echo
if [ -f "${DESTINO}.antes-do-git/.env" ]; then
  cp "${DESTINO}.antes-do-git/.env" "$DESTINO/.env"
  echo ".env anterior copiado automaticamente — confira se está completo."
else
  echo "Falta configurar o .env:"
  echo "  cp .env.example .env && nano .env"
fi

echo
echo "Instalação concluída. Daqui pra frente, atualizar é:"
echo "  cd $DESTINO && git pull && ./atualizar.sh --git"
