"""Consulta ao PubMed (NCBI/NIH) — base pública, gratuita e amplamente
respeitada em medicina. Usada como complemento ao RAG interno, nunca no
lugar dele: a base institucional continua sendo a fonte principal; o
PubMed entra quando o modelo precisa de literatura mais ampla ou recente
do que o que já foi catalogado internamente.

Só busca resumo/metadado público (título, autores, revista, ano, resumo
do abstract) — nunca reproduz o artigo inteiro, mesma regra de direito
autoral que vale pro resto do sistema.
"""

import logging

import httpx

log = logging.getLogger("meucardio.pubmed")

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TIMEOUT = 6.0


def buscar_pubmed(consulta: str, max_resultados: int = 3) -> list[dict]:
    """Retorna até `max_resultados` artigos do PubMed relevantes à consulta.
    Falha graciosamente (lista vazia) se o serviço estiver fora do ar —
    nunca deve derrubar a resposta da IA por causa de uma fonte externa."""
    try:
        with httpx.Client(timeout=TIMEOUT) as cliente:
            busca = cliente.get(f"{BASE}/esearch.fcgi", params={
                "db": "pubmed", "term": consulta, "retmode": "json",
                "retmax": max_resultados, "sort": "relevance",
            })
            busca.raise_for_status()
            ids = busca.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return []

            resumo = cliente.get(f"{BASE}/esummary.fcgi", params={
                "db": "pubmed", "id": ",".join(ids), "retmode": "json",
            })
            resumo.raise_for_status()
            dados = resumo.json().get("result", {})

            artigos = []
            for pid in ids:
                item = dados.get(pid)
                if not item:
                    continue
                autores = ", ".join(a["name"] for a in item.get("authors", [])[:3])
                artigos.append({
                    "pmid": pid,
                    "titulo": item.get("title", ""),
                    "autores": autores,
                    "revista": item.get("fulljournalname") or item.get("source", ""),
                    "ano": (item.get("pubdate") or "")[:4],
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                })
            return artigos
    except Exception:
        log.exception("Falha ao consultar PubMed para: %s", consulta)
        return []


def montar_contexto_pubmed(artigos: list[dict]) -> str:
    if not artigos:
        return ""
    linhas = ["LITERATURA PÚBLICA (PubMed/NCBI — fonte externa, não institucional):"]
    for i, a in enumerate(artigos, start=1):
        linhas.append(
            f"[PM{i}] {a['titulo']} — {a['autores']} et al. {a['revista']}, {a['ano']}. "
            f"PMID {a['pmid']}."
        )
    return "\n".join(linhas)
