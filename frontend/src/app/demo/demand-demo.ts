import { PILOT_CATALOG } from './demand-catalog';

export const PERIOD = 'DEMO / SIGUIENTE PERÍODO';
export const VERSION = 'piloto-propuesta-53';
export type Priority = 'Alta' | 'Media' | 'Baja';
export interface RequestDemo {
  student: string;
  state: 'enviada' | 'borrador' | 'retirada' | 'invalidada';
  current: boolean;
  approved: string[];
  selections: { course: string; priority: Priority; failed: boolean }[];
}
// Fixture determinista aislado de DemoState y de cualquier futura API.
export const REQUESTS: RequestDemo[] = Array.from({ length: 96 }, (_, i) => {
  const candidates = PILOT_CATALOG.filter(c => c.demostracion_elegibilidad_calculable && !c.revision_pendiente);
  const chosen = [candidates[i % candidates.length], candidates[(i + 1) % candidates.length]];
  const approved: string[] = [...new Set(chosen.flatMap(c => [...c.prerrequisitos_ids]))];
  return {
    student: `sintetico-${i + 1}`,
    state: i >= 84 ? (['borrador', 'retirada', 'invalidada'] as const)[i % 3] : 'enviada',
    current: i < 80 || i >= 84,
    approved,
    selections: chosen.filter(c => !approved.includes(c.id_referencia)).map((c, j) => ({
      course: c.id_referencia, priority: (['Alta', 'Media', 'Baja'] as const)[(i + j) % 3], failed: (i + j) % 4 === 0,
    })),
  };
});

// Comprobación ilustrativa del fixture; no sustituye validaciones futuras del backend.
function validRequest(request: RequestDemo) {
  const high = request.selections.filter(s => s.priority === 'Alta').length;
  return request.selections.length > 0 && high <= 3 && request.selections.length - high <= 4 &&
    request.selections.every(selection => {
      const course = PILOT_CATALOG.find(c => c.id_referencia === selection.course);
      return course && ['Alta', 'Media', 'Baja'].includes(selection.priority) &&
        !course.revision_pendiente && course.demostracion_elegibilidad_calculable &&
        !request.approved.includes(course.id_referencia) &&
        course.prerrequisitos_ids.every(id => request.approved.includes(id));
    });
}

export interface Filters { query: string; semester: string; priority: string; order: string }
export function report(filters: Filters, requests: RequestDemo[] = REQUESTS) {
  const rows = PILOT_CATALOG.filter(c =>
    (c.asignatura + ' ' + c.id_referencia).toLocaleLowerCase().includes(filters.query.trim().toLocaleLowerCase()) &&
    (!filters.semester || c.semestre_curricular === Number(filters.semester)),
  ).map(course => {
    const people = new Map<string, { priority: Priority; failed: boolean }>();
    for (const request of requests.filter(validRequest)) {
      if (request.state !== 'enviada' || !request.current || course.revision_pendiente ||
          !course.demostracion_elegibilidad_calculable || request.approved.includes(course.id_referencia) ||
          !course.prerrequisitos_ids.every(id => request.approved.includes(id))) continue;
      for (const selection of request.selections) {
        if (selection.course === course.id_referencia && (!filters.priority || selection.priority === filters.priority)) {
          people.set(request.student, selection);
        }
      }
    }
    const values = [...people.values()];
    const high = values.filter(v => v.priority === 'Alta').length;
    return { course, people: [...people.keys()], total: people.size, high,
      medium: values.filter(v => v.priority === 'Media').length,
      low: values.filter(v => v.priority === 'Baja').length,
      repeated: values.filter(v => v.failed).length,
      highPercent: people.size ? high / people.size * 100 : 0 };
  });
  rows.sort((a, b) => filters.order === 'name' ? a.course.asignatura.localeCompare(b.course.asignatura, 'es') :
    filters.order === 'semester' ? a.course.semestre_curricular - b.course.semestre_curricular || a.course.id_referencia.localeCompare(b.course.id_referencia) :
    (filters.order === 'ascending' ? a.total - b.total : b.total - a.total) || a.course.id_referencia.localeCompare(b.course.id_referencia));
  const total = rows.reduce((n, r) => n + r.total, 0);
  return { rows, total, students: new Set(rows.flatMap(r => r.people)).size,
    demanded: rows.filter(r => r.total > 0).length,
    leaders: rows.filter(r => r.total > 0 && r.total === Math.max(...rows.map(r => r.total))).map(r => r.course.asignatura),
    semesters: Array.from({ length: 10 }, (_, i) => ({ semester: i + 1,
      total: rows.filter(r => r.course.semestre_curricular === i + 1).reduce((n, r) => n + r.total, 0),
      students: new Set(rows.filter(r => r.course.semestre_curricular === i + 1).flatMap(r => r.people)).size,
    })).filter(r => !filters.semester || r.semester === Number(filters.semester)) };
}
export function groupSize(value: unknown): number | null {
  const n = Number(value);
  return Number.isSafeInteger(n) && n > 0 ? n : null;
}
export function csvReport(result: ReturnType<typeof report>, size: number | null, filters: Filters) {
  const cell = (value: unknown) => {
    let text = String(value ?? '');
    if (/^[\s]*[=+@-]/.test(text)) text = "'" + text;
    return '"' + text.replaceAll('"', '""') + '"';
  };
  const generated = new Date().toISOString();
  return '\uFEFF' + [
    ['tipo_datos','periodo','version','generado_utc','busqueda','filtro_semestre','filtro_prioridad','orden','id_temporal','asignatura','semestre','total','alta','media','baja','repeticion_declarada','porcentaje_alta','tamano_grupo_simulado','grupos_orientativos','condicion','prerrequisitos_propuestos'],
    ...result.rows.map(r => ['SINTETICOS; no acredita elegibilidad ni cupos', PERIOD, VERSION, generated, filters.query, filters.semester, filters.priority, filters.order,
      r.course.id_referencia, r.course.asignatura, r.course.semestre_curricular, r.total, r.high, r.medium, r.low, r.repeated,
      r.highPercent.toFixed(2), size, size ? Math.ceil(r.total / size) : '', r.course.revision_pendiente ? 'Pendiente de verificar; excluida del conteo' : 'Propuesta no oficial; autodeclaracion sintetica', r.course.prerrequisito_texto_original]),
  ].map(row => row.map(cell).join(',')).join('\r\n');
}
