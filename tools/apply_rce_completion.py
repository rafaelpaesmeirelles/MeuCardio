#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    content = read(path)
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: esperado 1 trecho, encontrado {count}: {old[:100]!r}")
    write(path, content.replace(old, new, 1))


def regex_once(path: str, pattern: str, replacement: str) -> None:
    content = read(path)
    updated, count = re.subn(pattern, replacement, content, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{path}: padrão não encontrado: {pattern[:120]}")
    write(path, updated)


# ---------------------------------------------------------------------------
# Seed dos tipos: a RCE física não usa numeração SNCR; o SNCR continua sendo
# requisito para emissão/registro eletrônico e para notificações numeradas.
# ---------------------------------------------------------------------------
replace_once(
    "backend/app/services/carregar_controlados.py",
    '''    # "em duas vias" está no subtítulo da própria lista C1 e C5 — conferido.
    dict(codigo="RCE", nome="Receita de Controle Especial", cor="branca", vias=2,
         exige_numeracao_sncr=True, endpoint_sncr="/numeracoes/receita-especial-retencao",
         lote_min=1000, lote_max=1000, exige_retencao=True, ativo=False),
''',
    '''    # Modelo físico Anvisa V2, vigente e obrigatório desde 18/05/2026.
    # Não contém numeração SNCR. A saída é manual/impressa em duas vias;
    # emissão eletrônica permanece bloqueada até a integração oficial.
    dict(codigo="RCE", nome="Receita de Controle Especial", cor="branca", vias=2,
         destinacao_vias=["1ª via - Retenção pela Farmácia", "2ª via - Paciente"],
         validade_dias=30, exige_numeracao_sncr=False, endpoint_sncr=None,
         lote_min=None, lote_max=None, exige_retencao=True,
         campos_obrigatorios=["emitente", "paciente_nome", "paciente_documento",
                              "prescricao", "data", "assinatura"], ativo=True),
''',
)

# ---------------------------------------------------------------------------
# API do receituário: CID persistido, RCE física e C5 fail-closed.
# ---------------------------------------------------------------------------
replace_once(
    "backend/app/api/receituario.py",
    '''class ReceituarioIn(BaseModel):
    patient_id: int | None = None
    destinatario: DestinatarioIn
    itens: list[ItemIn] = Field(min_length=1)
    observacoes: str = ""
''',
    '''class ReceituarioIn(BaseModel):
    patient_id: int | None = None
    destinatario: DestinatarioIn
    itens: list[ItemIn] = Field(min_length=1)
    observacoes: str = ""
    cid: str | None = Field(default=None, max_length=10)
''',
)

replace_once(
    "backend/app/api/receituario.py",
    '''        "motivo_correcao": doc.motivo_correcao,
        "fonte_versao_listas": doc.fonte_versao_listas,
    }
''',
    '''        "motivo_correcao": doc.motivo_correcao,
        "fonte_versao_listas": doc.fonte_versao_listas,
        "cid": doc.cid,
    }
''',
)

replace_once(
    "backend/app/api/receituario.py",
    '''            pendencias=plano.pendencias, fonte_versao_listas=versao,
        )
''',
    '''            pendencias=plano.pendencias, fonte_versao_listas=versao,
            cid=(dados.cid or "").strip() or None,
        )
''',
)

EMITIR = r'''@router\.post\("/documentos/\{documento_id\}/emitir"\)\ndef emitir\(.*?\n\n\nclass EnviarEmailIn'''
NOVO_EMITIR = '''@router.post("/documentos/{documento_id}/emitir")
def emitir(documento_id: int, dados: EmitirIn = EmitirIn(), db: Session = Depends(get_db),
          user=Depends(current_user)):
    """Emite receituário comum ou RCE física; demais tipos continuam fail-closed.

    A Receita de Controle Especial usa o modelo físico Anvisa V2 e somente o
    método MANUAL, para impressão e assinatura de próprio punho. Notificações
    A/B/B2, retinoides e talidomida permanecem bloqueadas sem numeração oficial.
    """
    doc = db.get(PrescriptionDocument, documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(
            status_code=422,
            detail="endereco precisa ser 'residencial', 'profissional' ou omitido.",
        )

    try:
        provedor, info_metodo = assinatura_emissao.preparar(dados.metodo)
    except assinatura_emissao.MetodoInvalido as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    tipo = _tipos(db).get(doc.tipo_codigo)
    bloqueios: list[str] = []
    if doc.status != "revisado":
        bloqueios.append("O documento precisa ser revisado antes de emitido.")
    if not tipo:
        bloqueios.append(f"Tipo de receita desconhecido: {doc.tipo_codigo}.")
    elif not tipo.ativo:
        bloqueios.append(
            f"O tipo {doc.tipo_codigo} permanece indisponível sem numeração oficial "
            "ou integração SNCR aplicável; nenhum número será simulado."
        )
    if tipo and tipo.exige_numeracao_sncr and not doc.numeracao:
        bloqueios.append(
            "Este tipo exige numeração oficial do SNCR/Vigilância Sanitária; "
            "nenhuma numeração foi atribuída ao documento."
        )
    if doc.tipo_codigo not in {"COMUM", "RCE"}:
        bloqueios.append(
            "A geração deste modelo numerado só será liberada após integração "
            "oficial e validação do número atribuído ao prescritor."
        )
    if doc.tipo_codigo == "RCE" and dados.metodo != "MANUAL":
        bloqueios.append(
            "A RCE disponível nesta etapa é o modelo físico para impressão e "
            "assinatura manual. A emissão eletrônica aguarda o SNCR."
        )

    disponivel, motivo_indisponivel = provedor.disponivel()
    if not disponivel:
        bloqueios.append(motivo_indisponivel)

    from app.services.pdf_documento import receituario_comum, resolver_endereco

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    destinatario = {"nome": "", "endereco": "", "documento": ""}
    if dest:
        destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
        if dest.endereco_cifrado:
            destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)
        if dest.documento_cifrado:
            destinatario["documento"] = cofre.decifrar_campo(dest.documento_cifrado, presc.id)

    endereco_medico = resolver_endereco(
        user, "profissional" if doc.tipo_codigo == "RCE" else dados.endereco
    )
    medico = document_identity(user)
    data_emissao = datetime.now(timezone.utc)

    if doc.tipo_codigo == "RCE":
        from app.services.receita_controle_especial import (
            MODELO_VERSAO, receita_controle_especial, validar_requisitos_rce,
        )
        medico_rce = dict(medico)
        medico_rce["cpf"] = user.cpf
        requisitos = validar_requisitos_rce(
            medico=medico_rce, destinatario=destinatario, itens=doc.itens,
            endereco_profissional=endereco_medico, cid=doc.cid,
        )
        bloqueios.extend(requisitos)
    else:
        MODELO_VERSAO = "CORVIA-RECEITUARIO-COMUM"
        medico_rce = medico

    if bloqueios:
        raise HTTPException(status_code=409, detail={
            "erro": "Emissão indisponível.",
            "bloqueios": list(dict.fromkeys(bloqueios)),
            "nada_foi_simulado": True,
        })

    if doc.tipo_codigo == "RCE":
        try:
            pdf_visual = receita_controle_especial(
                destinatario=destinatario, itens=doc.itens,
                observacoes=presc.notes or "", medico=medico_rce,
                endereco_profissional=endereco_medico,
                data_emissao=data_emissao, cid=doc.cid,
            )
        except ValueError as e:
            raise HTTPException(status_code=409, detail={
                "erro": "RCE incompleta.", "bloqueios": str(e).split(" | "),
                "nada_foi_simulado": True,
            }) from e
    else:
        pdf_visual = receituario_comum(
            destinatario=destinatario, itens=doc.itens,
            observacoes=presc.notes or "", medico=medico,
            endereco=endereco_medico, data_emissao=data_emissao,
            metodo_assinatura=dados.metodo, provedor_nome=info_metodo.nome,
        )

    emitido = assinatura_emissao.assinar_e_persistir(
        db, tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc.id,
        metodo=dados.metodo, provedor=provedor, info=info_metodo,
        pdf_visual=pdf_visual, medico=medico_rce,
        criado_por=user.id, data_emissao=data_emissao,
    )

    doc.status = "emitido"
    doc.emitido_em = data_emissao
    doc.endereco_exibido = "profissional" if doc.tipo_codigo == "RCE" else (
        dados.endereco if endereco_medico else None
    )
    db.add(AuditLog(
        user_id=user.id, action="emitir_documento_receita",
        entity="prescription_document", entity_id=str(doc.id),
        detail={
            "tipo": doc.tipo_codigo, "bytes": len(emitido.pdf),
            "metodo": dados.metodo, "sha256": emitido.registro.sha256,
            "modelo": MODELO_VERSAO,
            "lista_c5": any(str(i.get("lista") or "").upper() == "C5" for i in doc.itens),
        },
    ))
    db.commit()
    nome_arquivo = (
        f"receita-controle-especial-{doc.id}.pdf"
        if doc.tipo_codigo == "RCE" else f"receituario-{doc.id}.pdf"
    )
    return Response(content=emitido.pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'inline; filename="{nome_arquivo}"',
    })


class EnviarEmailIn'''
regex_once("backend/app/api/receituario.py", EMITIR, NOVO_EMITIR)

# ---------------------------------------------------------------------------
# Frontend: campo CID, requisitos C5 e mensagens coerentes com o modelo físico.
# ---------------------------------------------------------------------------
replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''  fonte_versao_listas: string | null;
};
''',
    '''  fonte_versao_listas: string | null; cid: string | null;
};
''',
)

replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''  const [documento, setDocumento] = useState("");
  const [observacoes, setObservacoes] = useState("");
''',
    '''  const [documento, setDocumento] = useState("");
  const [cid, setCid] = useState("");
  const [observacoes, setObservacoes] = useState("");
''',
)

replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''    observacoes,
  };
''',
    '''    observacoes,
    cid: cid.trim() || undefined,
  };
''',
)

replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''    setDocumento(d.destinatario.documento ?? "");
    setObservacoes(d.observacoes ?? "");
''',
    '''    setDocumento(d.destinatario.documento ?? "");
    setCid(d.documentos.find((doc) => doc.cid)?.cid ?? "");
    setObservacoes(d.observacoes ?? "");
''',
)

replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''          <label style={{ marginTop: "0.5rem" }}>Documento — RG/CPF (opcional)</label>
          <input value={documento} onChange={(e) => setDocumento(e.target.value)} />

          <p className="eyebrow" style={{ margin: "1rem 0 0" }}>Itens da receita</p>
''',
    '''          <label style={{ marginTop: "0.5rem" }}>CPF ou passaporte do paciente</label>
          <input value={documento} onChange={(e) => setDocumento(e.target.value)} />
          <label style={{ marginTop: "0.5rem" }}>CID (obrigatório para anabolizantes/Lista C5)</label>
          <input value={cid} onChange={(e) => setCid(e.target.value.toUpperCase())}
                 placeholder="Ex.: E29.1" maxLength={10} />
          <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
            Para Lista C5, também são obrigatórios endereço do paciente, CPF do prescritor,
            endereço e telefone profissionais. A emissão é restrita a CRM ou CRO.
          </p>

          <p className="eyebrow" style={{ margin: "1rem 0 0" }}>Itens da receita</p>
