# Verificación del diccionario de datos (T-02)

Verifica cada afirmación numérica de `docs/06_datos/data_dictionary.md` contra el CSV crudo. Solo lectura: no modifica datos, código ni configuración.

- Archivo: `data/raw/demanda_electricidad_original_mensual1.csv`
- SHA-256: `b2964bd292dbde9b7b688268b04ae2f0bb783ebf0d48a87ee1d85f7b2eaf2241` (`sha256sum data/raw/demanda_electricidad_original_mensual1.csv`)
- Entorno: Python 3 con pandas 3.1.0 en un venv temporal fuera del repo (el repo aún no tiene entorno instalado en esta máquina).
- Fecha de ejecución: 2026-10-31.

## Cómo reproducir

Guardá el script de abajo como `verif_t02.py` fuera del repo (por ejemplo en `/tmp`) y ejecutá desde la raíz del repo:

```bash
python -I /tmp/verif_t02.py data/raw/demanda_electricidad_original_mensual1.csv
```

## Script

```python
"""Verificaciones T-02: cada afirmación numérica del diccionario contra el CSV crudo."""
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1], encoding="utf-8")
df["indice_tiempo"] = pd.to_datetime(df["indice_tiempo"])
sectores = ["demanda_residencial", "comercio_e_industria", "grandes_usuarios"]
base = ["demanda_total", "temperatura_promedio", "potencia_maxima"]
dist = [c for c in df.columns if c not in ["indice_tiempo"] + sectores + base]

print("== V1 estructura ==")
print("shape", df.shape, "| columnas únicas:", df.columns.is_unique)
print("rango fechas", df.indice_tiempo.min().date(), df.indice_tiempo.max().date())
print("todos día 1:", (df.indice_tiempo.dt.day == 1).all(),
      "| duplicadas:", df.indice_tiempo.duplicated().sum(),
      "| meses esperados:", len(pd.date_range("2001-01-01", "2026-08-01", freq="MS")),
      "| ordenado:", df.indice_tiempo.is_monotonic_increasing)
print("dtypes distintos de float (salvo fecha):",
      {c: str(t) for c, t in df.dtypes.items() if c != "indice_tiempo" and str(t) != "float64"})
print("grupos:", len(sectores), "sectores,", len(base), "base,", len(dist), "distribuidoras")

print("\n== V2 nulos y disponibilidad ==")
print("nulos base:", df[base].isna().sum().to_dict())
for c in sectores:
    nn = df.loc[df[c].notna(), "indice_tiempo"]
    print(c, "nulos", df[c].isna().sum(), "primero", nn.min().date(), "último", nn.max().date())
print("nulos sectores solo antes de 2005-01:",
      df.loc[df[sectores].isna().any(axis=1), "indice_tiempo"].max().date())
print("filas con los 3 sectores:", df[sectores].notna().all(axis=1).sum())
print("nulos distribuidoras total:", int(df[dist].isna().sum().sum()),
      "| por columna (únicos):", sorted(df[dist].isna().sum().unique().tolist()))
# nulos por distribuidora (para detectar columnas con huecos distintos)
nn = df[dist].notna().any(axis=1)
print("fechas con >=1 distribuidora:", df.loc[nn, "indice_tiempo"].min().date(),
      df.loc[nn, "indice_tiempo"].max().date(), "meses:", nn.sum())
print("meses con las 23 presentes:", df[dist].notna().all(axis=1).sum(),
      "| con alguna presente pero no todas:", (nn & ~df[dist].notna().all(axis=1)).sum())
print("celdas no nulas distribuidoras (filas del formato largo):", int(df[dist].notna().sum().sum()))
print("nulos 2026-07/08 en distribuidoras:",
      df.loc[df.indice_tiempo >= "2026-07-01", dist].isna().all().all())

print("\n== V3 rangos ==")
print(df[base + sectores].describe().loc[["min", "max", "mean"]].round(2).to_string())
print("negativos (todas numéricas):", int((df.drop(columns="indice_tiempo") < 0).sum().sum()))
z = (df.demanda_total - df.demanda_total.mean()) / df.demanda_total.std()
print("|z|>3 en demanda_total:", int((z.abs() > 3).sum()), "| max |z|:", round(z.abs().max(), 2))

print("\n== V4 suma de sectores ==")
m = df[sectores].notna().all(axis=1)
diff = (df.loc[m, sectores].sum(axis=1) - df.loc[m, "demanda_total"]).abs()
print("filas:", m.sum(), "| diferencia absoluta máx:", diff.max(), "| >1e-6:", int((diff > 1e-6).sum()))

print("\n== V5 distribuidoras vs total ==")
sub = df[df[dist].notna().any(axis=1)]
cob = sub[dist].sum(axis=1) / sub.demanda_total
print("meses", len(sub), "media", round(cob.mean(), 4), "min", round(cob.min(), 4), "max", round(cob.max(), 4))

print("\n== V6 correlaciones ==")
print("corr(potencia_maxima, demanda_total) =", round(df.potencia_maxima.corr(df.demanda_total), 4))
print("corr(temperatura, demanda_total)     =", round(df.temperatura_promedio.corr(df.demanda_total), 4))

print("\n== V7 tendencia ==")
anual = df.groupby(df.indice_tiempo.dt.year).demanda_total.mean()
print("media anual 2001:", round(anual[2001]), "| 2002:", round(anual[2002]), "| 2025:", round(anual[2025]),
      "| 2026 (parcial, 8 meses):", round(anual[2026]))

print("\n== V8 estacionalidad ==")
mm = df.groupby(df.indice_tiempo.dt.month).demanda_total.mean().round(0)
print("media por mes:", mm.to_dict())
print("meses ordenados de mayor a menor:", mm.sort_values(ascending=False).index.tolist())
ma = df.demanda_total.rolling(12, center=True).mean()
ratio = df.demanda_total / ma
rmax = ratio.groupby(df.indice_tiempo.dt.year).max().round(3)
print("ratio máx a media móvil centrada 12m por año:", rmax.to_dict())

print("\n== V9 split 80/20 ==")
n = len(df); ntr = int(n * 0.8)
print("n", n, "train", ntr, "test", n - ntr, "| primera fecha test:", df.indice_tiempo.iloc[ntr].date())
```

