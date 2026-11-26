import { Routes } from '@angular/router';
import { Demo } from './demo/demo';
import { studentOnly, adminOnly } from './features/auth/role-guards';

export const routes: Routes = [
  { path: '', component: Demo, pathMatch: 'full' },
  ...[
    'inicio-estudiante', 'seleccion', 'mi-seleccion', 'historial',
    'mi-perfil-academico', 'asignaturas-habilitadas',
  ].map((path) => ({ path, component: Demo, canActivate: [studentOnly] })),
  ...['panel-administrador', 'demanda', 'planificacion'].map((path) => ({
    path, component: Demo, canActivate: [adminOnly],
  })),
  { path: 'acceso-estudiante', loadComponent: () => import('./features/auth/auth').then((m) => m.Auth) },
  { path: 'acceso-administrador', loadComponent: () => import('./features/auth/auth').then((m) => m.Auth) },
  { path: 'iniciar-sesion', redirectTo: 'acceso-estudiante' },
  { path: 'crear-cuenta', redirectTo: 'acceso-estudiante' },
  { path: '**', redirectTo: '' },
];
