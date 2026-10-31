# Proyecto: Clasificación de períodos de demanda eléctrica (Normal / Alta / Crítica)

> Documento base bajo **SDD (Spec-Driven Development)**: primero se acuerda la especificación, después el plan técnico, después las tareas, y recién entonces se implementa (con ayuda de un agente de IA por integrante). Cualquier cambio de alcance se hace primero en este documento, con su propio commit, y después en el código.

Versión **0.3** · Equipo: 3 integrantes (A, B, Angel Zambrano) · GitHub · SQLite · scikit-learn

**Qué cambió respecto de v0.2**
- Se agrega el **proceso ETL** del CSV `demanda_electricidad_original_mensual1.csv` → SQLite, ya diseñado y verificado (25 tests) contra el archivo real.
- Se **reorganizan las tareas** entre los 3 integrantes (ETL repartido por módulos) y se elimina la tarea del dataset sintético: el ETL real genera la BD el primer día.
- Cada tarea tiene una **ficha con prompt para el agente de IA** en `docs/04_integrantes/A/TAREAS_A.md`, `docs/04_integrantes/B/TAREAS_B.md` y `docs/04_integrantes/Angel_Zambrano/TAREAS_C.md`.
- Se incorporan los **hallazgos de calidad de datos** (§1.3), que cambian decisiones de etiqueta, features y validación.

---

## 1. Especificación (QUÉ y PARA QUÉ)

### 1.1 Objetivo
Analizar el dataset de demanda eléctrica y aplicar ML para **clasificar períodos de demanda alta o crítica frente a demanda normal**, a partir de demanda total y sectorial, temperatura, potencia máxima y estacionalidad.

### 1.2 Requerimientos aceptados (trazabilidad)

| ID | Requerimiento | Criterio de aceptación |
|----|---------------|------------------------|
| RF-1 | `sklearn.pipeline.Pipeline` con imputación, escalado y codificación de categóricas | Un preprocesador común (`ColumnTransformer`) usado por los 3 modelos dentro de un `Pipeline` |
| RF-2 | Comparar al menos 2 algoritmos con búsqueda de hiperparámetros | Logistic Regression (`GridSearchCV`), Random Forest y XGBoost (`RandomizedSearchCV`) |
| RF-3 | Accuracy, Precision, Recall, F1 y matriz de confusión | Un solo `evaluate.py` para los 3 modelos, mismo conjunto de test |
| RF-4 | Persistencia en SQLite | Tabla 1 (datos limpios), Tabla 2 (predicciones + métricas), Tabla 3 (configuración) |
| RF-5 | Visualización | Gráficos y tablas claras + dashboard Streamlit con comparación de modelos |
| RF-6 | **ETL** del CSV a SQLite | `python scripts/run_etl.py` valida, transforma y carga de forma atómica e idempotente, con auditoría |

**Entrega académica:** además de los requisitos técnicos, la consigna pide repositorio con código, script de carga, dependencias y README; base de datos accesible para revisión; **6 a 8 diapositivas en PDF o PPTX subidas al campus**; y defensa de **8 a 10 minutos**. Estos entregables se verifican en F-3/F-4 y en [Avance general](../05_seguimiento/avance.md).

La rúbrica asigna 25 % a cada bloque: código y Git; BD y visualización; modelado y resultados; presentación oral y defensa. La materia exige al menos dos modelos y visualizaciones claras; el equipo mantiene el compromiso de tres modelos y dashboard. La Tabla 3 es opcional en la consigna y parte del alcance interno de este plan.

### 1.3 Datos y riesgos de diseño

Los períodos, disponibilidad, unidades y hallazgos observados se mantienen en el [diccionario de datos](../06_datos/data_dictionary.md). La evidencia de ejecución y los defectos abiertos se registran en [avance general](../05_seguimiento/avance.md).

El diseño debe evitar que los sectores reconstruyan la etiqueta, evaluar el efecto de potencia y respetar la separación temporal. La implementación de referencia usa una media centrada con una dependencia temporal comprobada: su existencia no aprueba esa metodología ni permite dar el ETL por cerrado.

### 1.4 Decisiones a cerrar en T-01

