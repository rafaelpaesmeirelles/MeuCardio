import { useEffect, useRef } from "react";

export default function MiniUniverseCanvas({ clockwise = true }: { clockwise?: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    const image = new Image();
    let frame = 0;
    let cancelled = false;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let repaint: (() => void) | undefined;
    const motionChanged = () => repaint?.();
    reducedMotion.addEventListener("change", motionChanged);
    image.src = "/spaces/corvia-galaxy-cameo.webp";

    image.onload = () => {
      if (cancelled) return;
      const width = 620;
      const height = 350;
      const sourceWidth = image.naturalWidth || 768;
      const sourceHeight = image.naturalHeight || 256;
      const square = sourceWidth;
      const coreXRatio = 386.62 / 768;
      const coreYRatio = 119.25 / 256;
      const projectedHeight = width * sourceHeight / sourceWidth;
      const top = (height - projectedHeight) / 2;
      const scaleX = width / square;
      const scaleY = projectedHeight / square;
      const coreSquareX = coreXRatio * square;
      const coreSquareY = coreYRatio * square;
      const coreTargetX = coreXRatio * width;
      const coreTargetY = top + coreYRatio * projectedHeight;
      const durationMs = 240_000;

      canvas.width = width;
      canvas.height = height;
      const sourceCanvas = document.createElement("canvas");
      sourceCanvas.width = square;
      sourceCanvas.height = square;
      const sourceContext = sourceCanvas.getContext("2d");
      if (!sourceContext) return;
      sourceContext.clearRect(0, 0, square, square);
      sourceContext.drawImage(image, 0, 0, square, square);

      const startedAt = performance.now();
      let lastPaint = 0;
      const paint = (now: number) => {
        if (cancelled) return;
        if (!lastPaint || now - lastPaint >= 32) {
          lastPaint = now;
          const rotationDirection = clockwise ? 1 : -1;
          const angle = reducedMotion.matches ? 0 : rotationDirection * (((now - startedAt) % durationMs) / durationMs) * Math.PI * 2;
          ctx.clearRect(0, 0, width, height);
          ctx.save();
          ctx.translate(coreTargetX, coreTargetY);
          ctx.scale(scaleX, scaleY);
          ctx.rotate(angle);
          ctx.translate(-coreSquareX, -coreSquareY);
          ctx.drawImage(sourceCanvas, 0, 0);
          ctx.restore();
          canvas.dataset.ready = "true";
          canvas.parentElement?.setAttribute("data-galaxy-ready", "true");
        }
        if (!reducedMotion.matches) frame = requestAnimationFrame(paint);
      };
      repaint = () => {
        cancelAnimationFrame(frame);
        lastPaint = 0;
        paint(performance.now());
      };
      paint(startedAt);
    };

    return () => {
      cancelled = true;
      reducedMotion.removeEventListener("change", motionChanged);
      canvas.parentElement?.removeAttribute("data-galaxy-ready");
      cancelAnimationFrame(frame);
    };
  }, [clockwise]);

  return <canvas ref={canvasRef} className="galaxy-theme-toggle__canvas-live" aria-hidden="true" />;
}
