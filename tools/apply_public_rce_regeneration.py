#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "backend/app/api/documentos_publicos.py"
source = path.read_text(encoding="utf-8")

old = '''        destinatario = {}
        if dest:
            destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
            if dest.endereco_cifrado:
                destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)

        return receituario_comum(
            destinatario=destinatario, itens=doc.itens, observacoes=presc.notes or "",
            medico=document_identity(medico) if medico else {"full_name": ""},
            endereco=resolver_endereco(medico, doc.endereco_exibido) if medico else None,
            data_emissao=doc.emitido_em,
        )
'''
new = '''        destinatario = {"nome": "", "endereco": "", "documento": ""}
        if dest:
            destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
            if dest.endereco_cifrado:
                destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)
            if dest.documento_cifrado:
                destinatario["documento"] = cofre.decifrar_campo(dest.documento_cifrado, presc.id)

        identidade = document_identity(medico) if medico else {"full_name": ""}
        endereco = resolver_endereco(medico, doc.endereco_exibido) if medico else None
        if doc.tipo_codigo == "RCE":
            from app.services.receita_controle_especial import receita_controle_especial

            identidade = dict(identidade)
            identidade["cpf"] = medico.cpf if medico else None
            return receita_controle_especial(
                destinatario=destinatario,
                itens=doc.itens,
                observacoes=presc.notes or "",
                medico=identidade,
                endereco_profissional=endereco,
                data_emissao=doc.emitido_em,
                cid=doc.cid,
            )

        return receituario_comum(
            destinatario=destinatario, itens=doc.itens, observacoes=presc.notes or "",
            medico=identidade, endereco=endereco, data_emissao=doc.emitido_em,
        )
'''
if source.count(old) != 1:
    raise SystemExit(f"Bloco de regeneração encontrado {source.count(old)} vezes.")
source = source.replace(old, new, 1)

old = '''    return pdf, f"receituario-{doc.id}.pdf"
'''
new = '''    nome = (
        f"receita-controle-especial-{doc.id}.pdf"
        if doc.tipo_codigo == "RCE" else f"receituario-{doc.id}.pdf"
    )
    return pdf, nome
'''
if source.count(old) != 1:
    raise SystemExit(f"Nome de arquivo encontrado {source.count(old)} vezes.")
path.write_text(source.replace(old, new, 1), encoding="utf-8")

test = ROOT / "backend/tests/test_identidade_documentos_audit.py"
with test.open("a", encoding="utf-8") as f:
    f.write('''\n\ndef test_link_publico_preserva_modelo_da_receita_controle_especial():
    source = _ler("app/api/documentos_publicos.py")
    assert 'doc.tipo_codigo == "RCE"' in source
    assert "receita_controle_especial(" in source
    assert 'identidade["cpf"]' in source
    assert "cid=doc.cid" in source
''')

Path(__file__).unlink()
print("Regeneração pública da RCE corrigida.")
