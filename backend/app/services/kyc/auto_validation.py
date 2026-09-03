"""Validação automática conservadora de KYC médico usando CFM + OCR local.

A aprovação automática só acontece quando todos os sinais objetivos
necessários concordam. Incerteza de OCR, indisponibilidade do CFM ou ausência
em documento vai para revisão manual — nunca vira aprovação por aproximação.

Nenhum documento/trecho de OCR sai do backend. O resultado persistido/auditado
contém somente flags e motivos; os arquivos originais continuam cifrados no
cofre KYC para revisão administrativa.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from difflib import SequenceMatcher
import io
import re
import shutil
import subprocess
import unicodedata

import fitz
from PIL import Image, ImageOps

from app.core.config import settings
from app.models.user import User
from app.services.cfm_registry import CFM_NOT_FOUND_CODE, CfmWebserviceClient, CfmWebserviceError


@dataclass(frozen=True)
class ResultadoAutoKyc:
    decisao: str  # aprovado | reprovado | manual | nao_aplicavel
    motivo: str
    conselho_status: str
    conselho_detalhe: str
    verificado_em: datetime
    checks: dict[str, bool | None] = field(default_factory=dict)


_TITULOS = {"DR", "DRA", "DOUTOR", "DOUTORA", "MEDICO", "MEDICA"}
_RE_CPF = re.compile(r"(?<!\d)(\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[-.\s]?\d{2})(?!\d)")
_RE_DATA = re.compile(r"(?<!\d)(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})(?!\d)")


def _sem_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto or "")
        if not unicodedata.combining(c)
    )


def normalizar_nome(texto: str) -> str:
    bruto = _sem_acentos(texto).upper()
    tokens = re.findall(r"[A-Z]+", bruto)
    while tokens and tokens[0] in _TITULOS:
        tokens.pop(0)
    return " ".join(tokens)


def nomes_compativeis(esperado: str, observado: str) -> bool:
    a = normalizar_nome(esperado)
    b = normalizar_nome(observado)
    if not a or not b:
        return False
    if a == b:
        return True
    ta, tb = a.split(), b.split()
    if len(ta) < 2 or len(tb) < 2 or ta[0] != tb[0] or ta[-1] != tb[-1]:
        return False
    return SequenceMatcher(None, a, b).ratio() >= 0.92


def nome_presente_no_texto(nome: str, texto: str) -> bool:
    alvo = normalizar_nome(nome)
    corpo = normalizar_nome(texto)
    if not alvo or not corpo:
        return False
    if alvo in corpo:
        return True
    tokens = alvo.split()
    # OCR frequentemente perde um nome intermediário; para aprovação exigimos
    # primeiro e último nomes e pelo menos 80% dos tokens do nome completo.
    if len(tokens) < 2 or tokens[0] not in corpo or tokens[-1] not in corpo:
        return False
    presentes = sum(1 for t in tokens if t in corpo.split())
    return presentes / len(tokens) >= 0.80


def _somente_digitos(valor: str | None) -> str:
    return re.sub(r"\D", "", valor or "")


def _ocr_imagem(content: bytes) -> str:
    executavel = shutil.which("tesseract")
    if not executavel:
        raise RuntimeError("OCR local indisponível")
    try:
        with Image.open(io.BytesIO(content)) as source:
            source.load()
            img = ImageOps.exif_transpose(source).convert("RGB")
            # Mantém boa resolução para números pequenos de CRM/CPF.
            out = io.BytesIO()
            img.save(out, format="PNG", optimize=True)
            payload = out.getvalue()
        proc = subprocess.run(
            [executavel, "stdin", "stdout", "--psm", "11", "-l", "por+eng"],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=15,
            check=True,
        )
        return proc.stdout.decode("utf-8", errors="replace")[:150_000]
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise RuntimeError("OCR local falhou") from exc


def extrair_texto_documento(content: bytes | None) -> str:
    if not content:
        return ""
    if content.startswith(b"%PDF"):
        try:
            doc = fitz.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise RuntimeError("PDF inválido para OCR") from exc
        try:
            partes: list[str] = []
            for pagina in list(doc)[:6]:
                texto = pagina.get_text("text") or ""
                if texto.strip():
                    partes.append(texto)
                # Mesmo PDF digital pode conter somente imagem.
                pix = pagina.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
                partes.append(_ocr_imagem(pix.tobytes("png")))
            return "\n".join(partes)[:250_000]
        finally:
            doc.close()
    return _ocr_imagem(content)


def _datas_equivalentes(data_esperada: date, texto: str) -> bool:
    formatos = {
        data_esperada.strftime("%d/%m/%Y"),
        data_esperada.strftime("%d-%m-%Y"),
        data_esperada.strftime("%-d/%-m/%Y"),
        data_esperada.strftime("%-d-%-m-%Y"),
    }
    encontrados = set(_RE_DATA.findall(texto))
    return bool(formatos & encontrados)


def _cpf_presente(cpf: str, texto: str) -> bool:
    alvo = _somente_digitos(cpf)
    if len(alvo) != 11:
        return False
    encontrados = {_somente_digitos(v) for v in _RE_CPF.findall(texto)}
    return alvo in encontrados or alvo in _somente_digitos(texto)


def _rqe_confirmado(rqe: str | None, especialidades: tuple[str, ...]) -> bool | None:
    esperado = _somente_digitos(rqe)
    if not esperado:
        return None
    corpus = _somente_digitos(" ".join(especialidades))
    return esperado in corpus


def validar_medico(user: User, docs) -> ResultadoAutoKyc:
    agora = datetime.now(timezone.utc)
    conselho = (user.council_name or "CRM").strip().upper()
    if conselho not in {"", "CRM"}:
        return ResultadoAutoKyc(
            decisao="nao_aplicavel",
            motivo="Validação CFM automática se aplica somente a CRM.",
            conselho_status="indisponivel_para_conselho",
            conselho_detalhe="Conselho sem validação automática pelo CFM.",
            verificado_em=agora,
        )

    crm = _somente_digitos(user.council_number or user.crm)
    uf = (user.council_state or "").strip().upper()
    if not crm or len(uf) != 2:
        return ResultadoAutoKyc(
            decisao="manual",
            motivo="CRM ou UF ausente/inválido no cadastro.",
            conselho_status="erro_checagem",
            conselho_detalhe="Dados profissionais insuficientes para consulta automática ao CFM.",
            verificado_em=agora,
        )
    if not settings.cfm_webservice_chave.strip():
        return ResultadoAutoKyc(
            decisao="manual",
            motivo="Web Service CFM ainda sem credencial configurada no backend.",
            conselho_status="erro_checagem",
            conselho_detalhe="Consulta automática CFM indisponível; revisão manual necessária.",
            verificado_em=agora,
        )

    try:
        with CfmWebserviceClient() as ws:
            cfm = ws.consultar(crm, uf)
    except CfmWebserviceError as exc:
        if exc.codigo == CFM_NOT_FOUND_CODE:
            return ResultadoAutoKyc(
                decisao="reprovado",
                motivo="CRM/UF não localizado no CFM.",
                conselho_status="nao_confirmado",
                conselho_detalhe="CRM/UF não localizado no Web Service oficial do CFM.",
                verificado_em=agora,
                checks={"cfm_localizado": False},
            )
        return ResultadoAutoKyc(
            decisao="manual",
            motivo=f"CFM indisponível para decisão automática (código {exc.codigo}).",
            conselho_status="erro_checagem",
            conselho_detalhe="Falha controlada na consulta ao CFM; revisão manual necessária.",
            verificado_em=agora,
        )

    checks: dict[str, bool | None] = {
        "cfm_localizado": True,
        "cfm_regular": cfm.is_regular,
        "crm_confere": _somente_digitos(cfm.crm_exibicao) == crm,
        "uf_confere": cfm.uf.strip().upper() == uf,
        "nome_cadastro_cfm": nomes_compativeis(user.full_name, cfm.nome),
        "rqe_confere": _rqe_confirmado(user.rqe, cfm.especialidades),
    }

    if not cfm.is_regular:
        return ResultadoAutoKyc(
            decisao="reprovado",
            motivo=f"Inscrição encontrada no CFM, porém não regular ({cfm.situacao_texto or cfm.situacao_codigo}).",
            conselho_status="nao_confirmado",
            conselho_detalhe=f"Situação cadastral CFM: {cfm.situacao_texto or cfm.situacao_codigo or 'não regular'}.",
            verificado_em=agora,
            checks=checks,
        )
    if not checks["crm_confere"] or not checks["uf_confere"] or not checks["nome_cadastro_cfm"]:
        return ResultadoAutoKyc(
            decisao="reprovado",
            motivo="Dados profissionais informados divergem do cadastro oficial do CFM.",
            conselho_status="ativo_confirmado",
            conselho_detalhe="CRM ativo no CFM, porém houve divergência cadastral objetiva.",
            verificado_em=agora,
            checks=checks,
        )
    if checks["rqe_confere"] is False:
        return ResultadoAutoKyc(
            decisao="reprovado",
            motivo="RQE informado não foi confirmado nas especialidades retornadas pelo CFM.",
            conselho_status="ativo_confirmado",
            conselho_detalhe="CRM ativo; RQE declarado exige validação manual.",
            verificado_em=agora,
            checks=checks,
        )

    try:
        prof_texto = "\n".join(filter(None, [
            extrair_texto_documento(docs.doc_profissional_frente),
            extrair_texto_documento(docs.doc_profissional_verso),
        ]))
        pessoal_texto = "\n".join(filter(None, [
            extrair_texto_documento(docs.doc_pessoal_frente),
            extrair_texto_documento(docs.doc_pessoal_verso),
            extrair_texto_documento(docs.doc_pessoal_digital),
        ]))
    except RuntimeError:
        return ResultadoAutoKyc(
            decisao="manual",
            motivo="Não foi possível ler os documentos com segurança pelo OCR local.",
            conselho_status="ativo_confirmado",
            conselho_detalhe="CRM ativo confirmado no CFM; documentos exigem revisão manual.",
            verificado_em=agora,
            checks=checks,
        )

    checks["nome_doc_profissional"] = nome_presente_no_texto(cfm.nome, prof_texto)
    checks["crm_doc_profissional"] = crm in _somente_digitos(prof_texto)
    checks["nome_doc_pessoal"] = nome_presente_no_texto(cfm.nome, pessoal_texto)
    checks["selfie_presente"] = bool(getattr(docs, "selfie", None))

    identificador_pessoal_ok: bool | None = None
    cpf = _somente_digitos(user.cpf)
    if len(cpf) == 11:
        identificador_pessoal_ok = _cpf_presente(cpf, pessoal_texto)
        checks["cpf_doc_pessoal"] = identificador_pessoal_ok
    elif user.birth_date:
        identificador_pessoal_ok = _datas_equivalentes(user.birth_date, pessoal_texto)
        checks["nascimento_doc_pessoal"] = identificador_pessoal_ok
    else:
        checks["identificador_pessoal"] = None

    necessarios = [
        checks["nome_doc_profissional"],
        checks["crm_doc_profissional"],
        checks["nome_doc_pessoal"],
        checks["selfie_presente"],
        identificador_pessoal_ok,
    ]
    if all(v is True for v in necessarios):
        return ResultadoAutoKyc(
            decisao="aprovado",
            motivo="CFM, cadastro e documentos conferem na validação automática.",
            conselho_status="ativo_confirmado",
            conselho_detalhe="CRM ativo/regular confirmado no CFM e identidade documental consistente.",
            verificado_em=agora,
            checks=checks,
        )

    # Ausência de um campo por OCR pode ser falso negativo; não transforma em
    # rejeição definitiva. O usuário fica sem acesso e vai para revisão manual.
    return ResultadoAutoKyc(
        decisao="manual",
        motivo="CFM confirmado, mas um ou mais elementos documentais não puderam ser confirmados automaticamente.",
        conselho_status="ativo_confirmado",
        conselho_detalhe="CRM ativo no CFM; documentos encaminhados para revisão manual.",
        verificado_em=agora,
        checks=checks,
    )
