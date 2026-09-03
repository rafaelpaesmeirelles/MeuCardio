"""Backfill incremental de RAG — ferramenta operacional (correção coordenada
de 03/09/2026, seção "melhorar o comando de backfill").

Indexa, nesta ordem: `documents` (via `rag.indexar_tudo`) e as 12 frentes de
`rag_sources.FONTES_RAG` + calculadoras (via `rag_multi.indexar_tipo`).
Idempotente por `content_hash`: entidade cujo texto-fonte não mudou desde a
última indexação nunca gera chamada de rede (ver `rag.indexar_documento`/
`rag_multi.indexar_entidade`). Por isso é seguro rodar de novo a qualquer
momento — inclusive depois de uma interrupção no meio — sem cursor nem estado
externo: a próxima chamada retoma exatamente do que ainda está pendente.

Responsável ÚNICO pela indexação incremental do RAG. `reconcile_content` e
`deploy.sh` NUNCA chamam o provedor de embeddings diretamente — ambos disparam
este comando (ou nada, no caso de `reconcile_content`, que só publica/
reconcilia o corpus local). `app.services.indexar` foi descontinuado por cobrir
só `documents`, sem as outras 12 frentes — ver aviso no próprio módulo.

Uso:
    # produção normal — só o que está pendente/stale, sem teto de item
    python -m app.commands.reindex_rag_completo_20260902

    # preflight, só leitura: conta backlog, não chama o provedor, não grava nada
    python -m app.commands.reindex_rag_completo_20260902 --dry-run

    # só um recorte de frentes, em lotes pequenos e seguros
    python -m app.commands.reindex_rag_completo_20260902 --only-types evidencia,estudo --limit 200

    # reprocessa TUDO, mesmo quem já está com content_hash em dia (só depois
    # de trocar de modelo/dimensão de embedding)
    python -m app.commands.reindex_rag_completo_20260902 --forcar

Contrato de exit code (nunca "0 = sucesso" por presunção):
    0   sucesso completo — todas as frentes pedidas processadas, zero falha,
        zero backlog restante (ou dry-run que rodou sem erro).
    1   falha operacional real — banco inacessível, dimensão de embedding
        divergente do schema, argumento inválido, ou qualquer exceção não
        prevista pelo circuit breaker por-item de `indexar_tudo`/`indexar_tipo`.
    2   rodou, mas ficou backlog (falha de item isolado, `--limit` cortou o
        lote, ou circuit breaker interrompeu uma frente por 3 falhas seguidas
        do provedor) — não é erro de programa, é "ainda não terminou".
    130 interrompido por SIGINT/SIGTERM (Ctrl-C) — seguro: cada entidade só é
        gravada depois que o embedding já chegou (ver `indexar_documento`/
        `indexar_entidade`), então interromper entre itens nunca corrompe
        nada; o item em voo é perdido e reentra no backlog normalmente.
    3   já existe outra execução com o advisory lock — desiste sem tocar em
        nada (ver `_JaEmExecucao`).
    4   `AI_ENABLED=false` nesta instalação — a investigação original
        (03/09/2026) achou que o comando gastava crédito mesmo com a IA
        clínica desligada, sem guarda nenhuma (o endpoint HTTP
        `/api/ai/reindexar` já tinha essa guarda; o comando de linha de
        comando não tinha). `--dry-run` continua funcionando com IA
        desligada — é só leitura, útil para preparar o backlog antes de
        ligar.

Cada execução grava uma linha em `rag_reindex_runs` (migration `b7ri20260903`)
com contadores, duração e `exit_code` — é o que alimenta observabilidade sem
precisar caçar log de container (`docker compose logs` não guarda `exec`
antigo)."""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import signal
import sys
import time
from datetime import datetime, timezone

from sqlalchemy import select, text

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.rag import DocumentChunk, KnowledgeChunk, RagReindexRun
from app.services.calculators import REGISTRY as CALCULATORS_REGISTRY
from app.services.knowledge_graph import _id_estavel
from app.services.rag import EmbeddingDimensionError, content_hash, indexar_tudo, verificar_dimensao_embedding
from app.services.rag_multi import _indexar_calculadoras, indexar_tipo
from app.services.rag_sources import FONTES_POR_TIPO, FONTES_RAG, publicados

