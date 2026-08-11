import { useEffect, useState, type ReactNode } from "react";
import Icone from "./Icone";
import "../styles/dica-contextual.css";

/**
 * Terceiro nível do onboarding da issue #52 — a dica contextual.
 *
 * O primeiro nível é o Quick Start (`pages/Tour.tsx`, cinco telas no
 * primeiro acesso) e o segundo é o tour completo (opcional, mesmo
 * componente). Este é o que evita que o onboarding precise explicar tudo de
 * uma vez: na PRIMEIRA vez que o médico abre uma área, uma frase curta
 * explica o que aquela tela resolve; ele fecha e ela não volta.
 *
 * Regras de convivência com o resto do produto:
 *
 * - **Some por inteiro depois de fechada** — nunca vira banner permanente.
 * - **Nunca bloqueia a tela**: é um bloco no fluxo da página, não um modal.
 *   O médico consegue usar a área inteira ignorando a dica.
 * - **Preferência local, não estado de conta**: a marca de "já vi" vive no
 *   `localStorage` sob `corvia.dica.<id>` — mesma prateleira já usada para
 *   preferências de interface (largura de painel, conta ativa do Mail).
 *   Não é credencial nem sessão; `scripts/check-auth-storage.mjs` proíbe
 *   token no `localStorage`, e isto não é token.
 * - **Falha em silêncio**: navegador em modo privado ou com storage
 *   bloqueado apenas faz a dica aparecer de novo — nunca quebra a página.
 */

const PREFIXO = "corvia.dica.";

function jaFechada(id: string): boolean {
  try {
    return window.localStorage.getItem(PREFIXO + id) === "1";
  } catch {
    return false;
  }
}

function marcarFechada(id: string): void {
  try {
    window.localStorage.setItem(PREFIXO + id, "1");
  } catch {
    /* storage indisponível — a dica só reaparece, nada quebra. */
  }
}

export default function DicaContextual({
  id,
  titulo,
  children,
}: {
  /** Identificador estável da área. Trocar o valor faz a dica reaparecer. */
  id: string;
  titulo: string;
  children: ReactNode;
}) {
  const [visivel, setVisivel] = useState(false);

  // Decide no efeito, não na renderização inicial: leitura de storage no
  // corpo do componente quebraria uma eventual renderização no servidor e
  // dispara aviso de hidratação.
  useEffect(() => {
    setVisivel(!jaFechada(id));
  }, [id]);

  if (!visivel) return null;

  function fechar() {
    marcarFechada(id);
    setVisivel(false);
  }

  return (
    <aside className="dica-ctx" aria-label={`Dica: ${titulo}`}>
      <span className="dica-ctx__icone" aria-hidden="true">
        <Icone nome="rota" width={17} height={17} />
      </span>
      <div className="dica-ctx__texto">
        <p className="dica-ctx__titulo">{titulo}</p>
        <p className="dica-ctx__corpo">{children}</p>
      </div>
      <button type="button" className="dica-ctx__fechar" onClick={fechar} aria-label="Dispensar esta dica">
        <Icone nome="fechar" width={15} height={15} aria-hidden="true" />
      </button>
    </aside>
  );
}
