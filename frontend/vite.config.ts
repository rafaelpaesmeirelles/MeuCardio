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
// A análise cardiovascular depende do backend e do provedor multimodal em toda
// execução. O chunk continua disponível por NetworkFirst, mas não ocupa o
// precache inicial com uma tela que não funciona offline.
const analiseCardiovascularSomenteOnline = /(?:^|\/)(?:ECGQuickOpinion|CardiovascularExamAI)-[^/]*\.(?:js|css)$/;
// A busca transversal depende da API para resultados, conexões e detalhes de
// medicamentos. O chunk segue disponível por NetworkFirst, sem ocupar o
// precache com uma tela que não produz conteúdo offline.
const buscaTudoComTudoSomenteOnline = /(?:^|\/)Busca-[^/]*\.js$/;
// Checklists aplicados, trilhas e materiais dependem da API para carregar
// estado/conteúdo e para qualquer mutação ou geração de PDF. Pré-carregar os
// chunks não os torna utilizáveis offline; eles permanecem disponíveis pelo
// cache NetworkFirst de assets quando acessados.
const conteudoConectadoSomenteOnline = /(?:^|\/)(?:ChecklistModelo|ChecklistAlta|MaterialPaciente|MaterialPacienteDetalhe|Trilha)-[^/]*\.js$/;

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["corvia-mark-canonical.svg", "corvia-logo-canonical.svg", "corvia-logo-canonical-dark.svg"],
      manifest: {
        name: "CorVIA — Cardiology Spaces",
        short_name: "CorVIA",
        description: "Ambientes de cardiologia centrados no médico: conhecimento, contexto, decisão e ação conectados.",
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
        // Uma navegação digitada diretamente para /api precisa chegar ao
        // backend. Sem esta negação, o fallback SPA pode devolver index.html
        // no lugar de JSON e esconder falhas de sessão em PWA/mobile.
        navigateFallbackDenylist: [/^\/api\//],
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        // O PNG existe para clientes de e-mail que não renderizam SVG, mas
        // não precisa ocupar o precache offline do aplicativo.
        globIgnores: ["corvia-logo-canonical.png", "corvia-logo.png"],
        manifestTransforms: [
          async (entries) => ({
            manifest: entries.filter((entry) => {
              if (loginSomenteOnline.test(entry.url)) return false;
              if (validacaoPublicaSomenteOnline.test(entry.url)) return false;
              if (analiseCardiovascularSomenteOnline.test(entry.url)) return false;
              if (buscaTudoComTudoSomenteOnline.test(entry.url)) return false;
              if (conteudoConectadoSomenteOnline.test(entry.url)) return false;
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
            urlPattern: ({ request, url }) => request.mode === "navigate" && !url.pathname.startsWith("/api/"),
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
