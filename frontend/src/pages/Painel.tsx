import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { AreaClinicaIcone, type AreaClinicaMarca } from "../components/IdentidadeClinica";
import LogoCorviaMail from "../components/LogoCorviaMail";
import MapaDeslocamento, { type RotaDeslocamento } from "../components/MapaDeslocamento";
import { api, assetUrl } from "../lib/api";
import { tokenEmail } from "../lib/apiEmail";
import { useAuth } from "../lib/auth";

type Tema = { theme: string; count: number };
type Paciente = { id: number };
type ListaComTotal = { total?: number };
type Catalogo = { total: number };
type Agendamento = {
  id: number;
  patient_name: string | null;
  scheduled_at: string;
  appointment_type: string;
  status: string;
};

type PreferenciaMobilidade = {
  enabled: boolean;
  automatic_foreground_refresh: boolean;
  refresh_interval_minutes: number;
  traffic_configured: boolean;
};

type ConfiguracaoMapa = { provider: string; configured: boolean; api_key: string | null };

type ProximoLocal = {
  appointment_id: number | null;
  routine_id: number | null;
  starts_at: string;
  ends_at: string | null;
  service_name: string;
  source: "work_routine" | "appointment";
  arrival_buffer_minutes: number;
  location: { id: number; name: string; address: Record<string, string>; latitude: number | null; longitude: number | null };
};

type Deslocamento = {
  status: string;
  provider?: string;
  updated_at?: string;
  destination: ProximoLocal | null;
  routes: RotaDeslocamento[];
  tips: string[];
};

type Atalho = {
  to?: string;
  acao?: "abrir-chat";
  nome: string;
  descricao: string;
  icone: NomeIcone;
  principal?: boolean;
};

type Grupo = {
  titulo: string;
  descricao: string;
  icone: NomeIcone;
  links: { to: string; nome: string }[];
};

type AreaDestaque = {
  nome: string;
  contexto: string;
  descricao: string;
  to: string;
  marca: AreaClinicaMarca;
  tema?: string;
};

type StatusEmail = {
  status: string;
  incluido_no_plano: boolean;
};

type ContaEmail = {
  ativa: boolean;
  email_address?: string;
};

type MensagemEmail = {
  messageId?: string;
  id?: string;
  subject?: string;
  fromAddress?: string;
  sender?: string;
  receivedTime?: string;
  sentDateInGMT?: string;
  date?: string;
  status?: string;
};

type ResumoEmail = {
  disponivel: boolean;
  email_address: string | null;
  pendentes: MensagemEmail[];
};

const ATALHOS: Atalho[] = [
  {
    to: "/receituario",
    nome: "Nova prescrição",
    descricao: "Prescreva, revise e prepare a assinatura digital.",
    icone: "prescricao",
    principal: true,
  },
  {
    to: "/documentos",
    nome: "Emitir documento",
    descricao: "Atestado, relatório, solicitação ou encaminhamento.",
    icone: "documento",
  },
  {
    to: "/triagem-sintomas",
    nome: "Iniciar triagem",
    descricao: "Organize sintomas, risco e próximos passos.",
    icone: "triagem",
  },
  {
    to: "/assistente",
    nome: "Perguntar ao assistente",
    descricao: "Consulte a base clínica com fontes verificáveis.",
    icone: "assistente",
  },
  {
    to: "/corvia-mail",
    nome: "CorvIA Mail",
    descricao: "Centralize mensagens, prioridades, modelos e comunicação clínica.",
    icone: "mail",
  },
  {
    acao: "abrir-chat",
    nome: "CorvIA Chat",
    descricao: "Fale com profissionais e acompanhe mensagens não lidas.",
    icone: "comunicacao",
  },
];

