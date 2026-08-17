import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./lib/auth";
import { liberarRecargaPendente, verificarVersaoAtual } from "./lib/freshness";
import "./styles/tokens.css";
import "./styles/shell.css";
import "./styles/clinical-os.css";
import "./styles/clinical-os-polish.css";
import "./styles/clinical-os-a11y.css";
import "./styles/produto.css";
import "./styles/tour.css";
import "./styles/tour-clinical-os.css";
import "./styles/clinical-command-center-v2.css";
import "./styles/clinical-pages-v2.css";
import "./styles/clinical-medications-v2.css";
import "./styles/clinical-knowledge-v2.css";
import "./styles/clinical-evidence-v2.css";
import "./styles/clinical-work-v2.css";
import "./styles/clinical-mobile-nav-v2.css";
import "./styles/public-clinical-command-v2.css";
import "./styles/clinical-command-center-canonical.css";
import "./styles/clinical-mobile-more-canonical.css";
import "./styles/corvia-mail-clinical-command.css";
import "./styles/corvia-mail-brand.css";
import "./styles/clinical-domains-canonical.css";
import "./styles/clinical-patient-command.css";
import "./styles/clinical-agenda-command.css";
import "./styles/clinical-documents-command.css";
import "./styles/clinical-assistant-command.css";
import "./styles/clinical-intelligence-context.css";
import "./styles/clinical-account-admin-command.css";
import "./styles/clinical-editorial-safety.css";
import "./styles/clinical-contextual-tip.css";
import "./styles/clinical-agenda-final-polish.css";
import "./styles/clinical-brand-final.css";
import "./styles/clinical-overlay-safety.css";
import "./styles/clinical-command-center-compat.css";
import "./styles/clinical-canonical-fidelity.css";
import "./styles/clinical-home-board-fidelity.css";
import "./styles/clinical-shell-board-fidelity.css";
import "./styles/clinical-medication-board-fidelity.css";
import "./styles/clinical-patient-board-fidelity.css";
import "./styles/clinical-emergency-board-fidelity.css";
import "./styles/clinical-assistant-board-fidelity.css";
import "./styles/clinical-home-mobile-final.css";
import "./styles/clinical-full-viewport.css";
import "./styles/clinical-release-hardening.css";
import "./styles/prehome-approved-auth-flow.css";
import "./styles/prehome-reference-final.css";
import "./styles/clinical-reference-board-final.css";
import "./styles/clinical-navigation-reference-final.css";
import "./styles/clinical-reference-fidelity-release.css";
import "./styles/release-candidate-hotfix.css";
import "./styles/clinical-interior-board-lock.css";
import "./styles/postdeploy-home-density.css";
import "./styles/clinical-form-control-contrast.css";

let swRecargaPendente = false;
function tentarRecarregarPorNovoSW() {
  const ultimaRecargaEm = Number(sessionStorage.getItem("sw-recarregado-em") || "0");
  if (Date.now() - ultimaRecargaEm < 5000) return;
  if ((window as unknown as { __streamAtivo?: boolean }).__streamAtivo) {
    swRecargaPendente = true;
    return;
  }
  sessionStorage.setItem("sw-recarregado-em", String(Date.now()));
  window.location.reload();
}

async function verificarAtualizacaoCompleta(forcar = false) {
  await verificarVersaoAtual(forcar);
  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.getRegistration().then((registro) => registro?.update()).catch(() => undefined);
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.addEventListener("controllerchange", tentarRecarregarPorNovoSW);
}

(window as unknown as { __streamEncerrado: () => void }).__streamEncerrado = () => {
  liberarRecargaPendente();
  if (swRecargaPendente) {
    swRecargaPendente = false;
    tentarRecarregarPorNovoSW();
  }
};

void verificarAtualizacaoCompleta(true);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") void verificarAtualizacaoCompleta(true);
});
window.addEventListener("pageshow", () => void verificarAtualizacaoCompleta(true));

document.addEventListener("click", () => void verificarAtualizacaoCompleta(false), { capture: true });
document.addEventListener("keydown", () => void verificarAtualizacaoCompleta(false), { capture: true });

(window as unknown as { __corviaVerificarAtualizacao?: () => void }).__corviaVerificarAtualizacao = () => {
  void verificarAtualizacaoCompleta(true);
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
