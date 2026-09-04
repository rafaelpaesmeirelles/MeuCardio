import { useEffect, useLayoutEffect, useRef } from "react";
import { useAuth } from "../lib/auth";
import { chamamentoComArtigo } from "../lib/clinicalIdentity";
import { useCorviaTheme } from "../lib/corviaTheme";
import "../styles/galaxy-theme-toggle-refinement.css";

const SPACES_CANONICAL_MOTTO = "O Ambiente muda. O Médico Continua no Centro.";

/**
 * Mantém uma única redação de identidade nas superfícies irmãs do
 * Cardiology Spaces. O GalaxyThemeToggle está presente tanto na tela de
 * escolha quanto em Completo/Essencial/Ciência & Ensino; por isso esta
 * sincronização fica no mesmo ponto compartilhado e não precisa ser
 * duplicada por ambiente, tema ou breakpoint.
 */
function useCanonicalSpacesIdentityCopy() {
  const { usuario } = useAuth();
  const chamamento = chamamentoComArtigo(usuario, { curto: true, fallback: "o Médico" });
  const question = `Onde ${chamamento} vai trabalhar agora?`;

  useLayoutEffect(() => {
    const syncText = (element: Element | null, text: string) => {
      if (!(element instanceof HTMLElement) || element.textContent === text) return;
      element.textContent = text;
      element.dataset.canonicalSpacesCopy = "true";
    };

    // Os dois ramos são mutuamente exclusivos, mas usar seletores explícitos
    // garante o mesmo contrato quando o usuário alterna a experiência.
    syncText(document.querySelector(".spaces-workspace__greeting h1"), question);
    syncText(document.querySelector(".spaces-choice__content h1"), question);
    syncText(document.querySelector(".spaces-motto"), SPACES_CANONICAL_MOTTO);
    syncText(document.querySelector(".spaces-choice > footer"), SPACES_CANONICAL_MOTTO);
  });
}

/**
 * Controle canônico único de alternância claro/escuro — substitui a
 * astrofotografia estática (`corvia-galaxy-cameo.webp`) por um vídeo em
 * loop contínuo. Reutiliza `useCorviaTheme()`/`toggleTheme()` já existentes
 * — não existe um segundo mecanismo de tema.
 *
 * `width`/`height`/`aspect-ratio` do vídeo são fixos via CSS
 * (`.galaxy-theme-toggle__video`), então o layout nunca se move quando o
 * vídeo carrega ou começa a tocar (sem CLS).
 */
export default function GalaxyThemeToggle({ className = "" }: { className?: string }) {
  const { theme, toggleTheme } = useCorviaTheme();
  const videoRef = useRef<HTMLVideoElement>(null);
  useCanonicalSpacesIdentityCopy();

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    // `prefers-reduced-motion`: o controle continua funcional (clique
    // alterna o tema normalmente), só o movimento para — mostra o poster
    // estático parado em vez do loop.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      video.pause();
    }
  }, []);

  return (
    <button
      type="button"
      className={`galaxy-theme-toggle${className ? ` ${className}` : ""}`}
      onClick={toggleTheme}
      aria-label={`Ativar modo ${theme === "light" ? "escuro" : "claro"}`}
      title={`Ativar modo ${theme === "light" ? "escuro" : "claro"}`}
    >
      <video
        ref={videoRef}
        className="galaxy-theme-toggle__video"
        src="/spaces/galaxy-loop-v2.mp4"
        poster="/spaces/galaxy-loop-poster.webp"
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        aria-hidden="true"
        tabIndex={-1}
        // decorativo: nunca deve roubar o clique do botão nem oferecer
        // controles/interação própria.
        controls={false}
        onContextMenu={(event) => event.preventDefault()}
      />
    </button>
  );
}
