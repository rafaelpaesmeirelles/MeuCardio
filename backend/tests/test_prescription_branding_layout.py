"""Real PDF geometry without app imports, settings, DB or pytest conftest.

Run directly: python -B backend/tests/test_prescription_branding_layout.py
Optional --demo-dir /tmp/... emits explicitly fictitious PDFs and page PNGs.
"""
import ast
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import pdfplumber
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.units import mm


SERVICES = Path(__file__).resolve().parents[1] / "app/services"
DATE = datetime(2026, 9, 11, 12, tzinfo=timezone.utc)


def _load(name, injected=None):
    path = SERVICES / name
    tree = ast.parse(path.read_text())
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and (node.module or "").startswith("app.")
    )]
    namespace = {"__file__": str(path), "__name__": "isolated_pdf_layout", **(injected or {})}
    exec(compile(tree, str(path), "exec"), namespace)
    return SimpleNamespace(**namespace)


def load_renderers(marker):
    # Real pure formatting helpers; intentionally never load profile settings.
    tree = ast.parse((SERVICES / "professional_profile.py").read_text())
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name in {"professional_name", "workplace_lines"}]
    profile = {"Any": object}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "<pure-profile-formatters>", "exec"), profile)
    brand = _load("pdf/marca.py")
    wrapping = _load("pdf/wrapping.py").wrap_text
    institution = _load("pdf/identidade_institucional.py", {"wrap_text": wrapping})
    common = {"logo_path": lambda url: marker if url == "/logos/demonstrativo.png" else None,
              "professional_name": profile["professional_name"], "workplace_lines": profile["workplace_lines"],
              "wrap_text": wrapping, "EMPRESA": institution.EMPRESA,
              "desenhar_identidade_institucional": institution.desenhar_identidade_institucional,
              "LOGO": brand.LOGO, "logo_disponivel": brand.logo_disponivel,
              "COBRE": brand.COBRE, "NAVY": brand.NAVY}
    regulated = _load("receita_controle_especial.py", common)
    ordinary = _load("pdf_documento.py", {**common, "_logo_corvia": regulated._logo_corvia,
                                          "_logo_profissional": regulated._logo_profissional})
    return regulated, ordinary


