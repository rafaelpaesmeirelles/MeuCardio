import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import { Carregando } from "../components/Estado";
import LogoAssistenteClinica, { IconeAssistenteClinica } from "../components/LogoAssistenteClinica";
import LogoAssistentePessoal, { IconeAssistentePessoal } from "../components/LogoAssistentePessoal";

type Modo = "clinica" | "pessoal";

type Fonte = {
  referencia: string; slug: string; titulo: string; tema: string; review_status: string;
};
type FontePubmed = { pmid: string; titulo: string; autores: string; revista: string; ano: string; url: string };
type Mensagem = {
  papel: "user" | "assistant"; conteudo: string; fontes?: Fonte[]; fontesPubmed?: FontePubmed[];
  truncado?: boolean;
};
type Status = {
  ativo: boolean; provedor: string; modelo: string; modelos_disponiveis: string[];
  limite_diario: number; usado_hoje: number; restante_hoje: number;
  ferramentas_disponiveis_instalacao: boolean; ferramentas_consentidas: boolean;
};
type ConversaResumo = { id: number; titulo: string; modo: Modo; updated_at: string };

const SUGESTOES: Record<Modo, string[]> = {
  clinica: [
    "Quando indicar anticoagulação em FA com CHA₂DS₂-VASc 1?",
    "Ajuste de dose de apixabana na doença renal crônica",
    "Quais os quatro pilares da ICFER e a ordem de introdução?",
  ],
  pessoal: [
    "O que eu tenho na agenda amanhã?",
    "Qual o próximo local de atendimento e quanto tempo até lá?",
    "Resuma os e-mails não lidos de hoje",
  ],
};

/** Seletor exibido toda vez que o assinante entra em "Assistente" — decisão
 * do Rafael em 07/08/2026 (Trabalho 15): renomear a página única para
 * abrigar dois modos, em vez de duas páginas separadas. Clínica mantém
 * exatamente o comportamento de sempre (base institucional + PubMed, sem
 * ferramentas); Pessoal é novo — sem base científica, com acesso à agenda/
 * e-mail do próprio médico quando ele autorizar. */
function Escolha({ onEscolher }: { onEscolher: (modo: Modo) => void }) {
  return (
    <div className="ia-escolha">
      <p className="eyebrow">Assistente</p>
      <h1>Qual assistente você quer usar?</h1>
      <div className="ia-escolha__cartoes">
        <button className="ia-escolha__cartao" onClick={() => onEscolher("clinica")}>
          <LogoAssistenteClinica />
          <p>
            Conteúdo médico/científico — base da Corvia, PubMed e busca na internet
            focada em literatura. As respostas vêm com as fontes usadas.
          </p>
        </button>
        <button className="ia-escolha__cartao" onClick={() => onEscolher("pessoal")}>
          <LogoAssistentePessoal />
          <p>
            Rotina do dia a dia — agenda, compromissos, deslocamento, e-mail e
            temas gerais. Não é fonte de conteúdo clínico.
          </p>
        </button>
      </div>
    </div>
  );
}

/** Consentimento individual para o Assistente Pessoal mexer em agenda/e-mail
 * — a rota já existia (PUT /api/ai/ferramentas/consentimento, Trabalho 5),
 * só nunca tinha tela que a chamasse. Aparece na primeira vez que o médico
 * entra em modo Pessoal sem ter concedido ainda; "usar sem essas
 * ferramentas" deixa seguir como assistente geral, sem tocar em agenda/
 * e-mail, e pode ser ativado depois pelo aviso dentro do chat. */
