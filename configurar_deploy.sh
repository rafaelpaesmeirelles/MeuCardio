#!/usr/bin/env bash
# Cria um usuário 'deploy' sem privilégio de root, com permissão só pra rodar
# Docker (necessário pra subir/reiniciar os serviços) e escrever na pasta do
# projeto. NÃO tem sudo, NÃO tem senha, só entra por chave SSH.
#
# Rodar UMA VEZ, como root, no servidor:
#   sudo bash configurar_deploy.sh "CHAVE_PUBLICA_AQUI"
set -euo pipefail

CHAVE_PUBLICA="${1:-}"
PROJETO="/opt/meucardio"

if [ -z "$CHAVE_PUBLICA" ]; then
  echo "Uso: sudo bash configurar_deploy.sh \"ssh-ed25519 AAAA... meucardio-deploy-claude\""
  exit 1
fi

if ! id deploy &>/dev/null; then
  useradd -m -s /bin/bash deploy
  echo "Usuário 'deploy' criado."
else
  echo "Usuário 'deploy' já existe, reaproveitando."
fi

usermod -aG docker deploy

mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh

# restrições na própria linha da chave: sem encaminhamento de porta, sem X11,
# sem agent forwarding — reduz o que a chave pode fazer mesmo com acesso normal
echo "restrict $CHAVE_PUBLICA" > /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh

# deploy só escreve dentro da pasta do projeto
chown -R deploy:deploy "$PROJETO" 2>/dev/null || echo "Aviso: ajuste manual de dono de $PROJETO pode ser necessário."

echo
echo "Pronto. Testando localmente..."
su - deploy -c "docker ps" && echo "deploy consegue rodar docker — ok" || echo "AVISO: deploy sem acesso a docker, confira o grupo"

echo
echo "Não esqueça: sem senha, sem sudo. Se precisar revogar depois:"
echo "  sudo userdel -r deploy"
