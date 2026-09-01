"""Aliases de slugs de estudos consolidados sem quebrar links persistidos.

Os slugs à esquerda foram retirados do manifesto por serem duplicatas do
mesmo PMID/DOI. Favoritos, URLs salvas e progresso de trilhas podem continuar
referenciando-os; por isso a troca precisa ser explícita e versionada.
"""

STUDY_SLUG_ALIASES: dict[str, str] = {
    "deliver-dapagliflozina-icfep":
        "deliver-consistencia-por-faixa-de-feve-nao-e-reclassificacao-2026",
    "paragon-hf-sacubitril-valsartana-na-icfep":
        "paragon-hf-neutro-e-a-faixa-45-49-nao-e-paradigm",
    "finearts-hf-finerenona-na-icfem-e-icfep":
        "finearts-hf-populacao-feve-maior-igual-40-faixa-historica-icfei",
    "summit-tirzepatida-icfep-com-obesidade":
        "tirzepatida-e-icfep-com-obesidade-o-ensaio-summit",
    "advor-acetazolamida-diuretico-ic-aguda-descompensada":
        "advor-mullens-2022-acetazolamida-iv-descongestao-apos-alca",
    "select-lincoff-semaglutida-24mg-mace-obesidade-sem-diabetes":
        "select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes",
    "clorotic-hidroclorotiazida-associada-a-diuretico-de-alca-na-ic-aguda":
        "clorotic-trullas-2023-hctz-oral-add-on-furosemida-iv",
    "peitho-fibrinolise-em-tep-de-risco-intermediario":
        "peitho-tenecteplase-versus-placebo-tep-normotenso-vd-e-troponina",
    "ben-farhat-valvoplastia-por-balao-versus-comissurotomia-cirurgica-na-estenose-mitral":
        "ben-farhat-valvoplastia-mitral-por-balao-versus-comissurotomia-cirurgica",
    "invictus-rivaroxabana-versus-varfarina-na-fa-da-cardiopatia-reumatica":
        "invictus-rivaroxabana-na-fibrilacao-atrial-da-valvopatia-reumatica",
    "remedy-registro-global-de-cardiopatia-reumatica":
        "remedy-registro-global-de-cardiopatia-reumatica-desfechos-em-2-anos-2016",
    "scd-heft-cdi-vs-amiodarona-na-icfer":
        "scd-heft-amiodarona-ou-cdi-na-insuficiencia-cardiaca",
    "coapt-reparo-mitral-transcateter-na-regurgitacao-mitral-secundaria-e-insuficiencia-cardiaca":
        "coapt-reparo-mitral-transcateter-na-regurgitacao-secundaria",
    "mitra-fr-reparo-percutaneo-versus-tratamento-clinico-na-regurgitacao-mitral-secundaria":
        "mitra-fr-reparo-percutaneo-na-regurgitacao-mitral-secundaria",
    "evolut-low-risk-reintervencao-por-regurgitacao-em-6-7-anos-tavi-versus-cirurgia":
        "evolut-low-risk-seis-anos",
    "coralreef-lipids-enlicitide-inibidor-oral-de-pcsk9":
        "coralreef-lipids-enlicitide-inibidor-oral-de-pcsk9-versus-placebo",
    "coralreef-addon-enlicitide-versus-bempedoico-ezetimiba":
        "coralreef-addon-enlicitide-versus-acido-bempedoico-e-ezetimiba",
    "early-bosentana-classe-funcional-ii-hipertensao-arterial-pulmonar":
        "early-bosentana-na-hap-classe-funcional-ii",
    "starts-1-sildenafila-pediatrica-hipertensao-arterial-pulmonar":
        "starts-1-sildenafila-oral-em-criancas-com-hipertensao-arterial-pulmonar",
    "starts-2-sobrevida-longo-prazo-sildenafila-pediatrica-hipertensao-arterial-pulmonar":
        "starts-2-sildenafila-sobrevida-hipertensao-pulmonar-pediatrica",
    "madit-ii-cdi-profilatico-pos-infarto-com-fracao-de-ejecao-reduzida":
        "madit-ii-cdi-profilatico-pos-iam",
    "madit-crt-ressincronizacao-cardiaca-na-prevencao-de-eventos-de-insuficiencia-cardiaca":
        "madit-crt-ressincronizacao-cardiaca-na-insuficiencia-cardiaca-leve",
    "east-afnet4-controle-de-ritmo-precoce-na-fibrilacao-atrial":
        "east-afnet-4-controle-precoce-do-ritmo-na-fibrilacao-atrial",
    "raft-ressincronizacao-cardiaca-na-insuficiencia-cardiaca-leve-a-moderada":
        "raft-ressincronizacao-cardiaca-em-ic-leve-a-moderada",
    "bridge-anticoagulacao-ponte-perioperatoria-na-fibrilacao-atrial":
        "bridge-sem-ponte-de-heparina-na-fa-periprocedimento",
    "pause-manejo-perioperatorio-de-anticoagulante-oral-direto":
        "pause-interrupcao-perioperatoria-de-doac-na-fibrilacao-atrial",
    "chap-tratamento-da-hipertensao-cronica-leve-na-gravidez":
        "chap-tratamento-hipertensao-cronica-leve-na-gestacao",
    "chips-controle-menos-rigoroso-versus-rigoroso-da-hipertensao-na-gravidez":
        "chips-controle-tight-versus-less-tight-da-hipertensao-na-gestacao",
    "fresh-firibastate-inibidor-da-aminopeptidase-a-na-hipertensao-resistente":
        "fresh-firibastate-em-hipertensos-com-sobrepeso-estudo-aberto-fase-2",
    "declare-timi-58-dapagliflozina-desfechos-cardiovasculares-diabetes-tipo-2":
        "declare-timi-58-dapagliflozina-em-diabetes-tipo-2",
    "oconnor-2009-hf-action-treinamento-fisico-em-insuficiencia-cardiaca":
        "hf-action-exercicio-na-icfer-estavel",
    "rate-af-digoxina-versus-bisoprolol-controle-de-frequencia-na-fa":
        "rate-af-digoxina-versus-bisoprolol-na-fa-permanente",
    "poet-5-anos-antibiotico-oral-parcial-endocardite":
        "poet-seguimento-cinco-anos-terapia-oral-parcial-endocardite",
    "apple-heart-study-smartwatch-para-deteccao-de-fibrilacao-atrial":
        "apple-heart-study-smartwatch-na-deteccao-de-fibrilacao-atrial",
    "interheart-fator-psicossocial-risco-de-infarto":
        "interheart-fatores-de-risco-modificaveis-para-infarto-no-mundo",
    "ischemia-estrategia-invasiva-inicial-na-dac-estavel":
        "ischemia-invasivo-vs-conservador-dac-estavel",
}


def canonical_study_slug(slug: str) -> str:
    """Devolve o slug publicado que substitui uma duplicata retirada."""
    return STUDY_SLUG_ALIASES.get(slug, slug)


def canonicalize_study_slugs(slugs: list[str] | None) -> list[str]:
    """Migra uma lista persistida, removendo duplicatas após a conversão."""
    return sorted({canonical_study_slug(slug) for slug in (slugs or [])})
