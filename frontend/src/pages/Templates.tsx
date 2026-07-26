import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Template = { id: number; title: string; doc_type: string; body: string };

const RÓTULO: Record<string, string> = { atestado: "Atestado", laudo: "Laudo", outro: "Outro" };

export default function Templates() {
  const [lista, setLista] = useState<Template[] | null>(null);
  const [editando, setEditando] = useState<Partial<Template> | null>(null);
  const [salvando, setSalvando] = useState(false);

  const recarregar = () => api.get<Template[]>("/document-templates").then(setLista);
  useEffect(() => { recarregar(); }, []);

  async function salvar() {
    if (!editando?.title || !editando.doc_type || !editando.body) return;
    setSalvando(true);
    try {
      if (editando.id) {
        await api.put(`/document-templates/${editando.id}`, editando);
      } else {
        await api.post("/document-templates", editando);
      }
      setEditando(null);
      recarregar();
    } finally {
      setSalvando(false);
    }
  }

  async function apagar(id: number) {
    await api.delete(`/document-templates/${id}`);
    recarregar();
  }

  return (
    <>
      <p className="eyebrow">Documentos</p>
      <h1>Modelos de atestado e laudo</h1>
      <p style={{ color: "var(--cinza-texto)", maxWidth: "60ch" }}>
        Crie modelos com variáveis entre chaves duplas — ex.: <code>{"{{dias_afastamento}}"}</code> —
        preenchidas na hora de gerar o documento, dentro da ficha de cada paciente.
      </p>

      <button className="botao" style={{ marginTop: "0.8rem" }}
              onClick={() => setEditando({ title: "", doc_type: "atestado", body: "" })}>
        + Novo modelo
      </button>

      {editando && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <label>Título</label>
          <input value={editando.title ?? ""} onChange={(e) => setEditando({ ...editando, title: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Tipo</label>
          <select value={editando.doc_type ?? "atestado"}
                  onChange={(e) => setEditando({ ...editando, doc_type: e.target.value })}>
            <option value="atestado">Atestado</option>
            <option value="laudo">Laudo</option>
            <option value="outro">Outro</option>
          </select>
          <label style={{ marginTop: "0.5rem" }}>Corpo do documento</label>
          <textarea rows={8} value={editando.body ?? ""}
                    placeholder={"Atesto que o(a) paciente {{nome}} necessita de afastamento de suas atividades por {{dias_afastamento}} dias, a partir de {{data_inicio}}, por motivo de {{motivo}}."}
                    onChange={(e) => setEditando({ ...editando, body: e.target.value })} />
          <div style={{ display: "flex", gap: 8, marginTop: "0.6rem" }}>
            <button className="botao" onClick={salvar} disabled={salvando}>
              {salvando ? "Salvando…" : "Salvar modelo"}
            </button>
            <button className="botao botao--secundario" onClick={() => setEditando(null)}>Cancelar</button>
          </div>
        </div>
      )}

      <div style={{ marginTop: "1.2rem" }}>
        {lista === null ? (
          <Carregando />
        ) : lista.length === 0 ? (
          <Vazio titulo="Nenhum modelo ainda" acao="Crie o primeiro modelo acima." />
        ) : (
          lista.map((t) => (
            <div key={t.id} className="cartao" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <div>
                <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[t.doc_type] ?? t.doc_type}</p>
                <strong>{t.title}</strong>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                        onClick={() => setEditando(t)}>Editar</button>
                <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                        onClick={() => apagar(t.id)}>Apagar</button>
              </div>
            </div>
          ))
        )}
      </div>
    </>
  );
}
