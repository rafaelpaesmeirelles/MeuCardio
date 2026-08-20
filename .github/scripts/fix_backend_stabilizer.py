from pathlib import Path

path = Path(__file__).with_name("stabilize_product_backend.py")
text = path.read_text(encoding="utf-8")

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

path.write_text(text, encoding="utf-8")
print("backend stabilizer matcher corrected")
