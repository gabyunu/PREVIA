import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../features/auth/auth-service';
import { Demand } from './demand';
import { Eligibility } from '../features/academic/eligibility';
import { Academic } from '../features/academic/academic';
import { Selection } from '../features/academic/selection';
import { History } from '../features/academic/history';
import { Home } from '../features/home/home';
import { AdminPlanning } from '../features/admin/planning';
import { AdminDashboard } from '../features/admin/dashboard';

@Component({
  selector: 'app-demo',
  imports: [
    RouterLink, RouterLinkActive, Home, AdminPlanning, AdminDashboard,
    History, Demand, Academic, Eligibility, Selection,
  ],
  templateUrl: './demo.html',
})
export class Demo {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  readonly path = inject(ActivatedRoute).snapshot.routeConfig?.path ?? '';
  readonly studentTabs = [
    { path: '/inicio-estudiante', title: 'Inicio' },
    { path: '/mi-perfil-academico', title: 'Mi perfil académico' },
    { path: '/asignaturas-habilitadas', title: 'Habilitadas' },
    { path: '/mi-seleccion', title: 'Mi selección' },
    { path: '/historial', title: 'Historial' },
  ];
  readonly adminTabs = [
    { path: '/panel-administrador', title: 'Panel general' },
    { path: '/demanda', title: 'Demanda de asignaturas' },
    { path: '/planificacion', title: 'Planificación · CRUD' },
  ];
  readonly title = [...this.studentTabs, ...this.adminTabs]
    .find((tab) => tab.path === '/' + this.path)?.title ?? 'Bienvenido a PREVIA';

  constructor() {
    if (!this.auth.checked()) void this.auth.refresh();
  }

  async signOut() {
    await this.auth.logout();
    await this.router.navigateByUrl('/');
  }
}
