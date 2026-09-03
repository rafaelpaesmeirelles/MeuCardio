"""Integração oficial CFM: carga TOTAL.ZIP + consulta pontual SOAP.

Princípios:
- TOTAL.ZIP é a fonte oficial para carga completa/local e é tratado como
  snapshot autoritativo somente depois de validação integral dos 27 arquivos.
- O Web Service é usado para consulta pontual CRM+UF, nunca para varrer a
  base inteira.
- A chave do CFM nunca entra em URL, log, exceção ou banco.
- O conteúdo oficial é preservado; normalizações servem apenas para busca e
  decisão defensiva do CorVIA.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
import re
import time
from typing import Iterable, Iterator
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile

import httpx
from sqlalchemy import or_, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.cfm_registry import CfmPhysician, CfmSyncRun

CFM_WEBSERVICE_DEFAULT_URL = (
    "https://ws.cfm.org.br:8080/WebServiceConsultaMedicos/ServicoConsultaMedicos"
)
CFM_TOTALZIP_PORTAL_URL = "https://sistemas.cfm.org.br/listamedicos/"
CFM_PORTAL_HOST = "sistemas.cfm.org.br"
CFM_WS_HOST = "ws.cfm.org.br"
CFM_MAX_ZIP_BYTES = 128 * 1024 * 1024
CFM_SYNC_ADVISORY_LOCK = 0x43464D31  # "CFM1"
CFM_TRANSIENT_ERROR_CODES = frozenset({"2010", "2030", "2040"})
CFM_NOT_FOUND_CODE = "8101"
CFM_INVALID_KEY_CODE = "3010"

UFS = frozenset(
    {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    }
)


class CfmRegistryError(RuntimeError):
    """Erro operacional seguro: nunca inclui a chave do CFM."""


class CfmDatasetError(CfmRegistryError):
    pass


class CfmDownloadError(CfmRegistryError):
    pass


class CfmWebserviceError(CfmRegistryError):
    def __init__(self, codigo: str, mensagem: str, *, transient: bool = False) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.transient = transient


@dataclass(frozen=True)
class CfmRecord:
    crm_raw: str
    uf: str
    nome: str
    tipo_inscricao_texto: str
    situacao_texto: str
    especialidades_raw: str

    @property
    def crm_consulta(self) -> str | None:
        candidato = self.crm_raw.strip()
        if not candidato.isdigit():
            return None
        numero = int(candidato)
        if numero < 1 or numero > 9_999_999:
            return None
        return str(numero)

    @property
    def identificador_valido(self) -> bool:
        return self.crm_consulta is not None

    @property
    def is_regular(self) -> bool:
        return self.situacao_texto.strip().casefold() == "ativo"


@dataclass(frozen=True)
class CfmConsultaResultado:
    crm_exibicao: str
    uf: str
    nome: str
    situacao_codigo: str | None
    situacao_texto: str
    tipo_inscricao_codigo: str | None
    tipo_inscricao_texto: str
    especialidades: tuple[str, ...]
    data_atualizacao: date | None

    @property
    def is_regular(self) -> bool:
        codigo = (self.situacao_codigo or "").strip().upper()
        if codigo:
            return codigo == "A"
        return self.situacao_texto.strip().casefold() in {"ativo", "regular"}


@dataclass
class _HtmlForm:
    method: str
    action: str
    inputs: list[tuple[str, str, str]]


class _FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.forms: list[_HtmlForm] = []
        self._current: _HtmlForm | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): (value or "") for key, value in attrs}
        if tag.lower() == "form":
            self._current = _HtmlForm(
                method=data.get("method", "get").lower(),
                action=data.get("action", ""),
                inputs=[],
            )
            self.forms.append(self._current)
            return
        if tag.lower() == "input" and self._current is not None:
            nome = data.get("name", "")
            if nome:
                self._current.inputs.append(
                    (nome, data.get("type", "text").lower(), data.get("value", ""))
                )

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "form":
            self._current = None


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        data = {key.lower(): (value or "") for key, value in attrs}
        href = data.get("href", "").strip()
        if href:
            self.links.append(href)


def _same_official_host(url: str, expected_host: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and (parsed.hostname or "").lower() == expected_host


def _credential_field(form: _HtmlForm) -> str | None:
    candidatos = [
        (nome, tipo)
        for nome, tipo, _ in form.inputs
        if tipo not in {"hidden", "submit", "button", "image", "reset", "checkbox", "radio"}
    ]
    if not candidatos:
        return None
    palavras = ("chave", "codigo", "código", "acesso", "key", "token")
    preferidos = [nome for nome, _ in candidatos if any(p in nome.casefold() for p in palavras)]
    if len(preferidos) == 1:
        return preferidos[0]
    if len(candidatos) == 1:
        return candidatos[0][0]
    return None


def descobrir_form_acesso(html: str, base_url: str = CFM_TOTALZIP_PORTAL_URL) -> tuple[str, dict[str, str], str]:
    """Descobre o formulário oficial sem inventar o nome do campo de chave.

    O código exige POST e mesmo host. Assim a credencial não aparece na URL e
    não pode ser redirecionada a terceiros.
    """
    parser = _FormParser()
    parser.feed(html)
    validos: list[tuple[str, dict[str, str], str]] = []
    for form in parser.forms:
        campo = _credential_field(form)
        if campo is None or form.method != "post":
            continue
        action = urljoin(base_url, form.action or base_url)
        if not _same_official_host(action, CFM_PORTAL_HOST):
            continue
        hidden = {
            nome: valor
            for nome, tipo, valor in form.inputs
            if tipo == "hidden" and nome != campo
        }
        validos.append((action, hidden, campo))
    if len(validos) != 1:
        raise CfmDownloadError("Não foi possível identificar com segurança o formulário oficial de acesso ao TOTAL.ZIP.")
    return validos[0]


def _validar_tamanho_zip(payload: bytes) -> bytes:
    if not payload.startswith(b"PK"):
        raise CfmDownloadError("A resposta do CFM não contém um arquivo ZIP válido.")
    if len(payload) > CFM_MAX_ZIP_BYTES:
        raise CfmDownloadError("O arquivo retornado pelo CFM excede o limite de segurança configurado.")
    return payload


def _seguir_resposta_download(client: httpx.Client, response: httpx.Response) -> bytes:
    atual = response
    for _ in range(6):
        if atual.status_code in {301, 302, 303, 307, 308}:
            location = atual.headers.get("location", "")
            destino = urljoin(str(atual.url), location)
            if not _same_official_host(destino, CFM_PORTAL_HOST):
                raise CfmDownloadError("O CFM retornou redirecionamento para host não autorizado.")
            atual = client.get(destino)
            continue
        if atual.status_code != 200:
            raise CfmDownloadError(f"O portal do CFM respondeu HTTP {atual.status_code} ao solicitar o arquivo.")
        tamanho = atual.headers.get("content-length")
        if tamanho and tamanho.isdigit() and int(tamanho) > CFM_MAX_ZIP_BYTES:
            raise CfmDownloadError("O arquivo informado pelo CFM excede o limite de segurança configurado.")
        payload = atual.content
        if payload.startswith(b"PK"):
            return _validar_tamanho_zip(payload)
        content_type = atual.headers.get("content-type", "").casefold()
        if "html" not in content_type and not payload.lstrip().startswith(b"<"):
            raise CfmDownloadError("O CFM não retornou ZIP nem uma página de continuação reconhecível.")
        texto_html = payload.decode("utf-8", errors="replace")
        parser = _LinkParser()
        parser.feed(texto_html)
        candidatos = []
        for href in parser.links:
            destino = urljoin(str(atual.url), href)
            if _same_official_host(destino, CFM_PORTAL_HOST) and urlparse(destino).path.casefold().endswith(".zip"):
                candidatos.append(destino)
        candidatos = list(dict.fromkeys(candidatos))
        if len(candidatos) != 1:
            raise CfmDownloadError("O CFM não retornou um único link oficial de ZIP após a autenticação.")
        atual = client.get(candidatos[0])
    raise CfmDownloadError("Excesso de redirecionamentos ao baixar a base oficial do CFM.")


def baixar_totalzip(chave: str, *, portal_url: str = CFM_TOTALZIP_PORTAL_URL, client: httpx.Client | None = None) -> bytes:
    chave = (chave or "").strip()
    if not chave:
        raise CfmDownloadError("A chave de acesso do CFM não está configurada no backend.")
    if not _same_official_host(portal_url, CFM_PORTAL_HOST):
        raise CfmDownloadError("URL de download do CFM fora do host oficial permitido.")
    proprio = client is None
    sessao = client or httpx.Client(timeout=httpx.Timeout(60.0, connect=20.0), follow_redirects=False)
    try:
        pagina = sessao.get(portal_url)
        if pagina.status_code != 200:
            raise CfmDownloadError(f"O portal do CFM respondeu HTTP {pagina.status_code} antes da autenticação.")
        action, hidden, campo = descobrir_form_acesso(pagina.text, str(pagina.url))
        dados = dict(hidden)
        dados[campo] = chave
        resposta = sessao.post(action, data=dados)
        return _seguir_resposta_download(sessao, resposta)
    except CfmRegistryError:
        raise
    except httpx.HTTPError as exc:
        raise CfmDownloadError("Falha de rede ao acessar o portal oficial do CFM.") from exc
    finally:
        if proprio:
            sessao.close()


def _uf_from_name(filename: str) -> str | None:
    stem = Path(filename).stem.upper()
    return stem if stem in UFS else None


def iterar_totalzip(payload: bytes) -> Iterator[CfmRecord]:
    """Valida integralmente a estrutura do snapshot antes do uso como fonte completa."""
    if not payload.startswith(b"PK"):
        raise CfmDatasetError("Arquivo CFM não possui assinatura ZIP.")
    vistos: dict[str, str] = {}
    try:
        with ZipFile(BytesIO(payload)) as archive:
            arquivos: dict[str, str] = {}
            for info in archive.infolist():
                if info.is_dir() or not info.filename.casefold().endswith(".txt"):
                    continue
                uf = _uf_from_name(info.filename)
                if uf is None:
                    raise CfmDatasetError(f"Arquivo TXT inesperado no ZIP oficial: {Path(info.filename).name}")
                if uf in arquivos:
                    raise CfmDatasetError(f"UF duplicada no ZIP oficial: {uf}")
                arquivos[uf] = info.filename
            faltantes = sorted(UFS - arquivos.keys())
            extras = sorted(arquivos.keys() - UFS)
            if faltantes or extras or len(arquivos) != 27:
                raise CfmDatasetError(
                    f"Snapshot CFM incompleto: faltantes={','.join(faltantes) or '-'} extras={','.join(extras) or '-'}"
                )
            for uf in sorted(UFS):
                nome_arquivo = arquivos[uf]
                with archive.open(nome_arquivo) as handle:
                    for numero_linha, raw in enumerate(handle, start=1):
                        try:
                            linha = raw.decode("utf-8").rstrip("\r\n")
                        except UnicodeDecodeError as exc:
                            raise CfmDatasetError(f"UTF-8 inválido em {uf}, linha {numero_linha}.") from exc
                        if not linha:
                            continue
                        campos = linha.split("!")
                        if len(campos) != 6:
                            raise CfmDatasetError(f"Registro CFM com {len(campos)} campos em {uf}, linha {numero_linha}.")
                        crm_raw, uf_linha, nome, tipo, situacao, especialidades = campos
                        uf_canonica = uf_linha.strip().upper()
                        if uf_canonica != uf:
                            raise CfmDatasetError(
                                f"UF interna {uf_canonica!r} diverge do arquivo {uf} na linha {numero_linha}."
                            )
                        if not crm_raw or not nome or not tipo or not situacao:
                            raise CfmDatasetError(f"Campo obrigatório vazio em {uf}, linha {numero_linha}.")
                        chave = f"{uf}\0{crm_raw}"
                        if chave in vistos:
                            raise CfmDatasetError(
                                f"CRM duplicado no snapshot oficial: {uf} {crm_raw!r} (linhas {vistos[chave]} e {numero_linha})."
                            )
                        vistos[chave] = str(numero_linha)
                        yield CfmRecord(
                            crm_raw=crm_raw,
                            uf=uf,
                            nome=nome,
                            tipo_inscricao_texto=tipo,
                            situacao_texto=situacao,
                            especialidades_raw=especialidades,
                        )
    except BadZipFile as exc:
        raise CfmDatasetError("Arquivo CFM corrompido ou não reconhecido como ZIP.") from exc


def validar_totalzip(payload: bytes) -> tuple[str, int, int]:
    digest = sha256(payload).hexdigest()
    total = 0
    invalidos = 0
    for registro in iterar_totalzip(payload):
        total += 1
        invalidos += int(not registro.identificador_valido)
    if total == 0:
        raise CfmDatasetError("Snapshot CFM validado sem nenhum registro.")
    return digest, total, invalidos


def _adquirir_lock(db: Session):
    conexao = db.get_bind().connect()
    ok = conexao.execute(
        text("SELECT pg_try_advisory_lock(:key)"), {"key": CFM_SYNC_ADVISORY_LOCK}
    ).scalar_one()
    if not ok:
        conexao.close()
        raise CfmRegistryError("Já existe uma sincronização CFM em execução.")
    return conexao


def _liberar_lock(conexao) -> None:
    try:
        conexao.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": CFM_SYNC_ADVISORY_LOCK})
    finally:
        conexao.close()


def _upsert_batch(db: Session, registros: list[dict]) -> None:
    if not registros:
        return
    stmt = pg_insert(CfmPhysician).values(registros)
    excl = stmt.excluded
    stmt = stmt.on_conflict_do_update(
        index_elements=["uf", "crm_raw"],
        set_={
            "crm_consulta": excl.crm_consulta,
            "crm_exibicao": excl.crm_exibicao,
            "nome": excl.nome,
            "tipo_inscricao_texto": excl.tipo_inscricao_texto,
            "situacao_texto": excl.situacao_texto,
            "especialidades_raw": excl.especialidades_raw,
            "identificador_valido": excl.identificador_valido,
            "is_regular": excl.is_regular,
            "is_current": True,
            "source_last": "totalzip",
            "last_seen_at": excl.last_seen_at,
            "last_seen_sync_id": excl.last_seen_sync_id,
            "updated_at": excl.updated_at,
        },
    )
    db.execute(stmt)


def importar_totalzip(db: Session, payload: bytes, *, expected_sha256: str | None = None, batch_size: int = 5000) -> CfmSyncRun:
    """Importa snapshot oficial idempotentemente e só desativa ausentes após sucesso total."""
    digest, total_validado, invalidos_validados = validar_totalzip(payload)
    if expected_sha256 and digest.casefold() != expected_sha256.strip().casefold():
        raise CfmDatasetError("SHA-256 do snapshot CFM diverge do valor esperado.")
    lock = _adquirir_lock(db)
    run = CfmSyncRun(
        source_type="totalzip",
        status="running",
        dataset_sha256=digest,
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    run_id = run.id
    try:
        agora = datetime.now(timezone.utc)
        batch: list[dict] = []
        total = 0
        invalidos = 0
        for registro in iterar_totalzip(payload):
            total += 1
            invalidos += int(not registro.identificador_valido)
            batch.append(
                {
                    "uf": registro.uf,
                    "crm_raw": registro.crm_raw,
                    "crm_consulta": registro.crm_consulta,
                    "crm_exibicao": registro.crm_raw,
                    "nome": registro.nome,
                    "tipo_inscricao_texto": registro.tipo_inscricao_texto,
                    "tipo_inscricao_codigo": None,
                    "situacao_texto": registro.situacao_texto,
                    "situacao_codigo": None,
                    "especialidades_raw": registro.especialidades_raw,
                    "data_atualizacao_cfm": None,
                    "identificador_valido": registro.identificador_valido,
                    "is_regular": registro.is_regular,
                    "is_current": True,
                    "source_last": "totalzip",
                    "first_seen_at": agora,
                    "last_seen_at": agora,
                    "last_live_verified_at": None,
                    "updated_at": agora,
                    "last_seen_sync_id": run_id,
                }
            )
            if len(batch) >= batch_size:
                _upsert_batch(db, batch)
                db.commit()
                batch.clear()
        _upsert_batch(db, batch)
        db.commit()
        if total != total_validado or invalidos != invalidos_validados:
            raise CfmDatasetError("Contagem mudou entre validação e importação do snapshot CFM.")

        desativados = db.execute(
            update(CfmPhysician)
            .where(
                CfmPhysician.is_current.is_(True),
                or_(CfmPhysician.last_seen_sync_id.is_(None), CfmPhysician.last_seen_sync_id != run_id),
            )
            .values(is_current=False, updated_at=datetime.now(timezone.utc))
        ).rowcount or 0
        run = db.get(CfmSyncRun, run_id)
        assert run is not None
        run.status = "success"
        run.record_count = total
        run.invalid_identifier_count = invalidos
        run.deactivated_count = int(desativados)
        run.finished_at = datetime.now(timezone.utc)
        run.detail = "Snapshot oficial CFM validado em 27 UFs e aplicado integralmente."
        db.commit()
        db.refresh(run)
        return run
    except Exception as exc:
        db.rollback()
        run = db.get(CfmSyncRun, run_id)
        if run is not None:
            run.status = "failure"
            run.finished_at = datetime.now(timezone.utc)
            run.detail = f"Sincronização abortada sem desativar ausentes: {type(exc).__name__}"
            db.commit()
        raise
    finally:
        _liberar_lock(lock)


def importar_totalzip_path(db: Session, path: str | Path, *, expected_sha256: str | None = None) -> CfmSyncRun:
    arquivo = Path(path)
    if not arquivo.is_file():
        raise CfmDatasetError("Arquivo TOTAL.ZIP informado não existe.")
    payload = arquivo.read_bytes()
    if len(payload) > CFM_MAX_ZIP_BYTES:
        raise CfmDatasetError("Arquivo TOTAL.ZIP excede o limite de segurança configurado.")
    return importar_totalzip(db, payload, expected_sha256=expected_sha256)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def _text_content(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join(t.strip() for t in element.itertext() if t and t.strip()).strip()


def _find_first(root: ET.Element, names: Iterable[str]) -> ET.Element | None:
    alvo = {name.casefold() for name in names}
    for element in root.iter():
        if _local_name(element.tag) in alvo:
            return element
    return None


def _find_child_text(element: ET.Element | None, names: Iterable[str]) -> str:
    if element is None:
        return ""
    alvo = {name.casefold() for name in names}
    for child in element.iter():
        if child is element:
            continue
        if _local_name(child.tag) in alvo:
            texto = _text_content(child)
            if texto:
                return texto
    return ""


def _parse_data_cfm(valor: str) -> date | None:
    valor = valor.strip()
    if not valor:
        return None
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor[:10], formato).date()
        except ValueError:
            continue
    return None


def _normalizar_codigo_descricao(root: ET.Element, tag: str) -> tuple[str | None, str]:
    element = _find_first(root, [tag])
    if element is None:
        return None, ""
    codigo = _find_child_text(element, ["codigo", "código", "id", "sigla"])
    descricao = _find_child_text(element, ["descricao", "descrição", "nome"])
    texto = _text_content(element)
    if not descricao:
        descricao = texto
    if codigo and descricao.startswith(codigo):
        descricao = descricao[len(codigo):].lstrip(" -–—:")
    return (codigo or None), descricao


def parse_consultar_response(xml_bytes: bytes) -> CfmConsultaResultado:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise CfmWebserviceError("xml", "O CFM retornou XML inválido.") from exc

    codigo_erro_el = _find_first(root, ["codigoErro", "codErro", "codigo_erro"])
    codigo_erro = _text_content(codigo_erro_el)
    if codigo_erro and codigo_erro not in {"0", "0000"}:
        descricao = _text_content(_find_first(root, ["descricaoErro", "mensagemErro", "erro"]))
        mensagem = descricao or f"Web Service CFM recusou a consulta (código {codigo_erro})."
        raise CfmWebserviceError(
            codigo_erro,
            mensagem,
            transient=codigo_erro in CFM_TRANSIENT_ERROR_CODES,
        )

    crm = _text_content(_find_first(root, ["crm"]))
    uf = _text_content(_find_first(root, ["uf"])).strip().upper()
    nome = _text_content(_find_first(root, ["nome"]))
    if not crm or uf not in UFS or not nome:
        raise CfmWebserviceError("schema", "Resposta do CFM sem os campos obrigatórios esperados.")

    situacao_codigo, situacao_texto = _normalizar_codigo_descricao(root, "situacao")
    tipo_codigo, tipo_texto = _normalizar_codigo_descricao(root, "tipoInscricao")
    especialidades: list[str] = []
    for element in root.iter():
        if _local_name(element.tag) != "especialidade":
            continue
        valor = _text_content(element)
        if valor:
            especialidades.append(valor)
    data_texto = _text_content(_find_first(root, ["dataAtualizacao", "data_atualizacao"]))
    return CfmConsultaResultado(
        crm_exibicao=crm,
        uf=uf,
        nome=nome,
        situacao_codigo=situacao_codigo,
        situacao_texto=situacao_texto,
        tipo_inscricao_codigo=tipo_codigo,
        tipo_inscricao_texto=tipo_texto,
        especialidades=tuple(especialidades),
        data_atualizacao=_parse_data_cfm(data_texto),
    )


def _soap_envelope_consultar(crm: str, uf: str, chave: str) -> bytes:
    # ElementTree faz o escape XML da chave sem colocá-la em logs/URL.
    envelope = ET.Element("{http://schemas.xmlsoap.org/soap/envelope/}Envelope")
    body = ET.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
    consultar = ET.SubElement(body, "{http://servico.cfm.org.br/}Consultar")
    ET.SubElement(consultar, "crm").text = crm
    ET.SubElement(consultar, "uf").text = uf
    ET.SubElement(consultar, "chave").text = chave
    return ET.tostring(envelope, encoding="utf-8", xml_declaration=True)


def normalizar_crm_consulta(numero_crm: str | int) -> str:
    valor = str(numero_crm).strip()
    if not re.fullmatch(r"\d{1,7}", valor):
        raise CfmWebserviceError("4010", "CRM para consulta deve ser número natural de até 7 dígitos.")
    numero = int(valor)
    if numero < 1:
        raise CfmWebserviceError("4010", "CRM para consulta deve ser maior que zero.")
    return str(numero)


class CfmWebserviceClient:
    def __init__(self, *, chave: str | None = None, url: str | None = None, client: httpx.Client | None = None) -> None:
        self._chave = (chave if chave is not None else settings.cfm_webservice_chave).strip()
        configurada = (url if url is not None else settings.cfm_webservice_url).strip()
        self._url = configurada or CFM_WEBSERVICE_DEFAULT_URL
        if not self._chave:
            raise CfmWebserviceError("4020", "Chave do Web Service CFM não configurada no backend.")
        if not _same_official_host(self._url, CFM_WS_HOST):
            raise CfmWebserviceError("config", "URL do Web Service CFM fora do host oficial permitido.")
        self._proprio = client is None
        self._client = client or httpx.Client(timeout=httpx.Timeout(30.0, connect=15.0), follow_redirects=False)

    def close(self) -> None:
        if self._proprio:
            self._client.close()

    def consultar(self, numero_crm: str | int, uf: str, *, max_attempts: int = 2) -> CfmConsultaResultado:
        crm = normalizar_crm_consulta(numero_crm)
        uf_canonica = str(uf).strip().upper()
        if uf_canonica not in UFS:
            raise CfmWebserviceError("4000", "UF inválida para consulta ao CFM.")
        envelope = _soap_envelope_consultar(crm, uf_canonica, self._chave)
        ultimo: CfmWebserviceError | None = None
        for tentativa in range(1, max(1, max_attempts) + 1):
            try:
                response = self._client.post(
                    self._url,
                    content=envelope,
                    headers={
                        "Content-Type": "text/xml; charset=utf-8",
                        "SOAPAction": '""',
                    },
                )
                if response.status_code != 200:
                    raise CfmWebserviceError(
                        "http",
                        f"Web Service CFM respondeu HTTP {response.status_code}.",
                        transient=response.status_code >= 500,
                    )
                return parse_consultar_response(response.content)
            except CfmWebserviceError as exc:
                ultimo = exc
                if not exc.transient or tentativa >= max_attempts:
                    raise
                time.sleep(0.4 * tentativa)
            except httpx.HTTPError as exc:
                ultimo = CfmWebserviceError("network", "Falha de rede ao consultar o Web Service CFM.", transient=True)
                if tentativa >= max_attempts:
                    raise ultimo from exc
                time.sleep(0.4 * tentativa)
        assert ultimo is not None
        raise ultimo

    def __enter__(self) -> "CfmWebserviceClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def consultar_e_persistir(
    db: Session,
    numero_crm: str | int,
    uf: str,
    *,
    chave: str | None = None,
    url: str | None = None,
    client: httpx.Client | None = None,
) -> CfmConsultaResultado:
    crm = normalizar_crm_consulta(numero_crm)
    uf_canonica = str(uf).strip().upper()
    with CfmWebserviceClient(chave=chave, url=url, client=client) as ws:
        resultado = ws.consultar(crm, uf_canonica)
    agora = datetime.now(timezone.utc)
    existente = db.execute(
        select(CfmPhysician)
        .where(
            CfmPhysician.uf == uf_canonica,
            CfmPhysician.crm_consulta == crm,
        )
        .order_by(CfmPhysician.is_current.desc(), CfmPhysician.id.asc())
        .limit(1)
    ).scalar_one_or_none()
    especialidades_raw = ", ".join(resultado.especialidades)
    if existente is None:
        existente = CfmPhysician(
            uf=uf_canonica,
            crm_raw=resultado.crm_exibicao or crm,
            crm_consulta=crm,
            crm_exibicao=resultado.crm_exibicao or crm,
            nome=resultado.nome,
            tipo_inscricao_texto=resultado.tipo_inscricao_texto,
            tipo_inscricao_codigo=resultado.tipo_inscricao_codigo,
            situacao_texto=resultado.situacao_texto,
            situacao_codigo=resultado.situacao_codigo,
            especialidades_raw=especialidades_raw,
            data_atualizacao_cfm=resultado.data_atualizacao,
            identificador_valido=True,
            is_regular=resultado.is_regular,
            is_current=True,
            source_last="webservice",
            first_seen_at=agora,
            last_seen_at=agora,
            last_live_verified_at=agora,
            updated_at=agora,
        )
        db.add(existente)
    else:
        existente.crm_exibicao = resultado.crm_exibicao or existente.crm_exibicao
        existente.nome = resultado.nome
        existente.tipo_inscricao_texto = resultado.tipo_inscricao_texto
        existente.tipo_inscricao_codigo = resultado.tipo_inscricao_codigo
        existente.situacao_texto = resultado.situacao_texto
        existente.situacao_codigo = resultado.situacao_codigo
        existente.especialidades_raw = especialidades_raw
        existente.data_atualizacao_cfm = resultado.data_atualizacao
        existente.identificador_valido = True
        existente.is_regular = resultado.is_regular
        existente.is_current = True
        existente.source_last = "webservice"
        existente.last_seen_at = agora
        existente.last_live_verified_at = agora
        existente.updated_at = agora
    db.commit()
    return resultado
