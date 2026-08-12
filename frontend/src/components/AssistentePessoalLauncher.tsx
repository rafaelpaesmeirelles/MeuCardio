import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth";
import Icone from "./Icone";

/**
 * Presença transversal do Assistente Pessoal no desktop.
 *
 * Ele não compete com a Home (que já possui o rail completo) nem com a própria
 * página do Assistente. Nos demais módulos, mantém a promessa de que agenda,
 * deslocamento e rotina estão sempre a um gesto de distância, sem transformar
 * a experiência em um chatbot flutuante invasivo.
 */
export default function AssistentePessoalLauncher() {
  const { usuario } = useAuth();
  const { pathname } = useLocation();

  if (!usuario) return null;
  if (pathname === "/" || pathname.startsWith("/assistente") || pathname.startsWith("/emergencia") || pathname.startsWith("/tour")) {
    return null;
  }

  return (
    <Link
      to="/assistente?modo=pessoal"
      className="assistente-pessoal-launcher"
      aria-label="Abrir Assistente Pessoal — agenda, deslocamento e rotina"
    >
      <span className="assistente-pessoal-launcher__icon"><Icone nome="assistente" /></span>
      <span className="assistente-pessoal-launcher__text">
        <strong>Assistente Pessoal</strong>
        <small>Agenda · deslocamento · rotina</small>
      </span>
      <Icone nome="chevron" className="assistente-pessoal-launcher__arrow" />
    </Link>
  );
}
