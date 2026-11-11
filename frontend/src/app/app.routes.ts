import { Routes } from '@angular/router';
import { Demo } from './demo/demo';
export const routes: Routes = [
  { path: '', component: Demo, pathMatch: 'full' },
  ...['seleccion', 'mi-seleccion', 'historial', 'demanda'].map((path) => ({
    path,
    component: Demo,
  })),
  { path: '**', redirectTo: '' },
];
