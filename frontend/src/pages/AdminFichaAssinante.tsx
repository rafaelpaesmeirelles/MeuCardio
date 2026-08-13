import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import "../styles/admin-assinantes.css";

/** Ficha administrativa completa do assinante (issue de estabilização
 * pré-lançamento, 11/08/2026). Consome só `GET /api/admin/usuarios/{id}` e
 * as rotas de decisão de KYC já existentes (`POST /admin/kyc/{id}/aprovar`
 * `/rejeitar` `/solicitar-reenvio`) — backend em `backend/app/api/admin.py`
 * pronto e testado (`ficha_usuario`), não alterado aqui. */

type Endereco = {
  street: string | null; number: string | null; complement: string | null;
  neighborhood: string | null; city: string | null; state: string | null; zip: string | null;
};

type EnderecoProfissional = Endereco & { phone: string | null };

type Conta = {
  status: string; is_active: boolean; role: string;
  reviewed_by: number | null; reviewed_by_nome: string | null; reviewed_at: string | null;
  rejection_note: string | null; created_at: string;
  convidado: boolean; investidor: boolean; convidado_plano_preferido: string | null;
  profile_completion_required: boolean;
};

type DadosPessoais = {
  full_name: string; cpf: string | null; birth_date: string | null; email: string;
  instagram_handle: string | null; endereco_residencial: Endereco;
};

type DadosProfissionais = {
  profession: string | null;
  council_name: string | null; council_name_other: string | null;
  council_number: string | null; council_state: string | null; council_state_other: string | null;
  crm: string | null; rqe: string | null; specialty: string | null; professional_title: string | null;
  workplace_name: string | null; workplace_department: string | null; workplace_role: string | null;
  workplace_notes: string | null; include_workplace_on_documents: boolean;
  endereco_profissional: EnderecoProfissional;
};

type AssinaturaItem = {
  id: number; kind: string; course_id: number | null;
  plano: string | null; periodicidade: string | null; status: string;
  current_period_end: string | null;
  stripe_customer_id: string | null; stripe_subscription_id: string | null;
  last_event_at: string | null; created_at: string; updated_at: string;
};

type Assinatura = {
  tem_acesso_ao_produto: boolean;
  origem_acesso: string;
  acesso_administrativo_sem_pagamento: boolean;
  assinatura_principal: AssinaturaItem | null;
  todas_assinaturas: AssinaturaItem[];
};

type DocumentoKyc = { campo: string; disponivel: boolean; url: string | null };

type UltimaDecisao = {
  action: string; em: string; admin_id: number | null; admin_nome: string | null; nota: string | null;
} | null;

type Kyc = {
  existe: boolean; id: number | null; status: string | null;
  criado_em: string | null; atualizado_em: string | null;
  liberado_em: string | null; aprovado_em: string | null; aprovado_por: number | null;
  nota_revisao: string | null;
  conselho_check_status: string | null; conselho_check_detalhe: string | null;
  ultima_decisao: UltimaDecisao;
  documentos: DocumentoKyc[];
};

type HistoricoItem = {
  id: number; action: string; entity: string; entity_id: string | null;
  detail: Record<string, unknown> | null; created_at: string;
  admin_id: number | null; admin_nome: string | null;
};

type Ficha = {
  id: number; full_name: string; email: string; cpf_mascarado: string | null;
  status: string; role: string; created_at: string;
  conta: Conta;
  dados_pessoais: DadosPessoais;
  dados_profissionais: DadosProfissionais;
  assinatura: Assinatura;
  kyc: Kyc;
  historico: HistoricoItem[];
};

const STATUS_CONTA: Record<string, string> = { pendente: "Pendente", aprovado: "Aprovado", rejeitado: "Rejeitado" };

const STATUS_KYC: Record<string, string> = {
  aguardando_revisao: "Aguardando revisão",
  liberado_conselho_ok: "Liberado — conselho confirmado",
  liberado_sem_checagem: "Liberado — sem checagem automática",
  aprovado: "Aprovado",
  rejeitado: "Rejeitado",
  reenvio_solicitado: "Reenvio solicitado",
};

const STATUS_ASSINATURA: Record<string, string> = {
  inativo: "Inativo", ativo: "Ativo", teste: "Teste", pendente: "Pendente",
  inadimplente: "Inadimplente", suspenso: "Suspenso", cancelado: "Cancelado", pausado: "Pausado",
};

const PLANO_ROTULO: Record<string, string> = { basico: "Básico", completo: "Completo" };

