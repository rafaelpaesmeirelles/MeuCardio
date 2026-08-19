import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";

type Cap = { enabled: boolean; allows_self: boolean; rafael_signer: boolean };
type Prov = { codigo: string; nome: string; nivel: string; disponivel: boolean };
type Rx = {
  id: number; patient_name: string | null; body: string; mode: "propria" | "rafael";
  status: string; originator_name: string | null; review_note: string | null;
  signed: boolean; awaiting_external_signature: boolean;
};
const ROT: Record<string, string> = {
  pronta_assinatura: "Pronta para assinatura", pendente_assinatura: "Aguardando Dr. Rafael",
  aprovada: "Aprovada", devolvida: "Devolvida", recusada: "Recusada",
  aguardando_assinatura_externa: "Aguardando PDF assinado", assinado: "Assinada",
};
function abrir(b: Blob, imprimir = false) {
  const u = URL.createObjectURL(b);
  if (imprimir) window.open(u, "_blank", "noopener,noreferrer");
  else { const a = document.createElement("a"); a.href = u; a.download = "receituario.pdf"; a.click(); }
  setTimeout(() => URL.revokeObjectURL(u), 5000);
}

export default function PrescricaoLivreEspecial() {
  const [cap, setCap] = useState<Cap>();
  const [prov, setProv] = useState<Prov[]>([]);
  const [mine, setMine] = useState<Rx[]>([]);
  const [fila, setFila] = useState<Rx[]>([]);
  const [pac, setPac] = useState(""); const [body, setBody] = useState("");
  const [mode, setMode] = useState<"propria" | "rafael">("rafael");
  const [edit, setEdit] = useState<number>(); const [metodo, setMetodo] = useState<Record<number, string>>({});
  const [erro, setErro] = useState("");

  async function load() {
    const c = await api.get<Cap>("/prescricao-especial/capacidades"); setCap(c);
    if (c.enabled) setMine(await api.get<Rx[]>("/prescricao-especial/minhas"));
    if (c.rafael_signer) setFila(await api.get<Rx[]>("/prescricao-especial/pendentes"));
  }
  useEffect(() => { load().catch(() => setCap({ enabled: false, allows_self: false, rafael_signer: false })); api.get<Prov[]>("/assinatura/provedores").then(setProv).catch(() => {}); }, []);
  useEffect(() => { if (cap?.enabled && !cap.allows_self) setMode("rafael"); }, [cap]);
  const disponiveis = prov.filter(p => p.disponivel);
  const metodoRx = (r: Rx) => metodo[r.id] || disponiveis.find(p => p.codigo === "A1_ARQUIVO" && (r.mode !== "rafael" || p.nivel === "qualificada"))?.codigo || disponiveis.find(p => r.mode !== "rafael" || p.nivel === "qualificada")?.codigo || "A1_ARQUIVO";
  const falha = (e: unknown) => setErro(e instanceof ApiError ? e.message : "Não foi possível concluir.");

  async function salvar() {
    setErro(""); try {
      const payload = { patient_name: pac.trim(), body: body.trim() };
      if (edit) await api.put(`/prescricao-especial/${edit}`, payload);
      else await api.post("/prescricao-especial", { ...payload, mode });
      setPac(""); setBody(""); setEdit(undefined); await load();
    } catch (e) { falha(e); }
  }
  async function decisao(r: Rx, action: "aprovar" | "devolver" | "recusar") {
    const note = action === "aprovar" ? null : prompt(action === "devolver" ? "Orientação para correção:" : "Motivo da recusa:");
    if (action !== "aprovar" && !note?.trim()) return;
    try { await api.post(`/prescricao-especial/${r.id}/decisao`, { action, note }); await load(); } catch (e) { falha(e); }
  }
  async function emitir(r: Rx) {
    try { abrir(await api.blobPost(`/prescricao-especial/${r.id}/emitir`, { metodo: metodoRx(r), endereco: "profissional" })); await load(); } catch (e) { falha(e); }
  }
  async function externa(r: Rx, f?: File) { if (f) try { await api.upload(`/prescricao-especial/${r.id}/assinatura-externa`, "arquivo", f); await load(); } catch (e) { falha(e); } }
  async function pdf(r: Rx, print = false) { try { abrir(await api.blob(`/prescricao-especial/${r.id}/pdf`), print); } catch (e) { falha(e); } }
  async function email(r: Rx) {
    const to = prompt("E-mail do destinatário:"); if (!to?.trim()) return;
    try { const x = await api.post<{ enviado: boolean; link: string | null }>(`/prescricao-especial/${r.id}/enviar-email`, { email: to.trim() }); if (!x.enviado && x.link) prompt("Copie o link seguro:", x.link); } catch (e) { falha(e); }
  }

  if (!cap || (!cap.enabled && !cap.rafael_signer)) return null;
  const seletor = (r: Rx) => <select value={metodoRx(r)} onChange={e => setMetodo({ ...metodo, [r.id]: e.target.value })}>{disponiveis.filter(p => r.mode !== "rafael" || (p.nivel === "qualificada" && p.codigo !== "MANUAL")).map(p => <option key={p.codigo} value={p.codigo}>{p.nome}</option>)}</select>;
  const card = (r: Rx, filaRafael = false) => <div key={r.id} className="cartao" style={{ marginTop: ".5rem", padding: ".7rem" }}>
    <strong>{r.patient_name}{filaRafael && ` · preparado por ${r.originator_name ?? "usuário"}`}</strong> <span className="eyebrow">{ROT[r.status] ?? r.status}</span>
    <p style={{ whiteSpace: "pre-wrap" }}>{r.body}</p>{r.review_note && <p style={{ color: "var(--alerta)" }}>{r.review_note}</p>}
    {filaRafael && r.status === "pendente_assinatura" && <p><button className="botao" onClick={() => decisao(r, "aprovar")}>Aprovar</button> <button className="botao botao--secundario" onClick={() => decisao(r, "devolver")}>Devolver</button> <button className="botao botao--secundario" onClick={() => decisao(r, "recusar")}>Recusar</button></p>}
    {(r.status === "pronta_assinatura" || (filaRafael && r.status === "aprovada")) && <p>{seletor(r)} <button className="botao" onClick={() => emitir(r)}>Emitir/assinar</button></p>}
    {r.status === "devolvida" && !filaRafael && <button className="botao botao--secundario" onClick={() => { setEdit(r.id); setPac(r.patient_name ?? ""); setBody(r.body); }}>Corrigir</button>}
    {r.awaiting_external_signature && <label className="botao botao--secundario">Enviar PDF assinado <input hidden type="file" accept="application/pdf" onChange={e => externa(r, e.target.files?.[0])} /></label>}
    {r.signed && !filaRafael && <p><button className="botao botao--secundario" onClick={() => pdf(r)}>Download</button> <button className="botao botao--secundario" onClick={() => pdf(r, true)}>Imprimir</button> <button className="botao botao--secundario" onClick={() => email(r)}>E-mail</button></p>}
  </div>;

  return <div className="cartao" style={{ marginBottom: "1rem" }}>
    <p className="eyebrow">Prescrição livre</p>{erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}
    {cap.enabled && <><label>Paciente</label><input value={pac} onChange={e => setPac(e.target.value)} /><label>Prescrição livre</label><textarea rows={8} value={body} onChange={e => setBody(e.target.value)} placeholder="Digite livremente a prescrição, posologia e orientações…" />
      {!edit && cap.allows_self && <><label>Emissão</label><select value={mode} onChange={e => setMode(e.target.value as "propria" | "rafael")}><option value="propria">Minhas credenciais/assinatura</option><option value="rafael">Enviar ao Dr. Rafael</option></select></>}
      {!cap.allows_self && <p className="eyebrow">Emissão somente pelo Dr. Rafael</p>}
      <button className="botao" disabled={!pac.trim() || !body.trim()} onClick={salvar}>{edit ? "Enviar correção" : mode === "rafael" ? "Enviar ao Dr. Rafael" : "Criar para emissão"}</button>
      {mine.length > 0 && <div><p className="eyebrow">Minhas prescrições livres</p>{mine.map(r => card(r))}</div>}</>}
    {cap.rafael_signer && fila.length > 0 && <div><p className="eyebrow">Aguardando sua assinatura</p>{fila.map(r => card(r, true))}</div>}
  </div>;
}
