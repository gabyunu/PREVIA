import { DatePipe } from '@angular/common';
import { Component, effect, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../auth/auth-service';

interface Version {
  id: number;
  numero: number;
  malla_id: number;
  revision_perfil_id: number;
  creado_en: string;
  enviado_en: string | null;
  tipo: string;
  estado: string;
  vigente: boolean;
  numero_asignaturas: number;
  eventos: { tipo: string; registrado_en: string }[];
}
interface Principal {
  id: number;
  periodo: string;
  estado: string;
  creado_en: string;
  enviado_en: string | null;
  version_vigente_id: number | null;
  version_trabajo_id: number | null;
  version: Version;
}
interface Page<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}
interface Versions extends Page<Version> {
  solicitud: Principal;
}
interface Detail {
  solicitud: Principal;
  version: Version;
  selecciones: {
    malla_asignatura_id: number;
    nombre: string;
    semestre_curricular: number;
    prioridad: string;
  }[];
}

@Component({
  selector: 'app-history',
  imports: [DatePipe, RouterLink],
  templateUrl: './history.html',
})
export class History {
  readonly auth = inject(AuthService);
  readonly page = signal<Page<Principal> | null>(null);
  readonly versions = signal<Versions | null>(null);
  readonly detail = signal<Detail | null>(null);
  readonly error = signal('');
  readonly loading = signal(false);
  private generation = 0;
  constructor() {
    effect(() => {
      const user = this.auth.user();
      ++this.generation;
      this.page.set(null);
      this.versions.set(null);
      this.detail.set(null);
      this.error.set('');
      this.loading.set(false);
      if (user) void this.load();
    });
  }
  label(value: string) {
    const labels: Record<string, string> = {
      borrador: 'Borrador',
      enviada: 'Enviada',
      invalidada: 'Invalidada',
      vigente: 'Vigente',
      borrador_actual: 'Borrador actual',
      sustituida: 'Sustituida',
      envio: 'Envío',
      fundamento_actualizado: 'Fundamento actualizado',
      invalidacion: 'Invalidación',
      alta: 'Alta',
      media: 'Media',
      baja: 'Baja',
    };
    return labels[value] ?? value;
  }
  utc(value: string | null) {
    return value ? value + 'Z' : null;
  }
  private async read<T>(path: string, apply: (data: T) => void) {
    const generation = ++this.generation;
    this.error.set('');
    this.loading.set(true);
    try {
      const data = await this.auth.call<T>(path);
      if (generation === this.generation) apply(data);
    } catch (error) {
      if (generation === this.generation)
        this.error.set(
          error instanceof Error ? error.message : 'No se pudo consultar el historial.',
        );
    } finally {
      if (generation === this.generation) this.loading.set(false);
    }
  }
  async load(offset = 0) {
    this.page.set(null);
    this.versions.set(null);
    this.detail.set(null);
    await this.read<Page<Principal>>(`/me/request-history?offset=${offset}&limit=10`, (data) =>
      this.page.set(data),
    );
  }
  async open(id: number, offset = 0) {
    this.versions.set(null);
    this.detail.set(null);
    await this.read<Versions>(
      `/me/request-history/${id}/versions?offset=${offset}&limit=10`,
      (data) => this.versions.set(data),
    );
  }
  async inspect(id: number, version: number) {
    this.detail.set(null);
    await this.read<Detail>(`/me/request-history/${id}/versions/${version}`, (data) =>
      this.detail.set(data),
    );
  }
}
