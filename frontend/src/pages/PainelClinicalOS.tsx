import { type FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import MapaDeslocamento, { type RotaDeslocamento } from "../components/MapaDeslocamento";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

type AcaoRapida = { to: string; titulo: string; detalhe: string; icone: NomeIcone; tone: string; featured?: boolean };
type ContextoRecente = { path: string; titulo: string; detalhe: string; icone: NomeIcone; visitadoEm: number };
type Atualizacao = { id: number; slug: string; org: string; title: string; published_at: string; status: "detected" | "aguardando_revisao" | "revisada"; url: string | null };
type RespostaAtualizacoes = { cutoff: string; items: Atualizacao[] };
type Catalogo = { total: number; published_total?: number };
type Contagem = { total?: number };
type Paciente = { id: number };
type Agendamento = { id: number; patient_name: string | null; scheduled_at: string; appointment_type: string; status: string };
type ProximoLocal = {
  target_key: string;
  target_type: "appointment" | "work_routine" | "commitment" | string;
  appointment_id: number | null;
  routine_id: number | null;
  commitment_id?: string | null;
  starts_at: string;
  ends_at: string | null;
  service_name: string;
  title?: string;
  source: "work_routine" | "appointment" | "commitment" | "return";
  arrival_buffer_minutes: number;
  location: { id: number; name: string; address: Record<string, string>; latitude: number | null; longitude: number | null } | null;
};
type PreferenciaMobilidade = {
  enabled: boolean; automatic_foreground_refresh: boolean; refresh_interval_minutes: number;
  traffic_configured: boolean; day_start_origin_mode: "current_location" | "saved_location";
  day_start_location_id: number | null; day_start_location: ProximoLocal["location"];
  day_end_destination_location_id: number | null; day_end_destination_location: ProximoLocal["location"];
};
type ContextoDeslocamentoDia = {
  stage: "before_first" | "active_day" | "at_last" | "no_commitments";
  first_target: ProximoLocal | null; last_target: ProximoLocal | null;
  start_location: ProximoLocal["location"]; end_location: ProximoLocal["location"];
};
type Deslocamento = { status: string; provider?: string; updated_at?: string; destination: ProximoLocal | null; origin_location?: ProximoLocal["location"]; routes: RotaDeslocamento[]; tips: string[] };
type Origem = { latitude: number; longitude: number } | null;
type ConfigMapa = { provider: string; configured: boolean; api_key: string | null };
type EstadoPermissao = "desconhecida" | "concedida" | "negada" | "indisponivel";
type ModuloItem = { to: string; label: string; icon: NomeIcone; adminOnly?: boolean };
type ModuloGrupo = { title: string; tone: "cyan" | "violet" | "blue" | "amber" | "teal" | "slate"; icon: NomeIcone; items: ModuloItem[] };

const ACOES: AcaoRapida[] = [
  { to: "/calculadoras", titulo: "Calculadoras", detalhe: "Escores e índices", icone: "calculadora", tone: "amber" },
  { to: "/assistente", titulo: "CorVIA IA", detalhe: "Assistente Clínica", icone: "assistente", tone: "blue" },
  { to: "/emergencia", titulo: "Emergências", detalhe: "Condutas rápidas", icone: "emergencia", tone: "red" },
  { to: "/diretrizes", titulo: "Guidelines", detalhe: "Diretrizes atuais", icone: "conhecimento", tone: "green" },
  { to: "/exames-ia", titulo: "IA para Exames", detalhe: "Análise cardiovascular multimodal", icone: "ecg", tone: "green", featured: true },
  { to: "/receituario", titulo: "Prescrever", detalhe: "Novo receituário", icone: "prescricao", tone: "cyan" },
  { to: "/documentos", titulo: "Solicitar exames", detalhe: "Adicionar solicitação", icone: "clinica", tone: "blue" },
  { to: "/busca?modo=tudo-com-tudo", titulo: "Tudo com Tudo", detalhe: "Tema completo, organizado por áreas", icone: "busca", tone: "violet" },
];

const MODULOS: ModuloGrupo[] = [
  {
    title: "Clínica & Decisão", tone: "cyan", icon: "clinica", items: [
      { to: "/doencas", label: "Guia de Doenças", icon: "doencas" },
      { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
      { to: "/exames", label: "Exames", icon: "clinica" },
      { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
      { to: "/emergencia", label: "Emergências", icon: "emergencia" },
      { to: "/cardiologia-intensiva", label: "Cardiologia Intensiva & UCO", icon: "clinica" },
      { to: "/checklists", label: "Checklists", icon: "check" },
      { to: "/triagem-sintomas", label: "Triagem de sintomas", icon: "triagem" },
      { to: "/interacoes", label: "Interações medicamentosas", icon: "medicamento" },
      { to: "/condicoes", label: "Condições especiais", icon: "check" },
      { to: "/fluxogramas", label: "Fluxogramas clínicos", icon: "seta" },
      { to: "/avaliacao-preoperatoria", label: "Avaliação pré-operatória", icon: "clinica" },
    ],
  },
  {
    title: "Estudo & Aprendizagem", tone: "violet", icon: "conhecimento", items: [
      { to: "/evidencias", label: "Evidências", icon: "evidencia" },
      { to: "/estudos", label: "Estudos", icon: "evidencia" },
      { to: "/diretrizes", label: "Diretrizes & Guidelines", icon: "conhecimento" },
      { to: "/trilhas/timeline", label: "Timeline do conhecimento", icon: "seta" },
      { to: "/trilhas", label: "Trilhas", icon: "seta" },
      { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
      { to: "/biblioteca", label: "Biblioteca científica", icon: "conhecimento" },
      { to: "/galeria", label: "Atlas & Galeria", icon: "galeria" },
      { to: "/cursos", label: "Cursos & Atualizações", icon: "curso" },
      { to: "/apresentacao", label: "Modo apresentação", icon: "documento" },
    ],
  },
  {
    title: "Trabalho & Assistência", tone: "blue", icon: "pacientes", items: [
      { to: "/exames-ia", label: "IA para Exames · destaque", icon: "ecg" },
      { to: "/round", label: "Pacientes", icon: "pacientes" },
      { to: "/receituario", label: "Prescrição", icon: "prescricao" },
      { to: "/documentos", label: "Documentos & Solicitações", icon: "documento" },
      { to: "/material-paciente", label: "Material para paciente", icon: "documento" },
      { to: "/agenda", label: "Agenda", icon: "agenda" },
      { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
      { to: "/telediagnostico", label: "Telediagnóstico", icon: "evidencia" },
      { to: "/indicadores", label: "Indicadores", icon: "indicadores" },
    ],
  },
  {
    title: "Ferramentas & Produtividade", tone: "amber", icon: "calculadora", items: [
      { to: "/busca?modo=tudo-com-tudo", label: "Tudo com Tudo", icon: "busca" },
      { to: "/calculadoras", label: "Calculadoras avançadas", icon: "calculadora" },
      { to: "/indicadores", label: "Indicadores & Métricas", icon: "indicadores" },
      { to: "/apresentacao", label: "Modo apresentação", icon: "documento" },
      { to: "/exportar", label: "Exportar conteúdo (PDF)", icon: "documento" },
      { to: "/favoritos", label: "Favoritos", icon: "favorito" },
      { to: "/busca", label: "Busca avançada", icon: "busca" },
      { to: "/assistente", label: "Assistente Clínica", icon: "assistente" },
    ],
  },
  {
    title: "Rede & Conectividade", tone: "teal", icon: "sincronizar", items: [
      { to: "/usuarios-online", label: "Rede profissional", icon: "pacientes" },
      { to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" },
      { to: "/telediagnostico", label: "Consultoria / Telediagnóstico", icon: "evidencia" },
      { to: "/material-paciente", label: "Compartilhamento com paciente", icon: "documento" },
    ],
  },
  {
    title: "Administração & Conta", tone: "slate", icon: "gestao", items: [
      { to: "/minha-conta", label: "Minha Conta", icon: "conta" },
      { to: "/tour?origem=assinatura&modo=quick", label: "Tour CorVIA", icon: "check" },
      { to: "/tour", label: "Tour da plataforma", icon: "curso" },
      { to: "/privacidade", label: "Segurança & Privacidade", icon: "check" },
      { to: "/termos", label: "Termos de uso", icon: "documento" },
      { to: "/admin", label: "Painel administrativo", icon: "gestao", adminOnly: true },
      { to: "/admin/usuarios", label: "Usuários & Permissões", icon: "pacientes", adminOnly: true },
      { to: "/fila-telediagnostico", label: "Fila de telediagnóstico", icon: "evidencia", adminOnly: true },
    ],
  },
];

const CONTEXTOS_INICIAIS: ContextoRecente[] = [
  { path: "/doencas", titulo: "Insuficiência Cardíaca (ICFER)", detalhe: "Condição", icone: "doencas", visitadoEm: 0 },
  { path: "/medicamentos?slug=sacubitril-valsartana", titulo: "Sacubitril/Valsartana", detalhe: "Medicamento", icone: "medicamento", visitadoEm: 0 },
  { path: "/evidencias", titulo: "Evidências", detalhe: "Recomendações clínicas", icone: "evidencia", visitadoEm: 0 },
  { path: "/round", titulo: "Paciente", detalhe: "Contexto clínico", icone: "pacientes", visitadoEm: 0 },
  { path: "/calculadoras", titulo: "CHA₂DS₂-VASc", detalhe: "Calculadora", icone: "calculadora", visitadoEm: 0 },
];

const EXEMPLOS = ["tratamento da pericardite", "nebido dose", "critérios de Duke", "prescrever losartana", "calcular CHA₂DS₂-VASc"];

function saudacao() {
  const hora = new Date().getHours();
  if (hora < 12) return "Bom dia";
  if (hora < 18) return "Boa tarde";
  return "Boa noite";
}
function primeiroNome(nome?: string) {
  const partes = (nome || "").trim().split(/\s+/).filter(Boolean);
  const primeira = /^(dr|dra)\.?$/i.test(partes[0] || "") ? partes[1] : partes[0];
  return primeira || "Doutor(a)";
}
function chaveContextosRecentes(userId?: number) { return userId ? `corvia:contextos-recentes:${userId}` : ""; }
function mesmoDia(a: Date, b: Date) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); }
function horario(valor?: string | null) { if (!valor) return "—"; const data = new Date(valor); return Number.isNaN(data.getTime()) ? "—" : data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }); }
function dataCurta(valor: string) { const data = new Date(valor); return Number.isNaN(data.getTime()) ? "" : data.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" }); }
function tempoRelativo(timestamp: number) { if (!timestamp) return "Acesso hoje"; const minutos = Math.max(1, Math.round((Date.now() - timestamp) / 60000)); if (minutos < 60) return `Acesso há ${minutos} min`; const horas = Math.round(minutos / 60); if (horas < 24) return `Acesso há ${horas} h`; return `Acesso há ${Math.round(horas / 24)} d`; }
function statusAtualizacao(item: Atualizacao) { return item.status === "revisada" ? "Principais mudanças nas recomendações" : "Nova publicação detectada para revisão"; }
function transito(valor?: string) { return ({ normal: "livre", leve: "leve", moderado: "moderado", intenso: "intenso" } as Record<string, string>)[valor || ""] || valor || "atualizado"; }
function enderecoDestino(destino?: ProximoLocal | null) {
  if (!destino?.location?.address) return "Endereço a definir";
  const a = destino.location.address;
  return [a.street, a.number, a.city, a.state].filter(Boolean).join(", ") || "Endereço a definir";
}
function destinoDoComando(valor: string) {
  const termo = valor.trim(); const normalizado = termo.toLocaleLowerCase("pt-BR");
  if (/\b(ecg|eletrocardiograma|holter|mapa|ecocardiograma|resson[aâ]ncia|tomografia|exame cardiovascular)\b/.test(normalizado)) return "/exames-ia";
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

export default function PainelClinicalOS() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [comando, setComando] = useState("");
  const [recentes, setRecentes] = useState<ContextoRecente[]>([]);
  const [atualizacoes, setAtualizacoes] = useState<Atualizacao[]>([]);
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [evidencias, setEvidencias] = useState<number | null>(null);
  const [estudos, setEstudos] = useState<number | null>(null);
  const [pacientes, setPacientes] = useState<number | null>(null);
  const [agenda, setAgenda] = useState<Agendamento[]>([]);
  const [proximoAlvo, setProximoAlvo] = useState<ProximoLocal | null>(null);
  const [mobilidade, setMobilidade] = useState<PreferenciaMobilidade | null>(null);
  const [contextoDeslocamento, setContextoDeslocamento] = useState<ContextoDeslocamentoDia | null>(null);
  const [deslocamento, setDeslocamento] = useState<Deslocamento | null>(null);
  const [origem, setOrigem] = useState<Origem>(null);
  const [configMapa, setConfigMapa] = useState<ConfigMapa | null>(null);
  const [permissao, setPermissao] = useState<EstadoPermissao>("desconhecida");
  const [calculandoRota, setCalculandoRota] = useState(false);
  const [erroRota, setErroRota] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const chamadaRotaEmCurso = useRef(false);
  const ultimaRotaEm = useRef(0);

  useEffect(() => { document.body.classList.add("ccc-home-active"); return () => document.body.classList.remove("ccc-home-active"); }, []);

  useEffect(() => {
    const chave = chaveContextosRecentes(usuario?.id);
    if (!chave) return setRecentes([]);
    try { const salvos = JSON.parse(sessionStorage.getItem(chave) || "[]") as ContextoRecente[]; setRecentes(salvos.filter((item) => item?.path && item?.titulo).slice(0, 5)); }
    catch { setRecentes([]); }
  }, [usuario?.id]);

  useEffect(() => {
    api.get<RespostaAtualizacoes>("/guideline-updates").then((r) => setAtualizacoes((r.items ?? []).slice(0, 3))).catch(() => setAtualizacoes([]));
    api.get<Catalogo>("/library/catalog").then(setCatalogo).catch(() => setCatalogo(null));
    api.get<Contagem>("/evidence?limit=1").then((r) => setEvidencias(r.total ?? null)).catch(() => setEvidencias(null));
    api.get<Contagem>("/studies?limit=1").then((r) => setEstudos(r.total ?? null)).catch(() => setEstudos(null));
    api.get<Paciente[]>("/round/patients").then((r) => setPacientes(r.length)).catch(() => setPacientes(null));
    api.get<Array<{ id: number; patient_name: string | null; starts_at: string; appointment_type: string; status: string }>>("/agenda/appointments").then((items) => setAgenda(items.map((item) => ({ id: item.id, patient_name: item.patient_name, scheduled_at: item.starts_at, appointment_type: item.appointment_type, status: item.status })))).catch(() => setAgenda([]));
    api.post<ProximoLocal | null>("/agenda/mobility/prepare-next-target", {}).catch(() => api.get<ProximoLocal | null>("/agenda/mobility/next-target")).then(setProximoAlvo).catch(() => setProximoAlvo(null));
    api.get<PreferenciaMobilidade>("/agenda/mobility/preferences").then(setMobilidade).catch(() => setMobilidade(null));
    api.get<ContextoDeslocamentoDia>("/agenda/mobility/day-context").then(setContextoDeslocamento).catch(() => setContextoDeslocamento(null));
    api.get<ConfigMapa>("/agenda/mobility/map-config").then(setConfigMapa).catch(() => setConfigMapa(null));
  }, []);

  useEffect(() => {
    if (!mobilidade?.enabled) { setPermissao("desconhecida"); return; }
    if (!navigator.geolocation) { setPermissao("indisponivel"); return; }
    if (!navigator.permissions?.query) return;
    let ativo = true;
    let status: PermissionStatus | null = null;
    navigator.permissions.query({ name: "geolocation" }).then((resultado) => {
      if (!ativo) return;
      status = resultado;
      const aplicar = () => setPermissao(resultado.state === "granted" ? "concedida" : resultado.state === "denied" ? "negada" : "desconhecida");
      aplicar();
      resultado.onchange = aplicar;
    }).catch(() => undefined);
    return () => { ativo = false; if (status) status.onchange = null; };
  }, [mobilidade?.enabled]);

  useEffect(() => {
    function focar(evento: KeyboardEvent) { if (evento.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") { evento.preventDefault(); inputRef.current?.focus(); } }
    document.addEventListener("keydown", focar); return () => document.removeEventListener("keydown", focar);
  }, []);

  const contextos = useMemo(() => recentes.length ? recentes : CONTEXTOS_INICIAIS, [recentes]);
  const compromissosHoje = useMemo(() => agenda.filter((item) => item.status !== "cancelado" && mesmoDia(new Date(item.scheduled_at), new Date())).sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at)), [agenda]);
  const proximoAgenda = useMemo(() => agenda.filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= Date.now()).sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0], [agenda]);
  const retornoAtivo = Boolean(contextoDeslocamento?.stage === "at_last" && contextoDeslocamento.last_target && contextoDeslocamento.end_location);
  const destinoPlanejado = useMemo<ProximoLocal | null>(() => {
    if (!retornoAtivo || !contextoDeslocamento?.last_target || !contextoDeslocamento.end_location) return proximoAlvo;
    const ultimo = contextoDeslocamento.last_target;
    const local = contextoDeslocamento.end_location;
    return {
      target_key: `return:${ultimo.target_key}:${local.id}`, target_type: "day_return",
      appointment_id: null, routine_id: null, commitment_id: null,
      starts_at: ultimo.ends_at || ultimo.starts_at, ends_at: null,
      service_name: "Retorno", title: `Retorno para ${local.name}`, source: "return",
      arrival_buffer_minutes: 0, location: local,
    };
  }, [contextoDeslocamento, proximoAlvo, retornoAtivo]);
  const destino = deslocamento && deslocamento.destination?.target_key === destinoPlanejado?.target_key
    ? deslocamento.destination
    : destinoPlanejado;
  const targetKey = destinoPlanejado?.target_key || null;
  const proximo = useMemo<Agendamento | undefined>(() => destinoPlanejado ? ({
    id: destinoPlanejado.appointment_id || 0,
    patient_name: destinoPlanejado.title || destinoPlanejado.location?.name || destinoPlanejado.service_name || null,
    scheduled_at: destinoPlanejado.starts_at,
    appointment_type: destinoPlanejado.service_name || "Compromisso",
    status: "confirmado",
  }) : proximoAgenda, [destinoPlanejado, proximoAgenda]);
  const pendencias = useMemo(() => agenda.filter((item) => ["pendente", "pending_external", "proposed"].includes(item.status)).length, [agenda]);
  const rota = deslocamento?.destination?.target_key === targetKey ? deslocamento?.routes?.[0] : undefined;
  const saidaPlanejada = destino && rota && proximo ? retornoAtivo
    ? new Date(proximo.scheduled_at)
    : new Date(new Date(proximo.scheduled_at).getTime() - (rota.duration_seconds + destino.arrival_buffer_minutes * 60) * 1000) : null;
  // Enquanto a saída ainda é futura, preserva a janela planejada do compromisso.
  // Depois que essa janela passou, o card precisa refletir a rota viva — não um horário histórico.
  const agora = new Date();
  const rotaAtualizadaEm = deslocamento?.updated_at ? new Date(deslocamento.updated_at) : agora;
  const referenciaRota = Number.isNaN(rotaAtualizadaEm.getTime())
    ? agora
    : new Date(Math.max(agora.getTime(), rotaAtualizadaEm.getTime()));
  const rotaAtualizadaAgora = !retornoAtivo && saidaPlanejada && referenciaRota.getTime() > saidaPlanejada.getTime();
  const saidaRecomendada = rotaAtualizadaAgora ? referenciaRota : saidaPlanejada;
  const chegadaPrevista = rota && proximo && destino ? retornoAtivo
    ? new Date(new Date(proximo.scheduled_at).getTime() + rota.duration_seconds * 1000)
    : rotaAtualizadaAgora && saidaRecomendada
      ? new Date(saidaRecomendada.getTime() + rota.duration_seconds * 1000)
      : new Date(new Date(proximo.scheduled_at).getTime() - destino.arrival_buffer_minutes * 60000) : null;
  const destinoMapeavel = Boolean(destino?.location && destino.location.latitude != null && destino.location.longitude != null);
  const provedorMapa = deslocamento?.provider || configMapa?.provider;
  const usaOrigemSalva = retornoAtivo || Boolean(
    contextoDeslocamento?.stage === "before_first"
    && mobilidade?.day_start_origin_mode === "saved_location"
    && mobilidade.day_start_location_id,
  );
  const origemPlanejada = deslocamento?.origin_location || (retornoAtivo
    ? contextoDeslocamento?.last_target?.location
    : usaOrigemSalva ? contextoDeslocamento?.start_location : null);
  const origemMapa = origem || (origemPlanejada?.latitude != null && origemPlanejada.longitude != null
    ? { latitude: origemPlanejada.latitude, longitude: origemPlanejada.longitude } : null);
  const origemNome = origemPlanejada?.name || (origem ? "Sua localização atual" : "Localização atual");

  useEffect(() => {
    setDeslocamento(null);
    setOrigem(null);
    setErroRota(null);
    ultimaRotaEm.current = 0;
  }, [targetKey]);

  const calcularDeslocamento = useCallback((solicitarPermissao = false) => {
    if (!mobilidade?.enabled || !proximo || !destino || !targetKey || !destino.location) return;
    if (chamadaRotaEmCurso.current) return;
    if (!usaOrigemSalva && (!navigator.geolocation || (!solicitarPermissao && permissao !== "concedida"))) return;

    chamadaRotaEmCurso.current = true;
    setCalculandoRota(true);
    setErroRota(null);
    const aplicarResultado = (resultado: Deslocamento) => {
        if (resultado.destination?.target_key !== targetKey) {
          setDeslocamento({ ...resultado, status: "destination_mismatch", destination: null, routes: [] });
          setErroRota("O destino retornado não corresponde ao compromisso exibido.");
          return;
        }
        setDeslocamento(resultado);
        if (resultado.origin_location?.latitude != null && resultado.origin_location.longitude != null) {
          setOrigem({ latitude: resultado.origin_location.latitude, longitude: resultado.origin_location.longitude });
        }
        // Mantém a referência do alvo quando o conteúdo é idêntico — o objeto novo
        // a cada refresh invalidava deps e recriava o mapa sem necessidade.
        if (!retornoAtivo) setProximoAlvo((atual) => atual && resultado.destination && JSON.stringify(atual) === JSON.stringify(resultado.destination) ? atual : resultado.destination);
        ultimaRotaEm.current = Date.now();
        if (!resultado.routes?.length && resultado.status !== "ok") {
          const mensagem = resultado.status === "origin_not_geocoded"
            ? "Não foi possível localizar com segurança o ponto de partida salvo."
            : resultado.status === "destination_not_geocoded"
            ? "Não foi possível localizar com segurança o endereço deste compromisso. Complete o local na Agenda."
            : resultado.status === "destination_without_location"
              ? "Este compromisso ainda não possui um local definido."
              : "O provedor não retornou uma rota utilizável.";
          setErroRota(mensagem);
        }
    };
    const concluir = () => {
      chamadaRotaEmCurso.current = false;
      setCalculandoRota(false);
    };
    if (retornoAtivo && contextoDeslocamento?.last_target && mobilidade.day_end_destination_location_id) {
      api.post<Deslocamento>("/agenda/mobility/commute-return", {
        origin_target_key: contextoDeslocamento.last_target.target_key,
        destination_location_id: mobilidade.day_end_destination_location_id,
      }).then(aplicarResultado).catch(() => {
        setErroRota("Não foi possível atualizar a rota agora.");
      }).finally(concluir);
      return;
    }
    if (usaOrigemSalva && mobilidade.day_start_location_id) {
      api.post<Deslocamento>("/agenda/mobility/commute-target-from-location", {
        origin_location_id: mobilidade.day_start_location_id, target_key: targetKey,
      }).then(aplicarResultado).catch(() => {
        setErroRota("Não foi possível atualizar a rota agora.");
      }).finally(concluir);
      return;
    }
    navigator.geolocation.getCurrentPosition((position) => {
      const origemAtual = { latitude: position.coords.latitude, longitude: position.coords.longitude };
      setOrigem((atual) => atual && atual.latitude === origemAtual.latitude && atual.longitude === origemAtual.longitude ? atual : origemAtual);
      setPermissao("concedida");
      api.post<Deslocamento>("/agenda/mobility/commute-target", {
        ...origemAtual, target_key: targetKey,
      }).then(aplicarResultado).catch(() => {
        setErroRota("Não foi possível atualizar a rota agora.");
      }).finally(concluir);
    }, (erro) => {
      if (erro.code === erro.PERMISSION_DENIED) { setPermissao("negada"); setErroRota("A localização foi negada no navegador."); }
      else setErroRota("Não foi possível obter sua localização atual.");
      concluir();
    }, { enableHighAccuracy: false, timeout: 8000, maximumAge: 120000 });
  }, [contextoDeslocamento, destino, mobilidade, permissao, proximo, retornoAtivo, targetKey, usaOrigemSalva]);

  useEffect(() => {
    if (!mobilidade?.enabled || !mobilidade.automatic_foreground_refresh || (!usaOrigemSalva && permissao !== "concedida") || !destino || !targetKey) return;
    const intervaloMs = Math.max(2, mobilidade.refresh_interval_minutes || 5) * 60000;
    const atualizarSeVisivel = () => {
      if (document.visibilityState !== "visible") return;
      if (Date.now() - ultimaRotaEm.current < intervaloMs && ultimaRotaEm.current) return;
      calcularDeslocamento(false);
    };
    atualizarSeVisivel();
    const timer = window.setInterval(atualizarSeVisivel, intervaloMs);
    const visibilidade = () => { if (document.visibilityState === "visible") atualizarSeVisivel(); };
    document.addEventListener("visibilitychange", visibilidade);
    return () => { window.clearInterval(timer); document.removeEventListener("visibilitychange", visibilidade); };
  }, [calcularDeslocamento, destino, mobilidade?.automatic_foreground_refresh, mobilidade?.enabled, mobilidade?.refresh_interval_minutes, permissao, targetKey, usaOrigemSalva]);

  function executar(evento: FormEvent) { evento.preventDefault(); if (comando.trim().length < 2) return; navigate(destinoDoComando(comando)); }
  function usarExemplo(texto: string) { setComando(texto); inputRef.current?.focus(); }
  function abrirAssistentePessoal() { window.dispatchEvent(new Event("corvia:abrir-assistente-pessoal")); }

  const descricaoDeslocamento = !proximo
    ? "Sem compromisso futuro"
    : !destino
      ? "Este compromisso não possui endereço/local disponível para rota"
      : !destino.location
        ? "Este compromisso ainda não possui local definido"
        : !mobilidade?.enabled
          ? "Mobilidade desabilitada"
          : !usaOrigemSalva && permissao === "negada"
            ? "Localização negada no navegador"
            : !mobilidade.traffic_configured
              ? "Provider de trânsito indisponível"
              : calculandoRota
                ? "Calculando rota com trânsito atual..."
                : rota
                  ? `${Math.ceil(rota.duration_seconds / 60)} min · ${(rota.distance_meters / 1000).toFixed(1)} km · trânsito ${transito(rota.congestion)}`
                  : erroRota || (destino.location.latitude == null || destino.location.longitude == null ? "Localizando destino para calcular a rota" : usaOrigemSalva ? `Mapa pronto · calcular a partir de ${origemNome}` : "Mapa pronto · permita sua localização para calcular a rota");

  const grupos = MODULOS.map((grupo) => ({ ...grupo, items: grupo.items.filter((item) => !item.adminOnly || usuario?.role === "admin") })).filter((grupo) => grupo.items.length);

  return (
    <div className="ccc-home ccc-home--board ccc-reference-board">
      <main className="ccc-home__main">
        <header className="ccc-home__welcome">
          <h1>{saudacao()}, Dr. {primeiroNome(usuario?.full_name)}! <span aria-hidden="true">👋</span></h1>
          <p>O que você precisa resolver agora?</p>
        </header>

        <form className="ccc-command" onSubmit={executar} role="search">
          <Icone nome="busca" />
          <input ref={inputRef} value={comando} onChange={(e) => setComando(e.target.value)} placeholder="Pergunte, pesquise ou execute uma ação..." aria-label="Pergunte, pesquise ou execute uma ação" autoComplete="off" />
          <kbd>⌘ K</kbd>
          <button type="submit" aria-label="Executar comando"><Icone nome="seta" /></button>
        </form>
        <div className="ccc-examples" aria-label="Exemplos de comandos"><span>Exemplos:</span>{EXEMPLOS.map((texto) => <button key={texto} type="button" onClick={() => usarExemplo(texto)}>{texto}</button>)}</div>

        <section className="ccc-section ccc-actions-section" aria-labelledby="ccc-actions-title">
          <div className="ccc-section__head"><h2 id="ccc-actions-title">Ações rápidas</h2><Link to="/busca"><Icone nome="configuracao" /> Personalizar</Link></div>
          <div className="ccc-actions">{ACOES.map((acao) => <Link to={acao.to} key={acao.titulo} className={`ccc-action ccc-action--${acao.icone}${acao.featured ? " is-featured" : ""}`} data-tone={acao.tone}>{acao.featured && <em className="ccc-action__featured">Destaque</em>}<span className="ccc-action__icon"><Icone nome={acao.icone} /></span><span><strong>{acao.titulo}</strong><small>{acao.detalhe}</small></span></Link>)}</div>
        </section>

        <section className="ccc-mobile-summary ccc-reference-summary" aria-label="Resumo do dia e próximo deslocamento">
          <Link className="ccc-mobile-summary__card ccc-reference-day" to="/agenda"><span><small>Seu dia</small><strong>{compromissosHoje.length} compromisso{compromissosHoje.length === 1 ? "" : "s"} hoje</strong><p>{proximo ? `Próximo: ${horario(proximo.scheduled_at)} · ${proximo.patient_name || "Compromisso"}` : "Agenda livre para novos compromissos"}</p></span><Icone nome="agenda" /></Link>

          <article className="ccc-mobile-commute ccc-reference-commute" aria-label="Próximo Deslocamento">
            <header>
              <span><small>{retornoAtivo ? "Retorno do último compromisso" : "Próximo Deslocamento"}</small><strong>{destino?.location?.name || proximo?.patient_name || "Próximo compromisso"}</strong>{proximo && <p>{proximo.appointment_type} · {horario(proximo.scheduled_at)}</p>}</span>
              <span className="ccc-mobile-commute__icon"><Icone nome="rota" /></span>
            </header>
            <div className="ccc-reference-commute__details">
              <div className="ccc-reference-commute__route">
                <span><small>Saída às</small><strong>{saidaRecomendada ? horario(saidaRecomendada.toISOString()) : "—"}</strong><p>{rota ? `Em ${Math.ceil(rota.duration_seconds / 60)} min` : "Horário calculado com trânsito"}</p></span>
                <span className="ccc-reference-commute__point"><i className="is-origin" /><small>Origem</small><strong>{origemNome}</strong></span>
                <span className="ccc-reference-commute__point"><i className="is-destination" /><small>Destino</small><strong>{destino?.location?.name || "A definir"}</strong><p>{enderecoDestino(destino)}</p></span>
              </div>
              <div className="ccc-mobile-commute__metrics">
                <span><small>Tempo estimado</small><strong>{rota ? `${Math.ceil(rota.duration_seconds / 60)} min` : "—"}</strong></span>
                <span><small>Distância</small><strong>{rota ? `${(rota.distance_meters / 1000).toFixed(1)} km` : "—"}</strong></span>
                <span><small>Trânsito ao vivo</small><strong>{rota ? transito(rota.congestion) : "—"}</strong></span>
                <span><small>Chegada</small><strong>{chegadaPrevista ? horario(chegadaPrevista.toISOString()) : "—"}</strong></span>
              </div>
              {!rota && <div className={`ccc-mobile-commute__state${calculandoRota ? " is-loading" : ""}`}><span><Icone nome={calculandoRota ? "sincronizar" : destinoMapeavel ? "rota" : "pin"} /></span><p>{descricaoDeslocamento}</p></div>}
              <footer><Link to="/agenda">{rota ? "Ver rota" : "Abrir Agenda"} <Icone nome="seta" /></Link>{mobilidade?.enabled && destino?.location && (!mobilidade.automatic_foreground_refresh || !rota || erroRota) && <button type="button" onClick={() => calcularDeslocamento(true)} disabled={calculandoRota}>{calculandoRota ? "Atualizando..." : !usaOrigemSalva && permissao === "negada" ? "Tentar novamente" : rota ? "Atualizar rota" : "Calcular rota"}</button>}</footer>
            </div>
            <div className="ccc-mobile-commute__map ccc-reference-commute__map">
              {destinoMapeavel && destino?.location ? <MapaDeslocamento compact rotas={deslocamento?.routes || []} origem={origemMapa} destino={{ latitude: destino.location.latitude, longitude: destino.location.longitude, name: destino.location.name }} provider={provedorMapa} updatedAt={deslocamento?.updated_at} googleMapsApiKey={configMapa?.api_key} /> : <div className="ccc-reference-map-empty"><Icone nome="rota" /><strong>{retornoAtivo ? "Mapa do retorno" : "Mapa do próximo deslocamento"}</strong><span>{descricaoDeslocamento}</span></div>}
            </div>
          </article>

          <button className="ccc-mobile-summary__card ccc-mobile-summary__card--assistant ccc-reference-assistant-summary" type="button" onClick={abrirAssistentePessoal}><span><small>Assistente</small><strong>{pendencias || pacientes || 0} item(ns) para acompanhar</strong><p>Agenda, pendências e comunicação</p></span><span className="ccc-spark">✦</span></button>
          <Link className="ccc-mobile-summary__card ccc-reference-updates-summary" to="/diretrizes"><span><small>Atualizações</small><strong>{atualizacoes.length ? `${atualizacoes.length} atualização(ões)` : "Central científica"}</strong><p>{atualizacoes[0]?.title || "Guidelines e estudos recentes"}</p></span><Icone nome="evidencia" /></Link>
        </section>

        <section className="ccc-section ccc-updates-section ccc-reference-updates" aria-labelledby="ccc-updates-title">
          <div className="ccc-section__head"><h2 id="ccc-updates-title">Atualizações importantes para você</h2><Link to="/diretrizes">Ver central <Icone nome="seta" /></Link></div>
          <div className="ccc-updates ccc-reference-update-strip">
            {atualizacoes.length ? atualizacoes.slice(0, 3).map((item, indice) => <Link to="/diretrizes" key={item.id} className={`ccc-update ccc-update--${indice + 1}`}><small>{item.org || "Atualização científica"} · {dataCurta(item.published_at)}</small><strong>{item.title}</strong><p>{statusAtualizacao(item)}</p><span>{indice === 0 ? "Ver o que mudou" : indice === 1 ? "Resumo do estudo" : "Saiba mais"} <Icone nome="seta" /></span></Link>) : <Link to="/diretrizes" className="ccc-update ccc-update--empty"><small>Central científica</small><strong>Atualizações clínicas revisadas</strong><p>Novas publicações oficiais aparecem aqui quando detectadas.</p><span>Abrir central <Icone nome="seta" /></span></Link>}
            {contextos.slice(0, 3).map((item) => <Link key={item.path} to={item.path} className="ccc-reference-context"><span><Icone nome={item.icone} /></span><div><small>{item.detalhe}</small><strong>{item.titulo}</strong><p>{tempoRelativo(item.visitadoEm)}</p></div></Link>)}
          </div>
        </section>

        <section className="ccc-section ccc-module-directory" aria-labelledby="ccc-modules-title">
          <div className="ccc-section__head"><h2 id="ccc-modules-title">CorVIA Clinical OS</h2><Link to="/busca">Explorar tudo <Icone nome="seta" /></Link></div>
          <div className="ccc-module-directory__grid">
            {grupos.map((grupo) => <article key={grupo.title} className="ccc-module-group" data-tone={grupo.tone}>
              <header><span><Icone nome={grupo.icon} /></span><strong>{grupo.title}</strong></header>
              <nav aria-label={grupo.title}>{grupo.items.map((item) => <Link key={`${grupo.title}-${item.to}-${item.label}`} to={item.to}><span><Icone nome={item.icon} />{item.label}</span><Icone nome="chevron" /></Link>)}</nav>
            </article>)}
          </div>
        </section>

        <section className="ccc-reference-trust" aria-label="Pilares do CorVIA">
          <div><Icone nome="assistente" /><span><strong>Inteligência clínica</strong><small>Contexto e apoio à decisão.</small></span></div>
          <div><Icone nome="evidencia" /><span><strong>Evidências atualizadas</strong><small>Conteúdo validado e rastreável.</small></span></div>
          <div><Icone nome="sincronizar" /><span><strong>Integração Tudo com Tudo</strong><small>Dados, pessoas e ferramentas conectados.</small></span></div>
          <div><Icone nome="check" /><span><strong>Segurança e privacidade</strong><small>Ambiente profissional e auditável.</small></span></div>
          <div><Icone nome="clinica" /><span><strong>Feito para médicos</strong><small>Prática clínica real no centro.</small></span></div>
        </section>
      </main>

      <aside className="ccc-home__intelligence" aria-label="CorVIA Intelligence">
        <section className="ccc-rail-card ccc-intelligence-card">
          <header><span><Icone nome="assistente" /> CorVIA Intelligence</span><Link to="/busca">Ver tudo</Link></header>
          <div className="ccc-intelligence-list">
            <Link to="/diretrizes"><span><Icone nome="evidencia" /></span><strong>{atualizacoes.length || "—"}</strong><p>atualizações científicas nas últimas 24 horas</p></Link>
            <Link to="/diretrizes"><span><Icone nome="conhecimento" /></span><strong>{atualizacoes[0] ? "1" : "—"}</strong><p>{atualizacoes[0]?.title || "Guideline nova"}</p></Link>
            <Link to="/biblioteca" title="O total conta registros canônicos únicos; aprofundamentos, revisões e vínculos Tudo com Tudo não duplicam o mesmo conteúdo."><span><Icone nome="check" /></span><strong>{catalogo?.published_total ?? catalogo?.total ?? "—"}</strong><p>conteúdos únicos publicados · +{Math.max((catalogo?.published_total ?? catalogo?.total ?? 9452) - 9452, 0)} novos desde 26/08</p></Link>
            <Link to={contextos[0]?.path || "/busca"}><span><Icone nome={contextos[0]?.icone || "busca"} /></span><strong>↻</strong><p>Continuar: {contextos[0]?.titulo || "última pesquisa"}</p></Link>
          </div>
          <Link to="/busca" className="ccc-intelligence-graph"><span>◎</span><span><strong>Explorar relações</strong><small>Tudo com Tudo</small></span><Icone nome="seta" /></Link>
          <div className="ccc-intelligence-metrics"><span><strong>{evidencias ?? "—"}</strong><small>evidências</small></span><span><strong>{estudos ?? "—"}</strong><small>estudos</small></span></div>
        </section>
      </aside>

      <aside className="ccc-home__assistant" aria-label="Assistente Pessoal">
        <section className="ccc-rail-card ccc-assistant-card ccc-assistant-card--window">
          <header><span><span className="ccc-spark">✦</span> Assistente Pessoal</span><span className="ccc-assistant-window-controls" aria-hidden="true"><i>−</i><i>×</i></span></header>
          <div className="ccc-assistant-greeting"><span className="ccc-spark">✦</span><div><strong>{saudacao()}, Dr. {primeiroNome(usuario?.full_name)}!</strong><small>Aqui está o resumo do seu dia.</small></div></div>
          <div className="ccc-assistant-block"><small>Seu dia</small><div className="ccc-assistant-row"><span><Icone nome="agenda" /></span><div><strong>{compromissosHoje.length} compromisso{compromissosHoje.length === 1 ? "" : "s"}</strong><p>{proximo ? `${dataCurta(proximo.scheduled_at)} · ${horario(proximo.scheduled_at)}` : "Nenhum compromisso pendente"}</p></div></div></div>
          <div className="ccc-assistant-block"><small>Próximo compromisso</small><div className="ccc-assistant-row"><span><Icone nome="pin" /></span><div><strong>{destino?.location?.name || proximo?.patient_name || "Agenda disponível"}</strong><p>{destino ? `${destino.service_name} · ${horario(proximo?.scheduled_at)}` : proximo ? `${proximo.appointment_type} · ${horario(proximo.scheduled_at)}` : "Sem próximo compromisso definido"}</p></div></div><Link to="/agenda" className="ccc-assistant-inline-action">Ver agenda</Link></div>
          <div className="ccc-assistant-block ccc-assistant-block--commute"><small>{retornoAtivo ? "Retorno do último compromisso" : "Próximo Deslocamento"}</small><div className="ccc-assistant-row"><span><Icone nome="rota" /></span><div><strong>{saidaRecomendada ? `Sair às ${horario(saidaRecomendada.toISOString())}` : descricaoDeslocamento}</strong><p>{rota ? `${Math.ceil(rota.duration_seconds / 60)} min · ${(rota.distance_meters / 1000).toFixed(1)} km${rota.traffic_delay_seconds > 0 ? ` · +${Math.ceil(rota.traffic_delay_seconds / 60)} min` : ""}` : destinoMapeavel ? (usaOrigemSalva ? `Origem: ${origemNome}` : "Destino localizado no mapa; rota depende da localização atual.") : "A rota nunca é substituída por outro compromisso."}</p></div></div>
            {destinoMapeavel && destino?.location && <div className="ccc-assistant-commute-map"><MapaDeslocamento rotas={deslocamento?.routes || []} origem={origemMapa} destino={{ latitude: destino.location.latitude, longitude: destino.location.longitude, name: destino.location.name }} provider={provedorMapa} updatedAt={deslocamento?.updated_at} googleMapsApiKey={configMapa?.api_key} /></div>}
            <div className="ccc-assistant-commute-actions"><Link to="/agenda" className="ccc-assistant-inline-action">Ver agenda</Link>{mobilidade?.enabled && destino?.location && <button type="button" className="ccc-assistant-inline-action" onClick={() => calcularDeslocamento(true)} disabled={calculandoRota}>{calculandoRota ? "Atualizando…" : rota ? "Atualizar rota" : "Calcular rota"}</button>}</div>
          </div>
          <div className="ccc-assistant-block"><small>Pendências</small><div className="ccc-assistant-checks"><span><i />{pendencias} agendamento{pendencias === 1 ? "" : "s"} a revisar</span><span><i />{pacientes ?? 0} paciente{pacientes === 1 ? "" : "s"} no round</span></div></div>
          <button type="button" className="ccc-assistant-input" onClick={abrirAssistentePessoal}><span>Pergunte ou peça algo...</span><Icone nome="assistente" /></button>
        </section>
      </aside>
    </div>
  );
}
