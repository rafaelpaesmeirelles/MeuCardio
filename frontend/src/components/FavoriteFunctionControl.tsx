import { useLocation } from "react-router-dom";
import { findClinicalRoute, type ClinicalRouteDefinition } from "../lib/clinicalRouteRegistry";
import BotaoFavorito from "./BotaoFavorito";

export function favoriteFunctionSlug(route?: ClinicalRouteDefinition): string | null {
  if (!route?.catalog || route.kind !== "page" || route.group === "admin" || route.gate?.startsWith("admin") || route.gate === "no-product-access" || /[:*]/.test(route.path) || route.path === "/" || route.path === "/favoritos") return null;
  return route.path.replace(/^\/+|\/+$/g, "").replaceAll("/", "-");
}

export default function FavoriteFunctionControl() {
  const { pathname } = useLocation();
  const route = findClinicalRoute(pathname);
  const slug = favoriteFunctionSlug(route);
  if (!slug || !route) return null;
  return <div className="function-favorite-context" style={{ display: "flex", justifyContent: "flex-end", padding: "8px 12px", minWidth: 0 }}>
    <BotaoFavorito key={slug} itemType="funcao" itemSlug={slug} label={`função ${route.name}`} />
  </div>;
}
