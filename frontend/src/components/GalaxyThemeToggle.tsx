import { useEffect, useLayoutEffect, useRef } from "react";
import { useAuth } from "../lib/auth";
import { chamamentoComArtigo } from "../lib/clinicalIdentity";
import { useCorviaTheme } from "../lib/corviaTheme";
import "../styles/galaxy-theme-toggle-refinement.css";
import "../styles/corvia-approved-fidelity-20260904.css";

const SPACES_CANONICAL_MOTTO = "O Ambiente muda. O Médico Continua no Centro.";

/**
 * Mantém a redação canônica nas superfícies irmãs do Cardiology Spaces.
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

    syncText(document.querySelector(".spaces-workspace__greeting h1"), question);
    syncText(document.querySelector(".spaces-choice__content h1"), question);
    syncText(document.querySelector(".spaces-motto"), SPACES_CANONICAL_MOTTO);
    syncText(document.querySelector(".spaces-choice > footer"), SPACES_CANONICAL_MOTTO);
  });
}

/**
 * Controle canônico claro/escuro usando diretamente a galáxia real já
 * versionada em /spaces. O vídeo não passa mais por threshold de canvas; a
 * transparência visual vem do blend/mask da folha de fidelidade aprovada.
 */
export default function GalaxyThemeToggle({ className = "" }: { className?: string }) {
  const { theme, toggleTheme } = useCorviaTheme();
  const videoRef = useRef<HTMLVideoElement>(null);
  useCanonicalSpacesIdentityCopy();

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const syncMotionPreference = () => {
      if (reducedMotion.matches) video.pause();
      else void video.play().catch(() => undefined);
    };
    syncMotionPreference();
    reducedMotion.addEventListener?.("change", syncMotionPreference);
    return () => reducedMotion.removeEventListener?.("change", syncMotionPreference);
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
        controls={false}
        disablePictureInPicture
        onContextMenu={(event) => event.preventDefault()}
      />
    </button>
  );
}
