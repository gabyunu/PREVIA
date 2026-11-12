const assert = require('node:assert/strict');
const { validPriorities } = require('/tmp/previa-h05a/selection-rules.js');
function choices(high, low) {
  return Array.from({length: high + low}, (_, i) => ({malla_asignatura_id: i+1, prioridad: i < high ? 'alta' : i % 2 ? 'media' : 'baja'}));
}
for (const [high, low, valid] of [[3,4,true],[0,4,true],[0,0,true],[1,6,false],[0,5,false],[4,0,false],[2,5,false],[3,5,false]])
  assert.equal(validPriorities(choices(high, low)), valid);
assert.equal(validPriorities([{malla_asignatura_id:1, prioridad:'alta'},{malla_asignatura_id:1, prioridad:'media'}]), false);
assert.equal(validPriorities([{malla_asignatura_id:1, prioridad:'urgente'}]), false);
console.log('H05-A: 10 comprobaciones de prioridades y duplicados aprobadas.');
