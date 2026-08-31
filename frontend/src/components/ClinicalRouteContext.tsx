import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import "../styles/cardiology-spaces-route-deep.css";
import "../styles/cardiology-spaces-consultorio-pages.css";
import "../styles/cardiology-spaces-consultorio-prescricao.css";
import "../styles/cardiology-spaces-consultorio-knowledge.css";
import "../styles/cardiology-spaces-hospital-pages.css";

type RouteGroup = "documentos" | "pacientes" | "prescricao" | "agenda" | "mail" | "assistente" | "integracoes" | "conhecimento" | "ferramentas" | "emergencia" | "rede" | "telediagnostico" | "conta" | "admin" | "geral";
type CardiologySpace = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";
type RouteContext = { prefix: string; group: RouteGroup; space: CardiologySpace };

/**
 * Contrato de contexto de TODAS as rotas autenticadas do Cardiology Spaces.
 *
 * A classe `corvia-route--*` é preservada para compatibilidade com os estilos
 * e comportamentos existentes. A classe `corvia-space--*` passa a ser a fonte
 * canônica de identidade visual: Consultório (ciano), Hospital (azul), Ensino
 * (violeta), Pesquisa (rosa) e Gestão (teal), exatamente como na prancha
 * aprovada. A ordem importa apenas quando um prefixo é subconjunto de outro.
 */
const ROUTES: RouteContext[] = [
  { prefix: "/documentos", group: "documentos", space: "consultorio" },
  { prefix: "/avaliacao-preoperatoria", group: "documentos", space: "consultorio" },
  { prefix: "/receituario", group: "prescricao", space: "consultorio" },
  { prefix: "/agenda", group: "agenda", space: "consultorio" },
  { prefix: "/prontuario", group: "pacientes", space: "consultorio" },
  { prefix: "/doencas", group: "conhecimento", space: "consultorio" },
  { prefix: "/medicamentos", group: "conhecimento", space: "consultorio" },
  { prefix: "/interacoes", group: "conhecimento", space: "consultorio" },
  { prefix: "/exames", group: "conhecimento", space: "consultorio" },
  { prefix: "/calculadoras", group: "ferramentas", space: "consultorio" },
  { prefix: "/triagem-sintomas", group: "ferramentas", space: "consultorio" },
  { prefix: "/condicoes", group: "ferramentas", space: "consultorio" },
  { prefix: "/assistente", group: "assistente", space: "consultorio" },

  { prefix: "/heart-team", group: "assistente", space: "hospital" },
  { prefix: "/round", group: "pacientes", space: "hospital" },
  { prefix: "/cardiologia-intensiva", group: "ferramentas", space: "hospital" },
  { prefix: "/checklists", group: "ferramentas", space: "hospital" },
  { prefix: "/emergencia", group: "emergencia", space: "hospital" },
  { prefix: "/exames-ia", group: "ferramentas", space: "hospital" },
  { prefix: "/ecg-ia", group: "ferramentas", space: "hospital" },

  { prefix: "/casos-clinicos", group: "conhecimento", space: "ensino" },
  { prefix: "/trilhas", group: "conhecimento", space: "ensino" },
  { prefix: "/material-paciente", group: "ferramentas", space: "ensino" },
  { prefix: "/galeria", group: "ferramentas", space: "ensino" },
  { prefix: "/apresentacao", group: "ferramentas", space: "ensino" },

  { prefix: "/documentos-cientificos-ia", group: "conhecimento", space: "pesquisa" },
  { prefix: "/evidencias", group: "conhecimento", space: "pesquisa" },
  { prefix: "/estudos", group: "conhecimento", space: "pesquisa" },
  { prefix: "/diretrizes", group: "conhecimento", space: "pesquisa" },
  { prefix: "/biblioteca", group: "conhecimento", space: "pesquisa" },
  { prefix: "/busca", group: "ferramentas", space: "pesquisa" },
  { prefix: "/fluxogramas", group: "ferramentas", space: "pesquisa" },
  { prefix: "/exportar", group: "ferramentas", space: "pesquisa" },
  { prefix: "/favoritos", group: "conhecimento", space: "pesquisa" },

  { prefix: "/corvia-mail", group: "mail", space: "gestao" },
  { prefix: "/caixa-de-email", group: "mail", space: "gestao" },
  { prefix: "/whatsapp-assistant", group: "integracoes", space: "gestao" },
  { prefix: "/usuarios-online", group: "rede", space: "gestao" },
  { prefix: "/telediagnostico", group: "telediagnostico", space: "gestao" },
  { prefix: "/fila-telediagnostico", group: "telediagnostico", space: "gestao" },
  { prefix: "/sincronizacao", group: "integracoes", space: "gestao" },
  { prefix: "/minha-conta", group: "conta", space: "gestao" },
  { prefix: "/assinatura", group: "conta", space: "gestao" },
  { prefix: "/verificacao-identidade", group: "conta", space: "gestao" },
  { prefix: "/excluir-conta", group: "conta", space: "gestao" },
  { prefix: "/indicadores", group: "conta", space: "gestao" },
  { prefix: "/receitas-para-assinatura", group: "admin", space: "gestao" },
  { prefix: "/admin", group: "admin", space: "gestao" },
  { prefix: "/privacidade", group: "geral", space: "gestao" },
  { prefix: "/termos", group: "geral", space: "gestao" },
];

function matches(pathname: string, prefix: string) {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

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

    const context = ROUTES.find((item) => matches(pathname, item.prefix)) ?? { prefix: pathname, group: "geral" as RouteGroup, space: "gestao" as CardiologySpace };
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
