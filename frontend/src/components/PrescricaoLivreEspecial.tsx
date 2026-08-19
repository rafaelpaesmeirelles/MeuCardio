import { useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../lib/api";

type Capacidades = {
  enabled: boolean;
  allows_self: boolean;
  rafael_signer: boolean;
  profile: string | null;
};

type Provedor = {
  codigo: string;
  nome: string;
  nivel: string;
  disponivel: boolean;
  motivo: string | null;
};

type PrescricaoEspecial = {
  id: number;
  patient_name: string | null;
  body: string;
  mode: "propria" | "rafael";
  status: string;
  originator_id: number;
  originator_name: string | null;
  signer_id: number;
  signer_name: string | null;
  review_note: string | null;
  created_at: string;
  signed_at: string | null;
  signed: boolean;
  method: string | null;
  awaiting_external_signature: boolean;
};

const STATUS: Record<string, string> = {
  pronta_assinatura: "Pronta para assinatura",
  pendente_assinatura: "Aguardando Dr. Rafael",
  aprovada: "Aprovada para assinatura",
  devolvida: "Devolvida para correção",
  recusada: "Recusada",
  aguardando_assinatura_externa: "Aguardando PDF assinado",
  assinado: "Assinada",
};

function abrirBlob(blob: Blob, imprimir = false) {
  const url = URL.createObjectURL(blob);
  if (imprimir) {
    const janela = window.open(url, "_blank", "noopener,noreferrer");
    if (janela) setTimeout(() => janela.print(), 800);
  } else {
    const a = document.createElement("a");
    a.href = url;
    a.download = "receituario.pdf";
    a.click();
  }
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

export default function PrescricaoLivreEspecial() {
  const [cap, setCap] = useState<Capacidades | null>(null);
  const [provedores, setProvedores] = useState<Provedor[]>([]);
  const [minhas, setMinhas] = useState<PrescricaoEspecial[]>([]);
  const [fila, setFila] = useState<PrescricaoEspecial[]>([]);
  const [paciente, setPaciente] = useState("");
  const [texto, setTexto] = useState("");
  const [modo, setModo] = useState<"propria" | "rafael">("rafael");
  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [metodos, setMetodos] = useState<Record<number, string>>({});
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  async function recarregar() {
    const capacidades = await api.get<Capacidades>("/prescricao-especial/capacidades");
    setCap(capacidades);
    if (capacidades.enabled) {
      const itens = await api.get<PrescricaoEspecial[]>("/prescricao-especial/minhas");
      setMinhas(itens);
    }
    if (capacidades.rafael_signer) {
      const pendentes = await api.get<PrescricaoEspecial[]>("/prescricao-especial/pendentes");
      setFila(pendentes);
    }
  }

  useEffect(() => {
    Promise.all([
      recarregar(),
      api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => setProvedores([])),
    ]).catch(() => setCap({ enabled: false, allows_self: false, rafael_signer: false, profile: null }));
  }, []);

  useEffect(() => {
    if (cap?.enabled && !cap.allows_self) setModo("rafael");
  }, [cap]);

  const provedoresDisponiveis = useMemo(() => provedores.filter((p) => p.disponivel), [provedores]);

  function metodoDe(id: number, delegada: boolean) {
    const elegiveis = delegada
      ? provedoresDisponiveis.filter((p) => p.nivel === "qualificada" && p.codigo !== "MANUAL")
      : provedoresDisponiveis;
    return metodos[id] || elegiveis.find((p) => p.codigo === "A1_ARQUIVO")?.codigo || elegiveis[0]?.codigo || "A1_ARQUIVO";
  }

  async function salvar() {
    if (!paciente.trim() || !texto.trim()) return;
    setCarregando(true);
    setErro("");
    try {
      if (editandoId) {
        await api.put(`/prescricao-especial/${editandoId}`, {
          patient_name: paciente.trim(),
          body: texto.trim(),
        });
      } else {
        await api.post("/prescricao-especial", {
          patient_name: paciente.trim(),
          body: texto.trim(),
          mode: modo,
        });
      }
      setPaciente("");
      setTexto("");
      setEditandoId(null);
      await recarregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível salvar a prescrição.");
    } finally {
      setCarregando(false);
    }
  }

  async function decidir(item: PrescricaoEspecial, action: "aprovar" | "devolver" | "recusar") {
    const precisaMotivo = action !== "aprovar";
    const note = precisaMotivo ? window.prompt(action === "devolver" ? "Motivo/orientação para correção:" : "Motivo da recusa:") : null;
    if (precisaMotivo && !note?.trim()) return;
    setErro("");
    try {
      await api.post(`/prescricao-especial/${item.id}/decisao`, { action, note });
      await recarregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível atualizar a solicitação.");
    }
  }

  async function emitir(item: PrescricaoEspecial) {
    const metodo = metodoDe(item.id, item.mode === "rafael");
    setErro("");
    try {
      const blob = await api.blobPost(`/prescricao-especial/${item.id}/emitir`, {
        metodo,
        endereco: "profissional",
      });
      abrirBlob(blob, false);
      await recarregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível emitir/assinar a receita.");
    }
  }

  async function concluirExterna(item: PrescricaoEspecial, arquivo: File | null) {
    if (!arquivo) return;
    setErro("");
    try {
      await api.upload(`/prescricao-especial/${item.id}/assinatura-externa`, "arquivo", arquivo);
      await recarregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível validar o PDF assinado.");
    }
  }

  async function pdf(item: PrescricaoEspecial, imprimir: boolean) {
    setErro("");
    try {
      const blob = await api.blob(`/prescricao-especial/${item.id}/pdf`);
      abrirBlob(blob, imprimir);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível abrir a receita assinada.");
    }
  }

  async function enviarEmail(item: PrescricaoEspecial) {
    const email = window.prompt("E-mail do destinatário:");
    if (!email?.trim()) return;
    setErro("");
    try {
      const r = await api.post<{ enviado: boolean; link: string | null; erro: string | null }>(
        `/prescricao-especial/${item.id}/enviar-email`,
        { email: email.trim() },
      );
      if (!r.enviado && r.link) window.prompt("O envio automático não foi possível. Copie o link seguro:", r.link);
      await recarregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar a receita.");
    }
  }

  if (!cap || (!cap.enabled && !cap.rafael_signer)) return null;

  return (
    <div className="cartao" style={{ marginBottom: "1rem", border: "1px solid var(--borda)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "0.8rem", alignItems: "baseline", flexWrap: "wrap" }}>
        <div>
          <p className="eyebrow" style={{ margin: 0 }}>Prescrição livre</p>
          <strong>Digitação manual e assinatura controlada</strong>
        </div>
        {cap.enabled && !cap.allows_self && (
          <span className="eyebrow" style={{ margin: 0 }}>Emissão somente pelo Dr. Rafael</span>
        )}
      </div>

      {erro && <p role="alert" style={{ color: "var(--alerta)", marginTop: "0.6rem" }}>{erro}</p>}

      {cap.enabled && (
        <div style={{ marginTop: "0.8rem" }}>
          <label>Paciente</label>
          <input value={paciente} onChange={(e) => setPaciente(e.target.value)} placeholder="Nome do paciente" />
          <label style={{ marginTop: "0.5rem" }}>Prescrição livre</label>
          <textarea
            rows={8}
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Digite livremente a prescrição, posologia e orientações…"
          />

          {!editandoId && cap.allows_self && (
            <div style={{ marginTop: "0.6rem" }}>
              <label>Quem emitirá esta receita?</label>
              <select value={modo} onChange={(e) => setModo(e.target.value as "propria" | "rafael")}>
                <option value="propria">Emitir com minhas credenciais/assinatura</option>
                <option value="rafael">Enviar ao Dr. Rafael para assinatura</option>
              </select>
            </div>
          )}

          <button className="botao" style={{ marginTop: "0.7rem" }} onClick={salvar} disabled={carregando || !paciente.trim() || !texto.trim()}>
            {carregando ? "Salvando…" : editandoId ? "Enviar correção ao Dr. Rafael" : modo === "rafael" ? "Enviar ao Dr. Rafael" : "Criar para emissão"}
          </button>
          {editandoId && (
            <button className="botao botao--secundario" style={{ margin: "0.7rem 0 0 0.5rem" }} onClick={() => { setEditandoId(null); setPaciente(""); setTexto(""); }}>
              Cancelar correção
            </button>
          )}
        </div>
      )}

      {cap.enabled && minhas.length > 0 && (
        <div style={{ marginTop: "1rem" }}>
          <p className="eyebrow">Minhas prescrições livres</p>
          {minhas.map((item) => {
            const delegada = item.mode === "rafael";
            const podeAssinar = !delegada && item.status === "pronta_assinatura";
            const metodosPermitidos = delegada
              ? provedoresDisponiveis.filter((p) => p.nivel === "qualificada" && p.codigo !== "MANUAL")
              : provedoresDisponiveis;
            return (
              <div key={item.id} className="cartao" style={{ marginTop: "0.5rem", padding: "0.7rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem", flexWrap: "wrap" }}>
                  <strong>{item.patient_name}</strong>
                  <span className="eyebrow" style={{ margin: 0 }}>{STATUS[item.status] ?? item.status}</span>
                </div>
                <p style={{ whiteSpace: "pre-wrap", fontSize: "0.86rem", margin: "0.45rem 0" }}>{item.body}</p>
                {item.review_note && <p style={{ color: "var(--alerta)", fontSize: "0.84rem" }}>Observação: {item.review_note}</p>}

                {item.status === "devolvida" && (
                  <button className="botao botao--secundario" onClick={() => { setEditandoId(item.id); setPaciente(item.patient_name ?? ""); setTexto(item.body); }}>
                    Corrigir prescrição
                  </button>
                )}

                {podeAssinar && (
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
                    <select value={metodoDe(item.id, false)} onChange={(e) => setMetodos({ ...metodos, [item.id]: e.target.value })}>
                      {metodosPermitidos.map((p) => <option key={p.codigo} value={p.codigo}>{p.nome}</option>)}
                    </select>
                    <button className="botao" onClick={() => emitir(item)}>Emitir/assinar</button>
                  </div>
                )}

                {item.awaiting_external_signature && (
                  <label className="botao botao--secundario" style={{ display: "inline-block", marginTop: "0.4rem", cursor: "pointer" }}>
                    Enviar PDF assinado
                    <input type="file" accept="application/pdf" style={{ display: "none" }} onChange={(e) => concluirExterna(item, e.target.files?.[0] ?? null)} />
                  </label>
                )}

                {item.signed && (
                  <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap", marginTop: "0.4rem" }}>
                    <button className="botao botao--secundario" onClick={() => pdf(item, false)}>Download</button>
                    <button className="botao botao--secundario" onClick={() => pdf(item, true)}>Imprimir</button>
                    <button className="botao botao--secundario" onClick={() => enviarEmail(item)}>Enviar por e-mail</button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {cap.rafael_signer && fila.length > 0 && (
        <div style={{ marginTop: "1rem" }}>
          <p className="eyebrow">Aguardando sua assinatura</p>
          {fila.map((item) => {
            const metodosPermitidos = provedoresDisponiveis.filter((p) => p.nivel === "qualificada" && p.codigo !== "MANUAL");
            return (
              <div key={item.id} className="cartao" style={{ marginTop: "0.5rem", padding: "0.7rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem", flexWrap: "wrap" }}>
                  <strong>{item.patient_name} · preparado por {item.originator_name}</strong>
                  <span className="eyebrow" style={{ margin: 0 }}>{STATUS[item.status] ?? item.status}</span>
                </div>
                <p style={{ whiteSpace: "pre-wrap", fontSize: "0.88rem", margin: "0.55rem 0" }}>{item.body}</p>

                {item.status === "pendente_assinatura" && (
                  <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                    <button className="botao" onClick={() => decidir(item, "aprovar")}>Aprovar</button>
                    <button className="botao botao--secundario" onClick={() => decidir(item, "devolver")}>Devolver para correção</button>
                    <button className="botao botao--secundario" onClick={() => decidir(item, "recusar")}>Recusar</button>
                  </div>
                )}

                {item.status === "aprovada" && (
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
                    <select value={metodoDe(item.id, true)} onChange={(e) => setMetodos({ ...metodos, [item.id]: e.target.value })}>
                      {metodosPermitidos.map((p) => <option key={p.codigo} value={p.codigo}>{p.nome}</option>)}
                    </select>
                    <button className="botao" disabled={metodosPermitidos.length === 0} onClick={() => emitir(item)}>Assinar receita</button>
                  </div>
                )}

                {item.awaiting_external_signature && (
                  <label className="botao botao--secundario" style={{ display: "inline-block", marginTop: "0.4rem", cursor: "pointer" }}>
                    Enviar PDF assinado pelo Assinador ITI
                    <input type="file" accept="application/pdf" style={{ display: "none" }} onChange={(e) => concluirExterna(item, e.target.files?.[0] ?? null)} />
                  </label>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
