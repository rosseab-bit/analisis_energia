#!/usr/bin/env bash
# Crea labels, milestones e issues del proyecto en GitHub usando la CLI `gh`.
# Requisitos: gh instalado y autenticado (gh auth login), ejecutar dentro del repo clonado.
#
# Uso:
#   export GH_USER_A="usuario-github-de-A"
#   export GH_USER_B="usuario-github-de-B"
#   export GH_USER_C="usuario-github-de-C"
#   bash scripts/crear_issues.sh
#
# Los issues se crean en orden; cada uno indica "Depende de" por ID de tarea (ej. T-09).
# Al terminar, el script reemplaza los IDs por referencias #N reales (segunda pasada).

set -euo pipefail

: "${GH_USER_A:?Definir GH_USER_A}"
: "${GH_USER_B:?Definir GH_USER_B}"
: "${GH_USER_C:?Definir GH_USER_C}"

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Repositorio: $REPO"

# ---------- Labels ----------
label() { gh label create "$1" --color "$2" --description "$3" --force >/dev/null; }
label "persona-A" "1f77b4" "Responsable: A"
label "persona-B" "2ca02c" "Responsable: B"
label "persona-C" "ff7f0e" "Responsable: C"
label "equipo"    "7f7f7f" "Tarea conjunta"
label "modelo-logreg" "9467bd" "Logistic Regression"
label "modelo-rf"     "8c564b" "Random Forest"
label "modelo-xgb"    "e377c2" "XGBoost"
label "comparacion"   "17becf" "Comparación de métricas"
label "base-compartida" "bcbd22" "Componentes comunes"

# ---------- Milestones ----------
ms() { gh api "repos/$REPO/milestones" -f title="$1" -f description="$2" >/dev/null 2>&1 || true; }
ms "Fase 0 - Fundacion"       "Repo, specs, contratos, schema y config"
ms "Fase 1 - Base compartida" "Datos, BD, preprocesador, split, evaluate, runner, CI"
ms "Fase 2 - Modelos"         "LR (A), RF (B), XGB (C) en paralelo"
ms "Fase 3 - Comparacion"     "Comparacion de metricas y decision del modelo"
ms "Fase 4 - Cierre"          "Dashboard, integracion, informe y demo"

user_for() { case "$1" in A) echo "$GH_USER_A";; B) echo "$GH_USER_B";; C) echo "$GH_USER_C";; *) echo "";; esac; }

