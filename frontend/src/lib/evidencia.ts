// Rótulos de classe/força e nível/certeza das evidências.
//
// Existe aqui, e não dentro de uma página, porque a MESMA regra vale na lista
// (`Evidencias.tsx`) e no detalhe (`Evidencia.tsx`). Enquanto a lógica estava
// só no detalhe, a lista imprimia `Nível {evidence_level}` fixo e mostrava
// "Nível Alta" e "Nível Mod" para os registros em GRADE — corrigido em
// 31/07/2026 movendo tudo para cá.
//
// A base convive com TRÊS sistemas de graduação diferentes, porque as
// sociedades não usam o mesmo:
//
//  1. ESC/AHA clássico      — Classe I/IIa/IIb/III  +  Nível A/B/C
//  2. ACC/AHA 2016          — mesmas classes, mas o nível ganha sufixo:
//                             A, B-R, B-NR, C-LD, C-EO. É o sistema que a
//                             World Heart Federation adota na diretriz de
//                             cardiopatia reumática de 2023 (que grafa a
//                             classe em algarismo arábico — 1, 2A, 2B —,
//                             normalizada para I/IIa/IIb na carga).
//  3. GRADE                 — Força forte/ponderada/condicional/fraca  +
//                             certeza alta/moderada/baixa/muito baixa.
//                             Usado pela OMS e pelas diretrizes brasileiras
//                             de Chagas e de eco de estresse.
//
// Os dois rótulos são decididos de forma INDEPENDENTE, porque os sistemas se
// misturam na prática: a diretriz da SBC de Chagas usa força "Forte/Ponderada"
// junto com nível de evidência A/B/C — ali o certo é "Força Forte" + "Nível B".

const CLASSES_ESC = new Set(["I", "IIa", "IIb", "III"]);

// Níveis em letra simples (ESC/AHA clássico) e com sufixo (ACC/AHA 2016).
// `evidence_level` é varchar(5) no banco, o que acomoda "B-NR" e "C-EO" sem
// migração — mas não acomoda "Moderada" (8 caracteres), e é por isso que a
// certeza GRADE é gravada abreviada e expandida aqui, na exibição.
const NIVEIS_LETRA = new Set(["A", "B", "C", "B-R", "B-NR", "C-LD", "C-EO"]);

const CERTEZA_POR_EXTENSO: Record<string, string> = {
  Alta: "alta",
  Mod: "moderada",
  Baixa: "baixa",
  MtBx: "muito baixa",
};

// `recommendation_class` é varchar(10), e "Condicional" tem 11 caracteres — não
// cabe por um caractere. Gravado abreviado e expandido aqui, pela mesma razão e
// da mesma forma que a certeza GRADE acima. As demais forças ("Forte", "Fraca",
// "Ponderada") cabem e são gravadas por extenso.
const FORCA_POR_EXTENSO: Record<string, string> = { Cond: "condicional" };

export const rotuloClasse = (c: string) =>
  CLASSES_ESC.has(c) ? `Classe ${c}` : `Força ${FORCA_POR_EXTENSO[c] ?? c}`;

// Versão curta, para o selo da listagem, onde não cabe a palavra inteira.
export const rotuloClasseCurto = (c: string) =>
  CLASSES_ESC.has(c) ? c : (FORCA_POR_EXTENSO[c] ? "Condic." : c);

export const rotuloNivel = (n: string) => {
  // "?" é usado quando a classe foi confirmada mas a letra do nível não pôde
  // ser lida na fonte original (hoje: uma recomendação da AHA 2009 atrás de
  // paywall). Mostrar "Nível ?" ou "Certeza ?" não diz nada ao leitor.
  if (n === "?") return "Nível não confirmado";
  return NIVEIS_LETRA.has(n)
    ? `Nível ${n}`
    : `Certeza ${CERTEZA_POR_EXTENSO[n] ?? n}`;
};
