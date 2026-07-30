import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type ContaEmail = { ativa: boolean; email_address?: string; status?: string };
type Pasta = { folderId?: string; id?: string; folderName?: string; name?: string };
type Mensagem = {
  messageId?: string; id?: string;
  subject?: string; fromAddress?: string; sender?: string;
  receivedTime?: string; date?: string; summary?: string;
};
type MensagemCompleta = Mensagem & { content?: string; htmlContent?: string };

function idDaPasta(p: Pasta): string {
  return p.folderId ?? p.id ?? "";
}
function nomeDaPasta(p: Pasta): string {
  return p.folderName ?? p.name ?? "Pasta";
}
function idDaMensagem(m: Mensagem): string {
  return m.messageId ?? m.id ?? "";
}
function remetente(m: Mensagem): string {
  return m.fromAddress ?? m.sender ?? "—";
}
function dataMensagem(m: Mensagem): string {
  const bruto = m.receivedTime ?? m.date;
  if (!bruto) return "";
  const n = Number(bruto);
  const d = Number.isFinite(n) && bruto.length > 8 ? new Date(n) : new Date(bruto);
  return Number.isNaN(d.getTime()) ? "" : d.toLocaleString("pt-BR");
}

export default function CaixaDeEmail() {
  const [conta, setConta] = useState<ContaEmail | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [ativando, setAtivando] = useState(false);

  const [pastas, setPastas] = useState<Pasta[] | null>(null);
  const [pastaAtual, setPastaAtual] = useState<string | undefined>(undefined);
  const [mensagens, setMensagens] = useState<Mensagem[] | null>(null);
  const [mensagemAberta, setMensagemAberta] = useState<MensagemCompleta | null>(null);
  const [compondo, setCompondo] = useState(false);
  const [novaMsg, setNovaMsg] = useState({ para: "", assunto: "", corpo_html: "" });
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    api.get<ContaEmail>("/email/conta")
      .then(setConta)
      .catch((e: ApiError) => setErro(e.status === 503 ? "Caixa de e-mail ainda não está disponível." : e.message));
  }, []);

  useEffect(() => {
    if (!conta?.ativa) return;
    api.get<Pasta[]>("/email/pastas").then(setPastas).catch(() => setPastas([]));
  }, [conta]);

  useEffect(() => {
    if (!conta?.ativa) return;
    setMensagens(null);
    setMensagemAberta(null);
    const params = pastaAtual ? `?pasta=${encodeURIComponent(pastaAtual)}` : "";
    api.get<Mensagem[]>(`/email/mensagens${params}`).then(setMensagens).catch(() => setMensagens([]));
  }, [conta, pastaAtual]);

  async function ativar() {
    setAtivando(true);
    try {
      const resultado = await api.post<ContaEmail>("/email/conta");
      setConta(resultado);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível ativar a caixa de e-mail.");
    } finally {
      setAtivando(false);
    }
  }

  async function abrirMensagem(m: Mensagem) {
    const id = idDaMensagem(m);
    if (!id) return;
    const completa = await api.get<MensagemCompleta>(`/email/mensagens/${encodeURIComponent(id)}`);
    setMensagemAberta(completa);
  }

  async function enviar() {
    setEnviando(true);
    try {
      await api.post("/email/mensagens", novaMsg);
      setCompondo(false);
      setNovaMsg({ para: "", assunto: "", corpo_html: "" });
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar a mensagem.");
    } finally {
      setEnviando(false);
    }
  }

  if (erro) {
    return (
      <>
        <p className="eyebrow">Caixa de e-mail</p>
        <h1>nome@corvia.med.br</h1>
        <Erro mensagem={erro} />
      </>
    );
  }

  if (conta === null) {
    return (
      <>
        <p className="eyebrow">Caixa de e-mail</p>
        <h1>nome@corvia.med.br</h1>
        <Carregando />
      </>
    );
  }

  if (!conta.ativa) {
    return (
      <>
        <p className="eyebrow">Caixa de e-mail</p>
        <h1>Sua caixa de e-mail própria</h1>
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <p>
            Todo assinante da Corvia tem direito a um endereço de e-mail próprio no
            domínio <strong>@corvia.med.br</strong>, incluído na assinatura — sem
            senha separada, o acesso é o mesmo login de sempre.
          </p>
          <button className="botao" onClick={ativar} disabled={ativando}>
            {ativando ? "Ativando…" : "Ativar minha caixa de e-mail"}
          </button>
        </div>
      </>
    );
  }

  return (
    <>
      <p className="eyebrow">Caixa de e-mail</p>
      <h1>{conta.email_address}</h1>

      <button className="botao" style={{ marginTop: "0.5rem" }} onClick={() => setCompondo(true)}>
        + Escrever
      </button>

      {compondo && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <label>Para</label>
          <input value={novaMsg.para} onChange={(e) => setNovaMsg({ ...novaMsg, para: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Assunto</label>
          <input value={novaMsg.assunto} onChange={(e) => setNovaMsg({ ...novaMsg, assunto: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Mensagem</label>
          <textarea rows={6} value={novaMsg.corpo_html}
                    onChange={(e) => setNovaMsg({ ...novaMsg, corpo_html: e.target.value })} />
          <div style={{ display: "flex", gap: 8, marginTop: "0.6rem" }}>
            <button className="botao" onClick={enviar} disabled={enviando || !novaMsg.para || !novaMsg.assunto}>
              {enviando ? "Enviando…" : "Enviar"}
            </button>
            <button className="botao botao--secundario" onClick={() => setCompondo(false)}>Cancelar</button>
          </div>
        </div>
      )}

      <div className="grade" style={{ gridTemplateColumns: "180px 1fr 1.4fr", gap: "1rem", marginTop: "1rem", alignItems: "start" }}>
        <div className="cartao">
          <p className="eyebrow" style={{ margin: 0 }}>Pastas</p>
          <ul style={{ listStyle: "none", padding: 0, margin: "0.5rem 0 0" }}>
            <li>
              <button className="botao botao--secundario" style={{ width: "100%", textAlign: "left" }}
                      onClick={() => setPastaAtual(undefined)}>
                Entrada
              </button>
            </li>
            {(pastas ?? []).map((p) => (
              <li key={idDaPasta(p)} style={{ marginTop: 4 }}>
                <button className="botao botao--secundario" style={{ width: "100%", textAlign: "left" }}
                        onClick={() => setPastaAtual(idDaPasta(p))}>
                  {nomeDaPasta(p)}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="cartao" style={{ padding: 0, maxHeight: 480, overflowY: "auto" }}>
          {mensagens === null ? (
            <div style={{ padding: "1rem" }}><Carregando /></div>
          ) : mensagens.length === 0 ? (
            <div style={{ padding: "1rem" }}>
              <Vazio titulo="Nenhuma mensagem" />
            </div>
          ) : (
            mensagens.map((m) => (
              <button key={idDaMensagem(m)} onClick={() => abrirMensagem(m)}
                      style={{
                        display: "block", width: "100%", textAlign: "left", padding: "0.6rem 0.8rem",
                        border: "none", borderBottom: "1px solid var(--linha)", background: "transparent", cursor: "pointer",
                      }}>
                <strong style={{ display: "block" }}>{remetente(m)}</strong>
                <span style={{ display: "block" }}>{m.subject ?? "(sem assunto)"}</span>
                <span className="eyebrow" style={{ margin: 0 }}>{dataMensagem(m)}</span>
              </button>
            ))
          )}
        </div>

        <div className="cartao">
          {!mensagemAberta ? (
            <Vazio titulo="Selecione uma mensagem" />
          ) : (
            <>
              <h3 style={{ marginTop: 0 }}>{mensagemAberta.subject ?? "(sem assunto)"}</h3>
              <p className="eyebrow">
                {remetente(mensagemAberta)} · {dataMensagem(mensagemAberta)}
              </p>
              {mensagemAberta.htmlContent ? (
                // eslint-disable-next-line react/no-danger
                <div dangerouslySetInnerHTML={{ __html: mensagemAberta.htmlContent }} />
              ) : (
                <p style={{ whiteSpace: "pre-wrap" }}>{mensagemAberta.content ?? mensagemAberta.summary ?? ""}</p>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}
