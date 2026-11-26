# PREVIA — Final Term Project Report (Database Systems)

**University:** Yachay Tech University  
**Course:** Database Systems  
**Team members:** [Complete both names]  
**Date:** November 23, 2026  
**Project:** PREVIA — Provisional Academic Demand Planning

## 1. Problem and objective

The university would benefit from knowing which courses students intend to take in the next academic term. PREVIA is a local academic prototype that allows students to declare their academic progress, review eligible courses, express preferences using priorities, and submit a versioned academic-demand request. Administrators can review aggregate demand and manage **non-binding planning estimates**. PREVIA is **not an enrollment system**, does not reserve places, and does not use verified institutional records.

## 2. Relational database design

The project contains **24 tables** in one shared SQLAlchemy relational metadata model, implemented on MySQL 8.4. Representative groups:

- **Curriculum:** `carrera`, `version_malla`, `asignatura`, `malla_asignatura`, `prerrequisito`.
- **Identity/security:** `usuario`, `rol`, `usuario_rol`, `desafio_otp`, `sesion`, `limite_auth`, `evento_seguridad`.
- **Academic declarations:** `perfil_estudiante`, `revision_perfil`, `estado_academico_declarado`.
- **Requests/history:** `solicitud`, `version_solicitud`, `detalle_solicitud`, `evento_solicitud`.
- **Term and reports:** `periodo_academico`, `planificacion_cupos`, `nota_administrativa`.

The pilot curriculum contains **53 provisional courses over 10 semesters**, with **34 proposed internal prerequisite relationships**. The curriculum is not an official institutional source. The full ER diagram is in `database/er_diagram.svg` / `.pdf`, and the schema SQL is in `database/schema_mysql.sql`.

### Integrity and normalization

Tables have primary and foreign keys, unique constraints, and checks on statuses and quantities. Course identity is normalized away from student selections. Composite FKs preserve consistency between selected courses and the curriculum revision. The student request/version/detail design retains immutable past submissions instead of overwriting history. `NULL` planned capacity means **unknown**, while 0 means **zero**; these values cannot be conflated.

## 3. Database implementation

MySQL runs in Docker Desktop with a development database `previa_dev` bound only to `127.0.0.1:3307`. Alembic migrations build the official project schema and a seed script loads the pilot catalog. Mailpit, on `127.0.0.1:8025`, receives test OTP messages. `database/schema_mysql.sql` is a stand-alone DDL export intended for explaining the design or creating a **new empty** MySQL schema; **do not run it against an Alembic-migrated database**.

## 4. Flask API design and CRUD

The final-project API is served from `backend/app/flask_api.py` by **Flask**, using **Flask-SQLAlchemy** with the same SQLAlchemy metadata managed by Alembic. The existing academic/authentication/request domain functions are exposed through Flask HTTP adapters; the repository retains FastAPI imports in legacy domain handlers and `app/main.py` for previous tests. The server invoked by Windows scripts is **Flask**, not FastAPI. This is an **incremental migration**, not a wholesale elimination of FastAPI internals.

A native Flask-SQLAlchemy model and Blueprint implement full **Create, Read, Update, Delete** on `planificacion_cupos`:

| HTTP method | Endpoint | Purpose | Access |
|---|---|---|---|
| `POST` | `/api/v1/admin/planning` | Create a capacity record | Admin + CSRF |
| `GET` | `/api/v1/admin/planning` | List records | Admin |
| `GET` | `/api/v1/admin/planning/{item_id}` | Read a record | Admin |
| `PUT` | `/api/v1/admin/planning/{item_id}` | Update estimated capacity | Admin + CSRF |
| `DELETE` | `/api/v1/admin/planning/{item_id}` | Delete an unreferenced planning record | Admin + CSRF |
| `GET` | `/api/v1/admin/planning/catalog` | List available periods and courses | Admin |

`POST` rejects duplicate `(periodo_id, malla_asignatura_id)` pairs; values less than zero are invalid; deletion of a record referenced by administrative notes is blocked by FK integrity. Students cannot access the administrative CRUD endpoints. Existing student APIs support login, profile revisions, eligibility, drafts, submissions, and read-only version history. **Historical submissions are deliberately not physically deletable.**

