"""OpenAPI 3.0 documentation for the Flask API (maintained with route changes)."""


def spec():
    paths = {}

    def add(path, method, summary, *, tag, body=None, params=None, result="200", responses=None):
        operation = {
            "tags": [tag],
            "summary": summary,
            "responses": {
                result: {"description": "Success", "content": {"application/json": {"schema": {"type": "object"}}}},
                "401": {"description": "Authentication required"},
                "403": {"description": "Forbidden / invalid CSRF or origin"},
                "422": {"description": "Validation error"},
            },
        }
        if params:
            operation["parameters"] = params
        if body:
            operation["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": body}},
            }
        if responses:
            operation["responses"].update(responses)
        paths.setdefault(path, {})[method.lower()] = operation

    ref = lambda name: {"$ref": f"#/components/schemas/{name}"}
    arg = lambda name: {"name": name, "in": "path", "required": True, "schema": {"type": "integer", "minimum": 1}}
    query = lambda name: {"name": name, "in": "query", "required": False, "schema": {"type": "string"}}

    add("/health", "GET", "Health check", tag="Service")
    add("/api/v1/auth/otp/request", "POST", "Send local OTP", tag="Authentication", body=ref("Email"), result="202")
    add("/api/v1/auth/otp/verify", "POST", "Verify OTP and sign in", tag="Authentication", body=ref("Verify"))
    add("/api/v1/auth/logout", "POST", "Sign out", tag="Authentication", result="204")
    add("/api/v1/me", "GET", "Current authenticated user", tag="Authentication")
    add("/api/v1/careers", "GET", "Available pilot careers", tag="Academics")
    add("/api/v1/curricula", "GET", "Curriculum versions", tag="Academics", params=[query("career_id")])
    add("/api/v1/curricula/{curriculum_id}", "GET", "Curriculum courses and prerequisites", tag="Academics", params=[arg("curriculum_id")])
    add("/api/v1/me/academic-profile", "GET", "Read own academic profile", tag="Academics")
    add("/api/v1/me/academic-profile", "PUT", "Update own academic profile", tag="Academics", body=ref("Profile"))
    add("/api/v1/me/eligibility", "GET", "Check eligible courses", tag="Academics")
    add("/api/v1/periods", "GET", "Published academic terms", tag="Requests")
    add("/api/v1/me/requests/{period_id}", "GET", "Read own draft", tag="Requests", params=[arg("period_id")])
    add("/api/v1/me/requests/{period_id}/draft", "PUT", "Create or update draft", tag="Requests", params=[arg("period_id")], body=ref("Draft"))
    add("/api/v1/me/requests/{period_id}/submit", "POST", "Submit versioned request", tag="Requests", params=[arg("period_id")], body=ref("Submit"))
    add("/api/v1/me/request-history", "GET", "Read own request history", tag="History")
    add("/api/v1/me/request-history/{request_id}/versions", "GET", "List version history", tag="History", params=[arg("request_id")])
    add("/api/v1/me/request-history/{request_id}/versions/{version_id}", "GET", "Read historical version", tag="History", params=[arg("request_id"), arg("version_id")])
    add("/api/v1/admin/demand/options", "GET", "Demand report filter choices", tag="Reports")
    add("/api/v1/admin/demand", "GET", "Admin demand (JSON or CSV)", tag="Reports", params=[query("formato"), query("periodo_id"), query("malla_id"), query("q"), query("semestre"), query("prioridad"), query("orden"), query("tamano_grupo")])
    add("/api/v1/admin/planning/catalog", "GET", "Planning form options", tag="Admin CRUD")
    add("/api/v1/admin/planning", "GET", "Read planning records", tag="Admin CRUD", params=[query("periodo_id")])
    add("/api/v1/admin/planning", "POST", "Create planned capacity", tag="Admin CRUD", body=ref("PlannedCapacityNew"), result="201", responses={"409": {"description": "Duplicate planned capacity"}})
    add("/api/v1/admin/planning/{item_id}", "GET", "Read one planned capacity", tag="Admin CRUD", params=[arg("item_id")])
    add("/api/v1/admin/planning/{item_id}", "PUT", "Update planned capacity", tag="Admin CRUD", params=[arg("item_id")], body=ref("PlannedCapacityUpdate"))
    add("/api/v1/admin/planning/{item_id}", "DELETE", "Delete unused planned capacity", tag="Admin CRUD", params=[arg("item_id")], result="204", responses={"409": {"description": "Record referenced by notes"}})
    return {
        "openapi": "3.0.3",
        "info": {"title": "PREVIA - Flask / MySQL API", "version": "1.0.0", "description": "Provisional academic planning prototype; no enrollment or seat reservation."},
        "servers": [{"url": "http://127.0.0.1:8000"}],
        "components": {
            "securitySchemes": {"CookieAuth": {"type": "apiKey", "in": "cookie", "name": "previa_session"}},
            "schemas": {
                "Email": {"type": "object", "required": ["correo"], "additionalProperties": False, "properties": {"correo": {"type": "string", "format": "email", "example": "demo@estudiantes.example.test"}}},
                "Verify": {"type": "object", "required": ["desafio_id", "codigo"], "additionalProperties": False, "properties": {"desafio_id": {"type": "string"}, "codigo": {"type": "string", "pattern": "^[0-9]{8}$"}}},
                "Profile": {"type": "object", "required": ["revision_esperada", "malla_id", "semestre_declarado", "estados"], "additionalProperties": False, "properties": {"revision_esperada": {"type": "integer", "minimum": 0}, "malla_id": {"type": "integer", "minimum": 1}, "semestre_declarado": {"type": "integer", "minimum": 1}, "estados": {"type": "array", "items": {"$ref": "#/components/schemas/State"}}}},
                "State": {"type": "object", "required": ["malla_asignatura_id", "estado"], "properties": {"malla_asignatura_id": {"type": "integer", "minimum": 1}, "estado": {"type": "string", "enum": ["aprobada", "reprobada", "no_cursada"]}}},
                "Draft": {"type": "object", "required": ["revision_esperada", "revision_perfil", "selecciones"], "properties": {"revision_esperada": {"type": "integer", "minimum": 0}, "revision_perfil": {"type": "integer", "minimum": 1}, "selecciones": {"type": "array", "maxItems": 7, "items": {"$ref": "#/components/schemas/Selection"}}}},
                "Selection": {"type": "object", "required": ["malla_asignatura_id", "prioridad"], "properties": {"malla_asignatura_id": {"type": "integer"}, "prioridad": {"type": "string", "enum": ["alta", "media", "baja"]}}},
                "Submit": {"type": "object", "required": ["revision_esperada", "revision_perfil", "version_trabajo_id"], "properties": {"revision_esperada": {"type": "integer", "minimum": 0}, "revision_perfil": {"type": "integer", "minimum": 1}, "version_trabajo_id": {"type": "integer", "minimum": 1}}},
                "PlannedCapacityNew": {"type": "object", "required": ["periodo_id", "malla_asignatura_id", "cupos_planificados"], "additionalProperties": False, "properties": {"periodo_id": {"type": "integer", "minimum": 1}, "malla_asignatura_id": {"type": "integer", "minimum": 1}, "cupos_planificados": {"type": "integer", "minimum": 0, "maximum": 1000000, "nullable": True}}},
                "PlannedCapacityUpdate": {"type": "object", "required": ["cupos_planificados"], "additionalProperties": False, "properties": {"cupos_planificados": {"type": "integer", "minimum": 0, "maximum": 1000000, "nullable": True}}},
            },
        },
        "paths": paths,
    }
