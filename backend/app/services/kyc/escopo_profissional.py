"""Escopo legal de prescrição por profissão — Trabalho 11, ampliação de
06/08/2026.

Pedido do Rafael: "Consulte a legislacao e libere o tipo de receituario e
o item a ser prescrito [...] somente o que a lei permite para cada
profissao de acordo com as legislacoes/decisoes mais recentes em
vigencia." Pesquisa feita por WebSearch durante a sessão, um conselho por
vez, citando lei/resolução real — resumo e fonte por conselho abaixo.
Decisões de recorte confirmadas com o Rafael em 06/08/2026 onde a lei é
ambígua ou está sub judice (ver cada bloco).

Três escopos, do mais amplo ao mais restrito:

- **ESCOPO_COMPLETO** (CRM): sem restrição adicional daqui — é o
  receituário pleno já construído na Tarefa 27, com toda a classificação
  por lista da Portaria 344/98.
- **ESCOPO_RESTRITO_ODONTO** (CRO): Lei 5.081/1966, art. 6º, inciso III —
  o cirurgião-dentista pode prescrever qualquer medicamento com indicação
  odontológica, inclusive a maioria dos controlados da Portaria 344/98,
  **exceto a Lista C4** (retinoides sistêmicos — teratogênicos, sem
  indicação odontológica em nenhuma leitura da norma). É o único limite
  verificável automaticamente pelo sistema; a exigência legal de que a
  prescrição tenha "indicação odontológica" depende do julgamento do
  próprio dentista e não é algo que a Corvia possa checar.
- **ESCOPO_APENAS_ISENTOS** (todos os demais: COREN, CRF, CRN, CREFITO,
  CRP, CREF, CRESS, CRBM, e qualquer profissão fora da lista fixa —
  "OUTRO"): restrito a medicamentos **isentos de prescrição** (tarja "Sem
  Tarja" na CMED — ver `eh_isento_de_prescricao`). Três profissões deste
  grupo têm, na lei, um direito mais amplo do que este recorte concede —
  registrado aqui, não implementado, por decisão explícita do Rafael ou
  por a base de dados não sustentar o recorte com segurança:
    * **COREN** — Lei 7.498/1986, art. 11, alínea "c", e Parecer COFEN
      Nº 03/2023: o enfermeiro pode prescrever medicamentos, mas só
      **dentro de protocolos e rotinas aprovados pela instituição de
      saúde** onde atua, e nunca controlados da Portaria 344/98. A Corvia
      não tem como validar qual protocolo institucional está em vigor
      para cada enfermeiro — fica restrito a isentos até existir um jeito
      de capturar isso (ex.: upload do protocolo, aprovado manualmente).
    * **CRF** — a Resolução CFF Nº 586/2013 formalmente autoriza
      prescrição farmacêutica (isentos sempre; os que exigem prescrição
      médica só dentro de programa/protocolo/parceria formal com outro
      prescritor), mas está com **eficácia suspensa por decisão judicial
      de 1ª instância** que a declarou inconstitucional (o CFF recorreu,
      sem trânsito em julgado até 06/08/2026). Decisão do Rafael:
      restringir a isentos enquanto a suspensão estiver em vigor.
    * **CRN** — Lei 8.234/1991: o nutricionista tem direito consolidado
      (não condicionado, ao contrário do COREN/CRF acima) de prescrever
      **suplemento nutricional**. Não implementado porque a base de
      medicamentos/CMED da Corvia não distingue "suplemento nutricional"
      como categoria própria — os itens dela são medicamentos regulados,
      e boa parte dos suplementos nem está na CMED. Criar esse recorte
      sem essa categoria seria inventar uma fronteira que os dados não
      sustentam.

Documentos não-medicamentosos (atestado de comparecimento, laudo/relatório
dentro da própria especialidade) continuam liberados para qualquer
profissional cadastrado através de `document-templates` — são texto livre
que o próprio profissional redige, já limitado pelo cadastro verificado de
conselho (KYC), e cada conselho listado acima tem previsão legal de emitir
esse tipo de documento dentro da própria área (fisioterapeuta: Lei
13.716/2018; psicólogo, assistente social etc.: resolução do respectivo
conselho). O gate desta sessão fica só em cima de receituário de
medicamento, que é onde a lei realmente diferencia por profissão de forma
verificável.

**Material ao paciente é isento deste gate por completo** — decisão do
Rafael em 06/08/2026 ("libere a emissao de todo o conteudo para todas as
profissoes, por ser somente material informativo"): é conteúdo educativo,
não prescrição nem documento com efeito legal individualizado.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.cmed import CmedApresentacao

ESCOPO_COMPLETO = "completo"
ESCOPO_RESTRITO_ODONTO = "restrito_odonto"
ESCOPO_APENAS_ISENTOS = "apenas_isentos"

LISTA_VEDADA_ODONTO = "C4"
TARJA_ISENTA = "Tarja Sem Tarja"

_ESCOPO_POR_CONSELHO = {
    "CRM": ESCOPO_COMPLETO,
    "CRO": ESCOPO_RESTRITO_ODONTO,
}
# Qualquer conselho RECONHECIDO fora do dicionário acima (COREN, CRF, CRN,
# CREFITO, CRP, CREF, CRESS, CRBM, OUTRO) recebe o escopo mais restrito —
# fail closed, nunca o inverso. `council_name` em branco/`None` é tratado
# como CRM (escopo completo), não como o mais restrito: o cadastro já
# bloqueia o primeiro acesso à plataforma sem `profession`/`council_name`/
# `council_number`/`council_state` preenchidos (`_perfil_profissional_
# completo()` em `app/api/auth.py`) — na prática nenhum assinante chega ao
# receituário com o campo vazio, e a Corvia era uma plataforma só de
# médicos até esta ampliação (06/08/2026), então em branco é literalmente
# o histórico real da base, não uma suposição otimista nova.


def escopo_de(council_name: str | None) -> str:
    conselho = (council_name or "").strip().upper()
    if not conselho:
        return ESCOPO_COMPLETO
    return _ESCOPO_POR_CONSELHO.get(conselho, ESCOPO_APENAS_ISENTOS)


def eh_isento_de_prescricao(db: Session, drug_id: int | None) -> bool:
    """Só considera isento quando existir ao menos um casamento com a CMED
    e TODAS as apresentações casadas estiverem marcadas 'Tarja Sem Tarja'.
    Substância sem casamento na CMED (drug_id nulo, ou nenhuma linha
    casada) conta como NÃO isento — mesma regra de sempre deste projeto:
    dependência externa não confirmada é tratada como indisponível, nunca
    como favorável à liberação."""
    if drug_id is None:
        return False
    tarjas = [
        t for (t,) in db.query(CmedApresentacao.tarja)
        .filter(CmedApresentacao.drug_id == drug_id).all()
    ]
    if not tarjas:
        return False
    return all((t or "").strip() == TARJA_ISENTA for t in tarjas)


@dataclass
class ItemAvaliado:
    permitido: bool
    motivo: str | None = None


def avaliar_item(db: Session, escopo: str, lista: str | None, drug_id: int | None) -> ItemAvaliado:
    if escopo == ESCOPO_COMPLETO:
        return ItemAvaliado(True)
    if escopo == ESCOPO_RESTRITO_ODONTO:
        if lista == LISTA_VEDADA_ODONTO:
            return ItemAvaliado(
                False,
                "Lista C4 (retinoides sistêmicos) está fora do escopo de "
                "prescrição do cirurgião-dentista (Lei 5.081/1966, art. 6º).",
            )
        return ItemAvaliado(True)
    # ESCOPO_APENAS_ISENTOS
    if eh_isento_de_prescricao(db, drug_id):
        return ItemAvaliado(True)
    return ItemAvaliado(
        False,
        "Este item exige prescrição médica ou pertence a lista controlada "
        "da Portaria 344/98 — fora do escopo de prescrição desta profissão "
        "na Corvia hoje. Apenas medicamentos isentos de prescrição estão "
        "liberados para este cadastro.",
    )
