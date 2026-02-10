"""
module for export data from and _the_ PostgreSQL database to .txt, .csv, .json
   
"""


import psycopg
from sqlalchemy import create_engine
import pandas as pd
from pathlib import Path
from psycopg import sql

from audit_log import Audit
from auxiliary_functions import _read_int, _exports_dir


DB_NAME = "Moj_sklad.DB"
DB_USER = "postgres"
DB_PASSWORD = "0123"
DB_HOST = "localhost"
DB_PORT = 5432


# ------------------------------
# Export / import
# ------------------------------

class ExportData:
    """Export data from DB to CSV/JSON/TXT."""

    TABLES = {1: "products", 2: "categories", 3: "suppliers"}

    def __init__(self, conn: psycopg.Connection, audit: Audit) -> None:
        self.conn = conn
        self.audit = audit
        self.engine = create_engine(
            f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        )

    def export_to_csv(self) -> Path:
        """Export vybranej tabuľky do CSV (do ./exports)."""
        for k, name in self.TABLES.items():
            print(f"{k}. {name}")

        choice = _read_int("Vyber tabuľku na export do CSV: ")
        table = self.TABLES.get(choice)
        if not table:
            raise ValueError("Neplatná voľba tabuľky.")

        out_path = _exports_dir() / f"{table}.csv"
        df = pd.read_sql_query(f"SELECT * FROM {table};", self.conn)
        df.to_csv(out_path, index=False, sep=";", encoding="utf-8-sig")

        print(f"Export hotový: {out_path}")
        self.audit.write_log(f"[EXPORT] {table} -> CSV ({out_path.name})")
        return out_path

    # backward-compatible názvy (pôvodný kód volal export_to_CSV)
    def export_to_CSV(self) -> Path:  # noqa: N802
        return self.export_to_csv()

    def export_to_json(self) -> Path:
        """Export vybranej tabuľky do JSON (do ./exports)."""
        for k, name in self.TABLES.items():
            print(f"{k}. {name}")

        choice = _read_int("Vyber tabuľku na export do JSON: ")
        table = self.TABLES.get(choice)
        if not table:
            raise ValueError("Neplatná voľba tabuľky.")

        out_path = _exports_dir() / f"{table}.json"
        df = pd.read_sql(f"SELECT * FROM {table};", self.engine)
        df.to_json(out_path, orient="records", force_ascii=False, date_format="iso", default_handler=str)

        print(f"Export hotový: {out_path}")
        self.audit.write_log(f"[EXPORT] {table} -> JSON ({out_path.name})")
        return out_path

    def export_to_JSON(self) -> Path:  # noqa: N802
        return self.export_to_json()

    def export_txt(self) -> Path:
        """Export vybranej tabuľky do TXT (do ./exports)."""
        for k, name in self.TABLES.items():
            print(f"{k}. {name}")

        choice = _read_int("Vyber tabuľku na export do TXT: ")
        table = self.TABLES.get(choice)
        if not table:
            raise ValueError("Neplatná voľba tabuľky.")

        out_path = _exports_dir() / f"{table}.txt"
        with self.conn.cursor() as cur:
            cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table)))
            rows = cur.fetchall()

        with out_path.open("w", encoding="utf-8") as f:
            f.write(f"Zoznam {table}:\n")
            for row in rows:
                f.write(str(row) + "\n")

        print(f"Export hotový: {out_path}")
        self.audit.write_log(f"[EXPORT] {table} -> TXT ({out_path.name})")
        return out_path
