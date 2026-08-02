from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.audit import AuditLog
from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.drug import Drug
from app.services import cmed_precos

router = APIRouter(prefix="/api/drugs", tags=["medicamentos"])

FIELDS = (
    "slug generic_name brand_names drug_class mechanism presentations "
    "commercial_presentations dosing "
    "renal_adjustment hepatic_adjustment contraindications interactions monitoring "
    "indications adverse_effects notes "
    "pregnancy lactation outcomes cost_reference half_life_hours half_life_note "
    "sbp_reduction_mmhg dbp_reduction_mmhg bp_evidence_source "
    "references review_status"
).split()


def _dump(d: Drug) -> dict:
    return {f: getattr(d, f) for f in FIELDS}


ARQUIVO_INTERACOES = "/medicamentos/interacoes.json"


def _interacoes_curadas() -> list[dict]:
    """Lê a base par a par do disco a cada chamada.

    É bind mount somente-leitura, igual às outras frentes de conteúdo: corrigir
    uma interação é editar o JSON e importar, sem rebuild e sem migração. Se o
    arquivo faltar ou estiver quebrado, devolve lista vazia — a rota continua
    respondendo com as menções em prosa em vez de derrubar a tela inteira.
    """
    import json

    try:
        with open(ARQUIVO_INTERACOES, encoding="utf-8") as f:
            dados = json.load(f)
        return dados if isinstance(dados, list) else []
    except (OSError, ValueError):
        return []


class InteracoesIn(BaseModel):
    slugs: list[str]


class MeiaVidaIn(BaseModel):
    half_life_hours: float | None = None
    half_life_note: str | None = None


class EficaciaPAIn(BaseModel):
    sbp_reduction_mmhg: float | None = None
    dbp_reduction_mmhg: float | None = None
    bp_evidence_source: str | None = None


class ApresentacaoComercial(BaseModel):
    brand_name: str
    manufacturer: str
    form: str = "comprimido"
    dosage: str
    pack_sizes: list[int] = []
    generic_available: bool = False


