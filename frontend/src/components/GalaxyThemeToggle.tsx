import { useEffect, useRef } from "react";
import { useCorviaTheme } from "../lib/corviaTheme";

/**
 * Controle canônico único de alternância claro/escuro — substitui a
 * astrofotografia estática (`corvia-galaxy-cameo.webp`) por um vídeo em
 * loop contínuo (03/09/2026, fechamento do PR #811). Reutiliza
 * `useCorviaTheme()`/`toggleTheme()` já existentes — não existe um segundo
 * mecanismo de tema.
 *
 * `width`/`height`/`aspect-ratio` do vídeo são fixos via CSS
 * (`.galaxy-theme-toggle__video`), então o layout nunca se move quando o
 * vídeo carrega ou começa a tocar (sem CLS).
 */
export default function GalaxyThemeToggle({ className = "" }: { className?: string }) {
  const { theme, toggleTheme } = useCorviaTheme();
  const videoRef = useRef<HTMLVideoElement>(null);

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
