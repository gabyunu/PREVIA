# PREVIA: 15-minute database-focused oral presentation

This outline corresponds to the actual adapted project. Only claim a verification passed if you have executed it on the Windows 11 laptop.

| Slide | Presenter | Time | What to demonstrate or say |
|---|---|---:|---|
| 1. Introduction | A | 0:45 | Course demand intention; not enrollment or seat reservation. |
| 2. ER design | A | 2:00 | Show `database/er_diagram.pdf` and explain PK, FK, 24 tables. |
| 3. Request history | A | 1:30 | Show `solicitud → version_solicitud → detalle_solicitud`; why versions are immutable. |
| 4. MySQL implementation | A | 1:30 | DBeaver, `previa_dev`, constraints, one read-only query. |
| 5. API architecture | A | 1:15 | Angular → Flask + Flask-SQLAlchemy → MySQL; compatibility layer described. |
| 6. Full CRUD | B | 2:30 | Administrative GUI creates/reads/updates/deletes `planificacion_cupos`. |
| 7. Student GUI | B | 1:30 | OTP, academic profile, eligible courses. |
| 8. Persistent requests | B | 1:30 | Save draft, submit, history, reload to prove persistence. |
| 9. Reports | B | 1:30 | MySQL report, CSV export, synthetic stats clearly labeled. |
| 10. Testing and conclusions | B | 1:00 | Explain executed tests vs pending, GitHub and limitations. |

**Key questions to prepare:**
- What makes the database relational? PK, FK, UNIQUE, CHECK, 1:N links.
- Which table does CRUD operate on? `planificacion_cupos`, not historical requests.
- How does the API communicate with MySQL? Flask-SQLAlchemy managed engine and SQLAlchemy ORM/Core.
- Why distinguish `NULL` capacity from `0`? Unknown vs none planned.
- Why preserve request versions? Integrity, auditability and reproducible demand statistics.
- Are the 3,000 students real? No: completely synthetic fixture.
- Did you fully rewrite all internal handlers in Flask? No: Flask is the server and the native CRUD uses Flask-SQLAlchemy; remaining legacy domain handlers use an adapter.
- How many new tests passed? Do not assert until running `scripts/windows-tests.ps1` on the laptop.
