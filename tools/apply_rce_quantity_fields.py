#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    source = read(path)
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: esperado 1 trecho, encontrado {count}: {old[:90]!r}")
    write(path, source.replace(old, new, 1))


# Backend schema e classificação.
replace_once(
    "backend/app/api/receituario.py",
    '''    apresentacao: str = ""
    posologia: str = ""
    orientacao: str = ""
''',
    '''    apresentacao: str = ""
    quantidade: str = ""
    quantidade_extenso: str = ""
    posologia: str = ""
    orientacao: str = ""
''',
)
replace_once(
    "backend/app/api/receituario.py",
    '''        fora.append(ItemPrescrito(
            descricao=i.descricao or (substancia or i.drug_slug or "item sem descrição"),
            substancia=substancia, apresentacao=apresentacao or None,
            posologia=i.posologia or None,
        ))
''',
    '''        quantidade = (i.quantidade or "").strip()
        quantidade_extenso = (i.quantidade_extenso or "").strip()
        quantidade_impressa = quantidade
        if quantidade_extenso:
            quantidade_impressa = f"{quantidade} ({quantidade_extenso})" if quantidade else quantidade_extenso
        fora.append(ItemPrescrito(
            descricao=i.descricao or (substancia or i.drug_slug or "item sem descrição"),
            substancia=substancia, apresentacao=apresentacao or None,
            quantidade=quantidade_impressa or None,
            posologia=i.posologia or None,
        ))
''',
)
replace_once(
    "backend/app/api/receituario.py",
    '''                    "apresentacao": i.apresentacao, "posologia": i.posologia,
''',
    '''                    "apresentacao": i.apresentacao, "quantidade": i.quantidade,
                    "posologia": i.posologia,
''',
)
replace_once(
    "backend/app/api/receituario.py",
    '''    presc = Prescription(
        patient_id=dados.patient_id, created_by=user.id, notes=dados.observacoes,
''',
    '''    rce_itens = [
        item for plano in resultado.documentos if plano.tipo == "RCE" for item in plano.itens
    ]
    if rce_itens:
        from app.services.pdf_documento import resolver_endereco
        from app.services.receita_controle_especial import validar_requisitos_rce

        medico_rce = document_identity(user)
        medico_rce["cpf"] = user.cpf
        requisitos = validar_requisitos_rce(
            medico=medico_rce,
            destinatario={
                "nome": dados.destinatario.nome,
                "endereco": dados.destinatario.endereco,
                "documento": dados.destinatario.documento,
            },
            itens=[{
                "descricao": item.descricao, "substancia": item.substancia,
                "apresentacao": item.apresentacao, "quantidade": item.quantidade,
                "posologia": item.posologia, "lista": item.lista,
            } for item in rce_itens],
            endereco_profissional=resolver_endereco(user, "profissional"),
            cid=dados.cid,
        )
        if requisitos:
            raise HTTPException(status_code=422, detail={
                "erro": "Complete os campos obrigatórios antes de criar a Receita de Controle Especial.",
                "campos": requisitos,
            })

    presc = Prescription(
        patient_id=dados.patient_id, created_by=user.id, notes=dados.observacoes,
''',
)

# PDF comum mostra quantidade quando fornecida.
replace_once(
    "backend/app/services/pdf_documento.py",
    '''        if item.get("posologia"):
            c.setFont("Helvetica", 10)
''',
    '''        if item.get("quantidade"):
            c.setFont("Helvetica", 9.5)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            for linha in _quebrar(c, f"Quantidade: {item['quantidade']}", "Helvetica", 9.5, util - 6 * mm):
                c.drawString(MARGEM + 6 * mm, y, linha)
                y -= 4.4 * mm
        if item.get("posologia"):
            c.setFont("Helvetica", 10)
''',
)

# RCE mostra e valida a quantidade em ambas as formas.
replace_once(
    "backend/app/services/receita_controle_especial.py",
    '''import io
import logging
''',
    '''import io
import logging
import re
''',
)
replace_once(
    "backend/app/services/receita_controle_especial.py",
    '''        if apresentacao:
            primeira += f" - {apresentacao}"
''',
    '''        if apresentacao:
            primeira += f" - {apresentacao}"
        quantidade = _texto(item.get("quantidade"))
        if quantidade:
            primeira += f" - Quantidade: {quantidade}"
''',
)
replace_once(
    "backend/app/services/receita_controle_especial.py",
    '''    if not itens:
        erros.append("A receita precisa conter ao menos um medicamento.")
    if not endereco_profissional or not _endereco_completo(endereco_profissional):
''',
    '''    if not itens:
        erros.append("A receita precisa conter ao menos um medicamento.")
    for indice, item in enumerate(itens, start=1):
        quantidade = _texto(item.get("quantidade"))
        extenso = quantidade.split("(", 1)[1].rsplit(")", 1)[0] if "(" in quantidade and ")" in quantidade else ""
        if not re.search(r"\\d", quantidade) or not re.search(r"[A-Za-zÀ-ÿ]", extenso):
            erros.append(
                f"Informe a quantidade do item {indice} em algarismos e por extenso "
                "(ex.: 60 comprimidos / sessenta comprimidos)."
            )
    if not endereco_profissional or not _endereco_completo(endereco_profissional):
''',
)

