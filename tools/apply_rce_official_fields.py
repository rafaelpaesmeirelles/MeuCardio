#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "backend/app/services/receita_controle_especial.py"
source = path.read_text(encoding="utf-8")

changes = [
    (
        '''    y = _campo(c, y, "NOME COMPLETO:", _texto(destinatario.get("nome")), tamanho=9)
    y = _campo(c, y, "CPF ou, se estrangeiro, PASSAPORTE Nº:",
               _texto(destinatario.get("documento")), tamanho=9)
''',
        '''    y = _campo(c, y, "NOME COMPLETO:", _texto(destinatario.get("nome")), tamanho=9)
    y = _campo(c, y, "ENDEREÇO COMPLETO:", _texto(destinatario.get("endereco")), tamanho=9)
    y = _campo(c, y, "CPF ou, se estrangeiro, PASSAPORTE Nº:",
               _texto(destinatario.get("documento")), tamanho=9)
''',
    ),
    (
        '''    c.setFont("Helvetica-Oblique", 7.1)
    destino = "1ª via - Retenção pela Farmácia" if via == 1 else "2ª via - Paciente"
    c.drawRightString(LARGURA - MARGEM_X, 12 * mm, destino)
    c.setFont("Helvetica", 5.8)
    c.drawString(MARGEM_X, 8 * mm, f"Modelo {MODELO_VERSAO} · via {via}/2")
''',
        '''    c.setFont("Helvetica-Oblique", 7.1)
    destino = "1ª via - Retenção pela Farmácia" if via == 1 else "2ª via - Paciente"
    c.drawRightString(LARGURA - MARGEM_X, 14 * mm, destino)
    c.setFont("Helvetica", 6.5)
    c.drawString(
        MARGEM_X, 10 * mm,
        f"DATA DE IMPRESSÃO DESTE RECEITUÁRIO: {data_local} (recomendável)",
    )
    c.setFont("Helvetica", 5.8)
    c.drawString(MARGEM_X, 6 * mm, f"Modelo {MODELO_VERSAO} · via {via}/2")
''',
    ),
    (
        '''    if not _texto(destinatario.get("nome")):
        erros.append("Informe o nome completo do paciente.")
    if not _texto(destinatario.get("documento")):
        erros.append("Informe CPF ou passaporte do paciente.")
    if not itens:
        erros.append("A receita precisa conter ao menos um medicamento.")

    tem_c5 = any(_texto(item.get("lista")).upper() == "C5" for item in itens)
''',
        '''    if not _texto(destinatario.get("nome")):
        erros.append("Informe o nome completo do paciente.")
    if not _texto(destinatario.get("endereco")):
        erros.append("Informe o endereço completo do paciente.")
    if not _texto(destinatario.get("documento")):
        erros.append("Informe CPF ou passaporte do paciente.")
    if not itens:
        erros.append("A receita precisa conter ao menos um medicamento.")
    if not endereco_profissional or not _endereco_completo(endereco_profissional):
        erros.append("Cadastre o endereço profissional completo para a Receita de Controle Especial.")

    tem_c5 = any(_texto(item.get("lista")).upper() == "C5" for item in itens)
''',
    ),
    (
        '''        if not _texto(destinatario.get("endereco")):
            erros.append("Informe o endereço completo do paciente para receita de anabolizantes.")
        if not _texto(cid):
            erros.append("Informe o CID para receita de anabolizantes.")
        if not endereco_profissional or not _endereco_completo(endereco_profissional):
            erros.append("Cadastre o endereço profissional completo para receita de anabolizantes.")
''',
        '''        if not _texto(cid):
            erros.append("Informe o CID para receita de anabolizantes.")
''',
    ),
]

for old, new in changes:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Trecho encontrado {count} vezes; nenhuma alteração publicada: {old[:80]!r}")
    source = source.replace(old, new, 1)

path.write_text(source, encoding="utf-8")
Path(__file__).unlink()
print("Campos obrigatórios da RCE alinhados ao modelo físico vigente.")
