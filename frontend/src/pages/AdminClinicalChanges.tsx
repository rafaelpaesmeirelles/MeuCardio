import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import "../styles/admin-clinical-changes.css";

type Status = "pending" | "approved" | "rejected";
type Change = { item_type: string; item_id: number; label: string; before: unknown; after: unknown; before_text?: string; after_text?: string; source_url?: string; change_summary_pt: string; changed_fields?: string[]; effect_kind?: "editorial_summary" | "clinical_content" | "references_metadata"; impact_scope?: { fluxograma?: boolean; emergency_protocols?: { slug: string; title: string; relation: string }[] } };
type Proposal = { can_approve?: boolean; blocking_reason?: string | null; verification_status?: "verified" | "needs_verification"; candidates_count?: number; verified_count?: number; uncertain_count?: number; id: number; version: number; status: Status; created_at: string; guideline: { id: number; slug: string; title: string; doi?: string; url?: string }; proposed_changes: Change[]; reviewed_at?: string; reviewer_id?: number; reviewer_name?: string; rejection_reason?: string; audit_events?: { action: string; at: string; reviewer_id?: number; reviewer_name?: string; reason?: string }[] };
type ProposalList = { items: Proposal[]; total: number };
const statusNames: Record<Status, string> = { pending: "Pendentes", approved: "Aprovadas e aplicadas", rejected: "Rejeitadas" };
const typeNames: Record<string, string> = { unresolved: "Sugestão com alvo pendente", document_summary: "Síntese editorial", disease: "Guia de Doenças", doenca: "Guia de Doenças", drug: "Medicamento", medicamento: "Medicamento", documento: "Documento", estudo: "Estudo", evidencia: "Evidência", exame: "Exame", conduta: "Conduta", protocolo: "Protocolo", trilha: "Trilha", caso: "Caso clínico", material_paciente: "Material para paciente" };
const date = (value?: string) => value ? new Date(value).toLocaleString("pt-BR") : "Não registrado";
function sourceUrl(value?: string): string | null { try { const url = new URL(value || ""); return ["https:", "http:"].includes(url.protocol) ? url.href : null; } catch { return null; } }
const fieldNames: Record<string, string> = { body_md: "Conteúdo clínico", treatment_summary: "Conduta e tratamento", dosing: "Posologia", ambulatory_flow: "Fluxo ambulatorial", emergency_flow: "Fluxo de emergência", title: "Título", summary: "Resumo", theme: "Tema", tags: "Assuntos relacionados", source_refs: "Fontes e referências", evidence_level: "Nível de evidência", source_tier: "Categoria da fonte", review_status: "Estado da revisão", published: "Publicado", kind: "Classificação editorial", version: "Versão", gaps: "Lacunas documentadas", slug: "Identificador do conteúdo" };
const fieldName = (key: string) => fieldNames[key] || key.replaceAll("_", " ");
function readable(value: unknown): string {
  if (value == null || value === "") return "Não informado";
  if (typeof value === "boolean") return value ? "Sim" : "Não";
  if (Array.isArray(value)) return value.length ? value.map(item => `• ${readable(item)}`).join("\n") : "Nenhum item";
  if (typeof value === "object") return Object.entries(value).map(([key,item]) => `${fieldName(key)}: ${readable(item)}`).join("\n");
  return String(value);
}
function Snapshot({ value, fallback, fields }: { value: unknown; fallback?: string; fields?: string[] }) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return <pre>{fallback || readable(value)}</pre>;
  const entries = Object.entries(value).filter(([key]) => !fields?.length || fields.includes(key));
  return entries.length ? <dl>{entries.map(([key,item]) => <div key={key}><dt>{fieldName(key)}</dt><dd>{["body_md", "treatment_summary", "summary"].includes(key) && typeof item === "string" ? <Markdown remarkPlugins={[remarkGfm]} skipHtml components={{ a: ({ href, children }) => sourceUrl(href) ? <a href={sourceUrl(href)!} target="_blank" rel="noopener noreferrer">{children}</a> : <span>{children}</span>, img: () => null }}>{item}</Markdown> : <pre>{readable(item)}</pre>}</dd></div>)}</dl> : <p>Sem valor anterior nos campos alterados.</p>;
}
const eventNames: Record<string, string> = { clinical_change_proposed: "Proposta registrada", clinical_change_approved: "Aprovada e aplicada", clinical_change_rejected: "Rejeitada", approved: "Aprovada e aplicada", rejected: "Rejeitada" };

