import { Component, inject, input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from './auth-service';

@Component({
  selector: 'app-auth-form',
  imports: [FormsModule, RouterLink],
  templateUrl: './auth-form.html',
  styleUrl: './auth-form.css',
})
export class AuthForm {
  readonly registration = input(false);
  readonly otpPreview = signal(false);
  readonly message = signal('');
  readonly busy = signal(false);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private challenge = '';
  email = '';
  code = '';

  async requestCode() {
    if (this.busy()) return;
    this.busy.set(true);
    this.message.set('Solicitando código…');
    try {
      const result = await this.auth.call<{ desafio_id: string; vigencia_segundos: number }>(
        '/auth/otp/request',
        { correo: this.email },
      );
      this.challenge = result.desafio_id;
      this.code = '';
      this.otpPreview.set(true);
      this.message.set(
        `Si el correo está autorizado, encontrarás el código en Mailpit. Vence en ${result.vigencia_segundos / 60} minutos.`,
      );
    } catch (error) {
      this.message.set(error instanceof Error ? error.message : 'No se pudo solicitar el código.');
    } finally {
      this.busy.set(false);
    }
  }

  async verifyCode() {
    if (this.busy()) return;
    this.busy.set(true);
    this.message.set('Verificando código…');
    try {
      await this.auth.verify(this.challenge, this.code);
      this.code = '';
      this.challenge = '';
      await this.router.navigateByUrl('/');
    } catch (error) {
      this.code = '';
      this.message.set(error instanceof Error ? error.message : 'No se pudo verificar el código.');
    } finally {
      this.busy.set(false);
    }
  }

  back() {
    this.code = '';
    this.challenge = '';
    this.message.set('');
    this.otpPreview.set(false);
  }
}
