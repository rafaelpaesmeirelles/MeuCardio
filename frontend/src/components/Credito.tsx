export default function Credito({ compacto = false }: { compacto?: boolean }) {
  return (
    <p
      style={{
        fontSize: compacto ? "0.7rem" : "0.76rem",
        color: "var(--texto-secundario)",
        textAlign: "center",
        margin: compacto ? "0.6rem 0 0" : "1.4rem 0 0",
        lineHeight: 1.5,
      }}
    >
      Dr. Rafael Paes Meirelles — CRM-SP 138266 · RQE 134798 em Cardiologia
      <br />
      Idealizador, desenvolvedor, revisor e responsável técnico
    </p>
  );
}
