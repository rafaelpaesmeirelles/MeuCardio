import { defineConfig, type Plugin } from "vite";
import type { OutputChunk } from "rollup";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

const limitePrecacheJs = 100 * 1024;
const foraDoPrecacheInicial = /(?:^|\/)(?:Admin|AdminAssinantes|AdminFichaAssinante|FilaTelediagnostico|VerificacaoIdentidade|PrescricaoLivreEspecial)-[^/]*\.js$/;
const loginSomenteOnline = /(?:^|\/)(?:Entrar-[^/]*|PreHomeBrand-[^/]*|login-[^/]*|SolicitarAcesso-[^/]*|EsqueciSenha-[^/]*|RedefinirSenha-[^/]*)\.(?:js|css)$/;
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
// Agenda, prontuário, prescrição, round, e-mail, sincronização e conta dependem
// de sessão, dados atuais e APIs transacionais. Manter seus chunks no precache
// não cria um modo offline seguro e ainda pode exibir informação desatualizada.
// Eles continuam cobertos pelo cache NetworkFirst depois do primeiro uso.
const operacaoClinicaSomenteOnline = /(?:^|\/)(?:Agenda|Prontuario|Receituario|RoundGerenciavel|CaixaDeEmail|CorviaMail|MinhaConta|ExcluirConta|Sincronizacao)-[^/]*\.(?:js|css)$/;

// Cotações, saldo, chat e análises de IA exigem autorização e execução no backend.
// Pré-carregar essas telas não oferece operação offline; seus chunks mantêm o
// mesmo cache NetworkFirst de assets após o acesso, sem aumentar o download inicial.
const iaECobrancaSomenteOnline = /(?:^|\/)(?:Assinatura|Assistente|HeartTeamVirtual|ScientificDocumentAI|WhatsAppAssistant)-[^/]*\.(?:js|css)$/;

// O leitor de fontes e a rota Intelligence consultam versões/publicações no
// backend e baixam os artefatos autenticados sob demanda. Mantêm NetworkFirst
// para seus chunks; os documentos e APIs permanecem NetworkOnly. O monitor
// compartilhado pela Home continua no precache, preservando o shell visual.
const leituraCientificaSomenteOnline = /(?:^|\/)(?:ScientificReadingAccess|CorviaIntelligence)-[^/]*\.(?:js|css)$/;
// A decisão clínica administrativa requer uma comparação atual e autorização
// do proprietário no servidor; este chunk não oferece operação offline.
const aprovacaoClinicaSomenteOnline = /(?:^|\/)(?:AdminClinicalChanges)-[^/]*\.(?:js|css)$/;

const marcaForaDoPrecache = new Set([
  "atelier/corvia-logo-atelier.png",
  "atelier/corvia-mark-atelier-192.png",
  "atelier/corvia-mark-atelier-512.png",
  "corvia-logo-canonical.svg",
  "corvia-logo-canonical-dark.svg",
  "corvia-logo-spaces.svg",
  "corvia-logo-spaces-dark.svg",
  "corvia-mark-canonical.svg",
]);

