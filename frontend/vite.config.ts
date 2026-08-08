import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

// Diagramas e outras páginas pesadas continuam disponíveis pelo cache em
// tempo de execução. O precache deve conter apenas o shell e módulos menores,
// para não atrasar a primeira instalação do PWA em rede móvel.
const limitePrecacheJs = 140 * 1024;

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.png", "apple-touch-icon.png", "logo-horizontal.png", "brasao.png"],
      manifest: {
        name: "Corvia — O caminho do coração",
        short_name: "Corvia",
        description: "Plataforma clínica de apoio à decisão em Cardiologia.",
        lang: "pt-BR",
        theme_color: "#0B2E45",
        background_color: "#FFFFFF",
        display: "standalone",
        orientation: "portrait",
        start_url: "/",
        icons: [
          { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "/icon-maskable.png", sizes: "512x512", type: "image/png", purpose: "maskable" }
        ]
      },
      workbox: {
        skipWaiting: true,
        clientsClaim: true,
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        manifestTransforms: [
          async (entries) => ({
            manifest: entries.filter((entry) => {
              if (!entry.url.endsWith(".js")) return true;
              if (/(?:^|\/)(?:index|registerSW)-[^/]*\.js$/.test(entry.url)) return true;
              return (entry.size ?? 0) <= limitePrecacheJs;
            }),
            warnings: [],
          }),
        ],
        navigateFallback: "index.html",
        runtimeCaching: [
          {
            // Achado em 08/08/2026, pedido do Rafael ("continua abrindo
            // páginas antigas em cache" mesmo recarregando a página): por
            // padrão, o Workbox intercepta TODA requisição de navegação
            // (inclusive um F5/recarregar) e responde com o `index.html`
            // pré-cacheado (navigateFallback) — isso acontece ANTES de
            // qualquer verificação HTTP normal, então o `Cache-Control:
            // no-cache` que o Caddy manda para o shell da aplicação nunca
            // chega a ser considerado: o service worker responde primeiro,
            // direto do cache, sem nem tentar a rede. Precisava de uma regra
            // própria e explícita para navegação, com a rede em primeiro
            // lugar — sem isso, o app inteiro podia ficar "congelado" na
            // versão instalada até o mecanismo de detecção de SW novo (em
            // main.tsx) disparar, o que não cobre um F5 simples.
            urlPattern: ({ request }) => request.mode === "navigate",
            handler: "NetworkFirst",
            options: {
              cacheName: "corvia-navegacao",
              networkTimeoutSeconds: 4,
              expiration: { maxEntries: 20 },
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            // Trocado de StaleWhileRevalidate para NetworkFirst pelo mesmo
            // motivo acima: cada arquivo já tem hash no nome (muda sozinho a
            // cada deploy), então a rede deveria ser sempre tentada primeiro;
            // o cache aqui existe só como resiliência para rede ruim/offline,
            // não como atalho que arrisca servir um bundle antigo.
            urlPattern: /\/assets\/.*\.(?:js|css)$/,
            handler: "NetworkFirst",
            options: {
              cacheName: "corvia-assets-v1",
              networkTimeoutSeconds: 4,
              expiration: { maxEntries: 160, maxAgeSeconds: 2592000 },
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            urlPattern: /\/api\/emergencia/,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "corvia-emergencia-v2",
              expiration: { maxEntries: 8 },
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            // NetworkFirst, não StaleWhileRevalidate — pedido do Rafael,
            // 07/08/2026: com o acervo em expansão contínua, mostrar a
            // versão em cache antes de tentar a rede (o que SWR faz) deixava
            // o assinante vendo conteúdo desatualizado na PRIMEIRA abertura
            // de cada tela, mesmo com internet boa; só a próxima abertura
            // pegava a atualização, porque SWR revalida DEPOIS de responder.
            // NetworkFirst busca a rede primeiro (assinante sempre vê o que
            // está publicado agora) e só cai para o cache se a rede falhar
            // ou demorar mais que `networkTimeoutSeconds` — preserva a
            // resiliência offline sem servir dado velho com internet normal.
            urlPattern: /\/api\/(library|calculators|drugs|material-paciente)/,
            handler: "NetworkFirst",
            options: {
              cacheName: "corvia-conteudo",
              networkTimeoutSeconds: 4,
              expiration: { maxEntries: 500 },
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            urlPattern: /\/api\/round/,
            handler: "NetworkOnly"
          }
        ]
      }
    })
  ],
  build: { manifest: true },
  server: {
    port: 5173,
    proxy: { "/api": { target: "http://backend:8000", changeOrigin: true } }
  }
});
