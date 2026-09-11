import FinalizarDocumentoGerado from "./FinalizarDocumentoGerado";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import "../styles/patient-round-text.css";

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
  const [erroModelos, setErroModelos] = useState("");
  const consultaModelos = useRef(0);
  const consultaGeracao = useRef(0);

  async function carregarModelos() {
    const consulta = ++consultaModelos.current;
    setTemplates(null);
    setErroModelos("");
    try {
      const modelos = await api.get<Template[]>("/document-templates");
      if (consulta === consultaModelos.current) setTemplates(modelos);
    } catch (e) {
      if (consulta === consultaModelos.current) {
        setErroModelos(e instanceof Error ? e.message : "Não foi possível carregar os modelos.");
      }
    }
  }

  useEffect(() => {
    carregarModelos();
    return () => { consultaModelos.current += 1; };
  }, []);

  useEffect(() => {
    consultaGeracao.current += 1;
    setTemplateId(null);
    setValores({});
    setGerado(null);
    setGerando(false);
    setErro("");
    return () => { consultaGeracao.current += 1; };
  }, [patientId]);

  function selecionarModelo(id: number | null) {
    // Descarta respostas de outro contexto; não desfaz uma geração no servidor.
    consultaGeracao.current += 1;
    setTemplateId(id);
    setValores({});
    setGerado(null);
    setGerando(false);
    setErro("");
  }

  const template = templates?.find((t) => t.id === templateId) ?? null;
  const variaveis = template ? extrairVariaveis(template.body) : [];

  async function gerar() {
    if (!template || gerando) return;
    const consulta = ++consultaGeracao.current;
    setGerando(true);
    setGerado(null);
    setErro("");
    try {
      const r = await api.post<Gerado>("/document-templates/gerar", {
        template_id: template.id, patient_id: patientId, variables: valores,
      });
      if (consulta === consultaGeracao.current) setGerado(r);
    } catch (e) {
      if (consulta === consultaGeracao.current) {
        setErro(e instanceof Error ? e.message : "Não foi possível gerar.");
      }
    } finally {
      if (consulta === consultaGeracao.current) setGerando(false);
    }
  }

  return (
    <div className="cartao" style={{ background: "var(--fundo)" }}>
      <p className="eyebrow patient-round-heading" style={{ margin: 0 }}>Atestado / laudo</p>

      {erroModelos ? (
        <>
          <p role="alert" style={{ color: "var(--alerta)" }}>{erroModelos}</p>
          <button className="botao botao--secundario" onClick={carregarModelos}>Recarregar modelos</button>
        </>
      ) : templates === null ? (
        <p style={{ fontSize: "0.86rem" }}>Carregando…</p>
      ) : templates.length === 0 ? (
        <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
          Nenhum modelo criado ainda. <Link to="/documentos">Criar um modelo</Link>.
        </p>
      ) : (
        <>
          <label htmlFor={`modelo-documento-${patientId}`} style={{ display: "block", marginTop: "0.5rem", color: "var(--atelier-ink, var(--texto))", WebkitTextFillColor: "currentColor" }}>Modelo de atestado ou laudo</label>
          <select id={`modelo-documento-${patientId}`} value={templateId ?? ""} onChange={(e) => selecionarModelo(Number(e.target.value) || null)}
                  style={{ marginTop: "0.5rem" }}>
            <option value="">Escolha um modelo…</option>
            {templates.map((t) => <option key={t.id} value={t.id}>{t.title}</option>)}
          </select>

          {variaveis.map((v) => (
            <div key={v} style={{ marginTop: "0.4rem" }}>
              <label htmlFor={`variavel-documento-${patientId}-${templateId}-${v}`} style={{ color: "var(--atelier-ink, var(--texto))", WebkitTextFillColor: "currentColor" }}>{v}</label>
              <input id={`variavel-documento-${patientId}-${templateId}-${v}`} placeholder={v} value={valores[v] ?? ""}
                   onChange={(e) => setValores({ ...valores, [v]: e.target.value })}
                   style={{ marginTop: "0.4rem" }} />
            </div>
          ))}

          {template && (
            <button className="botao" style={{ marginTop: "0.6rem" }} onClick={gerar} disabled={gerando}>
              {gerando ? "Gerando…" : "Gerar documento"}
            </button>
          )}
          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
        </>
      )}

      {gerado && (
        <FinalizarDocumentoGerado key={gerado.id} geradoId={gerado.id}
          nomeArquivoBase={gerado.doc_type} provedores={null} onFechar={() => setGerado(null)} />
      )}
    </div>
  );
}
