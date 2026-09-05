import { useLayoutEffect } from "react";
import { useAuth } from "../lib/auth";
import { chamamentoComArtigo } from "../lib/clinicalIdentity";
import { useCorviaTheme } from "../lib/corviaTheme";
import MiniUniverseCanvas from "./MiniUniverseCanvas";
import "../styles/galaxy-theme-toggle-refinement.css";
import "../styles/corvia-approved-fidelity-20260904.css";
import "../styles/corvia-approved-fidelity-asset-fix-20260904.css";

const SPACES_CANONICAL_MOTTO = "O Ambiente muda. O Médico Continua no Centro.";

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

export default function GalaxyThemeToggle({ className = "" }: { className?: string }) {
  const { theme, toggleTheme } = useCorviaTheme();
  useCanonicalSpacesIdentityCopy();

  return (
    <button
      type="button"
      className={`galaxy-theme-toggle${className ? ` ${className}` : ""}`}
      onClick={toggleTheme}
      aria-label={`Ativar modo ${theme === "light" ? "escuro" : "claro"}`}
      title={`Ativar modo ${theme === "light" ? "escuro" : "claro"}`}
    >
      <img
        className="galaxy-theme-toggle__image"
        src="/spaces/galaxy-approved-canonical.webp"
        alt=""
        aria-hidden="true"
        draggable={false}
      />
      <MiniUniverseCanvas />
    </button>
  );
}
