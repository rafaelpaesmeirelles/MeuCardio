import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { stripTypeScriptTypes } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';

const source = file => readFileSync(new URL(`../src/${file}`, import.meta.url), 'utf8');
const page = source('pages/AdminGerenciarUsuario.tsx');
const apiSource = source('lib/api.ts');
function section(text, start, end) {
  const a = text.indexOf(start), b = text.indexOf(end, a + start.length);
  assert(a >= 0 && b > a, `Real source section exists: ${start}`);
  return text.slice(a, b);
}
const transform = code => stripTypeScriptTypes(code.replace(/^export /gm, ''), { mode: 'transform' });
const errorCode = transform(section(apiSource, 'export class ApiError', 'function redirecionarSessaoExpirada'));
const helpers = transform(section(page, 'const CAMPOS_TEXTO', 'export default function'));
const save = transform(section(page, '  async function salvar()', '\n  async function trocarSenha()'));

function harness({ self = true, role = 'admin', fail = false, sessionId = 99001 } = {}) {
  const user = { id: 99001, role, full_name: 'Profissional de Demonstração', email: 'demo@example.invalid',
    profession: 'Medicina', council_name: 'CRM', council_number: 'DEMO', council_state: 'SP',
    specialty: 'Especialidade demonstrativa', rqe: null, professional_title: 'Dr.',
    workplace_name: 'Instituição demonstrativa', workplace_department: null, workplace_role: null,
    workplace_notes: 'Rascunho profissional', cpf: 'DADO NÃO ENVIADO', birth_date: '1980-01-01',
    is_active: true, tipo_acesso: 'normal' };
  const latest = { ...user, id: sessionId, home_street: 'Rua de Demonstração', home_number: '0',
    home_state: 'SP', practice_street: 'Local profissional demonstrativo', practice_phone: 'DEMO',
    include_workplace_on_documents: true, council_name_other: 'Conselho demonstrativo',
    council_state_other: 'Região demonstrativa' };
  const state = { user, error: '', success: '', fail }, calls = [];
  const ctx = vm.createContext({ console, usuario: user, id: String(user.id), contaAdministrativa: role === 'admin',
    salvamentoEmCurso: {current:false},
    propriaConta: self, outroAdministrador: role === 'admin' && !self,
    setSalvando: value => { state.busy = value; }, setErro: value => { state.error = value; },
    setMensagem: value => { state.success = value; },
    setUsuario: value => { state.user = typeof value === 'function' ? value(state.user) : value; },
    api: {
      get: async path => { calls.push({ method: 'GET', path }); return latest; },
      patch: async (path, body) => {
        calls.push({ method: 'PATCH', path, body });
        if (state.fail) throw vm.runInContext('new ApiError(422, "Título profissional: Forma de tratamento inválida.")', ctx);
        return { ...latest, ...body, cpf: user.cpf };
      },
    } });
  vm.runInContext(errorCode + '\n' + helpers + '\n' + save, ctx);
  return { state, calls, ctx, run: () => vm.runInContext('salvar()', ctx) };
}

test('self-admin saves professional fields through exact PATCH /auth/me and preserves unexposed latest fields', async () => {
  const h = harness(); await h.run();
  assert.deepEqual(h.calls.map(({method,path}) => [method,path]), [['GET','/auth/me'],['PATCH','/auth/me']]);
  const payload = h.calls[1].body;
  for (const protectedField of ['id','role','email','is_active','tipo_acesso','convidado','investidor','cpf','birth_date']) {
    assert(!Object.hasOwn(payload, protectedField), protectedField);
  }
  assert.equal(payload.home_street, 'Rua de Demonstração');
  assert.equal(payload.practice_phone, 'DEMO');
  assert.equal(payload.include_workplace_on_documents, true);
  assert.equal(payload.specialty, 'Especialidade demonstrativa');
  assert.equal(payload.workplace_notes, 'Rascunho profissional');
  assert.equal(payload.council_name_other, null);
  assert.equal(h.state.user.role, 'admin');
  assert.match(h.state.success, /profissionais foram atualizados/);
  assert.equal(h.state.busy, false);
});

test('failed self update retains all draft edits, no success, then retry reconciles the response', async () => {
  const h = harness({ fail: true }); const original = h.state.user;
  await h.run(); assert.equal(h.state.user, original); assert.equal(h.state.success, '');
  assert.match(h.state.error, /^Título profissional:/); assert.equal(h.state.busy, false);
  h.state.fail = false; await h.run();
  assert.equal(h.state.error, ''); assert(h.state.success);
  assert.equal(h.state.user.workplace_notes, 'Rascunho profissional');
});

