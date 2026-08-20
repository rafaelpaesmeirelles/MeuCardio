import { useEffect, useMemo, useRef, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import LogoCorviaMail from "../components/LogoCorviaMail";
import LogoProvedor from "../components/LogoProvedor";
import { Carregando, Vazio } from "../components/Estado";
import { apiEmail, ApiEmailError, tokenEmail } from "../lib/apiEmail";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { CHAVE_PENDING_COMPOSE } from "../components/OfertaEnvioEmailPaciente";
import "../styles/corvia-mail-professional.css";

type Conta = { id: string; provider: "corvia" | "google" | "microsoft" | "yahoo" | "apple"; display_name: string; email_address: string; native: boolean; read_mail: boolean; send_mail: boolean; padrao: boolean };
type Pasta = { folderId?: string; id?: string; folderName?: string; name?: string; folderType?: string };
type Mensagem = { messageId?: string; id?: string; subject?: string; fromAddress?: string; sender?: string; toAddress?: string; ccAddress?: string; receivedTime?: string; sentDateInGMT?: string; date?: string; summary?: string; content?: string | null; htmlContent?: string | null; status?: string; status2?: string; hasAttachment?: number | string; flagid?: string; flagId?: string; origem?: string; provider?: string };
type AnexoRecebido = { attachmentId?: string; attachId?: string; attachmentName?: string; fileName?: string; attachmentSize?: number; size?: number };
type AnexoEnviado = { file_id: string; nome: string };
type Verificacao = { assinado: boolean; titular?: string; texto_comprovacao: string | null };
type Contato = { id: number; name: string; emails: string[]; organization: string };
type Filtro = "todas" | "nao_lidas" | "favoritas" | "anexos";
type Rascunho = { modo: "nova" | "reply" | "replyall" | "forward"; origem?: string; messageId?: string; de: string; para: string; cc: string; cco: string; assunto: string; corpo: string };
type CaixaCombinada = { mensagens: Mensagem[]; fontes_com_erro: { origem: string; provider: string; erro: string }[] };

const CHAVE_CONTA = "corvia.mail.professional.conta";
const CHAVE_COMBINADAS = "corvia.mail.professional.combinadas";
const RASCUNHO_VAZIO: Rascunho = { modo: "nova", de: "corvia", para: "", cc: "", cco: "", assunto: "", corpo: "" };
const NOMES_PROVEDOR: Record<string, string> = { corvia: "CorvIA Mail", google: "Google", microsoft: "Microsoft", yahoo: "Yahoo Mail", apple: "Apple iCloud" };
const NOMES_PASTA: Record<string, string> = { Inbox: "Entrada", INBOX: "Entrada", inbox: "Entrada", Entrada: "Entrada", Drafts: "Rascunhos", DRAFT: "Rascunhos", drafts: "Rascunhos", draft: "Rascunhos", Sent: "Enviados", SENT: "Enviados", sentitems: "Enviados", sent: "Enviados", Spam: "Spam", SPAM: "Spam", junkemail: "Spam", Bulk: "Spam", Trash: "Lixeira", TRASH: "Lixeira", deleteditems: "Lixeira", trash: "Lixeira", IMPORTANT: "Importantes", STARRED: "Com estrela", Snoozed: "Adiados", Outbox: "Saída" };
const ICONE_PASTA: Record<string, string> = { Entrada: "▣", Rascunhos: "◇", Enviados: "↗", Spam: "!", Lixeira: "⌫", Importantes: "◆", "Com estrela": "☆", Adiados: "◷", Saída: "↑" };
const CORES = ["#173f5f", "#7a2738", "#255c50", "#6f4e37", "#405c2b", "#4d4a8a", "#9b5c21"];

const idMensagem = (m: Mensagem) => m.messageId ?? m.id ?? "";
const idPasta = (p: Pasta) => p.folderId ?? p.id ?? "";
function nomePasta(p: Pasta) { const bruto = p.folderType ?? p.folderName ?? p.name ?? "Pasta"; return NOMES_PASTA[bruto] ?? NOMES_PASTA[p.folderName ?? ""] ?? p.folderName ?? p.name ?? bruto; }
const remetente = (m: Mensagem) => m.fromAddress ?? m.sender ?? "Remetente não informado";
function iniciais(texto: string) { const nome = texto.replace(/<[^>]+>/g, " ").split("@")[0].replace(/[^a-zA-ZÀ-ÿ0-9 ]/g, " ").trim(); const partes = nome.split(/\s+/).filter(Boolean); return (partes.slice(0, 2).map((p) => p[0]).join("") || "E").toUpperCase(); }
function corAvatar(texto: string) { let hash = 0; for (let i = 0; i < texto.length; i++) hash = (hash * 31 + texto.charCodeAt(i)) >>> 0; return CORES[hash % CORES.length]; }
const naoLida = (m: Mensagem) => ["0", "unread", "nao_lida"].includes(String(m.status ?? "").toLowerCase());
const favorita = (m: Mensagem) => ["followup", "important", "info"].includes(String(m.flagid ?? m.flagId ?? m.status2 ?? "").toLowerCase());
const temAnexo = (m: Mensagem) => Number(m.hasAttachment ?? 0) > 0;
function dataObj(m: Mensagem) { const bruto = m.receivedTime ?? m.sentDateInGMT ?? m.date; if (!bruto) return null; const n = Number(bruto); const d = Number.isFinite(n) && String(bruto).length > 8 ? new Date(n) : new Date(bruto); return Number.isNaN(d.getTime()) ? null : d; }
function dataCurta(m: Mensagem) { const d = dataObj(m); if (!d) return ""; const hoje = new Date(); return d.toDateString() === hoje.toDateString() ? d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" }); }
const dataCompleta = (m: Mensagem) => dataObj(m)?.toLocaleString("pt-BR", { dateStyle: "medium", timeStyle: "short" }) ?? "";
function formatarTamanho(bytes?: number) { if (!bytes) return ""; if (bytes < 1024) return `${bytes} B`; if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`; return `${(bytes / 1024 / 1024).toFixed(1)} MB`; }
function extrairEmail(valor: string) { return (valor.match(/<([^>]+)>/)?.[1] ?? valor).trim(); }
const prefixo = (contaId: string) => contaId === "corvia" ? "/email" : `/email/externas/${contaId}`;

function documentoSeguro(html: string, permitirImagens: boolean) {
  const parser = new DOMParser(); const doc = parser.parseFromString(html, "text/html");
  doc.querySelectorAll("script,iframe,object,embed,form,input,button,textarea,select,link,meta,base,svg,math,video,audio").forEach((e) => e.remove());
  doc.querySelectorAll("*").forEach((el) => {
    for (const attr of Array.from(el.attributes)) { const n = attr.name.toLowerCase(); if (n.startsWith("on") || n === "style" || n === "srcset") el.removeAttribute(attr.name); }
    if (el instanceof HTMLAnchorElement) { const href = el.getAttribute("href") ?? ""; if (!/^(https?:|mailto:|tel:)/i.test(href)) el.removeAttribute("href"); el.target = "_blank"; el.rel = "noopener noreferrer nofollow"; }
    if (el instanceof HTMLImageElement) { const src = el.getAttribute("src") ?? ""; const ok = permitirImagens ? /^(https?:|data:image\/)/i.test(src) : /^data:image\//i.test(src); if (!ok) el.remove(); else { el.removeAttribute("width"); el.removeAttribute("height"); el.loading = "lazy"; } }
  });
  const img = permitirImagens ? "https: http: data:" : "data:";
  return `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${img}; style-src 'unsafe-inline'; font-src data:"><style>html{font:15px/1.62 Inter,Arial,sans-serif;color:#26333b;background:white}body{margin:0;padding:2px 4px;overflow-wrap:anywhere}a{color:#7a2738}img{max-width:100%;height:auto}table{max-width:100%;border-collapse:collapse}td,th{padding:.35rem;border:1px solid #e6e9ec}blockquote{margin-left:0;padding-left:1rem;border-left:3px solid #ddd;color:#65727a}</style></head><body>${doc.body.innerHTML}</body></html>`;
}

function CorpoMensagem({ mensagem }: { mensagem: Mensagem }) {
  const [permitirImagens, setPermitirImagens] = useState(false);
  useEffect(() => setPermitirImagens(false), [mensagem.messageId, mensagem.id]);
  const conteudo = mensagem.htmlContent?.trim() || mensagem.content?.trim() || mensagem.summary?.trim() || "";
  if (!conteudo) return <Vazio titulo="Mensagem sem conteúdo disponível" />;
  if (!/<\s*(?:!doctype|html|body|div|p|span|table|br|a|ul|ol|li)\b/i.test(conteudo)) return <div className="cmp-reader__text">{conteudo}</div>;
  return <><div className="cmp-privacy"><span>Imagens externas {permitirImagens ? "liberadas" : "bloqueadas"}.</span><button onClick={() => setPermitirImagens((v) => !v)}>{permitirImagens ? "Bloquear" : "Carregar imagens"}</button></div><iframe className="cmp-reader__html" sandbox="allow-popups allow-popups-to-escape-sandbox" srcDoc={documentoSeguro(conteudo, permitirImagens)} title={`Conteúdo do e-mail: ${mensagem.subject ?? "sem assunto"}`} /></>;
}

// --------------------------------------------------------------------------
// Modo demonstração do investidor (issue #52, complemento "INVESTIDOR NO
// CORVIA MAIL") — navega a MESMA interface visual, com dado 100% sintético
// (`GET /email/demo/*`, current_user — nunca a sessão de mailbox própria,
// que o investidor nunca chega a ter). Toda ação real (enviar, responder,
// encaminhar, sincronizar, conectar conta) fica desabilitada aqui; o
// backend também recusa cada uma com 403 (`app/services/entitlement.py::
// bloquear_investidor_em_operacao_real_de_mail`) — este componente nunca é
// a única barreira, só evita que o médico clique num botão morto sem
// explicação.
type MensagemDemo = { messageId: string; subject: string; fromAddress: string; summary: string; receivedTime: string; status: string; content?: string };
type PastaDemo = { folderId: string; folderName: string; folderType: string };

function ModoDemonstracaoInvestidor() {
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [pastas, setPastas] = useState<PastaDemo[]>([]);
  const [mensagens, setMensagens] = useState<MensagemDemo[]>([]);
  const [aberta, setAberta] = useState<MensagemDemo | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [compondo, setCompondo] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<PastaDemo[]>("/email/demo/pastas"),
      api.get<MensagemDemo[]>("/email/demo/mensagens"),
    ])
      .then(([p, m]) => { setPastas(p); setMensagens(m); })
      .finally(() => setCarregando(false));
  }, []);

  async function abrir(m: MensagemDemo) {
    const completa = await api.get<MensagemDemo>(`/email/demo/mensagens/${m.messageId}`);
    setAberta(completa);
  }

  return (
    <main className="cmp-shell">
      <header className="cmp-topbar">
        <div className="cmp-brand">
          <LogoCorviaMail tamanho="compacto" />
          <span><strong>CorvIA Mail</strong><small>investidor.demo@corvia.med.br</small></span>
        </div>
        <div className="cmp-user">
          <div><strong>{usuario?.full_name || "Investidor"}</strong><small>{usuario?.email}</small></div>
          <button onClick={() => navigate("/corvia-mail")} title="Voltar">⏻</button>
        </div>
      </header>

      <div className="cmp-alert cmp-alert--warn" role="status">
        <span>
          <strong>Modo demonstração — CorvIA Mail.</strong> As mensagens abaixo são fictícias, só
          para conhecer a interface. Enviar, responder, encaminhar, conectar uma conta externa e
          sincronizar não estão disponíveis neste modo.
        </span>
      </div>

      <section className="cmp-workspace">
        <aside className="cmp-sidebar">
          <button
            className="cmp-compose-primary"
            onClick={() => setCompondo(true)}
            title="Recurso indisponível no modo investidor."
          >
            <span>＋</span> Nova mensagem
          </button>
          <div className="cmp-sidebar__section">
            <p>Correio</p>
            {pastas.map((p) => (
              <button key={p.folderId} className={p.folderType === "inbox" ? "is-active" : ""} disabled={p.folderType !== "inbox"}>
                <span>{p.folderType === "inbox" ? "▣" : p.folderType === "sent" ? "↗" : "◇"}</span>{p.folderName}
              </button>
            ))}
          </div>
          <div className="cmp-sidebar__privacy">
            <strong>Modo investidor</strong>
            <span>Conta de avaliação — sem caixa real, sem envio ou recebimento de e-mail.</span>
          </div>
        </aside>

        <section className="cmp-list">
          <div className="cmp-list__header">
            <div><p>Entrada (demonstração)</p><h2>{mensagens.length} mensagens</h2></div>
          </div>
          <div className="cmp-list__scroll">
            {carregando ? (
              <div className="cmp-state"><Carregando /></div>
            ) : (
              mensagens.map((m) => (
                <article key={m.messageId} className={`cmp-message ${aberta?.messageId === m.messageId ? "is-active" : ""}`}>
                  <button className="cmp-message__open" onClick={() => void abrir(m)}>
                    <span className="cmp-avatar" style={{ background: corAvatar(m.fromAddress) }}>{iniciais(m.fromAddress)}</span>
                    <span className="cmp-message__body">
                      <span className="cmp-message__meta"><strong>{m.fromAddress}</strong></span>
                      <b>{m.subject}</b>
                      <small>{m.summary}</small>
                    </span>
                  </button>
                </article>
              ))
            )}
          </div>
        </section>

        <section className={`cmp-reader ${aberta ? "has-message" : ""}`}>
          {!aberta ? (
            <div className="cmp-reader__empty"><span>✉</span><h2>Selecione uma mensagem</h2><p>Conteúdo de demonstração — nenhuma mensagem aqui é real.</p></div>
          ) : (
            <>
              <div className="cmp-reader__toolbar">
                <button disabled title="Recurso indisponível no modo investidor.">↩ Responder</button>
                <button disabled title="Recurso indisponível no modo investidor.">↩ Todos</button>
                <button disabled title="Recurso indisponível no modo investidor.">↗ Encaminhar</button>
              </div>
              <header className="cmp-reader__header">
                <h1>{aberta.subject}</h1>
                <div className="cmp-reader__sender">
                  <span className="cmp-avatar cmp-avatar--large" style={{ background: corAvatar(aberta.fromAddress) }}>{iniciais(aberta.fromAddress)}</span>
                  <div><strong>{aberta.fromAddress}</strong><small>Para: investidor.demo@corvia.med.br</small></div>
                </div>
              </header>
              <div className="cmp-reader__content"><CorpoMensagem mensagem={{ subject: aberta.subject, content: aberta.content }} /></div>
            </>
          )}
        </section>
      </section>

      {compondo && (
        <div className="cmp-compose-modal">
          <button className="cmp-compose-modal__backdrop" aria-label="Fechar" onClick={() => setCompondo(false)} />
          <section className="cmp-composer">
            <header><div><small>NOVA MENSAGEM</small><h2>Escrever (demonstração)</h2></div><button onClick={() => setCompondo(false)}>×</button></header>
            <div className="cmp-field"><label>Para</label><input placeholder="nome@exemplo.com" /></div>
            <div className="cmp-field cmp-field--subject"><label>Assunto</label><input /></div>
            <textarea className="cmp-compose-body" placeholder="Este é o modo demonstração — a mensagem não será enviada." />
            <footer>
              <button className="cmp-send" disabled title="Recurso indisponível no modo investidor.">Enviar</button>
              <span>Modo demonstração — nenhum e-mail real é enviado.</span>
            </footer>
          </section>
        </div>
      )}
    </main>
  );
}

