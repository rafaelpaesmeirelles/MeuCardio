import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { findClinicalRoute, type FunctionalSpace, type RouteGroup } from "../lib/clinicalRouteRegistry";
import "../styles/cardiology-spaces-route-deep.css";
import "../styles/cardiology-spaces-consultorio-pages.css";
import "../styles/cardiology-spaces-consultorio-prescricao.css";
import "../styles/cardiology-spaces-consultorio-knowledge.css";
import "../styles/cardiology-spaces-hospital-pages.css";
import "../styles/cardiology-spaces-ensino-pages.css";
import "../styles/cardiology-spaces-pesquisa-pages.css";
import "../styles/cardiology-spaces-gestao-pages.css";

/**
 * Adaptador temporário entre o registro canônico e as classes históricas.
 *
 * As classes e datasets permanecem inalterados enquanto as páginas antigas
 * ainda dependem deles. A identidade de toda rota registrada, entretanto,
 * já vem de uma única fonte e não de listas concorrentes por componente.
 */
export default function ClinicalRouteContext() {
  const { pathname } = useLocation();

  useEffect(() => {
    const previous = Array.from(document.body.classList).filter((item) => item.startsWith("corvia-route--") || item.startsWith("corvia-space--"));
    previous.forEach((item) => document.body.classList.remove(item));

    if (pathname === "/") {
      document.body.dataset.corviaRoute = "home";
      document.body.dataset.corviaSpace = "home";
      return () => {
        if (document.body.dataset.corviaRoute === "home") delete document.body.dataset.corviaRoute;
        if (document.body.dataset.corviaSpace === "home") delete document.body.dataset.corviaSpace;
      };
    }

    const registered = findClinicalRoute(pathname);
    const context: { group: RouteGroup; space: FunctionalSpace } = registered && registered.space !== "home"
      ? { group: registered.group, space: registered.space }
      : { group: "geral", space: "gestao" };
    const routeClass = `corvia-route--${context.group}`;
    const spaceClass = `corvia-space--${context.space}`;
    document.body.classList.add(routeClass, spaceClass);
    document.body.dataset.corviaRoute = context.group;
    document.body.dataset.corviaSpace = context.space;

    return () => {
      document.body.classList.remove(routeClass, spaceClass);
      if (document.body.dataset.corviaRoute === context.group) delete document.body.dataset.corviaRoute;
      if (document.body.dataset.corviaSpace === context.space) delete document.body.dataset.corviaSpace;
    };
  }, [pathname]);

  return null;
}
