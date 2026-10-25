"""Validación de calidad de datos. Errores detienen el ETL; advertencias se registran en la auditoría."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


class ETLValidationError(Exception):
    """El dataset no cumple las reglas mínimas para cargarse."""


@dataclass
class ValidationReport:
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errores


def _bloques_nulos(df: pd.DataFrame, fecha: str, col: str) -> str:
    """Describe los tramos consecutivos de nulos, ej. '48 meses (2001-01 a 2004-12)'."""
    mask = df[col].isna().to_numpy()
    fechas = df[fecha].reset_index(drop=True)
    tramos, i = [], 0
    while i < len(mask):
        if mask[i]:
            j = i
            while j + 1 < len(mask) and mask[j + 1]:
                j += 1
            tramos.append(f"{fechas[i]:%Y-%m} a {fechas[j]:%Y-%m}")
            i = j + 1
        else:
            i += 1
    return f"{int(mask.sum())} meses ({'; '.join(tramos)})"


def validate(df: pd.DataFrame, cfg: dict) -> ValidationReport:
    e = cfg["etl"]
    fecha, base, sec = e["columna_fecha"], e["columnas_base"], e["columnas_sectoriales"]
    rep = ValidationReport()

    faltantes = [c for c in [fecha, *base, *sec] if c not in df.columns]
    if faltantes:
        rep.errores.append(f"Columnas obligatorias ausentes: {faltantes}")
        return rep  # sin las columnas no se pueden aplicar el resto de las reglas

    # ---- fechas ----
    if df[fecha].isna().any():
        rep.errores.append(f"{int(df[fecha].isna().sum())} fechas no se pudieron interpretar")
        return rep
    if df[fecha].duplicated().any():
        rep.errores.append(f"Fechas duplicadas: {df.loc[df[fecha].duplicated(), fecha].dt.date.tolist()[:5]}")
    if not (df[fecha].dt.day == 1).all():
        rep.errores.append("Hay fechas que no son el primer día del mes (se esperaba serie mensual)")
    esperado = pd.date_range(df[fecha].min(), df[fecha].max(), freq="MS")
    huecos = esperado.difference(df[fecha])
    if len(huecos):
        rep.errores.append(f"Meses faltantes en la serie: {[d.date().isoformat() for d in huecos[:5]]}")

    # ---- columnas base: obligatorias, sin nulos, no negativas ----
    for c in base:
        if not pd.api.types.is_numeric_dtype(df[c]):
            rep.errores.append(f"{c} no es numérica")
            continue
        if df[c].isna().any():
            rep.errores.append(f"{c} tiene {int(df[c].isna().sum())} nulos y es obligatoria")
    for c in [*base, *sec]:
        if pd.api.types.is_numeric_dtype(df[c]) and (df[c] < 0).any():
            rep.errores.append(f"{c} tiene valores negativos")

    lo, hi = e["rango_temperatura"]
    t = df["temperatura_promedio"]
    if ((t < lo) | (t > hi)).any():
        rep.errores.append(f"temperatura_promedio fuera de [{lo}, {hi}] °C")

    # ---- sectores: todo o nada por fila, y deben sumar el total ----
    n_nulos_fila = df[sec].isna().sum(axis=1)
    if ((n_nulos_fila > 0) & (n_nulos_fila < len(sec))).any():
        rep.errores.append("Hay filas con sectores parcialmente nulos (deben estar los 3 o ninguno)")
    completas = n_nulos_fila == 0
    if completas.any():
        suma = df.loc[completas, sec].sum(axis=1)
        rel = (suma - df.loc[completas, "demanda_total"]).abs() / df.loc[completas, "demanda_total"]
        malas = int((rel > e["tolerancia_suma_sectores"]).sum())
        if malas:
            rep.errores.append(f"{malas} filas donde la suma de sectores no coincide con demanda_total")

    # ---- advertencias (esperadas / informativas) ----
    if df[sec[0]].isna().any():
        rep.advertencias.append("Demanda sectorial ausente en " + _bloques_nulos(df, fecha, sec[0]))
    dist = [c for c in df.columns if c not in [fecha, *base, *sec]]
    if dist:
        d0 = dist[0]
        if df[d0].isna().any():
            rep.advertencias.append("Distribuidoras ausentes en " + _bloques_nulos(df, fecha, d0))
        con = df[dist].notna().all(axis=1)
        if con.any():
            cob = (df.loc[con, dist].sum(axis=1) / df.loc[con, "demanda_total"]).mean()
            rep.advertencias.append(
                f"Las distribuidoras cubren en promedio {cob:.1%} de demanda_total (no suman el 100 %); "
                "no se usan para reconstruir el total"
            )
    z = (df["demanda_total"] - df["demanda_total"].mean()) / df["demanda_total"].std()
    n_out = int((z.abs() > e["z_outlier"]).sum())
    if n_out:
        rep.advertencias.append(f"{n_out} valores de demanda_total con |z| > {e['z_outlier']}")
    return rep


def assert_valid(df: pd.DataFrame, cfg: dict) -> ValidationReport:
    rep = validate(df, cfg)
    if not rep.ok:
        raise ETLValidationError("; ".join(rep.errores))
    return rep