export default function CaixaDeEmailProfessional() {
  const navigate = useNavigate(); const { usuario } = useAuth();
  const [semSessao, setSemSessao] = useState(!tokenEmail.get());
  const [endereco, setEndereco] = useState<string | null>(null);
  const [contas, setContas] = useState<Conta[]>([]);
  const [contaId, setContaId] = useState("corvia");
  const [combinadas, setCombinadas] = useState<Set<string> | null>(null);
  const [pastas, setPastas] = useState<Pasta[]>([]);
  const [pastaId, setPastaId] = useState<string | undefined>();
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [aberta, setAberta] = useState<Mensagem | null>(null);
  const [anexosRecebidos, setAnexosRecebidos] = useState<AnexoRecebido[]>([]);
  const [fontesComErro, setFontesComErro] = useState<CaixaCombinada["fontes_com_erro"]>([]);
  const [busca, setBusca] = useState(""); const [filtro, setFiltro] = useState<Filtro>("todas"); const [selecionadas, setSelecionadas] = useState<Set<string>>(new Set());
  const [carregandoContexto, setCarregandoContexto] = useState(false); const [atualizando, setAtualizando] = useState(false); const [erro, setErro] = useState<string | null>(null); const [aviso, setAviso] = useState<string | null>(null);
  const [compondo, setCompondo] = useState(false); const [rascunho, setRascunho] = useState<Rascunho>(RASCUNHO_VAZIO); const [mostrarCopias, setMostrarCopias] = useState(false); const [anexos, setAnexos] = useState<AnexoEnviado[]>([]); const [verificacoes, setVerificacoes] = useState<Record<string, Verificacao>>({}); const [enviando, setEnviando] = useState(false); const [enviandoAnexo, setEnviandoAnexo] = useState(false); const [contatos, setContatos] = useState<Contato[]>([]);
  const contextoSeq = useRef(0);

  function falha(e: unknown, fallback: string) { if (e instanceof ApiEmailError && e.status === 401) { setSemSessao(true); return "Sua sessão expirou. Entre novamente."; } return e instanceof ApiEmailError ? e.message : fallback; }
  function sair() { tokenEmail.clear(); navigate("/corvia-mail"); }

  async function carregarCombinada(ids: Set<string>, seq = contextoSeq.current) {
    const params = new URLSearchParams({ limite: "50", contas: [...ids].join(",") });
    const r = await apiEmail.get<CaixaCombinada>(`/email/mensagens/todas?${params}`);
    if (seq !== contextoSeq.current) return;
    setMensagens(r.mensagens); setFontesComErro(r.fontes_com_erro ?? []); setPastas([]); setPastaId(undefined);
  }

  async function carregarConta(id: string, seq = contextoSeq.current) {
    const p = prefixo(id); const listaPastas = await apiEmail.get<Pasta[]>(`${p}/pastas`); if (seq !== contextoSeq.current) return;
    setPastas(listaPastas);
    const inbox = listaPastas.find((x) => nomePasta(x) === "Entrada") ?? listaPastas[0]; const alvo = inbox ? idPasta(inbox) : undefined; setPastaId(alvo);
    const params = new URLSearchParams({ limite: "100", inicio: "1" }); if (alvo) params.set("pasta", alvo);
    const lista = await apiEmail.get<Mensagem[]>(`${p}/mensagens?${params}`); if (seq !== contextoSeq.current) return; setMensagens(lista); setFontesComErro([]);
  }

  async function carregarContexto() {
    if (!endereco) return; const seq = ++contextoSeq.current; setCarregandoContexto(true); setErro(null); setAberta(null); setAnexosRecebidos([]); setSelecionadas(new Set());
    try { if (combinadas?.size) await carregarCombinada(combinadas, seq); else await carregarConta(contaId, seq); }
    catch (e) { if (seq === contextoSeq.current) { setMensagens([]); setErro(falha(e, "Não foi possível carregar esta caixa.")); } }
    finally { if (seq === contextoSeq.current) setCarregandoContexto(false); }
  }

  useEffect(() => {
    if (semSessao) return;
    Promise.all([apiEmail.get<{ email_address: string }>("/email/eu"), apiEmail.get<Conta[]>("/email/contas")]).then(([eu, cs]) => {
      setEndereco(eu.email_address); setContas(cs);
      const salva = localStorage.getItem(CHAVE_CONTA); const padrao = cs.find((c) => c.padrao)?.id ?? "corvia"; setContaId(salva && cs.some((c) => c.id === salva) ? salva : padrao);
      const bruto = localStorage.getItem(CHAVE_COMBINADAS); if (bruto) { try { const ids = (JSON.parse(bruto) as string[]).filter((id) => cs.some((c) => c.id === id && c.read_mail)); if (ids.length > 1) setCombinadas(new Set(ids)); else localStorage.removeItem(CHAVE_COMBINADAS); } catch { localStorage.removeItem(CHAVE_COMBINADAS); } }
    }).catch((e) => setErro(falha(e, "Não foi possível iniciar o CorvIA Mail.")));
  }, [semSessao]);

  useEffect(() => { if (endereco) void carregarContexto(); }, [endereco, contaId, combinadas ? [...combinadas].sort().join("|") : ""]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (!endereco) return; apiEmail.get<Contato[]>("/email/contatos?limite=100").then(setContatos).catch(() => setContatos([])); }, [endereco]);

  useEffect(() => {
    if (semSessao) return; const bruto = sessionStorage.getItem(CHAVE_PENDING_COMPOSE); if (!bruto) return; sessionStorage.removeItem(CHAVE_PENDING_COMPOSE);
    try { const p = JSON.parse(bruto) as { para: string; assunto: string; corpo: string; anexos: AnexoEnviado[] }; setRascunho({ ...RASCUNHO_VAZIO, de: contas.find((c) => c.padrao)?.id ?? "corvia", para: p.para, assunto: p.assunto, corpo: p.corpo }); setAnexos(p.anexos ?? []); setCompondo(true); } catch { /* ignora payload inválido */ }
  }, [semSessao, contas]);

  async function mudarPasta(id: string) {
    if (combinadas) return; setPastaId(id); setAberta(null); setSelecionadas(new Set()); setAtualizando(true); setErro(null);
    try { const params = new URLSearchParams({ limite: "100", inicio: "1", pasta: id }); setMensagens(await apiEmail.get<Mensagem[]>(`${prefixo(contaId)}/mensagens?${params}`)); }
    catch (e) { setErro(falha(e, "Não foi possível carregar a pasta.")); }
    finally { setAtualizando(false); }
  }

  function selecionarConta(id: string) { setCombinadas(null); localStorage.removeItem(CHAVE_COMBINADAS); setContaId(id); localStorage.setItem(CHAVE_CONTA, id); }
  function selecionarTodas() { const ids = new Set(contas.filter((c) => c.read_mail).map((c) => c.id)); if (ids.size < 2) return; setCombinadas(ids); localStorage.setItem(CHAVE_COMBINADAS, JSON.stringify([...ids])); }

  async function abrirMensagem(m: Mensagem) {
    const origem = combinadas ? (m.origem ?? "corvia") : contaId; const id = idMensagem(m); if (!id) return; setErro(null);
    try { const completa = await apiEmail.get<Mensagem>(`${prefixo(origem)}/mensagens/${encodeURIComponent(id)}`); completa.origem = origem; setAberta(completa); setMensagens((ls) => ls.map((x) => idMensagem(x) === id && (!combinadas || x.origem === origem) ? { ...x, status: "1" } : x));
      if (origem === "corvia" && temAnexo(completa)) setAnexosRecebidos(await apiEmail.get<AnexoRecebido[]>(`/email/mensagens/${encodeURIComponent(id)}/anexos`).catch(() => [])); else setAnexosRecebidos([]);
    } catch (e) { setErro(falha(e, "Não foi possível abrir a mensagem.")); }
  }

  async function agir(acao: "lida" | "nao_lida" | "mover" | "sinalizar", ids: string[], extras: Record<string, string> = {}) {
    if (!ids.length || combinadas) return; setAtualizando(true); try { await apiEmail.put(`${prefixo(contaId)}/mensagens/acoes`, { message_ids: ids, acao, ...extras }); await carregarContexto(); setAviso("Ação aplicada."); } catch (e) { setErro(falha(e, "Não foi possível atualizar as mensagens.")); } finally { setAtualizando(false); }
  }

  async function excluirMensagem(m: Mensagem) {
    const origem = m.origem ?? contaId; const id = idMensagem(m); if (!id || !window.confirm("Mover esta mensagem para a lixeira?")) return; setAtualizando(true);
    try { await apiEmail.delete(`${prefixo(origem)}/mensagens/${encodeURIComponent(id)}`); setMensagens((ls) => ls.filter((x) => !(idMensagem(x) === id && (!combinadas || (x.origem ?? "corvia") === origem)))); if (aberta && idMensagem(aberta) === id) setAberta(null); setSelecionadas((ids) => { const n = new Set(ids); n.delete(id); return n; }); setAviso("Mensagem removida."); }
    catch (e) { setErro(falha(e, "Não foi possível remover a mensagem.")); } finally { setAtualizando(false); }
  }

  async function excluirSelecionadas() {
    if (combinadas || selecionadas.size === 0) return;
    const ids = [...selecionadas];
    if (!window.confirm(`Mover ${ids.length} ${ids.length === 1 ? "mensagem" : "mensagens"} para a lixeira?`)) return;
    setAtualizando(true); setErro(null);
    try {
      await Promise.all(ids.map((id) => apiEmail.delete(`${prefixo(contaId)}/mensagens/${encodeURIComponent(id)}`)));
      const removidas = new Set(ids);
      setMensagens((ls) => ls.filter((m) => !removidas.has(idMensagem(m))));
      if (aberta && removidas.has(idMensagem(aberta))) setAberta(null);
      setSelecionadas(new Set());
      setAviso(`${ids.length} ${ids.length === 1 ? "mensagem removida" : "mensagens removidas"}.`);
    } catch (e) { setErro(falha(e, "Não foi possível remover todas as mensagens selecionadas.")); }
    finally { setAtualizando(false); }
  }

  function novaMensagem() { const de = contas.find((c) => c.padrao && c.send_mail)?.id ?? contas.find((c) => c.send_mail)?.id ?? "corvia"; setRascunho({ ...RASCUNHO_VAZIO, de }); setAnexos([]); setVerificacoes({}); setMostrarCopias(false); setCompondo(true); }
  function responder(modo: "reply" | "replyall" | "forward") { if (!aberta) return; const origem = aberta.origem ?? contaId; const assunto = aberta.subject ?? "(sem assunto)"; setRascunho({ ...RASCUNHO_VAZIO, modo, origem, messageId: idMensagem(aberta), de: origem, para: modo === "forward" ? "" : extrairEmail(remetente(aberta)), cc: modo === "replyall" ? (aberta.ccAddress ?? "") : "", assunto: /^(re:|enc:)/i.test(assunto) ? assunto : `${modo === "forward" ? "Enc:" : "Re:"} ${assunto}` }); setAnexos([]); setMostrarCopias(modo === "replyall"); setCompondo(true); }

  async function anexar(file: File) { if (rascunho.de !== "corvia") { setErro("Anexos em contas externas ainda não são suportados com segurança. Selecione CorvIA Mail no campo De."); return; } setEnviandoAnexo(true); try { const r = await apiEmail.uploadAnexo(file); setAnexos((a) => [...a, r]); apiEmail.verificarAssinaturaAnexo(file).then((v) => setVerificacoes((x) => ({ ...x, [r.file_id]: v }))).catch(() => {}); } catch (e) { setErro(falha(e, "Não foi possível anexar o arquivo.")); } finally { setEnviandoAnexo(false); } }

  async function enviar() {
    if (!rascunho.para.trim()) { setErro("Informe ao menos um destinatário."); return; } setEnviando(true); setErro(null);
    try {
      const origem = rascunho.de;
      if (rascunho.modo === "nova" || origem !== "corvia") await apiEmail.post(`${prefixo(origem)}/mensagens`, { para: rascunho.para, cc: rascunho.cc || null, cco: rascunho.cco || null, assunto: rascunho.assunto, corpo_html: rascunho.corpo, anexos: origem === "corvia" ? anexos.map((a) => a.file_id) : [] });
      else await apiEmail.post(`/email/mensagens/${encodeURIComponent(rascunho.messageId ?? "")}/responder`, { acao: rascunho.modo, para: rascunho.modo === "forward" ? rascunho.para : null, cc: rascunho.cc || null, cco: rascunho.cco || null, assunto: rascunho.assunto, conteudo: rascunho.corpo, anexos: anexos.map((a) => a.file_id) });
      setCompondo(false); setRascunho(RASCUNHO_VAZIO); setAnexos([]); setAviso("Mensagem enviada.");
    } catch (e) { setErro(falha(e, "Não foi possível enviar a mensagem.")); } finally { setEnviando(false); }
  }

  async function definirPadrao(id: string) { try { await apiEmail.put("/email/conta-padrao-envio", { conta_id: id }); setContas((cs) => cs.map((c) => ({ ...c, padrao: c.id === id }))); setAviso("Conta padrão atualizada."); } catch (e) { setErro(falha(e, "Não foi possível definir a conta padrão.")); } }

  const filtradas = useMemo(() => mensagens.filter((m) => {
    const q = busca.trim().toLowerCase(); const bate = !q || `${remetente(m)} ${m.subject ?? ""} ${m.summary ?? ""}`.toLowerCase().includes(q); if (!bate) return false;
    if (filtro === "nao_lidas") return naoLida(m); if (filtro === "favoritas") return favorita(m); if (filtro === "anexos") return temAnexo(m); return true;
  }), [mensagens, busca, filtro]);
  const contaAtual = contas.find((c) => c.id === contaId); const pastaAtual = pastas.find((p) => idPasta(p) === pastaId);

  // Investidor (issue #52): nunca tem sessão de mailbox real (nenhuma
  // credencial jamais é emitida para ele — ver `POST /email/conta`,
  // bloqueado no backend) — em vez de cair no redirecionamento de "sem
  // sessão" abaixo, ele vê a interface em modo demonstração, sem precisar
  // logar em lugar nenhum.
  if (usuario?.investidor) return <ModoDemonstracaoInvestidor />;
  if (semSessao) return <Navigate to="/corvia-mail" replace />;
  if (!endereco) return <div className="cmp-loading"><LogoCorviaMail tamanho="compacto" /><Carregando /></div>;

  return <main className="cmp-shell">
    <header className="cmp-topbar">
      <div className="cmp-brand"><LogoCorviaMail tamanho="compacto" /><span><strong>CorvIA Mail</strong><small>{combinadas ? `${combinadas.size} contas unificadas` : `${NOMES_PROVEDOR[contaAtual?.provider ?? "corvia"]} · ${contaAtual?.email_address ?? endereco}`}</small></span></div>
      <label className="cmp-global-search"><span>⌕</span><input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Pesquisar nesta caixa" /></label>
      <div className="cmp-user">{usuario?.photo_url ? <img src={usuario.photo_url} alt="" /> : <span style={{ background: corAvatar(usuario?.full_name || usuario?.email || endereco) }}>{iniciais(usuario?.full_name || usuario?.email || endereco)}</span>}<div><strong>{usuario?.full_name || "Minha conta"}</strong><small>{usuario?.email}</small></div><button onClick={sair} title="Sair">⏻</button></div>
    </header>

    {erro && <div className="cmp-alert cmp-alert--error"><span>{erro}</span><button onClick={() => setErro(null)}>×</button></div>}
    {aviso && <div className="cmp-alert cmp-alert--ok"><span>{aviso}</span><button onClick={() => setAviso(null)}>×</button></div>}
    {fontesComErro.length > 0 && <div className="cmp-alert cmp-alert--warn"><span>{fontesComErro.length} conta(s) não responderam. As demais continuam disponíveis.</span></div>}

    <section className="cmp-workspace">
      <aside className="cmp-accounts" aria-label="Contas de e-mail">
        <button className={`cmp-account cmp-account--all ${combinadas ? "is-active" : ""}`} onClick={selecionarTodas} title="Todas as caixas"><span>⊞</span></button>
        <div className="cmp-accounts__rule" />
        {contas.filter((c) => c.read_mail).map((c) => <button key={c.id} className={`cmp-account ${!combinadas && contaId === c.id ? "is-active" : ""}`} onClick={() => selecionarConta(c.id)} title={`${NOMES_PROVEDOR[c.provider]} — ${c.email_address}`}>{c.provider === "corvia" ? <span className="cmp-account__corvia">C</span> : <LogoProvedor provedor={c.provider} />}{c.padrao && <i>•</i>}</button>)}
      </aside>

      <aside className="cmp-sidebar">
        <button className="cmp-compose-primary" onClick={novaMensagem}><span>＋</span> Nova mensagem</button>
        <div className="cmp-sidebar__section"><p>Correio</p>{combinadas ? <button className="is-active"><span>▣</span> Caixa unificada <b>{mensagens.filter(naoLida).length || ""}</b></button> : pastas.map((p) => { const n = nomePasta(p); return <button key={idPasta(p)} className={idPasta(p) === pastaId ? "is-active" : ""} onClick={() => void mudarPasta(idPasta(p))}><span>{ICONE_PASTA[n] ?? "□"}</span>{n}</button>; })}</div>
        <div className="cmp-sidebar__section"><p>Filtros rápidos</p><button className={filtro === "nao_lidas" ? "is-active" : ""} onClick={() => setFiltro(filtro === "nao_lidas" ? "todas" : "nao_lidas")}><span>●</span> Não lidas</button><button className={filtro === "favoritas" ? "is-active" : ""} onClick={() => setFiltro(filtro === "favoritas" ? "todas" : "favoritas")}><span>☆</span> Favoritas</button><button className={filtro === "anexos" ? "is-active" : ""} onClick={() => setFiltro(filtro === "anexos" ? "todas" : "anexos")}><span>⌕</span> Com anexos</button></div>
        {!combinadas && contaAtual && <div className="cmp-account-card"><small>CONTA ATIVA</small><strong>{contaAtual.email_address}</strong><span>{NOMES_PROVEDOR[contaAtual.provider]}</span>{contaAtual.padrao ? <em>★ Conta padrão</em> : contaAtual.send_mail ? <button onClick={() => void definirPadrao(contaAtual.id)}>☆ Tornar padrão</button> : null}</div>}
        <div className="cmp-sidebar__privacy"><strong>Privacidade</strong><span>Use o Cofre para dados clínicos identificáveis.</span></div>
      </aside>

      <section className="cmp-list">
        <div className="cmp-list__header"><div><p>{combinadas ? "Caixa unificada" : nomePasta(pastaAtual ?? {})}</p><h2>{filtradas.length} mensagens</h2></div><button onClick={() => void carregarContexto()} disabled={atualizando || carregandoContexto} title="Atualizar">↻</button></div>
        {!combinadas && selecionadas.size > 0 && <div className="cmp-bulk"><strong>{selecionadas.size}</strong><button onClick={() => void agir("lida", [...selecionadas])}>Lida</button><button onClick={() => void agir("nao_lida", [...selecionadas])}>Não lida</button><button className="danger" disabled={atualizando} onClick={() => void excluirSelecionadas()}>Excluir</button></div>}
        <div className="cmp-list__filters"><button className={filtro === "todas" ? "is-active" : ""} onClick={() => setFiltro("todas")}>Todas</button><button className={filtro === "nao_lidas" ? "is-active" : ""} onClick={() => setFiltro("nao_lidas")}>Não lidas</button><button className={filtro === "favoritas" ? "is-active" : ""} onClick={() => setFiltro("favoritas")}>Favoritas</button></div>
        <div className="cmp-list__scroll">{carregandoContexto ? <div className="cmp-state"><Carregando /></div> : filtradas.length === 0 ? <div className="cmp-state"><Vazio titulo="Nenhuma mensagem encontrada" /></div> : filtradas.map((m) => { const id = idMensagem(m); const origem = m.origem ?? contaId; const ativa = aberta && idMensagem(aberta) === id && (aberta.origem ?? contaId) === origem; return <article key={`${origem}-${id}`} className={`cmp-message ${naoLida(m) ? "is-unread" : ""} ${ativa ? "is-active" : ""}`}><label className="cmp-message__check"><input type="checkbox" disabled={!!combinadas} checked={selecionadas.has(id)} onChange={() => setSelecionadas((s) => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; })} /></label><button className="cmp-message__open" onClick={() => void abrirMensagem(m)}><span className="cmp-avatar" style={{ background: corAvatar(remetente(m)) }}>{iniciais(remetente(m))}</span><span className="cmp-message__body"><span className="cmp-message__meta"><strong>{remetente(m)}</strong><time>{dataCurta(m)}</time></span><b>{m.subject ?? "(sem assunto)"}</b><small>{m.summary || "Sem prévia disponível"}</small><span className="cmp-message__tags">{combinadas && <i>{NOMES_PROVEDOR[contas.find((c) => c.id === origem)?.provider ?? m.provider ?? "corvia"]}</i>}{temAnexo(m) && <i>⌕ Anexo</i>}</span></span></button>{!combinadas && contaId === "corvia" && <button className={`cmp-star ${favorita(m) ? "is-active" : ""}`} onClick={() => void agir("sinalizar", [id], { sinalizador: favorita(m) ? "flag_not_set" : "followup" })}>{favorita(m) ? "★" : "☆"}</button>}</article>; })}</div>
      </section>

      <section className={`cmp-reader ${aberta ? "has-message" : ""}`}>
        {!aberta ? <div className="cmp-reader__empty"><span>✉</span><h2>Selecione uma mensagem</h2><p>Leia, responda e organize seu correio sem sair desta tela.</p></div> : <><div className="cmp-reader__toolbar"><button onClick={() => responder("reply")}>↩ Responder</button><button onClick={() => responder("replyall")}>↩ Todos</button><button onClick={() => responder("forward")}>↗ Encaminhar</button><span /><button onClick={() => void excluirMensagem(aberta)} className="danger">⌫ Excluir</button></div><header className="cmp-reader__header"><p>{NOMES_PROVEDOR[contas.find((c) => c.id === (aberta.origem ?? contaId))?.provider ?? aberta.provider ?? "corvia"]}</p><h1>{aberta.subject ?? "(sem assunto)"}</h1><div className="cmp-reader__sender"><span className="cmp-avatar cmp-avatar--large" style={{ background: corAvatar(remetente(aberta)) }}>{iniciais(remetente(aberta))}</span><div><strong>{remetente(aberta)}</strong><small>Para: {aberta.toAddress ?? contaAtual?.email_address ?? endereco}</small></div><time>{dataCompleta(aberta)}</time></div></header>{anexosRecebidos.length > 0 && <div className="cmp-attachments"><strong>Anexos</strong>{anexosRecebidos.map((a) => { const aid = a.attachmentId ?? a.attachId ?? ""; const nome = a.attachmentName ?? a.fileName ?? "anexo"; return <button key={aid} onClick={() => void apiEmail.baixarAnexo(idMensagem(aberta), aid, nome)}><span>▱</span><span>{nome}<small>{formatarTamanho(a.attachmentSize ?? a.size)}</small></span><b>Baixar</b></button>; })}</div>}<div className="cmp-reader__content"><CorpoMensagem mensagem={aberta} /></div><footer className="cmp-reader__footer"><button className="cmp-reply" onClick={() => responder("reply")}>↩ Responder</button><button className="cmp-reply cmp-reply--secondary" onClick={() => responder("forward")}>↗ Encaminhar</button></footer></>}
      </section>
    </section>

    {compondo && <div className="cmp-compose-modal"><button className="cmp-compose-modal__backdrop" aria-label="Fechar" onClick={() => !enviando && setCompondo(false)} /><section className="cmp-composer"><header><div><small>NOVA MENSAGEM</small><h2>{rascunho.modo === "nova" ? "Escrever" : rascunho.modo === "forward" ? "Encaminhar" : "Responder"}</h2></div><button onClick={() => setCompondo(false)}>×</button></header><div className="cmp-from"><span>De</span><select value={rascunho.de} onChange={(e) => { const de = e.target.value; setRascunho((r) => ({ ...r, de })); if (de !== "corvia") setAnexos([]); }}>{contas.filter((c) => c.send_mail).map((c) => <option key={c.id} value={c.id}>{c.email_address} — {NOMES_PROVEDOR[c.provider]}{c.padrao ? " (padrão)" : ""}</option>)}</select></div><div className="cmp-field"><label>Para</label><input value={rascunho.para} onChange={(e) => setRascunho((r) => ({ ...r, para: e.target.value }))} placeholder="nome@exemplo.com" /><button onClick={() => setMostrarCopias((v) => !v)}>Cc/Cco</button></div>{mostrarCopias && <div className="cmp-copy-grid"><label>Cc<input value={rascunho.cc} onChange={(e) => setRascunho((r) => ({ ...r, cc: e.target.value }))} /></label><label>Cco<input value={rascunho.cco} onChange={(e) => setRascunho((r) => ({ ...r, cco: e.target.value }))} /></label></div>}<div className="cmp-field cmp-field--subject"><label>Assunto</label><input value={rascunho.assunto} onChange={(e) => setRascunho((r) => ({ ...r, assunto: e.target.value }))} /></div>{contatos.length > 0 && <div className="cmp-contacts"><span>Contatos</span>{contatos.slice(0, 8).map((c) => <button key={c.id} onClick={() => setRascunho((r) => ({ ...r, para: c.emails[0] || r.para }))}><b>{c.name}</b><small>{c.emails[0]}</small></button>)}</div>}<textarea className="cmp-compose-body" value={rascunho.corpo} onChange={(e) => setRascunho((r) => ({ ...r, corpo: e.target.value }))} placeholder="Escreva sua mensagem..." />{rascunho.de === "corvia" && <div className="cmp-compose-attachments"><label>▱ {enviandoAnexo ? "Anexando…" : "Anexar arquivo"}<input type="file" disabled={enviandoAnexo} onChange={(e) => { const f = e.target.files?.[0]; if (f) void anexar(f); e.currentTarget.value = ""; }} /></label>{anexos.map((a) => <span key={a.file_id}>{a.nome}{verificacoes[a.file_id]?.assinado && <em>✓ assinatura verificada</em>}<button onClick={() => setAnexos((xs) => xs.filter((x) => x.file_id !== a.file_id))}>×</button></span>)}</div>}<footer><button className="cmp-send" onClick={() => void enviar()} disabled={enviando}>{enviando ? "Enviando…" : "Enviar"}</button><span>{rascunho.de !== "corvia" ? "Envio pela conta externa selecionada" : "Envio pelo CorvIA Mail"}</span></footer></section></div>}
  </main>;
}
