import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../features/auth/auth-service';
import { DemandSynthetic } from './demand-synthetic';

interface Row {
  periodo_id: number;
  periodo: string;
  malla_id: number;
  malla: string;
  asignatura_id: number;
  codigo: string | null;
  nombre: string;
  semestre: number;
  total: number;
  alta: number;
  media: number;
  baja: number;
  repeticion: number;
  cupos_planificados: number | null;
  grupos: number | null;
}
interface Report {
  semestres: { semestre: number; estudiantes: number; intenciones: number }[];
  generado_en: string;
  aviso: string;
  filas: Row[];
  estudiantes: number;
  intenciones: number;
  alta: number;
  media: number;
  baja: number;
  asignaturas: number;
}
@Component({
  selector: 'app-demand',
  imports: [FormsModule, DemandSynthetic],
  templateUrl: './demand.html',
})
export class Demand implements OnInit {
  readonly auth = inject(AuthService);
  private readonly view = inject(ChangeDetectorRef);
  demonstration = false;
  options: {
    periodos: { id: number; identificador: string }[];
    mallas: { id: number; codigo_version: string }[];
  } = { periodos: [], mallas: [] };
  filters = {
    periodo_id: '',
    malla_id: '',
    q: '',
    semestre: '',
    prioridad: '',
    orden: 'descending',
    tamano_grupo: '',
  };
  data: Report | null = null;
  message = '';
  busy = false;
  private generation = 0;
  ngOnInit() {
    void this.initialize();
  }
  async initialize() {
    try {
      this.options = await this.auth.call('/admin/demand/options');
      await this.load();
    } catch (error) {
      this.message = (error as Error).message;
    } finally {
      this.view.markForCheck();
    }
  }
  params() {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(this.filters))
      if (value !== '' && value != null) params.set(key, value);
    return params.toString();
  }
  async load() {
    const generation = ++this.generation;
    this.data = null;
    this.message = '';
    this.busy = true;
    try {
      const data = await this.auth.call<Report>('/admin/demand?' + this.params());
      if (generation === this.generation) this.data = data;
    } catch (error) {
      if (generation === this.generation) this.message = (error as Error).message;
    } finally {
      if (generation === this.generation) this.busy = false;
      this.view.markForCheck();
    }
  }
  async exportCsv() {
    this.message = '';
    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/v1/admin/demand?' + this.params() + '&formato=csv',
        { credentials: 'include' },
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error?.error?.mensaje ?? 'No se pudo exportar.');
      }
      const url = URL.createObjectURL(await response.blob());
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'PREVIA-demanda.csv';
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      this.message = (error as Error).message;
    } finally {
      this.view.markForCheck();
    }
  }
}
