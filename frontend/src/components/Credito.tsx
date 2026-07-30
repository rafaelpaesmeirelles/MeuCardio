export default function Credito({ compacto = false }: { compacto?: boolean }) {
  return (
    <p
      style={{
        fontSize: compacto ? "0.7rem" : "0.76rem",
        color: "var(--texto-secundario)",
        textAlign: "center",
        margin: compacto ? "0.6rem 0 0" : "1.4rem 0 0",
        lineHeight: 1.6,
      }}
    >
      Corvia — O Caminho do Coração
      <br />
      Todos os Direitos Reservados
      <br />
      <br />
      Dr. Rafael Paes Meirelles — CRM-SP 138266 · RQE 134798 em Cardiologia
      <br />
      Idealizador, Desenvolvedor e Revisor
      <br />
      Fale Conosco:{" "}
      <a href="mailto:contato@corvia.med.br" style={{ color: "inherit" }}>
        contato@corvia.med.br
      </a>
    </p>
  );
}
