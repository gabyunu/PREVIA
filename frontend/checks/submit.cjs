const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const signal = value => Object.assign(() => value, {set: next => value = next});
let calls = [], fail = false;
const version = {id: 11, selecciones: [{malla_asignatura_id: 1, prioridad: 'media', nombre: 'DEMO', semestre_curricular: 1}]};
const saved = {estado: 'borrador', revision_control: 1, trabajo: version, vigente: null};
const auth = {user: signal({id: 1}), call: async (...args) => {
  calls.push(args);
  if (args[0].endsWith('/submit')) {if (fail) throw Error('Conexión perdida'); return {...saved, estado: 'enviada', trabajo: null, vigente: version};}
  if (args[0] === '/me/eligibility') return {materias: [{...version.selecciones[0], seleccionable: true}], revision_perfil: 1};
  if (args[0] === '/periods') return [{id: 2, identificador: 'DEMO', captura_abierta: true}];
  return saved;
}};
const context = {exports: {}, crypto: require('node:crypto').webcrypto, require: name => {
  if (name === '@angular/core') return {Component: () => target => target, effect: () => {}, inject: () => auth, signal};
  if (name.includes('selection-rules')) return {validPriorities: () => true};
  return {};
}};
const source = fs.readFileSync('src/app/features/academic/selection.ts', 'utf8');
vm.runInNewContext(ts.transpileModule(source, {compilerOptions: {target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS, experimentalDecorators: true}}).outputText, context);
(async () => {
  const component = new context.exports.Selection();
  await component.load();
  assert.equal(component.saved().trabajo.id, 11);
  await component.save();
  const put = calls.find(c => c[2] === 'PUT');
  assert.deepEqual(JSON.parse(JSON.stringify(put[1].selecciones)), [{malla_asignatura_id: 1, prioridad: 'media'}]);
  const before = calls.length;
  await component.submit();
  assert.equal(calls.length, before); // Confirmación obligatoria.
  component.confirming.set(true);
  fail = true;
  await component.submit();
  await component.submit();
  const retries = calls.filter(c => c[0].endsWith('/submit'));
  assert.equal(retries.length, 2);
  assert.equal(retries[0][3]['Idempotency-Key'], retries[1][3]['Idempotency-Key']);
  assert.deepEqual(retries[0][1], retries[1][1]);
  fail = false;
  await component.submit();
  assert.match(component.message(), /Solicitud enviada/);
  assert.equal(component.confirming(), false);
  component.confirming.set(true);
  component.dirty.set(true);
  const count = calls.length;
  await component.submit();
  assert.equal(calls.length, count);
  console.log('H05-B: 9 comprobaciones de componente, confirmación y reintentos aprobadas.');
})().catch(error => {console.error(error); process.exitCode = 1;});
