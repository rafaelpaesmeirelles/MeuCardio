"""Parte B da correção coordenada de 02/09/2026: registra a causa exata pela
qual 22 registros com `review_status="revisado"` seguem `published=False`,
até então sem `review_note` — o que a auditoria classificou como "publicado
pendente sem justificativa".

Investigação (não repita: os 22 slugs abaixo já foram conferidos um a um
contra o banco em produção): 21 são órfãos da fusão de duplicatas de
26/08/2026 (PR #528) — cada um tem um substituto vivo e publicado sob outro
slug, cobrindo o mesmo estudo/evidência. Publicá-los criaria uma segunda tela
do mesmo conteúdo científico, potencialmente divergente da versão corrigida.
O 22º (`chagas-hiv-profilaxia-secundaria-com-benznidazol-com-cd4-abaixo-de-200`)
não é órfão: tem um conflito de dose não resolvido na própria diretriz-fonte
(duas frequências de benznidazol diferentes no mesmo capítulo) — blocker
clínico real, não um problema de deduplicação.

NUNCA publica nada. Só preenche `review_note` (o campo feito para esta
anotação editorial), deixando `published`/`review_status` como estavam.
Idempotente — pode rodar de novo sem duplicar texto, sempre sobrescreve com
o mesmo conteúdo determinístico.

Rodar (mesmo padrão dos outros comandos de `app/commands/`):
    python -m app.commands.annotate_deduplicated_orphans_20260902
"""
from __future__ import annotations

import json

from app.core.db import SessionLocal
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy

NOTA_ORFAO = (
    "Órfão de deduplicação (achado na auditoria de 02/09/2026, confirmado "
    "contra a fusão de duplicatas de 26/08/2026, PR #528). Substituto vivo e "
    "publicado: {substituto}. Publicar este registro colocaria uma segunda "
    "versão do mesmo estudo no ar, sob slug diferente — mantido despublicado "
    "de propósito, preservado só para auditoria."
)

ORFAOS_ESTUDOS: dict[str, str] = {
    "advor-acetazolamida-diuretico-ic-aguda-descompensada": "advor-mullens-2022-acetazolamida-iv-descongestao-apos-alca",
    "ben-farhat-valvoplastia-por-balao-versus-comissurotomia-cirurgica-na-estenose-mitral": "ben-farhat-valvoplastia-mitral-por-balao-versus-comissurotomia-cirurgica",
    "clorotic-hidroclorotiazida-associada-a-diuretico-de-alca-na-ic-aguda": "clorotic-trullas-2023-hctz-oral-add-on-furosemida-iv",
    "coapt-reparo-mitral-transcateter-na-regurgitacao-mitral-secundaria-e-insuficiencia-cardiaca": "coapt-reparo-mitral-transcateter-na-regurgitacao-secundaria",
    "coralreef-addon-enlicitide-versus-bempedoico-ezetimiba": "coralreef-addon-enlicitide-versus-acido-bempedoico-e-ezetimiba",
    "coralreef-lipids-enlicitide-inibidor-oral-de-pcsk9": "coralreef-lipids-enlicitide-inibidor-oral-de-pcsk9-versus-placebo",
    "deliver-dapagliflozina-icfep": "deliver-consistencia-por-faixa-de-feve-nao-e-reclassificacao-2026",
    "evolut-low-risk-reintervencao-por-regurgitacao-em-6-7-anos-tavi-versus-cirurgia": "evolut-low-risk-seis-anos / evolut-low-risk-cinco-anos",
    "finearts-hf-finerenona-na-icfem-e-icfep": "finearts-hf-populacao-feve-maior-igual-40-faixa-historica-icfei",
    "interheart-fator-psicossocial-risco-de-infarto": "interheart-fatores-de-risco-modificaveis-para-infarto-no-mundo",
    "invictus-rivaroxabana-versus-varfarina-na-fa-da-cardiopatia-reumatica": "invictus-rivaroxabana-na-fibrilacao-atrial-da-valvopatia-reumatica",
    "mitra-fr-reparo-percutaneo-versus-tratamento-clinico-na-regurgitacao-mitral-secundaria": "mitra-fr-reparo-percutaneo-na-regurgitacao-mitral-secundaria",
    "momentum-3-relatorio-final-dav-de-fluxo-centrifugo": "momentum-3-dispositivo-de-assistencia-ventricular-centrifugo-vs-axial / momentum-3-acesso-continuado-heartmate-3-em-2200-implantes",
    "paragon-hf-sacubitril-valsartana-na-icfep": "paragon-hf-neutro-e-a-faixa-45-49-nao-e-paradigm",
    "peitho-fibrinolise-em-tep-de-risco-intermediario": "peitho-tenecteplase-versus-placebo-tep-normotenso-vd-e-troponina / hi-peitho-trombolise-dirigida-por-cateter-tep-risco-intermediario-alto",
    "remedy-registro-global-de-cardiopatia-reumatica": "remedy-registro-global-de-cardiopatia-reumatica-caracteristicas-basais-2015 / remedy-registro-global-de-cardiopatia-reumatica-desfechos-em-2-anos-2016",
    "scd-heft-cdi-vs-amiodarona-na-icfer": "scd-heft-amiodarona-ou-cdi-na-insuficiencia-cardiaca",
    "select-lincoff-semaglutida-24mg-mace-obesidade-sem-diabetes": "select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes",
    "summit-tirzepatida-icfep-com-obesidade": "tirzepatida-e-icfep-com-obesidade-o-ensaio-summit",
}

