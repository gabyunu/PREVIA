"""Export an offline SQL creation script from the real PREVIA metadata.

Never run this file against a migrated production database. Use Alembic there.
"""

from pathlib import Path

from sqlalchemy.schema import AddConstraint, CreateIndex, CreateTable
from sqlalchemy.dialects import mysql

from app.db.models import Base


def export(path: Path):
    dialect = mysql.dialect()
    tables = list(Base.metadata.tables.values())
    parts = [
        "-- PREVIA MySQL 8.4: database schema derived from SQLAlchemy metadata.",
        "-- FOR AN EMPTY DEMO DATABASE ONLY. Prefer Alembic migrations for normal setup.",
        "-- No DROP / destructive statements are included.",
        "CREATE DATABASE IF NOT EXISTS `previa_dev` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs;",
        "USE `previa_dev`;",
        "",
    ]
    for table in tables:
        # Circular references are added after all tables are created.
        parts.append(str(CreateTable(table, include_foreign_key_constraints=[]).compile(dialect=dialect)).rstrip() + ";")
    parts.append("\n-- Secondary indexes")
    for table in tables:
        for index in table.indexes:
            parts.append(str(CreateIndex(index).compile(dialect=dialect)).rstrip() + ";")
    parts.append("\n-- Foreign keys (added after all referenced tables exist)")
    for table in tables:
        for fk in table.foreign_key_constraints:
            parts.append(str(AddConstraint(fk).compile(dialect=dialect)).rstrip() + ";")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"Exported {len(tables)} tables to {path}")


if __name__ == "__main__":
    export(Path(__file__).resolve().parents[2] / "database" / "schema_mysql.sql")
