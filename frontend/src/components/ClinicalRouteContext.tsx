import { useEffect } from "react";
import { useLocation } from "react-router-dom";

/**
 * Classifica intenção/contexto sem autorizar linguagens visuais paralelas.
 * Toda rota autenticada permanece subordinada à prancha canônica do Clinical OS.
 * A Home aprovada é isolada do lock de páginas internas para não sofrer regressão.
 * A ordem importa apenas quando um prefixo é subconjunto de outro.
 */
const ROUTES: Array<[string, string]> = [
  // Trabalho executável
  ["/documentos", "documentos"],
  ["/avaliacao-preoperatoria", "documentos"],
  ["/round", "pacientes"],
  ["/receituario", "prescricao"],
  ["/agenda", "agenda"],
  ["/corvia-mail", "mail"],
  ["/caixa-de-email", "mail"],
  ["/assistente", "assistente"],
  ["/heart-team", "assistente"],
  ["/whatsapp-assistant", "integracoes"],

  // Conhecimento/contexto onde Intelligence agrega relações
  ["/medicamentos", "conhecimento"],
  ["/interacoes", "conhecimento"],
  ["/exames", "conhecimento"],
  ["/evidencias", "conhecimento"],
  ["/estudos", "conhecimento"],
  ["/diretrizes", "conhecimento"],
  ["/biblioteca", "conhecimento"],
  ["/doencas", "conhecimento"],
  ["/casos-clinicos", "conhecimento"],
  ["/trilhas", "conhecimento"],
  ["/cursos", "conhecimento"],
  ["/favoritos", "conhecimento"],

  // Ferramentas de decisão/consulta
  ["/calculadoras", "ferramentas"],
  ["/cardiologia-intensiva", "ferramentas"],
  ["/checklists", "ferramentas"],
  ["/fluxogramas", "ferramentas"],
  ["/triagem-sintomas", "ferramentas"],
  ["/condicoes", "ferramentas"],
  ["/material-paciente", "ferramentas"],
  ["/galeria", "ferramentas"],
  ["/apresentacao", "ferramentas"],
  ["/exportar", "ferramentas"],
  ["/busca", "ferramentas"],

  // Emergência preserva semântica clínica e acento de risco, mas usa o mesmo shell canônico.
  ["/emergencia", "emergencia"],

  // Comunicação/rede e trabalho remoto
  ["/usuarios-online", "rede"],
  ["/telediagnostico", "telediagnostico"],
  ["/fila-telediagnostico", "telediagnostico"],

  // Conta, integrações, segurança e gestão
  ["/sincronizacao", "integracoes"],
  ["/minha-conta", "conta"],
  ["/assinatura", "conta"],
  ["/verificacao-identidade", "conta"],
  ["/indicadores", "conta"],
  ["/admin", "admin"],

  // Políticas institucionais autenticadas também permanecem no canvas canônico.
  ["/privacidade", "geral"],
  ["/termos", "geral"],
];

export default function ClinicalRouteContext() {
  const { pathname } = useLocation();

  useEffect(() => {
    const anteriores = Array.from(document.body.classList).filter((item) => item.startsWith("corvia-route--"));
    anteriores.forEach((item) => document.body.classList.remove(item));

    if (pathname === "/") {
      document.body.dataset.corviaRoute = "home";
      return () => {
        if (document.body.dataset.corviaRoute === "home") delete document.body.dataset.corviaRoute;
      };
    }

    const grupo = ROUTES.find(([prefixo]) => pathname === prefixo || pathname.startsWith(`${prefixo}/`))?.[1] ?? "geral";
    const classe = `corvia-route--${grupo}`;
    document.body.classList.add(classe);
    document.body.dataset.corviaRoute = grupo;
    return () => {
      document.body.classList.remove(classe);
      if (document.body.dataset.corviaRoute === grupo) delete document.body.dataset.corviaRoute;
    };
  }, [pathname]);

  return null;
}
