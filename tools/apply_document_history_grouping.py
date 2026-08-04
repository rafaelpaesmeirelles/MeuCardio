#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "frontend/src/pages/Templates.tsx"
source = path.read_text(encoding="utf-8")

changes = [
    (
        '''type GeradoDetalhe = {
  template_id: number | null;
  variables: Record<string, string> | null;
};
''',
        '''type GeradoDetalhe = {
  template_id: number | null;
  variables: Record<string, string> | null;
  patient_name: string | null;
};
''',
    ),
    (
        '''      setValoresIniciais(detalhe.variables ?? {});
      setGerandoDe(template);
''',
        '''      setValoresIniciais({
        ...(detalhe.variables ?? {}),
        nome_paciente: detalhe.patient_name ?? detalhe.variables?.nome_paciente ?? "",
      });
      setGerandoDe(template);
''',
    ),
    (
        '''  return (
    <>
      <p className="eyebrow">Documentos</p>
''',
        '''  const gruposGerados = new Map<string, Gerado[]>();
  for (const gerado of gerados ?? []) {
    const paciente = gerado.patient_name?.trim() || "Paciente não informado";
    gruposGerados.set(paciente, [...(gruposGerados.get(paciente) ?? []), gerado]);
  }

  return (
    <>
      <p className="eyebrow">Documentos</p>
''',
    ),
    (
        '''      ) : (
        gerados.map((g) => (
          <div key={g.id} className="cartao" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <div>
              <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[g.doc_type] ?? g.doc_type}</p>
              <strong>{g.patient_name ?? "Paciente não informado"}</strong>
              <div style={{ fontSize: "0.86rem" }}>{g.title}</div>
              <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                {new Date(g.created_at).toLocaleString("pt-BR")}
              </p>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                      onClick={() => recriarBaseadoEm(g.id)}>
                Recriar baseado neste
              </button>
              <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                      onClick={async () => {
                        const blob = await api.blob(`/document-templates/gerados/${g.id}/pdf`);
                        baixarBlob(blob, `${g.doc_type}-${g.id}.pdf`);
                      }}>
                Baixar PDF
              </button>
            </div>
          </div>
        ))
      )}
''',
        '''      ) : (
        [...gruposGerados.entries()]
          .sort(([a], [b]) => a.localeCompare(b, "pt-BR"))
          .map(([paciente, documentos]) => (
            <section key={paciente} style={{ marginBottom: "1rem" }}>
              <h3 style={{ marginBottom: "0.45rem" }}>{paciente}</h3>
              {documentos.map((g) => (
                <div key={g.id} className="cartao" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                  <div>
                    <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[g.doc_type] ?? g.doc_type}</p>
                    <strong>{g.title}</strong>
                    <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                      {new Date(g.created_at).toLocaleString("pt-BR")}
                    </p>
                  </div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                            onClick={() => recriarBaseadoEm(g.id)}>
                      Recriar baseado neste
                    </button>
                    <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                            onClick={async () => {
                              const blob = await api.blob(`/document-templates/gerados/${g.id}/pdf`);
                              baixarBlob(blob, `${g.doc_type}-${g.id}.pdf`);
                            }}>
                      Baixar PDF
                    </button>
                  </div>
                </div>
              ))}
            </section>
          ))
      )}
''',
    ),
]

for old, new in changes:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Trecho encontrado {count} vezes: {old[:100]!r}")
    source = source.replace(old, new, 1)

path.write_text(source, encoding="utf-8")
Path(__file__).unlink()
print("Histórico de documentos agrupado por paciente e recriação preservada.")
