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
        // Sem isto, abrir /emergencia offline devolveria 404 do servidor em vez
        // da aplicação: a rota é do roteador do cliente, não existe no disco.
        navigateFallback: "index.html",
        runtimeCaching: [
          {
            // O pacote do Modo Emergência tem regra própria e vem primeiro: a
            // resposta guardada é servida de imediato e revalidada em segundo
            // plano, de modo que a tela abre mesmo sem rede. A página também
            // guarda o pacote por conta própria (localStorage), porque um
            // service worker pode não estar ativo no primeiro acesso — e a
            // única tela que não pode falhar é justamente esta.
            urlPattern: /\/api\/emergencia/,
            handler: "StaleWhileRevalidate",
            options: {
              // Nome novo de propósito: descarta qualquer cache antigo que já
              // tenha guardado uma resposta de erro, em vez de esperar que ela
              // expire por conta própria.
              cacheName: "corvia-emergencia-v2",
              expiration: { maxEntries: 8 },
              // Sem isto, uma resposta de erro (401/404 — por exemplo, de antes
              // de a rota existir em produção) fica presa em cache e a tela
              // volta a mostrá-la a cada abertura, mesmo com o backend já
              // corrigido: só uma resposta 200 substitui o cache.
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            // Conteúdo científico fica disponível offline após a primeira leitura.
            urlPattern: /\/api\/(library|calculators|drugs|material-paciente)/,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "corvia-conteudo",
              expiration: { maxEntries: 500 },
              cacheableResponse: { statuses: [200] }
            }
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
