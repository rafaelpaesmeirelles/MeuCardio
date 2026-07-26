#!/usr/bin/env bash
# Deploy do CardioBene em produção: HTTPS automático no domínio configurado.
# Rodar no servidor, dentro da pasta do projeto.
set -euo pipefail

if [ ! -f .env ]; then
  echo "Falta o arquivo .env. Rode:  cp .env.example .env   e preencha antes de continuar."
  exit 1
fi

# shellcheck disable=SC1091
source .env

for var in DOMAIN POSTGRES_PASSWORD JWT_SECRET; do
  valor="${!var:-}"
  if [ -z "$valor" ] || [[ "$valor" == troque-esta-senha* ]] || [[ "$valor" == gere-com-* ]] || [[ "$valor" == cardiobene.seudominio* ]]; then
    echo "A variável $var no .env ainda está com o valor de exemplo. Ajuste antes de continuar."
    exit 1
  fi
done

if ! command -v docker &>/dev/null; then
  echo "Docker não encontrado. Instale com:"
  echo "  curl -fsSL https://get.docker.com | sh"
  exit 1
fi

echo "Domínio: $DOMAIN"
echo "Verificando se o DNS já aponta para este servidor..."
IP_SERVIDOR=$(curl -s -4 ifconfig.me || true)
IP_DOMINIO=$(getent hosts "$DOMAIN" | awk '{print $1}' || true)
if [ -n "$IP_SERVIDOR" ] && [ -n "$IP_DOMINIO" ] && [ "$IP_SERVIDOR" != "$IP_DOMINIO" ]; then
  echo "Aviso: $DOMAIN resolve para $IP_DOMINIO, mas este servidor é $IP_SERVIDOR."
  echo "O Caddy só consegue emitir o certificado HTTPS depois que o DNS apontar certo."
  read -rp "Continuar mesmo assim? [y/N] " resp
  [ "$resp" = "y" ] || exit 1
fi

echo "Subindo os serviços..."
docker compose -f docker-compose.prod.yml up -d --build

echo "Aguardando o backend responder..."
for _ in $(seq 1 30); do
  if docker compose -f docker-compose.prod.yml exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" &>/dev/null; then
    break
  fi
  sleep 2
done

echo "Importando conteúdo científico..."
docker compose -f docker-compose.prod.yml exec -T backend python -m app.services.importer

if [ "${AI_ENABLED:-false}" = "true" ]; then
  echo "Indexando a base para a IA clínica (consome créditos do provedor)..."
  docker compose -f docker-compose.prod.yml exec -T backend python -m app.services.indexar
fi

echo
echo "Pronto. https://$DOMAIN deve responder em alguns segundos, assim que o"
echo "Caddy terminar de emitir o certificado (pode levar até 1 minuto na primeira vez)."
echo "Login inicial: ${ADMIN_EMAIL:-<ADMIN_EMAIL do .env>} / a senha que você definiu em ADMIN_PASSWORD."
echo "Troque essa senha assim que entrar."
