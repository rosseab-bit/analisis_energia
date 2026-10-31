# Diccionario de datos

Fuente: `data/raw/demanda_electricidad_original_mensual1.csv` · 308 filas × 30 columnas · serie **mensual** 2001-01 a 2026-08 (sin meses faltantes). SHA-256 del archivo: `b2964bd292dbde9b7b688268b04ae2f0bb783ebf0d48a87ee1d85f7b2eaf2241`.

Las cifras de este documento se verificaron contra el CSV; comando, salida y comparación en `docs/05_seguimiento/evidencia/VERIFICACION_DATOS_T02.md`. Las **unidades** de demanda y potencia **no figuran en el archivo** y están PENDIENTES (ver [Unidades](#unidades-pendiente-d7)).

## Columnas del CSV crudo (30)

Todas son `float64`, salvo `indice_tiempo` (fecha). Los nombres de columna ya vienen normalizados (minúsculas, sin espacios).

### Tiempo y variables base (4 columnas, sin nulos)

| Columna | Disponible | Descripción | Unidad |
|---|---|---|---|
| `indice_tiempo` | 2001-01 → 2026-08 (308 meses) | Primer día de cada mes | — |
| `demanda_total` | completa · 5.745,32 – 13.996,90 | Demanda total del mes | PENDIENTE |
| `temperatura_promedio` | completa · 9,3 – 27,1 | Temperatura media del mes | °C (supuesto por el rango; PENDIENTE de confirmar) |
| `potencia_maxima` | completa · 12.209 – 30.257 | Potencia máxima del mes | PENDIENTE |

### Sectores (3 columnas, 48 nulos cada una)

Disponibles desde 2005-01; los 48 nulos son 2001-01 → 2004-12. Hay 260 filas con los tres sectores.

| Columna | Rango | Descripción | Unidad |
|---|---|---|---|
| `demanda_residencial` | 2.184,77 – 6.927,38 | Demanda del sector residencial | PENDIENTE (misma que `demanda_total`, ver hallazgo 1) |
| `comercio_e_industria` | 3.261,45 – 5.016,57 | Demanda del sector comercio e industria | ídem |
| `grandes_usuarios` | 1.403,76 – 2.333,80 | Demanda de grandes usuarios | ídem |

### Distribuidoras (23 columnas, 158 nulos cada una)

Disponibles desde 2014-01 hasta 2026-06 (150 meses; los 158 nulos son 2001-01 → 2013-12 y 2026-07/08). En los 150 meses están presentes las 23; no hay meses con distribuidoras parciales. Cada columna es la demanda mensual de una distribuidora; el nombre es el del CSV (no se expanden siglas). Unidad: PENDIENTE.

| Columna | Mín – máx |
|---|---|
| `ede_tucuman` | 178,86 – 348,59 |
| `edelap_sa` | 165,54 – 333,93 |
| `edenor_distribuidor` | 1.399,59 – 2.567,91 |
| `edesal_distribuidor` | 75,57 – 133,83 |
| `edestesa_emp_dist__este` | 52,18 – 88,72 |
| `edesur_distribuidor` | 1.115,96 – 1.995,71 |
| `emp_de_energia_de_rio_negro_sa` | 92,61 – 150,16 |
| `emp_dist_energ_atlantica` | 189,23 – 306,23 |
| `emp_de_energia_de_la_rioja_sa` | 71,78 – 163,41 |
| `emp_dist_energia_de_salta` | 132,03 – 221,76 |
| `emp_electric_misiones_sa` | 86,55 – 295,59 |
| `empresa_dis_estero_sa` | 85,88 – 249,23 |
| `empresa_jujenia_de_energia_sa` | 61,85 – 97,63 |
| `energia_de_catamarca_sa` | 61,98 – 129,59 |
| `energia_de_entre_rios_sa` | 189,39 – 351,44 |
| `energia_de_mendoza_sa` | 214,95 – 373,21 |
| `energia_san_juan_sa_exedessa` | 102,08 – 258,07 |
| `epec_distribuidor` | 598,43 – 996,61 |
| `epen_distribuidor` | 64,69 – 105,61 |
| `epesf_distribuidor` | 645,84 – 1.172,63 |
| `recursos_y_energia_formosa_sa` | 75,20 – 185,51 |
| `secheep` | 165,77 – 414,90 |
| `spse_santa_cruz` | 32,67 – 64,25 |

## Hallazgos de calidad (verificados sobre el CSV)

1. **Sectores:** en las 260 filas donde existen, `residencial + comercio_e_industria + grandes_usuarios = demanda_total` de forma exacta (diferencia máxima 1,8e-12, ruido de coma flotante). Consecuencia: si la etiqueta se deriva de `demanda_total`, los sectores en valores absolutos **la reconstruyen** (fuga de datos). Usar participaciones (`part_*`) o excluirlos; se compara en el experimento de ablación (ver `docs/07_especificaciones/03-comparacion.md`, aún por redactar en CMP-1).
2. **Distribuidoras:** cubren en promedio ~71 % de `demanda_total` (66 %–76 %) en los 150 meses con datos; **no** suman el total. No se usan como features en la v1; se guardan en formato largo en `demanda_distribuidora`.
3. **`potencia_maxima`** tiene correlación ≈ 0,96 con `demanda_total` (y `temperatura_promedio` ≈ 0,04 con la demanda total, pues el efecto es no lineal: sube en verano y en invierno). Es una variable concurrente muy informativa; se mantiene como feature pero se evalúa su peso en la ablación.
4. **Tendencia:** la demanda anual media crece de ~6.500 (2001: 6.508) a ~11.800 (2025: 11.771); el valor de 2026 (12.217) cubre solo enero-agosto. Eso afecta a una etiqueta basada en percentiles globales. El código de referencia utiliza `relativo_tendencia`, pero su media centrada tiene un defecto temporal abierto. La decisión metodológica se mantiene en D1 de la spec, no se da por aprobada en este diccionario.
5. **Estacionalidad:** las medias por mes más altas son julio, enero y diciembre; las más bajas, abril, septiembre y octubre. La amplitud del pico estacional **crece** con los años: el máximo anual del cociente demanda / media móvil centrada de 12 meses pasa de 1,05 en 2001 a entre 1,13 y 1,19 en 2023-2025. Qué efecto tiene esto sobre la cantidad de meses `Crítica` en test depende de la etiqueta definitiva (D1) y se medirá en ETL-3; no se afirma aquí.
6. Sin valores negativos ni outliers (|z| > 3) en `demanda_total` (|z| máximo 2,24).

## Unidades (PENDIENTE, D7)

El CSV no incluye metadatos de unidades y no hay otra fuente en el repositorio que las indique. **No se asumen.** Hasta confirmarlas con la fuente:

| Variable | Unidad | Estado |
|---|---|---|
| `demanda_total`, sectores, distribuidoras | PENDIENTE (candidatos a verificar: GWh o MWh por mes) | Confirmar con la fuente del dataset |
| `potencia_maxima` | PENDIENTE (candidato a verificar: MW) | Confirmar con la fuente del dataset |
| `temperatura_promedio` | °C (supuesto: el rango 9,3 – 27,1 es plausible y `config.yaml` ya la trata como °C) | Confirmar con la fuente |

Cuando se confirmen, se completa esta tabla y la columna «Unidad» de arriba, se registra la fuente y la fecha de consulta, y se actualiza D7 en `docs/07_especificaciones/01-datos.md`. Hasta entonces, los gráficos y el informe deben rotular los ejes como «unidad pendiente» o evitar afirmar la unidad. La procedencia exacta del dataset también está pendiente (ver `docs/05_seguimiento/avance.md`).

## Tabla `datos_limpios` (Tabla 1 — salida del ETL)

Clave primaria: `fecha` (TEXT ISO `YYYY-MM-01`).

| Columna | Origen / regla |
|---|---|
| `anio`, `mes`, `trimestre` | Derivadas de la fecha |
| `estacion` | Verano (dic-feb), Otoño (mar-may), Invierno (jun-ago), Primavera (sep-nov) — hemisferio sur |
| `mes_sin`, `mes_cos` | Codificación cíclica del mes (dic y ene quedan cercanos) |
| `demanda_total`, `temperatura_promedio`, `potencia_maxima` | Copia validada (sin nulos) |
| `demanda_residencial`, `comercio_e_industria`, `grandes_usuarios` | Copia; **NULL antes de 2005-01** (no se imputa en el ETL) |
| `part_residencial`, `part_comercio_industria`, `part_grandes_usuarios` | sector / `demanda_total`; NULL si no hay sectores |
| `tiene_sectores` | 1 si los tres sectores están presentes |
| `demanda_ratio_tendencia` | `demanda_total` / media móvil centrada 12 m (solo método `relativo_tendencia`). **Derivada de la etiqueta: no usar como feature** |
| `etiqueta` | `Normal` (≤ P75), `Alta` (P75–P90), `Crítica` (> P90); umbrales calculados **solo con train**. Es la regla de la implementación actual; su definición final es la decisión D1 |
| `split` | `train` (primeros 80 % de los meses) / `test` (últimos 20 %), cronológico |

Columnas **prohibidas como feature** (definidas en `config.yaml`): `fecha`, `etiqueta`, `split`, `demanda_total`, `demanda_ratio_tendencia`.

## Tablas extra del ETL

- `demanda_distribuidora(fecha, distribuidora, demanda)` — formato largo, 150 meses × 23 distribuidoras = 3.450 filas (coincide con las celdas no nulas del CSV).
- `etl_auditoria` — una fila por corrida: archivo, SHA-256, filas leídas/cargadas, nulos por columna, umbrales de etiqueta, advertencias y configuración usada.
