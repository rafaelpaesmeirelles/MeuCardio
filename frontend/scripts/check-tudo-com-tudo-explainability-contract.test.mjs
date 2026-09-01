import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");

const busca = read("src/pages/Busca.tsx");
const contexto = read("src/components/TudoSobreEsteTema.tsx");
const grafo = read("src/components/GrafoRelacionados.tsx");

test("full-text search is not presented as a clinical connection", () => {
  assert.match(busca, /Tudo com Tudo · busca textual/);
  assert.match(busca, /Um resultado textual não é, por si só, uma conexão clínica/);
  assert.match(busca, /data-search-mode="full-text"/);
  assert.match(busca, /Correspondências encontradas/);
  assert.match(busca, /sinal \$\{item\.match_score\} · mínimo \$\{item\.match_threshold\}/);
  assert.doesNotMatch(busca, /Conteúdo conectado/);
  assert.doesNotMatch(busca, /Conectando o conhecimento/);
});

test("contextual inference is explicit and deduplicated against graph relations", () => {
  assert.match(contexto, /data-relationship-surface="contextual-inference"/);
  assert.match(contexto, /Inferida por contexto/);
  assert.match(contexto, /não equivale a vínculo clínico curado/);
  assert.match(contexto, /carregarRelacoesDoGrafo/);
  assert.match(contexto, /chavesVisiveisDoGrafo/);
  assert.match(contexto, /!chavesDoGrafo\.has\(`\$\{grupo\.tipo\}:\$\{item\.slug\}`\)/);
  assert.match(contexto, /Relações já exibidas no grafo foram removidas daqui/);
  assert.match(contexto, /sinal \$\{item\.match_score\} · mínimo \$\{item\.match_threshold\}/);
});

test("reviewed medication topics propagate response-level explainability", () => {
  assert.match(contexto, /relation_scope\?: string/);
  assert.match(contexto, /relation_method\?: string/);
  assert.match(contexto, /contexto\.relation_scope === "structured_clinical_topic"/);
  assert.match(contexto, /contexto\.relation_method === "reviewed_drug_indication"/);
  assert.match(contexto, /Estruturada e revisada/);
  assert.match(contexto, /indicação clínica revisada/);
  assert.match(contexto, /explicacao\.rotulo\.startsWith\("Estruturada"\) \? "estruturada"/);
});

test("full-text deduplication removes only the same contextual item", () => {
  assert.match(busca, /const chavesTextuais = new Set/);
  assert.match(busca, /!chavesTextuais\.has\(`\$\{g\.tipo\}:\$\{item\.slug\}`\)/);
  assert.match(busca, /!chavesTextuais\.has\(`rota:\$\{item\.rota\}`\)/);
  assert.doesNotMatch(busca, /!cobertos\.has\(g\.tipo\)/);
});

test("knowledge graph exposes provenance, confidence, review and relevance", () => {
  assert.match(grafo, /data-relationship-surface="knowledge-graph"/);
  assert.match(grafo, /Curada e revisada/);
  assert.match(grafo, /Estruturada e revisada/);
  assert.match(grafo, /Inferida · não curada/);
  assert.match(grafo, /ROTULO_PROVENIENCIA/);
  assert.match(grafo, /ROTULO_CONFIANCA/);
  assert.match(grafo, /ROTULO_RELACAO/);
  assert.match(grafo, /pertinência \{percentual\(item\.relevance_score\)\}/);
  assert.match(grafo, /item\.review_status === "pendente_revisao"/);
  assert.match(grafo, /Vínculo explícito de fonte importada/);
});

test("graph requests are shared by the contextual and graph panels", () => {
  assert.match(grafo, /const graphRequests = new Map<string, Promise<Resposta>>\(\)/);
  assert.match(grafo, /const existente = graphRequests\.get\(key\)/);
  assert.match(grafo, /graphRequests\.set\(key, request\)/);
});
