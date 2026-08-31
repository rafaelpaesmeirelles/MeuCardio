import type { Usuario } from "./api";

export function nomeComTratamento(usuario?: Pick<Usuario, "full_name" | "professional_title"> | null, curto = false): string {
  const nomeCompleto = usuario?.full_name?.trim() || "Assinante";
  const tratamento = usuario?.professional_title?.trim();
  const partes = nomeCompleto.split(/\s+/).filter(Boolean);
  const nomeSemTitulo = tratamento
    ? partes.filter((parte) => !/^(sr|sra|dr|dra|prof|profa|me|ma|esp)\.?$/i.test(parte)).join(" ") || nomeCompleto
    : nomeCompleto;
  const nome = curto ? nomeSemTitulo.split(/\s+/)[0] : nomeSemTitulo;
  return [tratamento, nome].filter(Boolean).join(" ");
}
