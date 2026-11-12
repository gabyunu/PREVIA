const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
let calls = [],
  reject = false,
  resolvePending;
const auth = {
  call: async (path) => {
    calls.push(path);
    if (reject) throw Error('Demanda requiere autorización administrativa.');
    if (path.endsWith('/options')) return { periodos: [{ id: 2 }], mallas: [{ id: 3 }] };
    if (path.includes('q=slow')) return new Promise((resolve) => (resolvePending = resolve));
    return { filas: [], estudiantes: 1, intenciones: 2 };
  },
};
let exported = '',
  csvOk = true;
const context = {
  exports: {},
  URLSearchParams,
  URL: { createObjectURL: () => 'blob:test', revokeObjectURL: () => {} },
  document: { createElement: () => ({ click() {} }) },
  fetch: async (url) => {
    exported = url;
    return {
      ok: csvOk,
      blob: async () => 'csv',
      json: async () => ({ error: { mensaje: 'Acceso denegado' } }),
    };
  },
  require: (name) =>
    name === '@angular/core'
      ? {
          ChangeDetectorRef: 'view',
          Component: () => (target) => target,
          inject: (token) => (token === 'view' ? { markForCheck() {} } : auth),
        }
      : {},
};
vm.runInNewContext(
  ts.transpileModule(fs.readFileSync('src/app/demo/demand.ts', 'utf8'), {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      experimentalDecorators: true,
    },
  }).outputText,
  context,
);
(async () => {
  const component = new context.exports.Demand();
  assert.equal(component.demonstration, false);
  await component.initialize();
  assert.equal(component.options.periodos[0].id, 2);
  assert.equal(component.data.estudiantes, 1);
  component.filters.periodo_id = '2';
  component.filters.malla_id = '3';
  component.filters.q = 'A & B';
  component.filters.prioridad = 'alta';
  await component.load();
  const params = new URLSearchParams(calls.at(-1).split('?')[1]);
  assert.equal(params.get('q'), 'A & B');
  assert.equal(params.get('malla_id'), '3');
  assert.equal(params.get('prioridad'), 'alta');
  await component.exportCsv();
  assert.equal(new URL(exported).searchParams.get('periodo_id'), '2');
  assert.equal(new URL(exported).searchParams.get('formato'), 'csv');
  csvOk = false;
  await component.exportCsv();
  assert.equal(component.message, 'Acceso denegado');
  component.filters.q = 'slow';
  const pending = component.load();
  component.filters.q = 'new';
  await component.load();
  resolvePending({ estudiantes: 99 });
  await pending;
  assert.equal(component.data.estudiantes, 1);
  reject = true;
  await component.load();
  assert.equal(component.data, null);
  assert.match(component.message, /autorización/);
  const html = fs.readFileSync('src/app/demo/demand.html', 'utf8');
  assert.match(html, /cupos_planificados \?\? 'Desconocido'/);
  assert.match(html, /<app-demand-synthetic/);
  console.log(
    'H06: fuente real, filtros, exportación, errores y respuestas concurrentes aprobados.',
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
