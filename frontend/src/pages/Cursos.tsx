export default function Cursos() {
  return (
    <section style={{ maxWidth: "68ch" }}>
      <p className="eyebrow">Educação continuada</p>
      <h1>Cursos parceiros</h1>
      <div className="cartao" style={{ marginTop: "1rem", textAlign: "center", padding: "2rem" }}>
        <p className="eyebrow">Em breve</p>
        <h2>Novos cursos parceiros estão em preparação</h2>
        <p style={{ color: "var(--texto-secundario)", marginBottom: 0 }}>
          O antigo curso demonstrativo foi retirado. Esta área será liberada somente
          quando houver parceiro real, conteúdo revisado, contrato e cobrança configurados.
        </p>
      </div>
    </section>
  );
}