''',
)

replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);

  async function revisar() {
''',
    '''  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);
  const temC5 = doc.itens.some((item) => String(item.lista ?? "").toUpperCase() === "C5");

  async function revisar() {
''',
)

replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''      {!doc.tipo_ativo && (
        <p style={{ fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Este tipo depende da integração com o SNCR (Anvisa, previsto até 30/09/2026) e do layout
          oficial ainda não reproduzido — ainda não pode ser emitido. A assinatura digital (manual)
          já funciona para qualquer tipo, não é mais o que falta aqui.
        </p>
      )}
''',
    '''      {!doc.tipo_ativo && (
        <p style={{ fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Este modelo exige numeração oficial ou integração SNCR. O sistema não simula número,
          talonário ou autorização; a emissão permanece bloqueada até o requisito existir.
        </p>
      )}
      {doc.tipo === "RCE" && (
        <p style={{ fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Modelo físico Anvisa V2: serão geradas duas vias, cada uma com frente e verso,
          para impressão e assinatura manual.
        </p>
      )}
      {temC5 && (
        <p style={{ color: "var(--alerta)", fontSize: "0.84rem", marginTop: "0.4rem" }}>
          Lista C5: emissão somente por CRM/CRO e com CPF do prescritor, endereço e telefone
          profissionais, endereço do paciente e CID preenchidos.
        </p>
      )}
''',
)

replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''          <label>Endereço no cabeçalho/rodapé (opcional)</label>
          <select value={endereco} onChange={(e) => setEndereco(e.target.value as typeof endereco)}>
            <option value="">Nenhum</option>
            <option value="profissional">Profissional (consultório)</option>
            <option value="residencial">Residencial</option>
          </select>
          <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
            Preencha em Minha Conta antes, se ainda não tiver cadastrado.
          </p>
''',
    '''          {doc.tipo === "RCE" ? (
            <p className="eyebrow" style={{ margin: "0.3rem 0" }}>
              A RCE usa automaticamente o endereço profissional cadastrado. Para Lista C5,
              endereço e telefone profissionais são obrigatórios.
            </p>
          ) : (
            <>
              <label>Endereço no cabeçalho/rodapé (opcional)</label>
              <select value={endereco} onChange={(e) => setEndereco(e.target.value as typeof endereco)}>
                <option value="">Nenhum</option>
                <option value="profissional">Profissional (consultório)</option>
                <option value="residencial">Residencial</option>
              </select>
              <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
                Preencha em Minha Conta antes, se ainda não tiver cadastrado.
              </p>
            </>
          )}
''',
)

replace_once(
    "frontend/src/pages/Receituario.tsx",
    '''                  onClick={() => { setCriado(null); setItens([{ ...ITEM_VAZIO }]); setBuscaFarmaco([""]); setNome(""); setPrevia(null); }}>
''',
    '''                  onClick={() => { setCriado(null); setItens([{ ...ITEM_VAZIO }]); setBuscaFarmaco([""]); setNome(""); setEndereco(""); setDocumento(""); setCid(""); setPrevia(null); }}>
''',
)

# Atualiza documentação de escopo para refletir o comportamento implementado.
with (ROOT / "docs/especificacao-perfil-documentos-prescricoes.md").open("a", encoding="utf-8") as f:
    f.write('''\n\n## Estado de implementação regulatória — 04/08/2026\n\n- RCE física no modelo Anvisa V2: implementada em duas vias, frente e verso.\n- Lista C5: validação obrigatória de CRM/CRO, CPF do prescritor, endereço e telefone profissionais, endereço do paciente e CID.\n- NRA, NRB, NRB2, NRR, NRT e RET: permanecem fail-closed sem numeração oficial/integração aplicável; nenhum número é simulado.\n- Emissão RCE disponível somente como documento físico com assinatura manual enquanto as funcionalidades eletrônicas do SNCR não estiverem integradas.\n''')

(ROOT / "tools/apply_rce_completion.py").unlink(missing_ok=True)
print("RCE, Lista C5 e frontend regulatório aplicados.")
