"""Relatório de retenção de documentos KYC — issue #52, hardening de segurança.

**Este comando NUNCA apaga nada.** É a estrutura pedida para permitir exclusão
programada FUTURA, quando houver decisão humana sobre o prazo — enquanto essa
decisão não existir, o único papel deste comando é mostrar o estado real (há
quantos registros em cada status, há quanto tempo, quantos arquivos ainda
existem) para embasar essa decisão. Ver `docs/kyc-retention-policy.md` para o
raciocínio completo e o que falta decidir.

Uso: `python -m app.commands.kyc_retention_relatorio`
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.kyc import KycVerification
from app.services.kyc import verificacao


def _dias_desde(momento: datetime | None) -> int | None:
    if momento is None:
        return None
    agora = datetime.now(timezone.utc)
    referencia = momento if momento.tzinfo else momento.replace(tzinfo=timezone.utc)
    return (agora - referencia).days


def gerar_relatorio() -> list[dict]:
    db = SessionLocal()
    try:
        registros = db.query(KycVerification).order_by(KycVerification.criado_em.asc()).all()
        linhas = []
        for r in registros:
            referencia = r.aprovado_em or r.atualizado_em or r.criado_em
            campos = (
                "doc_profissional_frente", "doc_profissional_verso",
                "doc_pessoal_frente", "doc_pessoal_verso", "doc_pessoal_digital", "selfie",
            )
            arquivos_presentes = 0
            for campo in campos:
                try:
                    verificacao.ler_documento(r, campo, r.owner_id)
                    arquivos_presentes += 1
                except FileNotFoundError:
                    pass
                except Exception:  # noqa: BLE001 — arquivo existe mas não decifra; conta como presente
                    arquivos_presentes += 1
            linhas.append({
                "verification_id": r.id,
                "owner_id": r.owner_id,
                "status": r.status,
                "dias_desde_ultima_atualizacao_de_status": _dias_desde(referencia),
                "arquivos_ainda_presentes": arquivos_presentes,
                "total_de_campos_possiveis": len(campos),
            })
        return linhas
    finally:
        db.close()


def main() -> int:
    linhas = gerar_relatorio()
    if not linhas:
        print("Nenhum registro de verificação KYC no banco.")
        return 0

    por_status: dict[str, int] = {}
    for linha in linhas:
        por_status[linha["status"]] = por_status.get(linha["status"], 0) + 1

    print(f"kyc_dir: {settings.kyc_dir}")
    print(f"Total de registros: {len(linhas)}")
    print("Por status:")
    for status, contagem in sorted(por_status.items()):
        print(f"  {status}: {contagem}")
    print()
    print("Nenhum arquivo foi apagado por este relatório — é só leitura.")
    print(
        "Política de retenção ainda PENDENTE de decisão humana — ver "
        "docs/kyc-retention-policy.md antes de implementar qualquer exclusão automática."
    )
    print()
    for linha in linhas:
        print(
            f"  verification_id={linha['verification_id']} owner_id={linha['owner_id']} "
            f"status={linha['status']} "
            f"dias_desde_atualizacao={linha['dias_desde_ultima_atualizacao_de_status']} "
            f"arquivos_presentes={linha['arquivos_ainda_presentes']}/{linha['total_de_campos_possiveis']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
