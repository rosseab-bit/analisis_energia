# Tareas de Angel Zambrano — Infraestructura, Load del ETL, Visualización y XGBoost

Para ejecutar estas tareas de a poco, consultá [tu plan personal](PLAN_PERSONAL_ANGEL.md). Los pasos del plan no agregan nuevas tareas ni reemplazan sus dependencias.

Complementa a `docs/02_planificacion/PLAN_SDD.md` (qué y cuándo) y `docs/03_guias/GUIA_EQUIPO.md` (cómo). Cada ficha trae un **prompt listo para pegar en tu agente de IA** (Claude Code). Antes de pegar un prompt, seguí el *arranque de tarea* de `docs/03_guias/GUIA_EQUIPO.md §3` (rama nueva, `git pull`, agente abierto en la raíz del repo para que lea `docs/03_guias/CLAUDE.md`). La única excepción es **T-00**, que arranca antes de que exista el repo.

**Responsable: Angel Zambrano.** C se conserva como identificador interno en el nombre de esta ficha, `GH_USER_C`, `persona-C` y los marcadores `<C>` (tu usuario real de GitHub). Guía práctica: [Plan personal de Angel](PLAN_PERSONAL_ANGEL.md).

**Tu foco:** dejar el repositorio y la CI funcionando desde el día 1 (de eso depende que los otros dos puedan trabajar), cargar los datos a SQLite de forma segura (Load), todo lo visual (gráficos y dashboard) y el modelo **XGBoost**.

## Cómo elegir la siguiente tarea

