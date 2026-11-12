import { Component, effect, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../auth/auth-service';

interface Prerequisite {
  malla_asignatura_id: number;
  nombre: string;
  estado_declarado: string | null;
}
interface Row {
  malla_asignatura_id: number;
  nombre: string;
  semestre_curricular: number;
  estado_declarado: string | null;
  prerrequisitos_cumplidos: boolean;
  seleccionable: boolean;
  advertencia: string | null;
  motivos: { codigo: string; mensaje: string }[];
  prerrequisitos_requeridos: Prerequisite[];
  condiciones_externas: string[];
}
interface Result {
  revision_perfil: number;
  materias: Row[];
  advertencia: string;
}

@Component({
  selector: 'app-eligibility',
  imports: [RouterLink],
  templateUrl: './eligibility.html',
})
export class Eligibility {
  readonly auth = inject(AuthService);
  readonly result = signal<Result | null>(null);
  readonly error = signal('');
  readonly loading = signal(false);
  private generation = 0;
  constructor() {
    effect(() => {
      const user = this.auth.user();
      ++this.generation;
      this.result.set(null);
      this.error.set('');
      if (user) void this.load();
    });
  }
  get groups() {
    const rows = this.result()?.materias ?? [];
    return [...new Set(rows.map((r) => r.semestre_curricular))].map((semester) => ({
      semester,
      rows: rows.filter((r) => r.semestre_curricular === semester),
    }));
  }
  stateLabel(state: string | null) {
    const labels: Record<string, string> = {
      aprobada: 'Aprobada',
      reprobada: 'Reprobada',
      no_cursada: 'No cursada',
    };
    return labels[state ?? ''] ?? 'Sin declaración';
  }
  label(row: Row) {
    if (row.estado_declarado === 'aprobada') return 'Ya aprobada';
    if (row.advertencia) return 'Bloqueada: reglas por verificar';
    if (row.seleccionable) return 'Habilitada';
    return row.motivos.some((m) => m.codigo === 'prerrequisito_no_aprobado')
      ? 'Bloqueada: prerrequisitos'
      : 'Bloqueada: falta declaración';
  }
  async load() {
    const generation = ++this.generation;
    this.result.set(null);
    this.loading.set(true);
    this.error.set('');
    try {
      const result = await this.auth.call<Result>('/me/eligibility');
      if (generation === this.generation) this.result.set(result);
    } catch (error) {
      if (generation === this.generation)
        this.error.set(
          error instanceof Error ? error.message : 'No se pudo consultar la elegibilidad.',
        );
    } finally {
      if (generation === this.generation) this.loading.set(false);
    }
  }
}
