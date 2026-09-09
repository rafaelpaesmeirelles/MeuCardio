import test, { after } from "node:test";
import assert from "node:assert/strict";
import { readFile, mkdtemp, writeFile, rm } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import React from "react";
import TestRenderer, { act } from "react-test-renderer";
import { transform } from "esbuild";

const root = fileURLToPath(new URL("../", import.meta.url));
const temp = await mkdtemp(path.join(root, "node_modules/.signature-tests-"));
after(() => rm(temp, { recursive: true, force: true }));
const source = await readFile(path.join(root, "src/components/FinalizarDocumentoGerado.tsx"), "utf8");
// Run the real component and React effects with API/child-widget boundaries stubbed.
const component = source.slice(source.indexOf("function FinalizarDocumentoGerado("));
const transformed = await transform(`
import React, { useState, useEffect } from 'react';
const METODOS_MANUAL_EXTERNO = new Set(['GOVBR','VIDAAS','BIRDID','SAFEID','NEOID','REMOTEID','A3_TOKEN']);
const api = {get:(...args)=>globalThis.signatureFixture.get(...args), blob:(...args)=>globalThis.signatureFixture.blob(...args), post:()=>{throw Error('unexpected send')}};
class ApiError extends Error {}
const useAuth=()=>({usuario:{assinatura_metodo_preferido:'MANUAL'}});
const baixarBlob=()=>{};
const AssinaturaExternaITI=()=>null;
const OfertaEnvioEmailPaciente=()=>null;
${component}
export default FinalizarDocumentoGerado;
`, {loader:"tsx", format:"esm"});
const filename = path.join(temp, "finalize.mjs");
await writeFile(filename, transformed.code);
const {default: Finalize} = await import(pathToFileURL(filename));
const providers = [
  {codigo:"MANUAL", nome:"Manual", disponivel:true},
  {codigo:"A1_ARQUIVO", nome:"Certificado A1", disponivel:true},
  {codigo:"GOVBR", nome:"gov.br", disponivel:true},
];
const text = node => node.children.map(c => typeof c === "string" ? c : text(c)).join("");
const button = (renderer, label) => renderer.root.findAllByType("button").find(b => text(b).includes(label));
async function mount(signature = null, fail = false) {
  const calls = [];
  globalThis.signatureFixture = {
    get: async url => url.includes('/assinatura/provedores') ? providers : {assinatura:signature},
    blob: async url => { calls.push(url); if (fail) throw Error('signing failed'); return new Blob(['PDF']); },
  };
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(Finalize, {geradoId:20,nomeArquivoBase:'documento',provedores:providers,onFechar:()=>{}})); });
  return {renderer,calls};
}

test('A1 selection is sent to emission and locks only after success', async () => {
  const {renderer,calls} = await mount();
  assert.equal(button(renderer,'Enviar por e-mail').props.disabled,true);
  await act(async () => renderer.root.findByType('select').props.onChange({target:{value:'A1_ARQUIVO'}}));
  await act(async () => button(renderer,'Assinar digitalmente').props.onClick());
  assert.match(calls[0], /pdf\?metodo=A1_ARQUIVO$/);
  assert.equal(renderer.root.findByType('select').props.disabled,true);
  await act(async () => renderer.root.findByType('input').props.onChange({target:{value:'exemplo@teste.local'}}));
  assert.equal(button(renderer,'Enviar por e-mail').props.disabled,false);
  await act(async () => renderer.unmount());
});

test('Failed signature keeps email locked and method selectable', async () => {
  const {renderer} = await mount(null,true);
  await act(async () => renderer.root.findByType('select').props.onChange({target:{value:'A1_ARQUIVO'}}));
  await act(async () => button(renderer,'Assinar digitalmente').props.onClick());
  assert.equal(renderer.root.findByType('select').props.disabled,false);
  assert.equal(button(renderer,'Enviar por e-mail').props.disabled,true);
  assert.ok(renderer.root.findByProps({role:'alert'}));
  await act(async () => renderer.unmount());
});

test('External signature stays pending after preparing the PDF', async () => {
  const {renderer} = await mount();
  await act(async () => renderer.root.findByType('select').props.onChange({target:{value:'GOVBR'}}));
  await act(async () => button(renderer,'Preparar PDF').props.onClick());
  await act(async () => renderer.root.findByType('input').props.onChange({target:{value:'exemplo@teste.local'}}));
  assert.equal(button(renderer,'Enviar por e-mail').props.disabled,true);
  await act(async () => renderer.unmount());
});

test('Reopening signed PDF restores its method rather than the account default', async () => {
  const {renderer,calls} = await mount({metodo:'A1_ARQUIVO',assinado_em:'2026-09-09T12:00:00Z'});
  assert.equal(renderer.root.findByType('select').props.value,'A1_ARQUIVO');
  assert.equal(renderer.root.findByType('select').props.disabled,true);
  await act(async () => button(renderer,'Baixar PDF').props.onClick());
  assert.match(calls[0], /metodo=A1_ARQUIVO$/);
  await act(async () => renderer.unmount());
});