El orden, responsables y dependencias se mantienen en el [plan SDD](../../02_planificacion/PLAN_SDD.md#5-tareas). Las fichas de abajo explican cómo ejecutar cada entrega; no mantienen un segundo calendario. Prepará borradores si falta una dependencia, pero no la des por cerrada ni implementes un contrato no aprobado.

**Revisás los PRs de:** B (tus PRs los revisa A).

---

## T-00 · Completar el repositorio y la infraestructura
**Depende de:** nada · **Rama:** `chore/T-00-esqueleto` · **Entregable:** repo instalable y proceso de trabajo verificado.

El repo y el ETL de referencia ya están versionados. No recrear el repo, retirar módulos de otros integrantes ni hacer otro commit inicial directo en `main`.

**Prompt para el agente**
```text
Tarea T-00. Revisá el estado existente y completá solo la infraestructura pendiente.
1) Verificá usuarios reales y mapa de dueños: A, extract/transform, db/ y logreg;
   B, validate, módulos comunes y rf; Angel Zambrano, load/pipeline, CLI ETL, viz y xgb.
   Specs y configuración son compartidas. Prepará CODEOWNERS sin usuarios inventados.
2) Prepará .github/pull_request_template.md con resumen, Closes #N, validación,
   definición de hecho del plan y checklist del revisor de la guía del equipo.
3) Contrastá instalación y comandos con docs/00_inicio/README.md. Verificá el paquete,
   load_config y la semilla esperada. Registrá errores sin ocultarlos.
4) Revisá scripts/crear_issues.sh en modo de prueba. Las tareas provienen del plan;
   no escribas otro catálogo ni ejecutes la publicación sin mi indicación.
5) Mostrame cambios y evidencia, y proponé commits solo para cambios reales.
   No hagas commit, push ni cambios remotos.
```

**Configuración que debe confirmar la persona con permisos de administración:** acceso de A/B, PR y aprobación en `main`, sin force-push, merge commits sin squash. El check obligatorio se incorpora después de ejecutar T-15. Confirmar que A/B instalan sus copias.

**Issues:** el único generador es `scripts/crear_issues.sh`; funciona con Bash 3.2 y Python 3 estándar. `DRY_RUN=1 bash scripts/crear_issues.sh` valida sin `gh` ni cambios externos. Para publicar requiere `gh` autenticado y `GH_USER_A/B/C`; si ya hay issues, se completan manualmente para evitar duplicados.

**Aceptación:** instalación y configuración verificadas por el equipo; dueños, plantilla, acceso y reglas confirmados; issues organizados y seguimiento disponible. Los borradores de archivos no acreditan por sí solos la configuración remota.

**Ejemplos de commits si corresponden al diff:** `chore(T-00): define dueños y plantilla de PR`, `docs(T-00): aclara instalación verificada`. La definición de hecho exige aportes reales, no recrear archivos para cumplir un número.

---

## T-15 · CI en GitHub Actions
**Depende de:** T-00 · **Rama:** `chore/T-15-ci` · **Entregable:** `.github/workflows/ci.yml`
```text
Tarea T-15. Creá .github/workflows/ci.yml que en cada push y pull_request: use Python 3.11 con caché de pip,
instale requirements.txt y `pip install -e .`, corra `ruff check src tests` y `pytest -q`. Un solo job
llamado "test". Ya existen tests: no tolerar "no tests collected" ni ocultar fallos de lint o pytest.
Después de mergear, indicame cómo marcar el job "test" como required check en la regla de protección de main.
```
**Aceptación:** el job corre en un PR de prueba y queda como *required* · falla si el lint o un test falla.

**Commits:** `chore(T-15): workflow de CI con ruff y pytest` → `docs(T-15): cómo marcar el check como obligatorio`

---

## ETL-4 · Load
**Depende de:** T-03 · **Rama:** `feat/ETL-4-load` · **Entregable:** `src/demanda/etl/load.py` + tests

**Referencia:** `src/demanda/etl/load.py` del zip.

**Prompt para el agente**
```text
Tarea ETL-4 (Load). Seguí docs/03_guias/CLAUDE.md y docs/07_especificaciones/01-datos.md (criterios ETL-7 y ETL-8). Tests primero
(tests/test_load.py) con una BD temporal (tempfile), después implementación.
Funciones: connect(db_path), init_schema(conn, schema_path, reset=False) y
load(conn, datos_limpios, distribuidoras, auditoria) -> dict.
Requisitos: (a) la carga es ATÓMICA: `with conn:` y si algo falla no queda nada a medias; (b) IDEMPOTENTE:
correr dos veces deja 308 filas, no 616, y 2 filas en etl_auditoria; (c) NaN se guarda como NULL; (d) NO
borra predicciones/metricas_modelo/config_modelo (solo reset=True las borra); (e) etl_run_id incluye
microsegundos (dos corridas en el mismo segundo no pueden pisarse). Tests: idempotencia, NULL en sectores
anteriores a 2005, rollback (un valor que viola un CHECK deja la corrida anterior intacta), que reset=True
borra los resultados de modelos y reset=False los conserva.
```
**Aceptación:** los 5 comportamientos probados · sin SQL armado con datos del usuario (solo `?` para valores).

**Commits:** `test(ETL-4): tests de idempotencia, NULL, rollback y reset` → `feat(ETL-4): carga transaccional e idempotente` → `feat(ETL-4): auditoría de corrida con SHA-256` → `docs(ETL-4): política de re-ejecución en docs/03_guias/GUIA_EQUIPO.md`

**Revisá vos:** el test de rollback debe romper algo *a mitad de la carga* (no antes de empezar) para probar de verdad la atomicidad.

---

## ETL-5 · Pipeline + CLI
**Depende de:** ETL-1, ETL-2, ETL-3, ETL-4 · **Rama:** `feat/ETL-5-pipeline` · **Entregable:** `etl/pipeline.py`, `scripts/run_etl.py`, test de integración

**Referencia:** `pipeline.py` y `scripts/run_etl.py` del zip.

**Prompt para el agente**
```text
Tarea ETL-5. Creá etl/pipeline.py con run_etl(config_path=None, reset=False, csv_path=None, db_path=None)
que encadena extract -> assert_valid -> transform -> init_schema -> load y devuelve un resumen (filas,
umbrales, advertencias, distribución de etiquetas por split). scripts/run_etl.py es el CLI (argparse:
--config, --reset): imprime el resumen, y si la validación falla imprime el error y sale con código 1 SIN
escribir nada en la BD. Test de integración con el CSV real y una BD temporal: 308 filas en datos_limpios,
3450 en demanda_distribuidora (150 meses x 23 distribuidoras), sectores desde 2005-01-01, las 3 clases
presentes en train, 1 fila de auditoría. Test de CLI: un CSV inválido (fecha duplicada) devuelve 1 y deja la
BD vacía de datos. Al terminar corré `python scripts/run_etl.py` y pegame la salida.
```
**Aceptación:** `python scripts/run_etl.py` genera `db/demanda.db` · falla limpio con datos inválidos · **avisar a A y B apenas esté mergeado** (los desbloquea).

**Commits:** `test(ETL-5): integración con el CSV real y caso inválido` → `feat(ETL-5): run_etl encadena E-V-T-L` → `feat(ETL-5): CLI run_etl.py con --reset` → `docs(ETL-5): comando en README`

---

## VIZ-2 · BD fixture para tests y dashboard
**Depende de:** T-03 · **Rama:** `test/VIZ-2-fixture` · **Entregable:** `tests/fixtures.py`
```text
Tarea VIZ-2. Creá tests/fixtures.py con make_fixture_db(path) que crea una BD con el schema.sql real y la llena
con DATOS FICTICIOS pero con la forma exacta de las tablas: 36 meses en datos_limpios (con etiquetas y split),
y 3 runs de resultados (run_id con prefijo "fixture_", modelos logreg/rf/xgb) en predicciones,
metricas_modelo y config_modelo, con métricas inventadas pero coherentes (matriz de confusión que suma
n_test). Marcá los datos como ficticios en comentarios y en un campo reconocible (prefijo fixture_) para
que nunca se confundan con resultados reales. Tests que verifiquen que las 3 tablas quedan pobladas y que
respeta los CHECKs. Es lo que usarán A (CMP-2) y vos (VIZ-1, CMP-3, V-1) para trabajar sin esperar a los modelos.
```
**Commits:** `test(VIZ-2): fixture con datos ficticios y 3 runs` → `docs(VIZ-2): aclara que son datos ficticios`

---

## VIZ-1 · `plots.py` base
**Depende de:** ETL-5 · **Rama:** `feat/VIZ-1-plots` · **Entregable:** `src/demanda/viz/plots.py` + tests de humo
```text
Tarea VIZ-1. Creá src/demanda/viz/plots.py con funciones PURAS (reciben DataFrames, devuelven una figura de
matplotlib o plotly; no leen la BD ni llaman a plt.show): plot_clases_por_split, plot_demanda_vs_temperatura
(dispersión coloreada por etiqueta), plot_estacionalidad (perfil por mes con la banda por año),
plot_serie_con_criticos (serie de demanda_total con los meses Crítica marcados y la línea de corte
train/test). Títulos, ejes y leyendas en español, con unidades "PENDIENTE" si D7 no está resuelto. Paleta que
distinga Normal/Alta/Crítica de forma accesible (no solo por color: usá también marcador o forma). Tests de
humo con la fixture (VIZ-2): cada función devuelve una figura y no lanza con una BD de 36 meses ni con la real.
```
**Aceptación:** 4 funciones puras · accesibles (no dependen solo del color) · tests de humo verdes.

**Commits:** `test(VIZ-1): tests de humo de cada gráfico` → `feat(VIZ-1): gráficos de clases y demanda vs temperatura` → `feat(VIZ-1): gráficos de estacionalidad y serie con críticos`

---

## XG-1 … XG-7 · Modelo XGBoost
Archivos: `docs/07_especificaciones/02-modelo-xgb.md`, `src/demanda/models/xgb.py`, `tests/test_xgb.py`, `notebooks/04_xgb.ipynb`. Mismo preprocesador, split, CV y `evaluate` que los otros dos (no los reimplementes).

### XG-1 · Spec del modelo
**Depende de:** T-01 · **Entregable:** `docs/07_especificaciones/02-modelo-xgb.md` + acuerdo con B
```text
Tarea XG-1. Escribí docs/07_especificaciones/02-modelo-xgb.md: por qué XGBoost (boosting, interacciones no lineales), y los DOS puntos
delicados: (1) etiquetas: XGBoost requiere clases enteras; el módulo debe codificar/decodificar
internamente para que el sistema siga viendo "Normal/Alta/Crítica"; (2) desbalance: en multiclase no hay
class_weight; se usan pesos balanceados. Acordá con B el contrato NEEDS_SAMPLE_WEIGHT y dónde se calculan:
cada fit de CV debe calcularlos solo con las filas de entrenamiento de su fold; el ajuste final usa
train completo. Documentá la interfaz elegida antes del código. Pasar un vector calculado con todo
train no resuelve la independencia de cada fold. Espacio de RandomizedSearchCV (n_estimators [100,200,400],
max_depth [3,5,7], learning_rate [0.03,0.1,0.3], subsample/colsample_bytree [0.7,0.9,1.0], reg_lambda
[1,5,10], n_iter=30; justificá con 246 filas de train). Criterios de aceptación de XG-2…XG-7. Sin código.
Dejá el contrato NEEDS_SAMPLE_WEIGHT como PR a docs/07_especificaciones/00-contratos.md para que lo apruebe B (MC-4).
```
**Commits:** `docs(XG-1): justifica el modelo, etiquetas enteras y sample_weight` → `docs(XG-1): espacio de búsqueda y criterios` → `docs(XG-1): propone contrato NEEDS_SAMPLE_WEIGHT`

### XG-2 · Módulo del modelo
**Depende de:** XG-1, T-03 · **Entregable:** `models/xgb.py` + `tests/test_xgb.py`
```text
Tarea XG-2. Tests primero. Implementá src/demanda/models/xgb.py con el contrato de docs/02_planificacion/PLAN_SDD.md §2.4: NAME="xgb",
SEARCH="random", NEEDS_SAMPLE_WEIGHT=True, get_estimator(random_state), get_param_grid() (claves "clf__..."),
get_n_iter() -> 30. get_estimator debe devolver un estimador compatible con sklearn que ACEPTE y DEVUELVA las
etiquetas de texto ("Normal","Alta","Crítica"): un wrapper (o subclase de XGBClassifier) que codifique con
LabelEncoder en fit y decodifique en predict, y exponga classes_ con los strings. Tiene que funcionar con
sklearn.base.clone, dentro de Pipeline y de RandomizedSearchCV. Tests: fit/predict con etiquetas de texto;
predict_proba tiene 3 columnas en el orden de classes_; clone() conserva los parámetros; sample_weight llega
al fit. CUIDADO: el orden de classes_ es alfabético (Alta, Crítica, Normal), no (Normal, Alta, Crítica): el
runner y save_run deben mapear las probabilidades por NOMBRE de clase, no por posición. Dejalo escrito en la spec.
```
**Commits:** `test(XG-2): tests de etiquetas de texto, clone y sample_weight` → `feat(XG-2): wrapper de XGBClassifier con etiquetas de texto` → `docs(XG-2): orden de classes_ y mapeo de probabilidades`

### XG-3 · Baseline
**Depende de:** XG-2, MC-1, MC-2, MC-3
```text
Tarea XG-3. Con build_preprocessor(cfg, "base") y el split de la columna `split`, entrená XGBoost con parámetros por
defecto y sample_weight balanceado, obtené métricas de referencia mediante la validación temporal de train con evaluate.py.
No uses test para comparar decisiones de pesos ni seleccionar parámetros. Mostrame los números. Verificá que sample_weight realmente se usa (compará con y
sin él) y reportá la diferencia.
```
**Commits:** `test(XG-3): test de reproducibilidad` → `feat(XG-3): baseline de xgb con sample_weight`

### XG-4 · Búsqueda de hiperparámetros
**Depende de:** XG-3
```text
Tarea XG-4. RandomizedSearchCV (n_iter=30, random_state=semilla) sobre Pipeline(prep+clf), cv=get_cv(cfg),
scoring f1_macro, SOLO con train y el contrato de pesos aprobado en XG-1. Probá que cada fit calcula
los pesos solo con las clases y filas de entrenamiento de su fold, sin frecuencias de validación.
No basta con alinear un vector balanceado previamente sobre todo train. Registrá mejores parámetros,
cv_best_score y tiempo. La comparación con test se informa después, en XG-5, sin usarla para ajustar la búsqueda.
```
**Commits:** `feat(XG-4): RandomizedSearchCV con CV temporal` → `test(XG-4): test de alineación de sample_weight por fold` → `docs(XG-4): resultados y decisión sobre sample_weight`

### XG-5 · Evaluación y ablación
**Depende de:** XG-4, MC-3
```text
Tarea XG-5. Evaluá el mejor XGBoost en test con evaluate.py y repetí con los 3 feature_sets (base,
con_participaciones, sin_potencia). Tabla comparativa y lectura honesta, con conteos de clase medidos en la corrida evaluada.
```
**Commits:** `feat(XG-5): evaluación en test` → `feat(XG-5): ablación por feature set` → `docs(XG-5): tabla comparativa`

### XG-6 · Persistencia
**Depende de:** XG-5, MC-4, DB-2
```text
Tarea XG-6. Persistí con save_run (run_id único por feature set, ej. xgb_base_<timestamp>). Verificá con SQL: las
probabilidades están en las columnas correctas (prob_normal/alta/critica mapeadas por NOMBRE de clase: comprobá
que la suma por fila ≈ 1 y que la columna prob_critica es la más alta en los meses y_pred="Crítica"),
matriz de confusión parseable, mismos semilla y split que logreg y rf.
```
**Commits:** `feat(XG-6): persiste runs de xgb en Tablas 2 y 3` → `test(XG-6): verifica probabilidades por clase y JSON`

### XG-7 · Notebook e interpretación
**Depende de:** XG-6 · **Entregable:** `notebooks/04_xgb.ipynb` + sección en `docs/08_entrega/model_card.md`
```text
Tarea XG-7. Notebook que lee desde demanda.db: métricas, matriz de confusión, importancia por gain (y SHAP si hay
tiempo y la librería está en requirements), y análisis de errores (meses confundidos, deriva del pico
estacional). Limitaciones honestas.
```
**Commits:** `docs(XG-7): notebook de métricas e importancias` → `docs(XG-7): análisis de errores en model_card`

---

## CMP-3 · Gráficos de comparación
**Depende de:** CMP-2, VIZ-1 · **Rama:** `feat/CMP-3-plots-comparacion` · **Entregable:** funciones nuevas en `plots.py`
```text
Tarea CMP-3. Agregá a plots.py (funciones puras que reciben el DataFrame de compare_runs y/o las
matrices de confusión): plot_metricas_por_modelo (barras agrupadas de accuracy, precision, recall y F1 macro),
plot_matrices_confusion (una por modelo, lado a lado, misma escala), plot_f1_por_clase, plot_tiempos y
plot_ablacion (F1 macro por modelo × feature set). Incluí en cada gráfico el n_test y los conteos de clase de los runs comparados,
sin hardcodear cifras del ETL de referencia. Tests de humo con la fixture VIZ-2.
```
**Commits:** `test(CMP-3): tests de humo con la fixture` → `feat(CMP-3): métricas y matrices de confusión comparadas` → `feat(CMP-3): F1 por clase, tiempos y ablación`

## V-1 · Dashboard Streamlit
**Depende de:** CMP-3 · **Rama:** `feat/V-1-dashboard` · **Entregable:** `src/demanda/viz/app.py`
```text
Tarea V-1. Dashboard Streamlit que solo LEE db/demanda.db (con @st.cache_data). Barra lateral: modelo(s), feature
set, rango de fechas, clase. Pestañas: "Datos" (VIZ-1), "Modelos" (tabla de métricas y matriz de confusión por
run), "Comparación" (gráficos CMP-3), "Predicciones" (tabla filtrable y serie con aciertos/errores) y
"Calidad de datos" (etl_auditoria: archivo, SHA-256, filas, nulos por tramo, advertencias, umbrales de la
etiqueta). Si la BD no existe o no hay runs, mostrar un mensaje claro con el comando para generarlos, no un
traceback. Test de humo con streamlit.testing.v1.AppTest sobre la BD fixture.
```
**Aceptación:** `streamlit run src/demanda/viz/app.py` funciona con la BD real · mensajes claros sin datos · test de humo verde.

**Commits:** `test(V-1): test de humo del dashboard` → `feat(V-1): pestañas Datos y Modelos` → `feat(V-1): pestañas Comparación y Predicciones` → `feat(V-1): pestaña Calidad de datos desde etl_auditoria`

---

## Tareas conjuntas (las tres personas)

| ID | Tu parte |
|---|---|
| **T-01** | Redactar `docs/07_especificaciones/04-visualizacion.md` (qué muestra el dashboard) y presentar la estructura del repo |
| **CMP-1** | Aportar criterios de presentación de la comparación (qué se grafica y cómo se advierte la incertidumbre) |
| **CMP-5** | Decisión final del modelo |
| **F-2** | Revisar los PRs de B |
| **F-3 / F-4** | Sección "Infraestructura, visualización y XGBoost" del informe; ensayo de demo |

## Verificación personal de Angel Zambrano

El cierre formal está en el plan y el estado se registra en avance general. Antes de entregar, comprobá también:

- [ ] El dashboard no se rompe sin datos.
- [ ] Puedo explicar la atomicidad de la carga y por qué `classes_` está en orden alfabético.
