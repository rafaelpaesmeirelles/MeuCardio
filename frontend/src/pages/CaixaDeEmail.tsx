import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { apiEmail, ApiEmailError, tokenEmail } from "../lib/apiEmail";
import { Carregando, Erro, Vazio } from "../components/Estado";
import LogoCorviaMail from "../components/LogoCorviaMail";

type Pasta = { folderId?: string; id?: string; folderName?: string; name?: string };
type Mensagem = {
  messageId?: string;
  id?: string;
  subject?: string;
  fromAddress?: string;
  sender?: string;
  receivedTime?: string;
  date?: string;
  summary?: string;
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

function htmlParaTextoSeguro(html: string): string {
  return html
    .replace(
      /<\s*(script|style|head|iframe|object|embed|svg|form)\b[^>]*>[\s\S]*?<\s*\/\s*\1\s*>/gi,
      "",
    )
    .replace(/<\s*br\s*\/?>/gi, "\n")
    .replace(/<\s*li\b[^>]*>/gi, "• ")
    .replace(/<\s*\/(?:p|div|li|tr|h[1-6])\s*>/gi, "\n")
    .replace(/<[^>]*>/g, "")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function corpoSeguro(mensagem: MensagemCompleta): string {
  if (mensagem.content?.trim()) return mensagem.content;
  if (mensagem.summary?.trim()) return mensagem.summary;
  if (mensagem.htmlContent?.trim()) return htmlParaTextoSeguro(mensagem.htmlContent);
  return "";
}

/** Esta caixa é para uso administrativo/profissional geral e não deve receber
 * dado clínico identificável de paciente. */
function RessalvaClinica() {
  return (
    <div
      className="cartao"
      style={{ marginTop: "0.8rem", borderLeft: "3px solid var(--acento)" }}
      role="note"
    >
      <p style={{ margin: 0, fontSize: "0.86rem" }}>
        <strong>Esta caixa é para uso administrativo e profissional geral</strong> — agenda,
        contato com paciente sobre assunto administrativo e avisos do próprio sistema Corvia.
        Ela não tem o mesmo padrão de proteção do Cofre do telediagnóstico. <strong>Não envie
        nome, CPF ou outro dado identificável junto de informação clínica.</strong>
      </p>
    </div>
  );
}

export default function CaixaDeEmail() {
  const navigate = useNavigate();
  const [semSessao, setSemSessao] = useState(!tokenEmail.get());
  const [enderecoAtual, setEnderecoAtual] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const [pastas, setPastas] = useState<Pasta[] | null>(null);
  const [pastaAtual, setPastaAtual] = useState<string | undefined>(undefined);
  const [mensagens, setMensagens] = useState<Mensagem[] | null>(null);
  const [mensagemAberta, setMensagemAberta] = useState<MensagemCompleta | null>(null);
  const [compondo, setCompondo] = useState(false);
  const [novaMsg, setNovaMsg] = useState({ para: "", assunto: "", corpo_html: "" });
  const [enviando, setEnviando] = useState(false);
  const [anexos, setAnexos] = useState<{ file_id: string; nome: string }[]>([]);
  const [enviandoAnexo, setEnviandoAnexo] = useState(false);
  const [excluindo, setExcluindo] = useState(false);

  function sair() {
    tokenEmail.clear();
    navigate("/corvia-mail");
  }

  useEffect(() => {
    if (semSessao) return;
    apiEmail
      .get<{ email_address: string }>("/email/eu")
      .then((r) => setEnderecoAtual(r.email_address))
      .catch((e) => {
        if (e instanceof ApiEmailError && e.status === 401) {
          setSemSessao(true);
          return;
        }
        setErro(e instanceof ApiEmailError ? e.message : "Não foi possível carregar sua caixa de e-mail.");
      });
  }, [semSessao]);

  useEffect(() => {
    if (semSessao || !enderecoAtual) return;
    apiEmail.get<Pasta[]>("/email/pastas").then(setPastas).catch(() => setPastas([]));
  }, [semSessao, enderecoAtual]);

  useEffect(() => {
    if (semSessao || !enderecoAtual) return;
    setMensagens(null);
    setMensagemAberta(null);
    const params = pastaAtual ? `?pasta=${encodeURIComponent(pastaAtual)}` : "";
    apiEmail
      .get<Mensagem[]>(`/email/mensagens${params}`)
      .then(setMensagens)
      .catch(() => setMensagens([]));
  }, [semSessao, enderecoAtual, pastaAtual]);

  async function abrirMensagem(m: Mensagem) {
    const id = idDaMensagem(m);
    if (!id) return;
    const completa = await apiEmail.get<MensagemCompleta>(
      `/email/mensagens/${encodeURIComponent(id)}`,
    );
    setMensagemAberta(completa);
  }

  async function excluirMensagemAberta() {
    const id = mensagemAberta ? idDaMensagem(mensagemAberta) : "";
    if (!id || !window.confirm("Excluir esta mensagem?")) return;
    setExcluindo(true);
    try {
      await apiEmail.delete(`/email/mensagens/${encodeURIComponent(id)}`);
      setMensagens((lista) => (lista ?? []).filter((m) => idDaMensagem(m) !== id));
      setMensagemAberta(null);
    } catch (e) {
      setErro(e instanceof ApiEmailError ? e.message : "Não foi possível excluir a mensagem.");
    } finally {
      setExcluindo(false);
    }
  }

  async function anexar(arquivo: File) {
    setEnviandoAnexo(true);
    try {
      const resultado = await apiEmail.uploadAnexo(arquivo);
      setAnexos((a) => [...a, resultado]);
    } catch (e) {
      setErro(e instanceof ApiEmailError ? e.message : "Não foi possível anexar o arquivo.");
    } finally {
      setEnviandoAnexo(false);
    }
  }

  async function enviar() {
    setEnviando(true);
    try {
      await apiEmail.post("/email/mensagens", {
        ...novaMsg,
        anexos: anexos.map((a) => a.file_id),
      });
      setCompondo(false);
      setNovaMsg({ para: "", assunto: "", corpo_html: "" });
      setAnexos([]);
    } catch (e) {
      setErro(e instanceof ApiEmailError ? e.message : "Não foi possível enviar a mensagem.");
    } finally {
      setEnviando(false);
    }
  }

  if (semSessao) return <Navigate to="/corvia-mail" replace />;

  if (erro) {
    return (
      <>
        <p className="eyebrow">Caixa de e-mail</p>
        <LogoCorviaMail tamanho="compacto" />
        <Erro mensagem={erro} />
      </>
    );
  }

  if (!enderecoAtual) {
    return (
      <>
        <p className="eyebrow">Caixa de e-mail</p>
        <LogoCorviaMail tamanho="compacto" />
        <Carregando />
      </>
    );
  }

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
        <div>
          <p className="eyebrow" style={{ margin: 0 }}>Caixa de e-mail</p>
          <div style={{ margin: "0.2rem 0 0.3rem", display: "flex", justifyContent: "flex-start" }}>
            <LogoCorviaMail tamanho="compacto" />
          </div>
          <h1 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 500 }}>{enderecoAtual}</h1>
        </div>
        <button className="botao botao--secundario" onClick={sair}>Sair da caixa</button>
      </div>
      <RessalvaClinica />

      <button className="botao" style={{ marginTop: "0.8rem" }} onClick={() => setCompondo(true)}>
        + Escrever
      </button>

      {compondo && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <label>Para</label>
          <input value={novaMsg.para} onChange={(e) => setNovaMsg({ ...novaMsg, para: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Assunto</label>
          <input value={novaMsg.assunto} onChange={(e) => setNovaMsg({ ...novaMsg, assunto: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Mensagem</label>
          <textarea
            rows={6}
            value={novaMsg.corpo_html}
            onChange={(e) => setNovaMsg({ ...novaMsg, corpo_html: e.target.value })}
          />

          <label style={{ marginTop: "0.5rem" }}>Anexo</label>
          <input
            type="file"
            disabled={enviandoAnexo}
            onChange={(e) => {
              const arquivo = e.target.files?.[0];
              if (arquivo) anexar(arquivo);
              e.target.value = "";
            }}
          />
          {anexos.length > 0 && (
            <ul style={{ margin: "0.4rem 0 0", paddingLeft: "1.2rem", fontSize: "0.86rem" }}>
              {anexos.map((a) => (
                <li key={a.file_id}>
                  {a.nome}{" "}
                  <button
                    type="button"
                    className="botao botao--secundario"
                    style={{ padding: "0 0.4rem", fontSize: "0.78rem" }}
                    onClick={() => setAnexos((lista) => lista.filter((x) => x.file_id !== a.file_id))}
                  >
                    remover
                  </button>
                </li>
              ))}
            </ul>
          )}
          {enviandoAnexo && <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>Enviando anexo…</p>}

          <div style={{ display: "flex", gap: 8, marginTop: "0.6rem" }}>
            <button
              className="botao"
              onClick={enviar}
              disabled={enviando || enviandoAnexo || !novaMsg.para || !novaMsg.assunto}
            >
              {enviando ? "Enviando…" : "Enviar"}
            </button>
            <button
              className="botao botao--secundario"
              onClick={() => {
                setCompondo(false);
                setAnexos([]);
              }}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div
        className="grade"
        style={{ gridTemplateColumns: "180px 1fr 1.4fr", gap: "1rem", marginTop: "1rem", alignItems: "start" }}
      >
        <div className="cartao">
          <p className="eyebrow" style={{ margin: 0 }}>Pastas</p>
          <ul style={{ listStyle: "none", padding: 0, margin: "0.5rem 0 0" }}>
            <li>
              <button
                className="botao botao--secundario"
                style={{ width: "100%", textAlign: "left" }}
                onClick={() => setPastaAtual(undefined)}
              >
                Entrada
              </button>
            </li>
            {(pastas ?? []).map((p) => (
              <li key={idDaPasta(p)} style={{ marginTop: 4 }}>
                <button
                  className="botao botao--secundario"
                  style={{ width: "100%", textAlign: "left" }}
                  onClick={() => setPastaAtual(idDaPasta(p))}
                >
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
            <div style={{ padding: "1rem" }}><Vazio titulo="Nenhuma mensagem" /></div>
          ) : (
            mensagens.map((m) => (
              <button
                key={idDaMensagem(m)}
                onClick={() => abrirMensagem(m)}
                style={{
                  display: "block",
                  width: "100%",
                  textAlign: "left",
                  padding: "0.6rem 0.8rem",
                  border: "none",
                  borderBottom: "1px solid var(--linha)",
                  background: "transparent",
                  cursor: "pointer",
                }}
              >
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
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.6rem" }}>
                <h3 style={{ marginTop: 0 }}>{mensagemAberta.subject ?? "(sem assunto)"}</h3>
                <button
                  className="botao botao--secundario"
                  style={{ fontSize: "0.8rem", flexShrink: 0 }}
                  onClick={excluirMensagemAberta}
                  disabled={excluindo}
                >
                  {excluindo ? "Excluindo…" : "Excluir"}
                </button>
              </div>
              <p className="eyebrow">
                {remetente(mensagemAberta)} · {dataMensagem(mensagemAberta)}
              </p>
              {mensagemAberta.htmlContent && !mensagemAberta.content && (
                <p className="eyebrow" role="note">
                  Formatação HTML removida por segurança. Links e recursos remotos não foram carregados.
                </p>
              )}
              <p style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>
                {corpoSeguro(mensagemAberta)}
              </p>
            </>
          )}
        </div>
      </div>
    </>
  );
}