log = logging.getLogger("corvia.reindex_rag")

TIPOS_VALIDOS = ("documento",) + tuple(f.entity_type for f in FONTES_RAG) + ("calculadora",)


class _Interrompido(Exception):
    """Levantada pelo handler de sinal — nunca pelo circuit breaker interno."""


class _IaDesligada(Exception):
    """AI_ENABLED=false — achado da investigação original de 03/09/2026: o
    comando gastava crédito do provedor mesmo com a IA clínica desligada
    nesta instalação, sem nenhuma guarda (diferente do endpoint HTTP
    equivalente, que já recusava com 503)."""


class _JaEmExecucao(Exception):
    """Outra execução (deploy.sh em background, cron, ou operador manual)
    já segura o lock. Achado da revisão adversarial de 03/09/2026: nada
    impedia duas execuções concorrentes de indexar a MESMA entidade ao mesmo
    tempo — sem constraint em `document_chunks` (só `knowledge_chunks` tem
    UniqueConstraint entity_type/entity_id/ordem), a corrida podia deixar
    chunk duplicado servido brevemente ao assistente clínico até a próxima
    passada corrigir por content_hash. Cenário real: o próprio AVISO que
    `deploy.sh` imprime quando `exec -d` falha ao DISPARAR instrui rodar o
    comando manualmente — se isso for feito enquanto o disparo automático na
    verdade tinha funcionado, colide."""


# Chave fixa e arbitrária do advisory lock — Postgres exige bigint, não
# string; nunca reaproveitar este número para outro lock do sistema.
_LOCK_KEY = 771103090


def _instalar_handler_interrupcao() -> None:
    def _handler(signum, _frame):
        raise _Interrompido(f"sinal {signum}")

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)


def _parse_tipos(bruto: str | None) -> list[str]:
    if not bruto:
        return list(TIPOS_VALIDOS)
    pedidos = [t.strip() for t in bruto.split(",") if t.strip()]
    invalidos = [t for t in pedidos if t not in TIPOS_VALIDOS]
    if invalidos:
        raise ValueError(
            f"--only-types com valor(es) desconhecido(s): {', '.join(invalidos)}. "
            f"Válidos: {', '.join(TIPOS_VALIDOS)}."
        )
    # remove duplicata preservando ordem
    vistos: set[str] = set()
    return [t for t in pedidos if not (t in vistos or vistos.add(t))]


def _texto_calculadora(calc) -> str:
    partes = [calc.purpose, calc.reference, "\n".join(calc.limitations or [])]
    return "\n\n".join(p for p in partes if p)


def _preflight_documento(db) -> dict:
    from app.models.content import Document

    docs = db.query(Document).filter(Document.published.is_(True)).all()
    pendentes = 0
    for d in docs:
        hash_atual = content_hash(d.body_md)
        hash_existente = db.execute(
            select(DocumentChunk.content_hash).where(DocumentChunk.document_id == d.id).limit(1)
        ).scalar_one_or_none()
        if hash_existente != hash_atual:
            pendentes += 1
    return {"entity_type": "documento", "publicados": len(docs), "pendentes": pendentes}


def _preflight_tipo(db, tipo: str) -> dict:
    if tipo == "calculadora":
        calculadoras = list(CALCULATORS_REGISTRY.values())
        pendentes = 0
        total = 0
        for calc in calculadoras:
            texto = _texto_calculadora(calc)
            if not texto.strip():
                continue
            total += 1
            entity_id = _id_estavel("calculadora", calc.slug)
            hash_atual = content_hash(texto)
            hash_existente = db.execute(
                select(KnowledgeChunk.content_hash)
                .where(KnowledgeChunk.entity_type == "calculadora", KnowledgeChunk.entity_id == entity_id)
                .limit(1)
            ).scalar_one_or_none()
            if hash_existente != hash_atual:
                pendentes += 1
        return {"entity_type": "calculadora", "publicados": total, "pendentes": pendentes}

    fonte = FONTES_POR_TIPO[tipo]
    itens = publicados(db, fonte)
    total = 0
    pendentes = 0
    for item in itens:
        texto = fonte.texto(item)
        if not texto or not texto.strip():
            continue
        total += 1
        hash_atual = content_hash(texto)
        hash_existente = db.execute(
            select(KnowledgeChunk.content_hash)
            .where(KnowledgeChunk.entity_type == tipo, KnowledgeChunk.entity_id == item.id)
            .limit(1)
        ).scalar_one_or_none()
        if hash_existente != hash_atual:
            pendentes += 1
    return {"entity_type": tipo, "publicados": total, "pendentes": pendentes}


