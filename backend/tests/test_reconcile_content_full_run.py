"""Regressão de ponta a ponta do incidente de deploy de 11/08/2026 (issue #52).

`reconcile_content --publish-reviewed` derrubou o backend em produção durante
o deploy certificado do RC `27d24089`, com três causas reais em sequência
(cada uma só apareceu depois de corrigir a anterior — ver commit `4e8fb339`):

1. `TypeError: 'review_note' is an invalid keyword argument for Drug` —
   construção de registro novo sem filtrar pelas colunas do modelo.
2. `StringDataRightTruncation` em dois campos `varchar` apertados que na
   prática guardam prosa/citação completa.
3. Ordem de carga em `FRONTS`: `trilhas` processada antes de
   `casos_clinicos`, rejeitando por engano referências genuinamente válidas.

Este teste roda `reconcile()` de ponta a ponta — a mesma função que o CLI
`python -m app.commands.reconcile_content --publish-reviewed` chama — contra
o conteúdo REAL do repositório (os caminhos de `FRONTS` resolvem para
`REPOSITORY_ROOT/<front>` quando o bind mount absoluto de produção não
existe, mesmo mecanismo que tornou possível reproduzir o incidente
localmente nesta sessão). Não é teste sintético: é a mesma verificação que
teria pego os três bugs antes do deploy, se já existisse.
"""
from app.commands import reconcile_content as reconciliation
from app.commands.reconcile_content import reconcile


def test_reconcile_publish_reviewed_termina_sem_excecao_contra_conteudo_real(db, monkeypatch):
    # This test explicitly targets repository content, independently of the
    # empty CONTENT_DIR used by isolated unit-test fixtures.
    monkeypatch.setitem(reconciliation.FRONTS["documentos"], "path",
                        str(reconciliation.REPOSITORY_ROOT / "content"))
    # allow_partial=True: este teste valida que a carga TERMINA COM SUCESSO
    # (sem exceção, sem rejeição bloqueante) — não é o gate de volume mínimo
    # do acervo, que já tem cobertura própria em outros testes.
    resultado = reconcile(publish_reviewed=True, allow_partial=True)

    # Nenhuma frente com diagnóstico bloqueante (erros/recusadas/falhas/...) —
    # é exatamente essa condição que `_assert_no_rejections` já checa dentro
    # de `_load_front`, e que o bug #3 (ordem trilhas x casos_clinicos)
    # violava de verdade contra dado real.
    for front, carga in resultado["loads"].items():
        for chave in ("erros", "recusadas", "recusados", "falhas", "avisos"):
            assert not carga.get(chave), f"{front}.{chave}: {carga.get(chave)}"

    assert "medicamentos" in resultado["loads"]
    assert resultado["loads"]["medicamentos"]["total"] > 0

    authorization = resultado["full_corpus_authorization"]
    assert authorization["schema_version"] == 2
    assert resultado["immutable_source_snapshot"] is True
    assert resultado["database"]["published_total"] == authorization["authorized_total"]
    for front, approved in authorization["approved"].items():
        actual = set(resultado["database"]["fronts"][front]["published_slugs"])
        assert actual == set(approved)
        assert actual.isdisjoint(authorization["quarantined"][front])

    from app.models.gallery import GalleryImage
    import json
    gallery_sources = json.loads((reconciliation.REPOSITORY_ROOT / "galeria/metadados.json").read_text())
    expected_paths = {item["slug"]: item["file_path"] for item in gallery_sources}
    for image in db.query(GalleryImage).filter(GalleryImage.slug.in_(expected_paths)).all():
        assert image.file_path == expected_paths[image.slug]
        assert "corvia-corpus-snapshot" not in image.file_path
