"""Export Graphviz ER diagram from SQLAlchemy table metadata; run from backend/."""

from pathlib import Path
from html import escape

from app.db.models import Base

root = Path(__file__).resolve().parents[2]
lines = [
    'digraph PREVIA {',
    'graph [rankdir=LR, bgcolor="white", ranksep=1.15, nodesep=0.30, splines=polyline, pad=0.25];',
    'node [shape=plain, fontname="Arial"];',
    'edge [color="#6788a2", arrowsize=0.45, penwidth=1.0];',
]

for table in Base.metadata.tables.values():
    fk_fields = {c.name for fk in table.foreign_key_constraints for c in fk.columns}
    labels = []
    for col in table.columns:
        suffix = 'PK' if col.primary_key else ('FK' if col.name in fk_fields else '')
        color = '#e7f3fb' if suffix else '#ffffff'
        labels.append(f'<TR><TD BGCOLOR="{color}" ALIGN="LEFT"><FONT POINT-SIZE="10">{escape(col.name)} {suffix}</FONT></TD></TR>')
    body = ''.join(labels)
    label = (
        '<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" COLOR="#1b587e">'
        f'<TR><TD BGCOLOR="#1b587e"><FONT COLOR="white" POINT-SIZE="12"><B>{escape(table.name)}</B></FONT></TD></TR>'
        + body + '</TABLE>'
    )
    lines.append(f'"{table.name}" [label=<{label}>];')

for table in Base.metadata.tables.values():
    links = set()
    for fk in table.foreign_key_constraints:
        linked = fk.referred_table.name
        if linked != table.name:
            links.add(linked)
    for name in sorted(links):
        lines.append(f'"{table.name}" -> "{name}";')

lines.append('}')
file = root / 'database' / 'er_diagram.dot'
file.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(file)
