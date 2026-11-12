import { Component, effect, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../auth/auth-service';

type State = 'aprobada' | 'reprobada' | 'no_cursada';
interface Subject {
  malla_asignatura_id: number;
  codigo_publicado: string | null;
  nombre_publicado: string;
  semestre_curricular: number;
}
interface Profile {
  revision: number;
  malla_id: number | null;
  semestre_declarado: number | null;
  estados: { malla_asignatura_id: number; estado: State }[];
}
interface Curriculum {
  id: number;
  codigo_version: string;
  asignaturas: Subject[];
}

@Component({
  selector: 'app-academic',
  imports: [FormsModule, RouterLink],
  templateUrl: './academic.html',
})
export class Academic {
  readonly auth = inject(AuthService);
  readonly ready = signal(false);
  readonly busy = signal(false);
  readonly message = signal('');
  readonly error = signal('');
  curriculum: Curriculum | null = null;
  career = '';
  revision = 0;
  semester: number | null = null;
  states: Record<number, State | ''> = {};
  groups: { semester: number; subjects: Subject[] }[] = [];
  private generation = 0;

  constructor() {
    effect(() => {
      const user = this.auth.user();
      const generation = ++this.generation;
      this.ready.set(false);
      this.curriculum = null;
      this.groups = [];
      this.states = {};
      this.message.set('');
      this.error.set('');
      if (user) void this.load(generation);
    });
  }

  async load(generation = ++this.generation) {
    this.ready.set(false);
    this.error.set('');
    try {
      const [careers, versions, profile] = await Promise.all([
        this.auth.call<{ id: number; nombre: string }[]>('/careers'),
        this.auth.call<{ id: number }[]>('/curricula'),
        this.auth.call<Profile>('/me/academic-profile'),
      ]);
      if (versions.length !== 1) throw new Error('La malla piloto no está disponible.');
      const curriculum = await this.auth.call<Curriculum>('/curricula/' + versions[0].id);
      if (generation !== this.generation) return;
      this.curriculum = curriculum;
      this.career = careers[0]?.nombre ?? '';
      this.revision = profile.revision;
      this.semester = profile.semestre_declarado;
      this.states = Object.fromEntries(
        profile.estados.map((s) => [s.malla_asignatura_id, s.estado]),
      );
      this.groups = [...new Set(curriculum.asignaturas.map((s) => s.semestre_curricular))].map(
        (semester) => ({
          semester,
          subjects: curriculum.asignaturas.filter((s) => s.semestre_curricular === semester),
        }),
      );
      this.ready.set(true);
    } catch (error) {
      if (generation === this.generation) this.error.set(this.describe(error));
    }
  }

  async save() {
    if (!this.curriculum || !this.auth.user() || this.busy()) return;
    this.busy.set(true);
    this.error.set('');
    this.message.set('');
    const generation = this.generation;
    try {
      const result = await this.auth.call<Profile & { mensaje: string }>(
        '/me/academic-profile',
        {
          revision_esperada: this.revision,
          malla_id: this.curriculum.id,
          semestre_declarado: this.semester,
          estados: Object.entries(this.states)
            .filter(([, state]) => state !== '')
            .map(([id, estado]) => ({
              malla_asignatura_id: Number(id),
              estado,
            })),
        },
        'PUT',
      );
      if (generation !== this.generation) return;
      this.revision = result.revision;
      this.message.set(result.mensaje);
    } catch (error) {
      if (generation === this.generation) this.error.set(this.describe(error));
    } finally {
      this.busy.set(false);
    }
  }

  private describe(error: unknown) {
    return error instanceof Error ? error.message : 'No se pudo completar la operación.';
  }
}
