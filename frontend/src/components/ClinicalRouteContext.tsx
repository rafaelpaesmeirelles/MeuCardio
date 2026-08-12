import { useEffect } from "react";
import { useLocation } from "react-router-dom";

/**
 * Classifica intenção/contexto visual, não estrutura de banco de dados.
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

  // Ferramentas de decisão/consulta: workspace amplo, sem rail decorativo
  ["/calculadoras", "ferramentas"],
  ["/checklists", "ferramentas"],
  ["/fluxogramas", "ferramentas"],
  ["/triagem-sintomas", "ferramentas"],
  ["/condicoes", "ferramentas"],
  ["/material-paciente", "ferramentas"],
  ["/galeria", "ferramentas"],
  ["/apresentacao", "ferramentas"],
  ["/busca", "ferramentas"],

  // Emergência tem identidade e shell próprios; não herda regras genéricas.
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

  // Políticas institucionais autenticadas não precisam de Intelligence.
  ["/privacidade", "geral"],
  ["/termos", "geral"],
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
