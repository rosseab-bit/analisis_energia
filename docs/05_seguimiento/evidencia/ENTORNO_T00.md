# T-00: entorno Python local verificado

Verificado el **30 de octubre de 2026**, sobre el código `ba0b9e2`, en la rama
`docs/T-00-guia-angel`. Alcance: paso 1 del plan personal de Angel. T-00 continúa
parcial; faltan sus otros criterios y la comprobación de instalación de A/B.

## Entorno instalado

- macOS 26.6, Apple Silicon (`arm64`).
- Python **3.12.16**, instalado con uv **0.13.6** en el espacio de usuario.
- Intérprete base: `~/.local/share/uv/python/cpython-3.12.16-macos-aarch64-none/bin/python3.12`.
- Entorno del proyecto: `.venv`, aislado de los paquetes del sistema.
- `demanda` **0.1.0**, instalado en modo editable; recurso `db/schema.sql` accesible.
- Python del sistema: 3.9.6. La instalación no modificó los perfiles del shell.

Para trabajar desde la raíz del repositorio:

```bash
source .venv/bin/activate
python --version
```

En VS Code, seleccionar `.venv/bin/python` mediante **Python: Select Interpreter**.
La activación se repite en cada terminal nueva. `.venv/` y `*.egg-info/` están
excluidos de Git, lo que se comprobó con `git check-ignore`.

## Instalación y repetición

Se utilizó el [instalador oficial de uv](https://docs.astral.sh/uv/getting-started/installation/)
con `UV_NO_MODIFY_PATH=1`; después se instaló Python 3.12 y se comprobó su versión
antes de crear el entorno. uv permite [instalar una versión concreta de Python](https://docs.astral.sh/uv/guides/install-python/).
Los comandos de instalación ejecutados, después de instalar uv, fueron:

```bash
~/.local/bin/uv python install 3.12
~/.local/bin/python3.12 --version
~/.local/bin/python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -e .
```

La resolución descargó pandas 3.1.0, NumPy 2.5.4, scikit-learn 1.9.1 y XGBoost 3.4.1,
además de las demás dependencias. Las versiones exactas, incluidas las transitivas,
están en [requirements_T00_macos_arm64.txt](requirements_T00_macos_arm64.txt), generado
con `python -m pip freeze --exclude-editable`. Es una instantánea local: todavía
no es la selección de versiones validada por los tres integrantes.

Para repetir esa resolución en **otro entorno nuevo** de esta plataforma, instalar
Python con `~/.local/bin/uv python install 3.12.16`, crear y activar el entorno,
satisfacer OpenMP según la sección siguiente y ejecutar desde la raíz:

```bash
python -m pip install -r requirements.txt -c docs/05_seguimiento/evidencia/requirements_T00_macos_arm64.txt
python -m pip install -e .
python -m pip check
```

## OpenMP para XGBoost en esta Mac

La instalación inicial por pip terminó correctamente, pero `import xgboost` falló
con `Library not loaded: @rpath/libomp.dylib`. `pip check` no detecta la ausencia
de esa biblioteca nativa. En equipos con Homebrew puede instalarse con
`brew install libomp` ([fórmula oficial](https://formulae.brew.sh/formula/libomp)).

Esta Mac no tenía Homebrew. Se descargó su paquete binario oficial de **libomp
23.1.4 para arm64_sequoia**, compatible con este macOS, y se verificó el SHA-256
contra la [API de la fórmula](https://formulae.brew.sh/api/formula/libomp.json):

- [Archivo descargado](https://ghcr.io/v2/homebrew/core/libomp/blobs/sha256:af8425bbe39630ec9b2022b67449ac737e0ed6d48e98a6309f841295d3c6f0f2).
- SHA-256: `af8425bbe39630ec9b2022b67449ac737e0ed6d48e98a6309f841295d3c6f0f2`.
- `libomp/23.1.4/lib/libomp.dylib` se copió a `lib/libomp.dylib` del intérprete base
  indicado arriba, una ruta que el cargador de este Python consulta.
- `libomp/23.1.4/LICENSE.TXT` se conservó en
  `share/licenses/libomp/LICENSE.TXT` del mismo intérprete.

No se modificó el binario de XGBoost. OpenMP quedó asociado a esta instalación
de Python de usuario; reinstalarla requiere restaurar también la biblioteca.
El archivo de versiones de pip no incluye OpenMP.

## Verificaciones y resultados

Las salidas de Python, pip, configuración, tests y Ruff están en
[verificacion_entorno_T00.txt](verificacion_entorno_T00.txt).

| Comprobación | Resultado |
|---|---|
| `python --version` | Python 3.12.16, compatible con `requires-python >=3.11`. |
| Instalación de requirements y `pip install -e .` | Ambas terminaron con código 0. |
| `python -m pip check` | Código 0: `No broken requirements found.` |
| `load_config()['semilla']` | Código 0, salida `42`. |
| `python -m pytest -q` | Código 0: **29 passed, 3 subtests passed in 19.51s**. Sin tests omitidos. |
| Importaciones | pandas, numpy, yaml, sklearn, xgboost, matplotlib, seaborn, plotly y streamlit: OK. |
| XGBoost con datos ficticios | `XGBClassifier(n_estimators=2, max_depth=1, n_jobs=1, random_state=42)` completó fit/predict con 6 muestras binarias. |
| `python -m ruff check src tests` | Código **1**: dos observaciones preexistentes, detalladas debajo. |

- **A:** `RUF046`, `src/demanda/etl/transform.py:60`, conversión redundante a `int`.
- **B:** `F401`, `src/demanda/etl/validate.py:6`, importación de NumPy sin uso.

Se registran para coordinar su corrección con cada dueño. El código de esos
módulos se conservó. No se ocultaron reglas ni errores de Ruff. La prueba de
XGBoost solo verifica el entorno; no produce resultados del proyecto ni acredita
las tareas del modelo. El defecto temporal del ETL descrito en el avance sigue
pendiente.
