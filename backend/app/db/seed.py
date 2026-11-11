"""Carga local transaccional. No publica mallas ni crea usuarios."""

import argparse
import hashlib
import json
from pathlib import Path

from sqlalchemy import insert, select

from app.db import models as m
from app.db.session import make_engine

SOURCE = (
    Path(__file__).resolve().parents[3]
    / "referencias/malla-piloto/PREVIA_malla_piloto_propuesta.json"
)


def load_pilot(connection, source=SOURCE):
    raw = Path(source).read_bytes()
    data = json.loads(raw)
    rows = data["asignaturas"]
    by_ref = {row["id_referencia"]: row for row in rows}
    if len(rows) != 53 or len(by_ref) != 53 or data["total_asignaturas"] != 53:
        raise ValueError("El piloto debe contener 53 identidades únicas")
    visiting, visited = set(), set()

    def visit(ref):
        if ref in visiting:
            raise ValueError("Ciclo curricular")
        if ref in visited:
            return
        visiting.add(ref)
        for target in by_ref[ref]["prerrequisitos_ids"]:
            if target not in by_ref:
                raise ValueError("Referencia interna inexistente")
            visit(target)
        visiting.remove(ref)
        visited.add(ref)

    for ref in by_ref:
        visit(ref)
    # La huella evita sobrescribir silenciosamente una carga distinta.
    code = "demo-piloto-" + hashlib.sha256(raw).hexdigest()[:16]
    career = (
        connection.execute(
            select(m.carrera).where(m.carrera.c.codigo == "DEMO-PILOTO-NO-OFICIAL")
        )
        .mappings()
        .first()
    )
    if career is None:
        career_id = connection.execute(
            insert(m.carrera).values(
                codigo="DEMO-PILOTO-NO-OFICIAL",
                nombre="Carrera piloto de demostración (nombre oficial pendiente)",
            )
        ).inserted_primary_key[0]
    else:
        career_id = career["id"]
    versions = (
        connection.execute(
            select(m.version_malla).where(m.version_malla.c.carrera_id == career_id)
        )
        .mappings()
        .all()
    )
    if versions:
        if len(versions) != 1 or versions[0]["codigo_version"] != code:
            raise ValueError(
                "La fuente cambió: requiere revisión y nueva versión explícita"
            )
        version_id = versions[0]["id"]
    else:
        version_id = connection.execute(
            insert(m.version_malla).values(carrera_id=career_id, codigo_version=code)
        ).inserted_primary_key[0]
    ids = {}

    def ensure(table, key, values):
        row = connection.execute(select(table).filter_by(**key)).mappings().first()
        if row is None:
            result = connection.execute(insert(table).values(**key, **values))
            return result.inserted_primary_key[0]
        if any(row[k] != v for k, v in values.items()):
            raise ValueError(f"Contenido divergente en {table.name}: {key}")
        return row.get("id")

    for row in rows:
        ref = row["id_referencia"]
        ids[ref] = ensure(
            m.asignatura,
            {"identificador_catalogo": "demo-piloto:" + ref},
            {"nombre": row["asignatura"]},
        )
        external = row["prerrequisitos_fuera_de_malla"]
        ensure(
            m.malla_asignatura,
            {"version_malla_id": version_id, "asignatura_id": ids[ref]},
            {
                "semestre_curricular": row["semestre_curricular"],
                "codigo_publicado": row["codigo_institucional"],
                "nombre_publicado": row["asignatura"],
                "estado_regla": row["estado_regla"],
                "revision_pendiente": row["revision_pendiente"] or bool(external),
                "prerrequisito_texto_original": row["prerrequisito_texto_original"],
                "condiciones_externas": external,
            },
        )
    expected = set()
    for row in rows:
        for target in row["prerrequisitos_ids"]:
            key = {
                "version_malla_id": version_id,
                "asignatura_id": ids[row["id_referencia"]],
                "requisito_asignatura_id": ids[target],
            }
            ensure(m.prerrequisito, key, {})
            expected.add((key["asignatura_id"], key["requisito_asignatura_id"]))
    actual = set(
        connection.execute(
            select(
                m.prerrequisito.c.asignatura_id,
                m.prerrequisito.c.requisito_asignatura_id,
            ).where(m.prerrequisito.c.version_malla_id == version_id)
        ).all()
    )
    entries = (
        connection.execute(
            select(m.malla_asignatura.c.asignatura_id).where(
                m.malla_asignatura.c.version_malla_id == version_id
            )
        )
        .scalars()
        .all()
    )
    if actual != expected or set(entries) != set(ids.values()):
        raise ValueError("La malla contiene entradas o relaciones divergentes")
    return {
        "asignaturas": len(entries),
        "prerrequisitos": len(expected),
        "reglas_pendientes": sum(
            r["revision_pendiente"] or bool(r["prerrequisitos_fuera_de_malla"])
            for r in rows
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    args = parser.parse_args()
    engine = make_engine()
    try:
        with engine.begin() as connection:
            result = load_pilot(connection, args.source)
        print(json.dumps(result))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
