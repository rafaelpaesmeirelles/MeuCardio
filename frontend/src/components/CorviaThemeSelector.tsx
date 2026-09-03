import { useId, type KeyboardEvent } from "react";
import { useCorviaTheme, type CorviaTheme } from "../lib/corviaTheme";
import Icone, { type NomeIcone } from "./Icone";

type ThemeOption = {
  theme: CorviaTheme;
  label: string;
  description: string;
  icon: NomeIcone;
};

const THEME_OPTIONS: ThemeOption[] = [
  { theme: "dark", label: "Modo escuro", description: "Imersão cósmica", icon: "lua" },
  { theme: "light", label: "Modo claro", description: "Observatório orbital", icon: "sol" },
];

export default function CorviaThemeSelector({ variant = "choice" }: { variant?: "choice" | "menu" }) {
  const { theme, setTheme } = useCorviaTheme();
  const uid = useId();
  const titleId = `corvia-theme-title-${uid}`;
  const descriptionId = `corvia-theme-description-${uid}`;

  function selectFromKeyboard(event: KeyboardEvent<HTMLButtonElement>, currentTheme: CorviaTheme) {
    const previous = event.key === "ArrowLeft" || event.key === "ArrowUp";
    const next = event.key === "ArrowRight" || event.key === "ArrowDown";
    if (!previous && !next && event.key !== "Home" && event.key !== "End") return;
    event.preventDefault();
    const currentIndex = THEME_OPTIONS.findIndex((option) => option.theme === currentTheme);
    const selected = event.key === "Home"
      ? THEME_OPTIONS[0].theme
      : event.key === "End"
        ? THEME_OPTIONS[THEME_OPTIONS.length - 1].theme
        : THEME_OPTIONS[(currentIndex + (previous ? -1 : 1) + THEME_OPTIONS.length) % THEME_OPTIONS.length].theme;
    setTheme(selected);
    requestAnimationFrame(() => document.getElementById(`corvia-theme-${uid}-${selected}`)?.focus());
  }

  return (
    <section className={`corvia-theme-selector corvia-theme-selector--${variant}`} aria-labelledby={titleId}>
      <div className="corvia-theme-selector__intro">
        <span className="corvia-theme-selector__orbit" aria-hidden="true"><i /><b /></span>
        <span>
          <strong id={titleId}>APARÊNCIA DO UNIVERSO</strong>
          <small id={descriptionId}>A mesma identidade CorVIA, sob outra luz.</small>
        </span>
      </div>
      <div
        className="corvia-theme-selector__options"
        role="radiogroup"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
      >
        {THEME_OPTIONS.map((option) => {
          const selected = theme === option.theme;
          return (
            <button
              key={option.theme}
              id={`corvia-theme-${uid}-${option.theme}`}
              type="button"
              className={selected ? "is-selected" : undefined}
              role="radio"
              aria-checked={selected}
              tabIndex={selected ? 0 : -1}
              onClick={() => setTheme(option.theme)}
              onKeyDown={(event) => selectFromKeyboard(event, option.theme)}
            >
              <span className="corvia-theme-selector__icon" aria-hidden="true"><Icone nome={option.icon} /></span>
              <span><strong>{option.label}</strong><small>{option.description}</small></span>
              <i aria-hidden="true" />
            </button>
          );
        })}
      </div>
      <span className="corvia-theme-selector__status" role="status" aria-live="polite">
        {theme === "light" ? "Modo claro ativado" : "Modo escuro ativado"}
      </span>
    </section>
  );
}
