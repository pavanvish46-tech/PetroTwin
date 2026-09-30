"""Small runtime schema guard for the SIH 26120 prototype.

The prototype originally used SQLAlchemy ``create_all`` only.  That creates new
columns but does not alter an existing Neon/PostgreSQL table.  This guard keeps
existing demo databases compatible without requiring a destructive reset.
For production, replace this with Alembic migrations.
"""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


# Existing databases seen during prototype integration were missing one or
# more columns from the alerts table.  All of these columns are nullable so
# adding them is safe for pre-existing rows.
_ALERT_COLUMNS = {
    "well_id": "VARCHAR(40)",
    "severity": "VARCHAR(20)",
    "alert_type": "VARCHAR(50)",
    "message": "TEXT",
    "value": "DOUBLE PRECISION",
    "acknowledged": "BOOLEAN DEFAULT FALSE",
    "created_at": "TIMESTAMP WITH TIME ZONE",
}


def ensure_runtime_schema(engine: Engine) -> None:
    """Create missing prototype columns without deleting existing data."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    # Base.metadata.create_all() must run before this function.
    if "alerts" not in tables:
        return

    existing = {c["name"] for c in inspector.get_columns("alerts")}
    dialect = engine.dialect.name

    with engine.begin() as conn:
        for name, sql_type in _ALERT_COLUMNS.items():
            if name in existing:
                continue
            # SQLite accepts the same common ALTER TABLE form. PostgreSQL does
            # too; the timestamp type is adjusted for SQLite below.
            actual_type = sql_type
            if dialect == "sqlite":
                actual_type = {
                    "DOUBLE PRECISION": "REAL",
                    "BOOLEAN DEFAULT FALSE": "BOOLEAN DEFAULT 0",
                    "TIMESTAMP WITH TIME ZONE": "DATETIME",
                }.get(sql_type, sql_type)
            conn.execute(text(f'ALTER TABLE alerts ADD COLUMN "{name}" {actual_type}'))

        # Helpful lookup index for the alerts endpoint. Ignore duplicate/index
        # syntax differences by using the dialect's safe IF NOT EXISTS form.
        if dialect == "postgresql":
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_alerts_well_id ON alerts (well_id)"))
        elif dialect == "sqlite":
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_alerts_well_id ON alerts (well_id)"))
