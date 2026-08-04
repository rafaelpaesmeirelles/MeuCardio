export default function FilaTelediagnostico() {
  return (
    <section style={{ maxWidth: "68ch" }}>
      <p className="eyebrow">Administração</p>
      <h1>Fila de telediagnóstico</h1>
      <div className="cartao" style={{ marginTop: "1rem" }}>
        <strong>Recurso desativado</strong>
        <p style={{ color: "var(--texto-secundario)", marginBottom: 0 }}>
          A fila ficará disponível quando o Telediagnóstico for reativado. Os pedidos
          históricos permanecem preservados no banco e nos volumes cifrados.
        </p>
      </div>
    </section>
  );
}
