import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Guarda de regressão para o bug de lifecycle corrigido em 13/08/2026 (KYC —
// selfie ao vivo): `ligarCamera()` chamava `getUserMedia()` e tentava ligar
// `videoRef.current.srcObject` ANTES de `setAtiva(true)` — nesse instante o
// <video> ainda não existia no DOM (só é montado quando `ativa === true`),
// então a conexão do stream falhava em silêncio. A correção move a conexão
// do stream para um `useEffect` que roda DEPOIS de `ativa` virar `true`, com
// o elemento já montado. Este script falha se alguém reintroduzir o padrão
// antigo, remover o tratamento de erro por tipo, ou abrir um fallback de
// upload que anularia o propósito da selfie ao vivo (KYC — Trabalho 11/12).

const targetPath = new URL("../src/components/SelfieAoVivo.tsx", import.meta.url);

/** Extrai o corpo de uma função a partir do índice onde `{` abre, contando
 * chaves até fechar — mais confiável que regex ao lidar com aninhamento. */
function extrairCorpo(source, indiceAbertura) {
  if (indiceAbertura === -1) return null;
  let profundidade = 0;
  for (let i = indiceAbertura; i < source.length; i++) {
    if (source[i] === "{") profundidade++;
    else if (source[i] === "}") {
      profundidade--;
      if (profundidade === 0) return source.slice(indiceAbertura, i + 1);
    }
  }
  return null;
}

function corpoDaFuncaoQueChama(source, nomeDaFuncao, chamadaAlvo) {
  const assinatura = new RegExp(`function\\s+${nomeDaFuncao}\\s*\\([^)]*\\)\\s*\\{`);
  const m = assinatura.exec(source);
  if (!m) return null;
  const corpo = extrairCorpo(source, source.indexOf("{", m.index));
  if (corpo && !corpo.includes(chamadaAlvo)) return null;
  return corpo;
}

export function validateCameraLifecycle(source) {
  const failures = [];

  // 1) `ligarCamera` (a função que chama getUserMedia) NÃO pode atribuir
  //    `.srcObject` diretamente — é exatamente o bug original.
  const corpoLigarCamera = corpoDaFuncaoQueChama(source, "ligarCamera", "getUserMedia");
  if (!corpoLigarCamera) {
    failures.push("não encontrei uma função ligarCamera() chamando getUserMedia — contrato não verificável");
  } else if (/\.srcObject\s*=/.test(corpoLigarCamera)) {
    failures.push(
      "ligarCamera() atribui .srcObject diretamente — a conexão do stream ao <video> deve acontecer " +
        "num useEffect dependente de `ativa`, executado depois do elemento montar, não dentro da função " +
        "que pede getUserMedia",
    );
  }

  // 2) Deve existir um useEffect, dependente de `ativa`, que conecta o
  //    stream ao <video> — a correção em si. Cada ocorrência é processada
  //    pela própria posição no source (nunca por indexOf do corpo já
  //    extraído), porque dois efeitos podem ter corpos com texto repetido.
  const efeitos = [];
  for (const m of source.matchAll(/useEffect\(\s*\(\)\s*=>\s*\{/g)) {
    const aberturaCorpo = source.indexOf("{", m.index);
    const corpo = extrairCorpo(source, aberturaCorpo);
    if (!corpo) continue;
    const restante = source.slice(aberturaCorpo + corpo.length, aberturaCorpo + corpo.length + 60);
    const depsMatch = /^\s*,\s*\[([^\]]*)\]\s*\)/.exec(restante);
    efeitos.push({ corpo, deps: depsMatch ? depsMatch[1] : null });
  }
  const efeitoDeConexao = efeitos.find((e) => e.corpo.includes(".srcObject") && e.corpo.includes("ativa"));
  if (!efeitoDeConexao) {
    failures.push(
      "não encontrei um useEffect que conecte .srcObject e dependa de `ativa` — a conexão do stream ao " +
        "<video> deve acontecer só depois de `ativa` virar true (elemento já montado)",
    );
  } else if (efeitoDeConexao.deps === null || !efeitoDeConexao.deps.includes("ativa")) {
    failures.push("o useEffect que conecta o stream ao <video> precisa depender de [ativa]");
  }

  // 3) Sem fallback de upload de arquivo pronto para a selfie.
  if (/type\s*=\s*["']file["']/.test(source)) {
    failures.push(
      "encontrei um <input type=\"file\"> — a selfie do KYC não pode ter fallback de upload de arquivo pronto",
    );
  }

  // 4) Preferência pela câmera frontal via facingMode ideal, não obrigatório.
  if (!/facingMode\s*:\s*\{\s*ideal\s*:\s*["']user["']\s*\}/.test(source)) {
    failures.push('getUserMedia precisa pedir facingMode: { ideal: "user" } (câmera frontal preferida, não forçada)');
  }

  // 5) Atributos do <video> preservados. `<video\s` (exige espaço logo
  //    depois) em vez de `<video\b` evita casar a menção em prosa ao
  //    elemento dentro de comentário (`// O <video> só existe...`), que não
  //    tem espaço após "video" e viria antes da tag JSX real no source.
  const videoTag = /<video\s[^>]*>/.exec(source)?.[0] ?? "";
  for (const atributo of ["autoPlay", "playsInline", "muted"]) {
    if (!new RegExp(`\\b${atributo}\\b`).test(videoTag)) {
      failures.push(`<video> perdeu o atributo ${atributo}`);
    }
  }

  // 6) Tratamento diferenciado dos três erros de câmera mais comuns.
  for (const nomeDeErro of ["NotAllowedError", "NotFoundError", "NotReadableError"]) {
    if (!source.includes(nomeDeErro)) {
      failures.push(`falta tratamento explícito para ${nomeDeErro}`);
    }
  }

  // 7) Cleanup de desmontagem (useEffect(() => () => <limpeza>, [])) não deve
  //    chamar setState — só liberar a câmera. setState num componente que já
  //    está desmontando é desnecessário (e gera aviso do React).
  const efeitoDeDesmontagem =
    /useEffect\(\s*\(\)\s*=>\s*\(\)\s*=>\s*(\{[\s\S]*?\}|[^,]+),\s*\[\s*\]\s*\)/.exec(source);
  if (!efeitoDeDesmontagem) {
    failures.push("não encontrei um useEffect de desmontagem (useEffect(() => () => ..., [])) liberando a câmera");
  } else if (/\bset[A-Z]\w*\s*\(/.test(efeitoDeDesmontagem[1])) {
    failures.push("o cleanup de desmontagem chama setState — deve só liberar a câmera (pararTracks), sem setState");
  }

  return failures;
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1]);

if (isMain) {
  const source = await readFile(fileURLToPath(targetPath), "utf8");
  const failures = validateCameraLifecycle(source);
  if (failures.length) {
    console.error("Falha no contrato de lifecycle da câmera (SelfieAoVivo.tsx):\n");
    for (const failure of failures) console.error(`- ${failure}`);
    process.exit(1);
  }
  console.log("Lifecycle da câmera (SelfieAoVivo.tsx): stream só conecta com o <video> já montado, sem regressão.");
}