def marker_image(path, size):
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((3, 3, size[0]-4, size[1]-4), radius=12, outline="#52605a", width=4)
    font = ImageFont.load_default(size=max(14, min(size)//5))
    draw.text((size[0]/2, size[1]*.40), "DEMO", fill="#263936", font=font, anchor="mm")
    small = ImageFont.load_default(size=max(10, min(size)//15))
    draw.text((size[0]/2, size[1]*.65), "LOGOTIPO", fill="#52605a", font=small, anchor="mm")
    draw.text((size[0]/2, size[1]*.76), "PROFISSIONAL", fill="#52605a", font=small, anchor="mm")
    image.save(path)


def fixture(long=False, c5=False):
    doctor = dict(full_name="Profissional Fictício de Demonstração", professional_title="",
                  profession="Medicina — demonstração", specialty="Especialidade demonstrativa",
                  council_name="CRM", council_number="000000-DEMO", council_state="SP", crm=None,
                  cpf="DOCUMENTO FICTÍCIO", document_logo_url="/logos/demonstrativo.png", rqe=None,
                  include_workplace_on_documents=long,
                  workplace_name="Estabelecimento Fictício de Demonstração de Cabeçalho e Identidade",
                  workplace_department="Departamento Demonstrativo de Validação Visual",
                  workplace_role="Profissional fictício — sem validade para atendimento",
                  workplace_notes="Informação demonstrativa para verificar quebra de linhas")
    address = dict(logradouro="Rua Fictícia de Demonstração", numero="0", complemento="Sala Modelo",
                   bairro="Bairro Fictício", cidade="Cidade Demonstrativa", uf="SP", cep="00000-000",
                   telefone="TELEFONE FICTÍCIO")
    patient = {"nome": "PACIENTE FICTÍCIO — DEMONSTRAÇÃO SEM VALIDADE",
               "documento": "DOCUMENTO FICTÍCIO",
               "endereco": "Rua Fictícia, 0 - Bairro Fictício - Cidade Demonstrativa/SP - CEP 00000-000"}
    item = {"descricao": "ITEM DEMONSTRATIVO — NÃO É MEDICAMENTO", "apresentacao": "Sem apresentação clínica",
            "quantidade": "0 unidades (zero unidades)", "lista": "C5" if c5 else "C1",
            "posologia": "NÃO UTILIZAR. EXEMPLO DE DIAGRAMAÇÃO SEM VALIDADE CLÍNICA.",
            "orientacao": "Marcador técnico no lugar do logotipo profissional; nenhum símbolo real foi reproduzido."}
    if long:
        item["posologia"] += " " + "LINHADEMO " * 150
    return doctor, address, patient, [item], "DEMONSTRAÇÃO SEM VALIDADE. " + ("OBSDEMO " * 70 if long else "Não assinar nem dispensar.")


def make_pdf(renderer, kind, long=False, c5=False, digital=False):
    doctor, address, patient, items, notes = fixture(long, c5)
    if kind == "rce":
        return renderer.receita_controle_especial(destinatario=patient, itens=items, observacoes=notes,
            medico=doctor, endereco_profissional=address, data_emissao=DATE,
            cid="DEMONSTRATIVO" if c5 else None, metodo_assinatura="A1_ARQUIVO" if digital else "MANUAL")
    if kind in {"atestado", "laudo"}:
        body = (
            f"{patient['nome']}\nDEMONSTRAÇÃO DE DIAGRAMAÇÃO — SEM VALIDADE CLÍNICA.\n"
            "Este exemplo não certifica comparecimento, afastamento, diagnóstico ou resultado de exame.\n"
            "Os dados do paciente e do profissional são fictícios. O logotipo profissional é um marcador técnico.\n"
            "Os dados institucionais da operadora são os canônicos, reproduzidos com autorização."
        )
        if long:
            body += "\n" + "\n".join(f"REGISTRODEMO {index:03d} — Texto de diagramação sem significado clínico." for index in range(65))
        return renderer.documento_generico(f"{kind.title()} — DEMONSTRATIVO SEM VALIDADE", body,
                                           doctor, DATE, endereco=address)
    return renderer.receituario_comum(patient, items, doctor, DATE, observacoes=notes, endereco=address)


def assert_safe_text(page, margin):
    for char in page.chars:
        assert char["x0"] >= margin-.5 and char["x1"] <= page.width-margin+.5, char
        assert 0 <= char["top"] <= char["bottom"] <= page.height
        if not char["text"].strip():
            continue
        for image in page.images:
            intersects = char["x0"] < image["x1"]-.2 and char["x1"] > image["x0"]+.2 and char["top"] < image["bottom"]-.2 and char["bottom"] > image["top"]+.2
            assert not intersects, ("text overlaps image", char["text"])


def assert_institution(page):
    start = page.search("Operadora da plataforma CorVIA")[0]
    end = page.search("38240-000")[0]
    # Generic documents have independent parallel columns. Extract the actual
    # institutional column so adjacent professional lines cannot interleave it.
    boxed = bool(page.search("IDENTIFICAÇÃO DO EMITENTE"))
    regulated = bool(page.search("RECEITA DE CONTROLE ESPECIAL"))
    right = start["x0"]+60*mm if regulated else page.width-start["x0"] if boxed else start["x0"]+65*mm
    block = page.crop((start["x0"]-.1, start["top"]-.1, right+.1, end["bottom"]+.1))
    text = " ".join(block.extract_text().split())
    for required in (
        "Operadora da plataforma CorVIA",
        "Meirelles e Maluf Serviços Médicos e Biomédicos Ltda.",
        "CNPJ 53.382.596/0001-06", "Av. 11, 423", "Centro",
        "Itapagipe/MG", "CEP 38240-000",
    ):
        assert required in text, (page.page_number, required)
    physician = page.crop((page.width/2+20*mm, 0, page.width,
                           start["top"] if boxed and not regulated else end["bottom"]+30*mm))
    physician_text = " ".join(physician.extract_text().split())
    assert "Profissional Fictício de Demonstração" in physician_text
    assert "CRM-SP 000000-DEMO" in physician_text or "CRM 000000-DEMO/SP" in physician_text
    assert block.chars and all(char["size"] >= 8-.01 for char in block.chars)
    return {"page": page.page_number, "institution_present": True,
            "operator_label": "Operadora da plataforma CorVIA"}


def geometry(data, margin):
    result = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            assert len(page.images) == 2, (number, "both identities required")
            brand = next(image for image in page.images if image["srcsize"] == (1800, 480))
            personal = next(image for image in page.images if image is not brand)
            assert abs((brand["top"]+brand["bottom"])/2 - (personal["top"]+personal["bottom"])/2) < .1
            assert brand["x1"] + 2*mm < personal["x0"]
            boxes = [rect for rect in page.rects if all(rect["x0"] <= im["x0"] and rect["x1"] >= im["x1"]
                     and rect["top"] <= im["top"] and rect["bottom"] >= im["bottom"] for im in page.images)]
            assert boxes, (number, "logos must share the issuer rectangle")
            assert_safe_text(page, margin)
            assert_institution(page)
            if page.search("RECEITA DE CONTROLE ESPECIAL"):
                start = page.search("Operadora da plataforma CorVIA")[0]
                end = page.search("38240-000")[0]
                assert start["top"] > brand["bottom"] + mm, "operator must be below its logo"
                operator = page.crop((brand["x0"]-.1, start["top"]-.1, brand["x0"]+60*mm+.1, end["bottom"]+.1))
                assert operator.chars and all(char["x1"] <= brand["x0"]+60*mm+.1 for char in operator.chars)
                assert operator.bbox[2] + 2*mm < personal["x0"], "operator must remain in the left column"
                assert not any(line["x0"] <= boxes[0]["x0"]+.1 and line["x1"] >= boxes[0]["x1"]-.1
                               and boxes[0]["top"]+.1 < line["top"] < boxes[0]["bottom"]-.1 for line in page.lines), "no transverse institutional band"
            for field in ("Operadora da plataforma CorVIA", "53.382.596/0001-06", "38240-000"):
                for match in page.search(field):
                    assert any(rect["x0"] <= match["x0"] and rect["x1"] >= match["x1"]
                               and rect["top"] <= match["top"] and rect["bottom"] >= match["bottom"] for rect in boxes)
            result.append({"page": number, "corvia_mm": [brand["width"]/mm, brand["height"]/mm],
                           "professional_mm": [personal["width"]/mm, personal["height"]/mm],
                           "issuer_box_mm": [boxes[0]["x0"]/mm, boxes[0]["top"]/mm, boxes[0]["width"]/mm, boxes[0]["height"]/mm]})
    return result


class PrescriptionBrandingLayoutTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="corvia-rx-branding-")
        self.addCleanup(self.directory.cleanup)
        self.marker = Path(self.directory.name) / "demonstrativo.png"
        marker_image(self.marker, (300, 300))
        self.rce, self.common = load_renderers(self.marker)

    def test_rce_operator_below_logo_in_left_column_short_long_and_upload_ratios(self):
        for size in ((300, 300), (600, 250), (200, 500)):
            marker_image(self.marker, size)
            regulated, _ = load_renderers(self.marker)
            for long in (False, True):
                with self.subTest(size=size, long=long):
                    data = make_pdf(regulated, "rce", long=long)
                    pages = geometry(data, 14*mm)
                    self.assertEqual(len(pages) % 2, 0)
                    if not long:
                        self.assertEqual(len(pages), 2)
                    for page in pages:
                        self.assertAlmostEqual(page["corvia_mm"][0], 60, places=3)
                        self.assertLessEqual(page["professional_mm"][0], 38+.001)
                        self.assertLessEqual(page["professional_mm"][1], 34+.001)
                        self.assertAlmostEqual(page["professional_mm"][0]/page["professional_mm"][1], size[0]/size[1], places=4)

    def test_both_prescriptions_align_large_images_inside_one_issuer_box(self):
        for kind, renderer, margin in (("rce", self.rce, 14*mm), ("common", self.common, 20*mm)):
            with self.subTest(kind=kind):
                data = make_pdf(renderer, kind)
                pages = geometry(data, margin)
                self.assertEqual(len(pages), 2 if kind == "rce" else 1)
                for page in pages:
                    self.assertAlmostEqual(page["corvia_mm"][0], 60, places=3)
                    self.assertAlmostEqual(page["professional_mm"][1], 34, places=3)

    def test_portrait_and_landscape_uploads_keep_ratio_and_clear_text(self):
        for size in ((600, 250), (200, 500)):
            marker_image(self.marker, size)
            rce, common = load_renderers(self.marker)
            for kind, renderer, margin in (("rce", rce, 14*mm), ("common", common, 20*mm)):
                with self.subTest(size=size, kind=kind):
                    for page in geometry(make_pdf(renderer, kind), margin):
                        width, height = page["professional_mm"]
                        self.assertAlmostEqual(width/height, size[0]/size[1], places=4)

    def test_long_c5_repeats_header_and_preserves_both_copies_and_signature_box(self):
        data = make_pdf(self.rce, "rce", long=True, c5=True, digital=True)
        pages = geometry(data, 14*mm)
        self.assertGreater(len(pages), 2)
        self.assertEqual(len(pages) % 2, 0)
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            half = len(pdf.pages)//2
            for part in (pdf.pages[:half], pdf.pages[half:]):
                text = " ".join(page.extract_text() for page in part)
                self.assertEqual(text.count("LINHADEMO"), 150)
                self.assertEqual(text.count("OBSDEMO"), 70)
            self.assertIn("1ª via - Retenção pela Farmácia", pdf.pages[0].extract_text())
            self.assertIn("2ª via - Paciente", pdf.pages[half].extract_text())
            for page in pdf.pages:
                self.assertTrue(any(abs(rect["y0"]-76*mm)<.1 and abs(rect["height"]-20*mm)<.1 for rect in page.rects))
                for word in page.extract_words():
                    if word["text"] in {"LINHADEMO", "OBSDEMO"}:
                        self.assertLess(word["bottom"], page.height-100*mm)

    def test_common_long_text_paginates_without_losing_tokens(self):
        data = make_pdf(self.common, "common", long=True)
        self.assertGreater(len(geometry(data, 20*mm)), 1)
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            text = " ".join(page.extract_text() for page in pdf.pages)
            self.assertEqual(text.count("LINHADEMO"), 150)
            self.assertEqual(text.count("OBSDEMO"), 70)
            self.assertIn("Documento sem assinatura digital", text)

    def test_generic_document_retains_old_brand_sizes_and_centered_personal_logo(self):
        doctor, address, _, _, _ = fixture()
        data = self.common.documento_generico("Documento demonstrativo", "SEM VALIDADE", doctor, DATE, endereco=address)
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            page = pdf.pages[0]
            brand = next(image for image in page.images if image["srcsize"] == (1800,480))
            personal = next(image for image in page.images if image["srcsize"] == (300,300))
            self.assertAlmostEqual(brand["width"]/mm, 40, places=3)
            self.assertAlmostEqual(personal["height"]/mm, 22, places=3)
            self.assertAlmostEqual((personal["x0"]+personal["x1"])/2, page.width/2, places=3)
            self.assertNotIn("IDENTIFICAÇÃO DO EMITENTE", page.extract_text())
            assert_institution(page)
            assert_safe_text(page, 20*mm)

    def test_canonical_company_values_remain_unchanged_and_reexported(self):
        self.assertEqual(self.common.EMPRESA, {
            "razao_social": "Meirelles e Maluf Serviços Médicos e Biomédicos Ltda.",
            "cnpj": "53.382.596/0001-06", "logradouro": "Av. 11", "numero": "423",
            "bairro": "Centro", "cidade": "Itapagipe", "uf": "MG", "cep": "38240-000",
        })
        tree = ast.parse((SERVICES / "pdf_documento.py").read_text())
        self.assertTrue(any(isinstance(node, ast.ImportFrom)
                            and node.module == "app.services.pdf.identidade_institucional"
                            and any(name.name == "EMPRESA" for name in node.names) for node in tree.body))

    def test_oversized_identity_still_rejects_before_overflowing_regulated_fields(self):
        doctor, address, patient, items, notes = fixture(long=True)
        doctor["workplace_notes"] = "CAMPO DEMONSTRATIVO EXCESSIVAMENTE LONGO " * 200
        with self.assertRaisesRegex(ValueError, "A identificação excede o espaço do formulário"):
            self.rce.receita_controle_especial(
                destinatario=patient, itens=items, observacoes=notes, medico=doctor,
                endereco_profissional=address, data_emissao=DATE,
            )

    def test_operator_and_doctor_are_identified_on_every_short_and_long_document_page(self):
        for kind in ("rce", "common", "atestado", "laudo"):
            for long in (False, True):
                with self.subTest(kind=kind, long=long):
                    data = make_pdf(self.rce if kind == "rce" else self.common, kind, long=long)
                    with pdfplumber.open(io.BytesIO(data)) as pdf:
                        if long:
                            self.assertGreater(len(pdf.pages), 1)
                        for page in pdf.pages:
                            assert_institution(page)
                            assert_safe_text(page, (14 if kind == "rce" else 20)*mm)
                        if kind in {"atestado", "laudo"} and long:
                            text = " ".join(page.extract_text() for page in pdf.pages)
                            self.assertEqual(text.count("REGISTRODEMO"), 65)
                            self.assertIn("Documento sem assinatura digital", text)


def demonstrations(directory, institutional=False, rce_short=False):
    import pypdfium2
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / "logotipo-profissional-DEMONSTRATIVO.png"
    marker_image(marker, (300, 300))
    rce, common = load_renderers(marker)
    report = {"classification": "DEMONSTRAÇÃO DE DIAGRAMAÇÃO — SEM VALIDADE CLÍNICA",
              "professional_identity": "technical placeholder, not the user's symbol",
              "institutional_identity": "canonical operator data, reproduced with authorization; not the medical issuer",
              "no_database_or_real_issuance": True, "files": []}
    cases = (("rce", True), ("common", True), ("atestado", False), ("laudo", True)) if institutional else (
        ("rce", False), ("rce", True), ("common", False), ("common", True))
    if rce_short:
        cases = (("rce", False),)
    for kind, long in cases:
        data = make_pdf(rce if kind == "rce" else common, kind, long=long)
        stem = {"rce": "receita-rce", "common": "receita-comum", "atestado": "atestado", "laudo": "laudo"}[kind]
        path = directory / f"{stem}-{'longo' if long else 'curto'}-DEMONSTRATIVO.pdf"
        path.write_bytes(data)
        if kind in {"rce", "common"}:
            pages = geometry(data, (14 if kind == "rce" else 20)*mm)
        else:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages = [assert_institution(page) for page in pdf.pages]
                for page in pdf.pages:
                    assert_safe_text(page, 20*mm)
        document = pypdfium2.PdfDocument(data)
        pngs = []
        for index in range(len(document)):
            page = document[index]
            image = page.render(scale=1.4).to_pil()
            png = directory / f"{path.stem}-pagina-{index+1}.png"
            image.save(png)
            pngs.append(str(png))
            page.close()
        document.close()
        report["files"].append({"pdf": str(path), "geometry": pages, "pngs": pngs})
    (directory / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] in {"--demo-dir", "--institutional-demo-dir", "--rce-short-demo-dir"}:
        demonstrations(Path(sys.argv[2]), institutional=sys.argv[1] == "--institutional-demo-dir",
                       rce_short=sys.argv[1] == "--rce-short-demo-dir")
    else:
        unittest.main()
