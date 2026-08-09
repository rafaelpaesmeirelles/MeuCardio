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

async function verificarAtualizacaoCompleta() {
  // 1) compara o commit do bundle com o commit realmente servido pelo backend;
  // 2) pede ao navegador para verificar o service worker sem esperar o ciclo
  // automático dele. Nenhuma das duas ações recarrega se não houver deploy novo.
  await verificarVersaoAtual();
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

void verificarAtualizacaoCompleta();
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") void verificarAtualizacaoCompleta();
});
window.addEventListener("pageshow", () => void verificarAtualizacaoCompleta());

// App.tsx chama isto em toda mudança de rota. É uma checagem de versão, não
// um F5 em todo clique: só há recarga quando o commit realmente mudou.
(window as unknown as { __corviaVerificarAtualizacao?: () => void }).__corviaVerificarAtualizacao = () => {
  void verificarAtualizacaoCompleta();
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
