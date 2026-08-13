import assert from "node:assert/strict";
import test from "node:test";

import { validateCameraLifecycle } from "./check-camera-lifecycle.mjs";

// Fonte sintética mínima que satisfaz o contrato inteiro — cada teste de
// falha parte desta base e quebra exatamente UMA regra por vez, mesmo
// padrão de check-rendering-security.test.mjs.
const FONTE_BOA = `
function ligarCamera() {
  const stream = getUserMedia();
  streamRef.current = stream;
  setAtiva(true);
}

useEffect(() => {
  if (!ativa) return;
  video.srcObject = streamRef.current;
  video.play();
}, [ativa]);

useEffect(() => () => pararTracks(), []);

if (erroCapturado.name === "NotAllowedError") {}
if (erroCapturado.name === "NotFoundError") {}
if (erroCapturado.name === "NotReadableError") {}

getUserMedia({ video: { facingMode: { ideal: "user" } } });

<video ref={videoRef} autoPlay playsInline muted />
`;

test("fonte que segue o contrato não falha em nenhuma regra", () => {
  assert.deepEqual(validateCameraLifecycle(FONTE_BOA), []);
});

test("falha se ligarCamera voltar a atribuir .srcObject diretamente (o bug original)", () => {
  const comBug = FONTE_BOA.replace(
    "function ligarCamera() {\n  const stream = getUserMedia();\n  streamRef.current = stream;\n  setAtiva(true);\n}",
    "function ligarCamera() {\n  const stream = getUserMedia();\n  streamRef.current = stream;\n  videoRef.current.srcObject = stream;\n  setAtiva(true);\n}",
  );
  const falhas = validateCameraLifecycle(comBug);
  assert.match(falhas.join("\n"), /ligarCamera\(\) atribui \.srcObject diretamente/);
});

test("falha se o useEffect de conexão não depender de [ativa]", () => {
  const semDep = FONTE_BOA.replace(
    "}, [ativa]);",
    "}, []);",
  );
  const falhas = validateCameraLifecycle(semDep);
  assert.match(falhas.join("\n"), /precisa depender de \[ativa\]/);
});

test("falha se não houver nenhum useEffect conectando .srcObject", () => {
  const semEfeito = FONTE_BOA.replace(
    /useEffect\(\(\) => \{\n  if \(!ativa\) return;\n  video\.srcObject = streamRef\.current;\n  video\.play\(\);\n\}, \[ativa\]\);\n\n/,
    "",
  );
  const falhas = validateCameraLifecycle(semEfeito);
  assert.match(falhas.join("\n"), /não encontrei um useEffect que conecte \.srcObject/);
});

test("falha se reabrirem fallback de upload de arquivo", () => {
  const comUpload = `${FONTE_BOA}\n<input type="file" accept="image/*" />`;
  const falhas = validateCameraLifecycle(comUpload);
  assert.match(falhas.join("\n"), /fallback de upload de arquivo pronto/);
});

test("falha se facingMode deixar de preferir a câmera frontal", () => {
  const semFacingMode = FONTE_BOA.replace('facingMode: { ideal: "user" }', "");
  const falhas = validateCameraLifecycle(semFacingMode);
  assert.match(falhas.join("\n"), /facingMode: \{ ideal: "user" \}/);
});

test("falha se o <video> perder autoPlay, playsInline ou muted", () => {
  const semMuted = FONTE_BOA.replace("<video ref={videoRef} autoPlay playsInline muted />", "<video ref={videoRef} autoPlay playsInline />");
  const falhas = validateCameraLifecycle(semMuted);
  assert.match(falhas.join("\n"), /perdeu o atributo muted/);
});

test("falha se faltar tratamento de algum dos três erros de câmera", () => {
  const semNotFound = FONTE_BOA.replace('if (erroCapturado.name === "NotFoundError") {}', "");
  const falhas = validateCameraLifecycle(semNotFound);
  assert.match(falhas.join("\n"), /falta tratamento explícito para NotFoundError/);
});

test("falha se o cleanup de desmontagem chamar setState", () => {
  const comSetState = FONTE_BOA.replace(
    "useEffect(() => () => pararTracks(), []);",
    "useEffect(() => () => { pararTracks(); setAtiva(false); }, []);",
  );
  const falhas = validateCameraLifecycle(comSetState);
  assert.match(falhas.join("\n"), /cleanup de desmontagem chama setState/);
});
