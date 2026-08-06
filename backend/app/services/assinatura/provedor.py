"""Abstração de provedor de assinatura de documento clínico (Tarefa 4).

Molde copiado de `app/services/ia/provedor.py`: ABC + dataclass de retorno +
factory com cache e seleção por string. Trocar ou acrescentar provedor é
escrever uma classe nova e um `elif` na factory — nenhuma rota, nenhum modelo
de dado e nenhuma tela precisam mudar de novo depois disso.

Por que uma interface só para fluxo síncrono (certificado local) e
assíncrono (certificado em nuvem): assinatura em nuvem — VIDaaS, Bird ID,
SafeID, NeoID, Remote ID — exige o titular autorizar num segundo fator (app,
biometria, OTP) antes do provedor devolver o CMS; não há como isso terminar
na mesma requisição HTTP que pediu a assinatura. `Assinatura.estado`
carrega os dois casos: "assinado"/"nao_assinado" fecham na hora,
"aguardando_titular" devolve `autorizacao_url` e exige um `consultar()`
depois (rota de polling em `app/api/assinatura.py`), e "indisponivel" é a
recusa honesta — nunca um PDF com aparência de assinado sem estar.

Regra que não se flexibiliza, herdada do CLAUDE.md: **nunca simular a
assinatura**. Por isso este módulo não tenta stub por provedor — todo
provedor sem adaptador real cai em `ProvedorIndisponivel`, que diz a
verdade em vez de fingir.

`A1_ARQUIVO` (Trabalho 7, 06/08/2026) é o primeiro provedor QUALIFICADA
(ICP-Brasil) de fato implementado — certificado local do próprio médico
(`.pfx`/`.p12`), sem depender de nenhuma relação comercial com terceiro. Os
provedores em nuvem (VIDaaS, Bird ID, SafeID, NeoID, Remote ID) continuam
`ProvedorIndisponivel`, mas com mensagem "em breve" distinta — são
planejados, não abandonados; só dependem de uma conta comercial que
ninguém abriu ainda (ver ADR).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.services.assinatura import catalogo

log = logging.getLogger("meucardio.assinatura")


@dataclass
class Assinatura:
    estado: str  # "assinado" | "nao_assinado" | "aguardando_titular" | "indisponivel"
    pdf: bytes | None = None
    referencia: str | None = None       # id da operação no provedor, para consultar()
    autorizacao_url: str | None = None  # onde o titular autoriza, no fluxo em nuvem
    motivo: str | None = None           # obrigatório quando estado == "indisponivel"


class ProvedorAssinatura(ABC):
    codigo: str
    nivel: str

    @abstractmethod
    def disponivel(self) -> tuple[bool, str | None]:
        """(True, None) se pronto pra assinar agora. (False, motivo) senão —
        motivo vira o texto que a rota devolve em `bloqueios` (409), no mesmo
        formato que `receituario.py` já usa para SNCR/RCE indisponíveis."""
        ...

    @abstractmethod
    def assinar(self, pdf: bytes, medico: dict, contexto: dict) -> Assinatura:
        """`contexto` carrega o que o provedor precisa e o `pdf_documento.py`
        não sabe: tipo de documento, ids para auditoria, etc. Implementações
        síncronas devolvem estado="assinado" direto; as em nuvem podem
        devolver "aguardando_titular" e exigir `consultar()` depois."""
        ...

    def consultar(self, referencia: str) -> Assinatura:
        """Só os provedores assíncronos (fluxo em nuvem) implementam —
        default aqui existe pra quem é síncrono nem precisar sobrescrever."""
        raise NotImplementedError(f"{self.codigo} não tem operação assíncrona para consultar.")


class SemAssinaturaDigital(ProvedorAssinatura):
    """`MANUAL` — o único provedor que funciona hoje. Devolve o PDF como
    veio, para o profissional carimbar e assinar de próprio punho. Sempre
    disponível: não depende de credencial nenhuma."""

    codigo = "MANUAL"
    nivel = catalogo.NIVEL_NENHUMA

    def disponivel(self) -> tuple[bool, str | None]:
        return True, None

    def assinar(self, pdf: bytes, medico: dict, contexto: dict) -> Assinatura:
        return Assinatura(estado="nao_assinado", pdf=pdf)


class CertificadoA1(ProvedorAssinatura):
    """`A1_ARQUIVO` — certificado local do próprio médico, guardado cifrado
    (`certificado_a1.py`), assinado de fato com `pyhanko` (`pdf_signer.py`).
    Único provedor cuja disponibilidade é POR USUÁRIO, não do sistema
    inteiro — por isso recebe `db`/`user` no construtor, e `obter_provedor()`
    não usa o cache module-level pra este código (cache por código
    quebraria entre usuários diferentes)."""

    codigo = "A1_ARQUIVO"
    nivel = catalogo.NIVEL_QUALIFICADA

    def __init__(self, db: Session, user: User) -> None:
        self._db = db
        self._user = user

    def disponivel(self) -> tuple[bool, str | None]:
        from app.services.assinatura import certificado_a1

        registro = certificado_a1.obter(self._db, self._user)
        if registro is None:
            return False, "Nenhum certificado A1 conectado. Cadastre um em Minha Conta → Assinatura digital."
        from datetime import datetime, timezone

        if registro.valido_ate < datetime.now(timezone.utc):
            return False, f"Seu certificado A1 venceu em {registro.valido_ate:%d/%m/%Y} — envie um novo."
        return True, None

    def assinar(self, pdf: bytes, medico: dict, contexto: dict) -> Assinatura:
        from app.services.assinatura import certificado_a1, pdf_signer

        try:
            carregado = certificado_a1.carregar_para_assinar(self._db, self._user)
        except certificado_a1.CertificadoInvalido as exc:
            log.warning("Certificado A1 inválido no momento de assinar (owner_id=%s): %s", self._user.id, exc)
            return Assinatura(estado="indisponivel", motivo=str(exc))

        motivo_doc = f"Documento clínico — {contexto.get('tipo', 'documento')}"
        local = medico.get("municipio") or "Brasil"
        try:
            pdf_assinado = pdf_signer.assinar_pdf(
                pdf, pfx_bytes=carregado.pfx_bytes, senha=carregado.senha, motivo=motivo_doc, local=local,
            )
        except pdf_signer.FalhaAoAssinar as exc:
            log.error("Falha ao assinar PDF com certificado A1 (owner_id=%s): %s", self._user.id, exc)
            return Assinatura(estado="indisponivel", motivo=f"Falha ao assinar: {exc}")

        return Assinatura(estado="assinado", pdf=pdf_assinado, referencia=carregado.dados.numero_serie)


class ProvedorIndisponivel(ProvedorAssinatura):
    """Representa, com honestidade, qualquer provedor do catálogo que ainda
    não tem adaptador real ou credencial configurada. Uma classe só,
    parametrizada — em vez de treze stubs vazios com aparência de
    integração que não existe."""

    def __init__(self, codigo: str, nivel: str, motivo: str) -> None:
        self.codigo = codigo
        self.nivel = nivel
        self._motivo = motivo

    def disponivel(self) -> tuple[bool, str | None]:
        return False, self._motivo

    def assinar(self, pdf: bytes, medico: dict, contexto: dict) -> Assinatura:
        log.info("Tentativa de assinar com provedor indisponível: %s", self.codigo)
        return Assinatura(estado="indisponivel", motivo=self._motivo)


# Provedores em nuvem (ICP-Brasil qualificada) — planejados, não abandonados.
# Todos exigem uma relação comercial que ninguém abriu ainda (contato com AC,
# KYC, credencial de homologação) — ver o histórico de pesquisa da sessão de
# 06/08/2026. Mensagem distinta da genérica "não integrado": aqui é "em
# breve", não "sem previsão".
_NUVEM_EM_BREVE = {"VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID"}


def _motivo_padrao(codigo: str, nome: str) -> str:
    if codigo in _NUVEM_EM_BREVE:
        return (
            f"{nome} está planejado (certificado em nuvem) — em breve. "
            f"Por ora, use um certificado A1 (arquivo) se já tiver um."
        )
    return (
        f"{nome} ainda não está integrado ou a credencial não foi configurada. "
        f"Nada foi assinado."
    )


_cache: dict[str, ProvedorAssinatura] = {}


def obter_provedor(codigo: str, *, db: Session | None = None, user: User | None = None) -> ProvedorAssinatura:
    """Factory com cache por código — EXCETO `A1_ARQUIVO`, que é por usuário
    e por isso nunca entra no cache module-level (cachear por código
    misturaria o certificado de um médico com a sessão de outro).

    `codigo` desconhecido é erro de quem chama — a validação contra
    `catalogo.codigos_validos()` é feita antes, na rota, para virar 422 e
    não 500."""
    info = catalogo.info(codigo)
    if info is None:
        raise KeyError(f"Método de assinatura desconhecido: {codigo}")

    if codigo == "A1_ARQUIVO":
        if db is None or user is None:
            raise ValueError("A1_ARQUIVO exige db e user — provedor por usuário, não por sistema.")
        return CertificadoA1(db, user)

    if codigo in _cache:
        return _cache[codigo]

    if codigo == "MANUAL":
        provedor: ProvedorAssinatura = SemAssinaturaDigital()
    elif codigo == "VIDAAS" and settings.vidaas_configurado:
        # Quando a credencial VIDAAS chegar (Tarefa 4, bloqueada desde
        # 28/07/2026), a implementação real entra aqui — sem tocar em mais
        # nada deste módulo nem em quem chama `obter_provedor`.
        raise NotImplementedError(
            "vidaas_configurado ficou True, mas o adaptador real do VIDaaS "
            "ainda não foi escrito."
        )
    else:
        provedor = ProvedorIndisponivel(info.codigo, info.nivel, _motivo_padrao(info.codigo, info.nome))

    _cache[codigo] = provedor
    return provedor