// Só os 5 valores reais de `assinatura.origem_acesso` (backend/app/api/admin.py,
// `_origem_acesso`) — "Teste" NÃO é um deles (é um valor possível de
// `subscription_status`, mostrado à parte na aba Assinatura).
const ORIGEM_ACESSO: Record<string, string> = {
  admin: "Administrador",
  convidado: "Convidado",
  investidor: "Investidor",
  assinatura_paga: "Pago",
  sem_acesso: "Sem acesso",
};

const ROTULO_DOCUMENTO: Record<string, string> = {
  doc_profissional_frente: "Documento profissional — frente",
  doc_profissional_verso: "Documento profissional — verso",
  doc_pessoal_frente: "Documento pessoal — frente",
  doc_pessoal_verso: "Documento pessoal — verso",
  doc_pessoal_digital: "Documento pessoal — PDF digital",
  selfie: "Selfie de validação",
};

// Ordem de exibição na grade de documentos — a API devolve `documentos`
// ordenado alfabeticamente por campo (`sorted(_CAMPOS_DOCUMENTO)`), esta
// ordem agrupa por tipo (profissional, depois pessoal) em vez disso. A
// selfie fica de fora — tem seção visual própria, ver `AbaDocumentos`.
const ORDEM_DOCUMENTOS = [
  "doc_profissional_frente", "doc_profissional_verso",
  "doc_pessoal_frente", "doc_pessoal_verso", "doc_pessoal_digital",
];

// Estados de KYC em que ainda cabe uma decisão do admin — aprovado,
// rejeitado e reenvio_solicitado já são o resultado de uma decisão
// anterior (o admin pode reabrir clicando de novo nos botões, mas o painel
// só aparece sozinho enquanto o caso está pendente).
const KYC_PENDE_DECISAO = new Set(["aguardando_revisao", "liberado_conselho_ok", "liberado_sem_checagem"]);

const ACAO_HISTORICO: Record<string, string> = {
  kyc_aprovado: "Verificação de identidade aprovada",
  kyc_rejeitado: "Verificação de identidade rejeitada",
  kyc_reenvio_solicitado: "Reenvio de documento solicitado",
  kyc_documento_visualizado: "Documento do KYC visualizado por um admin",
  decidir: "Decisão sobre solicitação de acesso",
  criar: "Conta criada",
  ativo: "Ativação/desativação da conta",
  convidado: "Status de convidado alterado",
  investidor: "Status de investidor alterado",
};

function rotuloAcao(action: string): string {
  if (ACAO_HISTORICO[action]) return ACAO_HISTORICO[action];
  return action.replaceAll("_", " ").replace(/^\w/, (c) => c.toUpperCase());
}

function formatarData(iso: string | null): string {
  if (!iso) return "—";
  try { return new Date(iso).toLocaleDateString("pt-BR"); } catch { return "—"; }
}

function formatarDataHora(iso: string | null): string {
  if (!iso) return "—";
  try { return new Date(iso).toLocaleString("pt-BR"); } catch { return "—"; }
}

function formatarCpf(cpf: string | null): string {
  if (!cpf) return "—";
  const digitos = cpf.replace(/\D/g, "");
  if (digitos.length !== 11) return cpf;
  return `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6, 9)}-${digitos.slice(9)}`;
}

function enderecoTexto(e: Endereco): string {
  const linha1 = [e.street, e.number].filter(Boolean).join(", ");
  const linha2 = [e.complement, e.neighborhood].filter(Boolean).join(" — ");
  const linha3 = [e.city, e.state].filter(Boolean).join("/");
  const partes = [linha1, linha2, linha3, e.zip ? `CEP ${e.zip}` : ""].filter(Boolean);
  return partes.length ? partes.join(" · ") : "—";
}

function conselhoTexto(d: DadosProfissionais): string {
  const nome = d.council_name === "Outro" ? (d.council_name_other || "Outro") : d.council_name;
  const uf = d.council_name === "Outro" ? (d.council_state_other || d.council_state) : d.council_state;
  if (!nome && !d.council_number) return "—";
  return [nome, d.council_number && uf ? `${d.council_number}/${uf}` : d.council_number].filter(Boolean).join(" ");
}

function seloContaClasse(status: string): string {
  if (status === "aprovado") return "selo selo--sucesso";
  if (status === "rejeitado") return "selo selo--atencao";
  return "selo";
}

function seloKycClasse(status: string | null): string {
  if (!status) return "selo selo--neutro";
  if (["aprovado", "liberado_conselho_ok", "liberado_sem_checagem"].includes(status)) return "selo selo--sucesso";
  if (status === "rejeitado") return "selo selo--atencao";
  return "selo";
}

