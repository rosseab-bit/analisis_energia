"""L — Carga: escribe en SQLite dentro de una única transacción."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

ETL_TABLES = ("datos_limpios", "demanda_distribuidora")
ALL_TABLES = (*ETL_TABLES, "etl_auditoria", "predicciones", "metricas_modelo", "config_modelo")


def connect(db_path: str | Path) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path))


def init_schema(conn: sqlite3.Connection, schema_path: str | Path, reset: bool = False) -> None:
    """Crea las tablas. Con reset=True borra TODAS (incluidos resultados de modelos)."""
    if reset:
        for t in ALL_TABLES:
            conn.execute(f"DROP TABLE IF EXISTS {t}")
    conn.executescript(Path(schema_path).read_text(encoding="utf-8"))


def _insert(conn: sqlite3.Connection, table: str, df: pd.DataFrame) -> int:
    cols = list(df.columns)
    rows = df.astype(object).where(df.notna(), None).values.tolist()  # NaN -> NULL
    conn.executemany(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})", rows
    )
    return len(rows)


def load(
    conn: sqlite3.Connection,
    datos_limpios: pd.DataFrame,
    distribuidoras: pd.DataFrame,
    auditoria: dict,
) -> dict:
    """Reemplaza el contenido de las tablas del ETL (idempotente) y registra la auditoría.

    No toca predicciones / metricas_modelo / config_modelo: los resultados de los modelos se conservan
    (si el ETL cambia las etiquetas, hay que volver a entrenar; ver GUIA_EQUIPO.md).
    """
    with conn:  # commit si todo sale bien, rollback ante cualquier error
        conn.execute("DELETE FROM datos_limpios")
        conn.execute("DELETE FROM demanda_distribuidora")
        n1 = _insert(conn, "datos_limpios", datos_limpios)
        n2 = _insert(conn, "demanda_distribuidora", distribuidoras)
        run_id = "etl_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # %f: dos corridas en el mismo segundo no colisionan
        conn.execute(
            "INSERT OR REPLACE INTO etl_auditoria VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                run_id,
                datetime.now().isoformat(timespec="seconds"),
                auditoria["archivo"],
                auditoria["sha256"],
                auditoria["filas_leidas"],
                n1,
                n2,
                json.dumps(auditoria["nulos"], ensure_ascii=False),
                json.dumps(auditoria["umbrales"], ensure_ascii=False),
                json.dumps(auditoria["advertencias"], ensure_ascii=False),
                json.dumps(auditoria["config"], ensure_ascii=False, default=str),
            ),
        )
    return {"etl_run_id": run_id, "filas_datos_limpios": n1, "filas_distribuidoras": n2}
