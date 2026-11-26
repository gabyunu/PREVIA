import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth-service';

function forRole(role: 'estudiante' | 'administrador'): CanActivateFn {
  return async () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    if (!auth.checked()) await auth.refresh();
    if (role === 'administrador' ? auth.isAdmin() : auth.isStudent()) return true;
    if (auth.isAdmin()) return router.parseUrl('/panel-administrador');
    if (auth.isStudent()) return router.parseUrl('/inicio-estudiante');
    return router.parseUrl(role === 'administrador' ? '/acceso-administrador' : '/acceso-estudiante');
  };
}

export const studentOnly = forRole('estudiante');
export const adminOnly = forRole('administrador');
