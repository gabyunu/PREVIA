import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../auth/auth-service';

interface DemandSummary {
  estudiantes: number;
  intenciones: number;
  alta: number;
  media: number;
  baja: number;
  asignaturas: number;
  filas: { nombre: string; total: number; alta: number; media: number; baja: number }[];
}
interface PlanningSummary { items: { id: number }[]; total: number; }

@Component({
  selector: 'app-admin-dashboard',
  imports: [RouterLink],
  template: `
    <section class="admin-dashboard" aria-label="Indicadores de demanda académica">
      <p class="notice">Datos agregados de intenciones de cursar materias. <strong>No son matrículas confirmadas</strong> ni cupos reservados. Solo se consideran solicitudes enviadas y vigentes en MySQL.</p>
      @if (busy) { <p role="status">Consultando MySQL...</p> }
      @if (error) { <p class="notice error" role="alert">{{ error }}</p> }
      @if (demand; as d) {
        <div class="metric-grid">
          <article><span>Estudiantes participantes</span><strong>{{ d.estudiantes }}</strong><small>Solicitudes vigentes</small></article>
          <article><span>Intenciones registradas</span><strong>{{ d.intenciones }}</strong><small>Selecciones de asignaturas</small></article>
          <article><span>Asignaturas solicitadas</span><strong>{{ d.asignaturas }}</strong><small>Con interés registrado</small></article>
          <article><span>Prioridades altas</span><strong>{{ d.alta }}</strong><small>Más {{ d.media }} medias y {{ d.baja }} bajas</small></article>
        </div>
        <h2 class="bar">Asignaturas más solicitadas <span>Datos actuales de MySQL</span></h2>
        <div class="scroll">
          <table>
            <thead><tr><th>Asignatura</th><th>Solicitudes</th><th>Alta</th><th>Media</th><th>Baja</th></tr></thead>
            <tbody>
              @for (row of topCourses; track $index) {
                <tr><td>{{ row.nombre }}</td><td><strong>{{ row.total }}</strong></td><td>{{ row.alta }}</td><td>{{ row.media }}</td><td>{{ row.baja }}</td></tr>
              } @empty {
                <tr><td colspan="5">Aún no existen solicitudes enviadas para este período de prueba.</td></tr>
              }
            </tbody>
          </table>
        </div>
      }
      <div class="admin-actions">
        <article>
          <h2>Informes de demanda</h2>
          <p>Filtra por semestre, asignatura, período y prioridad. Exporta los resultados a CSV.</p>
          <a class="button-primary" routerLink="/demanda">Ir a informes</a>
        </article>
        <article>
          <h2>Planificación de cupos</h2>
          <p>Registros orientativos guardados: <strong>{{ planningCount ?? '—' }}</strong>. Crea, edita, consulta y elimina planificaciones.</p>
          <a class="button-primary" routerLink="/planificacion">Administrar registros CRUD</a>
        </article>
      </div>
    </section>
  `,
})
export class AdminDashboard implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly change = inject(ChangeDetectorRef);
  demand: DemandSummary | null = null;
  planningCount: number | null = null;
  busy = false;
  error = '';

  get topCourses() {
    return (this.demand?.filas ?? []).slice().sort((a, b) => b.total - a.total).slice(0, 6);
  }
  ngOnInit() { void this.refresh(); }
  async refresh() {
    if (!this.auth.isAdmin()) return;
    this.busy = true;
    this.error = '';
    try {
      const [demand, planning] = await Promise.all([
        this.auth.call<DemandSummary>('/admin/demand'),
        this.auth.call<PlanningSummary>('/admin/planning'),
      ]);
      this.demand = demand;
      this.planningCount = planning.total;
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'No se pudo consultar MySQL.';
    } finally {
      this.busy = false;
      this.change.markForCheck();
    }
  }
}
