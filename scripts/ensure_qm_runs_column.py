# scripts/ensure_qm_runs_column.py
from sqlalchemy import text
from ..db.database import engine

def ensure_runs_column():
    # get current database name from engine URL
    db_name = engine.url.database
    table = 'qm_balls'
    column = 'runs_scored'

    check_sql = text("""
        SELECT COUNT(*) as cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table AND COLUMN_NAME = :column
    """)
    add_sql = text(f"ALTER TABLE {table} ADD COLUMN {column} INT NOT NULL DEFAULT 0;")

    with engine.connect() as conn:
        res = conn.execute(check_sql, {"db": db_name, "table": table, "column": column})
        cnt = res.scalar() or 0
        if cnt:
            print(f"Column '{column}' already exists on {table} in database '{db_name}'.")
            return
        print(f"Adding column '{column}' to {table} in database '{db_name}'...")
        conn.execute(add_sql)
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    ensure_runs_column()