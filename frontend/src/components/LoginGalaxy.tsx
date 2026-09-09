import { useEffect, useRef } from "react";
import lightSource from "../assets/login/galaxy-light.webp";
import darkSource from "../assets/login/galaxy-dark.webp";
import type { CorviaTheme } from "../lib/corviaTheme";

// Share one download/decode across theme switches and React remounts.
// Vite gives these files content hashes and the server caches /assets immutably.
const decodedImages = new Map<string, Promise<HTMLImageElement>>();

function loadGalaxy(source: string) {
  const cached = decodedImages.get(source);
  if (cached) return cached;
  const image = new Image();
  image.decoding = "async";
  image.fetchPriority = "high";
  image.src = source;
  const decoded = image.decode().then(() => image).catch((error: unknown) => {
    decodedImages.delete(source);
    throw error;
  });
  decodedImages.set(source, decoded);
  return decoded;
}

export default function LoginGalaxy({ theme }: { theme: CorviaTheme }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d", { alpha: true });
    if (!context) return;

    let animationFrame = 0;
    let cancelled = false;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let repaint: (() => void) | undefined;
    const motionChanged = () => repaint?.();
    const visibilityChanged = () => {
      cancelAnimationFrame(animationFrame);
      if (!document.hidden) repaint?.();
    };
    reducedMotion.addEventListener("change", motionChanged);
    document.addEventListener("visibilitychange", visibilityChanged);

    void loadGalaxy(theme === "light" ? lightSource : darkSource).then((image) => {
      if (cancelled) return;
      const width = 683;
      const height = Math.round(width * image.naturalHeight / image.naturalWidth);
      const dark = theme === "dark";
      const square = width * 2;
      // Preserve the approved disk geometry; only its texture turns in the plane.
      const coreXRatio = dark ? 0.519617 : 0.485368;
      const coreYRatio = dark ? 0.497165 : 0.471192;
      const projectedHeight = width * image.naturalHeight / image.naturalWidth;
      const sourceProjectionY = dark ? 0.454819 : 0.321819;
      const sourceInclination = (dark ? -12.242524 : 1.951326) * Math.PI / 180;
      const diskProjectionY = 0.34;
      const coreSquareX = square / 2;
      const coreSquareY = square / 2;

      canvas.width = width;
      canvas.height = height;
      const deprojected = document.createElement("canvas");
      deprojected.width = square;
      deprojected.height = square;
      const sourceContext = deprojected.getContext("2d", { alpha: true });
      if (!sourceContext) return;
      sourceContext.translate(coreSquareX, coreSquareY);
      sourceContext.scale(1, 1 / sourceProjectionY);
      sourceContext.rotate(-sourceInclination);
      sourceContext.drawImage(image, -coreXRatio * width, -coreYRatio * projectedHeight, width, projectedHeight);

      const startedAt = performance.now();
      let lastPaint = 0;
      const durationMs = 120_000;
      const draw = (now: number) => {
        if (cancelled) return;
        if (!lastPaint || now - lastPaint >= 32) {
          const direction = dark ? 1 : -1;
          const angle = reducedMotion.matches ? 0 : direction * ((now - startedAt) % durationMs) / durationMs * Math.PI * 2;
          context.clearRect(0, 0, width, height);
          context.save();
          context.translate(width / 2, height / 2);
          context.scale(0.72, diskProjectionY * 0.72);
          context.rotate(angle);
          context.drawImage(deprojected, -coreSquareX, -coreSquareY);
          context.restore();
          lastPaint = now;
        }
        if (!reducedMotion.matches && !document.hidden) animationFrame = requestAnimationFrame(draw);
      };
      repaint = () => {
        cancelAnimationFrame(animationFrame);
        lastPaint = 0;
        draw(performance.now());
      };
      draw(startedAt);
      // Reveal only the complete, projected frame. No progressive image or
      // raw-photo fallback can flash while downloading; no DOM writes per frame.
      canvas.dataset.ready = "true";
    }).catch(() => {
      // The decorative image must never prevent entering the application.
    });

    return () => {
      cancelled = true;
      reducedMotion.removeEventListener("change", motionChanged);
      document.removeEventListener("visibilitychange", visibilityChanged);
      cancelAnimationFrame(animationFrame);
    };
  }, [theme]);

  return <canvas key={theme} ref={canvasRef} className="login-gateway__galaxy-canvas" aria-hidden="true" />;
}
