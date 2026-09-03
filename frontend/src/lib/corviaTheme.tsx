import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "./auth";

export type CorviaTheme = "dark" | "light";

type CorviaThemeContextValue = {
  theme: CorviaTheme;
  setTheme: (theme: CorviaTheme) => void;
  toggleTheme: () => void;
};

const DEFAULT_THEME: CorviaTheme = "dark";
const THEME_STORAGE_PREFIX = "corvia:cardiology-spaces:theme:v1";
export const CORVIA_LOGIN_THEME_KEY = "corvia:cardiology-spaces:login-theme";
const THEME_COLORS: Record<CorviaTheme, string> = {
  dark: "#03101a",
  light: "#eef5fb",
};

const CorviaThemeContext = createContext<CorviaThemeContextValue | null>(null);

function isCorviaTheme(value: unknown): value is CorviaTheme {
  return value === "dark" || value === "light";
}

export function corviaThemeStorageKey(userId: number) {
  return `${THEME_STORAGE_PREFIX}:${userId}`;
}

function readStoredTheme(userId?: number): CorviaTheme {
  if (!userId) return DEFAULT_THEME;
  try {
    const stored = localStorage.getItem(corviaThemeStorageKey(userId));
    return isCorviaTheme(stored) ? stored : DEFAULT_THEME;
  } catch {
    return DEFAULT_THEME;
  }
}

function consumeLoginThemePreference(): CorviaTheme | null {
  try {
    const pendingTheme = sessionStorage.getItem(CORVIA_LOGIN_THEME_KEY);
    if (!isCorviaTheme(pendingTheme)) return null;
    sessionStorage.removeItem(CORVIA_LOGIN_THEME_KEY);
    return pendingTheme;
  } catch {
    return null;
  }
}

function applyDocumentTheme(theme: CorviaTheme) {
  const root = document.documentElement;
  root.dataset.corviaTheme = theme;
  root.style.colorScheme = theme;

  const themeColor = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  themeColor?.setAttribute("content", THEME_COLORS[theme]);
}

/**
 * Aparência global do universo autenticado CorVIA.
 *
 * A preferência é deliberadamente independente dos modos de trabalho e fica
 * vinculada ao assinante. Rotas públicas permanecem sempre no tema escuro de
 * origem; isso também impede que a preferência de um usuário vaze no logout.
 */
export function CorviaThemeProvider({ children }: { children: ReactNode }) {
  const { usuario } = useAuth();
  const location = useLocation();
  const userId = usuario?.id;
  const [storedTheme, setStoredTheme] = useState<CorviaTheme>(DEFAULT_THEME);
  const theme = userId ? storedTheme : DEFAULT_THEME;
  const publicValidationRoute = location.pathname === "/validar" || location.pathname.startsWith("/validar/");
  const documentTheme = publicValidationRoute ? DEFAULT_THEME : theme;

  useLayoutEffect(() => {
    if (!userId) {
      setStoredTheme(DEFAULT_THEME);
      return;
    }

    const loginTheme = consumeLoginThemePreference();
    const nextTheme = loginTheme ?? readStoredTheme(userId);
    setStoredTheme(nextTheme);
    if (loginTheme) {
      try {
        localStorage.setItem(corviaThemeStorageKey(userId), loginTheme);
      } catch {
        // A escolha continua válida na aba atual quando o storage está indisponível.
      }
    }
  }, [userId]);

  useLayoutEffect(() => {
    applyDocumentTheme(documentTheme);
  }, [documentTheme]);

  useEffect(() => {
    if (!userId) return;
    const key = corviaThemeStorageKey(userId);
    function syncAcrossTabs(event: StorageEvent) {
      if (event.key !== key) return;
      setStoredTheme(isCorviaTheme(event.newValue) ? event.newValue : DEFAULT_THEME);
    }
    window.addEventListener("storage", syncAcrossTabs);
    return () => window.removeEventListener("storage", syncAcrossTabs);
  }, [userId]);

  const setTheme = useCallback((nextTheme: CorviaTheme) => {
    if (!userId) return;
    setStoredTheme(nextTheme);
    try {
      localStorage.setItem(corviaThemeStorageKey(userId), nextTheme);
    } catch {
      // A escolha continua válida na aba atual quando o storage está indisponível.
    }
  }, [userId]);

  const toggleTheme = useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark");
  }, [setTheme, theme]);

  const value = useMemo(() => ({ theme, setTheme, toggleTheme }), [setTheme, theme, toggleTheme]);
  return <CorviaThemeContext.Provider value={value}>{children}</CorviaThemeContext.Provider>;
}

export function useCorviaTheme() {
  const context = useContext(CorviaThemeContext);
  if (!context) throw new Error("useCorviaTheme precisa estar dentro de CorviaThemeProvider");
  return context;
}