ORFAOS_EVIDENCIAS: dict[str, str] = {
    "avaliar-sintomas-com-metodo-que-ajude-o-paciente-a-descrever-a-experiencia": "avaliar-sintomas-por-metodos-que-ajudem-o-paciente-a-descrever-a-experiencia",
    "avaliacao-de-estresse-psicossocial-em-dcv": "esc-2021-avaliacao-de-sintomas-de-estresse-e-estressores-psicossociais / esc-2021-avaliacao-de-estressores-psicossociais-como-modificador-de-risco-cardiovascular",
}

BLOCKER_CHAGAS_SLUG = "chagas-hiv-profilaxia-secundaria-com-benznidazol-com-cd4-abaixo-de-200"

NOTA_BLOCKER_CHAGAS = (
    "Blocker clínico não resolvido (achado na auditoria de 02/09/2026): a "
    "fonte (Diretriz SBC sobre Cardiomiopatia da Doença de Chagas, 2023) "
    "descreve o esquema de profilaxia secundária com benznidazol em duas "
    "frequências diferentes no mesmo capítulo (2x/semana no quadro de "
    "recomendações vs. 3x/semana no texto corrido) e dois graus de convicção "
    "diferentes para a mesma conduta — incoerência interna da própria fonte, "
    "não um erro de transcrição. Mantido despublicado até confirmação da "
    "frequência correta contra a diretriz vigente ou uma fonte primária "
    "adicional. Não confundir com os demais 21 órfãos desta rodada: aqui não "
    "há duplicata a evitar, há uma dúvida clínica real não respondida."
)


def anotar() -> dict:
    anotados = {"estudos": [], "evidencias": []}
    with SessionLocal() as db:
        for slug, substituto in ORFAOS_ESTUDOS.items():
            item = db.query(ScientificStudy).filter(ScientificStudy.slug == slug).one()
            assert item.published is False, f"{slug} não deveria estar published=true"
            item.review_note = NOTA_ORFAO.format(substituto=substituto)
            anotados["estudos"].append(slug)

        for slug, substituto in ORFAOS_EVIDENCIAS.items():
            item = db.query(EvidenceRecord).filter(EvidenceRecord.slug == slug).one()
            assert item.published is False, f"{slug} não deveria estar published=true"
            item.review_note = NOTA_ORFAO.format(substituto=substituto)
            anotados["evidencias"].append(slug)

        chagas = db.query(EvidenceRecord).filter(EvidenceRecord.slug == BLOCKER_CHAGAS_SLUG).one()
        assert chagas.published is False
        chagas.review_note = NOTA_BLOCKER_CHAGAS
        anotados["evidencias"].append(chagas.slug)

        db.commit()
    return anotados


if __name__ == "__main__":
    resultado = anotar()
    print(json.dumps({
        "estudos_anotados": len(resultado["estudos"]),
        "evidencias_anotadas": len(resultado["evidencias"]),
        "total": len(resultado["estudos"]) + len(resultado["evidencias"]),
    }, ensure_ascii=False, indent=2))
