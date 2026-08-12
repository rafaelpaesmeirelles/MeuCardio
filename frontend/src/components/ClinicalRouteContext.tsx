import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const ROUTES: Array<[string, string]> = [
  ["/documentos", "documentos"],
  ["/avaliacao-preoperatoria", "documentos"],
  ["/round", "pacientes"],
  ["/receituario", "prescricao"],
  ["/agenda", "agenda"],
  ["/corvia-mail", "mail"],
  ["/caixa-de-email", "mail"],
  ["/assistente", "assistente"],
  ["/sincronizacao", "integracoes"],
  ["/minha-conta", "conta"],
  ["/assinatura", "conta"],
  ["/admin", "admin"],
  ["/usuarios-online", "rede"],
  ["/telediagnostico", "telediagnostico"],
  ["/fila-telediagnostico", "telediagnostico"],
  ["/biblioteca", "conhecimento"],
  ["/doencas", "conhecimento"],
  ["/casos-clinicos", "conhecimento"],
  ["/trilhas", "conhecimento"],
  ["/checklists", "ferramentas"],
  ["/fluxogramas", "ferramentas"],
  ["/triagem-sintomas", "ferramentas"],
  ["/material-paciente", "ferramentas"],
  ["/galeria", "ferramentas"],
];

export default function ClinicalRouteContext() {
  const { pathname } = useLocation();

  useEffect(() => {
    const grupo = ROUTES.find(([prefixo]) => pathname === prefixo || pathname.startsWith(`${prefixo}/`))?.[1] ?? "geral";
    const classe = `corvia-route--${grupo}`;
    const anteriores = Array.from(document.body.classList).filter((item) => item.startsWith("corvia-route--"));
    anteriores.forEach((item) => document.body.classList.remove(item));
    document.body.classList.add(classe);
    document.body.dataset.corviaRoute = grupo;
    return () => {
      document.body.classList.remove(classe);
      if (document.body.dataset.corviaRoute === grupo) delete document.body.dataset.corviaRoute;
    };
  }, [pathname]);

  return null;
}
