// Ejecutar tras compilar demand-demo.ts y demand-catalog.ts a /tmp/previa-h01-c.
const assert = require('node:assert/strict');
const {report, REQUESTS, groupSize, csvReport} = require('/tmp/previa-h01-c/demand-demo.js');
const {PILOT_CATALOG} = require('/tmp/previa-h01-c/demand-catalog.js');
const f = {query:'', semester:'', priority:'', order:'descending'};
const all = report(f);
assert.equal(PILOT_CATALOG.length,53);
const expected = new Map();
for (const req of REQUESTS) {
  if (req.state !== 'enviada' || !req.current) continue;
  assert(req.selections.length <= 7);
  assert(req.selections.filter(s => s.priority === 'Alta').length <= 3);
  assert(req.selections.filter(s => s.priority !== 'Alta').length <= 4);
  for (const s of req.selections) {
    const c = PILOT_CATALOG.find(c => c.id_referencia === s.course);
    assert(!c.revision_pendiente && c.demostracion_elegibilidad_calculable);
    assert(!req.approved.includes(c.id_referencia));
    assert(c.prerrequisitos_ids.every(id => req.approved.includes(id)));
    expected.set(req.student + ':' + s.course, s);
  }
}
assert.equal(all.total,expected.size);
assert.equal(all.students,new Set([...expected.keys()].map(k => k.split(':')[0])).size);
assert.equal(all.semesters.reduce((n,s) => n+s.total,0),all.total);
for (const r of all.rows) {
  assert.equal(r.total,r.high+r.medium+r.low);
  assert(r.repeated <= r.total);
  assert.equal(r.highPercent,r.total ? r.high/r.total*100 : 0);
  if (r.course.revision_pendiente) assert.equal(r.total,0);
}
assert.deepEqual(report(f,[...REQUESTS,...REQUESTS]),all);
assert.equal(report(f,REQUESTS.filter(r => r.state !== 'enviada' || !r.current)).total,0);
const broken = {...REQUESTS[0], approved:[], selections:[{course:'P02-01',priority:'Alta',failed:false}]};
assert.equal(report(f,[broken]).total,0);
for (const priority of ['Alta','Media','Baja']) {
  const subset = report({...f,priority});
  assert.equal(subset.total,all.rows.reduce((n,r) => n + r[{Alta:'high',Media:'medium',Baja:'low'}[priority]],0));
}
for (let s=1;s<=10;s++) assert.equal(report({...f,semester:String(s)}).total,all.semesters[s-1].total);
assert.equal(report({...f,query:'no existe'}).students,0);
assert.equal(report({...f,query:'no existe'}).total,0);
assert.deepEqual(report({...f,order:'ascending'}).rows.map(r=>r.total),all.rows.map(r=>r.total).sort((a,b)=>a-b));
for (const v of [null,'',0,-1,1.5,Infinity,NaN]) assert.equal(groupSize(v),null);
assert.equal(groupSize(30),30);
assert.equal(Math.ceil(31/groupSize(30)),2);
const csv = csvReport(all,30,f);
assert(csv.startsWith('\uFEFF'));
assert.equal(csv.split('\r\n').length,54);
assert(!csv.includes('sintetico-'));
assert(csv.includes('grupos_orientativos'));
assert(csvReport(report({...f,query:'=1'}),null,{...f,query:'=1'}).includes('generado_utc'));
console.log(JSON.stringify({asignaturas:all.rows.length,estudiantes:all.students,intenciones:all.total,conDemanda:all.demanded,altas:all.rows.reduce((n,r)=>n+r.high,0),medias:all.rows.reduce((n,r)=>n+r.medium,0),bajas:all.rows.reduce((n,r)=>n+r.low,0),repeticion:all.rows.reduce((n,r)=>n+r.repeated,0)}));
console.log('OK: fixture, prerrequisitos, exclusiones, deduplicación, filtros, orden, porcentajes, semestres, grupos y CSV.');