## Salida obtenida

```text
== V1 estructura ==
shape (308, 30) | columnas únicas: True
rango fechas 2001-01-01 2026-08-01
todos día 1: True | duplicadas: 0 | meses esperados: 308 | ordenado: True
dtypes distintos de float (salvo fecha): {}
grupos: 3 sectores, 3 base, 23 distribuidoras

== V2 nulos y disponibilidad ==
nulos base: {'demanda_total': 0, 'temperatura_promedio': 0, 'potencia_maxima': 0}
demanda_residencial nulos 48 primero 2005-01-01 último 2026-08-01
comercio_e_industria nulos 48 primero 2005-01-01 último 2026-08-01
grandes_usuarios nulos 48 primero 2005-01-01 último 2026-08-01
nulos sectores solo antes de 2005-01: 2004-12-01
filas con los 3 sectores: 260
nulos distribuidoras total: 3634 | por columna (únicos): [158]
fechas con >=1 distribuidora: 2014-01-01 2026-06-01 meses: 150
meses con las 23 presentes: 150 | con alguna presente pero no todas: 0
celdas no nulas distribuidoras (filas del formato largo): 3450
nulos 2026-07/08 en distribuidoras: True

== V3 rangos ==
      demanda_total  temperatura_promedio  potencia_maxima  demanda_residencial  comercio_e_industria  grandes_usuarios
min         5745.32                  9.30         12209.00              2184.77               3261.45           1403.76
max        13996.90                 27.10         30257.00              6927.38               5016.57           2333.80
mean        9761.71                 18.56         20040.83              4323.18               4008.38           1986.31
negativos (todas numéricas): 0
|z|>3 en demanda_total: 0 | max |z|: 2.24

== V4 suma de sectores ==
filas: 260 | diferencia absoluta máx: 1.8189894035458565e-12 | >1e-6: 0

== V5 distribuidoras vs total ==
meses 150 media 0.7097 min 0.6618 max 0.7602

== V6 correlaciones ==
corr(potencia_maxima, demanda_total) = 0.963
corr(temperatura, demanda_total)     = 0.0448

== V7 tendencia ==
media anual 2001: 6508 | 2002: 6373 | 2025: 11771 | 2026 (parcial, 8 meses): 12217

== V8 estacionalidad ==
media por mes: {1: 10611.0, 2: 9592.0, 3: 9846.0, 4: 8807.0, 5: 9603.0, 6: 10116.0, 7: 10616.0, 8: 10039.0, 9: 9098.0, 10: 9156.0, 11: 9316.0, 12: 10296.0}
meses ordenados de mayor a menor: [7, 1, 12, 6, 8, 3, 5, 2, 11, 10, 9, 4]
ratio máx a media móvil centrada 12m por año: {2001: 1.046, 2002: 1.081, 2003: 1.069, 2004: 1.067, 2005: 1.075, 2006: 1.06, 2007: 1.057, 2008: 1.053, 2009: 1.091, 2010: 1.092, 2011: 1.088, 2012: 1.096, 2013: 1.165, 2014: 1.133, 2015: 1.084, 2016: 1.102, 2017: 1.141, 2018: 1.137, 2019: 1.117, 2020: 1.148, 2021: 1.113, 2022: 1.141, 2023: 1.187, 2024: 1.132, 2025: 1.162, 2026: 1.112}

== V9 split 80/20 ==
n 308 train 246 test 62 | primera fecha test: 2021-07-01
```

