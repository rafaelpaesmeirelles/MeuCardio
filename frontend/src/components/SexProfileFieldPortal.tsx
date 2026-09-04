import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { api, ApiError, type Usuario } from "../lib/api";
import { useAuth } from "../lib/auth";

type UsuarioComSexo = Usuario & { sex?: string | null };

export default function SexProfileFieldPortal({ active }: { active: boolean }) {
  const { usuario, recarregar } = useAuth();
  const user = usuario as UsuarioComSexo | null;
  const [host, setHost] = useState<HTMLElement | null>(null);
  const [value, setValue] = useState(user?.sex ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => setValue(user?.sex ?? ""), [user?.sex]);

  useEffect(() => {
    if (!active || user?.investidor) {
      setHost(null);
      return;
    }

    const mount = () => {
      const card = document.getElementById("dados-pessoais");
      const treatment = document.querySelector('label[for="conta-tratamento"]');
      if (!(card instanceof HTMLElement) || !(treatment instanceof HTMLElement)) return false;
      let portalHost = card.querySelector<HTMLElement>("[data-sex-profile-portal]");
      if (!portalHost) {
        portalHost = document.createElement("div");
        portalHost.dataset.sexProfilePortal = "true";
        treatment.parentElement?.insertBefore(portalHost, treatment);
      }
      setHost(portalHost);
      return true;
    };

    if (mount()) return;
    const observer = new MutationObserver(() => {
      if (mount()) observer.disconnect();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, [active, user?.investidor]);

  const help = useMemo(() => {
    if (!value) return "Usado somente para a concordância do tratamento: “o Dr.” ou “a Dra.”.";
    return value === "F"
      ? "A interface usará o artigo “a” antes do título escolhido."
      : "A interface usará o artigo “o” antes do título escolhido.";
  }, [value]);

  if (!active || user?.investidor || !host) return null;

  async function change(next: string) {
    setValue(next);
    setError("");
    setSaved(false);
    if (!next) return;
    setSaving(true);
    try {
      await api.patch<{ sex: "M" | "F" }>("/auth/me/sex", { sex: next });
      await recarregar();
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível salvar o sexo cadastral.");
    } finally {
      setSaving(false);
    }
  }

  return createPortal(
    <div style={{ marginTop: "0.8rem", marginBottom: "0.2rem" }}>
      <label htmlFor="conta-sexo">Sexo</label>
      <select
        id="conta-sexo"
        value={value}
        disabled={saving}
        onChange={(event) => void change(event.target.value)}
        aria-describedby="conta-sexo-nota"
      >
        <option value="">Selecione</option>
        <option value="M">Masculino</option>
        <option value="F">Feminino</option>
      </select>
      <p id="conta-sexo-nota" className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
        {saving ? "Salvando…" : saved ? "Salvo. A personalização já foi atualizada." : help}
      </p>
      {error && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>{error}</p>}
    </div>,
    host,
  );
}