function seloAssinaturaClasse(status: string | null): string {
  if (!status || status === "inativo") return "selo selo--neutro";
  if (status === "ativo" || status === "teste") return "selo selo--sucesso";
  if (["inadimplente", "suspenso", "cancelado"].includes(status)) return "selo selo--atencao";
  return "selo";
}

function Campo({ rotulo, valor }: { rotulo: string; valor: ReactNode }) {
  return (
    <div className="admin-ficha__campo">
      <dt>{rotulo}</dt>
      <dd>{valor === "" || valor === null || valor === undefined ? <span className="admin-ficha__vazio">—</span> : valor}</dd>
    </div>
  );
}

// ---------------------------------------------------------------------
// Visualizador de documento — imagem via <img src="blob:...">, PDF via
// <iframe src="blob:..." sandbox="allow-same-origin">. Nunca marcação HTML
// injetada diretamente, nem pela propriedade especial do React nem pelo
// DOM (política de renderização segura do projeto,
// scripts/check-rendering-security.mjs). O Object URL vem sempre de um
// Blob buscado com `api.blob()` (autenticado, nunca URL pública), e é
// revogado ao trocar de documento ou fechar o visualizador.
// ---------------------------------------------------------------------

type ItemVisualizavel = { campo: string; rotulo: string; url: string };

