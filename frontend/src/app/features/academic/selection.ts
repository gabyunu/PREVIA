import { Component, effect, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../auth/auth-service';

import { Choice, Priority, validPriorities } from './selection-rules';
interface Subject {
  malla_asignatura_id: number;
  nombre: string;
  semestre_curricular: number;
  seleccionable: boolean;
  motivos: { mensaje: string }[];
}
interface Period {
  id: number;
  identificador: string;
  captura_abierta: boolean;
}
interface Saved {
  revision_control: number;
  trabajo: { selecciones: Choice[] };
}

@Component({
  selector: 'app-selection',
  imports: [FormsModule, RouterLink],
  templateUrl: './selection.html',
})
export class Selection {
  readonly auth = inject(AuthService);
  readonly subjects = signal<Subject[]>([]);
  readonly periods = signal<Period[]>([]);
  readonly choices = signal<Choice[]>([]);
  readonly message = signal('');
  readonly busy = signal(false);
  readonly ready = signal(false);
  periodId = 0;
  revision = 0;
  profileRevision = 0;
  query = '';
  private generation = 0;
  constructor() {
    effect(() => {
      const user = this.auth.user();
      ++this.generation;
      this.subjects.set([]);
      this.choices.set([]);
      this.periods.set([]);
      this.periodId = 0;
      this.revision = 0;
      this.message.set('');
      if (user) void this.load();
    });
  }
  get rows() {
    return this.subjects().filter((s) => s.nombre.toLowerCase().includes(this.query.toLowerCase()));
  }
  get selected() {
    return this.choices().map((c) => ({
      ...c,
      subject: this.subjects().find((s) => s.malla_asignatura_id === c.malla_asignatura_id),
    }));
  }
  get open() {
    return this.periods().some((p) => p.id === +this.periodId && p.captura_abierta);
  }
  priority(id: number) {
    return this.choices().find((c) => c.malla_asignatura_id === id)?.prioridad ?? '';
  }
  change(id: number, priority: string) {
    const subject = this.subjects().find((s) => s.malla_asignatura_id === id);
    if (priority && !subject?.seleccionable) return;
    const next = this.choices().filter((c) => c.malla_asignatura_id !== id);
    if (priority) next.push({ malla_asignatura_id: id, prioridad: priority as Priority });
    if (!validPriorities(next)) {
      this.message.set('Máximo 3 altas y 4 medias/bajas; 7 en total.');
      return;
    }
    this.choices.set(next);
    this.message.set('Cambios sin guardar.');
  }
  async load() {
    const generation = ++this.generation;
    this.ready.set(false);
    this.busy.set(true);
    this.message.set('');
    this.choices.set([]);
    try {
      const [eligibility, periods] = await Promise.all([
        this.auth.call<{ materias: Subject[]; revision_perfil: number }>('/me/eligibility'),
        this.auth.call<Period[]>('/periods'),
      ]);
      if (generation !== this.generation) return;
      this.subjects.set(eligibility.materias);
      this.profileRevision = eligibility.revision_perfil;
      this.periods.set(periods);
      if (!periods.some((p) => p.id === +this.periodId))
        this.periodId = (periods.find((p) => p.captura_abierta) ?? periods[0])?.id ?? 0;
      this.revision = 0;
      if (this.periodId) {
        // GET distingue explícitamente ausencia de borrador de otros errores.
        const saved = await this.auth.call<Saved | null>(
          `/me/requests/${this.periodId}?allow_empty=true`,
        );
        if (generation !== this.generation) return;
        if (saved) {
          this.revision = saved.revision_control;
          this.choices.set(saved.trabajo.selecciones);
        }
      } else
        this.message.set('No hay período publicado. Configura uno de DEMOSTRACIÓN en desarrollo.');
      this.ready.set(true);
    } catch (error) {
      if (generation === this.generation)
        this.message.set(error instanceof Error ? error.message : 'No se pudo cargar.');
    } finally {
      if (generation === this.generation) this.busy.set(false);
    }
  }
  async save() {
    if (!this.ready() || this.busy() || !this.open || !validPriorities(this.choices())) return;
    const generation = this.generation;
    this.busy.set(true);
    this.message.set('');
    try {
      const saved = await this.auth.call<Saved>(
        `/me/requests/${this.periodId}/draft`,
        {
          revision_esperada: this.revision,
          revision_perfil: this.profileRevision,
          selecciones: this.choices(),
        },
        'PUT',
      );
      if (generation !== this.generation) return;
      this.revision = saved.revision_control;
      this.choices.set(saved.trabajo.selecciones);
      this.message.set('Borrador guardado.');
    } catch (error) {
      if (generation === this.generation)
        this.message.set(error instanceof Error ? error.message : 'No se pudo guardar.');
    } finally {
      if (generation === this.generation) this.busy.set(false);
    }
  }
}
