# WIP isolado — arquitetura `access_grants` (NÃO faz parte de nenhum RC)

Rascunho de uma arquitetura de entitlement/grant administrativo unificado,
começada em 11/08/2026 (issue #52) para corrigir um bug real reportado:
`assinante_ativo()` (`backend/app/core/security.py`, o gate central de
acesso aplicado por router em `app/main.py`) só verifica
`Subscription.status` — nunca olha `User.convidado`. O bypass de cobrança do
convidado vive inteiramente dentro de `criar_checkout()`
(`backend/app/api/billing.py:358`), que só executa quando o usuário visita a
tela de Assinatura e clica em "Assinar". Sem esse clique, um convidado
marcado `convidado=True` pelo admin é barrado com 402 como um visitante sem
conta.

**Decisão humana explícita (11/08/2026): esta arquitetura NÃO entra no RC em
fechamento, e a correção mínima do bug também não** — o entitlement de
convidados e a definição do entitlement de investidores ficam registrados
como **pendência pré-lançamento comercial** (ver `docs/rc-remediation-*.md`
mais recente), a ser avaliada como frente própria, com decisão futura entre:
(a) correção mínima no modelo atual (sem migration — checar `user.convidado`
diretamente em `assinante_ativo()`/`_kyc_required()`); ou (b) esta
arquitetura de `access_grants` completa (tabela nova, serviço central de
decisão, endpoints admin de grant/revoke, consolidação das rotas de
frontend).

## Arquivos deste rascunho

- `access_grant.py.wip` — model SQLAlchemy `AccessGrant` (nunca importado
  em `app/models/__init__.py` neste estado — precisa ser reintegrado
  explicitamente se esta arquitetura for retomada).
- `bd91c24fa1c9_access_grants.py.wip` — migração Alembic correspondente
  (renomeada para `.wip`, fora de `migrations/versions/` de propósito —
  **nunca foi aplicada a nenhum banco**, confirmado por `alembic current`
  antes de mover). Se esta arquitetura for retomada, conferir que
  `down_revision` ainda aponta para o head real da hora (pode ter avançado
  desde 11/08/2026) antes de mover de volta para `migrations/versions/`.

## O que falta, se esta frente for retomada

Mapeamento completo já feito nesta sessão (issue #52), não precisa ser
refeito:
- gate central: `assinante_ativo()` (`backend/app/core/security.py:242`);
- KYC: `_kyc_required()` (`backend/app/api/auth.py`), duplica a mesma
  pergunta que `assinante_ativo()` já responde;
- frontend: três cópias manualmente sincronizadas de `STATUS_COM_ACESSO`
  (`frontend/src/pages/Assinatura.tsx:75`, `MinhaConta.tsx:37`,
  `CorviaMail.tsx:28`), nenhuma delas lendo de uma fonte central;
- `/auth/me` não expõe nada sobre plano/assinatura/convidado hoje — o
  gate de billing no frontend é só reativo (intercepta 402), diferente do
  gate de KYC/onboarding, que é proativo (`frontend/src/App.tsx`).
