"""Checagem automática de registro no conselho — generalizado para qualquer
profissão regulada (Trabalho 11, ampliação de 06/08/2026).

Pedido do Rafael: "usuarios nao medicos, especificar profissao, nome e
abreviacao do conselho de classe, regiao ou estado do registro no
respectivo conselho, e buscar para checagem as informacoes no respectivo
conselho. se nao achar e nao puder validar, libere a assinatura e o
acesso e ponha as informacoes nao verificadas junto ao cadastro do
profissional [...] que eu validarei".

Estado real, verificado antes de escrever este módulo (não presumido):
- **CRM**: o CFM tem webservice oficial (Resolução CFM 2.129/15), mas é
  pago para empresa privada e a credencial segue pendente — ver
  `crm_check.py`. Comportamento inalterado por este módulo.
- **CRO, CRBM, COREN, CRF, CREFITO, CRN, CRP, CREF, CRESS**: nenhum desses
  conselhos tem API pública documentada de consulta por número+UF (CFO,
  COFEN, CFF, COFFITO, CFN, CFP, CONFEF, CFESS e CFBM foram checados —
  todos têm busca pública em HTML/JS, sem endpoint documentado; a mesma
  razão que já barrou tentar raspar `portal.cfm.org.br` vale aqui:
  dependência frágil e não verificável não entra no sistema). Por isso a
  checagem automática destes é **estruturalmente indisponível hoje**, não
  apenas sem credencial configurada — não há credencial nenhuma a pedir.
- **OUTRO** (profissão fora da lista fixa de conselhos): idem, sem
  checagem possível por definição.

O que muda em relação ao CRM: quando a checagem automática **não está
disponível para o conselho**, `app/services/kyc/verificacao.py` libera o
acesso e a assinatura mesmo assim (ao contrário do CRM, que fica bloqueado
até confirmação automática ou aprovação manual) — decisão explícita do
Rafael, registrada na mesma mensagem, porque o escopo de prescrição dessas
profissões na Corvia já é restrito por padrão (`escopo_profissional.py`),
o que reduz o risco de liberar sem checagem confirmada.
"""

from __future__ import annotations

from app.services.kyc import crm_check
from app.services.kyc.crm_check import ResultadoChecagemCrm as ResultadoChecagemConselho

STATUS_ATIVO_CONFIRMADO = crm_check.STATUS_ATIVO_CONFIRMADO
STATUS_NAO_CONFIRMADO = crm_check.STATUS_NAO_CONFIRMADO
STATUS_ERRO_CHECAGEM = crm_check.STATUS_ERRO_CHECAGEM
STATUS_INDISPONIVEL_PARA_CONSELHO = "indisponivel_para_conselho"

# Único conselho com checagem automática implementável hoje (mesmo que a
# credencial ainda não tenha chegado) — todos os demais caem direto em
# "indisponível", sem tentar nenhuma chamada externa.
_CONSELHOS_COM_CHECAGEM_POTENCIAL = {"CRM"}


def checar_conselho(council_name: str | None, numero: str, uf: str) -> ResultadoChecagemConselho:
    from datetime import datetime, timezone

    conselho = (council_name or "").strip().upper()
    # Conselho em branco é tratado como CRM, não como "sem checagem
    # possível" — mesma convenção de `escopo_profissional.escopo_de()`,
    # pelo mesmo motivo: o cadastro já bloqueia o primeiro acesso sem
    # `council_name` preenchido, então em branco só aparece em dado
    # legado/de teste, e o histórico real da base é só de médicos.
    if not conselho or conselho in _CONSELHOS_COM_CHECAGEM_POTENCIAL:
        return crm_check.checar_crm(numero, uf)
    return ResultadoChecagemConselho(
        status=STATUS_INDISPONIVEL_PARA_CONSELHO,
        detalhe=(
            f"Não existe checagem automática disponível para o conselho "
            f"'{conselho or '(não informado)'}' — o registro informado "
            f"segue para validação manual do responsável pela Corvia."
        ),
        verificado_em=datetime.now(timezone.utc),
    )