const GRUPOS: Grupo[] = [
  {
    titulo: "Decisão clínica",
    descricao: "Da dúvida à conduta, com rastreabilidade.",
    icone: "clinica",
    links: [
      { to: "/assistente", nome: "Assistente clínico" },
      { to: "/doencas", nome: "Guia de doenças" },
      { to: "/calculadoras", nome: "Calculadoras e escores" },
      { to: "/interacoes", nome: "Interações medicamentosas" },
      { to: "/condicoes", nome: "Condições especiais" },
      { to: "/fluxogramas", nome: "Fluxogramas" },
      { to: "/medicamentos", nome: "Medicamentos" },
    ],
  },
  {
    titulo: "Prática e pacientes",
    descricao: "Continuidade do consultório ao hospital.",
    icone: "pacientes",
    links: [
      { to: "/agenda", nome: "Agenda" },
      { to: "/round", nome: "Round hospitalar" },
      { to: "/receituario", nome: "Prescrição eletrônica" },
      { to: "/documentos", nome: "Documentos" },
      { to: "/checklists", nome: "Checklist de alta" },
      { to: "/material-paciente", nome: "Material ao paciente" },
      { to: "/telediagnostico", nome: "Laudo e consultoria" },
    ],
  },
  {
    titulo: "Ciência e atualização",
    descricao: "Conteúdo clínico para consultar e aprofundar.",
    icone: "conhecimento",
    links: [
      { to: "/biblioteca", nome: "Biblioteca científica" },
      { to: "/diretrizes", nome: "Alertas de diretriz" },
      { to: "/evidencias", nome: "Evidências" },
      { to: "/estudos", nome: "Estudos" },
      { to: "/exames", nome: "Exames e marcadores" },
      { to: "/galeria", nome: "Galeria de imagens" },
      { to: "/casos-clinicos", nome: "Casos clínicos" },
      { to: "/trilhas", nome: "Trilhas de estudo" },
    ],
  },
  {
    titulo: "Comunicação e gestão",
    descricao: "Mensagens, acompanhamento e organização profissional.",
    icone: "comunicacao",
    links: [
      { to: "/corvia-mail", nome: "Corvia Mail" },
      { to: "/usuarios-online", nome: "Rede profissional" },
      { to: "/indicadores", nome: "Meus indicadores" },
      { to: "/favoritos", nome: "Favoritos" },
      { to: "/cursos", nome: "Cursos" },
      { to: "/apresentacao", nome: "Modo apresentação" },
    ],
  },
];

const AREAS_DESTAQUE: AreaDestaque[] = [
  {
    nome: "Cardiologia Pediátrica",
    contexto: "Infância e adolescência",
    descricao: "Congênitas, arritmias, insuficiência cardíaca e seguimento por faixa etária.",
    to: "/biblioteca?tema=Cardiologia%20pedi%C3%A1trica",
    marca: "pediatrica",
    tema: "Cardiologia pediátrica",
  },
  {
    nome: "Cardiologia Neonatal",
    contexto: "Primeiros dias de vida",
    descricao: "Triagem, cardiopatias congênitas e abordagem cardiovascular do recém-nascido.",
    to: "/doencas?tab=congenitas&area=cardiopediatria",
    marca: "neonatal",
  },
  {
    nome: "Cardiopatias Congênitas no Adulto",
    contexto: "Transição e seguimento",
    descricao: "Anatomia, intervenções prévias, risco tardio e cuidado longitudinal do adulto.",
    to: "/doencas?tab=congenitas",
    marca: "congenita",
  },
  {
    nome: "Cardio-Geriatria",
    contexto: "Longevidade cardiovascular",
    descricao: "Decisões adaptadas à multimorbidade, fragilidade e polifarmácia.",
    to: "/biblioteca?tema=Cardiologia%20geri%C3%A1trica",
    marca: "geriatria",
    tema: "Cardiologia geriátrica",
  },
  {
    nome: "Cardiologia na Gestação e Amamentação",
    contexto: "Ciclo gravídico-puerperal",
    descricao: "Condutas cardiovasculares e segurança terapêutica durante gestação e lactação.",
    to: "/biblioteca?tema=Gravidez",
    marca: "gestacao",
    tema: "Gravidez",
  },
  {
    nome: "Cardio-Oncologia",
    contexto: "Cuidado multidisciplinar",
    descricao: "Avaliação de risco, prevenção e acompanhamento da cardiotoxicidade.",
    to: "/biblioteca?tema=Cardio-oncologia",
    marca: "oncologia",
    tema: "Cardio-oncologia",
  },
];

