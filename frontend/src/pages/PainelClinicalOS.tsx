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
  destaque?: boolean;
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
  { to: "/receituario", titulo: "Prescrever", detalhe: "Medicamentos e receita digital", icone: "prescricao", destaque: true },
  { to: "/documentos", titulo: "Solicitar exames", detalhe: "Pedidos clínicos em poucos cliques", icone: "clinica" },
  { to: "/documentos", titulo: "Documento", detalhe: "Atestado, relatório ou documento livre", icone: "documento" },
  { to: "/calculadoras", titulo: "Calculadoras", detalhe: "Escores e apoio à decisão", icone: "calculadora" },
  { to: "/emergencia", titulo: "Emergências", detalhe: "Protocolos de risco imediato", icone: "emergencia" },
  { to: "/medicamentos", titulo: "Medicamentos", detalhe: "Busca, segurança e evidência", icone: "medicamento" },
  { to: "/diretrizes", titulo: "Guidelines", detalhe: "Diretrizes e alertas clínicos", icone: "evidencia" },
  { to: "/assistente", titulo: "CorVIA AI", detalhe: "Pergunte usando contexto clínico", icone: "assistente" },
];

const EXPLORAR = [
  { titulo: "Insuficiência cardíaca", detalhe: "Terapia, evidência e seguimento", to: "/busca?q=insuficiencia%20cardiaca", icone: "doencas" as NomeIcone },
  { titulo: "Arritmias", detalhe: "FA, taquiarritmias e bradiarritmias", to: "/busca?q=arritmias", icone: "doencas" as NomeIcone },
  { titulo: "Doença coronariana", detalhe: "Síndromes crônicas e agudas", to: "/busca?q=doenca%20coronariana", icone: "clinica" as NomeIcone },
  { titulo: "Hipertensão", detalhe: "Diagnóstico, risco e tratamento", to: "/busca?q=hipertensao", icone: "clinica" as NomeIcone },
  { titulo: "Valvopatias", detalhe: "Avaliação, intervenção e seguimento", to: "/busca?q=valvopatias", icone: "clinica" as NomeIcone },
  { titulo: "Cardio-oncologia", detalhe: "Risco, prevenção e monitorização", to: "/biblioteca?tema=Cardio-oncologia", icone: "evidencia" as NomeIcone },
  { titulo: "Cardiologia pediátrica", detalhe: "Congênitas e cuidado por faixa etária", to: "/biblioteca?tema=Cardiologia%20pedi%C3%A1trica", icone: "doencas" as NomeIcone },
  { titulo: "Gestação", detalhe: "Cardiologia no ciclo gravídico-puerperal", to: "/biblioteca?tema=Gravidez", icone: "check" as NomeIcone },
];

const CONTEXTOS_INICIAIS: ContextoRecente[] = [
  { path: "/doencas", titulo: "Doenças e condições", detalhe: "Consulta clínica", icone: "doencas", visitadoEm: 0 },
  { path: "/medicamentos", titulo: "Medicamentos", detalhe: "Farmacologia e segurança", icone: "medicamento", visitadoEm: 0 },
  { path: "/evidencias", titulo: "Evidências", detalhe: "Síntese científica", icone: "evidencia", visitadoEm: 0 },
  { path: "/calculadoras", titulo: "Calculadoras", detalhe: "Escores e decisão", icone: "calculadora", visitadoEm: 0 },
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
  if (/\b(calcul|escore|score)/.test(normalizado)) return "/calculadoras";
  if (/\b(emerg[eê]ncia|urg[eê]ncia)/.test(normalizado)) return "/emergencia";
  if (/\b(intera[cç][aã]o)/.test(normalizado)) return "/interacoes";
  if (/\b(medicamento|f[aá]rmaco)/.test(normalizado) && termo.split(/\s+/).length <= 3) return "/medicamentos";
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
  const dias = Math.round(horas / 24);
  return `há ${dias} d`;
}

