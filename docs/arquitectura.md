# Alcance y arquitectura

## Objetivo

Clasificar meses de demanda eléctrica como `Normal`, `Alta` o `Crítica`, comparar tres algoritmos y almacenar los datos, predicciones, métricas y configuración en SQLite. El alcance corresponde a clasificación de períodos; no incluye pronóstico, API ni despliegue productivo.

Los datos y sus unidades se describen en el [diccionario](datos/diccionario.md). La definición final de la etiqueta y el momento en que están disponibles las variables siguen abiertos en la [especificación de datos](especificaciones/datos-etl.md).

## Componentes y estado

| Componente | Función | Estado |
|---|---|---|
| ETL | Extracción, validación, transformación y carga del CSV | Implementado; defecto temporal de etiquetado pendiente |
| SQLite | Datos limpios, auditoría y tablas para resultados | Esquema implementado |
| Modelado | Preprocesamiento, entrenamiento y evaluación comunes | Pendiente |
| Comparación | Consulta y análisis de resultados de los tres modelos | Pendiente |
| Visualización | Gráficos y dashboard Streamlit sobre SQLite | Pendiente |

```text
CSV → extracción → validación → transformación → SQLite
                                                  ↓
                         preprocesamiento y modelos (pendiente)
                                                  ↓
                         predicciones, métricas y configuración
                                                  ↓
                         comparación y dashboard (pendiente)
```

## ETL implementado

| Módulo | Responsabilidad |
|---|---|
| `src/demanda/etl/extract.py` | Lectura del CSV, normalización de nombres, fechas y hash SHA-256 |
| `src/demanda/etl/validate.py` | Errores y advertencias de calidad de datos |
| `src/demanda/etl/transform.py` | Calendario, participaciones sectoriales, etiqueta, split y distribuidoras en formato largo |
| `src/demanda/etl/load.py` | Carga transaccional, sustitución de datos y auditoría |
| `src/demanda/etl/pipeline.py` | Orquestación de las etapas |
| `scripts/run_etl.py` | Interfaz de ejecución desde la terminal |

Los nulos de sectores y distribuidoras representan períodos sin datos y se conservan. Los criterios de validación y el diagnóstico de dependencia temporal están en la [especificación](especificaciones/datos-etl.md) y la [validación del ETL](validacion/etl.md).

## Persistencia

El [esquema SQLite](../src/demanda/db/schema.sql) contiene:

| Tabla | Contenido |
|---|---|
| `datos_limpios` | Una fila por mes, variables originales y derivadas, etiqueta y split |
| `demanda_distribuidora` | Demanda por mes y distribuidora, solo valores no nulos |
| `etl_auditoria` | Archivo y hash, conteos, nulos, umbrales, advertencias y configuración de cada carga |
| `predicciones` | Etiqueta real, predicción y probabilidades por clase y ejecución |
| `metricas_modelo` | Métricas globales y por clase, matriz de confusión, CV y tiempo de entrenamiento |
| `config_modelo` | Hiperparámetros, variables utilizadas, semilla y configuración de evaluación |

La clave de los datos mensuales es `fecha`, en formato ISO `YYYY-MM-01`; las ejecuciones de modelos se identifican por `run_id`. Repetir el ETL no duplica los datos. La carga conserva las tablas de modelos; si cambian las etiquetas, sus resultados deben regenerarse. `--reset` elimina todas las tablas antes de volver a crearlas.

## Diseño previsto de modelado

Los tres algoritmos utilizarán el mismo preprocesamiento dentro de un `sklearn.pipeline.Pipeline`, split cronológico, validación con `TimeSeriesSplit` y evaluación. La imputación, escalado y codificación de categóricas se ajustarán dentro del pipeline de entrenamiento. La semilla y los conjuntos de variables se leen de [config/config.yaml](../config/config.yaml).

| Modelo | Búsqueda de hiperparámetros |
|---|---|
| Regresión Logística | `GridSearchCV` |
| Random Forest | `RandomizedSearchCV` |
| XGBoost | `RandomizedSearchCV` |

La comparación prevista incluye Accuracy, Precision, Recall, F1 y matriz de confusión, con métricas macro y por clase. El ajuste utilizará `f1_macro` sobre validación temporal de train. Test queda reservado para la evaluación final.

Los conjuntos de variables definidos son `base`, `con_participaciones` y `sin_potencia`. Los sectores absolutos reconstruyen la demanda total y no se usan como predictores. También se excluyen `fecha`, `etiqueta`, `split`, `demanda_total` y `demanda_ratio_tendencia`.

### Interfaces propuestas, pendientes de implementación

Cada módulo de modelo expondrá:

```python
NAME = "logreg"  # "logreg" | "rf" | "xgb"
SEARCH = "grid"  # "grid" | "random"

def get_estimator(random_state: int): ...
def get_param_grid() -> dict: ...  # claves con prefijo "clf__"
def get_n_iter() -> int | None: ...
```

El acceso previsto a SQLite comprende `load_clean_data(db_path=None, desde_sectores=False)` y `save_run(run_id, predictions_df, metrics_dict, config_dict)`. Los modelos leerán la etiqueta y el split calculados por el ETL; el dashboard consultará la base de datos. Estas interfaces describen el diseño y todavía no están disponibles como módulos ejecutables.
