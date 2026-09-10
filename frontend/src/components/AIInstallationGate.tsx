import type { ReactNode } from "react";
import { Link } from "react-router-dom";

/** Discovery stays visible; a disabled installation never mounts operational UI. */
export default function AIInstallationGate({ enabled, label, children }: { enabled: boolean; label: string; children: ReactNode }) {
  if (enabled) return <>{children}</>;
  return <section className="pagina">
    <div className="cartao" style={{ maxWidth: 640 }}>
      <p className="eyebrow">Recursos de IA</p>
      <h1>{label}</h1>
      <p role="status">Este recurso ainda não está ativo nesta instalação do CorVIA.</p>
      <p>A integração precisa ser concluída pela administração para liberar o uso.</p>
      <Link className="botao botao--secundario" to="/">Voltar ao início</Link>
    </div>
  </section>;
}