// O núcleo Mermaid já excede o limite do precache e é importado sob demanda.
// Seus renderizadores isolados não permitem desenhar offline sem esse núcleo.
// Use o grafo real do Rollup, não nomes/hash de arquivos ou cortes em páginas.
const mermaidSobDemanda = new Set<string>();
const dependenciasPrecache: Plugin = {
  name: "corvia-precache-dependencies",
  apply: "build",
  generateBundle(_options, bundle) {
    mermaidSobDemanda.clear();
    const chunks = Object.values(bundle).filter((item): item is OutputChunk => item.type === "chunk");
    const byFile = new Map(chunks.map((chunk) => [chunk.fileName, chunk]));
    const visit = (roots: string[], dynamic: boolean, protectedFiles = new Set<string>()) => {
      const found = new Set<string>();
      const pending = [...roots];
      while (pending.length) {
        const file = pending.pop()!;
        if (found.has(file) || protectedFiles.has(file)) continue;
        const chunk = byFile.get(file);
        if (!chunk) continue;
        found.add(file);
        pending.push(...chunk.imports, ...(dynamic ? chunk.dynamicImports : []));
      }
      return found;
    };
    // Preserve entrada, Home, AppFrame e todas as dependências estáticas dos
    // demais módulos próprios, inclusive helpers compartilhados com Mermaid.
    const application = chunks.filter((chunk) => chunk.isEntry || chunk.moduleIds.some((id) =>
      /\/src\//.test(id.replaceAll("\\", "/")) && !/\/node_modules\//.test(id.replaceAll("\\", "/"))));
    const protectedFiles = visit(application.map((chunk) => chunk.fileName), false);
    const cores = chunks.filter((chunk) => chunk.isDynamicEntry
      && chunk.moduleIds.some((id) => /\/node_modules\/mermaid\/dist\/mermaid\.core\.mjs$/.test(id.replaceAll("\\", "/")))
      && Buffer.byteLength(chunk.code, "utf8") > limitePrecacheJs);
    for (const file of visit(cores.map((chunk) => chunk.fileName), true, protectedFiles)) {
      mermaidSobDemanda.add(file);
    }
  },
};

export default defineConfig({
  plugins: [
    react(),
    dependenciasPrecache,
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["atelier/corvia-mark-atelier.svg", "atelier/corvia-logo-atelier.svg"],
      // Os PNGs continuam públicos e no manifesto para instalação, sem baixar
      // de novo no precache imagens usadas só por instalação/e-mail/social.
      includeManifestIcons: false,
      manifest: {
        name: "CorVIA — Cardiology Spaces",
        short_name: "CorVIA",
        description: "Ambientes de cardiologia centrados no médico: conhecimento, contexto, decisão e ação conectados.",
        lang: "pt-BR",
        theme_color: "#f7f3e8",
        background_color: "#f7f3e8",
        display: "standalone",
        orientation: "portrait",
        start_url: "/",
        icons: [
          { src: "/atelier/corvia-mark-atelier-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
          { src: "/atelier/corvia-mark-atelier-512.png", sizes: "512x512", type: "image/png", purpose: "any maskable" }
        ]
      },
      workbox: {
        // Clinical API responses are NetworkOnly, including emergency doses.
        // Remove caches created by earlier service workers on activation.
        importScripts: ["/corvia-clinical-cache-cleanup-v1.js"],
        skipWaiting: true,
        clientsClaim: true,
        // Uma navegação digitada diretamente para /api precisa chegar ao
        // backend. Sem esta negação, o fallback SPA pode devolver index.html
        // no lugar de JSON e esconder falhas de sessão em PWA/mobile.
        navigateFallbackDenylist: [/^\/api\//, /^\/media\//],
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        // PNGs de marca e ícones de instalação são consumidos pelo navegador,
        // pelo manifesto ou por clientes de e-mail. Eles não fazem parte do
        // shell offline e duplicá-los no precache acrescenta mais de 1 MiB sem
        // melhorar a experiência depois que o PWA já foi instalado.
        globIgnores: [
          ...marcaForaDoPrecache,
          // Marketing media is fetched only after an explicit play/download.
          // It must never increase the initial PWA install or offline cache.
          "media/**",
          // Substituída pelo WebP canônico, carregado pelo cache de cenas.
          "spaces/galaxy-approved-alpha.png",
          "spaces/galaxy-light-soft-20260909.png",
          "spaces/galaxy-light-color-20260909.png",
          "corvia-logo-canonical.png",
          "corvia-logo.png",
          "corvia-logo-compacta.png",
          "logo-marca.png",
          "logo.png",
          "apple-touch-icon.png",
          "favicon.png",
          "icon-192.png",
          "icon-512.png",
          "icon-maskable.png",
        ],
        manifestTransforms: [
          async (entries) => ({
            manifest: entries.filter((entry) => {
              if (marcaForaDoPrecache.has(entry.url) || mermaidSobDemanda.has(entry.url)) return false;
              if (loginSomenteOnline.test(entry.url)) return false;
              if (validacaoPublicaSomenteOnline.test(entry.url)) return false;
              if (analiseCardiovascularSomenteOnline.test(entry.url)) return false;
              if (buscaTudoComTudoSomenteOnline.test(entry.url)) return false;
              if (conteudoConectadoSomenteOnline.test(entry.url)) return false;
              if (operacaoClinicaSomenteOnline.test(entry.url)) return false;
              if (iaECobrancaSomenteOnline.test(entry.url)) return false;
              if (leituraCientificaSomenteOnline.test(entry.url)) return false;
              if (aprovacaoClinicaSomenteOnline.test(entry.url)) return false;
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
            // As cenas dos cinco ambientes são parte do shell visual, mas ficam
            // fora de /assets porque são servidas a partir de public/. Guarde as
            // variantes otimizadas depois do primeiro acesso para que Home e
            // AppFrame não percam sua identidade quando o PWA ficar offline.
            // StaleWhileRevalidate preserva o fallback e atualiza URLs estáveis
            // quando uma release futura substituir a arte da mesma cena.
            urlPattern: ({ url }) =>
              url.origin === self.location.origin
              && /^\/(?:spaces|atelier)\/[^/]+\.(?:webp|jpg|ttf)$/.test(url.pathname),
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "corvia-space-scenes-v1",
              expiration: { maxEntries: 30, maxAgeSeconds: 60 * 60 * 24 * 60 },
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            urlPattern: ({ request, url }) => request.mode === "navigate" && !url.pathname.startsWith("/api/") && !url.pathname.startsWith("/media/"),
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