function dataCurta(valor: string) {
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) return "";
  return data.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" });
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
    const chave = chaveContextosRecentes(usuario?.id);
    if (!chave) {
      setRecentes([]);
      return;
    }
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
    <div className="cos-home">
      <section className="cos-home-hero">
        <div className="cos-home-hero__ambient" aria-hidden="true"><span /><span /><span /></div>
        <div className="cos-home-hero__intro">
          <p className="cos-home-hero__kicker"><span /> Clinical Command Center</p>
          <h1>{saudacao()}, {primeiroNome(usuario?.full_name)}.</h1>
          <p className="cos-home-hero__question">O que você precisa resolver agora?</p>
          <p className="cos-home-hero__sub">Conhecimento, decisão e ação clínica conectados a partir do mesmo ponto.</p>
        </div>

        <form className="cos-home-command" onSubmit={executar} role="search">
          <div className="cos-home-command__field">
            <span className="cos-home-command__spark">✦</span>
            <input
              ref={inputRef}
              value={comando}
              onChange={(evento) => setComando(evento.target.value)}
              placeholder="Pergunte, pesquise ou execute uma ação..."
              aria-label="Comando clínico"
              autoComplete="off"
            />
            <kbd>/</kbd>
            <button type="submit" aria-label="Executar comando"><Icone nome="seta" /></button>
          </div>
          <div className="cos-home-command__examples" aria-label="Exemplos de comandos">
            <span>Experimente:</span>
            <button type="button" onClick={() => usarExemplo("Tratamento da pericardite recorrente")}>Pericardite recorrente</button>
            <button type="button" onClick={() => usarExemplo("Nebido")}>Nebido</button>
            <button type="button" onClick={() => usarExemplo("Critérios de Duke")}>Critérios de Duke</button>
            <button type="button" onClick={() => usarExemplo("Prescrever medicamento")}>Prescrever</button>
          </div>
        </form>
      </section>

      <section className="cos-home-closer cos-home-assistant-spotlight" aria-label="Assistente Pessoal">
        <div><span className="cos-home-closer__spark">✦</span><div><p className="eyebrow">Seu Assistente</p><h2>Seu dia também é contexto.</h2><p>Agenda, deslocamento, próximos compromissos e continuidade da sua rotina sem transformar o CorVIA em prontuário.</p></div></div>
        <button type="button" className="cos-personal-trigger" onClick={abrirAssistentePessoal}><span>✦</span><span>Abrir briefing do dia</span></button>
      </section>

      <section className="cos-home-section" aria-labelledby="cos-acoes">
        <div className="cos-section-heading">
          <div><p className="eyebrow">Ações rápidas</p><h2 id="cos-acoes">Da intenção à ação, sem desvio</h2></div>
          <Link to="/busca">Ver todos os recursos <Icone nome="seta" /></Link>
        </div>
        <div className="cos-quick-grid">
          {ACOES.map((acao) => (
            <Link to={acao.to} key={acao.titulo} className={`cos-quick-action${acao.destaque ? " is-primary" : ""}${acao.icone === "emergencia" ? " is-emergency" : ""}`}>
              <span className="cos-quick-action__icon"><Icone nome={acao.icone} /></span>
              <span className="cos-quick-action__copy"><strong>{acao.titulo}</strong><small>{acao.detalhe}</small></span>
              <Icone nome="seta" className="cos-quick-action__arrow" />
            </Link>
          ))}
        </div>
      </section>

      <section className="cos-home-section" aria-labelledby="cos-continuar">
        <div className="cos-section-heading">
          <div><p className="eyebrow">Continuidade</p><h2 id="cos-continuar">Continuar de onde parei</h2></div>
          <small>Seus contextos clínicos recentes</small>
        </div>
        <div className="cos-recent-grid">
          {contextos.map((item) => (
            <Link to={item.path} className="cos-recent-card" key={item.path}>
              <span className="cos-recent-card__icon"><Icone nome={item.icone} /></span>
              <span className="cos-recent-card__copy"><strong>{item.titulo}</strong><small>{item.detalhe}</small></span>
              <span className="cos-recent-card__time">{tempoRelativo(item.visitadoEm)}</span>
              <Icone nome="seta" className="cos-recent-card__arrow" />
            </Link>
          ))}
        </div>
      </section>

      <section className="cos-home-grid-2">
        <article className="cos-home-panel cos-practice-updates">
          <div className="cos-section-heading">
            <div><p className="eyebrow">Atualização clínica</p><h2>O que pode mudar sua prática</h2></div>
            <Link to="/diretrizes">Abrir central <Icone nome="seta" /></Link>
          </div>
          {atualizacoes.length ? (
            <div className="cos-update-list">
              {atualizacoes.map((item) => (
                <Link to="/diretrizes" key={item.id} className="cos-update-item">
                  <span className="cos-update-item__icon"><Icone nome="evidencia" /></span>
                  <span className="cos-update-item__copy"><small>{item.org} · {dataCurta(item.published_at)}</small><strong>{item.title}</strong><em>{item.status === "revisada" ? "Revisão clínica concluída" : "Publicação detectada · revisão humana pendente"}</em></span>
                  <Icone nome="seta" />
                </Link>
              ))}
            </div>
          ) : (
            <div className="cos-update-empty"><span><Icone nome="check" /></span><div><strong>Central de atualização pronta</strong><small>Quando uma nova publicação oficial for detectada, ela aparece aqui sem alterar conteúdo clínico silenciosamente.</small></div></div>
          )}
        </article>

        <article className="cos-home-panel cos-knowledge-pulse">
          <div className="cos-section-heading">
            <div><p className="eyebrow">Base CorVIA</p><h2>Conhecimento conectado</h2></div>
            <Link to="/biblioteca">Explorar <Icone nome="seta" /></Link>
          </div>
          <div className="cos-metrics">
            <Link to="/biblioteca"><span><Icone nome="conhecimento" /></span><strong>{catalogo?.published_total ?? catalogo?.total ?? "—"}</strong><small>conteúdos no catálogo</small></Link>
            <Link to="/evidencias"><span><Icone nome="evidencia" /></span><strong>{evidencias ?? "—"}</strong><small>recomendações</small></Link>
            <Link to="/estudos"><span><Icone nome="evidencia" /></span><strong>{estudos ?? "—"}</strong><small>estudos</small></Link>
          </div>
          <Link to="/busca" className="cos-graph-callout">
            <span className="cos-graph-callout__symbol">◎</span>
            <span><small>Knowledge Graph</small><strong>Tudo com Tudo</strong><p>Doença → medicamento → estudo → evidência → guideline → exame → ação.</p></span>
            <Icone nome="seta" />
          </Link>
        </article>
      </section>

      <section className="cos-home-section" aria-labelledby="cos-explorar">
        <div className="cos-section-heading">
          <div><p className="eyebrow">Explorar</p><h2 id="cos-explorar">Entre por qualquer ponto clínico</h2></div>
          <Link to="/biblioteca">Biblioteca completa <Icone nome="seta" /></Link>
        </div>
        <div className="cos-explore-grid">
          {EXPLORAR.map((area) => (
            <Link to={area.to} className="cos-explore-card" key={area.titulo}>
              <span><Icone nome={area.icone} /></span>
              <div><strong>{area.titulo}</strong><small>{area.detalhe}</small></div>
              <Icone nome="seta" />
            </Link>
          ))}
        </div>
      </section>

      <section className="cos-home-closer">
        <div><span className="cos-home-closer__spark">✦</span><div><p className="eyebrow">CorVIA</p><h2>Você não precisa decorar onde cada função mora.</h2><p>Comece pelo problema. O sistema aproxima o conhecimento e a ação.</p></div></div>
        <Link to="/assistente">Perguntar à CorVIA AI <Icone nome="seta" /></Link>
      </section>
    </div>
  );
}
