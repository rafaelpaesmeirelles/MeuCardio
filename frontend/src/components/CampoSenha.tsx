import { useState, forwardRef, type InputHTMLAttributes } from "react";
import Icone from "./Icone";

/**
 * Campo de senha com botão de mostrar/ocultar embutido. Pedido do Rafael em
 * 08/08/2026: todo campo de digitação de senha do site precisa desse botão —
 * este componente é o padrão único a reaproveitar, em vez de repetir a lógica
 * em cada tela (era o que já acontecia em Entrar.tsx, com sua própria cópia
 * do padrão "position: relative + botão absoluto").
 *
 * Uso: substitui um `<input type="password" ...>` direto. Todas as props de
 * input são repassadas normalmente (`value`, `onChange`, `autoComplete`,
 * `required`, `aria-*` etc.) — só o `type` é controlado internamente.
 */
const CampoSenha = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function CampoSenha({ className, ...props }, ref) {
    const [visivel, setVisivel] = useState(false);
    return (
      <div className={`campo-senha${className ? ` ${className}` : ""}`}>
        <input {...props} ref={ref} type={visivel ? "text" : "password"} />
        <button
          type="button"
          className="campo-senha__alternar"
          onClick={() => setVisivel((v) => !v)}
          aria-label={visivel ? "Ocultar senha" : "Mostrar senha"}
          aria-pressed={visivel}
          tabIndex={-1}
        >
          <Icone nome={visivel ? "olho-fechado" : "olho"} width={18} height={18} />
        </button>
      </div>
    );
  }
);

export default CampoSenha;
