import { Injectable, signal } from '@angular/core';
import { DEMO_COURSES, Priority } from './demo-data';

// Estado efímero para presentar la interfaz. No guarda ni envía solicitudes.
@Injectable({ providedIn: 'root' })
export class DemoState {
  readonly selection = signal<Record<string, Priority>>({});
  readonly events = signal<string[]>([]);
  message = '';
  get chosen() {
    return DEMO_COURSES.filter((c) => this.selection()[c.id]);
  }
  get credits() {
    return this.chosen.reduce((sum, c) => sum + c.credits, 0);
  }
  get high() {
    return Object.values(this.selection()).filter((p) => p === 'Alta').length;
  }
  get additional() {
    return this.chosen.length - this.high;
  }
  toggle(id: string) {
    if (this.selection()[id]) {
      const next = { ...this.selection() };
      delete next[id];
      this.selection.set(next);
      this.record('Asignatura quitada: ' + id);
    } else if (DEMO_COURSES.some((c) => c.id === id && c.available)) {
      if (this.additional >= 4) {
        this.message =
          'Demostración: máximo cuatro prioridades medias/bajas. Puedes cambiar una prioridad a alta.';
        return;
      }
      this.selection.update((current) => ({ ...current, [id]: 'Media' }));
      this.record('Asignatura agregada: ' + id);
    }
  }
  priority(id: string, value: Priority) {
    if (!['Alta', 'Media', 'Baja'].includes(value) || !this.selection()[id]) return;
    const next = { ...this.selection(), [id]: value };
    const high = Object.values(next).filter((p) => p === 'Alta').length;
    if (high > 3 || Object.keys(next).length - high > 4) {
      this.message = 'Demostración: hasta tres altas y cuatro adicionales medias/bajas.';
      return;
    }
    this.selection.set(next);
    this.record('Prioridad de ' + id + ': ' + value);
  }
  review() {
    this.message =
      'Vista previa de ' +
      this.chosen.length +
      ' asignaturas. No se ha guardado ni enviado ninguna solicitud. Los datos se pierden al recargar.';
  }
  private record(event: string) {
    this.message = 'Cambio de demostración en memoria; no modifica solicitudes ni reportes.';
    this.events.update((events) => [event + ' · demostración', ...events]);
  }
}
