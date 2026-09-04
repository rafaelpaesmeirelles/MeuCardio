import { useEffect, useLayoutEffect, useRef } from "react";
import { useAuth } from "../lib/auth";
import { chamamentoComArtigo } from "../lib/clinicalIdentity";
import { useCorviaTheme } from "../lib/corviaTheme";
import "../styles/galaxy-theme-toggle-refinement.css";
import "../styles/cardiology-spaces-universe-final.css";

const SPACES_CANONICAL_MOTTO = "O Ambiente muda. O Médico Continua no Centro.";
const GALAXY_RENDER_WIDTH = 342;
const GALAXY_RENDER_HEIGHT = 180;

type VideoFrameCapable = HTMLVideoElement & {
  requestVideoFrameCallback?: (callback: () => void) => number;
  cancelVideoFrameCallback?: (handle: number) => void;
};

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

    syncText(document.querySelector(".spaces-workspace__greeting h1"), question);
    syncText(document.querySelector(".spaces-choice__content h1"), question);
    syncText(document.querySelector(".spaces-motto"), SPACES_CANONICAL_MOTTO);
    syncText(document.querySelector(".spaces-choice > footer"), SPACES_CANONICAL_MOTTO);
  });
}

/**
 * Controle canônico de alternância claro/escuro.
 *
 * O asset aprovado continua sendo o mesmo MP4 em loop. Para o tema claro o
 * fundo preto do H.264 não pode ser tratado com um retângulo colorido: o vídeo
 * é renderizado em canvas em baixa resolução e os pixels quase pretos recebem
 * alpha progressivo. Assim sobra somente o miniuniverso, com transparência
 * real, preservando o mesmo desenho nos dois temas sem alterar a página.
 */
export default function GalaxyThemeToggle({ className = "" }: { className?: string }) {
  const { theme, toggleTheme } = useCorviaTheme();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useCanonicalSpacesIdentityCopy();

  useEffect(() => {
    const video = videoRef.current as VideoFrameCapable | null;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = GALAXY_RENDER_WIDTH;
    canvas.height = GALAXY_RENDER_HEIGHT;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) return;

    let disposed = false;
    let videoFrameHandle: number | null = null;
    let animationFrameHandle: number | null = null;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const drawFrame = () => {
      if (disposed || video.readyState < 2) return;
      context.clearRect(0, 0, GALAXY_RENDER_WIDTH, GALAXY_RENDER_HEIGHT);
      context.drawImage(video, 0, 0, GALAXY_RENDER_WIDTH, GALAXY_RENDER_HEIGHT);

      const frame = context.getImageData(0, 0, GALAXY_RENDER_WIDTH, GALAXY_RENDER_HEIGHT);
      const pixels = frame.data;
      for (let index = 0; index < pixels.length; index += 4) {
        const red = pixels[index];
        const green = pixels[index + 1];
        const blue = pixels[index + 2];
        const maximum = Math.max(red, green, blue);
        const minimum = Math.min(red, green, blue);
        const chroma = maximum - minimum;
        const luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue;

        // Preto puro/compressão do fundo desaparece; azuis escuros saturados
        // da própria galáxia são preservados. A faixa intermediária é
        // suavizada para evitar qualquer halo ou recorte duro.
        if (maximum <= 12) {
          pixels[index + 3] = 0;
        } else if (luminance < 38 && chroma < 22) {
          const feather = Math.max(0, Math.min(1, (luminance - 10) / 28));
          pixels[index + 3] = Math.round(255 * feather);
        } else if (luminance < 24) {
          const feather = Math.max(0, Math.min(1, (luminance - 8) / 16));
          pixels[index + 3] = Math.round(255 * feather);
        } else {
          pixels[index + 3] = 255;
        }
      }
      context.putImageData(frame, 0, 0);
    };

    const scheduleNext = () => {
      if (disposed || reducedMotion) return;
      if (video.requestVideoFrameCallback) {
        videoFrameHandle = video.requestVideoFrameCallback(() => {
          drawFrame();
          scheduleNext();
        });
      } else {
        animationFrameHandle = window.requestAnimationFrame(() => {
          drawFrame();
          scheduleNext();
        });
      }
    };

    const onLoadedData = () => {
      drawFrame();
      if (reducedMotion) {
        video.pause();
      } else {
        void video.play().catch(() => undefined);
        scheduleNext();
      }
    };

    if (video.readyState >= 2) onLoadedData();
    else video.addEventListener("loadeddata", onLoadedData, { once: true });

    return () => {
      disposed = true;
      video.removeEventListener("loadeddata", onLoadedData);
      if (videoFrameHandle !== null && video.cancelVideoFrameCallback) {
        video.cancelVideoFrameCallback(videoFrameHandle);
      }
      if (animationFrameHandle !== null) window.cancelAnimationFrame(animationFrameHandle);
    };
  }, []);

  return (
    <button
      type="button"
      className={`galaxy-theme-toggle${className ? ` ${className}` : ""}`}
      onClick={toggleTheme}
      aria-label={`Ativar modo ${theme === "light" ? "escuro" : "claro"}`}
      title={`Ativar modo ${theme === "light" ? "escuro" : "claro"}`}
    >
      <canvas ref={canvasRef} className="galaxy-theme-toggle__canvas" aria-hidden="true" />
      <video
        ref={videoRef}
        className="galaxy-theme-toggle__video"
        src="/spaces/galaxy-loop-v2.mp4"
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        aria-hidden="true"
        tabIndex={-1}
        controls={false}
        onContextMenu={(event) => event.preventDefault()}
      />
    </button>
  );
}
