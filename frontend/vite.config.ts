import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

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
            // Recarregar/navegar tenta SEMPRE a rede primeiro. O cache do shell
            // só é fallback de indisponibilidade, nunca a fonte preferencial.
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
            // Assets têm hash de conteúdo no nome; mudança = URL nova. Rede
            // primeiro evita um SW antigo prolongar a vida de um bundle antigo.
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
            // Achado na revisão de segurança da issue #52 (11/08/2026): o
            // NetworkOnly genérico abaixo, ao passar a cobrir TODO /api/*,
            // engoliu sem querer a exceção deliberada do Modo Emergência —
            // desenhado desde 03/08/2026 para funcionar OFFLINE depois do
            // primeiro carregamento (documentado em CLAUDE.md: "o modo
            // offline-first do Emergência não dispara requisição de rede
            // depois de aberto"; é por isso, inclusive, que o Hub de
            // integração "Tudo sobre este tema" foi excluído do Modo
            // Emergência de propósito — essa garantia não podia quebrar).
            // Precisa vir ANTES da regra genérica: o Workbox usa a primeira
            // rota que casa, e um urlPattern mais específico só "vence" um
            // mais genérico se estiver antes na lista.
            urlPattern: /\/api\/emergencia/,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "corvia-emergencia-v2",
              expiration: { maxEntries: 8 },
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            // Ecossistema em atualização contínua: nenhuma outra resposta de
            // API é servida do cache do service worker. Isso abrange
            // conteúdo, agenda, CorvIA Mail, dados clínicos e status de
            // versão — a única exceção deliberada é /api/emergencia, acima.
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