function VisualizadorDocumento({
  itens, indiceInicial, aoFechar,
}: { itens: ItemVisualizavel[]; indiceInicial: number; aoFechar: () => void }) {
  const [indice, setIndice] = useState(indiceInicial);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [tipo, setTipo] = useState<"imagem" | "pdf" | "outro" | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [zoom, setZoom] = useState(1);
  const painelRef = useRef<HTMLDivElement>(null);
  const fecharRef = useRef<HTMLButtonElement>(null);

  const item = itens[indice];

  useEffect(() => {
    if (!item) return;
    let cancelado = false;
    let urlLocal: string | null = null;
    setCarregando(true);
    setErro("");
    setZoom(1);
    setBlobUrl(null);
    setTipo(null);
    api.blob(item.url)
      .then((blob) => {
        if (cancelado) return;
        urlLocal = URL.createObjectURL(blob);
        setBlobUrl(urlLocal);
        setTipo(blob.type.startsWith("image/") ? "imagem" : blob.type === "application/pdf" ? "pdf" : "outro");
      })
      .catch((e) => {
        if (!cancelado) setErro(e instanceof ApiError ? e.message : "Não foi possível abrir este documento.");
      })
      .finally(() => { if (!cancelado) setCarregando(false); });
    return () => {
      cancelado = true;
      if (urlLocal) URL.revokeObjectURL(urlLocal);
    };
  }, [item?.url]);

  function ir(delta: number) {
    setIndice((i) => (i + delta + itens.length) % itens.length);
  }

  useEffect(() => {
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const overflowAnterior = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    requestAnimationFrame(() => fecharRef.current?.focus());

    function aoTeclar(evento: KeyboardEvent) {
      if (evento.key === "Escape") { evento.preventDefault(); aoFechar(); return; }
      if (itens.length < 2) return;
      if (evento.key === "ArrowLeft") { evento.preventDefault(); ir(-1); }
      else if (evento.key === "ArrowRight") { evento.preventDefault(); ir(1); }
    }
    document.addEventListener("keydown", aoTeclar);
    return () => {
      document.removeEventListener("keydown", aoTeclar);
      document.body.style.overflow = overflowAnterior;
      previous?.focus();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itens.length]);

  if (!item) return null;

  return (
    <div
      className="admin-visualizador"
      role="dialog"
      aria-modal="true"
      aria-label={`Visualizador de documentos — ${item.rotulo}`}
      onMouseDown={(e) => { if (e.target === e.currentTarget) aoFechar(); }}
    >
      <div className="admin-visualizador__painel" ref={painelRef}>
        <div className="admin-visualizador__topo">
          <div>
            <p className="admin-visualizador__titulo">{item.rotulo}</p>
            {itens.length > 1 && <p className="admin-visualizador__contagem">{indice + 1} de {itens.length}</p>}
          </div>
          <button
            type="button" className="admin-visualizador__fechar" ref={fecharRef}
            onClick={aoFechar} aria-label="Fechar visualizador"
          >
            ✕
          </button>
        </div>

        <div className="admin-visualizador__corpo">
          {carregando && <Carregando texto="Carregando documento…" />}
          {!carregando && erro && <Erro mensagem={erro} />}
          {!carregando && !erro && blobUrl && tipo === "imagem" && (
            <div className="admin-visualizador__imagem-wrap">
              <img
                src={blobUrl} alt={item.rotulo} className="admin-visualizador__imagem"
                style={{ transform: `scale(${zoom})` }}
              />
            </div>
          )}
          {!carregando && !erro && blobUrl && tipo === "pdf" && (
            <iframe
              src={blobUrl} title={item.rotulo} className="admin-visualizador__pdf"
              sandbox="allow-same-origin"
            />
          )}
          {!carregando && !erro && blobUrl && tipo === "outro" && (
            <div style={{ textAlign: "center", padding: "1.5rem" }}>
              <p>Não é possível pré-visualizar este tipo de arquivo.</p>
              <a className="admin-visualizador__baixar" href={blobUrl} download={item.campo}>Baixar arquivo</a>
            </div>
          )}
        </div>

        <div className="admin-visualizador__rodape">
          <div className="admin-visualizador__navegacao">
            <button type="button" disabled={itens.length < 2} onClick={() => ir(-1)}>← Anterior</button>
            <button type="button" disabled={itens.length < 2} onClick={() => ir(1)}>Próxima →</button>
          </div>
          {tipo === "imagem" && (
            <div className="admin-visualizador__zoom">
              <button type="button" disabled={zoom <= 0.5} onClick={() => setZoom((z) => Math.max(0.5, +(z - 0.25).toFixed(2)))} aria-label="Reduzir zoom">−</button>
              <span className="eyebrow" style={{ margin: 0 }}>{Math.round(zoom * 100)}%</span>
              <button type="button" disabled={zoom >= 3} onClick={() => setZoom((z) => Math.min(3, +(z + 0.25).toFixed(2)))} aria-label="Ampliar zoom">+</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------
// Painel de decisão (aprovar / rejeitar / solicitar reenvio) — só aparece
// enquanto o KYC está num status que ainda pede decisão do admin
// (KYC_PENDE_DECISAO). Mesmo padrão de "revela campo de nota, confirma só
// com o campo preenchido" já usado em SolicitacaoCard (Admin.tsx).
// ---------------------------------------------------------------------

function PainelDecisaoKyc({ kycId, aoDecidido }: { kycId: number; aoDecidido: () => void }) {
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [formularioAberto, setFormularioAberto] = useState<"rejeitar" | "reenvio" | null>(null);
  const [nota, setNota] = useState("");

  async function aprovar() {
    if (!confirm("Aprovar definitivamente a verificação de identidade deste assinante?")) return;
    setErro(""); setEnviando(true);
    try {
      await api.post(`/admin/kyc/${kycId}/aprovar`, {});
      aoDecidido();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível aprovar.");
    } finally {
      setEnviando(false);
    }
  }

  async function confirmar(acao: "rejeitar" | "reenvio") {
    const texto = nota.trim();
    if (!texto) return;
    setErro(""); setEnviando(true);
    try {
      const rota = acao === "rejeitar" ? "rejeitar" : "solicitar-reenvio";
      await api.post(`/admin/kyc/${kycId}/${rota}`, { nota: texto });
      setNota("");
      setFormularioAberto(null);
      aoDecidido();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível registrar a decisão.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="admin-ficha__decisao">
      <p className="eyebrow" style={{ margin: "0 0 0.3rem" }}>Decisão de verificação de identidade</p>
      <p style={{ margin: 0, color: "var(--texto-secundario)", fontSize: "0.88rem" }}>
        Confira os documentos acima antes de decidir. A decisão fica registrada no histórico do
        assinante.
      </p>
      <div className="admin-ficha__decisao-acoes">
        <button type="button" className="botao" disabled={enviando} onClick={aprovar}>Aprovar</button>
        <button
          type="button" className="botao botao--secundario" disabled={enviando}
          onClick={() => setFormularioAberto((f) => (f === "rejeitar" ? null : "rejeitar"))}
        >
          Rejeitar
        </button>
        <button
          type="button" className="botao botao--secundario" disabled={enviando}
          onClick={() => setFormularioAberto((f) => (f === "reenvio" ? null : "reenvio"))}
        >
          Solicitar reenvio
        </button>
      </div>

      {formularioAberto && (
        <div className="admin-ficha__decisao-form">
          <label htmlFor="ficha-nota-decisao">
            {formularioAberto === "rejeitar" ? "Motivo da rejeição" : "O que precisa ser reenviado"}
          </label>
          <textarea
            id="ficha-nota-decisao" value={nota} onChange={(e) => setNota(e.target.value)}
            placeholder="Explique — este texto fica visível para o assinante."
          />
          <div className="admin-ficha__decisao-form-acoes">
            <button
              type="button" className="botao botao--perigo" disabled={enviando || !nota.trim()}
              onClick={() => confirmar(formularioAberto)}
            >
              {formularioAberto === "rejeitar" ? "Confirmar rejeição" : "Confirmar solicitação"}
            </button>
            <button
              type="button" className="botao botao--secundario" disabled={enviando}
              onClick={() => { setFormularioAberto(null); setNota(""); }}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.85rem", marginTop: "0.6rem" }}>{erro}</p>}
    </div>
  );
}

// ---------------------------------------------------------------------
// Abas
// ---------------------------------------------------------------------

function AbaDadosPessoais({ d }: { d: DadosPessoais }) {
  return (
    <dl className="admin-ficha__grade">
      <Campo rotulo="Nome completo" valor={d.full_name} />
      <Campo rotulo="CPF" valor={formatarCpf(d.cpf)} />
      <Campo rotulo="Nascimento" valor={formatarData(d.birth_date)} />
      <Campo rotulo="E-mail" valor={d.email} />
      <Campo rotulo="Instagram" valor={d.instagram_handle ? `@${d.instagram_handle}` : null} />
      <Campo rotulo="Endereço residencial" valor={enderecoTexto(d.endereco_residencial)} />
    </dl>
  );
}

function AbaProfissional({ d }: { d: DadosProfissionais }) {
  return (
    <dl className="admin-ficha__grade">
      <Campo rotulo="Profissão" valor={d.profession} />
      <Campo rotulo="Conselho de classe" valor={conselhoTexto(d)} />
      <Campo rotulo="CRM (legado)" valor={d.crm} />
      <Campo rotulo="RQE" valor={d.rqe} />
      <Campo rotulo="Especialidade" valor={d.specialty} />
      <Campo rotulo="Título profissional" valor={d.professional_title} />
      <Campo rotulo="Local de trabalho" valor={d.workplace_name} />
      <Campo rotulo="Departamento" valor={d.workplace_department} />
      <Campo rotulo="Cargo" valor={d.workplace_role} />
      <Campo rotulo="Exibe local em documentos" valor={d.include_workplace_on_documents ? "Sim" : "Não"} />
      <Campo rotulo="Observações do local" valor={d.workplace_notes} />
      <Campo rotulo="Telefone profissional" valor={d.endereco_profissional.phone} />
      <Campo rotulo="Endereço profissional" valor={enderecoTexto(d.endereco_profissional)} />
    </dl>
  );
}

function LinhaAssinatura({ s }: { s: AssinaturaItem }) {
  return (
    <tr>
      <td>{s.kind}{s.course_id ? ` (curso ${s.course_id})` : ""}</td>
      <td>{s.plano ? (PLANO_ROTULO[s.plano] ?? s.plano) : "—"}</td>
      <td>{s.periodicidade ?? "—"}</td>
      <td><span className={seloAssinaturaClasse(s.status)}>{STATUS_ASSINATURA[s.status] ?? s.status}</span></td>
      <td>{formatarData(s.current_period_end)}</td>
      <td className="dado">{s.stripe_customer_id ?? "—"}</td>
      <td className="dado">{s.stripe_subscription_id ?? "—"}</td>
      <td>{formatarDataHora(s.updated_at)}</td>
    </tr>
  );
}

function AbaAssinatura({ a }: { a: Assinatura }) {
  const principal = a.assinatura_principal;
  return (
    <>
      <dl className="admin-ficha__grade">
        <Campo rotulo="Tem acesso ao produto" valor={a.tem_acesso_ao_produto ? "Sim" : "Não"} />
        <Campo rotulo="Origem do acesso" valor={ORIGEM_ACESSO[a.origem_acesso] ?? a.origem_acesso} />
        <Campo
          rotulo="Acesso administrativo (sem cobrança)"
          valor={a.acesso_administrativo_sem_pagamento ? "Sim" : "Não"}
        />
        {principal && (
          <>
            <Campo rotulo="Plano atual" valor={principal.plano ? (PLANO_ROTULO[principal.plano] ?? principal.plano) : "—"} />
            <Campo rotulo="Periodicidade" valor={principal.periodicidade ?? "—"} />
            <Campo
              rotulo="Status da assinatura"
              valor={<span className={seloAssinaturaClasse(principal.status)}>{STATUS_ASSINATURA[principal.status] ?? principal.status}</span>}
            />
            <Campo rotulo="Fim do período atual" valor={formatarData(principal.current_period_end)} />
            <Campo rotulo="Cliente no Stripe" valor={principal.stripe_customer_id} />
            <Campo rotulo="Assinatura no Stripe" valor={principal.stripe_subscription_id} />
            <Campo rotulo="Último evento" valor={formatarDataHora(principal.last_event_at)} />
          </>
        )}
      </dl>

      <div className="admin-ficha__secao">
        <h2>Histórico de assinaturas</h2>
        {a.todas_assinaturas.length === 0 ? (
          <p style={{ color: "var(--texto-secundario)" }}>Nenhuma assinatura registrada para este usuário.</p>
        ) : (
          <div className="admin-ficha__assinaturas-wrap">
            <table className="admin-ficha__assinaturas">
              <thead>
                <tr>
                  <th>Tipo</th><th>Plano</th><th>Periodicidade</th><th>Status</th>
                  <th>Fim do período</th><th>Cliente Stripe</th><th>Assinatura Stripe</th><th>Atualizada em</th>
                </tr>
              </thead>
              <tbody>
                {a.todas_assinaturas.map((s) => <LinhaAssinatura key={s.id} s={s} />)}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}

function AbaDocumentos({ kyc, conta, aoAtualizar }: { kyc: Kyc; conta: Conta; aoAtualizar: () => void }) {
  const [visualizando, setVisualizando] = useState<number | null>(null);

  if (!kyc.existe) {
    return <p style={{ color: "var(--texto-secundario)" }}>Este assinante ainda não enviou documentos de verificação de identidade.</p>;
  }

  const porCampo = new Map(kyc.documentos.map((d) => [d.campo, d]));
  const selfie = porCampo.get("selfie");

  const todosDisponiveis: ItemVisualizavel[] = [...ORDEM_DOCUMENTOS, "selfie"]
    .map((campo) => porCampo.get(campo))
    .filter((d): d is DocumentoKyc => !!d && d.disponivel && !!d.url)
    .map((d) => ({ campo: d.campo, rotulo: ROTULO_DOCUMENTO[d.campo] ?? d.campo, url: d.url as string }));

  function abrir(campo: string) {
    const indice = todosDisponiveis.findIndex((d) => d.campo === campo);
    if (indice >= 0) setVisualizando(indice);
  }

  return (
    <>
      <dl className="admin-ficha__grade">
        <Campo rotulo="Status" valor={<span className={seloKycClasse(kyc.status)}>{kyc.status ? (STATUS_KYC[kyc.status] ?? kyc.status) : "—"}</span>} />
        <Campo rotulo="Enviado em" valor={formatarDataHora(kyc.criado_em)} />
        <Campo rotulo="Liberado em" valor={formatarDataHora(kyc.liberado_em)} />
        <Campo rotulo="Aprovado em" valor={formatarDataHora(kyc.aprovado_em)} />
        <Campo rotulo="Checagem automática de conselho" valor={kyc.conselho_check_status ?? "—"} />
        <Campo rotulo="Detalhe da checagem" valor={kyc.conselho_check_detalhe} />
        {kyc.nota_revisao && <Campo rotulo="Nota de revisão" valor={kyc.nota_revisao} />}
      </dl>

      {kyc.ultima_decisao && (
        <p style={{ marginTop: "0.8rem", color: "var(--texto-secundario)", fontSize: "0.85rem" }}>
          Última decisão: <strong>{rotuloAcao(kyc.ultima_decisao.action)}</strong>
          {" "}por {kyc.ultima_decisao.admin_nome ?? "administrador"} em {formatarDataHora(kyc.ultima_decisao.em)}
          {kyc.ultima_decisao.nota ? ` — "${kyc.ultima_decisao.nota}"` : ""}
        </p>
      )}

      <div className="admin-ficha__secao">
        <h2>Documentos enviados</h2>
        <div className="admin-ficha__documentos-grade">
          {ORDEM_DOCUMENTOS.map((campo) => {
            const doc = porCampo.get(campo);
            const disponivel = !!doc?.disponivel && !!doc.url;
            return (
              <button
                key={campo} type="button" className="admin-ficha__documento-item"
                disabled={!disponivel} onClick={() => abrir(campo)}
              >
                <span className="admin-ficha__documento-icone" aria-hidden="true">📄</span>
                <span className="admin-ficha__documento-rotulo">{ROTULO_DOCUMENTO[campo]}</span>
                <span className="admin-ficha__documento-estado">{disponivel ? "Ver documento" : "Não enviado"}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="admin-ficha__secao">
        <h2>Selfie de validação</h2>
        {selfie?.disponivel && selfie.url ? (
          <button type="button" className="admin-ficha__documento-item" onClick={() => abrir("selfie")}>
            <span className="admin-ficha__documento-icone" aria-hidden="true">🙂</span>
            <span className="admin-ficha__documento-rotulo">{ROTULO_DOCUMENTO.selfie}</span>
            <span className="admin-ficha__documento-estado">Ver selfie</span>
          </button>
        ) : (
          <p style={{ color: "var(--texto-secundario)" }}>Selfie não enviada.</p>
        )}
      </div>

      {(conta.convidado || conta.investidor) ? (
        // Convidado/investidor (13/08/2026) nunca dependem de decisão do
        // admin — `submeter()` no backend já garante aprovação automática
        // numa submissão válida. Informativo apenas, sem os botões
        // Aprovar/Rejeitar/Solicitar reenvio, mesmo no caso raro de um
        // registro legado ainda estar num status pendente de decisão.
        <p style={{ marginTop: "0.8rem", color: "var(--texto-secundario)", fontSize: "0.9rem" }}>
          {conta.investidor ? "Investidor" : "Convidado"} — acesso automático concedido.
        </p>
      ) : (
        kyc.status && KYC_PENDE_DECISAO.has(kyc.status) && kyc.id !== null && (
          <PainelDecisaoKyc kycId={kyc.id} aoDecidido={aoAtualizar} />
        )
      )}

      {visualizando !== null && (
        <VisualizadorDocumento
          itens={todosDisponiveis} indiceInicial={visualizando}
          aoFechar={() => setVisualizando(null)}
        />
      )}
    </>
  );
}

// Rótulo de campo do AuditLog.detail, legível — não é dicionário exaustivo
// de tradução, só "snake_case" → "Frase com inicial maiúscula", suficiente
// porque a maioria das chaves já nasce em português no backend (ex.:
// "tipo_acesso", "observacao", "plano_anterior").
function humanizarChaveDetalhe(chave: string): string {
  const texto = chave.replaceAll("_", " ");
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

// AuditLog.detail é um JSON livre por ação (definido caso a caso no
// backend) — nunca um formato único conhecido de antemão. Em vez de despejar
// o objeto cru (bug corrigido em 14/08/2026: aparecia como JSON bruto,
// ilegível para quem não é desenvolvedor), cada valor primitivo vira uma
// linha rotulada; valor desconhecido/aninhado cai no fallback de
// JSON.stringify SÓ para aquele valor específico, nunca para o registro
// inteiro — mantém "nunca dump cru" mesmo para o formato que não se
// consegue formatar melhor.
function formatarValorDetalhe(valor: unknown): string {
  if (valor === null || valor === undefined || valor === "") return "—";
  if (typeof valor === "boolean") return valor ? "Sim" : "Não";
  if (Array.isArray(valor)) {
    return valor.length ? valor.map(formatarValorDetalhe).join(", ") : "—";
  }
  if (typeof valor === "object") return JSON.stringify(valor);
  return String(valor);
}

function DetalheHistorico({ detail }: { detail: Record<string, unknown> }) {
  const entradas = Object.entries(detail).filter(([, v]) => v !== null && v !== undefined && v !== "");
  if (entradas.length === 0) return null;
  return (
    <dl className="admin-ficha__historico-detalhe">
      {entradas.map(([chave, valor]) => (
        <div key={chave} className="admin-ficha__historico-detalhe-linha">
          <dt>{humanizarChaveDetalhe(chave)}</dt>
          <dd>{formatarValorDetalhe(valor)}</dd>
        </div>
      ))}
    </dl>
  );
}

function AbaHistorico({ historico }: { historico: HistoricoItem[] }) {
  if (historico.length === 0) {
    return <p style={{ color: "var(--texto-secundario)" }}>Nenhum evento registrado para este assinante até o momento.</p>;
  }
  return (
    <ul className="admin-ficha__historico">
      {historico.map((h) => (
        <li key={h.id} className="admin-ficha__historico-item">
          <p className="admin-ficha__historico-acao">{rotuloAcao(h.action)}</p>
          <p className="admin-ficha__historico-meta">
            {formatarDataHora(h.created_at)} · {h.admin_nome ?? "sistema"}
          </p>
          {h.detail && <DetalheHistorico detail={h.detail} />}
        </li>
      ))}
    </ul>
  );
}

// ---------------------------------------------------------------------

const ABAS = [
  { id: "pessoais", rotulo: "Dados pessoais" },
  { id: "profissional", rotulo: "Profissional" },
  { id: "assinatura", rotulo: "Assinatura" },
  { id: "documentos", rotulo: "Documentos" },
  { id: "historico", rotulo: "Histórico" },
] as const;

type AbaId = typeof ABAS[number]["id"];

export default function AdminFichaAssinante() {
  const { id } = useParams();
  const [ficha, setFicha] = useState<Ficha | null>(null);
  const [erro, setErro] = useState("");
  const [naoEncontrado, setNaoEncontrado] = useState(false);
  const [aba, setAba] = useState<AbaId>("pessoais");

  function carregar() {
    if (!id) return;
    setErro("");
    api.get<Ficha>(`/admin/usuarios/${id}`)
      .then(setFicha)
      .catch((e) => {
        if (e instanceof ApiError && e.status === 404) setNaoEncontrado(true);
        else setErro(e instanceof ApiError ? e.message : "Não foi possível carregar a ficha deste assinante.");
      });
  }

  useEffect(() => {
    setFicha(null);
    setNaoEncontrado(false);
    setAba("pessoais");
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (naoEncontrado) {
    return (
      <>
        <Link to="/admin/usuarios" className="admin-ficha__voltar">← Voltar para assinantes</Link>
        <Erro mensagem="Usuário não encontrado." />
      </>
    );
  }
  if (erro) {
    return (
      <>
        <Link to="/admin/usuarios" className="admin-ficha__voltar">← Voltar para assinantes</Link>
        <Erro mensagem={erro} />
      </>
    );
  }
  if (!ficha) return <Carregando texto="Carregando ficha…" />;

  return (
    <>
      <Link to="/admin/usuarios" className="admin-ficha__voltar">← Voltar para assinantes</Link>

      <header className="admin-ficha__cabecalho">
        <div>
          <p className="eyebrow" style={{ margin: 0 }}>Ficha do assinante · #{ficha.id}</p>
          <h1>{ficha.full_name}</h1>
          <p className="admin-ficha__cabecalho-sub">
            {ficha.email} · CPF {ficha.cpf_mascarado ?? "—"} · cadastrado em {formatarData(ficha.created_at)}
          </p>
        </div>
        <div className="admin-ficha__cabecalho-badges">
          <span className={seloContaClasse(ficha.status)}>{STATUS_CONTA[ficha.status] ?? ficha.status}</span>
          <span className={seloKycClasse(ficha.kyc.status)}>
            {ficha.kyc.status ? (STATUS_KYC[ficha.kyc.status] ?? ficha.kyc.status) : "Sem KYC"}
          </span>
          <span className={seloAssinaturaClasse(ficha.assinatura.assinatura_principal?.status ?? null)}>
            {ficha.assinatura.assinatura_principal
              ? (STATUS_ASSINATURA[ficha.assinatura.assinatura_principal.status] ?? ficha.assinatura.assinatura_principal.status)
              : "Sem assinatura"}
          </span>
          <span className="selo selo--info">{ORIGEM_ACESSO[ficha.assinatura.origem_acesso] ?? ficha.assinatura.origem_acesso}</span>
        </div>
      </header>

      <div className="admin-ficha__abas" role="tablist" aria-label="Seções da ficha do assinante">
        {ABAS.map((a) => (
          <button
            key={a.id} type="button" role="tab" aria-selected={aba === a.id}
            onClick={() => setAba(a.id)}
          >
            {a.rotulo}
          </button>
        ))}
      </div>

      {aba === "pessoais" && <AbaDadosPessoais d={ficha.dados_pessoais} />}
      {aba === "profissional" && <AbaProfissional d={ficha.dados_profissionais} />}
      {aba === "assinatura" && <AbaAssinatura a={ficha.assinatura} />}
      {aba === "documentos" && <AbaDocumentos kyc={ficha.kyc} conta={ficha.conta} aoAtualizar={carregar} />}
      {aba === "historico" && <AbaHistorico historico={ficha.historico} />}

      <p style={{ marginTop: "1.6rem" }}>
        <Link to="/admin/usuarios" style={{ fontSize: "0.86rem" }}>← Voltar para a lista de assinantes</Link>
      </p>
    </>
  );
}
