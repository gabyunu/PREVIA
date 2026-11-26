import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthForm } from './auth-form';
import { AuthPresentation } from './auth-presentation';

@Component({
  selector: 'app-auth',
  imports: [RouterLink, RouterLinkActive, AuthForm, AuthPresentation],
  templateUrl: './auth.html',
  styleUrl: './auth.css',
})
export class Auth {
  readonly mode: 'administrador' | 'estudiante' =
    inject(ActivatedRoute).snapshot.routeConfig?.path === 'acceso-administrador'
      ? 'administrador' : 'estudiante';
}