# Formato: ID|Título|Responsables(A,B,C o combinación con +)|Milestone|Labels extra (coma)|Depende de|Entregable
TASKS=$(cat <<'EOF'
T-00|Crear repo, estructura, requirements, plantilla de PR, CODEOWNERS y proteccion de main|C|Fase 0 - Fundacion|base-compartida|-|Repo clonable y entorno reproducible
T-01|Cerrar decisiones (etiqueta, leakage, validacion) y redactar specs 00-contratos y 01-datos|A+B+C|Fase 0 - Fundacion|equipo|T-00|specs/00-contratos.md y specs/01-datos.md aprobadas
T-02|Diccionario de datos|A|Fase 0 - Fundacion|base-compartida|T-00|docs/data_dictionary.md
T-03|schema.sql (3 tablas) y config.yaml|A+B|Fase 0 - Fundacion|base-compartida|T-01|DDL y config versionados
CMP-1|Spec de comparacion de modelos (criterios definidos antes de ver resultados)|A+B+C|Fase 0 - Fundacion|comparacion,equipo|T-01|specs/03-comparacion.md
T-04|Ingesta y validacion del dataset crudo|A|Fase 1 - Base compartida|base-compartida|T-02|ingest.py + test de esquema
T-05|EDA: distribuciones, nulos, outliers, correlaciones, estacionalidad|A|Fase 1 - Base compartida|base-compartida|T-04|notebooks/01_eda.ipynb
T-06|Limpieza, features de calendario y construccion de etiqueta|A|Fase 1 - Base compartida|base-compartida|T-05|clean.py + tests
T-07|repository.py: crear BD y cargar Tabla 1|A|Fase 1 - Base compartida|base-compartida|T-03,T-06|run_data.py genera demanda.db
T-08|Dataset sintetico con el esquema exacto de Tabla 1|A|Fase 1 - Base compartida|base-compartida|T-03|CSV/BD de ejemplo (prioridad semana 1)
T-13|save_run(): guardado en Tabla 2 y Tabla 3|A|Fase 1 - Base compartida|base-compartida|T-03|Funcion + tests
T-09|build_preprocessor(): imputacion, escalado y OHE (excluye columnas de leakage)|B|Fase 1 - Base compartida|base-compartida|T-03,T-08|preprocessing.py + tests
T-10|get_split() cronologico y get_cv() comun|B|Fase 1 - Base compartida|base-compartida|T-03,T-08|splits.py + tests
T-11|evaluate.py: Accuracy, Precision, Recall, F1 y matriz de confusion|B|Fase 1 - Base compartida|base-compartida|T-03|evaluate.py + tests
T-12|Runner train.py con autodescubrimiento de modelos (--model)|B|Fase 1 - Base compartida|base-compartida|T-09,T-10,T-11,T-13|python -m demanda.models.train --model <x>
T-14|BD de prueba con las 3 tablas (fixtures)|C|Fase 1 - Base compartida|base-compartida|T-03|Fixture para tests y dashboard
T-15|CI en GitHub Actions (pytest + lint)|C|Fase 1 - Base compartida|base-compartida|T-00|Check obligatorio en PRs
T-16|plots.py base: clases, demanda vs temperatura, estacionalidad, serie con periodos criticos|C|Fase 1 - Base compartida|base-compartida|T-14|Funciones reutilizables
EOF
)

# Tareas de modelo: se generan para cada integrante con el mismo molde.
model_tasks() {
  local P="$1" PERSON="$2" LABEL="$3" NAME="$4" SEARCH="$5"
  cat <<EOF
${P}-1|[${NAME}] Spec del modelo: justificacion, grilla de hiperparametros, desbalance|${PERSON}|Fase 2 - Modelos|${LABEL}|T-01|specs/02-modelo-${NAME}.md
${P}-2|[${NAME}] Modulo del modelo (contrato NAME/SEARCH/get_estimator/get_param_grid) + test unitario|${PERSON}|Fase 2 - Modelos|${LABEL}|${P}-1,T-08|models/${NAME}.py + tests
${P}-3|[${NAME}] Baseline sin tuning con pipeline comun sobre dataset sintetico|${PERSON}|Fase 2 - Modelos|${LABEL}|${P}-2,T-09,T-10|Baseline reproducible
${P}-4|[${NAME}] Busqueda de hiperparametros (${SEARCH}) con CV comun y scoring f1_macro|${PERSON}|Fase 2 - Modelos|${LABEL}|${P}-3|Mejores parametros y cv_best_score
${P}-5|[${NAME}] Evaluacion en test: Accuracy, Precision, Recall, F1 y matriz de confusion|${PERSON}|Fase 2 - Modelos|${LABEL}|${P}-4,T-11|Metricas y matriz de confusion
${P}-6|[${NAME}] Persistencia en Tablas 2 y 3 con run_id propio (reejecutar con datos reales)|${PERSON}|Fase 2 - Modelos|${LABEL}|${P}-5,T-12,T-13,T-07|Filas en demanda.db
${P}-7|[${NAME}] Notebook e informe del modelo: interpretacion y analisis de errores|${PERSON}|Fase 2 - Modelos|${LABEL}|${P}-6|notebook + seccion en docs/model_card.md
EOF
}

TASKS+=$'\n'"$(model_tasks LR A modelo-logreg logreg GridSearchCV)"
TASKS+=$'\n'"$(model_tasks RF B modelo-rf rf RandomizedSearchCV)"
TASKS+=$'\n'"$(model_tasks XG C modelo-xgb xgb RandomizedSearchCV)"

