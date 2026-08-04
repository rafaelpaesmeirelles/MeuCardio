#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
service = ROOT / "backend/app/services/receita_controle_especial.py"
source = service.read_text(encoding="utf-8")
old = '''    for indice, item in enumerate(itens, start=1):
        quantidade = _texto(item.get("quantidade"))
        extenso = quantidade.split("(", 1)[1].rsplit(")", 1)[0] if "(" in quantidade and ")" in quantidade else ""
        if not re.search(r"\\d", quantidade) or not re.search(r"[A-Za-zÀ-ÿ]", extenso):
            erros.append(
                f"Informe a quantidade do item {indice} em algarismos e por extenso "
                "(ex.: 60 comprimidos / sessenta comprimidos)."
            )
    if not endereco_profissional or not _endereco_completo(endereco_profissional):
'''
new = '''    for indice, item in enumerate(itens, start=1):
        quantidade = _texto(item.get("quantidade"))
        extenso = quantidade.split("(", 1)[1].rsplit(")", 1)[0] if "(" in quantidade and ")" in quantidade else ""
        if not re.search(r"\\d", quantidade) or not re.search(r"[A-Za-zÀ-ÿ]", extenso):
            erros.append(
                f"Informe a quantidade do item {indice} em algarismos e por extenso "
                "(ex.: 60 comprimidos / sessenta comprimidos)."
            )
    total_c1 = sum(_texto(item.get("lista")).upper() == "C1" for item in itens)
    if total_c1 > 3:
        erros.append(
            "A Receita de Controle Especial pode conter no máximo três substâncias "
            "da Lista C1 (Portaria SVS/MS nº 344/1998, art. 57)."
        )
    if not endereco_profissional or not _endereco_completo(endereco_profissional):
'''
if source.count(old) != 1:
    raise SystemExit(f"Validador encontrado {source.count(old)} vezes.")
service.write_text(source.replace(old, new, 1), encoding="utf-8")

front = ROOT / "frontend/src/pages/Receituario.tsx"
source = front.read_text(encoding="utf-8")
old = '''              <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
                Os dois campos são obrigatórios para Receita de Controle Especial.
              </p>
'''
new = '''              <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
                Os dois campos são obrigatórios para Receita de Controle Especial. A RCE aceita
                no máximo três substâncias C1 e, em regra, quantidade para até 60 dias de tratamento.
              </p>
'''
if source.count(old) != 1:
    raise SystemExit(f"Aviso frontend encontrado {source.count(old)} vezes.")
front.write_text(source.replace(old, new, 1), encoding="utf-8")

test = ROOT / "backend/tests/test_receita_controle_especial.py"
with test.open("a", encoding="utf-8") as f:
    f.write('''\n\ndef test_rce_recusa_mais_de_tres_substancias_c1():
    itens = [
        {"descricao": f"Controlado {i}", "quantidade": "10 comprimidos (dez comprimidos)", "lista": "C1"}
        for i in range(4)
    ]
    erros = validar_requisitos_rce(
        medico=_medico(),
        destinatario={"nome": "Paciente", "documento": "123", "endereco": "Rua A, 1"},
        itens=itens, endereco_profissional=_endereco(), cid=None,
    )
    assert any("no máximo três substâncias" in erro for erro in erros)
''')

Path(__file__).unlink()
print("Limite de três substâncias C1 aplicado.")
