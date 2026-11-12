const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const signal = (value) => Object.assign(() => value, { set: (next) => (value = next) });
let effect,
  pending = [],
  calls = [];
const auth = {
  user: signal({ id: 1 }),
  call: (path) => {
    calls.push(path);
    return new Promise((resolve, reject) => pending.push({ resolve, reject }));
  },
};
const context = {
  exports: {},
  Error,
  require: (name) =>
    name === '@angular/core'
      ? {
          Component: () => (target) => target,
          effect: (fn) => {
            effect = fn;
          },
          inject: () => auth,
          signal,
        }
      : {},
};
vm.runInNewContext(
  ts.transpileModule(fs.readFileSync('src/app/features/academic/history.ts', 'utf8'), {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      experimentalDecorators: true,
    },
  }).outputText,
  context,
);
(async () => {
  const component = new context.exports.History();
  let task = component.load(10);
  assert.equal(calls.at(-1), '/me/request-history?offset=10&limit=10');
  pending.shift().resolve({ items: [{ id: 1 }], total: 11 });
  await task;
  assert.equal(component.page().total, 11);
  task = component.open(1, 10);
  assert.equal(calls.at(-1), '/me/request-history/1/versions?offset=10&limit=10');
  pending.shift().resolve({ items: [{ id: 5 }], solicitud: { id: 1 } });
  await task;
  task = component.inspect(1, 5);
  assert.equal(calls.at(-1), '/me/request-history/1/versions/5');
  pending.shift().resolve({ version: { id: 5 }, selecciones: [{ prioridad: 'media' }] });
  await task;
  assert.equal(component.detail().selecciones[0].prioridad, 'media');
  const stale = component.inspect(1, 2),
    recent = component.inspect(1, 3);
  pending.pop().resolve({ version: { id: 3 } });
  await recent;
  pending.shift().resolve({ version: { id: 2 } });
  await stale;
  assert.equal(component.detail().version.id, 3);
  task = component.inspect(1, 4);
  pending.shift().reject(Error('No disponible'));
  await task;
  assert.equal(component.detail(), null);
  assert.equal(component.error(), 'No disponible');
  task = component.load();
  auth.user.set(null);
  effect();
  assert.equal(component.page(), null);
  assert.equal(component.versions(), null);
  assert.equal(component.detail(), null);
  pending.shift().resolve({ items: [{ id: 99 }] });
  await task;
  assert.equal(component.page(), null);
  auth.user.set({ id: 2 });
  effect();
  pending.shift().resolve({ items: [] });
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(component.page().items.length, 0);
  assert.equal(component.label('sustituida'), 'Sustituida');
  assert.equal(component.utc('2026-01-01T12:00:00'), '2026-01-01T12:00:00Z');
  console.log(
    'H07: paginación, detalle, prioridades, errores, lecturas concurrentes y cambio de sesión aprobados.',
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