TASKS+=$'\n'"$(cat <<'EOF'
CMP-2|Consulta consolidada de metricas de los 3 run_id (compare_runs)|A|Fase 3 - Comparacion|comparacion|LR-6,RF-6,XG-6,CMP-1|repository.compare_runs() + tests
CMP-3|Tabla comparativa y graficos: barras de metricas, matrices lado a lado, F1 por clase, tiempos|C|Fase 3 - Comparacion|comparacion|CMP-2,T-16|Funciones en plots.py
CMP-4|Analisis: que modelo gana y por que, errores por clase, impacto del desbalance|B|Fase 3 - Comparacion|comparacion|CMP-3|notebooks/05_comparacion.ipynb
CMP-5|Decision del modelo final segun criterio de CMP-1|A+B+C|Fase 3 - Comparacion|comparacion,equipo|CMP-4|Seccion en docs/model_card.md
V-1|Dashboard Streamlit: filtros por modelo, fecha y clase; metricas; matrices; predicciones|C|Fase 4 - Cierre|base-compartida|CMP-3|app.py contra demanda.db
F-1|run_all.py + test de integracion (datos -> 3 modelos -> BD)|B|Fase 4 - Cierre|base-compartida|CMP-2|Ejecucion de punta a punta con un comando
F-2|Revision cruzada final de codigo y specs (A->B, B->C, C->A)|A+B+C|Fase 4 - Cierre|equipo|V-1,F-1|PRs de revision cerrados
F-3|Informe final y README de ejecucion (una seccion por integrante)|A+B+C|Fase 4 - Cierre|equipo|CMP-5,V-1|docs/informe_final.md
F-4|Ensayo de demo desde cero|A+B+C|Fase 4 - Cierre|equipo|F-3|Demo reproducible
EOF
)"

# ---------- Primera pasada: crear issues ----------
declare -A NUM
while IFS='|' read -r ID TITLE WHO MS LABELS DEPS DELIV; do
  [ -z "$ID" ] && continue
  LBL=""
  IFS='+' read -ra PEOPLE <<< "$WHO"
  ASSIGNEES=()
  for p in "${PEOPLE[@]}"; do
    LBL+="persona-$p,"
    ASSIGNEES+=(--assignee "$(user_for "$p")")
  done
  [ "$LABELS" != "-" ] && LBL+="$LABELS,"
  LBL="${LBL%,}"
  BODY="**ID:** $ID
**Responsable(s):** $WHO
**Depende de:** $DEPS
**Entregable:** $DELIV

### Definicion de hecho
- [ ] Spec/criterio escrito antes de implementar
- [ ] Minimo 3 commits propios (Conventional Commits con \`($ID)\`)
- [ ] Tests pasan en local y en CI
- [ ] Documentacion actualizada
- [ ] PR aprobado por otro integrante (\`Closes #N\`)
- [ ] Merge sin squash

Rama sugerida: \`feat/$ID-<descripcion-corta>\`"
  URL=$(gh issue create --title "[$ID] $TITLE" --body "$BODY" --label "$LBL" --milestone "$MS" "${ASSIGNEES[@]}")
  NUM[$ID]="${URL##*/}"
  echo "$ID -> #${NUM[$ID]}"
done <<< "$TASKS"

# ---------- Segunda pasada: reemplazar IDs de dependencias por #N ----------
while IFS='|' read -r ID TITLE WHO MS LABELS DEPS DELIV; do
  [ -z "$ID" ] && continue
  [ "$DEPS" = "-" ] && continue
  REFS=""
  IFS=',' read -ra DL <<< "$DEPS"
  for d in "${DL[@]}"; do REFS+="#${NUM[$d]} ($d), "; done
  REFS="${REFS%, }"
  CURRENT=$(gh issue view "${NUM[$ID]}" --json body -q .body)
  NEW="${CURRENT//\*\*Depende de:\*\* $DEPS/**Depende de:** $REFS}"
  gh issue edit "${NUM[$ID]}" --body "$NEW" >/dev/null
done <<< "$TASKS"

echo "Listo: ${#NUM[@]} issues creados."
