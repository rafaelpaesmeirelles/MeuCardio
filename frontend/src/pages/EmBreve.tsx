import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

export default function EmBreve() {
  const { usuario } = useAuth();

  // Esta página é somente o destino comercial enquanto novas assinaturas
  // estão pausadas. Convidado, investidor, sócio ou assinante com acesso
  // vigente nunca deve ficar preso aqui.
  if (usuario?.product_access) return <Navigate to="/" replace />;

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: "clamp(1.5rem, 5vw, 4rem)",
        overflow: "hidden",
        position: "relative",
        color: "#f4fbff",
        background: "radial-gradient(circle at 75% 20%, rgba(0,174,239,.16), transparent 34%), radial-gradient(circle at 20% 80%, rgba(235,44,139,.13), transparent 32%), #020b14",
      }}
    >
      <div aria-hidden="true" style={{ position: "absolute", inset: "auto 0 14%", height: 1, background: "linear-gradient(90deg, transparent, #00aeef, #7439f1, #eb2c8b, transparent)" }} />
      <section style={{ width: "min(760px, 100%)", textAlign: "center", position: "relative" }}>
        <img src="/corvia-logo-spaces-dark.svg" alt="CorVIA Cardiology Spaces" style={{ width: "min(310px, 70vw)", marginBottom: "clamp(2rem, 6vw, 4rem)" }} />
        <p style={{ margin: "0 0 1rem", color: "#52dded", fontWeight: 800, letterSpacing: ".22em", textTransform: "uppercase", fontSize: ".78rem" }}>
          Estamos preparando a experiência completa
        </p>
        <h1 style={{ margin: 0, fontSize: "clamp(3rem, 10vw, 7rem)", lineHeight: .92, letterSpacing: "-.055em" }}>
          Em breve<span style={{ color: "#eb2c8b" }}>.</span>
        </h1>
        <p style={{ maxWidth: 610, margin: "1.6rem auto 0", color: "#b7c9d6", fontSize: "clamp(1rem, 2.4vw, 1.25rem)", lineHeight: 1.65 }}>
          O CorVIA Cardiology Spaces está em fase final de preparação. As assinaturas permanecem pausadas e nenhuma cobrança será iniciada neste momento.
        </p>
        <div style={{ display: "flex", justifyContent: "center", gap: ".8rem", flexWrap: "wrap", marginTop: "2rem" }}>
          <Link to="/tour?modo=completo" style={{ padding: ".8rem 1.2rem", borderRadius: 10, color: "#03101a", background: "#52dded", fontWeight: 800, textDecoration: "none" }}>
            Rever o tour
          </Link>
          <a href="mailto:contato@corvia.med.br" style={{ padding: ".8rem 1.2rem", borderRadius: 10, color: "#e8f7ff", border: "1px solid #27536b", textDecoration: "none" }}>
            Falar com o suporte
          </a>
        </div>
        <small style={{ display: "block", marginTop: "2.5rem", color: "#69869a", letterSpacing: ".08em" }}>
          Clareza para decidir. Confiança para agir.
        </small>
      </section>
    </main>
  );
}
