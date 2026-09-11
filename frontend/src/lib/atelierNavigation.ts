import { catalogRoutesFor, CLINICAL_ROUTES, findClinicalRoute, routeAvailable, type ClinicalRouteDefinition, type FunctionalSpace } from "./clinicalRouteRegistry";

export type AtelierMode = "complete" | "essential" | "scientific";
export type AtelierContext = { space: FunctionalSpace; mode: AtelierMode };
type ContextStorage = Pick<Storage, "getItem" | "setItem">;

const SPACES = new Set(["consultorio", "hospital", "ensino", "pesquisa", "gestao"]);
const MODES = new Set(["complete", "essential", "scientific"]);
const CONTEXT_PREFIX = "corvia:atelier:context:v1";

function isContext(value: unknown): value is AtelierContext {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<AtelierContext>;
  return SPACES.has(candidate.space || "") && MODES.has(candidate.mode || "");
}

/** One module instance survives Home/Task unmounts. Storage is convenience,
 * never the only source of navigation state, and every entry is user-scoped. */
export function createAtelierContextStore(storage: () => ContextStorage | null = () => typeof window === "undefined" ? null : window.sessionStorage) {
  const memory = new Map<number, AtelierContext>();
  return {
    read(userId?: number, fallbackSpace: FunctionalSpace = "consultorio"): AtelierContext {
      const fallback: AtelierContext = { space: fallbackSpace, mode: "complete" };
      if (!userId) return fallback;
      const current = memory.get(userId);
      if (current) return { ...current };
      try {
        const saved = storage();
        if (!saved) return fallback;
        const raw: unknown = JSON.parse(saved.getItem(`${CONTEXT_PREFIX}:${userId}`) || "null");
        if (isContext(raw)) {
          memory.set(userId, { ...raw });
          return { ...raw };
        }
        // Read the previous keys once so existing users keep their context.
        const space = saved.getItem(`corvia:atelier:space:${userId}`);
        const mode = saved.getItem("corvia:cardiology-spaces:mode");
        const legacy: AtelierContext = {
          space: SPACES.has(space || "") ? space as FunctionalSpace : fallbackSpace,
          mode: MODES.has(mode || "") ? mode as AtelierMode : "complete",
        };
        if (space || mode) memory.set(userId, legacy);
        return { ...legacy };
      } catch { return fallback; }
    },
    write(userId: number | undefined, context: AtelierContext): boolean {
      if (!userId || !isContext(context)) return false;
      memory.set(userId, { ...context });
      try {
        const saved = storage();
        if (!saved) return false;
        saved.setItem(`${CONTEXT_PREFIX}:${userId}`, JSON.stringify(context));
        return true;
      } catch { return false; }
    },
  };
}

const sharedContext = createAtelierContextStore();
export const readAtelierContext = sharedContext.read;
export const writeAtelierContext = sharedContext.write;

export function atelierContextFromSearch(params: URLSearchParams, fallback: AtelierContext): AtelierContext {
  const space = params.get("espaco");
  const mode = params.get("modo");
  return {
    space: SPACES.has(space || "") ? space as FunctionalSpace : fallback.space,
    mode: MODES.has(mode || "") ? mode as AtelierMode : fallback.mode,
  };
}

export function atelierHomeHref(context: AtelierContext): string {
  return `/?espaco=${context.space}&modo=${context.mode}`;
}

/** Treat browser history as untrusted input. Retomar preserves a real page's
 * query/hash (including its selected patient), but never grants route access. */
export function atelierRecentContext(value: unknown, isAdmin: boolean, origin: string): { path: string; title: string } | null {
  if (!value || typeof value !== "object") return null;
  const candidate = value as { path?: unknown; title?: unknown };
  if (typeof candidate.path !== "string" || typeof candidate.title !== "string"
    || !candidate.path.startsWith("/") || candidate.path.startsWith("//") || candidate.path.startsWith("/\\")) return null;
  try {
    const base = new URL(origin);
    const target = new URL(candidate.path, base);
    if (!/^https?:$/.test(base.protocol) || target.origin !== base.origin) return null;
    const route = findClinicalRoute(target.pathname);
    if (!route || route.space === "home" || !routeAvailable(route, isAdmin)) return null;
    return { path: `${target.pathname}${target.search}${target.hash}`, title: candidate.title };
  } catch { return null; }
}

// These existing entry points are not primary catalog routes in the registry.
// Keep discovery separate from permission checks; never expose aliases/details.
const EXTRA_CATALOG_PATHS = new Set(["/caixa-de-email", "/tour", "/verificacao-identidade"]);
export function atelierCatalogRoutesFor(space: FunctionalSpace, isAdmin: boolean): ClinicalRouteDefinition[] {
  const primary = catalogRoutesFor(space, isAdmin);
  const extras = CLINICAL_ROUTES.filter((route) => EXTRA_CATALOG_PATHS.has(route.path)
    && (route.space === space || (route.path === "/tour" && space === "gestao"))
    && !primary.some((candidate) => candidate.path === route.path)
    && routeAvailable(route, isAdmin));
  return [...primary, ...extras];
}
