# Tareas del Integrante A — Datos, Base de datos y Logistic Regression

Complementa a `docs/02_planificacion/PLAN_SDD.md` (qué y cuándo) y `docs/03_guias/GUIA_EQUIPO.md` (cómo). Cada ficha trae un **prompt listo para pegar en tu agente de IA** (Claude Code). Antes de pegar cualquier prompt, seguí el *arranque de tarea* de `docs/03_guias/GUIA_EQUIPO.md §3` (rama nueva, `git pull`, agente abierto en la raíz del repo para que lea `docs/03_guias/CLAUDE.md`).

**Tu foco:** que los datos entren limpios y trazables a SQLite, la capa de persistencia (`repository`) y el modelo **Logistic Regression**.

## Cómo elegir la siguiente tarea

El orden, responsables y dependencias se mantienen en el [plan SDD](../../02_planificacion/PLAN_SDD.md#5-tareas). Las fichas de abajo explican cómo ejecutar cada entrega; no mantienen un segundo calendario. Prepará borradores si falta una dependencia, pero no la des por cerrada ni implementes un contrato no aprobado.

**Revisás los PRs de:** Angel Zambrano (rotación A→B→Angel Zambrano→A, tus PRs los revisa B).

---

## T-02 · Diccionario de datos y unidades
**Depende de:** T-00 · **Rama:** `docs/T-02-diccionario` · **Entregable:** `docs/06_datos/data_dictionary.md`

**Contexto:** el zip trae un diccionario base con los hallazgos ya verificados. Tu trabajo es validarlo contra el CSV y completar lo que no se puede inferir (unidades).

**Prompt para el agente**
```text
Tarea T-02. Revisá docs/06_datos/data_dictionary.md contra data/raw/demanda_electricidad_original_mensual1.csv.
1) Con pandas, verificá cada afirmación numérica del documento (rangos, nulos por columna, cobertura de
   distribuidoras, suma de sectores = demanda_total, correlación de potencia_maxima). Mostrame el comando y
   el resultado de cada verificación. Si algo no coincide, corregí el documento.
2) Asegurate de que las 30 columnas del CSV estén descriptas.
3) Dejá marcado como "PENDIENTE" lo que no se pueda saber del archivo (unidades de demanda y potencia).
   No inventes unidades.
No toques código ni config.
```
**Aceptación**
- Las 30 columnas documentadas; cada hallazgo con su verificación reproducible.
- Unidades marcadas como PENDIENTE hasta confirmarlas con la fuente (D7).

**Commits sugeridos:** `docs(T-02): agrega estructura y disponibilidad por columna` → `docs(T-02): documenta hallazgos de calidad verificados` → `docs(T-02): marca unidades pendientes de confirmar`

**Revisá vos:** que cada número del documento lo hayas visto salir de un comando, no del agente "de memoria".

---

## ETL-1 · Extract
**Depende de:** T-02 · **Rama:** `feat/ETL-1-extract` · **Entregable:** `src/demanda/etl/extract.py` + tests

**Referencia:** `src/demanda/etl/extract.py` del zip (ya funciona sobre el CSV real).

**Prompt para el agente**
```text
Tarea ETL-1 (Extract). Seguí docs/03_guias/CLAUDE.md y docs/07_especificaciones/01-datos.md (criterio ETL-1).
Orden obligatorio: 1) escribí primero los tests en tests/test_extract.py, 2) implementá
src/demanda/etl/extract.py, 3) documentá. Usá como punto de partida el archivo de referencia que te
paso, pero explicame cada decisión.
extract(csv_path, cfg) debe: leer el CSV en UTF-8, normalizar nombres de columnas (strip + minúsculas),
parsear la columna de fecha de cfg["etl"]["columna_fecha"] a datetime y fallar con un mensaje claro si la
columna no existe. NO debe imputar, descartar ni convertir valores. sha256_file(path) devuelve la huella
del archivo. Tests: CSV real (308 filas, primera fecha 2001-01-01), columna de fecha ausente, nombres con
espacios/mayúsculas, huella estable entre dos lecturas.
```
**Aceptación:** `pytest tests/test_extract.py` verde · no modifica valores · error claro si falta la fecha · `ruff` limpio.

**Commits:** `test(ETL-1): tests de lectura, fecha ausente y huella` → `feat(ETL-1): implementa extract y sha256_file` → `docs(ETL-1): docstrings y ejemplo de uso`

**Revisá vos:** que el test de "fecha ausente" realmente falle antes de implementar (si pasa de entrada, el test no prueba nada).

---

## T-03 · `schema.sql`
**Depende de:** T-01 · **Rama:** `feat/T-03-schema` · **Entregable:** `src/demanda/db/schema.sql` + test

**Referencia:** `src/demanda/db/schema.sql` del zip (Tabla 1, 2, 3 y extras `demanda_distribuidora`, `etl_auditoria`).

**Prompt para el agente**
```text
Tarea T-03. Revisá src/demanda/db/schema.sql contra docs/06_datos/data_dictionary.md y docs/07_especificaciones/01-datos.md.
Verificá: clave primaria `fecha` en datos_limpios, CHECKs (etiqueta en Normal/Alta/Crítica, split train/test,
mes 1..12), `CREATE TABLE IF NOT EXISTS` en todo, tablas de resultados (predicciones, metricas_modelo,
config_modelo) con las columnas del contrato. Escribí tests/test_schema.py que cree una BD vacía, verifique
que las 6 tablas existen, que ejecutar el script dos veces no falla y que un INSERT con etiqueta inválida
es rechazado. Hacé cambios mínimos y justificá cada uno.
```
**Aceptación:** las 6 tablas se crean desde cero · idempotente · CHECKs rechazan datos inválidos.

**Commits:** `test(T-03): tests de creación e idempotencia del esquema` → `feat(T-03): ajusta schema.sql a las decisiones de T-01` → `docs(T-03): documenta tablas y claves en el diccionario`

**Revisá vos:** que las claves de `metricas_modelo` y `config_modelo` coincidan con lo que `save_run` (DB-2) y `evaluate` (B) van a usar.

---

## ETL-3 · Transform
**Depende de:** T-01 · **Rama:** `feat/ETL-3-transform` · **Entregable:** `src/demanda/etl/transform.py` + tests

**Referencia:** `src/demanda/etl/transform.py` del zip. Implementa calendario, participaciones, etiqueta (`relativo_tendencia` o `percentil_global`), split cronológico y tabla larga de distribuidoras.

**Prompt para el agente**
```text
Tarea ETL-3 (Transform). Seguí docs/03_guias/CLAUDE.md y docs/07_especificaciones/01-datos.md (criterios ETL-3, 5, 6, 9) y las decisiones
D1–D7 aprobadas en T-01. Tests primero (tests/test_transform.py), después implementación.
Reglas no negociables: (a) los nulos de sectores y distribuidoras NO se imputan; (b) los umbrales de la
etiqueta, incluidos scores y percentiles de train, no dependen de test; (c) el split es cronológico con la
fracción de config.yaml; (d) la salida tiene exactamente las columnas de la tabla datos_limpios.
Tests obligatorios: participaciones suman 1 donde hay sectores; estación correcta en dic/ene (hemisferio
sur); cambiar los datos de test NO modifica scores, umbrales ni etiquetas de train, probando el método
configurado y las alternativas soportadas (test "sin fuga"); método de etiqueta
desconocido lanza ValueError; las distribuidoras salen en formato largo sin nulos.
Después corré el ETL sobre el CSV real y mostrame la distribución de etiquetas por split.
```
**Aceptación:** `pytest tests/test_transform.py` verde · independencia temporal del método elegido demostrada · distribución real registrada con la decisión aprobada, sin exigir conservar conteos del método defectuoso de referencia.

**Commits:** `test(ETL-3): tests de calendario, participaciones y sin fuga` → `feat(ETL-3): implementa features de calendario y participaciones` → `feat(ETL-3): implementa etiqueta con umbrales de train y split cronológico` → `docs(ETL-3): documenta método de etiqueta en docs/07_especificaciones/01-datos.md`

**Revisá vos:** el test "sin fuga": modificar solo test debe dejar intactos los cálculos de train; no alcanza probar una alternativa distinta de la configurada.

---

## DB-2 · `save_run()` — persistencia de resultados (Tablas 2 y 3)
**Depende de:** T-03 · **Rama:** `feat/DB-2-save-run` · **Entregable:** `src/demanda/db/repository.py` (parte escritura) + tests

**Sin código de referencia:** el agente lo construye desde la spec.

**Prompt para el agente**
```text
Tarea DB-2. Creá src/demanda/db/repository.py con:
save_run(run_id, predictions_df, metrics_dict, config_dict, db_path=None) -> None
- Escribe en predicciones, metricas_modelo y config_modelo en UNA transacción (todo o nada).
- predictions_df columnas: fecha, modelo, y_real, y_pred, prob_normal, prob_alta, prob_critica.
- metrics_dict claves: modelo, accuracy, precision_macro, recall_macro, f1_macro, precision_/recall_/f1_
  {normal,alta,critica}, matriz_confusion (lista de listas, se guarda como JSON, orden Normal/Alta/Crítica),
  cv_best_score, tiempo_entrenamiento_s, n_train, n_test.
- config_dict claves: modelo, grid_hiperparametros, mejores_params, umbrales_etiqueta, features_usadas,
  semilla, cv_folds, scoring (los dicts/listas se guardan como JSON).
- run_id repetido => error claro (no sobrescribir en silencio). db_path por defecto desde config.yaml.
Tests primero con una BD temporal: guarda y relee las 3 tablas; run_id duplicado falla; si falla la
inserción de predicciones no queda NADA en metricas_modelo (rollback); los JSON se pueden leer de vuelta.
Documentá estas claves en docs/07_especificaciones/00-contratos.md (es un contrato con B y Angel Zambrano, abrilo como PR aparte si T-01 ya está mergeado).
```
**Aceptación:** transacción única · rollback comprobado por test · contrato documentado y aprobado por B y Angel Zambrano.

**Commits:** `docs(DB-2): documenta el contrato de save_run en docs/07_especificaciones/00-contratos.md` → `test(DB-2): tests de persistencia, duplicados y rollback` → `feat(DB-2): implementa save_run transaccional`

**Revisá vos:** que `run_id` duplicado no pise resultados de otro modelo.

---

## DB-1 · `load_clean_data()`
**Depende de:** ETL-5 · **Rama:** `feat/DB-1-load-clean-data` · **Entregable:** `repository.py` (parte lectura) + tests

**Prompt para el agente**
```text
Tarea DB-1. En src/demanda/db/repository.py agregá
load_clean_data(db_path=None, desde_sectores=False) -> pd.DataFrame
Devuelve datos_limpios ordenado por fecha, con `fecha` como datetime y NULL como NaN. Con
desde_sectores=True devuelve solo filas con tiene_sectores = 1. Tests con una BD temporal cargada por el
ETL sobre el CSV real: 308 filas; con desde_sectores=True son 260 y la primera fecha es 2005-01-01;
las columnas son exactamente las de la tabla; está ordenado. No recalcules etiqueta ni split.
```
**Aceptación:** devuelve 308 / 260 filas según el flag · sin recalcular nada · tests verdes.

**Commits:** `test(DB-1): tests de lectura y filtro de sectores` → `feat(DB-1): implementa load_clean_data` → `docs(DB-1): documenta el contrato de lectura`

---

## LR-1 … LR-7 · Modelo Logistic Regression
Prefijo `LR-`. Rama `feat/LR-N-<slug>`. Archivos: `docs/07_especificaciones/02-modelo-logreg.md`, `src/demanda/models/logreg.py`, `tests/test_logreg.py`, `notebooks/02_logreg.ipynb`.
Todas las tareas usan el **mismo preprocesador, split, CV y `evaluate`** que los otros dos modelos: no los reimplementes.

### LR-1 · Spec del modelo
**Depende de:** T-01 · **Entregable:** `docs/07_especificaciones/02-modelo-logreg.md`
```text
Tarea LR-1. Escribí docs/07_especificaciones/02-modelo-logreg.md: por qué Logistic Regression en este problema (baseline
lineal e interpretable, necesita escalado), tratamiento del desbalance (class_weight='balanced'), la grilla
de GridSearchCV (C en [0.01,0.1,1,10,100], solver lbfgs/saga, penalty l2; justificá el rango), el scoring
(f1_macro) y los criterios de aceptación de LR-2…LR-7. Mencioná la limitación: 246 meses de train y la clase
Alta es chica. No escribas código.
```
**Commits:** `docs(LR-1): justifica el modelo y el tratamiento del desbalance` → `docs(LR-1): define grilla y criterios de aceptación`

### LR-2 · Módulo del modelo
**Depende de:** LR-1, T-03 · **Entregable:** `models/logreg.py` + `tests/test_logreg.py`
```text
Tarea LR-2. Tests primero. Implementá src/demanda/models/logreg.py con el contrato de modelos de docs/03_guias/CLAUDE.md:
NAME="logreg", SEARCH="grid", get_estimator(random_state) -> LogisticRegression(max_iter=2000,
class_weight="balanced", random_state=random_state), get_param_grid() con claves "clf__C", "clf__solver",
"clf__penalty" según la spec LR-1, get_n_iter() -> None. Tests: el estimador tiene predict_proba y
class_weight balanced; todas las claves de la grilla empiezan con "clf__"; get_n_iter es None.
No toques otros archivos de models/.
```
**Commits:** `test(LR-2): test del contrato del módulo logreg` → `feat(LR-2): implementa logreg con class_weight balanced` → `docs(LR-2): docstrings`

### LR-3 · Baseline sin tuning
**Depende de:** LR-2, MC-1, MC-2, MC-3 · **Entregable:** baseline reproducible + métrica de referencia
```text
Tarea LR-3. Con el pipeline común (build_preprocessor del set "base") y el split de la columna `split`,
entrená LogisticRegression con parámetros por defecto (sin búsqueda) mediante CV temporal de train.
Calculá la referencia con evaluate.py; reservá test para LR-5 y no lo uses para elegir parámetros. Dejalo como
función/script reproducible con la semilla de config.yaml y mostrame los números. Si MC-1/MC-2 no están
mergeados, usá el contrato y avisame qué stub usaste.
```
**Commits:** `test(LR-3): test de reproducibilidad del baseline` → `feat(LR-3): baseline de logreg con el pipeline común`

### LR-4 · Búsqueda de hiperparámetros
**Depende de:** LR-3 · **Entregable:** mejores parámetros y `cv_best_score`
```text
Tarea LR-4. Ejecutá GridSearchCV sobre el Pipeline (prep + clf) con la grilla de logreg.py, cv=TimeSeriesSplit
común (splits.get_cv), scoring="f1_macro", n_jobs=-1, SOLO sobre las filas train. Registrá mejores
parámetros, cv_best_score y el tiempo. Verificá que ninguna fila de test participa del ajuste ni de la CV.
Si el runner (MC-4) ya existe usalo: python -m demanda.models.train --model logreg --features base.
Reportá si la mejora sobre el baseline es significativa o está dentro del ruido (pocas filas).
```
**Commits:** `feat(LR-4): GridSearchCV con CV temporal y scoring f1_macro` → `test(LR-4): test de que la CV no usa filas de test` → `docs(LR-4): resultados y tiempos en la spec`

### LR-5 · Evaluación y ablación
**Depende de:** LR-4, MC-3 · **Entregable:** métricas y matrices por conjunto de features
```text
Tarea LR-5. Evaluá el mejor modelo en test con evaluate.py: Accuracy, Precision, Recall, F1 (macro y por
clase) y matriz de confusión. Repetí con los 3 feature_sets de config.yaml (base, con_participaciones,
sin_potencia) y armá una tabla comparativa. Para con_participaciones usá solo filas con tiene_sectores=1
(set con solo_con_sectores=true). Interpretá: ¿cuánto depende el modelo de potencia_maxima? No saques
conclusiones que los números no sostengan; reportá los conteos de clase de la corrida real.
```
**Commits:** `feat(LR-5): evaluación en test con evaluate.py` → `feat(LR-5): ablación de features` → `docs(LR-5): tabla comparativa de feature sets`

### LR-6 · Persistencia
**Depende de:** LR-5, MC-4, DB-2 · **Entregable:** filas de `logreg` en `demanda.db`
```text
Tarea LR-6. Guardá los resultados con save_run usando run_id único (ej. logreg_base_<timestamp>), uno por
feature set. Verificá releyendo con SQL que predicciones, metricas_modelo y config_modelo tienen las
filas esperadas (n_test filas de predicciones por run), que la matriz de confusión se parsea como JSON y
que features_usadas coincide con el set elegido. Correlo con la BD real generada por run_etl.py.
```
**Commits:** `feat(LR-6): persiste runs de logreg en Tablas 2 y 3` → `test(LR-6): verifica filas y JSON guardados`

### LR-7 · Notebook e interpretación
**Depende de:** LR-6 · **Entregable:** `notebooks/02_logreg.ipynb` + sección en `docs/08_entrega/model_card.md`
```text
Tarea LR-7. Notebook que lee SOLO desde demanda.db (no reentrena): métricas, matriz de confusión,
coeficientes por clase con los nombres de columnas del preprocesador (usá get_feature_names_out) y gráfico
de los más influyentes, y análisis de errores (qué meses se confunden y por qué: estacionalidad, deriva
del pico). Cerrá con limitaciones honestas (muestra chica, clase Alta casi ausente en test).
```
**Commits:** `docs(LR-7): notebook de métricas y coeficientes` → `docs(LR-7): análisis de errores y limitaciones en model_card`

---

## CMP-2 · `compare_runs()`
**Depende de:** LR-6, RF-6, XG-6, CMP-1 · **Rama:** `feat/CMP-2-compare-runs` · **Entregable:** función en `repository.py` + tests
```text
Tarea CMP-2. Agregá a repository.py compare_runs(run_ids=None, db_path=None) -> pd.DataFrame con una fila
por run: modelo, feature set, accuracy, precision/recall/F1 macro, F1 y recall de cada clase, cv_best_score,
tiempo y n_test. Verificá que todos los runs comparados comparten el mismo split y semilla (config_modelo) y
avisá si no. Tests con la BD fixture de Angel Zambrano (VIZ-2): ordena por f1_macro, filtra por run_ids, advierte si hay
semillas distintas. Sin lógica de decisión: el criterio de elección está en docs/07_especificaciones/03-comparacion.md.
```
**Commits:** `test(CMP-2): tests de ordenamiento, filtro y semillas` → `feat(CMP-2): implementa compare_runs` → `docs(CMP-2): documenta columnas devueltas`

---

## Tareas conjuntas (las tres personas)

| ID | Tu parte |
|---|---|
| **T-01** | Redactar `docs/07_especificaciones/01-datos.md` (decisiones D1–D7) y presentar los hallazgos del ETL |
| **CMP-1** | Aportar los criterios de comparación; proponer la métrica de desempate |
| **CMP-5** | Decisión final del modelo aplicando CMP-1 |
| **F-2** | Revisar los PRs de Angel Zambrano |
| **F-3 / F-4** | Sección "Datos, ETL y Logistic Regression" del informe; ensayo de demo |

## Verificación personal de A

El cierre formal está en el plan y el estado se registra en avance general. Antes de entregar, comprobá también:

- [ ] Puedo explicar la etiqueta, el split y por qué no hay fuga.
