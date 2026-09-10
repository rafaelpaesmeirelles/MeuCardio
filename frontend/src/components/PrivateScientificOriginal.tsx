import { useEffect, useState } from "react";
import { api } from "../lib/api";

// Private originals are loaded only after the user selects Original. Authentication
// and ownership are enforced by the file endpoint; no analysis request is made.
export default function PrivateScientificOriginal({ documentId, title }: { documentId: number; title: string }) {
  const [file, setFile] = useState<{ url: string; type: string; text?: string } | null>(null);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    let objectUrl: string | undefined;
    setFile(null); setError(false);
    api.blob(`/documentos-cientificos-ia/${documentId}/arquivo`).then(async blob => {
      const type = blob.type.split(";")[0].toLowerCase();
      const text = ["text/plain", "text/csv"].includes(type) ? await blob.text() : undefined;
      if (!active) return;
      objectUrl = URL.createObjectURL(blob);
      setFile({ url: objectUrl, type, text });
    }).catch(() => { if (active) setError(true); });
    return () => { active = false; if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [documentId, attempt]);
  return <article className="card" aria-label="Original privado">
    <h3>Original — {title}</h3>
    {error ? <><p role="alert">Não foi possível abrir este original privado.</p><button className="btn" type="button" onClick={() => setAttempt(value => value + 1)}>Tentar novamente</button></>
      : !file ? <p role="status">Carregando original…</p>
      : <>
        {file.type === "application/pdf" ? <iframe title={`Original: ${title}`} src={file.url} sandbox="" style={{ width: "100%", height: "65vh", border: 0 }} />
          : file.text !== undefined ? <pre style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere", fontFamily: "inherit", maxHeight: "65vh", overflow: "auto" }}>{file.text}</pre>
          : <p>Este formato está disponível para baixar e abrir no aplicativo correspondente.</p>}
        <a className="btn" href={file.url} download={`documento-${documentId}-original.${file.type === "application/pdf" ? "pdf" : file.type === "text/csv" ? "csv" : file.type === "text/plain" ? "txt" : file.type.includes("wordprocessingml") ? "docx" : file.type.includes("presentationml") ? "pptx" : "bin"}`}>Baixar arquivo original</a>
      </>}
  </article>;
}
