// Valida os blocos ```mermaid``` dos .md passados como argumento usando o
// parser real da lib (mermaid.parse), com jsdom fornecendo o DOM que o
// DOMPurify exige. Rodar a partir de /opt/meucardio/frontend.
import { readFileSync } from "node:fs";
import { JSDOM } from "/opt/meucardio/frontend/node_modules/jsdom/lib/api.js";

const dom = new JSDOM("<!doctype html><html><body></body></html>");
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.navigator = dom.window.navigator;
globalThis.Element = dom.window.Element;
globalThis.HTMLElement = dom.window.HTMLElement;
globalThis.Node = dom.window.Node;
globalThis.DocumentFragment = dom.window.DocumentFragment;
globalThis.NodeFilter = dom.window.NodeFilter;
globalThis.SVGElement = dom.window.SVGElement;
globalThis.DOMParser = dom.window.DOMParser;

const { default: mermaid } = await import("/opt/meucardio/frontend/node_modules/mermaid/dist/mermaid.core.mjs");
mermaid.initialize({ startOnLoad: false });

const arquivos = process.argv.slice(2);
let falhas = 0;
let blocosTotais = 0;

for (const arq of arquivos) {
  const texto = readFileSync(arq, "utf8");
  const blocos = [...texto.matchAll(/```mermaid\n([\s\S]*?)```/g)].map((m) => m[1]);
  if (blocos.length === 0) {
    console.log(`AVISO  ${arq}: nenhum bloco mermaid`);
    continue;
  }
  for (const [i, bloco] of blocos.entries()) {
    blocosTotais++;
    try {
      await mermaid.parse(bloco);
      console.log(`OK     ${arq} [bloco ${i + 1}]`);
    } catch (e) {
      console.log(`FALHA  ${arq} [bloco ${i + 1}]: ${String(e.message).split("\n")[0]}`);
      falhas++;
    }
  }
}
console.log(`\n${blocosTotais - falhas}/${blocosTotais} blocos validos`);
process.exit(falhas ? 1 : 0);
