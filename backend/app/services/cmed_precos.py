"""Baixa, casa e resolve o preço regulado da CMED (Tarefa A, CLAUDE.md).

Um só caminho de código para atualização manual (`POST /api/admin/cmed/atualizar`)
e automática (cron diário, ver `infra/cmed_cron.sh`) — as duas chamam
`atualizar(db)`. Fonte obrigatória e única: lista de preços da CMED. Nenhum
preço de outra origem, nenhuma alíquota de ICMS inventada — onde a UF não
tiver norma verificada, cai para a média nacional rotulada como tal (ver
`preco_pmc`).
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from statistics import mean

from sqlalchemy.orm import Session

from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.drug import Drug

log = logging.getLogger("meucardio.cmed")

PAGINA_PRECOS = "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
# O servidor da ANVISA devolve 403 sem User-Agent de browser — medido, não é
# tentativa de disfarce, é o mínimo pra passar do bloqueio de bot.

ARQUIVO_ICMS = Path(__file__).resolve().parent.parent / "data" / "icms_medicamentos_uf.json"

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

COL_SUBSTANCIA = 0
COL_LABORATORIO = 2
COL_GGREM = 3
COL_REGISTRO = 4
COL_EAN1 = 5
COL_PRODUTO = 8
COL_APRESENTACAO = 9
COL_CLASSE_TERAPEUTICA = 10
COL_TIPO_PRODUTO = 11
COL_RESTRICAO_HOSPITALAR = 65
COL_TARJA = 72
LINHA_CABECALHO = 42  # header ocupa a linha 42; dados começam na 43

COLUNAS_PMC = {
    39: "PMC Sem Impostos", 40: "PMC 0%", 41: "PMC 12%", 42: "PMC 12% ALC",
    43: "PMC 17%", 44: "PMC 17% ALC", 45: "PMC 17,5%", 46: "PMC 17,5% ALC",
    47: "PMC 18%", 48: "PMC 18% ALC", 49: "PMC 19%", 50: "PMC 19% ALC",
    51: "PMC 19,5%", 52: "PMC 19,5% ALC", 53: "PMC 20%", 54: "PMC 20% ALC",
    55: "PMC 20,5%", 56: "PMC 20,5% ALC", 57: "PMC 21%", 58: "PMC 21% ALC",
    59: "PMC 22%", 60: "PMC 22% ALC", 61: "PMC 22,5%", 62: "PMC 22,5% ALC",
    63: "PMC 23%", 64: "PMC 23% ALC",
}
# Colunas usadas pra "média nacional rotulada" quando a UF não tem alíquota
# verificada — só as alíquotas "cheias" (sem ALC, que é regime de área de
# livre comércio, exceção geográfica, não o caso geral de nenhuma UF).
COLUNAS_PMC_MEDIA_NACIONAL = [
    "PMC 12%", "PMC 17%", "PMC 17,5%", "PMC 18%", "PMC 19%", "PMC 19,5%",
    "PMC 20%", "PMC 20,5%", "PMC 21%", "PMC 22%", "PMC 22,5%", "PMC 23%",
]

RE_LINK_XLSX = re.compile(r'href="(https://[^"]*xls_conformidade_site[^"]*\.xlsx/@@download/file)"')
RE_DATA_URL = re.compile(r"xls_conformidade_site_(\d{8})_")


# --------------------------------------------------------------- localizar --
def localizar_url_planilha() -> tuple[str, str]:
    """Raspa o link da planilha na página da CMED — a URL tem timestamp
    (`xls_conformidade_site_<AAAAMMDD>_<ms>.xlsx`) e não é previsível por mês.
    Devolve (url, data_publicacao 'AAAAMMDD')."""
    req = urllib.request.Request(PAGINA_PRECOS, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    m = RE_LINK_XLSX.search(html)
    if not m:
        raise RuntimeError("Link da planilha CMED não encontrado na página — o layout pode ter mudado.")
    url = m.group(1)
    m_data = RE_DATA_URL.search(url)
    if not m_data:
        raise RuntimeError(f"URL da planilha sem o timestamp esperado: {url}")
    return url, m_data.group(1)


def baixar_planilha(url: str, destino: Path) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dados = resp.read()
    destino.write_bytes(dados)
    return dados


# ----------------------------------------------------------------- parser --
def _col_indice(ref: str) -> int:
    letras = ""
    for ch in ref:
        if ch.isalpha():
            letras += ch
        else:
            break
    idx = 0
    for ch in letras:
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def _carregar_strings(z: zipfile.ZipFile) -> list[str]:
    strings = []
    with z.open("xl/sharedStrings.xml") as f:
        for _, el in ET.iterparse(f):
            if el.tag == NS + "si":
                strings.append("".join(t.text or "" for t in el.iter(NS + "t")))
                el.clear()
    return strings


def _num(v: str | None) -> float | None:
    if v is None:
        return None
    try:
        return round(float(v), 2)
    except ValueError:
        return None


def parsear_linhas(caminho_xlsx: Path):
    """Gera um dict por linha de dado (a partir da linha 43), com as chaves
    de `COL_*`/`COLUNAS_PMC`. Parser em stdlib pura (zipfile + ElementTree) —
    o servidor de produção não tem openpyxl nem pip, decisão registrada no
    CLAUDE.md."""
    z = zipfile.ZipFile(caminho_xlsx)
    strings = _carregar_strings(z)
    with z.open("xl/worksheets/sheet1.xml") as f:
        for _, el in ET.iterparse(f):
            if el.tag != NS + "row":
                continue
            r = int(el.attrib["r"])
            if r <= LINHA_CABECALHO:
                el.clear()
                continue
            valores: dict[int, str] = {}
            for c in el.findall(NS + "c"):
                v_el = c.find(NS + "v")
                if v_el is None:
                    continue
                v = v_el.text
                if c.attrib.get("t") == "s":
                    v = strings[int(v)]
                valores[_col_indice(c.attrib["r"])] = v
            el.clear()
            sub = (valores.get(COL_SUBSTANCIA) or "").strip()
            if not sub:
                continue
            yield {
                "substancia": sub,
                "laboratorio": (valores.get(COL_LABORATORIO) or "").strip(),
                "produto": (valores.get(COL_PRODUTO) or "").strip(),
                "apresentacao": (valores.get(COL_APRESENTACAO) or "").strip(),
                "ggrem": (valores.get(COL_GGREM) or "").strip(),
                "registro": (valores.get(COL_REGISTRO) or "").strip() or None,
                "ean1": (valores.get(COL_EAN1) or "").strip() or None,
                "tarja": (valores.get(COL_TARJA) or "").strip() or None,
                "tipo_produto": (valores.get(COL_TIPO_PRODUTO) or "").strip() or None,
                "classe_terapeutica": (valores.get(COL_CLASSE_TERAPEUTICA) or "").strip() or None,
                "restricao_hospitalar": bool((valores.get(COL_RESTRICAO_HOSPITALAR) or "").strip()),
                "pmc_por_aliquota": {
                    nome: _num(valores.get(idx)) for idx, nome in COLUNAS_PMC.items()
                },
            }


# ----------------------------------------------------------- normalização --
PALAVRAS_SAL = {
    "CLORIDRATO", "BESILATO", "SUCCINATO", "TARTARATO", "HEMITARTARATO",
    "MALEATO", "FUMARATO", "HEMIFUMARATO", "MESILATO", "DICLORIDRATO",
    "CITRATO", "BROMIDRATO", "SULFATO", "ACETATO", "NAPSILATO", "FOSFATO",
    "BISSULFATO", "SODICA", "SODICO", "CALCICA", "CALCICO", "POTASSICA",
    "POTASSICO", "ETEXILATO", "CILEXETILA", "MONOIDRATADO", "MONOIDRATADA",
    "DIHIDRATADO", "DIHIDRATADA", "HEMIHIDRATADA", "HIDRATADA", "SINTETICA",
    "DE", "BOVINA", "SUINA", "RECOMBINANTE",
}
# Local usa, às vezes, uma glosa/sinônimo entre parênteses que a CMED não usa.
SINONIMOS_GLOSA = {
    "NITROGLICERINA TRINITRATO GLICERILA": "NITROGLICERINA",
}


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def palavras_normalizadas(nome: str) -> frozenset[str]:
    n = _sem_acento(nome.upper().strip())
    n = n.replace("(", " ").replace(")", " ").replace("-", " ")
    n = n.replace(";", " ").replace("/", " ")
    palavras = {p for p in re.split(r"\s+", n) if p and p not in PALAVRAS_SAL}
    chave = " ".join(sorted(palavras))
    if chave in SINONIMOS_GLOSA:
        palavras = set(SINONIMOS_GLOSA[chave].split())
    return frozenset(palavras)


def eh_combinacao(substancia_cmed: str) -> bool:
    return ";" in substancia_cmed


def eh_match(cmed_palavras: frozenset[str], local_palavras: frozenset[str]) -> bool:
    """Assimétrico de propósito: local pode ter glosa a mais (aceitável);
    CMED com palavra a mais quase sempre é 2º princípio ativo sem ";" no
    texto (ex.: "sacubitril valsartana sódica hidratada" não pode bater em
    "valsartana" isolada) — rejeitar sempre nesse sentido."""
    return bool(cmed_palavras) and cmed_palavras <= local_palavras


def casar_substancia(substancia_cmed: str, farmacos_normalizados: list[tuple[int, frozenset[str]]]) -> list[int]:
    """`farmacos_normalizados` é [(drug_id, palavras_normalizadas(generic_name)), ...].
    Nunca casa com uma linha de combinação (`;`) — ver docstring de `eh_match`."""
    if eh_combinacao(substancia_cmed):
        return []
    cmed_palavras = palavras_normalizadas(substancia_cmed)
    candidatos = [(drug_id, local_p) for drug_id, local_p in farmacos_normalizados
                  if eh_match(cmed_palavras, local_p)]
    if not candidatos:
        return []
    # Em empate (mais de um Drug local casando), prefere igualdade exata de
    # palavras sobre correspondência parcial — mais específico, menos risco.
    exatos = [drug_id for drug_id, local_p in candidatos if local_p == cmed_palavras]
    return exatos or [drug_id for drug_id, _ in candidatos]


# -------------------------------------------------------------- resolução --
def _icms_por_uf() -> dict:
    return json.loads(ARQUIVO_ICMS.read_text())["ufs"]


def preco_pmc(pmc_por_aliquota: dict, uf: str | None) -> dict:
    """Resolve o PMC pra uma UF. Nunca "preço médio" — é sempre o TETO
    regulado pela CMED. Três desfechos possíveis:
    1. UF com alíquota verificada -> preço daquela alíquota + rótulo com UF real.
    2. UF sem alíquota verificada (hoje, todas) -> média das alíquotas cheias
       publicadas pela CMED, claramente rotulada como média nacional, nunca
       atribuída a uma UF específica.
    3. Nenhuma coluna de PMC preenchida (uso restrito hospitalar, Resolução
       CMED nº 3/2009) -> sem preço ao consumidor, nunca em branco/estimado.
    """
    valores_validos = {k: v for k, v in pmc_por_aliquota.items() if v is not None}
    if not valores_validos:
        return {
            "valor": None, "rotulo": "Sem preço ao consumidor publicado (uso restrito hospitalar).",
            "fonte_icms": "cmed_sem_pmc",
        }

    ufs = _icms_por_uf()
    info_uf = ufs.get((uf or "").upper()) if uf else None
    if info_uf and info_uf.get("status") == "verificado" and info_uf.get("aliquota_pct") is not None:
        coluna = f"PMC {info_uf['aliquota_pct']}%".replace(".0%", "%")
        valor = pmc_por_aliquota.get(coluna)
        if valor is not None:
            return {
                "valor": valor,
                "rotulo": (
                    f"Preço máximo ao consumidor (PMC) — teto regulado pela CMED, "
                    f"{uf.upper()}, ICMS {info_uf['aliquota_pct']}%, lista de {info_uf.get('fonte_data', '?')}."
                ),
                "fonte_icms": "uf_verificada",
            }

    # Fallback: média das alíquotas cheias disponíveis, rotulada como tal —
    # nunca atribuída a uma UF, nunca chamada de "preço médio" do produto.
    presentes = [pmc_por_aliquota[c] for c in COLUNAS_PMC_MEDIA_NACIONAL if pmc_por_aliquota.get(c) is not None]
    if not presentes:
        return {
            "valor": None,
            "rotulo": "Sem preço ao consumidor publicado nas alíquotas cheias da CMED.",
            "fonte_icms": "cmed_sem_pmc_cheio",
        }
    return {
        "valor": round(mean(presentes), 2),
        "rotulo": (
            "Preço máximo ao consumidor (PMC) — média nacional das alíquotas de ICMS "
            "publicadas pela CMED; VERIFICAÇÃO HUMANA NECESSÁRIA para a alíquota real de "
            f"{uf.upper() if uf else 'sua UF'} (norma estadual ainda não conferida nesta base)."
        ),
        "fonte_icms": "media_nacional_nao_verificada",
    }


# --------------------------------------------------------------- pipeline --
def atualizar(db: Session, forcar: bool = False, diretorio: Path | None = None) -> dict:
    """Único caminho de código para atualização manual e automática. Só baixa
    de novo se o timestamp da URL mudou (ou `forcar=True`); carrega em
    transação única."""
    diretorio = diretorio or Path("/tmp/cmed")
    diretorio.mkdir(parents=True, exist_ok=True)

    url, publicado_em = localizar_url_planilha()
    ultima = db.query(CmedVersao).order_by(CmedVersao.id.desc()).first()
    if ultima and ultima.publicado_em == publicado_em and not forcar:
        return {"atualizado": False, "motivo": "mesma versão já importada", "publicado_em": publicado_em}

    caminho = diretorio / f"cmed_{publicado_em}.xlsx"
    dados = baixar_planilha(url, caminho)
    sha256 = hashlib.sha256(dados).hexdigest()

    farmacos = db.query(Drug.id, Drug.generic_name).all()
    farmacos_normalizados = [(drug_id, palavras_normalizadas(nome)) for drug_id, nome in farmacos]

    linhas = list(parsear_linhas(caminho))

    versao = CmedVersao(publicado_em=publicado_em, arquivo_url=url, sha256=sha256, linhas=len(linhas))
    db.add(versao)
    db.flush()  # pega o id sem commitar ainda — tudo numa transação só

    casados = 0
    for linha in linhas:
        drug_ids = casar_substancia(linha["substancia"], farmacos_normalizados)
        # Uma apresentação pode servir >1 Drug só no caso raro de dois slugs
        # locais mapeando pro mesmo nome (não deveria acontecer, mas não
        # arrisca perder preço se acontecer); sem match, drug_id fica None e
        # a linha entra mesmo assim (ver docstring do modelo).
        alvo_ids = drug_ids or [None]
        for drug_id in alvo_ids:
            if drug_id:
                casados += 1
            db.add(CmedApresentacao(
                cmed_versao_id=versao.id, drug_id=drug_id,
                substancia_cmed=linha["substancia"], laboratorio=linha["laboratorio"],
                produto=linha["produto"], apresentacao=linha["apresentacao"],
                ggrem=linha["ggrem"], registro=linha["registro"], ean1=linha["ean1"],
                tarja=linha["tarja"], tipo_produto=linha["tipo_produto"],
                classe_terapeutica=linha["classe_terapeutica"],
                restricao_hospitalar=linha["restricao_hospitalar"],
                pmc_por_aliquota=linha["pmc_por_aliquota"],
            ))

    db.commit()
    log.info("CMED %s importada: %d linhas, %d casadas com Drug", publicado_em, len(linhas), casados)
    return {
        "atualizado": True, "publicado_em": publicado_em, "linhas": len(linhas),
        "apresentacoes_casadas": casados, "cmed_versao_id": versao.id,
    }
