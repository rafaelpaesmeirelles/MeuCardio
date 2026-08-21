import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

const limitePrecacheJs = 100 * 1024;
const foraDoPrecacheInicial = /(?:^|\/)(?:Admin|AdminAssinantes|AdminFichaAssinante|FilaTelediagnostico|VerificacaoIdentidade|PrescricaoLivreEspecial)-[^/]*\.js$/;
const loginSomenteOnline = /(?:^|\/)(?:Entrar-[^/]*|login-[^/]*|SolicitarAcesso-[^/]*|EsqueciSenha-[^/]*|RedefinirSenha-[^/]*)\.(?:js|css)$/;
// A validação pública depende obrigatoriamente do backend para conferir SHA/PAdES
// e liberar o PDF original. Não há valor nem comportamento correto em precache
// offline dessa rota; os chunks continuam disponíveis por NetworkFirst em runtime.
const validacaoPublicaSomenteOnline = /(?:^|\/)ValidarDocumento-[^/]*\.(?:js|css)$/;

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["corvia-mark-canonical.svg", "corvia-logo-canonical.svg", "corvia-logo-canonical-dark.svg"],
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
          { src: "/corvia-mark-canonical.svg", sizes: "any", type: "image/svg+xml", purpose: "any" },
          { src: "/corvia-mark-canonical.svg", sizes: "any", type: "image/svg+xml", purpose: "maskable" }
        ]
      },
      workbox: {
        skipWaiting: true,
        clientsClaim: true,
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        // O PNG existe para clientes de e-mail que não renderizam SVG, mas
        // não precisa ocupar o precache offline do aplicativo.
        globIgnores: ["corvia-logo-canonical.png", "corvia-logo.png"],
        manifestTransforms: [
          async (entries) => ({
            manifest: entries.filter((entry) => {
              if (loginSomenteOnline.test(entry.url)) return false;
              if (validacaoPublicaSomenteOnline.test(entry.url)) return false;
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
