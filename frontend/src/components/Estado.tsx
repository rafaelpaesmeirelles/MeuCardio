import "../styles/estado-loading.css";

export function Carregando({ texto = "Carregando…" }: { texto?: string }) {
  return (
    <div className="corvia-loading-state" role="status" aria-live="polite">
      <img src="/corvia-mark-canonical.svg" alt="" aria-hidden="true" />
      <span className="corvia-loading-state__orbit" aria-hidden="true" />
      <p>{texto}</p>
    </div>
  );
}

export function Erro({ mensagem }: { mensagem: string }) {
  return (
    <div className="cartao" style={{ borderLeft: "3px solid var(--alerta)" }} role="alert">
      <p style={{ margin: 0 }}>{mensagem}</p>
    </div>
  );
}

export function Vazio({ titulo, acao }: { titulo: string; acao?: string }) {
  return (
    <div className="cartao">
      <h3>{titulo}</h3>
      {acao && <p style={{ margin: 0, color: "var(--texto-secundario)" }}>{acao}</p>}
    </div>
  );
}

export function SeloRevisao({ status }: { status: string }) {
  const mapa: Record<string, [string, string]> = {
    revisado: ["selo selo--revisado", "Revisado"],
    pendente_revisao: ["selo", "Revisão pendente"],
    verificacao_humana_necessaria: ["selo selo--pendente", "Verificação humana necessária"],
  };
  const [cls, texto] = mapa[status] ?? ["selo", status];
  return <span className={cls}>{texto}</span>;
}