def _preflight(db, tipos: list[str]) -> dict:
    """Só leitura: zero chamada de rede ao provedor, zero escrita no banco.
    Conta backlog real por `content_hash` (não só presença de chunk) e
    devolve também espaço em disco livre no volume do banco — barato de medir
    e útil antes de um backfill grande."""
    por_tipo = []
    for tipo in tipos:
        por_tipo.append(_preflight_documento(db) if tipo == "documento" else _preflight_tipo(db, tipo))
    total_publicados = sum(t["publicados"] for t in por_tipo)
    total_pendentes = sum(t["pendentes"] for t in por_tipo)
    try:
        uso_disco = shutil.disk_usage("/")
        disco = {"livre_gb": round(uso_disco.free / (1024**3), 2), "total_gb": round(uso_disco.total / (1024**3), 2)}
    except OSError:
        disco = None
    return {
        "por_tipo": por_tipo,
        "total_publicados": total_publicados,
        "total_pendentes": total_pendentes,
        "disco": disco,
    }


def rodar(
    *,
    dry_run: bool = False,
    forcar: bool = False,
    only_types: list[str] | None = None,
    limite: int | None = None,
) -> tuple[dict, int]:
    inicio = datetime.now(timezone.utc)
    tipos = only_types or list(TIPOS_VALIDOS)
    resultado: dict = {"tipos": tipos, "dry_run": dry_run, "forcar": forcar, "por_frente": {}}
    exit_code = 0
    erro_fatal: str | None = None
    # Conexão dedicada, mantida aberta pelo run inteiro — advisory lock é
    # amarrado à SESSÃO/conexão, não sobrevive a `with SessionLocal(): ...`
    # fechando no meio (que é o padrão usado por tipo, abaixo). dry-run é
    # só leitura e nunca chama o provedor: não precisa do lock.
    lock_conn = None

    try:
        if not dry_run:
            if not settings.ai_enabled:
                raise _IaDesligada(
                    "AI_ENABLED=false nesta instalação — o backfill não roda (gastaria "
                    "crédito do provedor por nada). Use --dry-run para só contar backlog."
                )
            lock_conn = SessionLocal()
            obtido = lock_conn.execute(text("SELECT pg_try_advisory_lock(:k)"), {"k": _LOCK_KEY}).scalar()
            if not obtido:
                raise _JaEmExecucao(
                    "Já existe um backfill em execução (advisory lock ocupado) — "
                    "não inicia um segundo em paralelo. Espere o outro terminar "
                    "(rag_reindex_runs mostra a execução em andamento) e rode de novo."
                )

        with SessionLocal() as db:
            # Falha explícita e cedo, antes de qualquer chamada de rede — uma
            # divergência de EMBEDDING_DIM contra o schema real não pode ser
            # descoberta só no primeiro INSERT de um backfill de milhares de
            # itens.
            verificar_dimensao_embedding(db)

        if dry_run:
            with SessionLocal() as db:
                resultado["preflight"] = _preflight(db, tipos)
            return resultado, 0

        falhas_totais = 0
        backlog_total = 0
        entidades_totais = 0
        trechos_totais = 0

        if "documento" in tipos:
            with SessionLocal() as db:
                r = indexar_tudo(db, apenas_pendentes=not forcar, limite=limite)
            resultado["por_frente"]["documento"] = r
            falhas_totais += r["falhas"]
            backlog_total += r.get("backlog_restante", 0)
            entidades_totais += r["documentos"]
            trechos_totais += r["trechos"]
            log.info("documento: %s", r)

        for tipo in [t for t in tipos if t != "documento"]:
            with SessionLocal() as db:
                if tipo == "calculadora":
                    r = _indexar_calculadoras(db, apenas_pendentes=not forcar, limite=limite)
                else:
                    r = indexar_tipo(db, tipo, apenas_pendentes=not forcar, limite=limite)
            resultado["por_frente"][tipo] = r
            falhas_totais += r["falhas"]
            backlog_total += r.get("backlog_restante", 0)
            entidades_totais += r["entidades"]
            trechos_totais += r["trechos"]
            log.info("%s: %s", tipo, r)

        resultado["falhas_totais"] = falhas_totais
        resultado["backlog_total"] = backlog_total
        resultado["entidades_totais"] = entidades_totais
        resultado["trechos_totais"] = trechos_totais
        exit_code = 0 if (falhas_totais == 0 and backlog_total == 0) else 2

    except _IaDesligada as exc:
        exit_code = 4
        erro_fatal = str(exc)
        log.warning(erro_fatal)
    except _JaEmExecucao as exc:
        exit_code = 3
        erro_fatal = str(exc)
        log.warning(erro_fatal)
    except _Interrompido:
        exit_code = 130
        erro_fatal = "interrompido (SIGINT/SIGTERM) — seguro, nenhuma escrita parcial: retome rodando de novo"
        log.warning(erro_fatal)
    except (EmbeddingDimensionError, ValueError) as exc:
        exit_code = 1
        erro_fatal = str(exc)
        log.error("Falha operacional antes de indexar: %s", erro_fatal)
    except Exception as exc:  # noqa: BLE001 — precisa gravar RagReindexRun mesmo em falha inesperada
        exit_code = 1
        erro_fatal = f"{type(exc).__name__}: {exc}"
        log.exception("Falha operacional inesperada no backfill.")
    finally:
        if lock_conn is not None:
            try:
                lock_conn.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": _LOCK_KEY})
                lock_conn.commit()
            except Exception:
                log.exception("Falha ao liberar o advisory lock do backfill (a conexão será fechada mesmo assim).")
            finally:
                lock_conn.close()
        fim = datetime.now(timezone.utc)
        resultado["duracao_segundos"] = round((fim - inicio).total_seconds(), 1)
        resultado["exit_code"] = exit_code
        if erro_fatal:
            resultado["erro"] = erro_fatal
        if not dry_run:
            try:
                with SessionLocal() as db:
                    db.add(RagReindexRun(
                        started_at=inicio,
                        finished_at=fim,
                        dry_run=False,
                        only_types=",".join(only_types) if only_types else None,
                        entidades_processadas=resultado.get("entidades_totais", 0),
                        trechos_gerados=resultado.get("trechos_totais", 0),
                        falhas=resultado.get("falhas_totais", 0),
                        backlog_restante=resultado.get("backlog_total", 0),
                        exit_code=exit_code,
                        detalhe=resultado,
                    ))
                    db.commit()
            except Exception:
                log.exception("Não foi possível gravar rag_reindex_runs (não altera o exit code do backfill em si).")

    return resultado, exit_code


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="só conta backlog por content_hash; zero rede, zero escrita")
    p.add_argument("--forcar", action="store_true", help="reprocessa mesmo quem já está com content_hash em dia (troca de modelo/dimensão)")
    p.add_argument("--only-types", type=str, default=None, help=f"lista separada por vírgula, entre: {', '.join(TIPOS_VALIDOS)}")
    p.add_argument("--limit", type=int, default=None, help="teto de entidades processadas por frente nesta chamada (lote seguro)")
    p.add_argument("--json", action="store_true", help="saída em JSON (padrão: também JSON, mas em uma linha de log antes)")
    args = p.parse_args()

    try:
        tipos = _parse_tipos(args.only_types)
    except ValueError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(1)

    _instalar_handler_interrupcao()
    t0 = time.monotonic()
    resultado, exit_code = rodar(dry_run=args.dry_run, forcar=args.forcar, only_types=tipos, limite=args.limit)
    print(json.dumps(resultado, ensure_ascii=False, indent=2, default=str))
    print(
        f"[reindex_rag] concluído em {time.monotonic() - t0:.1f}s — exit_code={exit_code} "
        f"(0=sucesso completo, 1=falha operacional, 2=backlog/falha de item restante, "
        f"3=já em execução, 4=IA desligada, 130=interrompido)",
        file=sys.stderr,
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
