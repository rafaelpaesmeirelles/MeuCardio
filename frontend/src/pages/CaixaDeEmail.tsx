import { useEffect, useMemo, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { apiEmail, ApiEmailError, tokenEmail } from "../lib/apiEmail";
import { Carregando, Vazio } from "../components/Estado";
import LogoCorviaMail from "../components/LogoCorviaMail";
import LogoProvedor from "../components/LogoProvedor";
import "../styles/corvia-mail.css";

type Pasta = {
  folderId?: string;
  id?: string;
  folderName?: string;
  name?: string;
  folderType?: string;
};

type Mensagem = {
  messageId?: string;
  id?: string;
  subject?: string;
  fromAddress?: string;
  sender?: string;
  toAddress?: string;
  ccAddress?: string;
  receivedTime?: string;
  sentDateInGMT?: string;
  date?: string;
  summary?: string;
  status?: string;
  status2?: string;
  priority?: string;
  hasAttachment?: number | string;
  folderId?: string;
  flagid?: string;
  flagId?: string;
};

type MensagemCompleta = Mensagem & { content?: string | null; htmlContent?: string | null };
type AnexoRecebido = {
  attachmentId?: string;
  attachId?: string;
  attachmentName?: string;
  fileName?: string;
  attachmentSize?: number;
  size?: number;
};
type AnexoEnviado = { file_id: string; nome: string };
type ContatoExterno = {
  id: number; name: string; emails: string[]; phones: string[];
  organization: string; provider: string; integration_id: number;
};
type ContaEmail = {
  id: string; provider: "corvia" | "google" | "microsoft";
  display_name: string; email_address: string; native: boolean;
  read_mail: boolean; send_mail: boolean;
};
type Filtro = "todas" | "nao_lidas" | "anexos" | "acompanhamento";
type AcaoResposta = "reply" | "replyall" | "forward";

type Rascunho = {
  modo: "nova" | AcaoResposta;
  messageId?: string;
  para: string;
  cc: string;
  cco: string;
  assunto: string;
  corpo: string;
};

const RASCUNHO_VAZIO: Rascunho = {
  modo: "nova",
  para: "",
  cc: "",
  cco: "",
  assunto: "",
  corpo: "",
};

const MODELOS = [
  {
    titulo: "Confirmar consulta",
    assunto: "Confirmação de consulta",
    corpo: "Olá,\n\nConfirmamos sua consulta conforme o agendamento realizado. Caso precise reagendar, responda a esta mensagem.\n\nAtenciosamente,",
  },
  {
    titulo: "Documentos recebidos",
    assunto: "Confirmação de recebimento de documentos",
    corpo: "Olá,\n\nConfirmamos o recebimento dos documentos enviados. Faremos a conferência administrativa e entraremos em contato se houver alguma pendência.\n\nAtenciosamente,",
  },
  {
    titulo: "Retorno administrativo",
    assunto: "Retorno do atendimento",
    corpo: "Olá,\n\nEntramos em contato para dar continuidade às providências administrativas do seu atendimento. Por favor, responda a esta mensagem quando puder.\n\nAtenciosamente,",
  },
  {
    titulo: "Lembrete de agendamento",
    assunto: "Lembrete de agendamento",
    corpo: "Olá,\n\nEste é um lembrete sobre seu próximo agendamento. Se precisar confirmar horário ou endereço, responda a esta mensagem.\n\nAtenciosamente,",
  },
];

const NOMES_PASTAS: Record<string, string> = {
  Inbox: "Entrada",
  Drafts: "Rascunhos",
  Templates: "Modelos",
  Snoozed: "Adiados",
  Sent: "Enviados",
  Spam: "Spam",
  Trash: "Lixeira",
  Outbox: "Saída",
  INBOX: "Entrada",
  DRAFT: "Rascunhos",
  SENT: "Enviados",
  SPAM: "Spam",
  TRASH: "Lixeira",
  inbox: "Entrada",
  drafts: "Rascunhos",
  sentitems: "Enviados",
  junkemail: "Spam",
  deleteditems: "Lixeira",
};

const MARCAS_PASTAS: Record<string, string> = {
  Inbox: "↓",
  Drafts: "◇",
  Templates: "▤",
  Snoozed: "◷",
  Sent: "↗",
  Spam: "!",
  Trash: "×",
  Outbox: "↑",
};

function idDaPasta(p: Pasta): string {
  return p.folderId ?? p.id ?? "";
}

function tipoDaPasta(p: Pasta): string {
  return p.folderType ?? p.folderName ?? p.name ?? "Pasta";
}

function nomeDaPasta(p: Pasta): string {
  const nome = p.folderName ?? p.name ?? p.folderType ?? "Pasta";
  return NOMES_PASTAS[p.folderType ?? nome] ?? nome;
}

function idDaMensagem(m: Mensagem): string {
  return m.messageId ?? m.id ?? "";
}

function remetente(m: Mensagem): string {
  return m.fromAddress ?? m.sender ?? "Remetente não informado";
}

function iniciais(m: Mensagem): string {
  const valor = remetente(m).split("@")[0].replace(/[^a-zA-ZÀ-ÿ0-9 ]/g, " ").trim();
  const partes = valor.split(/\s+/).filter(Boolean);
  return (partes.slice(0, 2).map((parte) => parte[0]).join("") || "E").toUpperCase();
}

function dataDaMensagem(m: Mensagem): Date | null {
  const bruto = m.receivedTime ?? m.sentDateInGMT ?? m.date;
  if (!bruto) return null;
  const numero = Number(bruto);
  const data = Number.isFinite(numero) && String(bruto).length > 8 ? new Date(numero) : new Date(bruto);
  return Number.isNaN(data.getTime()) ? null : data;
}

function dataMensagem(m: Mensagem, completa = false): string {
  const data = dataDaMensagem(m);
  if (!data) return "";
  const hoje = new Date();
  const mesmoDia = data.toDateString() === hoje.toDateString();
  if (!completa && mesmoDia) return data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  return data.toLocaleString("pt-BR", completa
    ? { dateStyle: "medium", timeStyle: "short" }
    : { day: "2-digit", month: "short" });
}

function ehNaoLida(m: Mensagem): boolean {
  const status = String(m.status ?? "").toLowerCase();
  return status === "0" || status === "unread" || status === "nao_lida";
}

function temAnexo(m: Mensagem): boolean {
  return Number(m.hasAttachment ?? 0) > 0;
}

function sinalizador(m: Mensagem): string {
  const valor = String(m.flagid ?? m.flagId ?? m.status2 ?? "").toLowerCase();
  return ["info", "important", "followup"].includes(valor) ? valor : "";
}

function estaEmAcompanhamento(m: Mensagem): boolean {
  return sinalizador(m) === "followup";
}

function pareceHtml(conteudo: string): boolean {
  return /<\s*(?:!doctype|html|head|body|meta|style|div|p|span|table|br|a|ul|ol|li)\b/i.test(conteudo);
}

function documentoSeguroDoEmail(html: string, permitirImagens: boolean): string {
  const parser = new DOMParser();
  const documento = parser.parseFromString(html, "text/html");
  documento
    .querySelectorAll("script, iframe, object, embed, form, input, button, textarea, select, link, meta, base, svg, math, video, audio")
    .forEach((elemento) => elemento.remove());

  documento.querySelectorAll("*").forEach((elemento) => {
    for (const atributo of Array.from(elemento.attributes)) {
      const nome = atributo.name.toLowerCase();
      if (nome.startsWith("on") || nome === "style" || nome === "srcset") {
        elemento.removeAttribute(atributo.name);
      }
    }
    if (elemento instanceof HTMLAnchorElement) {
      const href = elemento.getAttribute("href") ?? "";
      if (!/^(https?:|mailto:|tel:)/i.test(href)) elemento.removeAttribute("href");
      elemento.setAttribute("target", "_blank");
      elemento.setAttribute("rel", "noopener noreferrer nofollow");
    }
    if (elemento instanceof HTMLImageElement) {
      const src = elemento.getAttribute("src") ?? "";
      const permitido = permitirImagens
        ? /^(https?:|data:image\/)/i.test(src)
        : /^data:image\//i.test(src);
      if (!permitido) elemento.remove();
      else {
        elemento.removeAttribute("width");
        elemento.removeAttribute("height");
        elemento.setAttribute("loading", "lazy");
        elemento.setAttribute("referrerpolicy", "no-referrer");
      }
    }
  });

  const politicaImagens = permitirImagens ? "https: http: data:" : "data:";
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${politicaImagens}; style-src 'unsafe-inline'; font-src data:"><style>html{color:#26333b;background:#fff;font:15px/1.58 Inter,Arial,sans-serif}body{margin:0;padding:2px 4px;overflow-wrap:anywhere}a{color:#1c7293}img{max-width:100%;height:auto}table{max-width:100%;border-collapse:collapse}td,th{padding:.3rem;border:1px solid #e4e8ea}blockquote{margin-left:0;padding-left:.8rem;border-left:3px solid #e4e8ea;color:#55666f}</style></head><body>${documento.body.innerHTML}</body></html>`;
}

function CorpoDaMensagem({ mensagem }: { mensagem: MensagemCompleta }) {
  const [permitirImagens, setPermitirImagens] = useState(false);
  const conteudo = mensagem.content?.trim() || mensagem.htmlContent?.trim() || mensagem.summary?.trim() || "";
  const html = pareceHtml(conteudo);

  useEffect(() => setPermitirImagens(false), [mensagem.messageId, mensagem.id]);

  if (!conteudo) return <Vazio titulo="Mensagem sem conteúdo disponível" />;
  if (!html) return <div className="mail-leitura__texto">{conteudo}</div>;

  return (
    <>
      <div className="mail-privacidade" role="note">
        <span>HTML isolado por segurança. Imagens externas estão {permitirImagens ? "liberadas" : "bloqueadas"}.</span>
        <button type="button" onClick={() => setPermitirImagens((valor) => !valor)}>
          {permitirImagens ? "Bloquear imagens" : "Carregar imagens"}
        </button>
      </div>
      <iframe
        className="mail-leitura__html"
        sandbox="allow-popups allow-popups-to-escape-sandbox"
        srcDoc={documentoSeguroDoEmail(conteudo, permitirImagens)}
        title={`Conteúdo do e-mail: ${mensagem.subject ?? "sem assunto"}`}
      />
    </>
  );
}

function formatarTamanho(bytes?: number): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function RessalvaClinica() {
  return (
    <div className="mail-ressalva" role="note">
      <strong>Uso administrativo profissional.</strong>
      <span> Para dados clínicos identificáveis, utilize o Cofre do telediagnóstico ou o fluxo protegido de documentos.</span>
    </div>
  );
}

export default function CaixaDeEmail() {
  const navigate = useNavigate();
  const [semSessao, setSemSessao] = useState(!tokenEmail.get());
  const [enderecoAtual, setEnderecoAtual] = useState<string | null>(null);
  const [contasEmail, setContasEmail] = useState<ContaEmail[]>([]);
  const [contaEmailId, setContaEmailId] = useState("corvia");
  const [erro, setErro] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const [modo, setModo] = useState<"hoje" | "caixa">("hoje");

  const [pastas, setPastas] = useState<Pasta[] | null>(null);
  const [pastaAtual, setPastaAtual] = useState<string | undefined>(undefined);
  const [mensagens, setMensagens] = useState<Mensagem[] | null>(null);
  const [mensagemAberta, setMensagemAberta] = useState<MensagemCompleta | null>(null);
  const [anexosRecebidos, setAnexosRecebidos] = useState<AnexoRecebido[]>([]);
  const [busca, setBusca] = useState("");
  const [filtro, setFiltro] = useState<Filtro>("todas");
  const [selecionadas, setSelecionadas] = useState<Set<string>>(new Set());
  const [atualizando, setAtualizando] = useState(false);

  const [compondo, setCompondo] = useState(false);
  const [rascunho, setRascunho] = useState<Rascunho>(RASCUNHO_VAZIO);
  const [mostrarCopias, setMostrarCopias] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [anexos, setAnexos] = useState<AnexoEnviado[]>([]);
  const [enviandoAnexo, setEnviandoAnexo] = useState(false);
  const [contatos, setContatos] = useState<ContatoExterno[]>([]);
  const contaSelecionada = contasEmail.find((conta) => conta.id === contaEmailId);
  const contaExterna = contaSelecionada && !contaSelecionada.native ? contaSelecionada : null;
  const prefixoConta = contaExterna ? `/email/externas/${contaExterna.id}` : "/email";

  function mensagemDeErro(e: unknown, fallback: string): string {
    if (e instanceof ApiEmailError && e.status === 401) {
      setSemSessao(true);
      return "Sua sessão expirou. Entre novamente.";
    }
    return e instanceof ApiEmailError ? e.message : fallback;
  }

  function sair() {
    tokenEmail.clear();
    navigate("/corvia-mail");
  }

  async function carregarPastas() {
    try {
      const resultado = await apiEmail.get<Pasta[]>(`${prefixoConta}/pastas`);
      setPastas(resultado);
      const inbox = resultado.find((p) => tipoDaPasta(p).toLowerCase() === "inbox");
      setPastaAtual((atual) => atual ?? (inbox ? idDaPasta(inbox) : undefined));
    } catch (e) {
      setErro(mensagemDeErro(e, "Não foi possível carregar as pastas."));
      setPastas([]);
    }
  }

  async function carregarMensagens(pasta = pastaAtual) {
    setAtualizando(true);
    try {
      const params = new URLSearchParams({ limite: "100", inicio: "1" });
      if (pasta) params.set("pasta", pasta);
      const resultado = await apiEmail.get<Mensagem[]>(`${prefixoConta}/mensagens?${params}`);
      setMensagens(resultado);
      setSelecionadas(new Set());
    } catch (e) {
      setErro(mensagemDeErro(e, "Não foi possível carregar as mensagens."));
      setMensagens([]);
    } finally {
      setAtualizando(false);
    }
  }

  useEffect(() => {
    if (semSessao) return;
    apiEmail
      .get<{ email_address: string }>("/email/eu")
      .then(async (r) => {
        setEnderecoAtual(r.email_address);
        const contas = await apiEmail.get<ContaEmail[]>("/email/contas");
        setContasEmail(contas);
      })
      .catch((e) => setErro(mensagemDeErro(e, "Não foi possível carregar sua caixa de e-mail.")));
  }, [semSessao]);

  useEffect(() => {
    if (semSessao || !enderecoAtual) return;
    apiEmail.get<ContatoExterno[]>("/email/contatos?limite=100").then(setContatos).catch(() => setContatos([]));
  }, [semSessao, enderecoAtual]);

  useEffect(() => {
    if (semSessao || !enderecoAtual || pastas === null) return;
    setMensagemAberta(null);
    setAnexosRecebidos([]);
    void carregarMensagens(pastaAtual);
  }, [semSessao, enderecoAtual, pastaAtual, pastas, contaEmailId]);

  useEffect(() => {
    if (!enderecoAtual) return;
    setPastas(null);
    setPastaAtual(undefined);
    setMensagens(null);
    setMensagemAberta(null);
    setAnexosRecebidos([]);
    void carregarPastas();
  }, [contaEmailId, enderecoAtual]);

  const mensagensFiltradas = useMemo(() => {
    const termo = busca.trim().toLocaleLowerCase("pt-BR");
    return (mensagens ?? []).filter((mensagem) => {
      if (filtro === "nao_lidas" && !ehNaoLida(mensagem)) return false;
      if (filtro === "anexos" && !temAnexo(mensagem)) return false;
      if (filtro === "acompanhamento" && !estaEmAcompanhamento(mensagem)) return false;
      if (!termo) return true;
      return [remetente(mensagem), mensagem.subject, mensagem.summary, mensagem.toAddress]
        .filter(Boolean)
        .some((valor) => String(valor).toLocaleLowerCase("pt-BR").includes(termo));
    });
  }, [mensagens, busca, filtro]);

  const metricas = useMemo(() => {
    const hoje = new Date().toDateString();
    return {
      naoLidas: (mensagens ?? []).filter(ehNaoLida).length,
      hoje: (mensagens ?? []).filter((m) => dataDaMensagem(m)?.toDateString() === hoje).length,
      anexos: (mensagens ?? []).filter(temAnexo).length,
      acompanhamento: (mensagens ?? []).filter(estaEmAcompanhamento).length,
    };
  }, [mensagens]);

  async function abrirMensagem(mensagem: Mensagem) {
    const id = idDaMensagem(mensagem);
    if (!id) return;
    setErro(null);
    setModo("caixa");
    try {
      const completa = await apiEmail.get<MensagemCompleta>(`${prefixoConta}/mensagens/${encodeURIComponent(id)}`);
      setMensagemAberta(completa);
      setMensagens((lista) => (lista ?? []).map((item) =>
        idDaMensagem(item) === id ? { ...item, status: "1" } : item,
      ));
      if (temAnexo(completa) && !contaExterna) {
        const recebidos = await apiEmail
          .get<AnexoRecebido[]>(`/email/mensagens/${encodeURIComponent(id)}/anexos`)
          .catch(() => []);
        setAnexosRecebidos(recebidos);
      } else {
        setAnexosRecebidos([]);
      }
    } catch (e) {
      setErro(mensagemDeErro(e, "Não foi possível abrir a mensagem."));
    }
  }

  function alternarSelecao(id: string) {
    setSelecionadas((atual) => {
      const proximo = new Set(atual);
      if (proximo.has(id)) proximo.delete(id);
      else proximo.add(id);
      return proximo;
    });
  }

  async function agir(
    acao: "lida" | "nao_lida" | "mover" | "sinalizar",
    ids = Array.from(selecionadas),
    extras: { pasta_destino?: string; sinalizador?: string } = {},
  ) {
    if (!ids.length) return;
    setAtualizando(true);
    try {
      await apiEmail.put(`${prefixoConta}/mensagens/acoes`, { message_ids: ids, acao, ...extras });
      setMensagens((lista) => (lista ?? []).flatMap((mensagem) => {
        if (!ids.includes(idDaMensagem(mensagem))) return [mensagem];
        if (acao === "mover") return [];
        if (acao === "lida") return [{ ...mensagem, status: "1" }];
        if (acao === "nao_lida") return [{ ...mensagem, status: "0" }];
        return [{ ...mensagem, flagid: extras.sinalizador }];
      }));
      if (acao === "mover" && mensagemAberta && ids.includes(idDaMensagem(mensagemAberta))) {
        setMensagemAberta(null);
        setAnexosRecebidos([]);
      }
      setSelecionadas(new Set());
      setAviso("Ação aplicada com sucesso.");
    } catch (e) {
      setErro(mensagemDeErro(e, "Não foi possível atualizar as mensagens."));
    } finally {
      setAtualizando(false);
    }
  }

  async function excluir(ids = Array.from(selecionadas)) {
    if (!ids.length || !window.confirm(`Excluir ${ids.length === 1 ? "esta mensagem" : `${ids.length} mensagens`}?`)) return;
    setAtualizando(true);
    try {
      await Promise.all(ids.map((id) => apiEmail.delete(`${prefixoConta}/mensagens/${encodeURIComponent(id)}`)));
      setMensagens((lista) => (lista ?? []).filter((mensagem) => !ids.includes(idDaMensagem(mensagem))));
      if (mensagemAberta && ids.includes(idDaMensagem(mensagemAberta))) setMensagemAberta(null);
      setSelecionadas(new Set());
      setAviso("Mensagem removida.");
    } catch (e) {
      setErro(mensagemDeErro(e, "Não foi possível excluir a mensagem."));
    } finally {
      setAtualizando(false);
    }
  }

  function novaMensagem(modelo?: (typeof MODELOS)[number]) {
    setRascunho({
      ...RASCUNHO_VAZIO,
      assunto: modelo?.assunto ?? "",
      corpo: modelo?.corpo ?? "",
    });
    setAnexos([]);
    setMostrarCopias(false);
    setCompondo(true);
  }

  function responder(acao: AcaoResposta) {
    if (!mensagemAberta) return;
    const prefixo = acao === "forward" ? "Enc: " : "Re: ";
    const assunto = mensagemAberta.subject ?? "(sem assunto)";
    setRascunho({
      modo: acao,
      messageId: idDaMensagem(mensagemAberta),
      para: acao === "forward" ? "" : remetente(mensagemAberta),
      cc: "",
      cco: "",
      assunto: assunto.toLowerCase().startsWith(prefixo.toLowerCase()) ? assunto : `${prefixo}${assunto}`,
      corpo: "",
    });
    setAnexos([]);
    setMostrarCopias(acao === "replyall");
    setCompondo(true);
  }

  async function anexar(arquivo: File) {
    setEnviandoAnexo(true);
    try {
      const resultado = await apiEmail.uploadAnexo(arquivo);
      setAnexos((atuais) => [...atuais, resultado]);
    } catch (e) {
      setErro(mensagemDeErro(e, "Não foi possível anexar o arquivo."));
    } finally {
      setEnviandoAnexo(false);
    }
  }

  async function enviar() {
    setEnviando(true);
    try {
      if (rascunho.modo === "nova" || contaExterna) {
        await apiEmail.post(`${prefixoConta}/mensagens`, {
          para: rascunho.para,
          cc: rascunho.cc || null,
          cco: rascunho.cco || null,
          assunto: rascunho.assunto,
          corpo_html: rascunho.corpo,
          anexos: anexos.map((a) => a.file_id),
        });
      } else {
        await apiEmail.post(`/email/mensagens/${encodeURIComponent(rascunho.messageId ?? "")}/responder`, {
          acao: rascunho.modo,
          para: rascunho.modo === "forward" ? rascunho.para : null,
          cc: rascunho.cc || null,
          cco: rascunho.cco || null,
          assunto: rascunho.assunto,
          conteudo: rascunho.corpo,
          anexos: anexos.map((a) => a.file_id),
        });
      }
      setCompondo(false);
      setRascunho(RASCUNHO_VAZIO);
      setAnexos([]);
      setAviso(rascunho.modo === "nova" ? "Mensagem enviada." : "Resposta enviada.");
    } catch (e) {
      setErro(mensagemDeErro(e, "Não foi possível enviar a mensagem."));
    } finally {
      setEnviando(false);
    }
  }

  if (semSessao) return <Navigate to="/corvia-mail" replace />;
  if (!enderecoAtual) return <div className="mail-carregando"><LogoCorviaMail tamanho="compacto" /><Carregando /></div>;

  const pastaSelecionada = pastas?.find((p) => idDaPasta(p) === pastaAtual);
  const todosVisiveisSelecionados = mensagensFiltradas.length > 0
    && mensagensFiltradas.every((m) => selecionadas.has(idDaMensagem(m)));

  return (
    <main className="mail-app">
      <header className="mail-topo">
        <div className="mail-topo__identidade">
          <LogoCorviaMail tamanho="compacto" />
          <div>
            <p className="eyebrow">Central de comunicação profissional</p>
            <div className="mail-conta-ativa">
              {contaExterna && contaExterna.provider !== "corvia" && <LogoProvedor provedor={contaExterna.provider} />}
              <select value={contaEmailId} onChange={(event) => setContaEmailId(event.target.value)} aria-label="Conta de e-mail ativa">
                {contasEmail.map((conta) => <option key={conta.id} value={conta.id}>{conta.email_address}</option>)}
              </select>
            </div>
          </div>
        </div>
        <div className="mail-topo__acoes">
          <button className="botao" onClick={() => novaMensagem()}>+ Escrever</button>
          <button className="botao botao--secundario" onClick={() => void carregarMensagens()} disabled={atualizando}>
            {atualizando ? "Atualizando…" : "Atualizar"}
          </button>
          <button className="mail-link" onClick={sair}>Sair</button>
        </div>
      </header>

      <RessalvaClinica />

      <nav className="mail-abas" aria-label="Seções do Corvia Mail">
        <button className={modo === "hoje" ? "ativo" : ""} onClick={() => setModo("hoje")}>Hoje</button>
        <button className={modo === "caixa" ? "ativo" : ""} onClick={() => setModo("caixa")}>Caixa de entrada</button>
      </nav>

      {erro && (
        <div className="mail-alerta mail-alerta--erro" role="alert">
          <span>{erro}</span><button onClick={() => setErro(null)} aria-label="Fechar erro">×</button>
        </div>
      )}
      {aviso && (
        <div className="mail-alerta mail-alerta--sucesso" role="status">
          <span>{aviso}</span><button onClick={() => setAviso(null)} aria-label="Fechar aviso">×</button>
        </div>
      )}

      {modo === "hoje" ? (
        <section className="mail-dashboard" aria-label="Painel do Corvia Mail">
          <div className="mail-dashboard__boas-vindas">
            <div>
              <p className="eyebrow">Visão do dia</p>
              <h1>Sua comunicação profissional, organizada para agir.</h1>
              <p>Priorize respostas, acompanhe pendências e use modelos administrativos sem misturar dados clínicos sensíveis.</p>
            </div>
            <button className="botao" onClick={() => novaMensagem()}>Escrever mensagem</button>
          </div>

          <div className="mail-metricas">
            <button onClick={() => { setFiltro("nao_lidas"); setModo("caixa"); }}>
              <span>Não lidas</span><strong>{metricas.naoLidas}</strong><small>pedem triagem</small>
            </button>
            <button onClick={() => { setFiltro("todas"); setModo("caixa"); }}>
              <span>Recebidas hoje</span><strong>{metricas.hoje}</strong><small>novas conversas</small>
            </button>
            <button onClick={() => { setFiltro("acompanhamento"); setModo("caixa"); }}>
              <span>Acompanhar</span><strong>{metricas.acompanhamento}</strong><small>itens sinalizados</small>
            </button>
            <button onClick={() => { setFiltro("anexos"); setModo("caixa"); }}>
              <span>Com anexos</span><strong>{metricas.anexos}</strong><small>documentos recebidos</small>
            </button>
          </div>

          <div className="mail-dashboard__grade">
            <section className="mail-painel-card mail-painel-card--prioridades">
              <div className="mail-painel-card__topo">
                <div><p className="eyebrow">Prioridades</p><h2>Mensagens para revisar</h2></div>
                <button onClick={() => setModo("caixa")}>Ver todas</button>
              </div>
              {(mensagens ?? []).filter(ehNaoLida).slice(0, 5).length === 0 ? (
                <Vazio titulo="Nenhuma mensagem não lida" />
              ) : (
                (mensagens ?? []).filter(ehNaoLida).slice(0, 5).map((m) => (
                  <button className="mail-prioridade" key={idDaMensagem(m)} onClick={() => void abrirMensagem(m)}>
                    <span className="mail-avatar">{iniciais(m)}</span>
                    <span><strong>{m.subject ?? "(sem assunto)"}</strong><small>{remetente(m)}</small></span>
                    <time>{dataMensagem(m)}</time>
                  </button>
                ))
              )}
            </section>

            <section className="mail-painel-card">
              <p className="eyebrow">Modelos rápidos</p>
              <h2>Comunicação de consultório</h2>
              <div className="mail-modelos">
                {MODELOS.map((modelo) => (
                  <button key={modelo.titulo} onClick={() => novaMensagem(modelo)}>
                    <span>+</span>{modelo.titulo}
                  </button>
                ))}
              </div>
            </section>

            <section className="mail-painel-card mail-painel-card--contatos">
              <p className="eyebrow">Contatos conectados</p>
              <h2>Google, Microsoft e Apple</h2>
              {contatos.length ? contatos.slice(0, 5).map((contato) => <button key={contato.id} onClick={() => { novaMensagem(); setRascunho({ ...RASCUNHO_VAZIO, para: contato.emails[0] || "" }); }}><span className="mail-avatar">{contato.name.slice(0, 1).toUpperCase()}</span><span><strong>{contato.name}</strong><small>{contato.emails[0]}{contato.organization ? ` · ${contato.organization}` : ""}</small></span></button>) : <div className="mail-contatos-vazio"><span>Nenhum contato sincronizado.</span><Link to="/agenda">Conectar uma conta na Agenda</Link></div>}
            </section>

            <section className="mail-painel-card mail-painel-card--integracoes">
              <p className="eyebrow">Ecossistema Corvia</p>
              <h2>Continue o trabalho</h2>
              <Link to="/agenda"><strong>Agenda</strong><span>Consulte compromissos e organize retornos.</span></Link>
              <Link to="/material-paciente"><strong>Material do paciente</strong><span>Envie conteúdo revisado pelo fluxo apropriado.</span></Link>
              <Link to="/telediagnostico"><strong>Cofre protegido</strong><span>Use para informações clínicas identificáveis.</span></Link>
            </section>
          </div>
        </section>
      ) : (
        <section className={`mail-workspace ${mensagemAberta ? "mail-workspace--lendo" : ""}`}>
          <aside className="mail-pastas" aria-label="Pastas">
            <div className="mail-pastas__titulo"><span>Pastas</span><small>{pastas?.length ?? 0}</small></div>
            {pastas === null ? <Carregando /> : pastas.map((pasta) => {
              const tipo = tipoDaPasta(pasta);
              return (
                <button
                  key={idDaPasta(pasta)}
                  className={pastaAtual === idDaPasta(pasta) ? "ativo" : ""}
                  onClick={() => setPastaAtual(idDaPasta(pasta))}
                >
                  <span className="mail-pasta__icone" aria-hidden="true">{MARCAS_PASTAS[tipo] ?? "·"}</span>
                  <span>{nomeDaPasta(pasta)}</span>
                </button>
              );
            })}
            <div className="mail-pastas__atalhos">
              <Link to="/agenda">Abrir Agenda</Link>
              <Link to="/material-paciente">Material do paciente</Link>
            </div>
          </aside>

          <section className="mail-lista" aria-label="Lista de mensagens">
            <div className="mail-lista__topo">
              <div>
                <p className="eyebrow">{pastaSelecionada ? nomeDaPasta(pastaSelecionada) : "Mensagens"}</p>
                <h2>{mensagens?.length ?? 0} mensagens</h2>
              </div>
              {atualizando && <span className="mail-lista__sincronizando">Sincronizando…</span>}
            </div>
            <label className="mail-busca">
              <span aria-hidden="true">⌕</span>
              <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Buscar remetente, assunto ou texto" />
            </label>
            <div className="mail-filtros" role="group" aria-label="Filtros de mensagens">
              {([
                ["todas", "Todas"],
                ["nao_lidas", "Não lidas"],
                ["anexos", "Anexos"],
                ["acompanhamento", "Acompanhar"],
              ] as [Filtro, string][]).map(([valor, rotulo]) => (
                <button key={valor} className={filtro === valor ? "ativo" : ""} onClick={() => setFiltro(valor)}>{rotulo}</button>
              ))}
            </div>

            <div className="mail-selecao">
              <label>
                <input
                  type="checkbox"
                  checked={todosVisiveisSelecionados}
                  onChange={() => setSelecionadas(todosVisiveisSelecionados
                    ? new Set()
                    : new Set(mensagensFiltradas.map(idDaMensagem)))}
                />
                <span>{selecionadas.size ? `${selecionadas.size} selecionadas` : "Selecionar todas"}</span>
              </label>
            </div>

            {selecionadas.size > 0 && (
              <div className="mail-acoes-lote" role="toolbar" aria-label="Ações em lote">
                <button onClick={() => void agir("lida")}>Marcar lidas</button>
                <button onClick={() => void agir("nao_lida")}>Não lidas</button>
                {!contaExterna && <button onClick={() => void agir("sinalizar", undefined, { sinalizador: "followup" })}>Acompanhar</button>}
                <select
                  aria-label="Mover mensagens para pasta"
                  defaultValue=""
                  onChange={(e) => {
                    if (e.target.value) void agir("mover", undefined, { pasta_destino: e.target.value });
                    e.target.value = "";
                  }}
                >
                  <option value="">Mover para…</option>
                  {(pastas ?? []).filter((p) => idDaPasta(p) !== pastaAtual).map((p) => (
                    <option key={idDaPasta(p)} value={idDaPasta(p)}>{nomeDaPasta(p)}</option>
                  ))}
                </select>
                <button className="perigo" onClick={() => void excluir()}>Excluir</button>
              </div>
            )}

            <div className="mail-lista__rolagem">
              {mensagens === null ? (
                <div className="mail-estado"><Carregando /></div>
              ) : mensagensFiltradas.length === 0 ? (
                <div className="mail-estado"><Vazio titulo="Nenhuma mensagem neste filtro" /></div>
              ) : mensagensFiltradas.map((m) => {
                const id = idDaMensagem(m);
                return (
                  <article className={`mail-item ${ehNaoLida(m) ? "mail-item--nao-lida" : ""} ${mensagemAberta && idDaMensagem(mensagemAberta) === id ? "mail-item--ativo" : ""}`} key={id}>
                    <label className="mail-item__check" aria-label="Selecionar mensagem">
                      <input type="checkbox" checked={selecionadas.has(id)} onChange={() => alternarSelecao(id)} />
                    </label>
                    <button className="mail-item__abrir" onClick={() => void abrirMensagem(m)}>
                      <span className="mail-avatar">{iniciais(m)}</span>
                      <span className="mail-item__conteudo">
                        <span className="mail-item__linha"><strong>{remetente(m)}</strong><time>{dataMensagem(m)}</time></span>
                        <span className="mail-item__assunto">{m.subject ?? "(sem assunto)"}</span>
                        <span className="mail-item__resumo">{m.summary ?? "Sem prévia disponível"}</span>
                        <span className="mail-item__marcas">
                          {temAnexo(m) && <small>▱ Anexo</small>}
                          {estaEmAcompanhamento(m) && <small>⚑ Acompanhar</small>}
                        </span>
                      </span>
                    </button>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="mail-leitura" aria-label="Leitura da mensagem">
            {!mensagemAberta ? (
              <div className="mail-leitura__vazio">
                <span aria-hidden="true">✉</span>
                <h2>Selecione uma mensagem</h2>
                <p>Leia, responda, encaminhe e organize sem sair do Corvia.</p>
              </div>
            ) : (
              <>
                <button className="mail-leitura__voltar" onClick={() => setMensagemAberta(null)}>← Voltar às mensagens</button>
                <div className="mail-leitura__toolbar" role="toolbar" aria-label="Ações da mensagem">
                  <button onClick={() => responder("reply")}>Responder</button>
                  <button onClick={() => responder("replyall")}>Responder a todos</button>
                  <button onClick={() => responder("forward")}>Encaminhar</button>
                  <button onClick={() => void agir("nao_lida", [idDaMensagem(mensagemAberta)])}>Marcar não lida</button>
                  {!contaExterna && <button onClick={() => void agir("sinalizar", [idDaMensagem(mensagemAberta)], { sinalizador: "followup" })}>⚑ Acompanhar</button>}
                  <select
                    aria-label="Mover mensagem"
                    defaultValue=""
                    onChange={(e) => {
                      if (e.target.value) void agir("mover", [idDaMensagem(mensagemAberta)], { pasta_destino: e.target.value });
                      e.target.value = "";
                    }}
                  >
                    <option value="">Mover…</option>
                    {(pastas ?? []).filter((p) => idDaPasta(p) !== pastaAtual).map((p) => (
                      <option key={idDaPasta(p)} value={idDaPasta(p)}>{nomeDaPasta(p)}</option>
                    ))}
                  </select>
                  <button className="perigo" onClick={() => void excluir([idDaMensagem(mensagemAberta)])}>Excluir</button>
                </div>

                <header className="mail-leitura__cabecalho">
                  <p className="eyebrow">Mensagem</p>
                  <h2>{mensagemAberta.subject ?? "(sem assunto)"}</h2>
                  <div className="mail-leitura__remetente">
                    <span className="mail-avatar mail-avatar--grande">{iniciais(mensagemAberta)}</span>
                    <span><strong>{remetente(mensagemAberta)}</strong><small>Para: {mensagemAberta.toAddress ?? contaSelecionada?.email_address ?? enderecoAtual}</small></span>
                    <time>{dataMensagem(mensagemAberta, true)}</time>
                  </div>
                </header>

                {anexosRecebidos.length > 0 && (
                  <div className="mail-anexos-recebidos">
                    <strong>{anexosRecebidos.length} {anexosRecebidos.length === 1 ? "anexo" : "anexos"}</strong>
                    <div>
                      {anexosRecebidos.map((anexo) => {
                        const id = anexo.attachmentId ?? anexo.attachId ?? "";
                        const nome = anexo.attachmentName ?? anexo.fileName ?? "anexo";
                        return (
                          <button key={id} onClick={() => void apiEmail.baixarAnexo(idDaMensagem(mensagemAberta), id, nome)}>
                            <span>▱</span><span>{nome}<small>{formatarTamanho(anexo.attachmentSize ?? anexo.size)}</small></span><b>Baixar</b>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                <div className="mail-leitura__corpo"><CorpoDaMensagem mensagem={mensagemAberta} /></div>

                <div className="mail-leitura__rodape">
                  <button className="botao" onClick={() => responder("reply")}>↩ Responder</button>
                  <button className="botao botao--secundario" onClick={() => responder("forward")}>Encaminhar</button>
                </div>
              </>
            )}
          </section>
        </section>
      )}

      {compondo && (
        <div className="mail-modal" role="dialog" aria-modal="true" aria-labelledby="mail-compositor-titulo">
          <button className="mail-modal__fundo" aria-label="Fechar composição" onClick={() => setCompondo(false)} />
          <section className="mail-compositor">
            <header>
              <div>
                <p className="eyebrow">{rascunho.modo === "nova" ? "Nova comunicação" : "Continuar conversa"}</p>
                <h2 id="mail-compositor-titulo">
                  {rascunho.modo === "nova" ? "Escrever mensagem" : rascunho.modo === "forward" ? "Encaminhar" : "Responder"}
                </h2>
              </div>
              <button onClick={() => setCompondo(false)} aria-label="Fechar">×</button>
            </header>
            {(rascunho.modo === "nova" || rascunho.modo === "forward") && (
              <label>Para<input type="email" list="corvia-mail-contatos" value={rascunho.para} onChange={(e) => setRascunho({ ...rascunho, para: e.target.value })} /><datalist id="corvia-mail-contatos">{contatos.flatMap((contato) => contato.emails.map((email) => <option key={`${contato.id}-${email}`} value={email}>{contato.name}{contato.organization ? ` · ${contato.organization}` : ""}</option>))}</datalist></label>
            )}
            {(rascunho.modo === "nova" || rascunho.modo === "forward") && contatos.length > 0 && <div className="mail-compositor__contatos"><span>Contatos:</span>{contatos.filter((contato) => !rascunho.para || `${contato.name} ${contato.emails.join(" ")}`.toLocaleLowerCase("pt-BR").includes(rascunho.para.toLocaleLowerCase("pt-BR"))).slice(0, 6).map((contato) => <button key={contato.id} type="button" onClick={() => setRascunho({ ...rascunho, para: contato.emails[0] || "" })}>{contato.name}<small>{contato.emails[0]}</small></button>)}</div>}
            <button className="mail-compositor__copias" onClick={() => setMostrarCopias((valor) => !valor)}>
              {mostrarCopias ? "Ocultar Cc/Cco" : "Adicionar Cc/Cco"}
            </button>
            {mostrarCopias && (
              <div className="mail-compositor__grade">
                <label>Cc<input value={rascunho.cc} onChange={(e) => setRascunho({ ...rascunho, cc: e.target.value })} /></label>
                <label>Cco<input value={rascunho.cco} onChange={(e) => setRascunho({ ...rascunho, cco: e.target.value })} /></label>
              </div>
            )}
            <label>Assunto<input value={rascunho.assunto} onChange={(e) => setRascunho({ ...rascunho, assunto: e.target.value })} /></label>
            <label>Mensagem<textarea rows={11} value={rascunho.corpo} onChange={(e) => setRascunho({ ...rascunho, corpo: e.target.value })} /></label>
            <div className="mail-compositor__modelos">
              <span>Inserir modelo:</span>
              {MODELOS.map((modelo) => (
                <button key={modelo.titulo} onClick={() => setRascunho({ ...rascunho, assunto: modelo.assunto, corpo: modelo.corpo })}>{modelo.titulo}</button>
              ))}
            </div>
            {!contaExterna ? <div className="mail-compositor__anexos">
              <label className="botao botao--secundario">
                {enviandoAnexo ? "Enviando anexo…" : "▱ Anexar arquivo"}
                <input
                  type="file"
                  disabled={enviandoAnexo}
                  onChange={(e) => {
                    const arquivo = e.target.files?.[0];
                    if (arquivo) void anexar(arquivo);
                    e.target.value = "";
                  }}
                />
              </label>
              {anexos.map((anexo) => (
                <span key={anexo.file_id}>{anexo.nome}<button onClick={() => setAnexos((lista) => lista.filter((item) => item.file_id !== anexo.file_id))}>×</button></span>
              ))}
            </div> : <p className="mail-conta-nota">A conta externa envia pelo provedor original. Anexos externos serão liberados após a validação específica de segurança do Google e da Microsoft.</p>}
            <footer>
              <button className="botao" onClick={() => void enviar()} disabled={enviando || enviandoAnexo || !rascunho.assunto || !rascunho.corpo || ((rascunho.modo === "nova" || rascunho.modo === "forward") && !rascunho.para)}>
                {enviando ? "Enviando…" : rascunho.modo === "forward" ? "Encaminhar" : "Enviar"}
              </button>
              <button className="botao botao--secundario" onClick={() => setCompondo(false)}>Cancelar</button>
              <small>Não inclua dados clínicos identificáveis nesta mensagem.</small>
            </footer>
          </section>
        </div>
      )}
    </main>
  );
}
