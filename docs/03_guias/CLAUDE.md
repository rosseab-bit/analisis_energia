# Contexto del proyecto para el agente de IA

Proyecto académico en equipo (3 personas, GitHub, metodología SDD). Objetivo: clasificar meses de **demanda eléctrica** en `Normal` / `Alta` / `Crítica` con scikit-learn, guardar todo en **SQLite** y mostrarlo en un dashboard. Lee `docs/02_planificacion/PLAN_SDD.md` (plan y tareas), `docs/03_guias/GUIA_EQUIPO.md` (flujo de trabajo) y `docs/07_especificaciones/` antes de escribir código.

## Reglas que SIEMPRE se cumplen
1. **SDD:** primero la spec/criterio de aceptación (`docs/07_especificaciones/…`), después el test, después la implementación.
2. **Una tarea = una rama = un PR.** Rama `feat/<ID>-<slug>`. Nunca trabajar sobre `main`.
3. **Commits chicos (mínimo 3 por tarea)**, formato `tipo(ID): descripción en imperativo` (tipos: feat, fix, test, docs, refactor, data, chore). Un cambio lógico por commit. El humano revisa el diff y hace el commit con su propio usuario de Git.
4. **Tocar solo los archivos de tu tarea.** Los archivos de otros integrantes (ver `CODEOWNERS`) no se modifican sin avisar. Si hay que cambiar un contrato, es un PR a `docs/07_especificaciones/00-contratos.md`.
5. **Sin hardcodear:** semilla, umbrales, rutas, columnas y conjuntos de features salen de `config/config.yaml`.
6. **Sin fuga de datos (leakage):** `demanda_total`, `demanda_ratio_tendencia`, `etiqueta`, `split` y `fecha` nunca son features. Los umbrales de la etiqueta se calculan solo con `train`. Los sectores en valores absolutos suman exactamente `demanda_total`: usar participaciones o excluirlos.
7. **Split cronológico**, nunca aleatorio. CV con `TimeSeriesSplit`. Misma semilla, mismo split y mismo `evaluate.py` para los 3 modelos.
8. Los tests usan `unittest` o `pytest` y deben pasar (`pytest`) y el linter también (`ruff check src tests`).
9. No inventar columnas, resultados ni métricas: si algo no está en los datos o en la spec, preguntar.
10. No subir `db/*.db`, credenciales ni datos que no estén en `data/raw/`.

## Referencias principales

- Datos y unidades: `docs/06_datos/data_dictionary.md`.
- Decisiones D1-D7 y criterios ETL: `docs/07_especificaciones/01-datos.md`.
- Estado, evidencia y defectos abiertos: `docs/05_seguimiento/avance.md`.
- Instalación y comandos disponibles: `docs/00_inicio/README.md`.
- Contrato de modelos: `docs/02_planificacion/PLAN_SDD.md` §2.4; ampliaciones aprobadas en la spec de contratos cuando exista.
- Dueños y PR: `docs/02_planificacion/ORDEN_Y_COORDINACION.md`.

No duplicar estadísticas, calendarios o estados en este archivo. No suponer que una ruta planificada ya está implementada.

## Cómo trabajar con el humano
Explicá brevemente qué vas a hacer, hacelo en pasos pequeños, y al terminar cada paso proponé el mensaje de commit. El humano debe poder explicar cada línea del código que entrega: preferí código simple y comentado antes que ingenioso.
