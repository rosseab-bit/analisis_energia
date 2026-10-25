"""Orquesta Extract → Validate → Transform → Load."""
from __future__ import annotations

from demanda.config import load_config, resolve
from demanda.etl.extract import extract, sha256_file
from demanda.etl.load import connect, init_schema, load
from demanda.etl.transform import transform
from demanda.etl.validate import assert_valid


def run_etl(config_path: str | None = None, reset: bool = False, csv_path: str | None = None,
            db_path: str | None = None) -> dict:
    """Ejecuta el ETL completo y devuelve un resumen (también útil para tests)."""
    cfg = load_config(config_path)
    csv = resolve(cfg, csv_path or cfg["rutas"]["csv_crudo"])
    db = resolve(cfg, db_path or cfg["rutas"]["base_datos"])
    schema = resolve(cfg, cfg["rutas"]["schema_sql"])

    raw = extract(csv, cfg)                       # E
    reporte = assert_valid(raw, cfg)              # V (lanza ETLValidationError si hay errores)
    datos, distribuidoras, umbrales = transform(raw, cfg)   # T

    auditoria = {
        "archivo": csv.name,
        "sha256": sha256_file(csv),
        "filas_leidas": len(raw),
        "nulos": {c: int(n) for c, n in raw.isna().sum().items() if n > 0},
        "umbrales": umbrales,
        "advertencias": reporte.advertencias,
        "config": {k: cfg[k] for k in ("semilla", "etl", "etiqueta")},
    }
    conn = connect(db)
    try:
        init_schema(conn, schema, reset=reset)    # L
        resumen = load(conn, datos, distribuidoras, auditoria)
    finally:
        conn.close()

    resumen.update(
        base_datos=str(db),
        umbrales=umbrales,
        advertencias=reporte.advertencias,
        distribucion_etiquetas=datos.groupby(["split", "etiqueta"]).size().unstack(fill_value=0).to_dict("index"),
    )
    return resumen