function mesmoTema(a: string, b: string) {
  return a.localeCompare(b, "pt-BR", { sensitivity: "base" }) === 0;
}

function saudacao() {
  const hora = new Date().getHours();
  if (hora < 12) return "Bom dia";
  if (hora < 18) return "Boa tarde";
  return "Boa noite";
}

function dataExtenso() {
  const texto = new Intl.DateTimeFormat("pt-BR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date());
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function mesmoDia(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate();
}

function quantidade(valor: number | null | undefined) {
  return valor == null ? "—" : valor.toLocaleString("pt-BR");
}

function Numero({ rotulo, valor, to }: { rotulo: string; valor: number | null; to: string }) {
  return <Link to={to}><strong>{quantidade(valor)}</strong><span>{rotulo}</span></Link>;
}

function abrirChatGlobal() {
  const botao = document.querySelector<HTMLButtonElement>(
    'button[aria-label^="Abrir o CorvIA Chat"]',
  );
  botao?.click();
}

function nomeTipo(tipo: string) {
  return ({ consulta: "Consulta", retorno: "Retorno", exame: "Exame", outro: "Compromisso" } as Record<string, string>)[tipo]
    || "Compromisso";
}

function dataDoEmail(mensagem: MensagemEmail) {
  const bruto = mensagem.receivedTime ?? mensagem.sentDateInGMT ?? mensagem.date;
  if (!bruto) return null;
  const numero = Number(bruto);
  const data = Number.isFinite(numero) && String(bruto).length > 8 ? new Date(numero) : new Date(bruto);
  return Number.isNaN(data.getTime()) ? null : data;
}

function dataCurtaDoEmail(mensagem: MensagemEmail) {
  const data = dataDoEmail(mensagem);
  if (!data) return "";
  return data.toDateString() === new Date().toDateString()
    ? data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })
    : data.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

export default function Painel() {
  const { usuario } = useAuth();
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [temas, setTemas] = useState<Tema[]>([]);
  const [pacientes, setPacientes] = useState<number | null>(null);
  const [agenda, setAgenda] = useState<Agendamento[] | null>(null);
  const [fluxogramas, setFluxogramas] = useState<number | null>(null);
  const [evidencias, setEvidencias] = useState<number | null>(null);
  const [estudos, setEstudos] = useState<number | null>(null);
  const [mobilidade, setMobilidade] = useState<PreferenciaMobilidade | null>(null);
  const [configuracaoMapa, setConfiguracaoMapa] = useState<ConfiguracaoMapa | null>(null);
  const [proximosLocais, setProximosLocais] = useState<ProximoLocal[]>([]);
  const [deslocamento, setDeslocamento] = useState<Deslocamento | null>(null);
  const [origemDeslocamento, setOrigemDeslocamento] = useState<{ latitude: number; longitude: number } | null>(null);
  const [erroLocalizacao, setErroLocalizacao] = useState("");
  const [statusEmail, setStatusEmail] = useState<StatusEmail | null>(null);
  const [contaEmail, setContaEmail] = useState<ContaEmail | null>(null);
  const [emailsPendentes, setEmailsPendentes] = useState<MensagemEmail[]>([]);
  const [resumoEmail, setResumoEmail] = useState<"carregando" | "disponivel" | "indisponivel">("carregando");

  useEffect(() => {
    const total = (rota: string) =>
      api.get<ListaComTotal>(rota).then((dados) => dados.total ?? 0).catch(() => null);

    api.get<Catalogo>("/library/catalog").then(setCatalogo).catch(() => setCatalogo(null));
    api.get<Tema[]>("/library/themes").then(setTemas).catch(() => setTemas([]));
    api.get<Paciente[]>("/round/patients").then((lista) => setPacientes(lista.length)).catch(() => setPacientes(null));
    api.get<Agendamento[]>("/appointments").then(setAgenda).catch(() => setAgenda([]));
    total("/library/documents?kind=fluxograma&limit=1").then(setFluxogramas);
    total("/evidence?limit=1").then(setEvidencias);
    total("/studies?limit=1").then(setEstudos);
    api.get<PreferenciaMobilidade>("/agenda/mobility/preferences").then(setMobilidade).catch(() => setMobilidade(null));
    api.get<ConfiguracaoMapa>("/agenda/mobility/map-config").then(setConfiguracaoMapa).catch(() => setConfiguracaoMapa(null));
    api.get<ProximoLocal[]>("/agenda/workday/next-locations").then(setProximosLocais).catch(() => setProximosLocais([]));
    api.get<StatusEmail>("/billing/status-email").then(setStatusEmail).catch(() => setStatusEmail(null));
    api.get<ContaEmail>("/email/conta").then(setContaEmail).catch(() => setContaEmail(null));
    api.get<ResumoEmail>("/email/resumo")
      .then((resumo) => {
        setEmailsPendentes(resumo.pendentes ?? []);
        setResumoEmail(resumo.disponivel ? "disponivel" : "indisponivel");
      })
      .catch(() => {
        setEmailsPendentes([]);
        setResumoEmail("indisponivel");
      });
  }, []);

  useEffect(() => {
    if (!mobilidade?.enabled || !mobilidade.automatic_foreground_refresh || !navigator.geolocation) return;
    let ativo = true;
    let timer: number | undefined;
    const atualizar = () => navigator.geolocation.getCurrentPosition(
      (position) => {
        if (!ativo) return;
        setErroLocalizacao("");
        api.post<Deslocamento>("/agenda/mobility/commute", {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }).then((result) => {
          if (!ativo) return;
          setOrigemDeslocamento({ latitude: position.coords.latitude, longitude: position.coords.longitude });
          setDeslocamento(result);
        }).catch(() => {
          if (ativo) setErroLocalizacao("Não foi possível atualizar o trânsito agora.");
        });
      },
      (error) => {
        if (!ativo) return;
        setErroLocalizacao(error.code === error.PERMISSION_DENIED
          ? "A permissão de localização está bloqueada neste aparelho."
          : "Localização temporariamente indisponível.");
      },
      { enableHighAccuracy: false, timeout: 12_000, maximumAge: 120_000 },
    );
    atualizar();
    timer = window.setInterval(atualizar, Math.max(2, mobilidade.refresh_interval_minutes) * 60_000);
    const aoVoltar = () => { if (document.visibilityState === "visible") atualizar(); };
    document.addEventListener("visibilitychange", aoVoltar);
    return () => { ativo = false; if (timer) window.clearInterval(timer); document.removeEventListener("visibilitychange", aoVoltar); };
  }, [mobilidade]);

  const compromissosHoje = useMemo(() => {
    if (!agenda) return [];
    const hoje = new Date();
    return agenda
      .filter((item) => item.status !== "cancelado" && mesmoDia(new Date(item.scheduled_at), hoje))
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at));
  }, [agenda]);

  const proximo = useMemo(() => {
    const agora = Date.now();
    return (agenda ?? [])
      .filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= agora)
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0];
  }, [agenda]);

  const primeiroNome = usuario?.full_name?.trim().split(/\s+/)[0] || "Doutor(a)";
  const assinanteEmail = !!statusEmail && ["ativo", "teste", "inadimplente"].includes(statusEmail.status);
  const totalPrioridades = compromissosHoje.length + (pacientes ?? 0);
  const saidaRecomendada = proximosLocais[0] && deslocamento?.routes[0]
    ? new Date(new Date(proximosLocais[0].starts_at).getTime()
      - (deslocamento.routes[0].duration_seconds + proximosLocais[0].arrival_buffer_minutes * 60) * 1000)
    : null;
  const temasSecundarios = useMemo(
    () => temas.filter((tema) => !AREAS_DESTAQUE.some(
      (area) => area.tema && mesmoTema(area.tema, tema.theme),
    )),
    [temas],
  );

  return (
    <div className="hoje">
      <section className="hoje__cabecalho">
        <div>
          <p className="eyebrow">Central clínica</p>
          <h1>{saudacao()}, {primeiroNome}.</h1>
          <p className="hoje__data">{dataExtenso()} · sua rotina clínica em um só lugar.</p>
        </div>
        <div className="hoje__identidade-profissional">
          {usuario?.document_logo_url ? (
            <img src={assetUrl(usuario.document_logo_url)} alt="Logo profissional" />
          ) : (
            <img src="/corvia-logo-compacta.png" alt="CorvIA" />
          )}
          <span>
            <small>{usuario?.document_logo_url ? "Identidade profissional" : "Seu ambiente clínico"}</small>
            <strong>{usuario?.workplace_name || usuario?.specialty || "Cardiologia conectada"}</strong>
          </span>
        </div>
      </section>

      <section className="hoje__atalhos" aria-labelledby="acoes-frequentes">
        <div className="hoje__secao-topo">
          <div>
            <p className="eyebrow">Fluxo rápido</p>
            <h2 id="acoes-frequentes">O que você precisa fazer agora?</h2>
          </div>
        </div>
        <div className="hoje__atalhos-grade">
          {ATALHOS.map((atalho) => {
            const conteudo = <><span className="hoje-atalho__icone"><Icone nome={atalho.icone} /></span><span className="hoje-atalho__texto"><strong>{atalho.nome}</strong><small>{atalho.descricao}</small></span><Icone nome="seta" className="hoje-atalho__seta" /></>;
            const classe = `hoje-atalho${atalho.principal ? " hoje-atalho--principal" : ""}`;
            return atalho.acao === "abrir-chat"
              ? <button key={atalho.nome} type="button" className={classe} onClick={abrirChatGlobal}>{conteudo}</button>
              : <Link key={atalho.nome} to={atalho.to || "/"} className={classe}>{conteudo}</Link>;
          })}
        </div>
      </section>

      <section className="hoje__grade" aria-label="Resumo do dia">
        <article className="hoje-card hoje-card--agenda">
          <div className="hoje-card__topo">
            <div><p className="eyebrow">Seu dia</p><h2>Agenda de hoje</h2></div>
            <Link to="/agenda">Abrir agenda <Icone nome="seta" /></Link>
          </div>

          {agenda === null ? (
            <p className="hoje-card__estado" role="status">Carregando compromissos…</p>
          ) : compromissosHoje.length === 0 ? (
            <div className="hoje-card__vazio">
              <span><Icone nome="agenda" /></span>
              <div>
                <strong>Nenhum compromisso marcado para hoje.</strong>
                {proximo ? (
                  <small>
                    Próximo: {new Date(proximo.scheduled_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}
                    {" às "}{new Date(proximo.scheduled_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}.
                  </small>
                ) : <small>Sua agenda está livre para novos atendimentos.</small>}
              </div>
            </div>
          ) : (
            <div className="hoje-agenda">
              {compromissosHoje.slice(0, 4).map((item) => (
                <div className="hoje-agenda__item" key={item.id}>
                  <time>{new Date(item.scheduled_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</time>
                  <span><strong>{item.patient_name || "Paciente não informado"}</strong><small>{nomeTipo(item.appointment_type)}</small></span>
                  <span className="hoje-agenda__status">{item.status}</span>
                </div>
              ))}
              {compromissosHoje.length > 4 && (
                <Link className="hoje-agenda__mais" to="/agenda">Ver mais {compromissosHoje.length - 4} compromissos</Link>
              )}
            </div>
          )}
        </article>

        <article className="hoje-card hoje-card--round">
          <div className="hoje-card__topo">
            <div><p className="eyebrow">Continuidade</p><h2>Round hospitalar</h2></div>
            <Icone nome="round" />
          </div>
          <div className="hoje-card__numero"><strong>{quantidade(pacientes)}</strong><span>pacientes no round</span></div>
          <p>Acompanhe evolução, pendências e linha do tempo dos pacientes cadastrados.</p>
          <Link className="hoje-card__acao" to="/round">Abrir round <Icone nome="seta" /></Link>
        </article>

        <article className="hoje-card hoje-card--prioridades">
          <div className="hoje-card__topo">
            <div><p className="eyebrow">Foco clínico</p><h2>Prioridades do dia</h2></div>
            <span className="hoje-prioridades__sinal"><Icone nome="check" /></span>
          </div>
          <strong className="hoje-prioridades__total">{quantidade(totalPrioridades)}</strong>
          <div className="hoje-prioridades__lista">
            <Link to="/agenda"><span><Icone nome="agenda" /> Atendimentos</span><strong>{quantidade(compromissosHoje.length)}</strong></Link>
            <Link to="/round"><span><Icone nome="round" /> Pacientes em round</span><strong>{quantidade(pacientes)}</strong></Link>
            <Link to="/agenda"><span><Icone nome="rota" /> Próximo local</span><strong>{proximosLocais[0] ? "Definido" : "Configurar"}</strong></Link>
          </div>
          <Link className="hoje-card__acao" to="/agenda">Organizar meu dia <Icone nome="seta" /></Link>
        </article>

        <article className="hoje-card hoje-card--deslocamento">
          <div className="hoje-card__topo">
            <div><p className="eyebrow">Próximo deslocamento</p><h2>Rota para o trabalho</h2></div>
            <Icone nome="rota" />
          </div>
          {proximosLocais.length === 0 ? (
            <div className="deslocamento-vazio"><strong>Rotina ainda não cadastrada.</strong><span>Defina seus dias, entrada, saída e locais na Agenda.</span></div>
          ) : (
            <>
              <div className="deslocamento-destino">
                <span><Icone nome="pin" /></span>
                <div><strong>{proximosLocais[0].location.name}</strong><small>{new Date(proximosLocais[0].starts_at).toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit", month: "short" })} · início às {new Date(proximosLocais[0].starts_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</small></div>
              </div>
              {deslocamento?.status === "live" && deslocamento.routes[0] ? (
                <>
                  <div className="deslocamento-resumo">
                    <span><strong>{Math.ceil(deslocamento.routes[0].duration_seconds / 60)} min</strong><small>tempo estimado</small></span>
                    <span><strong>{(deslocamento.routes[0].distance_meters / 1000).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} km</strong><small>distância</small></span>
                    <span><strong>{deslocamento.routes[0].traffic_delay_seconds > 60 ? `+${Math.ceil(deslocamento.routes[0].traffic_delay_seconds / 60)} min` : "Sem atraso"}</strong><small>impacto do trânsito</small></span>
                    {saidaRecomendada && <span><strong>{saidaRecomendada.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</strong><small>saída recomendada</small></span>}
                  </div>
                  <MapaDeslocamento
                    rotas={deslocamento.routes}
                    origem={origemDeslocamento}
                    destino={{
                      name: proximosLocais[0].location.name,
                      latitude: proximosLocais[0].location.latitude,
                      longitude: proximosLocais[0].location.longitude,
                    }}
                    provider={deslocamento.provider}
                    updatedAt={deslocamento.updated_at}
                    googleMapsApiKey={configuracaoMapa?.api_key}
                  />
                  {deslocamento.tips.length > 0 && <div className="deslocamento-dicas">{deslocamento.tips.map((dica) => <span key={dica}>{dica}</span>)}</div>}
                </>
              ) : erroLocalizacao ? (
                <p className="deslocamento-estado">{erroLocalizacao}</p>
              ) : mobilidade?.enabled ? (
                <p className="deslocamento-estado">{mobilidade.traffic_configured ? "Atualizando trânsito…" : "Local e horário prontos; provedor de trânsito ainda não configurado."}</p>
              ) : (
                <p className="deslocamento-estado">Ative a localização uma vez nas configurações da Agenda para receber ETAs automáticos.</p>
              )}
              {proximosLocais.length > 1 && <div className="deslocamento-proximos">Depois: {proximosLocais.slice(1).map((item) => item.location.name).join(" · ")}</div>}
            </>
          )}
          <Link className="hoje-card__acao" to="/agenda">Abrir agenda e rotas <Icone nome="seta" /></Link>
        </article>

        <article className="hoje-card hoje-card--mail">
          <div className="hoje-mail__topo">
            <div><p className="eyebrow">Comunicação</p><h2>Seu consultório, também no e-mail</h2></div>
            <span className="hoje-mail__logo"><LogoCorviaMail tamanho="compacto" /></span>
          </div>

          {assinanteEmail ? (
            contaEmail?.ativa ? (
              <div className="hoje-mail__assinante">
                <div className="hoje-mail__conta">
                  <span><i />{contaEmail.email_address}</span>
                  <small>{resumoEmail === "disponivel" ? "Resumo de pendências atualizado" : "Caixa profissional conectada"}</small>
                </div>
                {emailsPendentes.length > 0 ? (
                  <div className="hoje-mail__mensagens" aria-label="E-mails não lidos mais recentes">
                    {emailsPendentes.map((mensagem, index) => (
                      <Link to="/caixa-de-email" key={mensagem.messageId ?? mensagem.id ?? index}>
                        <span><strong>{mensagem.fromAddress ?? mensagem.sender ?? "Remetente não informado"}</strong><small>{mensagem.subject || "Sem assunto"}</small></span>
                        <time>{dataCurtaDoEmail(mensagem)}</time>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="hoje-mail__sem-pendencias">
                    <Icone nome={resumoEmail === "disponivel" ? "check" : "sincronizar"} />
                    <span>
                      <strong>{resumoEmail === "carregando" ? "Atualizando pendências…" : resumoEmail === "disponivel" ? "Nenhum e-mail pendente" : "Resumo temporariamente indisponível"}</strong>
                      <small>{resumoEmail === "disponivel" ? "Sua caixa está em dia." : "Abra a caixa para consultar as mensagens recebidas."}</small>
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div className="hoje-mail__ativacao"><Icone nome="configuracao" /><span><strong>Assinatura ativa</strong><small>Escolha seu endereço @corvia.med.br e conclua a ativação segura.</small></span></div>
            )
          ) : (
            <div className="hoje-mail__beneficios">
              <span><Icone nome="mail" /><small>Endereço profissional<br /><strong>@corvia.med.br</strong></small></span>
              <span><Icone nome="sincronizar" /><small>Contatos e agenda<br /><strong>sincronizados</strong></small></span>
              <span><Icone nome="documento" /><small>Modelos, anexos e<br /><strong>fluxo profissional</strong></small></span>
            </div>
          )}
          <Link className="hoje-card__acao" to={contaEmail?.ativa && tokenEmail.get() ? "/caixa-de-email" : "/corvia-mail"}>
            {assinanteEmail ? contaEmail?.ativa ? "Abrir caixa de entrada" : "Ativar meu endereço" : "Conhecer e assinar o CorvIA Mail"} <Icone nome="seta" />
          </Link>
        </article>

        <article className="hoje-card hoje-card--central-documentos">
          <div className="hoje-card__topo">
            <div><p className="eyebrow">Produção clínica</p><h2>Central de documentos</h2></div>
            <Icone nome="documento" />
          </div>
          <p>Prescreva, documente e oriente o paciente sem interromper o fluxo do atendimento.</p>
          <div className="hoje-documentos__acoes">
            <Link to="/receituario"><Icone nome="prescricao" /><span><strong>Nova prescrição</strong><small>Medicamentos e uso contínuo</small></span><Icone nome="seta" /></Link>
            <Link to="/documentos"><Icone nome="documento" /><span><strong>Emitir documento</strong><small>Atestado, relatório ou solicitação</small></span><Icone nome="seta" /></Link>
            <Link to="/checklists"><Icone nome="check" /><span><strong>Checklist de alta</strong><small>Segurança na transição do cuidado</small></span><Icone nome="seta" /></Link>
          </div>
        </article>
      </section>

      <section className="hoje__acervo" aria-labelledby="acervo-titulo">
        <div className="hoje__secao-topo">
          <div><p className="eyebrow">Conhecimento aplicável</p><h2 id="acervo-titulo">Ciência à mão, quando a decisão acontece</h2></div>
          <Link to="/biblioteca">Explorar biblioteca <Icone nome="seta" /></Link>
        </div>
        <div className="hoje__metricas">
          <Numero rotulo="itens científicos" valor={catalogo?.total ?? null} to="/biblioteca" />
          <Numero rotulo="fluxogramas" valor={fluxogramas} to="/fluxogramas" />
          <Numero rotulo="evidências" valor={evidencias} to="/evidencias" />
          <Numero rotulo="estudos" valor={estudos} to="/estudos" />
        </div>

        <section className="hoje__destaques" aria-labelledby="areas-destaque-titulo">
          <div className="hoje__destaques-intro">
            <div>
              <p className="eyebrow">Áreas em destaque</p>
              <h3 id="areas-destaque-titulo">Respostas para cenários que exigem mais segurança</h3>
            </div>
            <p>Conteúdo especializado para decisões menos frequentes e de maior complexidade.</p>
          </div>
          <div className="hoje__destaques-grade">
            {AREAS_DESTAQUE.map((area, index) => {
              const total = area.tema
                ? temas.find((tema) => mesmoTema(area.tema || "", tema.theme))?.count
                : undefined;
              return (
                <article className="hoje-area" key={area.nome}>
                  <Link to={area.to} aria-label={`Explorar ${area.nome}`}>
                    <span className="hoje-area__topo">
                      <span className={`hoje-area__icone hoje-area__icone--${area.marca}`}><AreaClinicaIcone area={area.marca} /></span>
                      <span className="hoje-area__numero">{String(index + 1).padStart(2, "0")}</span>
                    </span>
                    <span className="hoje-area__contexto">{area.contexto}</span>
                    <h4>{area.nome}</h4>
                    <p>{area.descricao}</p>
                    <span className="hoje-area__rodape">
                      <small>{total !== undefined ? `${total.toLocaleString("pt-BR")} conteúdos` : "Coleção especializada"}</small>
                      <span>Explorar <Icone nome="seta" /></span>
                    </span>
                  </Link>
                </article>
              );
            })}
          </div>
        </section>

        {temasSecundarios.length > 0 && (
          <section className="hoje__outros-temas" aria-labelledby="outros-temas-titulo">
            <div className="hoje__outros-temas-topo">
              <div>
                <p className="eyebrow">Acervo completo</p>
                <h3 id="outros-temas-titulo">Outras áreas e temas</h3>
              </div>
              <span>{temasSecundarios.length} coleções</span>
            </div>
            <div className="hoje__temas" aria-label="Outras áreas e temas disponíveis">
              {temasSecundarios.map((tema) => (
                <Link key={tema.theme} to={`/biblioteca?tema=${encodeURIComponent(tema.theme)}`}>
                  <span>{tema.theme}</span><small>{tema.count.toLocaleString("pt-BR")}</small>
                </Link>
              ))}
            </div>
          </section>
        )}
      </section>

      <section className="hoje__explorar" aria-labelledby="explorar-titulo">
        <div className="hoje__secao-topo">
          <div><p className="eyebrow">Ecossistema Corvia</p><h2 id="explorar-titulo">Um espaço de trabalho, todas as etapas</h2></div>
        </div>
        <div className="hoje__grupos">
          {GRUPOS.map((grupo) => (
            <article className="hoje-grupo" key={grupo.titulo}>
              <span className="hoje-grupo__icone"><Icone nome={grupo.icone} /></span>
              <div className="hoje-grupo__titulo"><h3>{grupo.titulo}</h3><p>{grupo.descricao}</p></div>
              <div className="hoje-grupo__links">
                {grupo.links.map((link) => <Link key={link.to} to={link.to}>{link.nome}<Icone nome="seta" /></Link>)}
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