API documentation: `docs/openapi.json`, `docs/PREVIA_Postman_Collection.json`, and `/docs` (Swagger UI, requires internet for browser assets). JSON responses use HTTP status codes such as 200, 201, 204, 401, 403, 409 and 422.

## 5. GUI design and API integration

The Angular 22 frontend retains the university-inspired blue academic UI. Students can authenticate with OTP, declare statuses by semester, review prerequisite eligibility, select up to seven courses (maximum **three high** and **four medium/low**), submit drafts, and review immutable history. An administrator sees the new **Administración · CRUD** section, which uses authenticated JSON HTTP requests to perform full CRUD on `planificacion_cupos` and visibly refreshes the MySQL data. The demand tab includes filters, priority breakdowns, CSV export, and an explicitly separate synthetic demonstration.

The new CRUD GUI is in `frontend/src/app/features/admin/planning.ts`. It uses HTML labels, accessible tables, numeric validation feedback, and a confirmation before deletion. In the real browser, test both desktop and narrow windows before declaring responsive behavior fully verified.

## 6. Reporting and data interpretation

An isolated synthetic-data generator covers **3,000 generated student records**, **504 participants**, and **1,065 course selections** among **35 courses with demand**, distributed as **507 high**, **397 medium**, and **161 low** priorities. These are *not actual university students*, are not official statistics, and do not represent simultaneous users. The real administrative report derives from current submitted versions stored in MySQL, not from the synthetic fixture.

## 7. Repository and development environment

Source repository: https://github.com/gabyunu/PREVIA . The supplied ZIP contains an adapted standalone version. **It is not automatically pushed to GitHub.** A teammate must review, commit, and push the changes to the appropriate branch; no changes to the remote repository are claimed here.

Windows 11 instructions: `docs/WINDOWS_11.md` and `scripts/windows-setup.ps1`. Required programs include Git, Docker Desktop/WSL 2, Node matching Angular 22, and `uv` for Python 3.14.

## 8. Verification evidence and limitations

- In this adapted package, Python syntax compilation succeeds.
- A local run of the **legacy tests that do not require MySQL** yielded **1 passed and 81 skipped**. Skipped tests do not prove correctness.
- Historical project records reported 82 successful backend tests in an isolated MySQL test database at checkpoint H07. These are **not** proof that the newly adapted Flask version passed 82 tests.
- New isolated Flask CRUD tests were added in `backend/tests/test_flask_final.py`; they still need to be run on the Windows 11 laptop, because Flask packages could not be downloaded in the present authoring environment.
- MySQL integration, OTP, and full Angular GUI behavior on Windows 11 have **not yet been executed and verified** in the new environment.
- The final API retains legacy FastAPI handler imports as a compatibility bridge. Replacing this bridge with idiomatic Flask blueprints throughout would be a further maintenance improvement.

## 9. Demonstration plan (15 minutes)

1. **0:00–1:00:** problem statement, goals, local-only pilot.
2. **1:00–3:30:** ER diagram, PKs/FKs, relation between request, version, and detail.
3. **3:30–5:00:** DBeaver schema, query examples, MySQL persistence and constraints.
4. **5:00–6:30:** Flask, Flask-SQLAlchemy and the REST routes in Swagger.
5. **6:30–9:30:** full CRUD from the admin GUI; verify each operation in MySQL.
6. **9:30–12:30:** student workflow: OTP, declared profile, eligible courses, draft, submit, history.
7. **12:30–14:00:** demand report and synthetic data caveat.
8. **14:00–15:00:** test results, repo, caveats and future work.

## 10. Future enhancements

Confirm the curriculum with official records; perform end-to-end tests and concurrency tests on MySQL; audit auth and CSRF; deploy with a production WSGI server behind HTTPS; improve accessibility and responsive testing; separate all remaining handler implementations from the old FastAPI layer.

**Conclusion:** PREVIA provides a credible relational database case study with MySQL schema, SQL scripts, ER diagrams, Flask-served API, native Flask-SQLAlchemy CRUD, Angular screens, report generation, and reproducible Windows setup, subject to the stated testing and integration limits.
