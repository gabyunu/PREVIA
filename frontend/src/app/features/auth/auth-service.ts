import { Injectable, signal } from '@angular/core';

export interface AuthUser {
  id: number;
  correo: string;
  roles: string[];
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly user = signal<AuthUser | null>(null);
  readonly message = signal('');
  private csrf = '';
  private readonly api = 'http://127.0.0.1:8000/api/v1';

  async call<T>(path: string, body?: unknown): Promise<T> {
    let response: Response;
    try {
      response = await fetch(this.api + path, {
        method: body === undefined ? 'GET' : 'POST',
        credentials: 'include',
        headers:
          body === undefined
            ? {}
            : {
                'Content-Type': 'application/json',
                'X-CSRF-Token': this.csrf || this.csrfCookie(),
              },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
    } catch {
      throw new Error('No se pudo conectar con PREVIA. Comprueba que la API local esté iniciada.');
    }
    if (!response.ok) {
      const data = await response.json().catch(() => null);
      if (response.status === 401 && path !== '/auth/otp/verify') this.user.set(null);
      const retry = response.headers.get('Retry-After');
      throw new Error(
        (data?.error?.mensaje ?? 'No se pudo completar la operación.') +
          (retry ? ` Reintenta en ${retry} segundos.` : ''),
      );
    }
    return response.status === 204 ? (undefined as T) : response.json();
  }

  private csrfCookie() {
    return (
      document.cookie
        .split('; ')
        .find((c) => c.startsWith('previa_csrf='))
        ?.split('=')[1] ?? ''
    );
  }

  async refresh() {
    try {
      this.user.set(await this.call<AuthUser>('/me'));
    } catch (error) {
      this.user.set(null);
      this.message.set(error instanceof Error ? error.message : 'Sesión no disponible.');
    }
  }

  async verify(desafio_id: string, codigo: string) {
    const result = await this.call<{ usuario: AuthUser; csrf_token: string }>('/auth/otp/verify', {
      desafio_id,
      codigo,
    });
    this.csrf = result.csrf_token;
    this.user.set(result.usuario);
    this.message.set(
      'Sesión iniciada. El perfil académico todavía está pendiente de implementación.',
    );
  }

  async logout() {
    try {
      await this.call('/auth/logout', {});
      this.csrf = '';
      this.user.set(null);
      this.message.set('Sesión cerrada.');
    } catch (error) {
      this.message.set(error instanceof Error ? error.message : 'No se pudo cerrar sesión.');
    }
  }
}
