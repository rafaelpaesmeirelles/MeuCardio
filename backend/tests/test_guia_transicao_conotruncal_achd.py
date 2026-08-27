from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "content/Cardiopatias_congênitas/transicao-conotruncal-pediatria-para-achd-dossie-clinico-operacional.md"


def texto() -> str:
    return DOC.read_text(encoding="utf-8")


def test_documento_existe_e_permanece_pendente_de_revisao():
    value = texto()
    assert "review_status: pendente_revisao" in value
    assert "fonte_producao: chatgpt" in value
    assert "10.1161/CIR.0000000000001402" in value
    assert "10.1161/JAHA.122.025278" in value


def test_transicao_e_transferencia_nao_sao_fundidas():
    value = texto()
    assert "Transição não é sinônimo de transferência" in value
    assert "educação estruturada" in value
    assert "políticas e procedimentos formais" in value


def test_dossie_preserva_anatomia_operacoes_fisiologia_e_ritmo():
    value = texto()
    for required in (
        "Diagnóstico anatômico nativo",
        "Linha do tempo de operações e cateterismos",
        "Via de saída do VD e circulação pulmonar",
        "Ventrículos e hemodinâmica residual",
        "Aorta, valva sistêmica e coronárias",
        "Ritmo, condução e dispositivos",
    ):
        assert required in value


def test_conecta_pediatria_achd_sem_apagar_as_lesoes_especificas():
    value = texto()
    assert "cardiopatia-congenita-do-adulto-achd-manejo-abrangente-esc-2020.md" in value
    assert "seguimento-tardio-de-tetralogia-de-fallot-e-coarctacao-de-aorta-no-adulto.md" in value
    assert "dupla-via-de-saida-de-ventriculo-direito-classificacao-anatomica-estrategia-cirurgica-e-desfechos.md" in value
    assert "tronco-arterial-comum-classificacao-associacao-com-22q11-e-desfechos-cirurgicos-contemporaneos.md" in value


def test_nao_cria_atalhos_clinicos_indevidos():
    value = texto().casefold()
    for required in (
        "não diagnosticar 22q11.2 apenas pela anatomia cardíaca",
        "não classificar todo adulto com cardiopatia conotruncal como candidato automático a antibiótico profilático",
        "nenhuma decisão de cdi deve ser inferida automaticamente",
        "não autorizam anticoagulação, antiagregação ou suspensão farmacológica automática",
        "não deve gerar rótulo automático de “gestação segura” ou “gestação proibida”",
    ):
        assert required in value


def test_nao_contem_posologia_energia_ou_limiar_cirurgico_universal():
    value = texto().casefold()
    for forbidden in (
        "mg/kg",
        "mcg/kg/min",
        "j/kg",
        "joule",
        "ml/h",
        "ml/kg/h",
    ):
        assert forbidden not in value
    assert "não cria limiares universais de intervenção" in value


def test_cartao_de_emergencia_nao_atrasa_estabilizacao():
    value = texto()
    assert "Cartão de emergência recomendado" in value
    assert "não substitui estabilização de emergência" in value
    assert "atrasar estabilização de emergência aguardando contato com centro ACHD" in value
