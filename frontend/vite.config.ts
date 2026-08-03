import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

const limitePrecacheJs = 160 * 1024;

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
            urlPattern: /\/assets\/.*\.(?:js|css)$/,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "corvia-assets-v1",
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
            urlPattern: /\/api\/(library|calculators|drugs|material-paciente)/,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "corvia-conteudo",
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
