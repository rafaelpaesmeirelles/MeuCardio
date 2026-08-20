from pathlib import Path

path = Path(__file__).with_name("stabilize_product_backend.py")
text = path.read_text(encoding="utf-8")

# re.sub treats backslashes in a replacement string as escapes. Our generated
# source intentionally contains literal \n sequences, so use a callback.
text = text.replace(
    "    new, count = re.subn(pattern, replacement, text, count=1, flags=re.S)\n",
    "    new, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.S)\n",
)

# Current ResultadoEnvio has only (enviado, erro, assinado_smime), not provider/display fields.
text = text.replace(
    "    '                False, conta.provider, conta.display_name, False,\\n'\n"
    "    '                \"A caixa nativa CorVIA/Mail360 não aceita S/MIME neste transporte. \"\\n'\n"
    "    '                \"Escolha uma conta externa compatível ou desative a assinatura digital do e-mail.\",\\n'\n",
    "    '                False,\\n'\n"
    "    '                \"A caixa nativa CorVIA/Mail360 não aceita S/MIME. Selecione Google, Microsoft, Yahoo ou iCloud como conta padrão.\",\\n'\n",
)
text = text.replace(
    "    '                False, conta.provider, conta.display_name, False,\\n'\n"
    "    '                \"Este envio exigiu S/MIME explicitamente, mas a caixa nativa CorVIA/Mail360 \"\\n'\n"
    "    '                \"não aceita S/MIME neste transporte. Escolha uma conta externa compatível.\",\\n'\n",
    "    '                False,\\n'\n"
    "    '                \"Este envio exigiu S/MIME explicitamente, mas a caixa nativa CorVIA/Mail360 \"\\n'\n"
    "    '                \"não aceita S/MIME neste transporte. Escolha uma conta externa compatível.\",\\n'\n",
)

# Current home-location audit does not carry a detail dict. Patch the generated matcher accordingly.
text = text.replace(
    "    '    _audit(db, user, action, \"calendar_location\", item.id, {\"source\": \"profile_home_address\"})\\n'\n"
    "    '    db.commit()\\n'\n"
    "    '    db.refresh(item)\\n'\n"
    "    '    return _dump_location(item)\\n',\n"
    "    '    erro_geo = _try_geocode_calendar_location(item)\\n'\n"
    "    '    _audit(db, user, action, \"calendar_location\", item.id, {\"source\": \"profile_home_address\"})\\n'\n"
    "    '    db.commit()\\n'\n"
    "    '    db.refresh(item)\\n'\n"
    "    '    return _geocode_response(item, erro_geo)\\n',\n",
    "    '    _audit(db, user, action, \"calendar_location\", item.id)\\n'\n"
    "    '    db.commit()\\n'\n"
    "    '    db.refresh(item)\\n'\n"
    "    '    return _dump_location(item)\\n',\n"
    "    '    erro_geo = _try_geocode_calendar_location(item)\\n'\n"
    "    '    _audit(db, user, action, \"calendar_location\", item.id)\\n'\n"
    "    '    db.commit()\\n'\n"
    "    '    db.refresh(item)\\n'\n"
    "    '    return _geocode_response(item, erro_geo)\\n',\n",
)

path.write_text(text, encoding="utf-8")
print("backend stabilizer matchers corrected")
