import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";
import "../styles/admin-assinantes.css";

/** Lista pesquisável/paginada de assinantes (ficha administrativa completa,
 * issue de estabilização pré-lançamento, 11/08/2026). Consome
 * `GET /api/admin/usuarios` — backend já pronto e testado
 * (backend/app/api/admin.py, `listar_usuarios_ficha`). Clicar numa linha
 * leva para a ficha completa em `/admin/usuarios/:id`
 * (AdminFichaAssinante.tsx). */

type ItemUsuario = {
  id: number;
  full_name: string;
  email: string;
  cpf_mascarado: string | null;
  profession: string | null;
  council_name: string | null;
  council_number: string | null;
  council_state: string | null;
  created_at: string;
  status: string;
  convidado: boolean;
  investidor: boolean;
  kyc_status: string | null;
  kyc_aprovado_em: string | null;
  kyc_liberado_em: string | null;
  subscription_status: string | null;
  subscription_plano: string | null;
  subscription_periodicidade: string | null;
};

type ListaResposta = {
  items: ItemUsuario[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
};

const STATUS_CONTA: Record<string, string> = {
  pendente: "Pendente", aprovado: "Aprovado", rejeitado: "Rejeitado",
};

const STATUS_KYC: Record<string, string> = {
  sem_kyc: "Sem KYC",
  aguardando_revisao: "Aguardando revisão",
  liberado_conselho_ok: "Liberado (conselho)",
  liberado_sem_checagem: "Liberado (sem checagem)",
  aprovado: "Aprovado",
  rejeitado: "Rejeitado",
  reenvio_solicitado: "Reenvio solicitado",
};

const STATUS_ASSINATURA: Record<string, string> = {
  sem_assinatura: "Sem assinatura",
  inativo: "Inativo",
  ativo: "Ativo",
  teste: "Teste",
  pendente: "Pendente",
  inadimplente: "Inadimplente",
  suspenso: "Suspenso",
  cancelado: "Cancelado",
  pausado: "Pausado",
};

const PLANO_ROTULO: Record<string, string> = { basico: "Básico", completo: "Completo" };

function seloContaClasse(status: string): string {
  if (status === "aprovado") return "selo selo--sucesso";
  if (status === "rejeitado") return "selo selo--atencao";
  return "selo";
}

function seloKycClasse(status: string | null): string {
  if (!status || status === "sem_kyc") return "selo selo--neutro";
  if (status === "aprovado" || status === "liberado_conselho_ok" || status === "liberado_sem_checagem") return "selo selo--sucesso";
  if (status === "rejeitado") return "selo selo--atencao";
  return "selo";
}

function seloAssinaturaClasse(status: string | null): string {
  if (!status || status === "sem_assinatura" || status === "inativo") return "selo selo--neutro";
  if (status === "ativo" || status === "teste") return "selo selo--sucesso";
  if (status === "inadimplente" || status === "suspenso" || status === "cancelado") return "selo selo--atencao";
  return "selo";
}

function formatarData(iso: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("pt-BR");
  } catch {
    return "—";
  }
}

const PAGE_SIZE = 20;

type Filtros = {
  q: string;
  status: string;
  kycStatus: string;
  subscriptionStatus: string;
  convidado: string;
  investidor: string;
  page: number;
};

const FILTROS_INICIAIS: Filtros = {
  q: "", status: "", kycStatus: "", subscriptionStatus: "", convidado: "", investidor: "", page: 1,
};

