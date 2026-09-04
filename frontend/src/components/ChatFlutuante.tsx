/** CorvIA Chat — widget flutuante de conversa entre assinantes.
 *
 *  Fecha a Tarefa aberta em 31/07/2026: o backend (`app/api/chat.py`) já estava
 *  pronto e testado de ponta a ponta, e faltava toda a interface.
 *
 *  Decisões que valem registro, porque não são óbvias no código:
 *
 *  - **O envio vai por HTTP, não pelo WebSocket.** O socket é só para RECEBER
 *    em tempo real. É assim que o backend foi desenhado: `POST /mensagens/{id}`
 *    persiste, valida e então ecoa pelo socket para o destinatário e para as
 *    outras abas do próprio remetente. Mandar pelo socket exigiria duplicar
 *    validação e persistência do outro lado.
 *
 *  - **O socket só abre quando o widget é aberto pela primeira vez.** Manter uma
 *    conexão viva em toda navegação, para todo assinante, custa uma conexão por
 *    aba no servidor sem que a maioria vá conversar. O contador de não lidas,
 *    que é o que precisa aparecer sem abrir nada, vem de um GET barato.
 *
 *  - **O eco da própria mensagem chega pelo socket.** Por isso a lista de
 *    mensagens deduplica por id: sem isso, quem envia vê a mensagem duas vezes
 *    (uma da resposta do POST, outra do eco).
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { api, token } from "../lib/api";
import { useAuth } from "../lib/auth";
import LogoChat, { IconeChat } from "./LogoChat";

type Conversa = {
  user_id: number;
  full_name: string;
  photo_url: string | null;
  ultima_mensagem: string;
  ultima_em: string;
  de_mim: boolean;
  nao_lidas: number;
};

type UsuarioBusca = {
  id: number;
  full_name: string;
  email: string;
  council_name: string | null;
  council_number: string | null;
  council_state: string | null;
  specialty: string | null;
  photo_url: string | null;
};

type Suporte = UsuarioBusca & { online: boolean };

type Mensagem = {
  id: number;
  sender_id: number;
  recipient_id: number;
  body: string;
  created_at: string;
  read_at?: string | null;
};

type Vista = "lista" | "busca" | "conversa";

function horaCurta(iso: string) {
  const d = new Date(iso);
  const hoje = new Date();
  const mesmoDia = d.toDateString() === hoje.toDateString();
  return mesmoDia
    ? d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })
    : d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
}

function Avatar({ nome, foto, tamanho = 38 }: { nome: string; foto: string | null; tamanho?: number }) {
  const iniciais = nome.split(" ").filter(Boolean).slice(0, 2).map((p) => p[0]?.toUpperCase()).join("");
  if (foto) {
    return (
      <img
        src={foto}
        alt=""
        style={{ width: tamanho, height: tamanho, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }}
      />
    );
  }
  return (
    <span
      aria-hidden="true"
      style={{
        width: tamanho, height: tamanho, borderRadius: "50%", flexShrink: 0,
        background: "var(--acento)", color: "#fff", display: "flex",
        alignItems: "center", justifyContent: "center",
        fontSize: tamanho * 0.38, fontWeight: 700,
      }}
    >
      {iniciais || "?"}
    </span>
  );
}

export default function ChatFlutuante() {
  const { usuario } = useAuth();
  const [aberto, setAberto] = useState(false);
  const [vista, setVista] = useState<Vista>("lista");
  const [naoLidas, setNaoLidas] = useState(0);
  const [conversas, setConversas] = useState<Conversa[]>([]);
  const [suporte, setSuporte] = useState<Suporte | null>(null);
  const [termo, setTermo] = useState("");
  const [resultados, setResultados] = useState<UsuarioBusca[] | null>(null);
  const [buscando, setBuscando] = useState(false);
  // 07/08/2026, pedido do Rafael: toda ferramenta de busca do site precisa de
  // pelo menos duas formas de refinar. O backend já suportava filtro por
  // órgão de classe (`GET /chat/buscar-usuarios?conselho=...`) e já tinha a
  // rota `GET /chat/orgaos-de-classe` para popular um seletor — só faltava a
  // tela usar os dois. Sem eles, "Procurar outro profissional" tinha um único
  // campo de texto livre.
  const [conselho, setConselho] = useState("");
  const [orgaosDeClasse, setOrgaosDeClasse] = useState<string[]>([]);
  const [ativo, setAtivo] = useState<{ id: number; nome: string; foto: string | null } | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [texto, setTexto] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  const wsRef = useRef<WebSocket | null>(null);
  const fimRef = useRef<HTMLDivElement | null>(null);
  // Lido dentro do handler do socket, que é criado uma vez e não deve
  // reconstruir a cada troca de conversa.
  const ativoRef = useRef<number | null>(null);
  ativoRef.current = ativo?.id ?? null;

  const carregarNaoLidas = useCallback(() => {
    api.get<{ total: number }>("/chat/nao-lidas").then((r) => setNaoLidas(r.total)).catch(() => {});
  }, []);

  const carregarConversas = useCallback(() => {
    api.get<Conversa[]>("/chat/conversas").then(setConversas).catch(() => {});
  }, []);

  // Badge de não lidas: aparece sem abrir o widget, então é o único trabalho
  // feito de forma recorrente enquanto o chat está fechado.
  useEffect(() => {
    if (!usuario) return;
    carregarNaoLidas();
    const t = setInterval(carregarNaoLidas, 60000);
    const aoRetomar = () => carregarNaoLidas();
    const aoMudarVisibilidade = () => {
      if (document.visibilityState === "visible") carregarNaoLidas();
    };
    window.addEventListener("focus", aoRetomar);
    document.addEventListener("visibilitychange", aoMudarVisibilidade);
    return () => {
      clearInterval(t);
      window.removeEventListener("focus", aoRetomar);
      document.removeEventListener("visibilitychange", aoMudarVisibilidade);
    };
  }, [usuario, carregarNaoLidas]);

  // Socket: abre na primeira vez que o widget é aberto e fica vivo daí em diante.
  useEffect(() => {
    if (!aberto || wsRef.current) return;
    const t = token.get();
    if (!t) return;
    const protocolo = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${protocolo}://${window.location.host}/api/chat/ws?token=${encodeURIComponent(t)}`);
    wsRef.current = ws;

    ws.onmessage = (ev) => {
      let dados: any;
      try { dados = JSON.parse(ev.data); } catch { return; }
      if (dados?.tipo !== "mensagem") return;

      const meu = usuario?.id;
      const outro = dados.sender_id === meu ? dados.recipient_id : dados.sender_id;

      if (ativoRef.current === outro) {
        setMensagens((atual) =>
          atual.some((m) => m.id === dados.id) ? atual : [...atual, dados as Mensagem]
        );
        if (dados.sender_id !== meu) {
          api.post(`/chat/mensagens/${outro}/marcar-lidas`).then(carregarNaoLidas).catch(() => {});
        }
      } else if (dados.sender_id !== meu) {
        carregarNaoLidas();
      }
      carregarConversas();
    };

    // Keepalive: o handler do backend fica em `receive_text()`, então um ping
    // periódico é o que faz uma desconexão silenciosa aparecer de imediato.
    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 30000);

    return () => {
      clearInterval(ping);
      // Não fecha o socket aqui: o efeito roda de novo quando `aberto` muda,
      // e fechar a cada fechamento do painel derrubaria a entrega em tempo real
      // de quem só minimizou a janela.
    };
  }, [aberto, usuario, carregarNaoLidas, carregarConversas]);

  // Fecha o socket de vez quando o componente sai (logout, troca de rota raiz).
  useEffect(() => () => { wsRef.current?.close(); wsRef.current = null; }, []);

  useEffect(() => {
    if (!aberto) return;
    carregarConversas();
    carregarNaoLidas();
    api.get<Suporte | null>("/chat/suporte").then(setSuporte).catch(() => {});
    api.get<string[]>("/chat/orgaos-de-classe").then(setOrgaosDeClasse).catch(() => {});
  }, [aberto, carregarConversas, carregarNaoLidas]);

  useEffect(() => {
    fimRef.current?.scrollIntoView({ block: "end" });
  }, [mensagens, vista]);

  async function abrirConversa(id: number, nome: string, foto: string | null) {
    setAtivo({ id, nome, foto });
    setVista("conversa");
    setErro("");
    setMensagens([]);
    try {
      const hist = await api.get<Mensagem[]>(`/chat/mensagens/${id}`);
      setMensagens(hist);
      await api.post(`/chat/mensagens/${id}/marcar-lidas`);
      carregarNaoLidas();
      carregarConversas();
    } catch {
      setErro("Não foi possível abrir a conversa.");
    }
  }

  async function buscar(e: React.FormEvent) {
    e.preventDefault();
    const q = termo.trim();
    if (q.length < 2) return;
    setBuscando(true);
    setErro("");
    try {
      const params = new URLSearchParams({ q });
      if (conselho) params.set("conselho", conselho);
      setResultados(await api.get<UsuarioBusca[]>(`/chat/buscar-usuarios?${params}`));
    } catch {
      setErro("A busca falhou. Tente de novo.");
    } finally {
      setBuscando(false);
    }
  }

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    const corpo = texto.trim();
    if (!corpo || !ativo || enviando) return;
    setEnviando(true);
    setErro("");
    try {
      const msg = await api.post<Mensagem>(`/chat/mensagens/${ativo.id}`, { body: corpo });
      // Dedup por id: o eco do socket traz a mesma mensagem.
      setMensagens((atual) => (atual.some((m) => m.id === msg.id) ? atual : [...atual, msg]));
      setTexto("");
      carregarConversas();
    } catch (err: any) {
      setErro(err?.message ?? "Não foi possível enviar.");
    } finally {
      setEnviando(false);
    }
  }

  if (!usuario) return null;

  const CORPO_ALTURA = 420;

  return (
    <>
      {/* Acesso ao chat deliberadamente não circular: o rótulo e a geometria de
          conversa evitam confundi-lo com o atalho clínico de Emergência. */}
      {!aberto && (
        <button
          className="corvia-chat-launch"
          onClick={() => setAberto(true)}
          aria-label={naoLidas > 0 ? `Abrir o CorvIA Chat, ${naoLidas} mensagens não lidas` : "Abrir o CorvIA Chat"}
          title="CorvIA Chat"
        >
          <IconeChat tamanho={24} variante="sobre-navy" />
          <span className="corvia-chat-launch__label">Chat</span>
          {naoLidas > 0 && (
            <span className="corvia-chat-launch__badge" aria-live="polite">
              {naoLidas > 99 ? "99+" : naoLidas}
            </span>
          )}
        </button>
      )}

      {aberto && (
        <section
          className="corvia-chat-panel"
          aria-label="CorvIA Chat"
          style={{
            position: "fixed", right: 18, bottom: 78, zIndex: 1200,
            width: "min(380px, calc(100vw - 36px))",
            background: "var(--fundo, #fff)", borderRadius: 12,
            border: "1px solid var(--linha, #dcd8d2)",
            boxShadow: "0 10px 40px rgba(11,46,69,.28)",
            display: "flex", flexDirection: "column", overflow: "hidden",
          }}
        >
          <header
            style={{
              background: "var(--primaria)", color: "#fff", padding: ".6rem .75rem",
              display: "flex", alignItems: "center", gap: ".5rem",
            }}
          >
            {vista !== "lista" && (
              <button
                onClick={() => { setVista("lista"); setAtivo(null); setResultados(null); setTermo(""); setConselho(""); }}
                aria-label="Voltar"
                style={{ background: "none", border: "none", color: "#fff", cursor: "pointer", fontSize: "1.1rem", padding: "0 .2rem" }}
              >
                ‹
              </button>
            )}
            <span style={{ display: "flex", alignItems: "center", gap: ".45rem", flex: 1, minWidth: 0 }}>
              <IconeChat tamanho={24} variante="sobre-navy" />
              <strong style={{ fontSize: ".98rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {vista === "conversa" && ativo ? ativo.nome : "CorvIA Chat"}
              </strong>
            </span>
            <button
              onClick={() => setAberto(false)}
              aria-label="Fechar o chat"
              style={{ background: "none", border: "none", color: "#fff", cursor: "pointer", fontSize: "1.05rem", padding: "0 .2rem" }}
            >
              ✕
            </button>
          </header>

          {erro && (
            <p style={{ margin: 0, padding: ".5rem .75rem", background: "#fdecea", color: "#8a1c12", fontSize: ".85rem" }}>
              {erro}
            </p>
          )}

          {/* ---------------------------------------------------- LISTA -- */}
          {vista === "lista" && (
            <div style={{ height: CORPO_ALTURA, overflowY: "auto" }}>
              {suporte && (
                <button
                  onClick={() => abrirConversa(suporte.id, suporte.full_name, suporte.photo_url)}
                  style={{
                    width: "100%", textAlign: "left", cursor: "pointer",
                    display: "flex", gap: ".65rem", alignItems: "center",
                    padding: ".75rem", border: "none", borderBottom: "1px solid var(--linha, #e6e2dc)",
                    background: "var(--acento-suave, #eef5f8)",
                  }}
                >
                  <Avatar nome={suporte.full_name} foto={suporte.photo_url} tamanho={40} />
                  <span style={{ flex: 1, minWidth: 0 }}>
                    <strong style={{ display: "block", fontSize: ".92rem", color: "var(--primaria)" }}>
                      Fale com {suporte.full_name}
                    </strong>
                    <span style={{ fontSize: ".8rem", color: "var(--texto-suave, #5a6b78)" }}>
                      {suporte.online ? "Online agora" : "Responde assim que puder"}
                    </span>
                  </span>
                  <span aria-hidden="true" style={{ color: "var(--acento)" }}>›</span>
                </button>
              )}

              <button
                onClick={() => { setVista("busca"); setResultados(null); setTermo(""); setConselho(""); }}
                style={{
                  width: "100%", textAlign: "left", cursor: "pointer",
                  padding: ".7rem .75rem", border: "none",
                  borderBottom: "1px solid var(--linha, #e6e2dc)", background: "none",
                  color: "var(--acento)", fontWeight: 600, fontSize: ".9rem",
                }}
              >
                ＋ Procurar outro profissional
              </button>

              {conversas.length === 0 ? (
                <p style={{ padding: "1.25rem .9rem", color: "var(--texto-suave, #5a6b78)", fontSize: ".9rem", margin: 0 }}>
                  Nenhuma conversa ainda. Use “Procurar outro profissional” para começar, ou fale
                  direto com {suporte?.full_name ?? "o suporte CorVIA"}.
                </p>
              ) : (
                conversas.map((c) => (
                  <button
                    key={c.user_id}
                    onClick={() => abrirConversa(c.user_id, c.full_name, c.photo_url)}
                    style={{
                      width: "100%", textAlign: "left", cursor: "pointer",
                      display: "flex", gap: ".65rem", alignItems: "center",
                      padding: ".7rem .75rem", border: "none",
                      borderBottom: "1px solid var(--linha, #e6e2dc)", background: "none",
                    }}
                  >
                    <Avatar nome={c.full_name} foto={c.photo_url} />
                    <span style={{ flex: 1, minWidth: 0 }}>
                      <strong style={{ display: "block", fontSize: ".9rem" }}>{c.full_name}</strong>
                      <span
                        style={{
                          fontSize: ".82rem", color: "var(--texto-suave, #5a6b78)",
                          display: "block", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                        }}
                      >
                        {c.de_mim ? "Você: " : ""}{c.ultima_mensagem}
                      </span>
                    </span>
                    <span style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
                      <span style={{ fontSize: ".72rem", color: "var(--texto-suave, #5a6b78)" }}>
                        {horaCurta(c.ultima_em)}
                      </span>
                      {c.nao_lidas > 0 && (
                        <span
                          className="corvia-chat-panel__unread"
                          style={{
                            background: "var(--acao)", color: "#fff", fontSize: ".7rem", fontWeight: 700,
                            minWidth: 18, height: 18, borderRadius: 9, display: "flex",
                            alignItems: "center", justifyContent: "center", padding: "0 5px",
                          }}
                        >
                          {c.nao_lidas}
                        </span>
                      )}
                    </span>
                  </button>
                ))
              )}
            </div>
          )}

          {/* ---------------------------------------------------- BUSCA -- */}
          {vista === "busca" && (
            <div style={{ height: CORPO_ALTURA, overflowY: "auto" }}>
              <form onSubmit={buscar} style={{ display: "flex", flexDirection: "column", gap: ".4rem", padding: ".75rem" }}>
                <div style={{ display: "flex", gap: ".4rem" }}>
                  <input
                    value={termo}
                    onChange={(e) => setTermo(e.target.value)}
                    placeholder="Nome, e-mail ou registro do conselho"
                    aria-label="Procurar profissional"
                    style={{ flex: 1, padding: ".45rem .6rem", borderRadius: 6, border: "1px solid var(--linha, #cfcac3)" }}
                  />
                  <button type="submit" className="botao" disabled={buscando || termo.trim().length < 2}>
                    {buscando ? "…" : "Buscar"}
                  </button>
                </div>
                {orgaosDeClasse.length > 0 && (
                  <select
                    value={conselho}
                    onChange={(e) => setConselho(e.target.value)}
                    aria-label="Filtrar por órgão de classe"
                    style={{ padding: ".4rem .5rem", borderRadius: 6, border: "1px solid var(--linha, #cfcac3)", fontSize: ".85rem" }}
                  >
                    <option value="">Qualquer órgão de classe</option>
                    {orgaosDeClasse.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                )}
              </form>

              {resultados === null ? (
                <p style={{ padding: "0 .9rem", color: "var(--texto-suave, #5a6b78)", fontSize: ".86rem" }}>
                  A busca só encontra quem também tem assinatura ativa.
                </p>
              ) : resultados.length === 0 ? (
                <p style={{ padding: "0 .9rem", color: "var(--texto-suave, #5a6b78)", fontSize: ".9rem" }}>
                  Ninguém encontrado com esse termo.
                </p>
              ) : (
                resultados.map((u) => (
                  <button
                    key={u.id}
                    onClick={() => abrirConversa(u.id, u.full_name, u.photo_url)}
                    style={{
                      width: "100%", textAlign: "left", cursor: "pointer",
                      display: "flex", gap: ".65rem", alignItems: "center",
                      padding: ".65rem .75rem", border: "none",
                      borderBottom: "1px solid var(--linha, #e6e2dc)", background: "none",
                    }}
                  >
                    <Avatar nome={u.full_name} foto={u.photo_url} />
                    <span style={{ flex: 1, minWidth: 0 }}>
                      <strong style={{ display: "block", fontSize: ".9rem" }}>{u.full_name}</strong>
                      <span style={{ fontSize: ".8rem", color: "var(--texto-suave, #5a6b78)" }}>
                        {[u.council_name && u.council_number
                          ? `${u.council_name} ${u.council_number}${u.council_state ? "/" + u.council_state : ""}`
                          : null, u.specialty].filter(Boolean).join(" · ") || u.email}
                      </span>
                    </span>
                  </button>
                ))
              )}
            </div>
          )}

          {/* ------------------------------------------------- CONVERSA -- */}
          {vista === "conversa" && ativo && (
            <>
              <div style={{ height: CORPO_ALTURA, overflowY: "auto", padding: ".75rem", background: "var(--fundo-suave, #f6f4f1)" }}>
                {mensagens.length === 0 ? (
                  <p style={{ color: "var(--texto-suave, #5a6b78)", fontSize: ".9rem", textAlign: "center", marginTop: "2rem" }}>
                    Nenhuma mensagem ainda. Escreva a primeira.
                  </p>
                ) : (
                  mensagens.map((m) => {
                    const minha = m.sender_id === usuario.id;
                    return (
                      <div key={m.id} style={{ display: "flex", justifyContent: minha ? "flex-end" : "flex-start", marginBottom: ".45rem" }}>
                        <span
                          className={`corvia-chat-panel__message${minha ? " is-mine" : ""}`}
                          style={{
                            maxWidth: "78%", padding: ".45rem .65rem", borderRadius: 10,
                            background: minha ? "var(--primaria)" : "#fff",
                            color: minha ? "#fff" : "var(--texto, #14212b)",
                            border: minha ? "none" : "1px solid var(--linha, #e6e2dc)",
                            fontSize: ".9rem", lineHeight: 1.45, whiteSpace: "pre-wrap", wordBreak: "break-word",
                          }}
                        >
                          {m.body}
                          <span
                            style={{
                              display: "block", fontSize: ".68rem", marginTop: 3, textAlign: "right",
                              color: minha ? "rgba(255,255,255,.75)" : "var(--texto-suave, #7b8a95)",
                            }}
                          >
                            {horaCurta(m.created_at)}
                          </span>
                        </span>
                      </div>
                    );
                  })
                )}
                <div ref={fimRef} />
              </div>

              <form onSubmit={enviar} style={{ display: "flex", gap: ".4rem", padding: ".6rem", borderTop: "1px solid var(--linha, #e6e2dc)" }}>
                <input
                  value={texto}
                  onChange={(e) => setTexto(e.target.value)}
                  placeholder="Escreva uma mensagem"
                  aria-label="Mensagem"
                  maxLength={4000}
                  style={{ flex: 1, padding: ".5rem .6rem", borderRadius: 6, border: "1px solid var(--linha, #cfcac3)" }}
                />
                <button type="submit" className="botao" disabled={enviando || !texto.trim()}>
                  {enviando ? "…" : "Enviar"}
                </button>
              </form>
            </>
          )}

          <footer style={{ padding: ".45rem .75rem", borderTop: "1px solid var(--linha, #e6e2dc)", background: "var(--fundo, #fff)" }}>
            <LogoChat tamanho="compacto" />
          </footer>
        </section>
      )}
    </>
  );
}
