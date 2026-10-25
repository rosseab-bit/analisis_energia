"""E — Extracción: lee el CSV crudo sin transformar valores."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


def sha256_file(path: str | Path) -> str:
    """Huella del archivo de origen (queda en etl_auditoria para trazabilidad)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract(csv_path: str | Path, cfg: dict) -> pd.DataFrame:
    """Lee el CSV, normaliza nombres de columnas y parsea la fecha. No imputa ni descarta nada."""
    df = pd.read_csv(csv_path, encoding="utf-8")
    df.columns = [str(c).strip().lower() for c in df.columns]
    fecha = cfg["etl"]["columna_fecha"]
    if fecha not in df.columns:
        raise ValueError(f"El CSV no tiene la columna de fecha '{fecha}'. Columnas: {list(df.columns)[:5]}...")
    df[fecha] = pd.to_datetime(df[fecha], errors="coerce")
    return df