function ConsentimentoPessoal({
  instalado, onDecidir,
}: {
  instalado: boolean;
  onDecidir: (ativar: boolean) => void;
}) {
  const [enviando, setEnviando] = useState(false);

  async function decidir(ativar: boolean) {
    setEnviando(true);
    try {
      await api.put("/ai/ferramentas/consentimento", { ativar });
    } finally {
      setEnviando(false);
      onDecidir(ativar);
    }
  }

  return (
    <div className="ia-escolha">
      <LogoAssistentePessoal />
      <div className="cartao" style={{ marginTop: "1rem", maxWidth: 560 }}>
        <p style={{ marginTop: 0 }}>
          Para ajudar na sua rotina, o Assistente Pessoal pode acessar a sua própria agenda
          (ver, criar, reagendar e cancelar compromisso, saber o próximo local e o trânsito
          até lá) e ler a sua caixa do CorvIA Mail — sempre a sua conta, nunca a de outra
          pessoa. Nada disso é enviado por conta própria: ele só age quando você pedir na
          conversa.
        </p>
        {!instalado && (
          <p className="eyebrow" style={{ color: "var(--alerta)" }}>
            Estas ferramentas ainda não foram habilitadas nesta instalação. Sua escolha
            fica salva e passa a valer assim que forem habilitadas.
          </p>
        )}
        <div style={{ display: "flex", gap: 8, marginTop: "0.8rem", flexWrap: "wrap" }}>
          <button className="botao" onClick={() => decidir(true)} disabled={enviando}>
            Ativar acesso à agenda e ao e-mail
          </button>
          <button className="botao botao--secundario" onClick={() => decidir(false)} disabled={enviando}>
            Usar sem essas ferramentas por enquanto
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Assistente() {
  const [status, setStatus] = useState<Status | null>(null);
  const [modo, setModo] = useState<Modo | null>(null);
  const [mostrarConsentimento, setMostrarConsentimento] = useState(false);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [pergunta, setPergunta] = useState("");
  const [conversa, setConversa] = useState<number | null>(null);
  const [pensando, setPensando] = useState(false);
  const [etapa, setEtapa] = useState("");
  const [erro, setErro] = useState("");
  const [historico, setHistorico] = useState<ConversaResumo[]>([]);
  const [mostrarHistorico, setMostrarHistorico] = useState(false);
  // "" = Automático (recomendado) — o backend escolhe o modelo pela pergunta.
  const [modeloEscolhido, setModeloEscolhido] = useState("");
  // A base CorvIA e o PubMed continuam sempre ativos no modo Clínica. A
  // pesquisa web do Claude é uma etapa aprofundada e opcional ali, mas é o
  // recurso central do modo Pessoal — por isso nasce ligada nesse modo.
  const [usarInternet, setUsarInternet] = useState(false);
  const fim = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.get<Status>("/ai/status").then(setStatus).catch(() => setStatus(null));
  }, []);
  useEffect(() => { fim.current?.scrollIntoView({ behavior: "smooth" }); }, [mensagens, pensando]);

  const recarregarHistorico = (m: Modo) =>
    api.get<ConversaResumo[]>(`/ai/conversas?modo=${m}`).then(setHistorico).catch(() => {});
  useEffect(() => { if (modo) recarregarHistorico(modo); }, [modo]);

  function escolherModo(escolhido: Modo) {
    setModo(escolhido);
    setUsarInternet(escolhido === "pessoal");
    setMensagens([]);
    setConversa(null);
    setMostrarHistorico(false);
    setErro("");
    if (escolhido === "pessoal" && status && !status.ferramentas_consentidas) {
      setMostrarConsentimento(true);
    }
  }

  function trocarAssistente() {
    setModo(null);
    setMostrarConsentimento(false);
    setMensagens([]);
    setConversa(null);
    setErro("");
  }

  async function abrirConversa(id: number) {
    const c = await api.get<{
      modo: Modo;
      mensagens: { papel: "user" | "assistant"; conteudo: string; fontes: Fonte[]; fontes_pubmed: FontePubmed[] }[]
    }>(`/ai/conversas/${id}`);
    setConversa(id);
    setMensagens(c.mensagens.map((m) => ({
      ...m, fontes: m.fontes.length ? m.fontes : undefined,
      fontesPubmed: m.fontes_pubmed?.length ? m.fontes_pubmed : undefined,
    })));
    setMostrarHistorico(false);
  }

  function novaConversa() {
    setConversa(null);
    setMensagens([]);
    setMostrarHistorico(false);
  }

  async function apagarConversa(id: number, e: React.MouseEvent) {
    e.stopPropagation();
    await api.delete(`/ai/conversas/${id}`);
    if (conversa === id) novaConversa();
    if (modo) recarregarHistorico(modo);
  }

  async function enviar() {
    const texto = pergunta.trim();
    if (!texto || pensando || !modo) return;
    setPergunta("");
    setErro("");
    setMensagens((m) => [...m, { papel: "user", conteudo: texto }, { papel: "assistant", conteudo: "" }]);
    setPensando(true);
    setEtapa(modo === "clinica" ? "Preparando a consulta clínica…" : "Preparando a resposta…");
    // Sinaliza para main.tsx que um streaming está em andamento: se o
    // service worker trocar de versão nesse meio-tempo, a recarga da página
    // fica pendente em vez de cortar a resposta no meio (ver main.tsx).
    (window as unknown as { __streamAtivo?: boolean }).__streamAtivo = true;
    try {
      await api.stream("/ai/perguntar/stream", {
        pergunta: texto, conversation_id: conversa, modo,
        modelo: status?.provedor === "anthropic" && modeloEscolhido ? modeloEscolhido : undefined,
        usar_internet: status?.provedor === "anthropic" ? usarInternet : false,
      }, (evento) => {
        if (evento.tipo === "status") {
          setEtapa(evento.etapa || "Consultando fontes…");
        } else if (evento.tipo === "delta") {
          setEtapa("");
          // Acrescenta o pedaço à última mensagem (a bolha do assistente
          // criada vazia acima) em vez de esperar o texto inteiro — é o que
          // faz a resposta aparecer sendo "digitada" e mantém a conexão viva
          // numa pergunta longa.
          setMensagens((m) => {
            const copia = [...m];
            const ultima = copia[copia.length - 1];
            copia[copia.length - 1] = { ...ultima, conteudo: ultima.conteudo + evento.texto };
            return copia;
          });
        } else if (evento.tipo === "final") {
          setConversa(evento.conversation_id);
          setMensagens((m) => {
            const copia = [...m];
            const ultima = copia[copia.length - 1];
            copia[copia.length - 1] = {
              ...ultima, fontes: evento.fontes,
              fontesPubmed: evento.fontes_pubmed?.length ? evento.fontes_pubmed : undefined,
              truncado: evento.truncado,
            };
            return copia;
          });
          setStatus((s) => s && { ...s, usado_hoje: s.usado_hoje + 1, restante_hoje: s.restante_hoje - 1 });
          if (modo) recarregarHistorico(modo);
        } else if (evento.tipo === "erro") {
          setErro(evento.detalhe ?? "Não foi possível consultar o assistente.");
          setMensagens((m) => m.slice(0, -1));
        }
      });
    } catch (e) {
      setMensagens((m) => m.slice(0, -1));
      setErro(e instanceof Error ? e.message : "Não foi possível consultar o assistente.");
    } finally {
      setPensando(false);
      setEtapa("");
      (window as unknown as { __streamAtivo?: boolean }).__streamAtivo = false;
      (window as unknown as { __streamEncerrado?: () => void }).__streamEncerrado?.();
    }
  }

  if (!status) return <Carregando />;

  if (!status.ativo) {
    return (
      <>
        <p className="eyebrow">Assistente</p>
        <h1>Assistente desligado</h1>
        <div className="cartao">
          <p style={{ marginTop: 0 }}>
            Defina <code>AI_ENABLED=true</code> e a chave do provedor no <code>.env</code>,
            depois rode a indexação da base científica.
          </p>
          <pre className="bloco-comando">docker compose exec backend python -m app.services.indexar</pre>
        </div>
      </>
    );
  }

  if (!modo) return <Escolha onEscolher={escolherModo} />;

  if (mostrarConsentimento) {
    return (
      <ConsentimentoPessoal
        instalado={status.ferramentas_disponiveis_instalacao}
        onDecidir={(ativar) => {
          setStatus((s) => s && { ...s, ferramentas_consentidas: ativar });
          setMostrarConsentimento(false);
        }}
      />
    );
  }

  const IconeModo = modo === "clinica" ? IconeAssistenteClinica : IconeAssistentePessoal;

  return (
    <div className="ia">
      <header className="ia__topo">
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <IconeModo tamanho={32} />
          <div>
            <p className="eyebrow" style={{ margin: 0 }}>
              Assistente {modo === "clinica" ? "Clínica" : "Pessoal"}
              {" · "}
              <button
                className="ia__link-trocar"
                onClick={trocarAssistente}
                style={{ background: "none", border: "none", padding: 0, color: "var(--acento)", cursor: "pointer", font: "inherit" }}
              >
                trocar assistente
              </button>
            </p>
            <h1 style={{ marginBottom: 2 }}>{modo === "clinica" ? "Perguntar à base" : "Sua rotina"}</h1>
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          {status.provedor === "anthropic" && (
            <>
              <select
                value={modeloEscolhido}
                onChange={(e) => setModeloEscolhido(e.target.value)}
                aria-label="Modelo Claude"
                style={{ padding: "0.35rem 0.5rem", fontSize: "0.82rem" }}
              >
                <option value="">Automático (recomendado)</option>
                {status.modelos_disponiveis.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
              <label style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "0.82rem" }}>
                <input
                  type="checkbox"
                  checked={usarInternet}
                  onChange={(e) => setUsarInternet(e.target.checked)}
                />
                Pesquisa web {modo === "clinica" ? "aprofundada (mais lenta)" : ""}
              </label>
            </>
          )}
          <button className="botao botao--secundario" style={{ padding: "0.35rem 0.7rem", fontSize: "0.82rem" }}
                  onClick={novaConversa}>
            + Nova
          </button>
          <button className="botao botao--secundario" style={{ padding: "0.35rem 0.7rem", fontSize: "0.82rem" }}
                  onClick={() => setMostrarHistorico((v) => !v)}>
            Histórico ({historico.length})
          </button>
          <span className="selo dado">
            {status.restante_hoje} de {status.limite_diario} hoje
          </span>
        </div>
      </header>

      {modo === "pessoal" && !status.ferramentas_consentidas && (
        <p className="ia__aviso-ferramentas">
          O acesso à sua agenda e ao seu e-mail ainda não está ativado.{" "}
          <button
            onClick={() => setMostrarConsentimento(true)}
            style={{ background: "none", border: "none", padding: 0, color: "var(--acento)", cursor: "pointer", font: "inherit", textDecoration: "underline" }}
          >
            Ativar agora
          </button>
        </p>
      )}

      {mostrarHistorico && (
        <div className="cartao" style={{ marginBottom: "0.8rem", maxHeight: 260, overflowY: "auto" }}>
          {historico.length === 0 ? (
            <p style={{ margin: 0, color: "var(--texto-secundario)", fontSize: "0.88rem" }}>
              Nenhuma conversa anterior ainda.
            </p>
          ) : (
            historico.map((c) => (
              <div key={c.id}
                   onClick={() => abrirConversa(c.id)}
                   style={{
                     display: "flex", justifyContent: "space-between", alignItems: "center",
                     padding: "0.5rem 0.3rem", borderBottom: "1px solid var(--borda)",
                     cursor: "pointer", background: conversa === c.id ? "var(--fundo)" : "transparent",
                   }}>
                <span style={{ fontSize: "0.88rem" }}>{c.titulo}</span>
                <button className="botao botao--secundario" style={{ padding: "0.2rem 0.5rem", fontSize: "0.76rem" }}
                        onClick={(e) => apagarConversa(c.id, e)} aria-label="Apagar conversa">
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      )}

      <div className="ia__conversa">
        {mensagens.length === 0 && (
          <div className="ia__abertura">
            {modo === "clinica" ? (
              <>
                <p>
                  As respostas saem da base científica do serviço e vêm com as fontes usadas.
                  Quando a base não sustenta a resposta, o assistente diz isso.
                </p>
                <p className="ia__privacidade">
                  Descreva o caso sem identificar o paciente. CPF, telefone, cartão SUS e e-mail
                  são bloqueados no envio.
                </p>
              </>
            ) : (
              <>
                <p>
                  Ajuda com agenda, compromissos, deslocamento, e-mail e temas gerais do dia a
                  dia — não é fonte de conteúdo clínico. Para dúvida médica/científica, use o
                  Assistente Clínica.
                </p>
                <p className="ia__privacidade">
                  CPF, telefone, cartão SUS e e-mail de paciente são bloqueados no envio, mesmo aqui.
                </p>
              </>
            )}
            <div className="ia__sugestoes">
              {SUGESTOES[modo].map((s) => (
                <button key={s} className="ia__sugestao" onClick={() => setPergunta(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {mensagens.map((m, i) => (
          <div key={i} className={`ia__msg ia__msg--${m.papel}`}>
            {m.papel === "assistant" ? (
              // Bolha do assistente nasce vazia (enviar() já a insere antes do
              // primeiro pedaço chegar) — mostra os três pontinhos nela mesma
              // em vez de uma bolha extra embaixo, enquanto não há texto.
              m.conteudo === "" && pensando && i === mensagens.length - 1 ? (
                <span className="ia__carregando">
                  <span className="ia__pensando" aria-hidden="true"><span /><span /><span /></span>
                  <small role="status">{etapa || "Preparando resposta…"}</small>
                </span>
              ) : (
              <>
                <Markdown remarkPlugins={[remarkGfm]}>{m.conteudo}</Markdown>
                {m.truncado && (
                  <p className="selo selo--pendente" style={{ display: "inline-block", marginTop: 4 }}>
                    Resposta cortada por limite de tamanho — pode estar incompleta. Peça para continuar.
                  </p>
                )}
                {m.fontes && m.fontes.length > 0 && (
                  <div className="ia__fontes">
                    <p className="eyebrow">Fontes consultadas</p>
                    {m.fontes.map((f) => (
                      <Link key={f.slug} to={`/biblioteca/${f.slug}`} className="ia__fonte">
                        <span className="dado ia__fonte__marca">{f.referencia}</span>
                        <span>{f.titulo}</span>
                        {f.review_status === "verificacao_humana_necessaria" && (
                          <span className="selo selo--pendente">verificar</span>
                        )}
                      </Link>
                    ))}
                  </div>
                )}
                {m.fontesPubmed && m.fontesPubmed.length > 0 && (
                  <div className="ia__fontes">
                    <p className="eyebrow">Literatura pública (PubMed) — fonte externa, não institucional</p>
                    {m.fontesPubmed.map((f) => (
                      <a key={f.pmid} href={f.url} target="_blank" rel="noopener noreferrer" className="ia__fonte">
                        <span className="dado ia__fonte__marca">PM</span>
                        <span>{f.titulo} — {f.autores} et al. {f.revista}, {f.ano}</span>
                      </a>
                    ))}
                  </div>
                )}
              </>
              )
            ) : (
              m.conteudo
            )}
          </div>
        ))}
        <div ref={fim} />
      </div>

      {erro && <p className="ia__erro" role="alert">{erro}</p>}

      <div className="ia__envio">
        <textarea
          rows={2}
          value={pergunta}
          onChange={(e) => setPergunta(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviar(); }
          }}
          placeholder={modo === "clinica"
            ? "Descreva a dúvida clínica, sem identificar o paciente…"
            : "Pergunte sobre sua agenda, e-mail ou qualquer tema do dia a dia…"}
          aria-label="Pergunta"
        />
        <button className="botao" onClick={enviar} disabled={!pergunta.trim() || pensando}>
          Enviar
        </button>
      </div>
      <p className="ia__rodape">
        {modo === "clinica"
          ? "Apoio à decisão. Não substitui julgamento clínico, bula nem diretriz vigente."
          : "Assistente de apoio à rotina. Não substitui o Assistente Clínica para decisões médicas."}
      </p>
    </div>
  );
}