El único registro de D1-D7 está en la [spec de datos, sección 4](../07_especificaciones/01-datos.md#4-decisiones-abiertas-cerrar-en-t-01-con-los-3). Allí se acuerdan etiqueta, features, nulos, evaluación, split, distribuidoras y unidades. No se mantiene otra tabla de esas decisiones en el plan.

### 1.5 Fuera de alcance (v1)
Forecasting, despliegue productivo, API REST.

---

## 2. Arquitectura (CÓMO)

### 2.1 Flujo general

```
CSV ─E─► validar ─V─► transformar ─T─► SQLite: datos_limpios (Tabla 1) + demanda_distribuidora + etl_auditoria
                                                     │
                       ┌─────────────────────────────┼─────────────────────────────┐
                       ▼                             ▼                             ▼
                 [LR · A]                       [RF · B]                       [XGBoost]    ← mismo preprocesador,
          GridSearchCV · f1_macro      RandomizedSearchCV · f1_macro   RandomizedSearchCV     split, CV y evaluate
                       └─────────────────────────────┼─────────────────────────────┘
                                                     ▼
              SQLite: predicciones + metricas_modelo (Tabla 2) + config_modelo (Tabla 3)
                                                     ▼
                         [Comparación de métricas] ─► [Dashboard Streamlit]
```

### 2.2 Proceso ETL (módulos y dueños)

| Etapa | Módulo | Responsabilidad | Tarea | Dueño |
|---|---|---|---|---|
| **E**xtract | `etl/extract.py` | Lee el CSV, normaliza nombres, parsea fechas, SHA-256 del archivo | ETL-1 | A |
| **V**alidate | `etl/validate.py` | Errores (detienen) y advertencias (se auditan): fechas, huecos, negativos, rango de temperatura, nulos base, sectores todo-o-nada y suma = total | ETL-2 | B |
| **T**ransform | `etl/transform.py` | Calendario (mes, estación, seno/coseno), participaciones, etiqueta, split cronológico, tabla larga de distribuidoras | ETL-3 | A |
| **L**oad | `etl/load.py` | Transacción única, idempotente, rollback ante error, auditoría | ETL-4 | Angel Zambrano |
| Orquestación | `etl/pipeline.py`, `scripts/run_etl.py` | Une las etapas; CLI con `--reset` | ETL-5 | Angel Zambrano |

Reglas clave: los nulos de sectores/distribuidoras **no se imputan en el ETL** (el dato no existe esos meses; si hace falta imputar, ocurre dentro del `Pipeline` de sklearn para no filtrar información). Los umbrales de la etiqueta salen **solo del período train**.

**Código de referencia:** ya está incorporado al repositorio. Cada dueño revisa su módulo, ajusta lo necesario a las decisiones aprobadas y entrega evidencia y cambios reales. No se elimina y vuelve a incorporar código para atribuir trabajo. Los resultados de la verificación se mantienen en avance general.

### 2.3 Estructura del repositorio

```
analisis_energia/
├── docs/
│   ├── README.md                  # índice documental
│   ├── 00_inicio/                 # README técnico del proyecto
│   ├── 01_consigna/               # PDF oficial y revisión interna
│   ├── 02_planificacion/          # este plan y coordinación
│   ├── 03_guias/                  # equipo, agente, CLAUDE.md y PDF
│   ├── 04_integrantes/            # A/, B/ y Angel_Zambrano/
│   ├── 05_seguimiento/            # avance.md y evidencia/
│   ├── 06_datos/                  # diccionario de datos
│   ├── 07_especificaciones/       # contratos y specs
│   └── 08_entrega/                # informe, model card y presentación (por crear)
├── pyproject.toml · requirements.txt · .gitignore
├── CODEOWNERS · .github/          # infraestructura pendiente de completar
├── config/config.yaml
├── data/raw/                     # CSV original
├── db/                           # base generada, ignorada por Git
├── notebooks/                    # análisis de modelos (por implementar)
├── src/demanda/
│   ├── config.py
│   ├── etl/                      # extract, validate, transform, load, pipeline
│   ├── db/                       # esquema y repository (pendiente)
│   ├── models/                   # módulos de modelos (pendientes)
│   └── viz/                      # gráficos y app (pendientes)
├── scripts/
└── tests/
```

La documentación no se guarda en la raíz. Su jerarquía se conserva al trasladarla a Google Drive, mientras el repositorio mantiene el backup. Las ubicaciones futuras del árbol no acreditan archivos o entregas ya implementados.


### 2.4 Contrato de modelos
Cada modelo vive en su archivo (`logreg.py`, `rf.py`, `xgb.py`) y expone la misma interfaz; el runner los descubre solo, así que agregar un modelo no toca archivos ajenos.

```python
NAME = "logreg"            # "logreg" | "rf" | "xgb"
SEARCH = "grid"            # "grid" | "random"
def get_estimator(random_state: int): ...
def get_param_grid() -> dict: ...      # claves con prefijo "clf__"
def get_n_iter() -> int | None: ...
```
```bash
python -m demanda.models.train --model logreg --features base     # o rf / xgb
```
`--features` elige un conjunto de `config.yaml → modelado.feature_sets` (`base`, `con_participaciones`, `sin_potencia`).

### 2.5 Esquema SQLite
Clave natural `fecha` (primer día del mes); el ETL puede repetirse sin romper las referencias.

| Tabla | Contenido |
|---|---|
| **`datos_limpios`** (Tabla 1) | `fecha` PK, `anio`, `mes`, `trimestre`, `estacion`, `mes_sin`, `mes_cos`, `demanda_total`, 3 sectores, 3 `part_*`, `tiene_sectores`, `temperatura_promedio`, `potencia_maxima`, `demanda_ratio_tendencia`, `etiqueta`, `split` |
| `demanda_distribuidora` (extra) | `fecha`, `distribuidora`, `demanda` (formato largo) |
| `etl_auditoria` (extra) | corrida, archivo, SHA-256, conteos, nulos, umbrales, advertencias, config |
| **`predicciones`** (Tabla 2) | `run_id`, `fecha`, `modelo`, `y_real`, `y_pred`, `prob_normal/alta/critica` |
| **`metricas_modelo`** (Tabla 2) | `run_id`, accuracy, precision/recall/F1 macro y por clase, `matriz_confusion` (JSON), `cv_best_score`, tiempo, `n_train`, `n_test` |
| **`config_modelo`** (Tabla 3) | `run_id`, grilla, mejores parámetros, umbrales de etiqueta, features usadas, semilla, folds, scoring |

El esquema completo está en `src/demanda/db/schema.sql`.

### 2.6 Contratos entre integrantes
- **ETL → modelos:** `repository.load_clean_data(desde_sectores=False) -> DataFrame` (esquema de Tabla 1, con `etiqueta` y `split` ya definidos; los modelos **no** los recalculan).
- **Modelos → BD:** `repository.save_run(run_id, predictions_df, metrics_dict, config_dict)`.
- **BD → dashboard:** el dashboard solo lee `demanda.db`.
- **Mientras algo no esté mergeado:** cualquiera genera su `demanda.db` local con el ETL de referencia y trabaja contra el contrato.

---

## 3. Flujo de trabajo (resumen; detalle en `docs/03_guias/GUIA_EQUIPO.md`)

**Una tarea = un issue = una rama = varios commits propios = un PR revisado por otro integrante.**

1. `main` protegida (PR + 1 aprobación + CI verde). Ramas `feat/<ID>-<slug>`.
2. Cada integrante usa **su identidad de Git** → el historial prueba quién hizo qué.
3. **Mínimo 3 commits por tarea**, orden SDD: *spec → test → implementación → docs*. Formato `tipo(ID): descripción`.
4. Cada integrante trabaja **con su agente de IA**, pero el humano revisa el diff, entiende el código y es quien hace el commit.
5. PR con `Closes #N`, revisión rotativa A→B→Angel Zambrano→A, **merge sin squash**.
6. Los issues se crean con `scripts/crear_issues.sh` (labels, milestones, dependencias `#N`).

---

## 4. Reparto de responsabilidades

| | Área transversal | ETL | Modelo propio |
|---|---|---|---|
| **A** | Datos, diccionario, esquema de BD, `repository` (lectura y `save_run`) | **E**xtract + **T**ransform | **Logistic Regression** (`GridSearchCV`) |
| **B** | Núcleo de modelado común (preprocesador, split/CV, `evaluate`, runner) y EDA | **V**alidate + EDA de decisión D1/D2 | **Random Forest** (`RandomizedSearchCV`) |
| **Angel Zambrano** | Repo, CI, fixtures, visualización y dashboard | **L**oad + orquestación y CLI | **XGBoost** (`RandomizedSearchCV`) |

**Angel Zambrano corresponde al identificador interno C.** Se conservan `docs/04_integrantes/Angel_Zambrano/TAREAS_C.md`, `GH_USER_C` y `persona-C` para mantener las referencias del proyecto. Su guía práctica está en [Plan personal de Angel](../04_integrantes/Angel_Zambrano/PLAN_PERSONAL_ANGEL.md).

Fichas detalladas con prompts para el agente: `docs/04_integrantes/A/TAREAS_A.md`, `docs/04_integrantes/B/TAREAS_B.md`, `docs/04_integrantes/Angel_Zambrano/TAREAS_C.md`.

---

## 5. Tareas

`Depende de` = tareas que deben estar **mergeadas en `main`**. Las columnas sin dependencia cruzada se pueden hacer en paralelo.

### Fase 0 — Fundación (semana 1)

| ID | Tarea | Resp. | Depende de | Entregable |
|----|-------|-------|-----------|-----------|
| T-00 | Completar repo y esqueleto: `pyproject`, `requirements`, `.gitignore`, `config.yaml`, `docs/03_guias/CLAUDE.md`, `CODEOWNERS`, plantilla de PR, protección de `main`, invitaciones | Angel Zambrano | – | Repo clonable; `pip install -e .` funciona |
| T-01 | Reunión de arranque: cerrar D1–D7, aprobar `docs/07_especificaciones/00-contratos.md` y `docs/07_especificaciones/01-datos.md` (cada uno redacta su parte) | A+B+Angel Zambrano | T-00 | Specs aprobadas por PR |
| T-02 | Diccionario de datos y unidades (D7) | A | T-00 | `docs/06_datos/data_dictionary.md` |
| T-03 | `schema.sql` (Tabla 1, 2, 3 + extras del ETL) | A | T-01 | DDL idempotente |
| CMP-1 | Spec de comparación (criterios fijados **antes** de ver resultados) | A+B+Angel Zambrano | T-01 | `docs/07_especificaciones/03-comparacion.md` |

### Fase 1 — ETL y base compartida (semanas 1–2)

| ID | Tarea | Resp. | Depende de | Entregable |
|----|-------|-------|-----------|-----------|
| ETL-1 | **Extract**: lectura, normalización de columnas, fechas, SHA-256 | A | T-02 | `etl/extract.py` + tests |
| ETL-2 | **Validate**: reglas de calidad (errores vs advertencias) | B | T-01 | `etl/validate.py` + tests |
| ETL-3 | **Transform**: calendario, participaciones, etiqueta (D1), split cronológico, tabla larga | A | T-01 | `etl/transform.py` + tests (incl. "sin fuga") |
| ETL-4 | **Load**: transacción, idempotencia, rollback, auditoría | Angel Zambrano | T-03 | `etl/load.py` + tests |
| ETL-5 | **Pipeline + CLI** `run_etl.py` + test de integración con el CSV real | Angel Zambrano | ETL-1, ETL-2, ETL-3, ETL-4 | `demanda.db` reproducible |
| ETL-6 | **EDA de decisión**: comparar métodos de etiqueta (D1), balance de clases, correlaciones, ablación preliminar (D2) | B | ETL-5 | `notebooks/01_eda.ipynb` + recomendación |
| DB-1 | `repository.load_clean_data()` | A | ETL-5 | Función + tests |
| DB-2 | `repository.save_run()` (Tablas 2 y 3) en una transacción | A | T-03 | Función + tests |
| MC-1 | `build_preprocessor()` desde `feature_sets` (imputación, escalado, OHE; test anti-fuga) | B | T-01, ETL-5 | `preprocessing.py` + tests |
| MC-2 | `splits.py`: usa la columna `split` + `get_cv()` (`TimeSeriesSplit`) | B | ETL-5 | `splits.py` + tests |
| MC-3 | `evaluate.py`: Accuracy, Precision, Recall, F1 (macro y por clase) + matriz de confusión | B | T-01 | `evaluate.py` + tests |
| MC-4 | Runner `train.py` (`--model`, `--features`, autodescubrimiento) | B | MC-1, MC-2, MC-3, DB-1, DB-2 | Comando único |
| T-15 | CI en GitHub Actions (pytest + ruff) | Angel Zambrano | T-00 | Check obligatorio |
| VIZ-1 | `plots.py` base: clases, demanda vs temperatura, estacionalidad, serie con períodos críticos | Angel Zambrano | ETL-5 | Funciones reutilizables |
| VIZ-2 | BD fixture con las 3 tablas (resultados ficticios) para tests y dashboard | Angel Zambrano | T-03 | Fixture de test |

### Fase 2 — Entrenamiento de modelos (semanas 2–4, en paralelo, cada uno por separado)

Las **7 tareas son idénticas en estructura**; cambia el algoritmo. Prefijo `LR-` (A), `RF-` (B), `XG-` (Angel Zambrano).

| Paso | Tarea (se repite por modelo) | Depende de | Entregable |
|---|---|---|---|
| **X-1** | **Spec del modelo**: justificación, hiperparámetros y rangos, tratamiento del desbalance | T-01 | `docs/07_especificaciones/02-modelo-<x>.md` |
| **X-2** | **Módulo del modelo** (contrato §2.4) + test unitario | X-1, T-03 | `models/<x>.py` + `tests/` |
| **X-3** | **Baseline** sin tuning con el pipeline común y validación temporal de train, set `base` | X-2, MC-1, MC-2, MC-3 | Baseline reproducible |
| **X-4** | **Búsqueda de hiperparámetros** con la CV temporal común y scoring `f1_macro` | X-3 | Mejores parámetros, `cv_best_score` |
| **X-5** | **Evaluación** en test + **ablación** de features (`base`, `con_participaciones`, `sin_potencia`) | X-4, MC-3 | Métricas y matrices por set |
| **X-6** | **Persistencia** en Tablas 2 y 3 con `run_id` propio | X-5, MC-4, DB-2 | Filas en `demanda.db` |
| **X-7** | **Notebook e informe**: interpretación y análisis de errores | X-6 | `notebooks/0N_<x>.ipynb` + `docs/08_entrega/model_card.md` |

| | A · Logistic Regression | B · Random Forest | Angel Zambrano · XGBoost |
|---|---|---|---|
| Búsqueda | `GridSearchCV` | `RandomizedSearchCV` | `RandomizedSearchCV` |
| Hiperparámetros | `C`, `penalty`, `solver` | `n_estimators`, `max_depth`, `min_samples_leaf`, `max_features` | `n_estimators`, `max_depth`, `learning_rate`, `subsample`, `colsample_bytree`, `reg_lambda` |
| Desbalance | `class_weight='balanced'` | `class_weight='balanced'` | `sample_weight` balanceado (requiere acordar el contrato con B) |
| Interpretación | Coeficientes por clase | Importancia de variables | Importancia por *gain* (+ SHAP opcional) |
| Cuidado | Necesita escalado (lo da el preprocesador) | — | Etiquetas como enteros dentro del módulo |

### Fase 3 — Comparación de métricas (semanas 4–5)

| ID | Tarea | Resp. | Depende de | Entregable |
|----|-------|-------|-----------|-----------|
| CMP-2 | `compare_runs()`: consulta consolidada de los 3 `run_id` (mismo split y semilla) | A | LR-6, RF-6, XG-6, CMP-1 | Función + tests |
| CMP-3 | Tabla comparativa y gráficos: barras de métricas, matrices lado a lado, F1 por clase, tiempos, ablación | Angel Zambrano | CMP-2, VIZ-1 | `plots.py` ampliado |
| CMP-4 | Análisis: qué modelo gana y por qué, errores por clase, efecto del desbalance y de la deriva estacional | B | CMP-3 | `notebooks/05_comparacion.ipynb` |
| CMP-5 | Decisión del modelo final según los criterios de CMP-1 | A+B+Angel Zambrano | CMP-4 | Sección en `docs/08_entrega/model_card.md` |

### Fase 4 — Dashboard y cierre (semanas 5–6)

| ID | Tarea | Resp. | Depende de | Entregable |
|----|-------|-------|-----------|-----------|
| V-1 | Dashboard Streamlit: filtros por modelo, fecha y clase; métricas; matrices; predicciones; calidad de datos (auditoría ETL) | Angel Zambrano | CMP-3 | `app.py` sobre `demanda.db` |
| F-1 | `run_all.py` + test de integración (ETL → 3 modelos → BD) | B | CMP-2 | Un comando de punta a punta |
| F-2 | Revisión cruzada final (A→B, B→Angel Zambrano, Angel Zambrano→A) | A+B+Angel Zambrano | V-1, F-1 | PRs de revisión cerrados |
| F-3 | Informe y README, acceso de revisión a la BD y presentación de 6 a 8 diapositivas PDF/PPTX; acordar responsable y registrar subida al campus | A+B+Angel Zambrano | CMP-5, V-1 | Informe, README probado, BD accesible y presentación entregada |
| F-4 | Ensayo de demo desde cero y defensa oral de 8 a 10 minutos, con reparto de exposición | A+B+Angel Zambrano | F-3 | Demo reproducible, duración registrada y los tres preparados para defenderla |

Los borradores de presentación, el reparto de exposición y el mecanismo de acceso a la BD pueden prepararse antes de terminar el modelado. F-3/F-4 se cierran con resultados definitivos y las dependencias verificadas. La consolidación de diapositivas y la subida al campus se asignan explícitamente en el issue conjunto; no se presuponen a cargo de una persona.

### Camino crítico
`T-01 → T-03 → ETL-4 → ETL-5 → MC-1/MC-2 → MC-4 → X-3 → X-4 → X-5 → X-6 → CMP-2 → CMP-3 → CMP-4 → CMP-5 → F-3`

Los modelos pueden desarrollarse en paralelo una vez disponibles sus componentes comunes. CMP-2 reúne los tres runs; antes también existen dependencias compartidas de ETL, contratos, persistencia y runner.

### Carga por integrante (tareas propias, sin contar las conjuntas)

| A | B | Angel Zambrano |
|---|---|---|
| T-02, T-03, ETL-1, ETL-3, DB-1, DB-2, LR-1…7, CMP-2 = **14** | ETL-2, ETL-6, MC-1…4, RF-1…7, CMP-4, F-1 = **15** | T-00, T-15, ETL-4, ETL-5, VIZ-1, VIZ-2, XG-1…7, CMP-3, V-1 = **15** |

Conjuntas (las tres personas): T-01, CMP-1, CMP-5, F-2, F-3, F-4.

---

## 6. Definición de "hecho" (DoD) por tarea
- [ ] Issue con ID de tarea; el PR lo cierra (`Closes #N`).
- [ ] Spec/criterio escrito **antes** de implementar.
- [ ] Mínimo 3 commits propios, Conventional Commits con ID de tarea.
- [ ] Verificaciones pertinentes aprobadas; en código y CI, tests y linter en local y CI. En documentación, evidencia, enlaces y coherencia.
- [ ] El autor puede **explicar** el código (aunque lo haya generado el agente).
- [ ] Documentación y docstrings actualizados.
- [ ] PR aprobado por otro integrante; merge **sin squash**.
- [ ] Casilla marcada en `docs/05_seguimiento/avance.md`.

## 7. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| **Fuga de datos**: sectores suman `demanda_total`; etiqueta derivada de `demanda_total` | Columnas prohibidas en `config.yaml`; test anti-fuga en MC-1; features `base` sin sectores absolutos |
| **`potencia_maxima` casi colineal** con la demanda (0,96) | Ablación `sin_potencia`; reportar ambos resultados |
| **Muestra chica y clases desbalanceadas** → métricas inestables | `TimeSeriesSplit`, F1 macro + Recall Crítica, advertir en el informe; variante binaria |
| **Deriva estacional** (más Crítica en test) | Documentada; análisis en CMP-4 |
| Comparación injusta | Mismo preprocesador, split, CV, semilla y `evaluate.py` |
| Código del agente que nadie entiende | DoD: el autor explica el código; revisión cruzada; prompts piden código simple |
| Conflictos de merge | Un archivo por modelo y por etapa ETL; `CODEOWNERS` |
| Aportes desequilibrados | Revisar código, documentación, integración y revisiones; no usar solo la cantidad de commits |
| ETL cambia etiquetas y deja resultados viejos | Re-entrenar tras cualquier cambio de ETL; `--reset` documentado |

## 8. Cronograma interno (ajustable; no es una fecha oficial de entrega)

| Semana | Fechas | Foco |
|---|---|---|
| 1 | 26 oct – 1 nov | Fase 0 completa · ETL-1…4 en paralelo · CMP-1 |
| 2 | 2 – 8 nov | ETL-5, ETL-6 · DB-1/2 · MC-1…3 · X-1 y X-2 de cada modelo |
| 3 | 9 – 15 nov | MC-4 · X-3 y X-4 (baseline y tuning) · VIZ-1/2 |
| 4 | 16 – 22 nov | X-5 a X-7 · CMP-2 |
| 5 | 23 – 29 nov | CMP-3 a CMP-5 · V-1 |
| 6 | 30 nov – 6 dic | F-1…F-4: revisión cruzada, informe y demo |
