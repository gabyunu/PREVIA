import { Routes } from '@angular/router';
import { Demo } from './demo/demo';
export const routes: Routes = [
  { path: '', component: Demo, pathMatch: 'full' },
  ...[
    'seleccion',
    'mi-seleccion',
    'historial',
    'demanda',
    'mi-perfil-academico',
    'asignaturas-habilitadas',
  ].map((path) => ({
    path,
    component: Demo,
  })),
  {
    path: 'iniciar-sesion',
    loadComponent: () => import('./features/auth/auth').then((m) => m.Auth),
  },
  { path: 'crear-cuenta', loadComponent: () => import('./features/auth/auth').then((m) => m.Auth) },
  { path: '**', redirectTo: '' },
];
