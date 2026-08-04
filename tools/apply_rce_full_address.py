#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
service = ROOT / "backend/app/services/receita_controle_especial.py"
source = service.read_text(encoding="utf-8")

old = '''def _endereco_completo(endereco: dict | None) -> str:
    if not endereco:
        return ""
'''
new = '''def _endereco_estruturado_completo(endereco: dict | None) -> bool:
    """A RCE exige endereço profissional completo, não apenas algum texto.

    Logradouro, número, município e UF são o núcleo mínimo verificável do
    endereço estruturado. Bairro, complemento e CEP continuam impressos quando
    cadastrados, mas sua ausência não transforma um endereço identificável em
    inválido.
    """
    return bool(
        endereco
        and all(_texto(endereco.get(campo)) for campo in ("logradouro", "numero", "cidade", "uf"))
    )


def _endereco_completo(endereco: dict | None) -> str:
    if not endereco:
        return ""
'''
if source.count(old) != 1:
    raise SystemExit(f"Ponto de inserção do helper encontrado {source.count(old)} vezes.")
source = source.replace(old, new, 1)

old = '''    if not endereco_profissional or not _endereco_completo(endereco_profissional):
        erros.append("Cadastre o endereço profissional completo para a Receita de Controle Especial.")
'''
new = '''    if not _endereco_estruturado_completo(endereco_profissional):
        erros.append(
            "Cadastre logradouro, número, município e UF do endereço profissional "
            "para a Receita de Controle Especial."
        )
'''
if source.count(old) != 1:
    raise SystemExit(f"Validação antiga encontrada {source.count(old)} vezes.")
source = source.replace(old, new, 1)
service.write_text(source, encoding="utf-8")

test = ROOT / "backend/tests/test_receita_controle_especial.py"
with test.open("a", encoding="utf-8") as f:
    f.write('''\n\ndef test_rce_recusa_endereco_profissional_parcial():
    endereco_parcial = {"logradouro": "Rua das Flores", "numero": "", "cidade": "", "uf": ""}
    erros = validar_requisitos_rce(
        medico=_medico(),
        destinatario={"nome": "Paciente", "documento": "123", "endereco": "Rua A, 1"},
        itens=[{
            "descricao": "Controlado", "quantidade": "10 comprimidos (dez comprimidos)",
            "lista": "C1",
        }],
        endereco_profissional=endereco_parcial,
        cid=None,
    )
    assert any("logradouro, número, município e UF" in erro for erro in erros)
''')

Path(__file__).unlink()
print("Validação estrutural do endereço profissional da RCE aplicada.")
