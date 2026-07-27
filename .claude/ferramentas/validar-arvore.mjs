// Valida que cada bloco ```mermaid``` dos .md passados e uma ARVORE DE DECISAO
// estrita, no padrao da casa:
//   raiz      R["..."]      retangulo, exatamente uma, sem aresta de entrada
//   decisao   D{"...?"}     losango, precisa de 2+ filhos e de rotulo em toda aresta
//   conduta   C(["..."])    estadio, e sempre folha
// Propriedade de arvore: todo no que nao e a raiz tem exatamente um pai.
// Isso e o que proibe caminho convergente e volta — o que um flowchart permite
// e uma arvore de decisao, nao.
import { readFileSync } from "node:fs";

const FORMA = {
  '["': "raiz-ou-passo",
  '{"': "decisao",
  '(["': "conduta",
};

function formaDe(decl) {
  if (!decl) return null;
  if (decl.startsWith('(["')) return "conduta";
  if (decl.startsWith('{"')) return "decisao";
  if (decl.startsWith('["')) return "raiz-ou-passo";
  return "desconhecida";
}

function analisar(bloco) {
  const problemas = [];
  const forma = new Map();
  const arestas = [];
  const pais = new Map();

  const DECL = String.raw`(?:\(\["[^"]*"\]\)|\{"[^"]*"\}|\["[^"]*"\])`;
  const re = new RegExp(
    String.raw`^\s*([A-Za-z][\w]*)\s*(${DECL})?\s*-->\s*(?:\|([^|]*)\|)?\s*([A-Za-z][\w]*)\s*(${DECL})?\s*$`
  );

  for (const linhaBruta of bloco.split("\n")) {
    const linha = linhaBruta.trim();
    if (!linha || linha.startsWith("%%")) continue;
    if (/^(flowchart|graph)\b/.test(linha)) continue;
    if (/^(classDef|class|style|linkStyle|subgraph|end)\b/.test(linha)) continue;

    const m = linha.match(re);
    if (!m) {
      problemas.push(`linha fora do padrao da casa: ${linha}`);
      continue;
    }
    const [, de, declDe, rotulo, para, declPara] = m;
    if (declDe) forma.set(de, formaDe(declDe));
    if (declPara) forma.set(para, formaDe(declPara));
    arestas.push({ de, para, rotulo: (rotulo || "").trim() });
    pais.set(para, (pais.get(para) || 0) + 1);
  }

  const nos = new Set(arestas.flatMap((a) => [a.de, a.para]));
  const filhos = new Map();
  for (const a of arestas) filhos.set(a.de, [...(filhos.get(a.de) || []), a]);

  // 1. arvore: uma unica raiz, e todo o resto com exatamente um pai
  const raizes = [...nos].filter((n) => !pais.has(n));
  if (raizes.length !== 1) problemas.push(`raizes encontradas: ${raizes.length} (${raizes.join(", ") || "nenhuma"}) — a arvore precisa de exatamente uma`);
  for (const [no, qtd] of pais) {
    if (qtd > 1) problemas.push(`no '${no}' tem ${qtd} pais — caminho convergente nao e arvore`);
  }

  // 2. sem ciclo (alcancavel a partir da raiz sem revisitar)
  if (raizes.length === 1) {
    const visto = new Set();
    const pilha = [raizes[0]];
    while (pilha.length) {
      const n = pilha.pop();
      if (visto.has(n)) { problemas.push(`ciclo alcancando '${n}'`); continue; }
      visto.add(n);
      for (const a of filhos.get(n) || []) pilha.push(a.para);
    }
    for (const n of nos) if (!visto.has(n)) problemas.push(`no '${n}' inalcancavel a partir da raiz`);
  }

  // 3. toda folha e conduta; toda decisao ramifica e rotula
  for (const n of nos) {
    const f = forma.get(n) || "sem-declaracao";
    const saida = filhos.get(n) || [];
    if (saida.length === 0 && f !== "conduta") {
      problemas.push(`folha '${n}' e do tipo '${f}' — folha precisa ser conduta (["..."])`);
    }
    if (f === "conduta" && saida.length > 0) {
      problemas.push(`conduta '${n}' tem ${saida.length} filho(s) — conduta e sempre folha`);
    }
    if (f === "decisao") {
      if (saida.length < 2) problemas.push(`decisao '${n}' tem ${saida.length} ramo(s) — precisa de ao menos 2`);
      for (const a of saida) if (!a.rotulo) problemas.push(`aresta ${n} --> ${a.para} sem rotulo — ramo de decisao precisa de rotulo`);
    }
  }

  return { problemas, nos: nos.size, arestas: arestas.length, folhas: [...nos].filter((n) => !(filhos.get(n) || []).length).length };
}

let falhas = 0;
for (const arq of process.argv.slice(2)) {
  const blocos = [...readFileSync(arq, "utf8").matchAll(/```mermaid\n([\s\S]*?)```/g)].map((m) => m[1]);
  if (!blocos.length) { console.log(`AVISO  ${arq}: nenhum bloco mermaid`); continue; }
  for (const [i, b] of blocos.entries()) {
    const r = analisar(b);
    const rot = `${arq.replace("/opt/meucardio/content/", "")} [bloco ${i + 1}]`;
    if (r.problemas.length) {
      falhas++;
      console.log(`FALHA  ${rot}`);
      for (const p of r.problemas) console.log(`         - ${p}`);
    } else {
      console.log(`OK     ${rot}  (${r.nos} nos, ${r.folhas} condutas)`);
    }
  }
}
process.exit(falhas ? 1 : 0);
