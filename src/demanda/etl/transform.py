"""T — Transformación: limpieza, features de calendario, participaciones, etiqueta y split.

Reglas de diseño (ver specs/01-datos.md):
  * Los nulos de sectores y distribuidoras NO se imputan acá: son períodos en los que el dato
    no existe (sectores desde 2005-01, distribuidoras desde 2014-01). La imputación, si hace
    falta, ocurre dentro del Pipeline de sklearn para no filtrar información entre train y test.
  * Los umbrales de la etiqueta se calculan SOLO con el período de entrenamiento.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ETIQUETAS = ["Normal", "Alta", "Crítica"]
ESTACION = {
    12: "Verano", 1: "Verano", 2: "Verano",
    3: "Otoño", 4: "Otoño", 5: "Otoño",
    6: "Invierno", 7: "Invierno", 8: "Invierno",
    9: "Primavera", 10: "Primavera", 11: "Primavera",
}  # hemisferio sur (Argentina)


def agregar_calendario(out: pd.DataFrame, fecha: pd.Series) -> pd.DataFrame:
    out["anio"] = fecha.dt.year
    out["mes"] = fecha.dt.month
    out["trimestre"] = fecha.dt.quarter
    out["estacion"] = out["mes"].map(ESTACION)
    out["mes_sin"] = np.sin(2 * np.pi * out["mes"] / 12)   # codificación cíclica: dic y ene quedan cerca
    out["mes_cos"] = np.cos(2 * np.pi * out["mes"] / 12)
    return out


def agregar_participaciones(out: pd.DataFrame, sec: list[str]) -> pd.DataFrame:
    """Participación de cada sector en la demanda (suman 1). NaN donde no hay datos sectoriales."""
    nombres = {
        "demanda_residencial": "part_residencial",
        "comercio_e_industria": "part_comercio_industria",
        "grandes_usuarios": "part_grandes_usuarios",
    }
    total = out["demanda_total"]
    for c in sec:
        out[nombres.get(c, f"part_{c}")] = out[c] / total
    out["tiene_sectores"] = out[sec].notna().all(axis=1).astype(int)
    return out


def calcular_score(demanda: pd.Series, metodo: str, ventana: int) -> pd.Series:
    """Magnitud sobre la que se fijan los umbrales de la etiqueta."""
    if metodo == "percentil_global":
        return demanda.astype(float)
    if metodo == "relativo_tendencia":
        # Media móvil centrada: aísla el pico estacional del crecimiento de largo plazo.
        tendencia = demanda.rolling(ventana, center=True, min_periods=ventana // 2).mean()
        return demanda / tendencia
    raise ValueError(f"Método de etiqueta desconocido: {metodo}")


def asignar_split(n: int, fraccion_test: float) -> np.ndarray:
    """Split cronológico: los últimos meses son test (nunca aleatorio en series temporales)."""
    corte = int(round(n * (1 - fraccion_test)))
    return np.where(np.arange(n) < corte, "train", "test")


def construir_etiqueta(score: pd.Series, split: np.ndarray, q_alta: float, q_critica: float):
    """Normal <= P(q_alta) < Alta <= P(q_critica) < Crítica, con percentiles del set de train."""
    ref = score[split == "train"]
    p_alta, p_crit = (float(x) for x in ref.quantile([q_alta, q_critica]))
    etiqueta = pd.cut(score, bins=[-np.inf, p_alta, p_crit, np.inf], labels=ETIQUETAS).astype(str)
    return etiqueta, p_alta, p_crit


def transform(raw: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Devuelve (datos_limpios, demanda_distribuidora_larga, info_umbrales)."""
    e, et = cfg["etl"], cfg["etiqueta"]
    fcol, base, sec = e["columna_fecha"], e["columnas_base"], e["columnas_sectoriales"]

    df = raw.sort_values(fcol).reset_index(drop=True)
    dist = [c for c in df.columns if c not in [fcol, *base, *sec]]

    out = pd.DataFrame({"fecha": df[fcol].dt.strftime("%Y-%m-%d")})
    out = agregar_calendario(out, df[fcol])
    for c in [*base, *sec]:
        out[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    out = agregar_participaciones(out, sec)

    score = calcular_score(out["demanda_total"], et["metodo"], et["ventana_tendencia_meses"])
    split = asignar_split(len(out), et["fraccion_test"])
    etiqueta, p_alta, p_crit = construir_etiqueta(score, split, et["q_alta"], et["q_critica"])
    out["demanda_ratio_tendencia"] = score if et["metodo"] == "relativo_tendencia" else np.nan
    out["etiqueta"] = etiqueta
    out["split"] = split

    columnas = [
        "fecha", "anio", "mes", "trimestre", "estacion", "mes_sin", "mes_cos",
        "demanda_total", *sec,
        "part_residencial", "part_comercio_industria", "part_grandes_usuarios", "tiene_sectores",
        "temperatura_promedio", "potencia_maxima", "demanda_ratio_tendencia", "etiqueta", "split",
    ]
    out = out[columnas]

    larga = (
        df[[fcol, *dist]]
        .melt(id_vars=fcol, var_name="distribuidora", value_name="demanda")
        .dropna(subset=["demanda"])
        .rename(columns={fcol: "fecha"})
    )
    larga["fecha"] = larga["fecha"].dt.strftime("%Y-%m-%d")
    larga = larga.sort_values(["fecha", "distribuidora"]).reset_index(drop=True)

    corte = out.loc[out["split"] == "train", "fecha"].iloc[-1]
    info = {
        "metodo": et["metodo"],
        "p_alta": p_alta,
        "p_critica": p_crit,
        "q_alta": et["q_alta"],
        "q_critica": et["q_critica"],
        "ventana_tendencia_meses": et["ventana_tendencia_meses"],
        "n_train": int((split == "train").sum()),
        "n_test": int((split == "test").sum()),
        "ultimo_mes_train": corte,
    }
    return out, larga, info
