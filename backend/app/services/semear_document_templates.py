# -*- coding: utf-8 -*-
"""Semeia os modelos de documento do sistema — Tarefa 30, pedido do Rafael em
30/07/2026 ("tudo junto, mesma rodada"): atestado médico padrão, declaração
de acompanhante, atestado de aptidão física para atividade física e
documento em branco, mais o registro de listagem da avaliação de risco
cirúrgico (que tem fluxo próprio, ver `app/services/preop.py` e
`app/api/documents.py`).

Upsert por `slug_sistema`, mesmo padrão de `carregar_controlados.semear_tipos()`
— roda quantas vezes for preciso sem duplicar.

Fontes do texto de cada modelo:
- Atestado padrão: Resolução CFM nº 2.381/2024 (substitui a Resolução CFM nº
  1.658/2002, revogada), que normatiza a emissão de atestado médico — exige
  nome completo do paciente, data, identificação e registro do médico,
  período de afastamento, e trata a omissão do diagnóstico como direito do
  paciente (só consta se ele consentir expressamente).
- Declaração de acompanhante: não tem layout oficial fixo — é praxe
  documental para justificar a presença do acompanhante junto a terceiros
  (empregador, escola). O texto não cita norma que não regule especificamente
  este documento.
- Atestado de aptidão física: Atualização da Diretriz em Cardiologia do
  Esporte e do Exercício da SBC/SBMEE (Ghorayeb N, Stein R et al. Arq Bras
  Cardiol. 2019;112(3):326-368, DOI 10.5935/abc.20190048) e Posicionamento
  sobre Avaliação Pré-participação Cardiológica após a Covid-19 (Colombo CSS
  et al. Arq Bras Cardiol. 2021;116(6):1213-1226, PMID 34133609, DOI
  10.36660/abc.20210368).
- Documento em branco: sem texto fixo — título e corpo livres, preenchidos
  pelo médico a cada geração.
"""
from sqlalchemy.orm import Session

from app.models.clinical_docs import DocumentTemplate

MODELOS = [
    dict(
        slug_sistema="atestado-medico-padrao",
        title="Atestado médico",
        doc_type="atestado",
        body=(
            "Atesto, para os devidos fins, que o(a) paciente {{paciente_nome}} foi atendido(a) "
            "por mim nesta data e necessita de afastamento de suas atividades habituais por "
            "{{dias_afastamento}} dia(s), a partir de {{data_inicio}}.\n\n"
            "{{diagnostico}}\n\n"
            "Este atestado é fornecido a pedido do(a) paciente, nos termos da Resolução CFM "
            "nº 2.381/2024."
        ),
    ),
    dict(
        slug_sistema="declaracao-acompanhante",
        title="Declaração de acompanhante",
        doc_type="outro",
        body=(
            "Declaro, para os devidos fins, que {{acompanhante_nome}} acompanhou o(a) "
            "paciente {{paciente_nome}} em atendimento médico realizado em "
            "{{data_atendimento}}, no período de {{periodo}}, tendo sua presença sido "
            "necessária em razão do estado de saúde do paciente."
        ),
    ),
    dict(
        slug_sistema="atestado-atividade-fisica",
        title="Atestado de aptidão física (avaliação cardiológica)",
        doc_type="atestado",
        body=(
            "Atesto, para os devidos fins, que o(a) paciente {{paciente_nome}}, "
            "{{idade}} anos, foi avaliado(a) por mim em consulta cardiológica, incluindo "
            "{{exames_realizados}}, encontrando-se apto(a), do ponto de vista cardiovascular, "
            "à prática de {{modalidade}}.\n\n"
            "{{restricoes}}\n\n"
            "Avaliação fundamentada na Atualização da Diretriz em Cardiologia do Esporte e do "
            "Exercício da Sociedade Brasileira de Cardiologia e da Sociedade Brasileira de "
            "Medicina do Exercício e do Esporte (Arq Bras Cardiol. 2019;112(3):326-368, DOI "
            "10.5935/abc.20190048) e, quando aplicável, no Posicionamento sobre Avaliação "
            "Pré-participação Cardiológica após a Covid-19 (Arq Bras Cardiol. 2021;116(6):"
            "1213-1226, PMID 34133609)."
        ),
    ),
    dict(
        slug_sistema="documento-em-branco",
        title="Documento em branco",
        doc_type="outro",
        body="{{conteudo}}",
    ),
    dict(
        slug_sistema="avaliacao-risco-cirurgico",
        title="Avaliação cardiológica de risco cirúrgico (pré-operatória)",
        doc_type="laudo",
        # Corpo não usa substituição de {{variável}} — este modelo tem fluxo
        # próprio (ver POST /document-templates/avaliacao-preoperatoria), que
        # calcula o RCRI e monta o rascunho a partir de `app/services/preop.py`.
        # O texto aqui só aparece se alguém tentar gerar por engano pela rota
        # genérica de templates.
        body=(
            "Este modelo é gerado pela calculadora de risco perioperatório, não pelo "
            "formulário genérico de variáveis — use \"Avaliação de risco cirúrgico\" na "
            "tela de Documentos."
        ),
    ),
]


def semear(db: Session) -> dict:
    novos = atualizados = 0
    for m in MODELOS:
        existente = db.query(DocumentTemplate).filter(
            DocumentTemplate.slug_sistema == m["slug_sistema"]).first()
        if existente:
            existente.title, existente.doc_type, existente.body = (
                m["title"], m["doc_type"], m["body"])
            atualizados += 1
        else:
            db.add(DocumentTemplate(owner_id=None, **m))
            novos += 1
    db.commit()
    return {"novos": novos, "atualizados": atualizados, "total": len(MODELOS)}
