# Frontend PREVIA

Angular 22 y TypeScript. La página inicial reside en
`src/app/features/home/`; `app.routes.ts` define las rutas y `app.config.ts`
configura la aplicación. No hay integración con la API en H01.

Instalación y ejecución en Ubuntu: [guía local](../docs/local-development.md).
`npm ci` instala las versiones de `package-lock.json`; `npm start` inicia el
servidor local y `npm run build` compila en producción. H01 no incluye pruebas
unitarias frontend; la verificación disponible es la compilación.
