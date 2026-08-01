import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./lib/auth";
import "./styles/tokens.css";
import "./styles/shell.css";

// PWA: quando um novo service worker assume o controle (skipWaiting +
// clientsClaim, configurados em vite.config.ts), recarrega a aba uma única
// vez — sem isto, o app já aberto continua rodando o JS antigo mesmo com o
// SW novo já ativo, e o usuário só vê a versão nova fechando todas as abas.
// Guarda em sessionStorage evita loop se o evento disparar mais de uma vez
// na mesma sessão de aba.
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (sessionStorage.getItem("sw-recarregado") === "1") return;
    sessionStorage.setItem("sw-recarregado", "1");
    window.location.reload();
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
