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
        name: "Corvia — O caminho do coração",
        short_name: "Corvia",
        description:
          "Plataforma clínica de apoio à decisão em Cardiologia.",
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
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        runtimeCaching: [
          {
            // Conteúdo científico fica disponível offline após a primeira leitura.
            urlPattern: /\/api\/(library|calculators|drugs)/,
            handler: "StaleWhileRevalidate",
            options: { cacheName: "meucardio-conteudo", expiration: { maxEntries: 500 } }
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
