# Clasificación de períodos de demanda eléctrica

Proyecto de análisis de demanda eléctrica mensual para clasificar períodos como **Normal**, **Alta** o **Crítica** y comparar Regresión Logística, Random Forest y XGBoost, con persistencia en SQLite.

Actualmente están implementados la lectura, validación, transformación y carga del CSV, el esquema de la base de datos y las pruebas del ETL. El entrenamiento de modelos, su comparación y el dashboard están pendientes de implementación.

## Requisitos y ejecución

Requiere Python 3.11 o posterior. Con un entorno virtual activo, desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python scripts/run_etl.py
```

Pruebas y comprobación de estilo:

```bash
python -m pytest -q
python -m ruff check src tests
```

El ETL lee `data/raw/demanda_electricidad_original_mensual1.csv` y genera `db/demanda.db`. Las rutas, reglas de validación, método de etiquetado y conjuntos de variables están en [config/config.yaml](config/config.yaml).

La carga reemplaza los datos del ETL, conserva los resultados de modelos y agrega una auditoría. La opción `--reset` elimina todas las tablas, incluidos los resultados de modelos, antes de reconstruirlas.

## Integración continua

El [workflow de CI](.github/workflows/ci.yml) se ejecuta en cada `push` y `pull_request`. Su único job, `test`, usa Ubuntu y Python 3.11, instala `requirements.txt` y el paquete en modo editable, y ejecuta los comandos de pytest y Ruff indicados arriba. La caché de pip depende de `requirements.txt` y `pyproject.toml`. Cualquier error de instalación, pruebas o lint hace fallar el check; pytest también falla si no recoge pruebas. Las pruebas cubren el ETL y deben interpretarse junto con sus [limitaciones documentadas](docs/validacion/etl.md).

Los cambios se integran mediante PR hacia `develop`. Después de una ejecución real que publique el check `test`, un administrador puede editar o crear una regla para `develop` en **Settings → Branches → Branch protection rules**, activar **Require a pull request before merging** y **Require status checks to pass before merging**, seleccionar `test` de GitHub Actions y guardar. Debe repetir la configuración para `main`, que es una rama distinta, y verificar que el check sea obligatorio en ambas. Véase la [documentación de protecciones de GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule).

La validación local no acredita una ejecución de GitHub Actions. La CI requiere revisión e integración, evidencia de una ejecución satisfactoria en un PR y la configuración del check obligatorio en las ramas acordadas.

## Datos y limitaciones

El dataset contiene 308 meses, de enero de 2001 a agosto de 2026. Los sectores están disponibles desde 2005 y las distribuidoras desde enero de 2014 hasta junio de 2026. La procedencia exacta y las unidades de demanda y potencia están pendientes de confirmación.

El etiquetado configurado usa una media móvil centrada que introduce dependencia de test en algunos cálculos de train. Las etiquetas actuales son provisionales hasta resolver este problema; el diagnóstico se conserva en [validación del ETL](docs/validacion/etl.md).

## Documentación técnica

- [Consigna del proyecto](docs/consigna/Proyecto_Final.pdf).
- [Alcance y arquitectura](docs/arquitectura.md).
- [Diccionario de datos](docs/datos/diccionario.md).
- [Especificación de datos y ETL](docs/especificaciones/datos-etl.md).
- [Verificación del dataset](docs/validacion/datos.md).
- [Validación del ETL y limitaciones](docs/validacion/etl.md).
- [Esquema SQLite](src/demanda/db/schema.sql).
