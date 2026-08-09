import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./lib/auth";
import { liberarRecargaPendente, verificarVersaoAtual } from "./lib/freshness";
import "./styles/tokens.css";
import "./styles/shell.css";
import "./styles/produto.css";
import "./styles/tour.css";

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

// Qualquer interação relevante também consulta a versão, limitada internamente
// a uma chamada a cada 5 segundos. Assim uma aba aberta por horas percebe um
// deploy mesmo sem mudança de rota, sem transformar cada clique em tráfego.
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
  </React.StrictMode>
);
