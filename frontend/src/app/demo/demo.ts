import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../features/auth/auth-service';
import { DEMO_COURSES } from './demo-data';
import { DemoState } from './demo-state';
import { Demand } from './demand';
import { Eligibility } from '../features/academic/eligibility';
import { Academic } from '../features/academic/academic';
import { Selection } from '../features/academic/selection';
import { Home } from '../features/home/home';

@Component({
  selector: 'app-demo',
  imports: [
    FormsModule,
    RouterLink,
    RouterLinkActive,
    Home,
    Demand,
    Academic,
    Eligibility,
    Selection,
  ],
  templateUrl: './demo.html',
})
export class Demo {
  readonly auth = inject(AuthService);
  constructor() {
    void this.auth.refresh();
  }
  readonly state = inject(DemoState);
  readonly path = inject(ActivatedRoute).snapshot.routeConfig?.path ?? '';
  readonly tabs = [
    { path: '/', title: 'Inicio' },
    { path: '/seleccion', title: 'Selección' },
    { path: '/mi-seleccion', title: 'Mi selección' },
    { path: '/historial', title: 'Historial' },
    { path: '/mi-perfil-academico', title: 'Perfil académico' },
    { path: '/asignaturas-habilitadas', title: 'Habilitadas' },
    { path: '/demanda', title: 'Demanda' },
  ];
  readonly sideLinks = [
    { path: '/mi-perfil-academico', title: 'Mi perfil académico' },
    { path: '/asignaturas-habilitadas', title: 'Asignaturas habilitadas' },
    { path: '/mi-seleccion', title: 'Mi selección' },
  ];
  readonly courses = DEMO_COURSES;
  readonly title = this.tabs.find((tab) => tab.path === '/' + this.path)?.title ?? 'Inicio';
  query = '';
  level = 'Todos';
  menuOpen = false;
  get filtered() {
    return this.courses.filter(
      (c) =>
        (c.name + ' ' + c.id).toLowerCase().includes(this.query.toLowerCase()) &&
        (this.level === 'Todos' || c.level === +this.level),
    );
  }
}
