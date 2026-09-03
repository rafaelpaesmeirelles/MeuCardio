import type { Usuario } from "./api";

export type FonteIdentidadeClinica = Pick<Usuario, "full_name" | "professional_title"> & {
  gender?: string | null;
  genero?: string | null;
  sex?: string | null;
  sexo?: string | null;
};

type OpcoesChamamento = {
  curto?: boolean;
  inicioDeFrase?: boolean;
  fallback?: string;
};

function normalizarMarcador(valor?: string | null): string {
  return (valor || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .replaceAll(".", "")
    .replace(/\s+/g, " ")
    .trim();
}

function artigoDoTratamento(usuario?: FonteIdentidadeClinica | null): "a" | "o" | "" {
  const tratamento = normalizarMarcador(usuario?.professional_title);
  if (!tratamento) return "";

  if (["sra", "dra", "profa", "profa dra", "ma"].includes(tratamento)) return "a";
  if (["sr", "dr", "prof", "prof dr", "me"].includes(tratamento)) return "o";

  const marcador = normalizarMarcador(usuario?.gender || usuario?.genero || usuario?.sex || usuario?.sexo);
  if (["f", "feminino", "feminina", "female", "mulher"].includes(marcador)) return "a";
  if (["m", "masculino", "masculina", "male", "homem"].includes(marcador)) return "o";
  return "";
}

export function nomeComTratamento(usuario?: FonteIdentidadeClinica | null, curto = false): string {
  const nomeCompleto = usuario?.full_name?.trim() || "Assinante";
  const tratamento = usuario?.professional_title?.trim();
  const partes = nomeCompleto.split(/\s+/).filter(Boolean);
  const nomeSemTitulo = tratamento
    ? partes.filter((parte) => !/^(sr|sra|dr|dra|prof|profa|me|ma|esp)\.?$/i.test(parte)).join(" ") || nomeCompleto
    : nomeCompleto;
  const nome = curto ? nomeSemTitulo.split(/\s+/)[0] : nomeSemTitulo;
  return [tratamento, nome].filter(Boolean).join(" ");
}

export function chamamentoComArtigo(
  usuario?: FonteIdentidadeClinica | null,
  { curto = false, inicioDeFrase = false, fallback = "você" }: OpcoesChamamento = {},
): string {
  if (!usuario?.full_name?.trim()) return inicioDeFrase
    ? fallback.charAt(0).toLocaleUpperCase("pt-BR") + fallback.slice(1)
    : fallback;

  const identidade = nomeComTratamento(usuario, curto);
  const artigo = artigoDoTratamento(usuario);
  const resultado = [artigo, identidade].filter(Boolean).join(" ");
  return inicioDeFrase
    ? resultado.charAt(0).toLocaleUpperCase("pt-BR") + resultado.slice(1)
    : resultado;
}
