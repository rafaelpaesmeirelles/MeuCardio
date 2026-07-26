import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.png", "apple-touch-icon.png", "logo-horizontal.png", "brasao.png"],
      manifest: {
        name: "CardioBene — Serviço de Cardiologia",
        short_name: "CardioBene",
        description:
          "Plataforma clínica do Serviço de Cardiologia da Beneficência Portuguesa de Ribeirão Preto.",
        lang: "pt-BR",
        theme_color: "#6E1220",
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
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        runtimeCaching: [
          {
            // Conteúdo científico fica disponível offline após a primeira leitura.
            urlPattern: /\/api\/(library|calculators|drugs)/,
            handler: "StaleWhileRevalidate",
            options: { cacheName: "cardiobene-conteudo", expiration: { maxEntries: 500 } }
          },
          {
            // Dados de paciente nunca são cacheados.
            urlPattern: /\/api\/round/,
            handler: "NetworkOnly"
          }
        ]
      }
    })
  ],
  server: {
    port: 5173,
    proxy: { "/api": { target: "http://backend:8000", changeOrigin: true } }
  }
});
