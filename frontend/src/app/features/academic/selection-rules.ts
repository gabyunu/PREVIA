export type Priority = 'alta' | 'media' | 'baja';
export interface Choice {
  malla_asignatura_id: number;
  prioridad: Priority;
}

export function validPriorities(choices: Choice[]) {
  const high = choices.filter((c) => c.prioridad === 'alta').length;
  return (
    high <= 3 &&
    choices.length - high <= 4 &&
    choices.length <= 7 &&
    new Set(choices.map((c) => c.malla_asignatura_id)).size === choices.length &&
    choices.every((c) => ['alta', 'media', 'baja'].includes(c.prioridad))
  );
}
