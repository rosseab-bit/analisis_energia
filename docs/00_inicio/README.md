# Clasificación de períodos de demanda eléctrica

Índice de documentos: [docs/README.md](../README.md). Ejecutá los comandos de esta página desde la raíz del repositorio, no desde esta carpeta.

Clasifica cada mes en **Normal / Alta / Crítica** según demanda total y sectorial, temperatura, potencia máxima y estacionalidad, comparando tres modelos de scikit-learn/XGBoost y guardando todo en SQLite.

| Modelo | Responsable | Búsqueda de hiperparámetros |
|---|---|---|
| Logistic Regression | A | `GridSearchCV` |
| Random Forest | B | `RandomizedSearchCV` |
| XGBoost | Angel Zambrano | `RandomizedSearchCV` |

## Instalación

Requiere Python 3.11 o posterior. Seleccioná un intérprete compatible y verificá su versión antes de crear `.venv`; no se presupone que el `python` del sistema ya cumpla esa condición.

```bash
python --version
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
```

## Uso disponible

```bash
python scripts/run_etl.py                       # CSV -> SQLite (db/demanda.db)
python -m pytest -q
python -m ruff check src tests
```

El ETL de referencia tiene un defecto temporal abierto; consultá [avance general](../05_seguimiento/avance.md) antes de interpretar sus etiquetas como definitivas.

## Comandos previstos, todavía por implementar

```bash
python -m demanda.models.train --model logreg --features base     # o rf / xgb
streamlit run src/demanda/viz/app.py
python scripts/run_all.py --reset
```

Estas rutas figuran en el plan; no se presentan como ejecutables disponibles hasta que sus módulos estén integrados. El catálogo documental se mantiene únicamente en el [índice](../README.md).

## Base de datos (SQLite)
`datos_limpios` (Tabla 1) · `predicciones` y `metricas_modelo` (Tabla 2) · `config_modelo` (Tabla 3) · extras: `demanda_distribuidora`, `etl_auditoria`. Esquema en `src/demanda/db/schema.sql`.
