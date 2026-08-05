from app.api.receituario import ItemIn, _item_snapshot, _resolver
from app.models.drug import Drug


def test_uso_continuo_remove_quantidade_e_fica_no_snapshot(db):
    medicamento = Drug(
        slug="losartana-uso-continuo",
        generic_name="Losartana potássica",
        drug_class="BRA",
        published=True,
    )
    db.add(medicamento)
    db.commit()

    item = _resolver(db, [ItemIn(
        drug_slug=medicamento.slug,
        descricao="Losartana potássica",
        apresentacao="50 mg — comprimido",
        quantidade="60 comprimidos",
        quantidade_extenso="sessenta comprimidos",
        posologia="Tomar 1 comprimido a cada 12 horas.",
        uso_continuo=True,
    )])[0]

    assert item.quantidade is None
    assert item.uso_continuo is True
    assert _item_snapshot(item)["uso_continuo"] is True
