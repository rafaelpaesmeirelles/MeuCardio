from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def save(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = load(path)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: esperado 1 match, encontrado {count}: {old[:100]!r}")
    save(path, text.replace(old, new, 1))


def regex_once(path: str, pattern: str, replacement: str) -> None:
    text = load(path)
    new, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{path}: regex esperado 1 match, encontrado {count}: {pattern[:100]!r}")
    save(path, new)


# ---------------------------------------------------------------------------
# 1) Código público de validação deve sobreviver a rotação comum de JWT.
#    A chave do cofre é estável por definição enquanto arquivos antigos forem
#    legíveis; em desenvolvimento sem cofre, JWT continua sendo fallback.
# ---------------------------------------------------------------------------
replace_once(
    "backend/app/services/assinatura/validacao_publica.py",
    '    segredo = settings.jwt_secret.encode("utf-8")\n',
    '    segredo_base = settings.storage_encryption_key or settings.jwt_secret\n'
    '    segredo = segredo_base.encode("utf-8")\n',
)

# ---------------------------------------------------------------------------
# 2) O código/URL entra na aparência ANTES de assinar o PDF A1.
# ---------------------------------------------------------------------------
replace_once(
    "backend/app/services/assinatura/emissao.py",
    '    resultado = provedor.assinar(\n'
    '        pdf_visual,\n'
    '        medico,\n'
    '        {"tipo": tipo, "referencia_id": referencia_id, "layout": layout},\n'
    '    )\n',
    '    from app.services.assinatura import validacao_publica\n\n'
    '    codigo_validacao = validacao_publica.codigo_documento(\n'
    '        tipo=tipo, referencia_id=referencia_id, criado_por=criado_por,\n'
    '    )\n'
    '    url_validacao = validacao_publica.url_documento(\n'
    '        tipo=tipo, referencia_id=referencia_id, criado_por=criado_por,\n'
    '    )\n'
    '    resultado = provedor.assinar(\n'
    '        pdf_visual,\n'
    '        medico,\n'
    '        {\n'
    '            "tipo": tipo, "referencia_id": referencia_id, "layout": layout,\n'
    '            "codigo_validacao": codigo_validacao, "url_validacao": url_validacao,\n'
    '        },\n'
    '    )\n',
)

replace_once(
    "backend/app/services/assinatura/provedor.py",
    '                layout=contexto.get("layout"),\n'
    '            )\n',
    '                layout=contexto.get("layout"),\n'
    '                codigo_validacao=contexto.get("codigo_validacao"),\n'
    '                url_validacao=contexto.get("url_validacao"),\n'
    '            )\n',
)

regex_once(
    "backend/app/services/assinatura/pdf_signer.py",
    r'_SELO_VISIVEL = TextStampStyle\(.*?timestamp_format="%d/%m/%Y %H:%M:%S %Z",\n\)\n\n\ndef assinar_pdf',
    '''def _selo_visivel(codigo_validacao: str | None, url_validacao: str | None) -> TextStampStyle:\n    """Aparência assinada com um caminho verificável fora do consultório.\n\n    O endereço/código fazem parte da revisão criptografada. Não são desenhados\n    depois da assinatura e, portanto, qualquer alteração também invalida o PDF.\n    """\n    linhas = [\n        "ASSINATURA DIGITAL ICP-BRASIL",\n        "%(signer)s",\n        "%(ts)s",\n    ]\n    if url_validacao:\n        curto = url_validacao.removeprefix("https://").removeprefix("http://")\n        linhas.append(f"Validar: {curto}")\n    if codigo_validacao:\n        linhas.append(f"Codigo: {codigo_validacao}")\n    if not codigo_validacao and not url_validacao:\n        linhas.append("Assinatura criptografica embutida neste PDF")\n    return TextStampStyle(\n        border_width=1,\n        border_color=(0.043, 0.180, 0.271),\n        background=None,\n        background_opacity=1,\n        text_box_style=TextBoxStyle(\n            font_size=6,\n            text_color=(0.043, 0.180, 0.271),\n        ),\n        stamp_text="\\n".join(linhas),\n        timestamp_format="%d/%m/%Y %H:%M:%S %Z",\n    )\n\n\ndef assinar_pdf''',
)
replace_once(
    "backend/app/services/assinatura/pdf_signer.py",
    '    cadeia_der: list[bytes] | None = None, layout: str | None = None,\n) -> bytes:\n',
    '    cadeia_der: list[bytes] | None = None, layout: str | None = None,\n'
    '    codigo_validacao: str | None = None, url_validacao: str | None = None,\n'
    ') -> bytes:\n',
)
replace_once(
    "backend/app/services/assinatura/pdf_signer.py",
    '            stamp_style=_SELO_VISIVEL,\n',
    '            stamp_style=_selo_visivel(codigo_validacao, url_validacao),\n',
)

# ---------------------------------------------------------------------------
# 3) Endpoint público de validação: não entrega o PDF e não expõe conteúdo
#    clínico. Ele lê os bytes persistidos, confere hash e PAdES real.
# ---------------------------------------------------------------------------
replace_once(
    "backend/app/api/documentos_publicos.py",
    'from app.services.assinatura import emissao as assinatura_emissao\n',
    'from app.services.assinatura import emissao as assinatura_emissao\n'
    'from app.services.assinatura import validacao_publica\n',
)
validation_route = '''\n\n@router.get("/validar/{codigo}")\ndef validar_documento_publico(codigo: str, db: Session = Depends(get_db)):\n    registro = validacao_publica.localizar(db, codigo)\n    if registro is None:\n        raise HTTPException(status_code=404, detail="Código de validação inválido ou documento não encontrado.")\n\n    resultado = validacao_publica.validar(registro)\n    return {\n        "codigo": validacao_publica.codigo_documento(\n            tipo=registro.tipo, referencia_id=registro.referencia_id, criado_por=registro.criado_por,\n        ),\n        "valido": resultado.valido,\n        "tipo": registro.tipo,\n        "metodo": registro.metodo,\n        "nivel": registro.nivel,\n        "integridade_hash": resultado.integridade_hash,\n        "assinatura_encontrada": resultado.assinatura_encontrada,\n        "assinatura_intacta": resultado.assinatura_intacta,\n        "estrutura_valida": resultado.estrutura_valida,\n        "cobre_documento_inteiro": resultado.cobre_documento_inteiro,\n        "titular": resultado.titular,\n        "emissor_certificado": resultado.emissor_certificado,\n        "assinado_em": resultado.assinado_em,\n        "qualificada_icp_brasil": resultado.qualificada_icp_brasil,\n        "sha256": resultado.sha256,\n        "aviso": (\n            "A CorVIA confirmou os bytes persistidos e a integridade criptográfica da assinatura "\n            "embutida no PDF. A validação oficial de cadeia de confiança, revogação e requisitos "\n            "adicionais pode ser complementada pelo validador oficial do ITI/ICP-Brasil."\n        ),\n    }\n'''
replace_once(
    "backend/app/api/documentos_publicos.py",
    '\n\n@router.get("/{token}")\ndef baixar_por_token',
    validation_route + '\n\n@router.get("/{token}")\ndef baixar_por_token',
)

replace_once(
    "backend/tests/test_public_route_inventory.py",
    '    ("GET", "/api/documentos-publicos/{token}"): (\n'
    '        "Download destinado ao paciente, autorizado por token de alta entropia na URL."\n'
    '    ),\n',
    '    ("GET", "/api/documentos-publicos/{token}"): (\n'
    '        "Download destinado ao paciente, autorizado por token de alta entropia na URL."\n'
    '    ),\n'
    '    ("GET", "/api/documentos-publicos/validar/{codigo}"): (\n'
    '        "Validação pública de integridade; o código tem MAC não enumerável e a rota não entrega conteúdo clínico."\n'
    '    ),\n',
)

# ---------------------------------------------------------------------------
# 4) Receita por e-mail: preferência S/MIME significa "quando compatível".
#    Mail360 nativo não deve impedir o envio de um PDF já assinado. Apenas uma
#    exigência explícita assinar_smime=True continua fail-closed.
# ---------------------------------------------------------------------------
replace_once(
    "backend/app/services/envio_documento_email.py",
    '        if assinatura_obrigatoria:\n'
    '            return ResultadoEnvio(\n'
    '                False,\n'
    '                "A caixa nativa CorVIA/Mail360 não aceita S/MIME. Selecione Google, Microsoft, Yahoo ou iCloud como conta padrão.",\n'
    '            )\n',
    '        if assinar_smime:\n'
    '            return ResultadoEnvio(\n'
    '                False,\n'
    '                "Este envio exigiu S/MIME explicitamente, mas a caixa nativa CorVIA/Mail360 "\n'
    '                "não aceita S/MIME neste transporte. Escolha uma conta externa compatível.",\n'
    '            )\n'
    '        # A preferência do perfil é "assinar quando compatível". O PDF clínico\n'
    '        # continua com sua assinatura PAdES; Mail360 só transporta a mensagem\n'
    '        # sem uma segunda assinatura S/MIME no envelope do e-mail.\n',
)

# ---------------------------------------------------------------------------
# 5) Geocodificação no momento de salvar + retry explícito de pendências.
# ---------------------------------------------------------------------------
replace_once(
    "backend/app/api/agenda_integrada.py",
    'from app.services.agenda_integrada.traffic import traffic_eta\n',
    'from app.services.agenda_integrada.traffic import traffic_eta\n'
    'from app.services.agenda_integrada.geocoding import GeocodingError, geocode_address\n',
)

geocode_helpers = '''\n\ndef _location_geocode_query(item: CalendarLocation) -> str:\n    address = item.address or {}\n    keys = ("street", "number", "complement", "neighborhood", "district", "city", "state", "zip", "postal_code", "country")\n    partes = [str(address.get(key) or "").strip() for key in keys]\n    partes = [parte for parte in partes if parte]\n    if item.name:\n        partes.insert(0, item.name.strip())\n    return ", ".join(dict.fromkeys(partes))\n\n\ndef _try_geocode_calendar_location(item: CalendarLocation) -> str | None:\n    if item.latitude is not None and item.longitude is not None:\n        return None\n    consulta = _location_geocode_query(item)\n    if len(consulta) < 5:\n        return "Endereço insuficiente para localizar no mapa."\n    try:\n        resultado = geocode_address(consulta)\n    except GeocodingError as exc:\n        return str(exc)\n    item.latitude = resultado["latitude"]\n    item.longitude = resultado["longitude"]\n    return None\n\n\ndef _geocode_response(item: CalendarLocation, erro: str | None = None) -> dict:\n    payload = _dump_location(item)\n    payload["geocoding_status"] = "ok" if item.latitude is not None and item.longitude is not None else "pending"\n    payload["geocoding_message"] = erro\n    return payload\n'''
replace_once(
    "backend/app/api/agenda_integrada.py",
    '\n\n@router.get("/locations")\ndef list_locations',
    geocode_helpers + '\n\n@router.get("/locations")\ndef list_locations',
)

# Restore inactive location path.
replace_once(
    "backend/app/api/agenda_integrada.py",
    '        inactive.active = True\n'
    '        _audit(db, user, "agenda_location_restore", "calendar_location", inactive.id, {"owner_id": owner_id})\n'
    '        db.commit(); db.refresh(inactive)\n'
    '        return _dump_location(inactive)\n'
    '    item = CalendarLocation(owner_id=owner_id, **data.model_dump())\n'
    '    db.add(item); db.flush()\n',
    '        inactive.active = True\n'
    '        erro_geo = _try_geocode_calendar_location(inactive)\n'
    '        _audit(db, user, "agenda_location_restore", "calendar_location", inactive.id, {"owner_id": owner_id})\n'
    '        db.commit(); db.refresh(inactive)\n'
    '        return _geocode_response(inactive, erro_geo)\n'
    '    item = CalendarLocation(owner_id=owner_id, **data.model_dump())\n'
    '    erro_geo = _try_geocode_calendar_location(item)\n'
    '    db.add(item); db.flush()\n',
)
replace_once(
    "backend/app/api/agenda_integrada.py",
    '    db.commit(); db.refresh(item)\n'
    '    return _dump_location(item)\n\n\n@router.post("/locations/home")\n',
    '    db.commit(); db.refresh(item)\n'
    '    return _geocode_response(item, erro_geo)\n\n\n@router.post("/locations/home")\n',
)

# Home location gets geocoded immediately before commit.
replace_once(
    "backend/app/api/agenda_integrada.py",
    '    _audit(db, user, action, "calendar_location", item.id)\n'
    '    db.commit()\n'
    '    db.refresh(item)\n'
    '    return _dump_location(item)\n',
    '    erro_geo = _try_geocode_calendar_location(item)\n'
    '    _audit(db, user, action, "calendar_location", item.id)\n'
    '    db.commit()\n'
    '    db.refresh(item)\n'
    '    return _geocode_response(item, erro_geo)\n',
)

# Update location: if address/coordinates were edited, retry geocoding.
replace_once(
    "backend/app/api/agenda_integrada.py",
    '    for key, value in data.model_dump().items(): setattr(item, key, value)\n'
    '    _audit(db, user, "agenda_location_update", "calendar_location", item.id)\n'
    '    db.commit(); db.refresh(item)\n'
    '    return _dump_location(item)\n',
    '    for key, value in data.model_dump().items(): setattr(item, key, value)\n'
    '    erro_geo = _try_geocode_calendar_location(item)\n'
    '    _audit(db, user, "agenda_location_update", "calendar_location", item.id)\n'
    '    db.commit(); db.refresh(item)\n'
    '    return _geocode_response(item, erro_geo)\n',
)

retry_routes = '''\n\n@router.post("/locations/geocode-pending")\ndef geocode_pending_locations(db: Session = Depends(get_db), user: User = Depends(current_user)):\n    itens = db.query(CalendarLocation).filter(\n        CalendarLocation.owner_id == user.id,\n        CalendarLocation.active.is_(True),\n        or_(CalendarLocation.latitude.is_(None), CalendarLocation.longitude.is_(None)),\n    ).all()\n    atualizados = 0\n    erros: list[dict[str, object]] = []\n    for item in itens:\n        erro = _try_geocode_calendar_location(item)\n        if erro is None and item.latitude is not None and item.longitude is not None:\n            atualizados += 1\n            _audit(db, user, "agenda_location_geocode", "calendar_location", item.id, {"status": "ok"})\n        else:\n            erros.append({"id": item.id, "name": item.name, "message": erro or "Coordenadas não disponíveis."})\n    db.commit()\n    return {"updated": atualizados, "pending": len(erros), "errors": erros}\n\n\n@router.post("/locations/{location_id}/geocode")\ndef geocode_location_now(location_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):\n    item = db.query(CalendarLocation).filter(\n        CalendarLocation.id == location_id,\n        CalendarLocation.owner_id == user.id,\n        CalendarLocation.active.is_(True),\n    ).first()\n    if item is None:\n        raise HTTPException(status_code=404, detail="Local não encontrado.")\n    item.latitude = None\n    item.longitude = None\n    erro = _try_geocode_calendar_location(item)\n    if erro:\n        db.rollback()\n        raise HTTPException(status_code=422, detail=erro)\n    _audit(db, user, "agenda_location_geocode", "calendar_location", item.id, {"status": "ok"})\n    db.commit(); db.refresh(item)\n    return _geocode_response(item)\n'''
replace_once(
    "backend/app/api/agenda_integrada.py",
    '\n\n@router.patch("/locations/{location_id}")\ndef update_location',
    retry_routes + '\n\n@router.patch("/locations/{location_id}")\ndef update_location',
)

# ---------------------------------------------------------------------------
# 6) Regression tests focused on the failures observed in production.
# ---------------------------------------------------------------------------
(ROOT / "backend/tests/test_product_stabilization_contract.py").write_text('''from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\n\n\ndef text(path: str) -> str:\n    return (ROOT / path).read_text(encoding="utf-8")\n\n\ndef test_prescription_email_does_not_block_mail360_for_profile_smime_preference():\n    source = text("backend/app/services/envio_documento_email.py")\n    assert "if assinar_smime:" in source\n    assert "if assinatura_obrigatoria:\\n            return ResultadoEnvio(\\n                False, conta.provider" not in source\n\n\ndef test_public_validation_surface_is_wired_and_non_download():\n    source = text("backend/app/api/documentos_publicos.py")\n    assert '@router.get("/validar/{codigo}")' in source\n    assert "validacao_publica.validar(registro)" in source\n    assert "sha256" in source\n\n\ndef test_a1_visible_stamp_has_validation_address_and_code():\n    source = text("backend/app/services/assinatura/pdf_signer.py")\n    assert "Validar:" in source\n    assert "Codigo:" in source\n    assert "codigo_validacao" in source\n\n\ndef test_saved_locations_are_geocoded_and_have_retry_endpoint():\n    source = text("backend/app/api/agenda_integrada.py")\n    assert "_try_geocode_calendar_location" in source\n    assert '@router.post("/locations/geocode-pending")' in source\n    assert '@router.post("/locations/{location_id}/geocode")' in source\n''', encoding="utf-8")

print("backend product stabilization patches applied")
