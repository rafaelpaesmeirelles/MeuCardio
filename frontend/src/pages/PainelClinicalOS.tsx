import { type FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

type AcaoRapida = {
  to: string;
  titulo: string;
  detalhe: string;
  icone: NomeIcone;
};

type ContextoRecente = {
  path: string;
  titulo: string;
  detalhe: string;
  icone: NomeIcone;
  visitadoEm: number;
};

type Atualizacao = {
  id: number;
  slug: string;
  org: string;
  title: string;
  published_at: string;
  status: "detected" | "aguardando_revisao" | "revisada";
  url: string | null;
};

type RespostaAtualizacoes = { cutoff: string; items: Atualizacao[] };
type Catalogo = { total: number; published_total?: number };
type Contagem = { total?: number };

const ACOES: AcaoRapida[] = [
  { to: "/receituario", titulo: "Prescrever", detalhe: "Novo receituário", icone: "prescricao" },
  { to: "/documentos", titulo: "Solicitar exames", detalhe: "Adicionar solicitação", icone: "clinica" },
  { to: "/documentos", titulo: "Documento", detalhe: "Atestado, relatório...", icone: "documento" },
  { to: "/calculadoras", titulo: "Calculadoras", detalhe: "Escores e índices", icone: "calculadora" },
  { to: "/emergencia", titulo: "Emergências", detalhe: "Condutas rápidas", icone: "emergencia" },
  { to: "/medicamentos", titulo: "Medicamentos", detalhe: "Doses, interações...", icone: "medicamento" },
  { to: "/diretrizes", titulo: "Guidelines", detalhe: "Diretrizes atuais", icone: "conhecimento" },
  { to: "/assistente", titulo: "Assistente", detalhe: "Pergunte ao CorVIA", icone: "assistente" },
];

const CONTEXTOS_INICIAIS: ContextoRecente[] = [
  { path: "/doencas", titulo: "Insuficiência Cardíaca", detalhe: "Condição", icone: "doencas", visitadoEm: 0 },
  { path: "/medicamentos", titulo: "Sacubitril/Valsartana", detalhe: "Medicamento", icone: "medicamento", visitadoEm: 0 },
  { path: "/evidencias", titulo: "Evidências", detalhe: "Recomendações clínicas", icone: "evidencia", visitadoEm: 0 },
  { path: "/calculadoras", titulo: "CHA₂DS₂-VASc", detalhe: "Calculadora", icone: "calculadora", visitadoEm: 0 },
];

const EXEMPLOS = [
  "tratamento da pericardite",
  "dose de Nebido",
  "critérios de Duke",
  "prescrever losartana",
  "calcular CHA₂DS₂-VASc",
];

function saudacao() {
  const hora = new Date().getHours();
  if (hora < 12) return "Bom dia";
  if (hora < 18) return "Boa tarde";
  return "Boa noite";
}

function primeiroNome(nome?: string) {
  return nome?.trim().split(/\s+/)[0] || "Doutor(a)";
}

function chaveContextosRecentes(userId?: number) {
  return userId ? `corvia:contextos-recentes:${userId}` : "";
}

function destinoDoComando(valor: string) {
  const termo = valor.trim();
  const normalizado = termo.toLocaleLowerCase("pt-BR");
  if (/\b(prescrev|prescri|receita|receitu)/.test(normalizado)) return "/receituario";
  if (/\b(atestado|documento|relat[oó]rio|encaminhamento|solicitar exames?|pedido de exames?)/.test(normalizado)) return "/documentos";
  if (/\b(calcul|escore|score|cha.?ds.?vasc)/.test(normalizado)) return "/calculadoras";
  if (/\b(emerg[eê]ncia|urg[eê]ncia)/.test(normalizado)) return "/emergencia";
  if (/\b(intera[cç][aã]o)/.test(normalizado)) return "/interacoes";
  if (/\b(medicamento|f[aá]rmaco|dose)/.test(normalizado) && termo.split(/\s+/).length <= 4) return "/medicamentos";
  if (/\b(diretriz|guideline)/.test(normalizado) && termo.split(/\s+/).length <= 4) return "/diretrizes";
  if (/\b(paciente|round|enfermaria)/.test(normalizado) && termo.split(/\s+/).length <= 4) return "/round";
  return `/busca?q=${encodeURIComponent(termo)}`;
}

function tempoRelativo(timestamp: number) {
  if (!timestamp) return "Explorar";
  const minutos = Math.max(1, Math.round((Date.now() - timestamp) / 60000));
  if (minutos < 60) return `há ${minutos} min`;
  const horas = Math.round(minutos / 60);
  if (horas < 24) return `há ${horas} h`;
  return `há ${Math.round(horas / 24)} d`;
}

function dataCurta(valor: string) {
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) return "";
  return data.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" });
}