export default function AdminAssinantes() {
  const navigate = useNavigate();
  const [qInput, setQInput] = useState("");
  const [filtros, setFiltros] = useState<Filtros>(FILTROS_INICIAIS);
  const [resposta, setResposta] = useState<ListaResposta | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    const id = setTimeout(() => {
      setFiltros((f) => (f.q === qInput.trim() ? f : { ...f, q: qInput.trim(), page: 1 }));
    }, 400);
    return () => clearTimeout(id);
  }, [qInput]);

  useEffect(() => {
    setCarregando(true);
    setErro("");
    const params = new URLSearchParams();
    if (filtros.q) params.set("q", filtros.q);
    if (filtros.status) params.set("status", filtros.status);
    if (filtros.kycStatus) params.set("kyc_status", filtros.kycStatus);
    if (filtros.subscriptionStatus) params.set("subscription_status", filtros.subscriptionStatus);
    if (filtros.convidado) params.set("convidado", filtros.convidado === "sim" ? "true" : "false");
    if (filtros.investidor) params.set("investidor", filtros.investidor === "sim" ? "true" : "false");
    params.set("page", String(filtros.page));
    params.set("page_size", String(PAGE_SIZE));

    api.get<ListaResposta>(`/admin/usuarios?${params.toString()}`)
      .then(setResposta)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar a lista de assinantes."))
      .finally(() => setCarregando(false));
  }, [filtros]);

  function aplicar(mudanca: Partial<Omit<Filtros, "page">>) {
    setFiltros((f) => ({ ...f, ...mudanca, page: 1 }));
  }

  function limparFiltros() {
    setQInput("");
    setFiltros(FILTROS_INICIAIS);
  }

  const filtroAtivo = !!(filtros.q || filtros.status || filtros.kycStatus || filtros.subscriptionStatus || filtros.convidado || filtros.investidor);
  const inicio = resposta && resposta.total > 0 ? (resposta.page - 1) * resposta.page_size + 1 : 0;
  const fim = resposta ? Math.min(resposta.page * resposta.page_size, resposta.total) : 0;

  return (
    <>
      <p className="eyebrow">Administração</p>
      <h1>Assinantes</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "76ch" }}>
        Consulte a ficha completa ou use <strong>Gerenciar</strong> para alterar dados/senha e, quando permitido,
        excluir definitivamente contas gratuitas ou de demonstração junto com o CorVIA Mail.
      </p>

      <div className="admin-assinantes__filtros">
        <div className="admin-assinantes__campo admin-assinantes__campo--busca"><label htmlFor="aa-busca">Buscar</label><input id="aa-busca" type="search" placeholder="Nome, e-mail, CPF ou nº do conselho" value={qInput} onChange={(e) => setQInput(e.target.value)} /></div>
        <div className="admin-assinantes__campo"><label htmlFor="aa-status">Status da conta</label><select id="aa-status" value={filtros.status} onChange={(e) => aplicar({ status: e.target.value })}><option value="">Todos</option>{Object.entries(STATUS_CONTA).map(([v, r]) => <option key={v} value={v}>{r}</option>)}</select></div>
        <div className="admin-assinantes__campo"><label htmlFor="aa-kyc">Verificação (KYC)</label><select id="aa-kyc" value={filtros.kycStatus} onChange={(e) => aplicar({ kycStatus: e.target.value })}><option value="">Todos</option>{Object.entries(STATUS_KYC).map(([v, r]) => <option key={v} value={v}>{r}</option>)}</select></div>
        <div className="admin-assinantes__campo"><label htmlFor="aa-assinatura">Assinatura</label><select id="aa-assinatura" value={filtros.subscriptionStatus} onChange={(e) => aplicar({ subscriptionStatus: e.target.value })}><option value="">Todas</option>{Object.entries(STATUS_ASSINATURA).map(([v, r]) => <option key={v} value={v}>{r}</option>)}</select></div>
        <div className="admin-assinantes__campo"><label htmlFor="aa-convidado">Convidado</label><select id="aa-convidado" value={filtros.convidado} onChange={(e) => aplicar({ convidado: e.target.value })}><option value="">Indiferente</option><option value="sim">Sim</option><option value="nao">Não</option></select></div>
        <div className="admin-assinantes__campo"><label htmlFor="aa-investidor">Investidor</label><select id="aa-investidor" value={filtros.investidor} onChange={(e) => aplicar({ investidor: e.target.value })}><option value="">Indiferente</option><option value="sim">Sim</option><option value="nao">Não</option></select></div>
        {filtroAtivo && <button type="button" className="admin-assinantes__limpar" onClick={limparFiltros}>Limpar filtros</button>}
      </div>

      {erro && <Erro mensagem={erro} />}

      {carregando && !resposta ? <Carregando texto="Carregando assinantes…" /> : resposta && resposta.items.length === 0 ? (
        <Vazio titulo="Nenhum assinante encontrado" acao="Ajuste os filtros ou o termo de busca." />
      ) : resposta ? (
        <>
          <p className="admin-assinantes__resumo">Mostrando {inicio}–{fim} de {resposta.total}{carregando ? " · atualizando…" : ""}</p>
          <div className="admin-assinantes__tabela-wrap">
            <table className="admin-assinantes__tabela">
              <thead><tr><th>Nome / e-mail</th><th>CPF</th><th>Conselho</th><th>Profissão</th><th>Cadastro</th><th>Status conta</th><th>KYC</th><th>Assinatura</th><th>Ações</th></tr></thead>
              <tbody>
                {resposta.items.map((u) => (
                  <tr key={u.id} className="admin-assinantes__linha" tabIndex={0} role="link" aria-label={`Abrir ficha de ${u.full_name}`} onClick={() => navigate(`/admin/usuarios/${u.id}`)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); navigate(`/admin/usuarios/${u.id}`); } }}>
                    <td><span className="admin-assinantes__nome">{u.full_name}</span><span className="admin-assinantes__sub">{u.email}</span>{(u.convidado || u.investidor) && <span className="admin-assinantes__badges">{u.convidado && <span className="selo selo--info">Convidado</span>}{u.investidor && <span className="selo selo--info">Investidor</span>}</span>}</td>
                    <td className="dado">{u.cpf_mascarado ?? "—"}</td>
                    <td>{u.council_name ? `${u.council_name} ${u.council_number ?? ""}/${u.council_state ?? ""}` : "—"}</td>
                    <td>{u.profession ?? "—"}</td>
                    <td>{formatarData(u.created_at)}</td>
                    <td><span className={seloContaClasse(u.status)}>{STATUS_CONTA[u.status] ?? u.status}</span></td>
                    <td><span className={seloKycClasse(u.kyc_status)}>{u.kyc_status ? (STATUS_KYC[u.kyc_status] ?? u.kyc_status) : "Sem KYC"}</span></td>
                    <td><span className={seloAssinaturaClasse(u.subscription_status)}>{u.subscription_status ? (STATUS_ASSINATURA[u.subscription_status] ?? u.subscription_status) : "Sem assinatura"}</span>{u.subscription_plano && <span className="admin-assinantes__sub">{PLANO_ROTULO[u.subscription_plano] ?? u.subscription_plano}{u.subscription_periodicidade ? ` · ${u.subscription_periodicidade}` : ""}</span>}</td>
                    <td><button type="button" className="botao botao--secundario" style={{ padding: ".35rem .65rem", whiteSpace: "nowrap" }} onClick={(e) => { e.stopPropagation(); navigate(`/admin/usuarios/${u.id}/gerenciar`); }} onKeyDown={(e) => e.stopPropagation()}>Gerenciar</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="admin-assinantes__paginacao">
            <span className="eyebrow" style={{ margin: 0 }}>Página {resposta.page}</span>
            <div className="admin-assinantes__paginacao-botoes">
              <button type="button" className="botao botao--secundario" disabled={resposta.page <= 1 || carregando} onClick={() => setFiltros((f) => ({ ...f, page: f.page - 1 }))}>← Anterior</button>
              <button type="button" className="botao botao--secundario" disabled={!resposta.has_more || carregando} onClick={() => setFiltros((f) => ({ ...f, page: f.page + 1 }))}>Próxima →</button>
            </div>
          </div>
        </>
      ) : null}
    </>
  );
}
