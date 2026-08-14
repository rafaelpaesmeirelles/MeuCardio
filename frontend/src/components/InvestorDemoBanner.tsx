import { useAuth } from "../lib/auth";
import "../styles/investor-demo-banner.css";

export default function InvestorDemoBanner() {
  const { usuario } = useAuth();
  if (!usuario?.investidor) return null;

  return (
    <div className="investor-demo-banner" role="status" aria-live="polite">
      <span className="investor-demo-banner__dot" aria-hidden="true" />
      <strong>Modo Investidor</strong>
      <span>ambiente de demonstração · somente visualização</span>
    </div>
  );
}
