import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

type Template = { id: number; title: string; doc_type: string; body: string };
type Gerado = { id: number; title: string; doc_type: string; rendered_body: string; medico: any };

function extrairVariaveis(body: string): string[] {
  const encontradas = new Set<string>();
  const regex = /\{\{(\w+)\}\}/g;
  let m;
  while ((m = regex.exec(body))) encontradas.add(m[1]);
  return [...encontradas];
}

export default function PatientDocumentos({ patientId }: { patientId: number }) {
  const [templates, setTemplates] = useState<Template[] | null>(null);
  const [templateId, setTemplateId] = useState<number | null>(null);
  const [valores, setValores] = useState<Record<string, string>>({});
  const [gerando, setGerando] = useState(false);
  const [gerado, setGerado] = useState<Gerado | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => { api.get<Template[]>("/document-templates").then(setTemplates); }, []);

  const template = templates?.find((t) => t.id === templateId) ?? null;
  const variaveis = template ? extrairVariaveis(template.body) : [];

  async function gerar() {
    if (!template) return;
    setGerando(true);
    setErro("");
    try {
      const r = await api.post<Gerado>("/document-templates/gerar", {
        template_id: template.id, patient_id: patientId, variables: valores,
      });
      setGerado(r);
      setTimeout(() => window.print(), 200);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível gerar.");
    } finally {
      setGerando(false);
    }
  }

  return (
    <div className="cartao" style={{ background: "var(--fundo)" }}>
      <p className="eyebrow" style={{ margin: 0 }}>Atestado / laudo</p>

      {templates === null ? (
        <p style={{ fontSize: "0.86rem" }}>Carregando…</p>
      ) : templates.length === 0 ? (
        <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
          Nenhum modelo criado ainda. <Link to="/documentos">Criar um modelo</Link>.
        </p>
      ) : (
        <>
          <select value={templateId ?? ""} onChange={(e) => { setTemplateId(Number(e.target.value) || null); setValores({}); }}
                  style={{ marginTop: "0.5rem" }}>
            <option value="">Escolha um modelo…</option>
            {templates.map((t) => <option key={t.id} value={t.id}>{t.title}</option>)}
          </select>

          {variaveis.map((v) => (
            <input key={v} placeholder={v} value={valores[v] ?? ""}
                   onChange={(e) => setValores({ ...valores, [v]: e.target.value })}
                   style={{ marginTop: "0.4rem" }} />
          ))}

          {template && (
            <button className="botao" style={{ marginTop: "0.6rem" }} onClick={gerar} disabled={gerando}>
              {gerando ? "Gerando…" : "Gerar e imprimir"}
            </button>
          )}
          {erro && <p style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
        </>
      )}

      {gerado && (
        <div className="folha-impressao">
          <h2>{gerado.title}</h2>
          <p>{gerado.medico.full_name} — {gerado.medico.council_name} {gerado.medico.council_number}/{gerado.medico.council_state}</p>
          <hr />
          <p style={{ whiteSpace: "pre-wrap" }}>{gerado.rendered_body}</p>
        </div>
      )}
    </div>
  );
}