export default function AdminClinicalChanges() {
  const { usuario } = useAuth();
  if (usuario?.role !== "admin") return <p role="alert">Acesso restrito à administração.</p>;
  return <AdminClinicalWorkspace key={usuario.id} />;
}

function AdminClinicalWorkspace() {
  const { usuario } = useAuth();
  const isAdmin = usuario?.role === "admin";
  const [status, setStatus] = useState<Status>("pending");
  const [offset, setOffset] = useState(0);
  const [revision, setRevision] = useState(0);
  const [list, setList] = useState<ProposalList | null>(null);
  const [listError, setListError] = useState("");
  const [selected, setSelected] = useState<number | null>(null);
  const [detail, setDetail] = useState<Proposal | null>(null);
  const [detailError, setDetailError] = useState("");
  const [detailRevision, setDetailRevision] = useState(0);
  const [consent, setConsent] = useState(false);
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [conflict, setConflict] = useState(false);
  const [notice, setNotice] = useState("");
  const activeMutation = useRef(false);
  const epoch = useRef(0);
  useEffect(() => { const current = ++epoch.current; activeMutation.current = false; setBusy(false); return () => { if (epoch.current === current) epoch.current++; }; }, [usuario?.id]);
  useEffect(() => {
    let active = true;
    setList(null); setListError("");
    if (!isAdmin) return;
    api.get<ProposalList>(`/clinical-change-approvals?status=${status}&limit=50&offset=${offset}`).then(value => { if (active) setList(value); }).catch(error => { if (active) setListError(error instanceof ApiError && error.status === 403 ? "A revisão e a decisão destas mudanças estão restritas ao administrador responsável pelo CorVIA." : "Não foi possível carregar as propostas."); });
    return () => { active = false; };
  }, [isAdmin, usuario?.id, status, offset, revision]);
  useEffect(() => {
    let active = true;
    setDetail(null); setDetailError(""); setConsent(false); setReason(""); setConflict(false);
    if (!isAdmin || selected == null) return;
    api.get<Proposal>(`/clinical-change-approvals/${selected}`).then(value => { if (active) setDetail(value); }).catch(() => { if (active) setDetailError("Não foi possível abrir a comparação. Recarregue a proposta."); });
    return () => { active = false; };
  }, [isAdmin, usuario?.id, selected, detailRevision]);
  function selectStatus(value: Status) { if (busy) return; setStatus(value); setOffset(0); setSelected(null); setNotice(""); }
  async function decide(action: "approve" | "reject") {
    if (!isAdmin || !detail || detail.status !== "pending" || !detail.proposed_changes.length || conflict || activeMutation.current || (action === "approve" ? !consent || detail.can_approve === false : !reason.trim())) return;
    const currentEpoch = epoch.current;
    activeMutation.current = true; setBusy(true); setDetailError(""); setNotice("");
    try {
      const updated = await api.post<Proposal>(`/clinical-change-approvals/${detail.id}/${action}`, { expected_version: detail.version, ...(action === "reject" ? { reason: reason.trim() } : {}) });
      if (currentEpoch !== epoch.current) return;
      setDetail(updated);
      window.dispatchEvent(new CustomEvent("corvia:clinical-approvals-changed", { detail: { userId: usuario?.id } }));
      setConsent(false); setReason(""); setRevision(value => value + 1);
      setNotice(action === "approve" ? "Mudanças aprovadas e aplicadas ao conteúdo do CorVIA." : "Proposta rejeitada. O conteúdo foi preservado.");
    } catch (error) {
      if (currentEpoch !== epoch.current) return;
      setConflict(true); setConsent(false);
      if (error instanceof ApiError && error.status === 409) { setConflict(true); setConsent(false); setDetailError("Esta proposta ou seu conteúdo mudou durante a revisão. Recarregue e confira a comparação atual antes de decidir novamente."); }
      else setDetailError(error instanceof ApiError ? error.message : "Não foi possível confirmar a decisão. Recarregue a proposta para consultar o estado atual antes de tentar novamente.");
    } finally { if (currentEpoch === epoch.current) { activeMutation.current = false; setBusy(false); } }
  }
  if (!isAdmin) return <p role="alert">Acesso restrito à administração.</p>;
  return <section className="admin-clinical-changes">
    <header><h1>Mudanças de Conduta Baseadas em Novas Evidências para Aprovação</h1><p>O administrador responsável revisa as sugestões de conduta e tratamento identificadas pelo CorVIA Intelligence. A aprovação aplica a proposta ao conteúdo do site.</p></header>
    <nav aria-label="Estado das propostas">{(Object.keys(statusNames) as Status[]).map(value => <button type="button" key={value} className="botao botao--secundario" aria-pressed={status === value} disabled={busy} onClick={() => selectStatus(value)}>{statusNames[value]}</button>)}</nav>
    {notice && <p role="status">{notice}</p>}
    <div className="admin-clinical-changes__layout">
      <section aria-label="Lista de propostas">
        {listError ? <div role="alert"><p>{listError}</p><button type="button" className="botao botao--secundario" onClick={() => setRevision(value => value + 1)}>Tentar novamente</button></div> : !list ? <p role="status">Carregando propostas…</p> : <>
          <p>{list.total} proposta{list.total === 1 ? "" : "s"}</p>
          {!list.items.length && <p>Nenhuma proposta nesta categoria.</p>}
          <ul className="admin-clinical-changes__list">{list.items.map(proposal => <li key={proposal.id}><button type="button" className="botao botao--secundario" disabled={busy} aria-pressed={selected === proposal.id} onClick={() => { setSelected(proposal.id); setNotice(""); }}><strong>{proposal.proposed_changes[0]?.label || proposal.guideline.title}</strong><span>{proposal.guideline.title}</span><span>{proposal.proposed_changes.length} alterações · {date(proposal.created_at)}</span></button></li>)}</ul>
          <nav aria-label="Paginação de propostas"><button type="button" className="botao botao--secundario" disabled={busy || offset === 0} onClick={() => { setOffset(value => Math.max(0, value - 50)); setSelected(null); }}>Anterior</button><button type="button" className="botao botao--secundario" disabled={busy || offset + 50 >= list.total} onClick={() => { setOffset(value => value + 50); setSelected(null); }}>Próxima</button></nav>
        </>}
      </section>
      <section aria-label="Revisão da proposta" aria-busy={busy}>
        {detailError && <div role="alert"><p>{detailError}</p><button type="button" className="botao botao--secundario" disabled={busy} onClick={() => setDetailRevision(value => value + 1)}>Recarregar proposta</button></div>}
        {selected == null ? <p>Selecione uma proposta para comparar o conteúdo atual com a mudança sugerida.</p> : !detail ? !detailError && <p role="status">Carregando comparação…</p> : <>
          <h2>{detail.proposed_changes[0]?.label || detail.guideline.title}</h2><p><strong>Publicação de origem:</strong> {detail.guideline.title}</p>{detail.verification_status === "needs_verification" && <p role="status" className="clinical-editorial-warning">A verificação automática desta sugestão foi inconclusiva. Confira as fontes e a correspondência com o item afetado antes de autorizar sua aplicação.</p>}<p>{statusNames[detail.status]} · Proposta recebida em {date(detail.created_at)}</p>
          {sourceUrl(detail.guideline.url) && <a href={sourceUrl(detail.guideline.url)!} target="_blank" rel="noopener noreferrer">Abrir publicação de origem ↗</a>}
          {detail.guideline.doi && <p>DOI: {detail.guideline.doi}</p>}
          {detail.proposed_changes.map((change, index) => <article className="admin-clinical-changes__change" key={`${change.item_type}-${change.item_id}-${index}`}><h3>{change.label}</h3><p>{typeNames[change.item_type] || change.item_type}</p>{change.effect_kind && <p><strong>{change.effect_kind === "references_metadata" ? "Atualização de fontes e referências" : change.effect_kind === "editorial_summary" ? "Síntese editorial para revisão" : "Alteração de conteúdo clínico"}</strong></p>}{change.impact_scope?.fluxograma && <p>Afeta o fluxograma desta doença.</p>}{Boolean(change.impact_scope?.emergency_protocols?.length) && <div><strong>Protocolos de emergência relacionados</strong><ul>{change.impact_scope!.emergency_protocols!.map(protocol => <li key={protocol.slug}>{protocol.title} · {protocol.relation}</li>)}</ul></div>}<h4>Justificativa da mudança</h4><p>{change.change_summary_pt || "Justificativa não informada nesta proposta."}</p>{sourceUrl(change.source_url) && <a href={sourceUrl(change.source_url)!} target="_blank" rel="noopener noreferrer">Consultar fonte desta alteração ↗</a>}<div className="admin-clinical-changes__comparison"><section><h4>Antes</h4><Snapshot value={change.before} fallback={change.before_text} fields={change.changed_fields} /></section><section><h4>Após aprovação</h4><Snapshot value={change.after} fallback={change.after_text} fields={change.changed_fields} /></section></div></article>)}
          {detail.status === "pending" && <fieldset disabled={busy || conflict} className="admin-clinical-changes__decision"><legend>Decisão editorial</legend>{detail.can_approve === false && <p role="status">{detail.blocking_reason || "Esta sugestão ainda não pode ser aplicada: o alvo ou a fonte precisa de confirmação. Você pode rejeitá-la com uma justificativa."}</p>}<label><input type="checkbox" disabled={detail.can_approve === false} checked={consent} onChange={event => setConsent(event.target.checked)} /> Revisei as fontes e todas as alterações desta proposta e autorizo sua aplicação no conteúdo do CorVIA.</label><button type="button" className="botao" disabled={detail.can_approve === false || !consent || !detail.proposed_changes.length || busy || conflict} onClick={() => void decide("approve")}>{busy ? "Confirmando decisão…" : "Aprovar e aplicar alterações"}</button><label>Motivo da rejeição<textarea value={reason} onChange={event => setReason(event.target.value)} rows={3} maxLength={2000} /></label><button type="button" className="botao botao--secundario" disabled={!reason.trim() || busy || conflict} onClick={() => void decide("reject")}>Rejeitar proposta</button></fieldset>}
          <section><h3>Histórico de revisão</h3>{detail.reviewed_at ? <p>{detail.status === "approved" ? "Aprovada e aplicada" : "Rejeitada"} em {date(detail.reviewed_at)} por {detail.reviewer_name || `Administrador ${detail.reviewer_id ?? "não informado"}`}.</p> : <p>Aguardando decisão administrativa.</p>}{detail.rejection_reason && <p>Motivo: {detail.rejection_reason}</p>}{detail.audit_events?.length ? <ul>{detail.audit_events.map((event,index) => <li key={`${event.at}-${index}`}>{date(event.at)} · {event.reviewer_name || (event.reviewer_id ? `Administrador ${event.reviewer_id}` : "CorVIA Intelligence")} · {eventNames[event.action] || "Evento de revisão"}{event.reason ? ` · ${event.reason}` : ""}</li>)}</ul> : null}</section>
        </>}
      </section>
    </div>
  </section>;
}