function statusAtualizacao(item: Atualizacao) {
  return item.status === "revisada" ? "Revisão clínica concluída" : "Publicação detectada · revisão humana pendente";
}

export default function PainelClinicalOS() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [comando, setComando] = useState("");
  const [recentes, setRecentes] = useState<ContextoRecente[]>([]);
  const [atualizacoes, setAtualizacoes] = useState<Atualizacao[]>([]);
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [evidencias, setEvidencias] = useState<number | null>(null);
  const [estudos, setEstudos] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.body.classList.add("ccc-home-active");
    return () => document.body.classList.remove("ccc-home-active");
  }, []);

  useEffect(() => {
    const chave = chaveContextosRecentes(usuario?.id);
    if (!chave) return setRecentes([]);
    try {
      const salvos = JSON.parse(sessionStorage.getItem(chave) || "[]") as ContextoRecente[];
      setRecentes(salvos.filter((item) => item?.path && item?.titulo).slice(0, 5));
    } catch {
      setRecentes([]);
    }
  }, [usuario?.id]);

  useEffect(() => {
    api.get<RespostaAtualizacoes>("/guideline-updates")
      .then((resposta) => setAtualizacoes((resposta.items ?? []).slice(0, 3)))
      .catch(() => setAtualizacoes([]));
    api.get<Catalogo>("/library/catalog").then(setCatalogo).catch(() => setCatalogo(null));
    api.get<Contagem>("/evidence?limit=1").then((r) => setEvidencias(r.total ?? null)).catch(() => setEvidencias(null));
    api.get<Contagem>("/studies?limit=1").then((r) => setEstudos(r.total ?? null)).catch(() => setEstudos(null));
  }, []);

  useEffect(() => {
    function focar(evento: KeyboardEvent) {
      if (evento.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
        evento.preventDefault();
        inputRef.current?.focus();
      }
    }
    document.addEventListener("keydown", focar);
    return () => document.removeEventListener("keydown", focar);
  }, []);

  const contextos = useMemo(() => recentes.length ? recentes : CONTEXTOS_INICIAIS, [recentes]);

  function executar(evento: FormEvent) {
    evento.preventDefault();
    if (comando.trim().length < 2) return;
    navigate(destinoDoComando(comando));
  }

  function usarExemplo(texto: string) {
    setComando(texto);
    inputRef.current?.focus();
  }

  function abrirAssistentePessoal() {
    window.dispatchEvent(new Event("corvia:abrir-assistente-pessoal"));
  }

  return (
    <div className="ccc-home">
      <div className="ccc-home__main">
        <header className="ccc-home__welcome">
          <h1>{saudacao()}, {primeiroNome(usuario?.full_name)}! <span aria-hidden="true">👋</span></h1>
          <p>O que você precisa resolver agora?</p>
        </header>

        <form className="ccc-command" onSubmit={executar} role="search">
          <Icone nome="busca" />
          <input
            ref={inputRef}
            value={comando}
            onChange={(evento) => setComando(evento.target.value)}
            placeholder="Pergunte, pesquise ou execute uma ação..."
            aria-label="Pergunte, pesquise ou execute uma ação"
            autoComplete="off"
          />
          <kbd>/</kbd>
          <button type="submit" aria-label="Executar comando"><Icone nome="seta" /></button>
        </form>

        <div className="ccc-examples" aria-label="Exemplos de comandos">
          <span>Exemplos:</span>
          {EXEMPLOS.map((texto) => <button key={texto} type="button" onClick={() => usarExemplo(texto)}>{texto}</button>)}
        </div>

        <section className="ccc-section" aria-labelledby="ccc-actions-title">
          <div className="ccc-section__head">
            <h2 id="ccc-actions-title">Ações rápidas</h2>
            <Link to="/busca"><Icone nome="configuracao" /> Personalizar</Link>
          </div>
          <div className="ccc-actions">
            {ACOES.map((acao) => (
              <Link to={acao.to} key={acao.titulo} className={`ccc-action ccc-action--${acao.icone}`}>
                <span className="ccc-action__icon"><Icone nome={acao.icone} /></span>
                <span><strong>{acao.titulo}</strong><small>{acao.detalhe}</small></span>
              </Link>
            ))}
          </div>
        </section>

        <section className="ccc-section" aria-labelledby="ccc-recent-title">
          <div className="ccc-section__head">
            <h2 id="ccc-recent-title">Continuar de onde parei</h2>
          </div>
          <div className="ccc-recent">
            {contextos.map((item) => (
              <Link to={item.path} className="ccc-recent__card" key={item.path}>
                <span className="ccc-recent__icon"><Icone nome={item.icone} /></span>
                <span className="ccc-recent__meta">{item.detalhe}</span>
                <strong>{item.titulo}</strong>
                <small>{tempoRelativo(item.visitadoEm)}</small>
                <i aria-hidden="true" />
              </Link>
            ))}
            <Link to="/busca" className="ccc-recent__more" aria-label="Explorar mais contextos"><Icone nome="chevron" /></Link>
          </div>
        </section>

        <section className="ccc-section" aria-labelledby="ccc-updates-title">
          <div className="ccc-section__head">
            <h2 id="ccc-updates-title">Atualizações que podem importar para você</h2>
            <Link to="/diretrizes">Ver central <Icone nome="seta" /></Link>
          </div>
          <div className="ccc-updates">
            {atualizacoes.length ? atualizacoes.map((item, indice) => (
              <Link to="/diretrizes" key={item.id} className={`ccc-update ccc-update--${indice + 1}`}>
                <small>{item.org || "Atualização científica"} · {dataCurta(item.published_at)}</small>
                <strong>{item.title}</strong>
                <p>{statusAtualizacao(item)}</p>
                <span>Abrir atualização <Icone nome="seta" /></span>
              </Link>
            )) : (
              <Link to="/diretrizes" className="ccc-update ccc-update--empty">
                <small>Central científica</small>
                <strong>Atualizações clínicas revisadas</strong>
                <p>Novas publicações oficiais aparecem aqui quando detectadas.</p>
                <span>Abrir central <Icone nome="seta" /></span>
              </Link>
            )}
          </div>
        </section>
      </div>

      <aside className="ccc-home__rail" aria-label="Contexto inteligente">
        <section className="ccc-rail-card ccc-intelligence-card">
          <header><span><Icone nome="assistente" /> CorVIA Intelligence</span><Link to="/busca">Ver tudo</Link></header>
          <div className="ccc-intelligence-list">
            <Link to="/diretrizes"><span><Icone nome="evidencia" /></span><strong>{atualizacoes.length || "—"}</strong><p>atualizações científicas recentes</p></Link>
            <Link to="/diretrizes"><span><Icone nome="conhecimento" /></span><strong>{atualizacoes[0] ? "1" : "—"}</strong><p>{atualizacoes[0]?.title || "Guidelines e recomendações"}</p></Link>
            <Link to="/biblioteca"><span><Icone nome="conhecimento" /></span><strong>{catalogo?.published_total ?? catalogo?.total ?? "—"}</strong><p>conteúdos no catálogo</p></Link>
            <Link to="/estudos"><span><Icone nome="evidencia" /></span><strong>{estudos ?? "—"}</strong><p>estudos disponíveis para explorar</p></Link>
          </div>
          <Link to="/busca" className="ccc-intelligence-graph"><span>◎</span><span><strong>Explorar relações</strong><small>Tudo com Tudo</small></span><Icone nome="seta" /></Link>
        </section>

        <section className="ccc-rail-card ccc-assistant-card">
          <header><span><span className="ccc-spark">✦</span> Assistente Pessoal</span></header>
          <div className="ccc-assistant-greeting">
            <span className="ccc-spark">✦</span>
            <div><strong>{saudacao()}, {primeiroNome(usuario?.full_name)}!</strong><small>Seu briefing profissional fica disponível sob demanda.</small></div>
          </div>
          <div className="ccc-assistant-state">
            <span><Icone nome="agenda" /></span>
            <div><small>Seu dia</small><strong>Agenda, pendências e próximos compromissos</strong><p>Dados pessoais só são carregados quando necessários e com integrações autorizadas.</p></div>
          </div>
          <div className="ccc-assistant-state">
            <span><Icone nome="rota" /></span>
            <div><small>Deslocamento</small><strong>Planejamento quando você solicitar</strong><p>Localização e trânsito dependem de permissão explícita.</p></div>
          </div>
          <button type="button" className="ccc-assistant-open" onClick={abrirAssistentePessoal}><span className="ccc-spark">✦</span> Abrir Assistente Pessoal <Icone nome="seta" /></button>
        </section>

        <section className="ccc-rail-card ccc-knowledge-card">
          <header><span><Icone nome="conhecimento" /> Conhecimento conectado</span></header>
          <div className="ccc-knowledge-metrics">
            <Link to="/evidencias"><strong>{evidencias ?? "—"}</strong><small>evidências</small></Link>
            <Link to="/estudos"><strong>{estudos ?? "—"}</strong><small>estudos</small></Link>
          </div>
          <p>Condição → medicamento → estudo → guideline → exame → ação.</p>
        </section>
      </aside>
    </div>
  );
}
