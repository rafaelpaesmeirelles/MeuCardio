import { useEffect, useRef } from "react";

export default function MiniUniverseCanvas({ direction = "counterclockwise" }: { direction?: "clockwise" | "counterclockwise" }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    const image = new Image();
    let frame = 0;
    let cancelled = false;
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
      const durationMs = 120_000;

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
        if (now - lastPaint >= 32) {
          lastPaint = now;
          const rotationSign = direction === "clockwise" ? 1 : -1;
          const angle = rotationSign * (((now - startedAt) % durationMs) / durationMs) * Math.PI * 2;
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
        frame = requestAnimationFrame(paint);
      };
      frame = requestAnimationFrame(paint);
    };

    return () => {
      cancelled = true;
      canvas.parentElement?.removeAttribute("data-galaxy-ready");
      cancelAnimationFrame(frame);
    };
  }, [direction]);

  return <canvas ref={canvasRef} className="galaxy-theme-toggle__canvas-live" data-rotation-direction={direction} aria-hidden="true" />;
}
