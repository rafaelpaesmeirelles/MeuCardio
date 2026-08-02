"""Catálogo dos métodos de assinatura de documento clínico (Tarefa 4).

Por que constante no código, e não tabela de banco como `PrescriptionType`
(ver `controlados/DESENHO.md`): lá a tabela existe porque o CONJUNTO de tipos
muda por norma (RDC), sem ninguém tocar código. Aqui um provedor só passa a
existir quando alguém escreve o adaptador correspondente em
`app/services/assinatura/provedor.py` **e** a credencial é configurada — os
dois são fatos de código/deploy, não de norma. Regime que muda com o código
não precisa de tabela; e o catálogo abaixo é lido por `obter_provedor()` e
pela rota `GET /api/assinatura/provedores`, então continua sendo a única
fonte de verdade — só não é a única fonte no banco.

O campo `nivel` não é decorativo. Nem toda assinatura eletrônica vale para
receita: só a qualificada ICP-Brasil tem presunção legal de autenticidade e é
o que farmácia e o futuro SNCR vão exigir. `avancada` (gov.br comum,
Clicksign, D4Sign, ZapSign, Autentique, DocuSign) é válida como assinatura em
geral, mas o Rafael ainda não decidiu se ela deve ficar liberada para receita
— por ora o sistema apenas avisa (ver `app/api/assinatura.py`), não bloqueia.
"""

from __future__ import annotations

from dataclasses import dataclass

NIVEL_QUALIFICADA = "qualificada"  # ICP-Brasil — farmácia aceita, SNCR vai exigir
NIVEL_AVANCADA = "avancada"        # válida, mas sem presunção ICP-Brasil
NIVEL_NENHUMA = "nenhuma"          # sem assinatura digital nenhuma


@dataclass(frozen=True)
class ProvedorInfo:
    codigo: str
    nome: str
    nivel: str
    familia: str  # "manual" | "nuvem" | "local" | "govbr" | "plataforma"


# Ordem deliberada: manual primeiro (é a única disponível hoje), depois os
# qualificados ICP-Brasil (nuvem, depois local), depois gov.br, depois as
# plataformas de assinatura eletrônica — do nível jurídico mais forte pro
# mais fraco, mesma leitura que o médico vai fazer na tela.
PROVEDORES: tuple[ProvedorInfo, ...] = (
    ProvedorInfo("MANUAL", "Sem assinatura digital — carimbo e assinatura manual",
                 NIVEL_NENHUMA, "manual"),
    ProvedorInfo("VIDAAS", "VIDaaS (Valid)", NIVEL_QUALIFICADA, "nuvem"),
    ProvedorInfo("BIRDID", "Bird ID (Soluti)", NIVEL_QUALIFICADA, "nuvem"),
    ProvedorInfo("SAFEID", "SafeID (Safeweb)", NIVEL_QUALIFICADA, "nuvem"),
    ProvedorInfo("NEOID", "NeoID (Serpro)", NIVEL_QUALIFICADA, "nuvem"),
    ProvedorInfo("REMOTEID", "Remote ID (Certisign)", NIVEL_QUALIFICADA, "nuvem"),
    ProvedorInfo("A1_ARQUIVO", "Certificado A1 (arquivo .pfx/.p12)", NIVEL_QUALIFICADA, "local"),
    ProvedorInfo("A3_TOKEN", "Certificado A3 (token/cartão)", NIVEL_QUALIFICADA, "local"),
    ProvedorInfo("GOVBR", "Assinatura gov.br", NIVEL_AVANCADA, "govbr"),
    ProvedorInfo("CLICKSIGN", "Clicksign", NIVEL_AVANCADA, "plataforma"),
    ProvedorInfo("D4SIGN", "D4Sign", NIVEL_AVANCADA, "plataforma"),
    ProvedorInfo("ZAPSIGN", "ZapSign", NIVEL_AVANCADA, "plataforma"),
    ProvedorInfo("AUTENTIQUE", "Autentique", NIVEL_AVANCADA, "plataforma"),
    ProvedorInfo("DOCUSIGN", "DocuSign", NIVEL_AVANCADA, "plataforma"),
)

_POR_CODIGO: dict[str, ProvedorInfo] = {p.codigo: p for p in PROVEDORES}


def info(codigo: str) -> ProvedorInfo | None:
    return _POR_CODIGO.get(codigo)


def codigos_validos() -> frozenset[str]:
    return frozenset(_POR_CODIGO)
