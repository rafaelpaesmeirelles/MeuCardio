import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

// O precache mantém o shell e chunks clínicos pequenos disponíveis sem rede.
// Chunks pesados e sob demanda (principalmente renderizadores de diagramas)
// ficam no runtime cache NetworkFirst em vez de inflar a instalação do PWA.
const limitePrecacheJs = 100 * 1024;
// Superfícies administrativas/raras não precisam compor a instalação offline
// inicial. Elas continuam funcionando normalmente e entram no runtime cache
// após o primeiro uso, sem retirar qualquer rota ou funcionalidade do produto.
const foraDoPrecacheInicial = /(?:^|\/)(?:Admin|AdminAssinantes|AdminFichaAssinante|FilaTelediagnostico|VerificacaoIdentidade)-[^/]*\.js$/;
// A tela de entrada depende de backend/rede por definição (senha e provedores
// externos). Não há ganho em precacheá-la; JS/CSS continuam carregando
// normalmente e entram no runtime cache após o primeiro acesso online.
const loginSomenteOnline = /(?:^|\/)Entrar-[^/]*\.(?:js|css)$/;

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.png", "apple-touch-icon.png", "logo-horizontal.png", "brasao.png"],
      manifest: {
        name: "CorVIA — Clinical OS do médico",
        short_name: "CorVIA",
        description: "Workspace clínico inteligente do médico: conhecimento, contexto, decisão e ação conectados.",
        lang: "pt-BR",
        theme_color: "#03101A",
        background_color: "#03101A",
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
              if (loginSomenteOnline.test(entry.url)) return false;
              if (!entry.url.endsWith(".js")) return true;
              if (foraDoPrecacheInicial.test(entry.url)) return false;
              if (/(?:^|\/)(?:index|registerSW)-[^/]*\.js$/.test(entry.url)) return true;
              return (entry.size ?? 0) <= limitePrecacheJs;
            }),
            warnings: [],
          }),
        ],
        navigateFallback: "index.html",
        runtimeCaching: [
          {
            urlPattern: ({ request }) => request.mode === "navigate",
            handler: "NetworkFirst",
            options: {
              cacheName: "corvia-navegacao-v2",
              networkTimeoutSeconds: 4,
              expiration: { maxEntries: 20 },
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            urlPattern: /\/assets\/.*\.(?:js|css)$/,
            handler: "NetworkFirst",
            options: {
              cacheName: "corvia-assets-v2",
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
            urlPattern: /\/api\//,
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