@router.get("")
def list_drugs(
    q: str | None = None,
    drug_class: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    # Só medicamento publicado aparece — mesmo checkpoint das outras frentes.
    query = db.query(Drug).filter(Drug.published.is_(True))
    if q:
        query = query.filter(Drug.generic_name.ilike(f"%{q}%"))
    if drug_class:
        query = query.filter(Drug.drug_class == drug_class)
    return [
        {"slug": d.slug, "generic_name": d.generic_name, "drug_class": d.drug_class,
         "review_status": d.review_status}
        for d in query.order_by(Drug.generic_name).limit(300)
    ]


@router.get("/compare")
def compare(
    slugs: list[str] = Query(..., alias="slug"),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    if not 1 <= len(slugs) <= 4:
        raise HTTPException(status_code=422, detail="Selecione de 1 a 4 medicamentos.")
    drugs = db.query(Drug).filter(Drug.slug.in_(slugs), Drug.published.is_(True)).all()
    found = {d.slug for d in drugs}
    missing = [s for s in slugs if s not in found]
    if missing:
        raise HTTPException(status_code=404, detail=f"Não encontrado: {', '.join(missing)}")
    return {"drugs": [_dump(d) for d in drugs]}


@router.post("/interacoes")
def checar_interacoes(
    dados: InteracoesIn, db: Session = Depends(get_db), _=Depends(current_user)
):
    """Cruza a lista de fármacos do médico com a base de interações.

    Devolve DOIS blocos separados de propósito, e a separação é o ponto do
    recurso:

    - `verificadas`: pares da base curada, cada um com gravidade e fonte
      nominal. É o único bloco em que o sistema afirma alguma coisa.
    - `mencoes`: o texto de `interactions` da bula de cada fármaco escolhido,
      quando cita outro fármaco da mesma lista. **Sem gravidade atribuída** —
      é o que a bula diz, não uma classificação nossa. Graduar isso sem fonte
      seria inventar a parte mais importante da resposta.

    O `aviso` volta sempre: base pequena, ausência de alerta não é atestado de
    segurança.
    """
    slugs = [s for s in dict.fromkeys(dados.slugs) if s]
    if not 2 <= len(slugs) <= 10:
        raise HTTPException(status_code=422, detail="Selecione de 2 a 10 medicamentos.")

    drogas = db.query(Drug).filter(Drug.slug.in_(slugs), Drug.published.is_(True)).all()
    achados = {d.slug for d in drogas}
    ausentes = [s for s in slugs if s not in achados]
    if ausentes:
        raise HTTPException(status_code=404, detail=f"Não encontrado: {', '.join(ausentes)}")

    nome = {d.slug: d.generic_name for d in drogas}
    selecionados = set(achados)

    verificadas: list[dict] = []
    avisos_de_classe: list[dict] = []
    for i in _interacoes_curadas():
        farmacos = i.get("farmacos", [])
        envolvidos = [f for f in farmacos if f in selecionados]
        registro = {
            **{k: i[k] for k in ("slug", "gravidade", "efeito", "conduta", "fonte") if k in i},
            "classe_oposta": i.get("classe_oposta"),
            "farmacos": [{"slug": s, "nome": nome[s]} for s in envolvidos],
        }
        # Par fármaco×fármaco: os dois têm de estar na lista, e aí o alerta é
        # sobre a combinação que o médico montou.
        if len(farmacos) == 2 and len(envolvidos) == 2:
            verificadas.append(registro)
        # Fármaco×classe: só um lado é fármaco nomeado; o outro é uma classe
        # inteira. Fica em bloco SEPARADO de propósito — misturar com o de cima
        # faria "contraindicada" aparecer no topo por causa de um fármaco que o
        # paciente talvez nem use, e alerta que grita sem motivo é alerta que o
        # médico aprende a ignorar.
        elif len(farmacos) == 1 and len(envolvidos) == 1:
            avisos_de_classe.append(registro)

    ordem = {"contraindicada": 0, "grave": 1, "moderada": 2, "leve": 3}
    verificadas.sort(key=lambda v: ordem.get(v.get("gravidade", ""), 9))
    avisos_de_classe.sort(key=lambda v: ordem.get(v.get("gravidade", ""), 9))

    mencoes = []
    for d in drogas:
        for texto in (d.interactions or []):
            baixo = texto.lower()
            citados = [
                s for s in selecionados
                if s != d.slug and nome[s].split()[0].lower() in baixo
            ]
            if citados:
                mencoes.append({
                    "de": {"slug": d.slug, "nome": d.generic_name},
                    "cita": [{"slug": s, "nome": nome[s]} for s in citados],
                    "texto": texto,
                })

    return {
        "selecionados": [{"slug": d.slug, "nome": d.generic_name} for d in drogas],
        "verificadas": verificadas,
        "avisos_de_classe": avisos_de_classe,
        "mencoes": mencoes,
        "aviso": (
            "A base de interações verificadas é pequena e cresce por conferência "
            "contra bula. Nenhum alerta aqui NÃO significa ausência de interação — "
            "significa que não há registro com fonte rastreável para esta combinação."
        ),
    }


CONDICOES = {
    "gestacao": ("pregnancy", "Gestação"),
    "lactacao": ("lactation", "Lactação"),
    "renal": ("renal_adjustment", "Doença renal crônica"),
    "hepatica": ("hepatic_adjustment", "Hepatopatia"),
}


class CondicoesIn(BaseModel):
    slugs: list[str]
    condicoes: list[str]


@router.post("/condicoes")
def checar_condicoes(
    dados: CondicoesIn, db: Session = Depends(get_db), _=Depends(current_user)
):
    """Cruza os fármacos escolhidos com condições clínicas especiais do paciente.

    Não há base nova aqui: usa o que os verbetes já trazem com fonte conferida
    — `contraindications`, `pregnancy`, `lactation`, `renal_adjustment` e
    `hepatic_adjustment`.

    A resposta distingue TRÊS estados por fármaco e condição, e a distinção é o
    recurso:

    - `achados`: o verbete diz alguma coisa sobre aquela condição;
    - `sem_informacao`: o campo está vazio no verbete. **Não é atestado de
      segurança** — é ausência de dado, e aparece nomeado justamente porque a
      cobertura é desigual (contraindicações em 81% dos fármacos, mas gestação
      em 14% e lactação em 3%). Um alerta que ficasse calado nesses casos
      diria "pode usar" sem ninguém ter afirmado isso.

    A busca em `contraindications` é textual e por isso entra como achado
    separado, com o trecho à vista: quem classifica é o leitor.
    """
    slugs = [s for s in dict.fromkeys(dados.slugs) if s]
    condicoes = [c for c in dict.fromkeys(dados.condicoes) if c in CONDICOES]
    if not slugs:
        raise HTTPException(status_code=422, detail="Selecione ao menos um medicamento.")
    if not condicoes:
        raise HTTPException(
            status_code=422,
            detail=f"Informe ao menos uma condição: {', '.join(CONDICOES)}.",
        )

    drogas = db.query(Drug).filter(Drug.slug.in_(slugs), Drug.published.is_(True)).all()
    achados_ausentes = [s for s in slugs if s not in {d.slug for d in drogas}]
    if achados_ausentes:
        raise HTTPException(
            status_code=404, detail=f"Não encontrado: {', '.join(achados_ausentes)}"
        )

    # Termos que revelam a condição citada dentro do texto livre de
    # contraindicação. Deliberadamente curtos e amplos: aqui um falso positivo
    # custa uma leitura a mais, e um falso negativo custa a contraindicação.
    PISTAS = {
        "gestacao": ("gest", "grav", "gravíd"),
        "lactacao": ("lacta", "amament", "leite"),
        "renal": ("renal", "rim", "clearance", "depuração", "diálise"),
        "hepatica": ("hepát", "hepat", "fígado", "cirros"),
    }

    achados, sem_informacao = [], []
    for d in drogas:
        for c in condicoes:
            campo, rotulo = CONDICOES[c]
            texto = (getattr(d, campo, None) or "").strip()
            citados = [
                t for t in (d.contraindications or [])
                if any(p in t.lower() for p in PISTAS[c])
            ]
            if texto or citados:
                achados.append({
                    "farmaco": {"slug": d.slug, "nome": d.generic_name},
                    "condicao": c, "condicao_rotulo": rotulo,
                    "campo_proprio": texto or None,
                    "contraindicacoes_citando": citados,
                    "review_status": d.review_status,
                })
            else:
                sem_informacao.append({
                    "farmaco": {"slug": d.slug, "nome": d.generic_name},
                    "condicao": c, "condicao_rotulo": rotulo,
                })

    return {
        "achados": achados,
        "sem_informacao": sem_informacao,
        "aviso": (
            "Ausência de achado NÃO é atestado de segurança: significa que o verbete "
            "não traz informação para aquela condição. A cobertura é desigual — "
            "contraindicações constam em 81% dos fármacos, ajuste renal em 23%, "
            "gestação em 14% e lactação em 3%."
        ),
    }


@router.get("/{slug}")
def get_drug(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    d = db.query(Drug).filter(Drug.slug == slug, Drug.published.is_(True)).first()
    if not d:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
    return _dump(d)


@router.get("/{slug}/apresentacoes")
def apresentacoes_comerciais(
    slug: str, uf: str | None = Query(None, max_length=2),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    """Marca, laboratório, apresentação e PMC via CMED (Tarefa A/B,
    CLAUDE.md) — para o médico ver tudo ao digitar a prescrição. UF default
    vem do conselho do médico (`users.council_state`); nem sempre é onde o
    paciente compra, por isso o parâmetro `uf` sobrescreve.

    Ausência de linha aqui é, na maioria das vezes, informação real (a
    substância não tem produto com PMC publicado no Brasil, ou só existe em
    combinação) — nunca tratada como erro."""
    d = db.query(Drug).filter(Drug.slug == slug, Drug.published.is_(True)).first()
    if not d:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")

    versao = db.query(CmedVersao).order_by(CmedVersao.id.desc()).first()
    if not versao:
        return {
            "generic_name": d.generic_name, "uf": None, "cmed_publicado_em": None,
            "apresentacoes": [], "aviso": "Nenhuma lista da CMED foi importada ainda.",
        }

    linhas = db.query(CmedApresentacao).filter(
        CmedApresentacao.drug_id == d.id, CmedApresentacao.cmed_versao_id == versao.id,
    ).all()

    uf_usada = (uf or user.council_state or "").upper() or None
    apresentacoes = [
        {
            "produto": l.produto, "laboratorio": l.laboratorio, "apresentacao": l.apresentacao,
            "ggrem": l.ggrem, "registro": l.registro, "restricao_hospitalar": l.restricao_hospitalar,
            "preco": cmed_precos.preco_pmc(l.pmc_por_aliquota, uf_usada),
        }
        for l in linhas
    ]
    return {
        "generic_name": d.generic_name, "uf": uf_usada, "cmed_versao_id": versao.id,
        "cmed_publicado_em": versao.publicado_em,
        "apresentacoes": apresentacoes,
        "aviso": None if apresentacoes else (
            "Sem apresentação com preço publicado pela CMED para esta substância — "
            "pode ser produto genuinamente ausente da lista, ou existir só em combinação "
            "de dose fixa (que não tem o mesmo PMC do princípio isolado)."
        ),
    }


@router.patch("/{slug}/meia-vida")
def definir_meia_vida(
    slug: str, dados: MeiaVidaIn, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """Só admin define este número — não é extraído automaticamente do texto
    livre de farmacocinética, que é solto demais pra confiar sem revisão humana."""
    d = db.query(Drug).filter(Drug.slug == slug).first()
    if not d:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
    if dados.half_life_hours is not None and not (0 < dados.half_life_hours < 1000):
        raise HTTPException(status_code=422, detail="Valor de meia-vida fora de uma faixa plausível.")

    d.half_life_hours = dados.half_life_hours
    d.half_life_note = dados.half_life_note
    db.add(AuditLog(
        user_id=admin.id, action="definir_meia_vida", entity="drug", entity_id=slug,
        detail={"half_life_hours": dados.half_life_hours},
    ))
    db.commit()
    return _dump(d)


@router.put("/{slug}/apresentacoes-comerciais")
def definir_apresentacoes_comerciais(
    slug: str, dados: list[ApresentacaoComercial],
    db: Session = Depends(get_db), admin=Depends(require_admin),
):
    """Substitui a lista inteira de apresentações comerciais do medicamento.
    Só admin — dado comercial (marca, laboratório, caixa) exige a mesma
    checagem de fonte que qualquer outro dado clínico neste sistema."""
    d = db.query(Drug).filter(Drug.slug == slug).first()
    if not d:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
    d.commercial_presentations = [item.model_dump() for item in dados]
    db.add(AuditLog(
        user_id=admin.id, action="definir_apresentacoes_comerciais", entity="drug", entity_id=slug,
        detail={"quantidade": len(dados)},
    ))
    db.commit()
    return _dump(d)
