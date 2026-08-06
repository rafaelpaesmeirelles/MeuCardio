"""Texto de divulgação da assinatura digital, para o corpo do e-mail que
leva o link do documento — pedido do Rafael em 06/08/2026: "alguma maneira
do corvia mail reconhecer que o arquivo possui assinatura identificada e
sinalizar isso ao destinatario?", depois ampliado: ler o PDF de verdade
(não confiar em metadado do banco) e fazer o mesmo para qualquer provedor
de envio (Gmail, Hotmail/Microsoft, CorvIA Mail nativo, Yahoo, iCloud) e
tanto para receituário quanto para documento gerado.

Lê a assinatura embutida de verdade via `verificacao_pdf.py` (pyhanko) —
nunca usa o certificado ATUAL do médico como proxy, porque ele pode já ter
sido trocado desde que o documento foi assinado; o que importa é o que
está gravado NO ARQUIVO.
"""

from __future__ import annotations

from app.services.assinatura import verificacao_pdf


def texto_divulgacao(pdf_bytes: bytes) -> str | None:
    """`None` quando o PDF não tem assinatura embutida (emissão MANUAL) —
    quem chama decide se isso é esperado (documento comum) ou inesperado
    (receituário, que já exige `nivel == "qualificada"` antes de chegar
    aqui)."""
    resultado = verificacao_pdf.verificar(pdf_bytes)
    if resultado is None:
        return None

    partes = [
        f"assinado digitalmente por {resultado.titular_cn}",
        f"certificado emitido por {resultado.emissor_cn}",
        f"válido de {resultado.valido_de:%d/%m/%Y} até {resultado.valido_ate:%d/%m/%Y}",
    ]
    if resultado.assinado_em:
        partes.append(f"assinatura registrada em {resultado.assinado_em:%d/%m/%Y às %H:%M}")
    frase = ", ".join(partes)

    if resultado.intacta and resultado.cobre_documento_inteiro:
        integridade = (
            "A integridade do arquivo foi conferida no momento do envio — "
            "nenhuma alteração desde a assinatura."
        )
    else:
        # Nunca esconde um resultado ruim atrás de um texto genérico — se a
        # verificação não confirmou integridade, o destinatário precisa saber.
        integridade = (
            "⚠️ A verificação NÃO confirmou a integridade completa do arquivo — "
            "confira com cautela antes de usar este documento."
        )

    return (
        f"Este documento foi {frase}. {integridade} "
        f"Para conferir por conta própria, abra o PDF em um leitor compatível "
        f"(por exemplo, o Adobe Acrobat Reader), que mostra o painel de assinaturas com os mesmos dados."
    )