test('same-frame double activation schedules only one save', async () => {
  const h = harness(); await Promise.all([h.run(), h.run()]);
  assert.equal(h.calls.filter(call => call.method === 'PATCH').length, 1);
  assert.equal(h.ctx.salvamentoEmCurso.current, false);
});

test('another administrator and changed session can never reach a profile mutation', async () => {
  for (const options of [{ self:false }, { sessionId:99002 }]) {
    const h = harness(options); await h.run();
    assert.equal(h.calls.filter(call => call.method === 'PATCH').length, 0);
    assert(h.state.error); assert.equal(h.state.success, '');
  }
});

test('ordinary account management keeps its administrative endpoint and fields', async () => {
  const h = harness({ self:false, role:'medico' }); await h.run();
  assert.equal(h.calls.length, 1); assert.equal(h.calls[0].method, 'PATCH');
  assert.equal(h.calls[0].path, '/admin/user-management/99001');
  assert.equal(h.calls[0].body.role, 'medico'); assert.equal(h.calls[0].body.tipo_acesso, 'normal');
});

test('UI explicitly displays and locks governance for admin, with a route to own complete profile', () => {
  for (const name of ['E-mail de login', 'CPF', 'Data de nascimento', 'Perfil', 'Tipo de acesso']) {
    assert(page.includes(`aria-label="${name}" disabled={contaAdministrativa}`), name);
  }
  assert.match(page, /type="checkbox" disabled=\{contaAdministrativa\}/);
  assert.match(page, /option value="admin">Administrador — protegido/);
  assert.match(page, /Link to="\/minha-conta"/);
  assert.match(page, /disabled=\{salvando \|\| outroAdministrador\}/);
});

function errorHarness(status, detail) {
  const redirects = [];
  const ctx = vm.createContext({ Response, Headers, FormData, BASE:'/api',
    fetch: async () => new Response(JSON.stringify({detail}), {status,headers:{'Content-Type':'application/json'}}),
    redirecionarSessaoExpirada: () => redirects.push('expired'),
    window: {location:{pathname:'/admin/usuarios/99001/gerenciar',assign:path => redirects.push(path)}} });
  vm.runInContext(errorCode + '\n' + transform(section(apiSource, 'async function request<T>', '// Contrato de paginação')), ctx);
  return { redirects, request: () => vm.runInContext('request("/fixture")', ctx) };
}

test('422 identifies known fields but never echoes arbitrary validator messages, input, ctx or location keys', async () => {
  const h = errorHarness(422, [
    {loc:['body','professional_title'],msg:'Value error, Forma de tratamento inválida.',input:'SECRET_INPUT',ctx:{value:'SECRET_CTX'}},
    {loc:['body','email'],msg:'Value error, rejected SECRET_EMAIL'},
    {loc:['query','SECRET_QUERY_KEY'],msg:'invalid SECRET_QUERY_VALUE',input:'SECRET_QUERY_INPUT'},
    {loc:['body','council_state'],msg:'String should have at most 2 characters'},
  ]);
  await assert.rejects(h.request(), error => {
    assert.equal(error.status, 422); assert.match(error.message, /Título profissional: Forma de tratamento inválida/);
    assert.match(error.message, /E-mail: Valor inválido/); assert.match(error.message, /UF do conselho: Informe no máximo 2 caracteres/);
    assert(!error.message.includes('SECRET')); return true;
  });
});

for (const [status, detail, expected] of [
  [401,'not displayed','Sessão expirada.'], [403,'Acesso não autorizado.','Acesso não autorizado.'],
  [409,'Já existe uma conta com este e-mail.','Já existe uma conta com este e-mail.'],
  [422,'CPF já cadastrado não pode ser alterado por aqui.','CPF já cadastrado não pode ser alterado por aqui.'],
  [500,null,'Não foi possível concluir a solicitação.'],
  [500,'Serviço temporariamente indisponível.','Serviço temporariamente indisponível.'],
]) test(`HTTP ${status} preserves established string/fallback and session handling: ${String(detail)}`, async () => {
  const h = errorHarness(status, detail);
  await assert.rejects(h.request(), error => error.status === status && error.message === expected);
  assert.deepEqual(h.redirects, status === 401 ? ['expired'] : []);
});

test('existing structured errors and malformed validation lists retain their supported behavior', async () => {
  for (const [detail, expected] of [
    [{erro:'Revisão necessária',campos:[{campo:'Conselho',erro:'Obrigatório'}],bloqueios:['Sem aprovação']}, /Revisão necessária.*Conselho: Obrigatório.*Sem aprovação/],
    [[{unknown:'SECRET'}], /^Não foi possível concluir a solicitação\.$/],
  ]) await assert.rejects(errorHarness(422,detail).request(), error => expected.test(error.message));
});
