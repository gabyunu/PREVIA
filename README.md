# PREVIA — Proyecto final de Bases de Datos

**Versión adaptada para Windows 11.** API servida por **Flask** con integración
**Flask-SQLAlchemy**, frontend **Angular 22** y base de datos **MySQL 8.4**.

## Comenzar

- [Instalación desde cero en Windows 11](docs/WINDOWS_11.md)
- [Informe final del proyecto](docs/FINAL_PROJECT_REPORT.md)
- [Diagrama entidad-relación y scripts SQL](database/)
- [Pruebas y evidencia pendiente](docs/VERIFICATION_CHECKLIST.md)
- [Guion de exposición de 15 minutos](docs/EXPOSICION_15_MIN.md)
- [Documentación de la API OpenAPI](docs/openapi.json)
- [Colección Postman](docs/PREVIA_Postman_Collection.json)

La API nueva se ejecuta con `python -m flask --app app.flask_api:app run`.
El archivo `backend/app/main.py` mantiene el servidor FastAPI anterior
para compatibilidad de pruebas históricas; no es el punto de entrada de Windows.
Las funciones históricas siguen usando algunos tipos de FastAPI mediante un adaptador
HTTP conservador, mientras que el CRUD de administración es nativo Flask-SQLAlchemy.

**El prototipo usa malla y estados autodeclarados, no datos institucionales reales.**
No matricula estudiantes ni reserva cupos. Este ZIP no modifica GitHub ni incluye
una copia de la base de datos del equipo anterior.
