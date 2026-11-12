"""Evaluación provisional sobre una única revisión y versión curricular."""

from sqlalchemy import select

from app.db import models as m


def evaluate(conn, revision):
    version = revision["version_malla_id"]
    subjects = (
        conn.execute(
            select(m.malla_asignatura)
            .where(m.malla_asignatura.c.version_malla_id == version)
            .order_by(m.malla_asignatura.c.semestre_curricular, m.malla_asignatura.c.id)
        )
        .mappings()
        .all()
    )
    states = dict(
        conn.execute(
            select(
                m.estado_academico_declarado.c.malla_asignatura_id,
                m.estado_academico_declarado.c.estado,
            ).where(
                m.estado_academico_declarado.c.revision_perfil_id == revision["id"],
                m.estado_academico_declarado.c.version_malla_id == version,
            )
        ).all()
    )
    edges = (
        conn.execute(
            select(m.prerrequisito).where(m.prerrequisito.c.version_malla_id == version)
        )
        .mappings()
        .all()
    )
    by_catalog = {s["asignatura_id"]: s for s in subjects}
    rows = []
    for subject in subjects:
        required = []
        for edge in edges:
            if edge["asignatura_id"] != subject["asignatura_id"]:
                continue
            prerequisite = by_catalog[edge["requisito_asignatura_id"]]
            required.append(
                dict(
                    malla_asignatura_id=prerequisite["id"],
                    asignatura_id=prerequisite["asignatura_id"],
                    nombre=prerequisite["nombre_publicado"],
                    estado_declarado=states.get(prerequisite["id"]),
                )
            )
        passed = [r for r in required if r["estado_declarado"] == "aprobada"]
        pending = [r for r in required if r["estado_declarado"] != "aprobada"]
        rule = subject["estado_regla"]
        uncertain = (
            subject["revision_pendiente"]
            or bool(subject["condiciones_externas"])
            or rule
            not in (
                "ninguno_explicito_propuesto",
                "prerrequisitos_asignaturas_propuestos",
            )
            or (rule == "prerrequisitos_asignaturas_propuestos" and not required)
            or (rule == "ninguno_explicito_propuesto" and bool(required))
        )
        state = states.get(subject["id"])
        reasons = []
        if state == "aprobada":
            reasons.append(dict(codigo="ya_aprobada", mensaje="Ya declarada aprobada."))
        if uncertain:
            reasons.append(
                dict(
                    codigo="reglas_no_verificadas",
                    mensaje="Reglas pendientes de verificación.",
                )
            )
        if state is None:
            reasons.append(
                dict(
                    codigo="declaracion_incompleta",
                    mensaje="Declara el estado académico de esta asignatura.",
                )
            )
        for prerequisite in pending:
            reasons.append(
                dict(
                    codigo="prerrequisito_no_aprobado",
                    requisito_id=prerequisite["asignatura_id"],
                    mensaje=prerequisite["nombre"] + ": falta aprobación declarada.",
                )
            )
        rows.append(
            dict(
                malla_asignatura_id=subject["id"],
                asignatura_id=subject["asignatura_id"],
                nombre=subject["nombre_publicado"],
                semestre_curricular=subject["semestre_curricular"],
                estado_declarado=state,
                prerrequisitos_cumplidos=not uncertain and not pending,
                seleccionable=not reasons,
                motivos=reasons,
                prerrequisitos_requeridos=required,
                prerrequisitos_aprobados=passed,
                prerrequisitos_pendientes=pending,
                estado_regla=rule,
                condiciones_externas=subject["condiciones_externas"],
                advertencia="Reglas todavía no verificadas." if uncertain else None,
            )
        )
    return dict(
        revision_perfil=revision["numero"],
        malla_id=version,
        base_datos="AUTODECLARADA",
        materias=rows,
    )
