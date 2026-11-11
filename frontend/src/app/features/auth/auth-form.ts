import { Component, input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

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
  email = '';
  code = '';

  requestCode() {
    this.message.set('No se ha enviado ningún correo. Solicitar un código requiere la futura API de autenticación.');
  }

  previewCode() {
    this.code = '';
    this.message.set('Vista previa: no hay un código enviado ni un desafío de autenticación activo.');
    this.otpPreview.set(true);
  }

  verifyCode() {
    this.code = '';
    this.message.set('No se ha verificado ningún código ni creado una sesión o cuenta. Esta acción requiere la futura API de autenticación.');
  }

  back() {
    this.code = '';
    this.message.set('');
    this.otpPreview.set(false);
  }
}
