import { Component, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { DEMO_COURSES } from './demo-data';
import { DemoState } from './demo-state';
import { Demand } from './demand';
import { Home } from '../features/home/home';

@Component({
  selector: 'app-demo',
  imports: [FormsModule, DecimalPipe, RouterLink, RouterLinkActive, Home, Demand],
  templateUrl: './demo.html',
})
export class Demo {
  readonly state = inject(DemoState);
  readonly path = inject(ActivatedRoute).snapshot.routeConfig?.path ?? '';
  readonly tabs = [
    { path: '/', title: 'Inicio' },
    { path: '/seleccion', title: 'Selección de asignaturas' },
    { path: '/mi-seleccion', title: 'Mi selección' },
    { path: '/historial', title: 'Historial' },
    { path: '/demanda', title: 'Demanda' },
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
