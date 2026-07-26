"""Limpeza e ingestão do corpus V2.2 para a biblioteca MeuCardio.

O corpus herdado foi produzido em sessões de chat com pesquisa web. Cada arquivo
carrega um módulo real — um bloco ```json com o conhecimento estruturado — embrulhado
em resíduo de conversa que não pode entrar num sistema clínico:

  * marcadores de citação órfãos `[web:1344]`, sem destino;
  * blocos `<span style="display:none">[^39_1]…</span>` e divisores `⁂`;
  * notas de rodapé do turno de chat, que misturam referências de fármacos
    diferentes no mesmo arquivo — ler URLs soltas contamina o módulo;
  * parágrafos conversacionais ("Sigo o pipeline…", "Excelente! Obtive dados…").

Por isso a ingestão é JSON-first: a verdade do módulo é o bloco JSON, incluindo o
campo `referencias`. O texto ao redor é descartado. Cada módulo é então classificado
pelo melhor nível de fonte que suas próprias referências sustentam.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------- níveis de fonte
TIER_A = {
    "escardio.org", "academic.oup.com", "pubmed.ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov", "acc.org", "ahajournals.org", "nejm.org", "thelancet.com",
    "jamanetwork.com", "bmj.com", "onlinelibrary.wiley.com", "ema.europa.eu", "ec.europa.eu",
    "fda.gov", "accessdata.fda.gov", "gov.br", "anvisa.gov.br", "infarmed.pt", "cima.aemps.es",
    "cardiol.br", "abccardiol.org", "socesp.org.br", "socerj.org.br", "sbacv.org.br",
    "revespcardiol.org", "revportcardiol.org", "scielo.br", "sciencedirect.com", "jacc.org",
    "heartrhythmjournal.com", "clinicaltrials.gov", "who.int", "kdigo.org", "nice.org.uk",
    "eacts.org", "sts.org", "ccs.ca", "journals.lww.com", "nature.com", "elsevier.es",
    "publications.ersnet.org", "journals.sagepub.com", "tandfonline.com", "doi.org",
}
TIER_B = {
    "uptodate.com", "medscape.com", "msdmanuals.com", "guiafarmaceutico.hsl.org.br",
    "guiafarmaceutico.hospitalsaocamilosp.org.br", "einstein.br", "aplicacoes.einstein.br",
    "hcrp.usp.br", "protocolos.hcrp.usp.br", "observatorio.fm.usp.br", "cochranelibrary.com",
    "community.cochrane.org", "dynamed.com", "bvsalud.org", "proqualis.net", "aafp.org",
    "tctmd.com", "gracescore.org",
}
ORG_TIER_A = re.compile(
    r"\b(esc|european heart journal|european society of cardiology|aha|acc|acc/aha|"
    r"circulation|jacc|nejm|new england|lancet|jama|bmj|sbc|sociedade brasileira de cardiologia|"
    r"arquivos brasileiros de cardiologia|anvisa|fda|ema|kdigo|nice|heart rhythm|europace|"
    r"eur heart j|chest|ers|eacts|sts)\b",
    re.I,
)

CATEGORIA_TEMA = {
    "protocolos": "Protocolos", "medicamentos": "Farmacologia",
    "calculadoras": "Calculadoras", "estudos": "Diretrizes e estudos",
}
CATEGORIA_KIND = {
    "protocolos": "protocolo", "medicamentos": "farmacologia",
    "calculadoras": "calculadora", "estudos": "diretriz",
}

RE_JSON = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)
RE_SPAN = re.compile(r"<span style=\"display:\s*none\">.*?</span>", re.S)
RE_DIV = re.compile(r"<div align=\"center\">\s*⁂\s*</div>", re.S)
RE_NOTA = re.compile(r"^\[\^[^\]]+\]:\s*\S.*$", re.M)
RE_REF_ORFA = re.compile(r"\[\^[^\]]+\]")
RE_WEB = re.compile(r"\s*\[web:\d+\]")
RE_DOM = re.compile(r"https?://(?:www\.)?([^/\s]+)")
RE_VAZIO = re.compile(r"\n{3,}")

LACUNA = "VERIFICAÇÃO HUMANA NECESSÁRIA"


def _nivel_dominio(dom: str) -> str:
    dom = dom.lower()
    if any(dom == t or dom.endswith("." + t) for t in TIER_A):
        return "A"
    if any(dom == t or dom.endswith("." + t) for t in TIER_B):
        return "B"
    return "C"


def _slug(v: str) -> str:
    v = unicodedata.normalize("NFKD", v).encode("ascii", "ignore").decode()
    v = re.sub(r"[^\w\s-]", "", v).strip().lower()
    return re.sub(r"[\s_-]+", "-", v)[:120].strip("-")


def _despoluir(texto: str) -> str:
    t = RE_SPAN.sub("", texto)
    t = RE_DIV.sub("", t)
    t = RE_NOTA.sub("", t)
    t = RE_REF_ORFA.sub("", t)
    t = RE_WEB.sub("", t)
    return RE_VAZIO.sub("\n\n", t).strip()


@dataclass
class Referencia:
    titulo: str
    organizacao: str
    ano: str
    url: str
    doi: str
    nivel: str


@dataclass
class Modulo:
    slug: str
    title: str
    theme: str
    kind: str
    summary: str | None
    body_md: str
    dados: dict
    referencias: list[Referencia]
    source_tier: str
    review_status: str
    published: bool
    gaps: list[str] = field(default_factory=list)
    origem: str = ""


def _classificar_ref(r: dict) -> Referencia:
    url = str(r.get("url") or "")
    doi = str(r.get("doi") or "")
    org = str(r.get("organizacao") or r.get("organização") or "")
    nivel = "C"
    if doi:
        nivel = "A"
    elif url:
        m = RE_DOM.match(url)
        nivel = _nivel_dominio(m.group(1)) if m else "C"
    if nivel == "C" and ORG_TIER_A.search(org):
        nivel = "A"
    return Referencia(
        titulo=str(r.get("titulo") or r.get("título") or "")[:400],
        organizacao=org[:200], ano=str(r.get("ano") or ""), url=url, doi=doi, nivel=nivel,
    )


def _limpar_valores(no):
    """Remove os marcadores órfãos [web:N] e [^ref] de dentro dos valores do JSON."""
    if isinstance(no, dict):
        return {k: _limpar_valores(v) for k, v in no.items()}
    if isinstance(no, list):
        return [_limpar_valores(v) for v in no]
    if isinstance(no, str):
        return re.sub(r"\s{2,}", " ", RE_REF_ORFA.sub("", RE_WEB.sub("", no))).strip()
    return no


def _achar_lacunas(dados: dict, prefixo: str = "") -> list[str]:
    achados: list[str] = []
    if isinstance(dados, dict):
        for k, v in dados.items():
            achados += _achar_lacunas(v, f"{prefixo}.{k}" if prefixo else str(k))
    elif isinstance(dados, list):
        for i, v in enumerate(dados):
            achados += _achar_lacunas(v, f"{prefixo}[{i}]")
    elif isinstance(dados, str) and LACUNA in dados:
        achados.append(prefixo)
    return achados


def _resumo(dados: dict) -> str | None:
    for chave in ("definicao", "definição", "resumo", "indicacoes_precisas",
                  "indicacoes", "mecanismo_acao", "objetivo"):
        v = dados.get(chave)
        if isinstance(v, str) and len(v) > 40 and LACUNA not in v:
            v = re.sub(r"\s+", " ", v).strip()
            return v[:320].rsplit(" ", 1)[0] + "…" if len(v) > 320 else v
    return None


def _corpo(dados: dict, titulo: str) -> str:
    """Renderiza o JSON estruturado como Markdown legível, sem inventar nada."""
    linhas = [f"# {titulo}", ""]

    def escrever(valor, nivel: int, rotulo: str | None = None) -> None:
        pad = "  " * max(nivel - 2, 0)
        if isinstance(valor, dict):
            if rotulo:
                linhas.append(f"{'#' * min(nivel, 6)} {rotulo}")
                linhas.append("")
            for k, v in valor.items():
                if k in {"id", "referencias", "titulo", "título"}:
                    continue
                escrever(v, nivel + 1, k.replace("_", " ").capitalize())
        elif isinstance(valor, list):
            if rotulo:
                linhas.append(f"**{rotulo}**")
                linhas.append("")
            for item in valor:
                if isinstance(item, (dict, list)):
                    escrever(item, nivel + 1)
                else:
                    linhas.append(f"{pad}- {item}")
            linhas.append("")
        else:
            texto = str(valor).strip()
            if not texto:
                return
            if rotulo:
                linhas.append(f"{pad}**{rotulo}:** {texto}")
            else:
                linhas.append(f"{pad}{texto}")
            linhas.append("")

    for chave, valor in dados.items():
        if chave in {"id", "referencias", "titulo", "título"}:
            continue
        escrever(valor, 2, chave.replace("_", " ").capitalize())

    return RE_VAZIO.sub("\n\n", "\n".join(linhas)).strip()


def analisar(caminho: Path) -> Modulo | None:
    bruto = caminho.read_text(encoding="utf-8", errors="replace")
    m = RE_JSON.search(bruto)
    if not m:
        return None
    try:
        dados = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    if not isinstance(dados, dict):
        return None
    dados = _limpar_valores(dados)

    titulo = str(dados.get("titulo") or dados.get("título") or "").strip()
    if not titulo:
        titulo = str(dados.get("nome_generico") or "").strip()
    if not titulo:
        h = next((l for l in _despoluir(bruto).splitlines() if l.lstrip().startswith("#")), "")
        titulo = re.sub(r"^#+\s*(Módulo\s*[—-]\s*)?", "", h).strip() or caminho.stem
    titulo = re.sub(r"\s+", " ", titulo)[:300]

    refs = [_classificar_ref(r) for r in dados.get("referencias", []) if isinstance(r, dict)]
    niveis = {r.nivel for r in refs}
    tier = "A" if "A" in niveis else ("B" if "B" in niveis else ("C" if refs else "sem_fonte"))

    lacunas = _achar_lacunas(dados)
    publicavel = tier in {"A", "B"}
    status = (
        "sem_fonte_rastreavel" if tier == "sem_fonte"
        else "fonte_terciaria_revisar" if tier == "C"
        else "lacuna_declarada" if lacunas
        else "pendente_revisao"
    )

    cat = caminho.parent.name
    return Modulo(
        slug=_slug(titulo) or _slug(caminho.stem),
        title=titulo,
        theme=CATEGORIA_TEMA.get(cat, cat),
        kind=CATEGORIA_KIND.get(cat, "modulo"),
        summary=_resumo(dados),
        body_md=_corpo(dados, titulo),
        dados=dados,
        referencias=refs,
        source_tier=tier,
        review_status=status,
        published=publicavel,
        gaps=lacunas,
        origem=caminho.name,
    )


def _yaml(valor) -> str:
    return json.dumps(valor, ensure_ascii=False)


def ingerir(origem: str | Path, gravar_em: str | Path | None = None) -> dict:
    origem = Path(origem)
    arquivos = sorted(origem.rglob("*.md"))
    modulos: list[Modulo] = []
    rejeitados: list[str] = []

    for p in arquivos:
        mod = analisar(p)
        (modulos.append(mod) if mod else rejeitados.append(p.name))

    vistos: Counter = Counter()
    for mod in modulos:
        vistos[mod.slug] += 1
        if vistos[mod.slug] > 1:
            mod.slug = f"{mod.slug}-v{vistos[mod.slug]}"

    if gravar_em:
        destino = Path(gravar_em)
        for mod in modulos:
            pasta = destino / _slug(mod.theme)
            pasta.mkdir(parents=True, exist_ok=True)
            fm = [
                "---",
                f"title: {_yaml(mod.title)}",
                f"slug: {_yaml(mod.slug)}",
                f"theme: {_yaml(mod.theme)}",
                f"kind: {_yaml(mod.kind)}",
                f"summary: {_yaml(mod.summary) if mod.summary else 'null'}",
                f"source_tier: {_yaml(mod.source_tier)}",
                f"review_status: {_yaml(mod.review_status)}",
                f"published: {'true' if mod.published else 'false'}",
                f"origem: {_yaml(mod.origem)}",
            ]
            if mod.gaps:
                fm.append("gaps:")
                fm += [f"  - {_yaml(g)}" for g in mod.gaps]
            if mod.referencias:
                fm.append("source_refs:")
                for r in mod.referencias:
                    rotulo = " · ".join(x for x in [r.organizacao, r.ano, r.titulo] if x)
                    fm.append(f"  - {_yaml(f'[{r.nivel}] {rotulo}' + (f' — {r.doi or r.url}' if (r.doi or r.url) else ''))}")
            fm.append("---\n")
            (pasta / f"{mod.slug}.md").write_text(
                "\n".join(fm) + "\n" + mod.body_md + "\n", encoding="utf-8"
            )

    return {
        "arquivos_lidos": len(arquivos),
        "modulos_extraidos": len(modulos),
        "rejeitados_sem_json": rejeitados,
        "por_tema": dict(Counter(m.theme for m in modulos)),
        "por_nivel_de_fonte": dict(Counter(m.source_tier for m in modulos)),
        "publicaveis": sum(m.published for m in modulos),
        "retidos_para_revisao": sum(not m.published for m in modulos),
        "modulos_com_lacuna": sum(1 for m in modulos if m.gaps),
        "campos_com_lacuna": sum(len(m.gaps) for m in modulos),
    }


if __name__ == "__main__":
    import sys

    origem = sys.argv[1] if len(sys.argv) > 1 else "/content/_bruto"
    destino = sys.argv[2] if len(sys.argv) > 2 else "/content"
    print(json.dumps(ingerir(origem, destino), ensure_ascii=False, indent=2))
