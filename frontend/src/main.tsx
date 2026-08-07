import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./lib/auth";
import "./styles/tokens.css";
import "./styles/shell.css";
import "./styles/produto.css";
import "./styles/tour.css";

// PWA: quando um novo service worker assume o controle (skipWaiting +
// clientsClaim, configurados em vite.config.ts), recarrega a aba uma única
// vez — sem isto, o app já aberto continua rodando o JS antigo mesmo com o
// SW novo já ativo, e o usuário só vê a versão nova fechando todas as abas.
//
// MAS nunca recarregar com uma resposta do assistente em andamento — achado
// ao vivo em produção: o controllerchange pode disparar bem no meio de um
// streaming (dois deploys de frontend em poucos minutos), e um reload nesse
// instante corta a resposta na cara do usuário. `window.__streamAtivo` é
// setado pelo Assistente.tsx durante o streaming; se a troca de SW acontece
// nesse meio-tempo, a recarga fica pendente e só executa quando o streaming
// terminar (`window.__streamEncerrado()`), nunca no meio dele.
//
// BUG REAL corrigido em 07/08/2026, achado ao vivo (Rafael reportou "o site
// não atualiza automático quando entra ou acessa outra sessão ou opção"):
// a guarda original usava uma bandeira PERMANENTE em sessionStorage
// (`"sw-recarregado" === "1"`, nunca limpa) para evitar loop de reload. Com
// deploys frequentes no mesmo dia, isso quebrava a própria função da guarda:
// a PRIMEIRA troca de versão na aba recarregava e marcava a bandeira; toda
// troca de versão SEGUINTE, na mesma aba, era silenciosamente ignorada — o
// usuário ficava preso na versão daquele primeiro reload até fechar a aba.
// Trocado por um "debounce" por tempo: só ignora um controllerchange se o
// último reload aconteceu há menos de 5s (protege contra o evento disparar
// duas vezes seguidas pelo mesmo deploy), e volta a reagir normalmente a
// qualquer deploy depois disso — que é sempre minutos/horas depois, na
// prática deste projeto.
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
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.addEventListener("controllerchange", tentarRecarregarPorNovoSW);
}
(window as unknown as { __streamEncerrado: () => void }).__streamEncerrado = () => {
  if (swRecargaPendente) tentarRecarregarPorNovoSW();
};

// Pedido do Rafael, 07/08/2026: o conteúdo científico está em expansão
// contínua (centenas de itens publicados por dia), e o assinante não pode
// ficar preso numa aba com bundle antigo sem saber que há versão nova. Isto
// NÃO força reload nenhum por si só — `.update()` só verifica e baixa uma
// versão nova do service worker em segundo plano (o browser faz um GET
// condicional do sw.js; se o arquivo não mudou, é praticamente grátis). Quem
// de fato troca de versão e recarrega a aba é o listener de `controllerchange`
// acima, que só dispara se `.update()` encontrar algo realmente novo — por
// isso é seguro chamar em toda navegação interna, sem o custo de recarregar a
// página inteira a cada clique (que quebraria a experiência de SPA à toa).
function verificarAtualizacaoDoServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.getRegistration().then((registro) => registro?.update()).catch(() => {
    // Sem rede, ou SW ainda não registrado — não é erro para o usuário ver.
  });
}
verificarAtualizacaoDoServiceWorker();
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") verificarAtualizacaoDoServiceWorker();
});
window.addEventListener("pageshow", verificarAtualizacaoDoServiceWorker);
// Chamado por App.tsx a cada troca de rota (ver `useVerificarAtualizacao` em
// App.tsx) — é o gancho que cobre "toda página interna aberta".
(window as unknown as { __corviaVerificarAtualizacao?: () => void }).__corviaVerificarAtualizacao =
  verificarAtualizacaoDoServiceWorker;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
