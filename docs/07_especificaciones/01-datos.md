# Spec 01 — Datos y ETL

Estado: **borrador v0.1** (se aprueba en la tarea T-01). Cualquier cambio se hace primero acá.

## 1. Objetivo
Cargar `demanda_electricidad_original_mensual1.csv` en SQLite de forma **reproducible, validada y auditable**, dejando la Tabla 1 lista para que los tres modelos la consuman sin tocarla.

## 2. Pipeline

```
CSV ──E──► DataFrame crudo ──V──► reporte (errores/avisos) ──T──► datos_limpios + demanda_distribuidora ──L──► SQLite
        extract.py            validate.py                      transform.py                              load.py
```

Se ejecuta con `python scripts/run_etl.py [--reset]`. Orquestación en `etl/pipeline.py::run_etl`.

## 3. Criterios de aceptación

| ID | Criterio | Verificación |
|---|---|---|
| ETL-1 | El CSV se lee sin modificar valores; las fechas se parsean a datetime | `test_fechas_extraidas` |
| ETL-2 | La corrida **falla** (código de salida 1, sin escribir nada) si: faltan columnas obligatorias, hay fechas duplicadas o meses faltantes, valores negativos, temperatura fuera de rango, nulos en columnas base, sectores parcialmente nulos o que no suman `demanda_total` | `TestValidate` |
| ETL-3 | Los nulos esperados (sectores antes de 2005; distribuidoras antes de 2014 y tras 2026-06) generan **advertencia**, no error, y **no se imputan** en el ETL | `test_nulos_esperados_*`, `test_participaciones_*` |
| ETL-4 | Tabla 1 con una fila por mes, clave `fecha`, columnas según `docs/06_datos/data_dictionary.md` | `test_conteos` |
| ETL-5 | Los cálculos que definen los scores, umbrales y etiquetas de train no dependen de test; debe probarse el método configurado, incluidos sus pasos intermedios | Ampliar la prueba de independencia temporal; la actual solo verifica `percentil_global` |
| ETL-6 | Split cronológico (nunca aleatorio) con fracción de `config.yaml` | `test_split_cronologico` |
| ETL-7 | La carga es **atómica** (transacción) e **idempotente** (correr dos veces no duplica) | `test_rollback_*`, `test_carga_idempotente_*` |
| ETL-8 | Cada corrida deja una fila en `etl_auditoria` con SHA-256 del archivo, conteos, nulos, umbrales y configuración | `test_carga_idempotente_*` |
| ETL-9 | Las distribuidoras se guardan en formato largo, solo con datos no nulos | `test_distribuidoras_formato_largo_*` |

## 4. Decisiones abiertas (cerrar en T-01 con los 3)

| ID | Decisión | Propuesta por defecto | Alternativas / riesgo |
|---|---|---|---|
| D1 | **Definición de la etiqueta y momento de clasificación** | Acordar qué se clasifica y cuándo están disponibles las variables. La implementación actual usa `relativo_tendencia` y P75/P90, pero su media centrada tiene un defecto temporal comprobado | Decidir y justificar la solución antes de cambiar el código. No aprobar por defecto la media centrada ni sustituirla automáticamente por percentiles globales |
| D2 | **Fuga por sectores** | Los sectores suman exactamente `demanda_total`; usar solo `part_*` (participaciones) o excluirlos | Experimento de ablación: con/sin sectores, con/sin `potencia_maxima` |
| D3 | **Filas 2001-2004 sin sectores** | Mantenerlas en Tabla 1 (NULL). Los modelos que usen sectores trabajan desde 2005-01 (`tiene_sectores = 1`); los que no, usan toda la serie | Imputar (no recomendado: no hay dato real) |
| D4 | **Evaluación con muestra pequeña y desbalance** | CV temporal, F1 macro y Recall Crítica; reportar métricas por clase y limitaciones. Considerar variante binaria como experimento acordado | Medir los conteos de clase nuevamente si cambia la etiqueta; no fijar como definitivas las cifras de referencia |
| D5 | **Split y comparabilidad temporal** | Split cronológico 80/20 definido por el ETL y compartido por los modelos; documentar la deriva estacional | Al comparar features, controlar o explicitar cambios de población por disponibilidad sectorial. No seleccionar parámetros con test |
| D6 | **Distribuidoras** | Fuera de las features de v1 (cobertura parcial, solo desde 2014) | Experimento v2 desde 2014 |
| D7 | **Unidades** | Confirmar con la fuente (GWh/MWh, MW) y completar el diccionario | — |

## 5. Contrato con los modelos (lectura de Tabla 1)

```python
# demanda/db/repository.py  (tarea DB-1)
def load_clean_data(db_path=None, desde_sectores: bool = False) -> pd.DataFrame:
    """Devuelve datos_limpios ordenado por fecha. Si desde_sectores=True, solo filas con tiene_sectores=1."""
```

Los modelos **no** recalculan la etiqueta ni el split: leen `etiqueta` y `split` de la tabla.

Los hechos observados y unidades se mantienen en el diccionario; los estados de corrección, en avance general. Esta spec sigue siendo un borrador: centralizar D1-D7 no equivale a aprobar sus decisiones.
