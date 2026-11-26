import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../auth/auth-service';

interface PlanningRow {
  id: number;
  periodo_id: number;
  malla_asignatura_id: number;
  cupos_planificados: number | null;
  actualizado_en: string | null;
}
interface Catalog {
  periodos: { id: number; identificador: string }[];
  asignaturas: {
    id: number;
    codigo_publicado: string | null;
    nombre_publicado: string;
    semestre_curricular: number;
  }[];
}

@Component({
  selector: 'app-admin-planning',
  imports: [FormsModule],
  template: `
    <section class="admin-planning" aria-label="CRUD de planificación de cupos">
      <p class="notice">
        <strong>Administración · Operaciones CRUD de MySQL.</strong>
        Los cupos son orientativos y no representan plazas disponibles ni reservas oficiales.
      </p>
      @if (!auth.user()?.roles?.includes('administrador')) {
        <p class="notice" role="alert">Acceso exclusivo de administración. Inicia sesión con una cuenta autorizada.</p>
      } @else {
        <h2>Planificación de cupos por asignatura</h2>
        <p>Crear, consultar, actualizar y eliminar registros de planificación. El historial académico no se elimina.</p>
        <div class="controls">
          <label>Período académico
            <select [(ngModel)]="periodId" name="period">
              @for (p of catalog.periodos; track p.id) {
                <option [ngValue]="p.id">{{ p.identificador }}</option>
              }
            </select>
          </label>
          <label>Asignatura
            <select [(ngModel)]="courseId" name="course">
              @for (c of catalog.asignaturas; track c.id) {
                <option [ngValue]="c.id">{{ c.nombre_publicado }} · Sem. {{ c.semestre_curricular }}</option>
              }
            </select>
          </label>
          <label>Cupos orientativos
            <input type="number" min="0" max="1000000" [(ngModel)]="capacity" name="capacity" placeholder="Sin dato" />
          </label>
          <button type="button" [disabled]="busy || !periodId || !courseId" (click)="create()">Crear registro</button>
          <button type="button" [disabled]="busy" (click)="load()">Actualizar listado</button>
        </div>
        @if (message) { <p class="notice" role="status">{{ message }}</p> }
        <div class="table-scroll">
          <table>
            <caption>Registros guardados en MySQL (máximo 500)</caption>
            <thead><tr>
              <th scope="col">ID</th><th scope="col">Período</th><th scope="col">Asignatura</th>
              <th scope="col">Cupos</th><th scope="col">Acciones</th>
            </tr></thead>
            <tbody>
              @for (item of records; track item.id) {
                <tr>
                  <td>{{ item.id }}</td>
                  <td>{{ periodName(item.periodo_id) }}</td>
                  <td>{{ courseName(item.malla_asignatura_id) }}</td>
                  <td><input type="number" min="0" max="1000000" [(ngModel)]="item.cupos_planificados" [name]="'capacity-' + item.id" aria-label="Cupos planificados" placeholder="Desconocido" /></td>
                  <td>
                    <button type="button" [disabled]="busy" (click)="update(item)">Guardar</button>
                    <button type="button" [disabled]="busy" (click)="remove(item)">Eliminar</button>
                  </td>
                </tr>
              } @empty {
                <tr><td colspan="5">Todavía no hay registros de planificación.</td></tr>
              }
            </tbody>
          </table>
        </div>
      }
    </section>
  `,
  styles: [`
    .admin-planning { max-width: 100%; }
    .controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: end; margin: 16px 0; }
    .controls label { display: flex; flex-direction: column; gap: 4px; min-width: 180px; flex: 1; }
    input,select { max-width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #a8b4c2; }
    button { padding: 8px 12px; margin: 3px; cursor: pointer; }
    .table-scroll { max-width: 100%; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; }
    th,td { text-align:left; padding: 8px; border-bottom: 1px solid #ccd8e1; }
    caption { text-align: left; padding: 8px; }
  `],
})
export class AdminPlanning implements OnInit {
  readonly auth = inject(AuthService);
  private readonly cdr = inject(ChangeDetectorRef);
  catalog: Catalog = { periodos: [], asignaturas: [] };
  records: PlanningRow[] = [];
  periodId: number | null = null;
  courseId: number | null = null;
  capacity: number | null = null;
  message = '';
  busy = false;

  ngOnInit() { void this.initialize(); }
  async initialize() {
    await this.auth.refresh();
    if (!this.auth.user()?.roles?.includes('administrador')) { this.cdr.markForCheck(); return; }
    try {
      this.catalog = await this.auth.call<Catalog>('/admin/planning/catalog');
      this.periodId = this.catalog.periodos[0]?.id ?? null;
      this.courseId = this.catalog.asignaturas[0]?.id ?? null;
      await this.load();
    } catch (error) { this.showError(error); }
    finally { this.cdr.markForCheck(); }
  }
  periodName(id: number): string {
    return this.catalog.periodos.find((p) => p.id === id)?.identificador ?? String(id);
  }
  courseName(id: number): string {
    return this.catalog.asignaturas.find((c) => c.id === id)?.nombre_publicado ?? String(id);
  }
  showError(error: unknown) { this.message = error instanceof Error ? error.message : 'Operación no disponible.'; }
  async load() {
    try { const result = await this.auth.call<{ items: PlanningRow[] }>('/admin/planning'); this.records = result.items; }
    catch (error) { this.showError(error); }
    finally { this.cdr.markForCheck(); }
  }
  async create() {
    if (!this.periodId || !this.courseId || this.busy) return;
    this.busy = true; this.message = '';
    try {
      await this.auth.call('/admin/planning', {
        periodo_id: this.periodId, malla_asignatura_id: this.courseId,
        cupos_planificados: this.capacity == null ? null : Number(this.capacity),
      }, 'POST');
      await this.load(); this.message = 'Registro creado correctamente.';
    } catch (error) { this.showError(error); }
    finally { this.busy = false; this.cdr.markForCheck(); }
  }
  async update(row: PlanningRow) {
    this.busy = true; this.message = '';
    try {
      await this.auth.call(`/admin/planning/${row.id}`, {
        cupos_planificados: row.cupos_planificados == null ? null : Number(row.cupos_planificados),
      }, 'PUT');
      await this.load(); this.message = 'Registro actualizado.';
    } catch (error) { this.showError(error); }
    finally { this.busy = false; this.cdr.markForCheck(); }
  }
  async remove(row: PlanningRow) {
    if (!window.confirm('¿Eliminar esta planificación de prueba? Esta acción no borra solicitudes académicas.')) return;
    this.busy = true; this.message = '';
    try {
      await this.auth.call(`/admin/planning/${row.id}`, undefined, 'DELETE');
      await this.load(); this.message = 'Registro eliminado.';
    } catch (error) { this.showError(error); }
    finally { this.busy = false; this.cdr.markForCheck(); }
  }
}