## Lectura de los resultados

| Afirmación del diccionario | Resultado | Estado |
|---|---|---|
| 308 filas × 30 columnas; 2001-01 a 2026-08 sin huecos | 308 × 30; 308 meses esperados = 308 presentes; sin duplicados | Coincide |
| Columnas base completas | 0 nulos en `demanda_total`, `temperatura_promedio`, `potencia_maxima` | Coincide |
| Sectores desde 2005-01, 48 nulos al inicio | 48 nulos por sector, último nulo 2004-12; 260 filas con los tres | Coincide |
| 23 distribuidoras, 2014-01 a 2026-06, 158 nulos por columna | 158 nulos en cada una; 150 meses con las 23 presentes; ninguna parcial | Coincide |
| Rango de temperatura 9,3 – 27,1 | 9,30 – 27,10 | Coincide |
| Sectores suman exactamente `demanda_total` | 260 filas; diferencia máxima 1,8e-12 (ruido de coma flotante) | Coincide |
| Cobertura de distribuidoras ~71 % (66 % – 76 %) | media 70,97 %; mín 66,18 %; máx 76,02 % | Coincide |
| Correlación `potencia_maxima` ≈ 0,96 | 0,963 | Coincide |
| Correlación temperatura ≈ 0,04 | 0,0448 | Coincide |
| Sin negativos ni outliers \|z\| > 3 | 0 negativos; \|z\| máximo 2,24 | Coincide |
| Demanda anual media ~6.500 (2001) a ~12.200 (2026) | 2001: 6.508; 2025: 11.771; 2026: 12.217 pero con solo 8 meses (ene-ago) | **Corregido:** el valor de 2026 es parcial |
| Picos en enero, julio y diciembre; mínimos en abril y sep-oct | Medias por mes más altas: jul, ene, dic; más bajas: abr, sep, oct | Coincide |
| Ratio máximo a la tendencia: 1,05 (2001) → 1,16–1,19 (2023-2025) | 2001: 1,046; 2023: 1,187; 2024: 1,132; 2025: 1,162 | **Corregido:** el rango 2023-2025 es 1,13–1,19 |
| "Hay más meses Crítica en test que en train" | No verificable con el CSV crudo: depende de la etiqueta (D1 abierta) | **Retirado** del diccionario hasta medir con la etiqueta aprobada |
| Split 80/20 cronológico | 246 train / 62 test; primer mes de test 2021-07 (aplicando 80 % a 308 filas; el split real lo calcula el ETL) | Cálculo aritmético, no lectura del ETL |