# Frontend: estado, payload, histórico e campos de digitação.
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''  drug_slug?: string; descricao: string; apresentacao: string; posologia: string; orientacao: string;
''',
    '''  drug_slug?: string; descricao: string; apresentacao: string;
  quantidade: string; quantidade_extenso: string; posologia: string; orientacao: string;
''',
)
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''  drug_slug: string | null; descricao: string; apresentacao: string;
  posologia: string; orientacao: string;
''',
    '''  drug_slug: string | null; descricao: string; apresentacao: string;
  quantidade: string; quantidade_extenso: string; posologia: string; orientacao: string;
''',
)
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''const ITEM_VAZIO: Item = { descricao: "", apresentacao: "", posologia: "", orientacao: "" };
''',
    '''const ITEM_VAZIO: Item = {
  descricao: "", apresentacao: "", quantidade: "", quantidade_extenso: "",
  posologia: "", orientacao: "",
};
''',
)
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''      ? { drug_slug: f.slug, descricao: f.nome, apresentacao: "", posologia: it.posologia, orientacao: it.orientacao }
''',
    '''      ? { drug_slug: f.slug, descricao: f.nome, apresentacao: "",
          quantidade: it.quantidade, quantidade_extenso: it.quantidade_extenso,
          posologia: it.posologia, orientacao: it.orientacao }
''',
)
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''      drug_slug: it.drug_slug, descricao: it.descricao, apresentacao: it.apresentacao,
      posologia: it.posologia, orientacao: it.orientacao,
''',
    '''      drug_slug: it.drug_slug, descricao: it.descricao, apresentacao: it.apresentacao,
      quantidade: it.quantidade, quantidade_extenso: it.quantidade_extenso,
      posologia: it.posologia, orientacao: it.orientacao,
''',
)
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''          apresentacao: i.apresentacao ?? "", posologia: i.posologia ?? "",
          orientacao: i.orientacao ?? "",
''',
    '''          apresentacao: i.apresentacao ?? "", quantidade: i.quantidade ?? "",
          quantidade_extenso: i.quantidade_extenso ?? "", posologia: i.posologia ?? "",
          orientacao: i.orientacao ?? "",
''',
)
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''              <label style={{ marginTop: "0.4rem" }}>Posologia</label>
              <input value={it.posologia} onChange={(e) => atualizarItem(i, "posologia", e.target.value)} />
''',
    '''              <div className="grade grade--2" style={{ marginTop: "0.4rem" }}>
                <div>
                  <label>Quantidade em algarismos</label>
                  <input value={it.quantidade} onChange={(e) => atualizarItem(i, "quantidade", e.target.value)}
                         placeholder="Ex.: 60 comprimidos" />
                </div>
                <div>
                  <label>Quantidade por extenso</label>
                  <input value={it.quantidade_extenso}
                         onChange={(e) => atualizarItem(i, "quantidade_extenso", e.target.value)}
                         placeholder="Ex.: sessenta comprimidos" />
                </div>
              </div>
              <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
                Os dois campos são obrigatórios para Receita de Controle Especial.
              </p>
              <label style={{ marginTop: "0.4rem" }}>Posologia</label>
              <input value={it.posologia} onChange={(e) => atualizarItem(i, "posologia", e.target.value)} />
''',
)
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''          <label style={{ marginTop: "0.5rem" }}>Endereço (opcional)</label>
''',
    '''          <label style={{ marginTop: "0.5rem" }}>Endereço completo (obrigatório para controle especial)</label>
''',
)

# Testes: RCE válida agora precisa das duas formas de quantidade.
test_path = ROOT / "backend/tests/test_receita_controle_especial.py"
test_source = test_path.read_text(encoding="utf-8")
test_source = test_source.replace(
    '"posologia": "Tomar 1 comprimido à noite", "lista": "C1"',
    '"quantidade": "60 comprimidos (sessenta comprimidos)", "posologia": "Tomar 1 comprimido à noite", "lista": "C1"',
)
test_source = test_source.replace(
    '"posologia": "Uso conforme prescrição", "lista": "C5"',
    '"quantidade": "10 ampolas (dez ampolas)", "posologia": "Uso conforme prescrição", "lista": "C5"',
)
test_source += '''\n\ndef test_rce_recusa_quantidade_sem_algarismos_e_extenso():
    erros = validar_requisitos_rce(
        medico=_medico(),
        destinatario={"nome": "Paciente", "documento": "123", "endereco": "Rua A, 1"},
        itens=[{"descricao": "Controlado", "quantidade": "60 comprimidos", "lista": "C1"}],
        endereco_profissional=_endereco(), cid=None,
    )
    assert any("algarismos e por extenso" in erro for erro in erros)
'''
test_path.write_text(test_source, encoding="utf-8")

with (ROOT / "docs/especificacao-perfil-documentos-prescricoes.md").open("a", encoding="utf-8") as f:
    f.write("\n- RCE: cada item exige quantidade em algarismos e por extenso, conforme art. 52, §1º, da Portaria SVS/MS nº 344/1998.\n")

Path(__file__).unlink()
print("Quantidades em algarismos e por extenso aplicadas à RCE.")
