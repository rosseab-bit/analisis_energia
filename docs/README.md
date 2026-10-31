# Documentación del proyecto de energía

Este índice organiza la documentación para Google Drive y su backup en el repositorio. Cada tema tiene un documento principal; los otros lo enlazan en lugar de copiar sus listas o estados.

## Empezar

- **Angel:** [plan personal paso a paso](04_integrantes/Angel_Zambrano/PLAN_PERSONAL_ANGEL.md), con motivos, requisitos y bloqueos; [ficha C](04_integrantes/Angel_Zambrano/TAREAS_C.md) para los prompts técnicos.
- **Equipo:** [avance general](05_seguimiento/avance.md), para saber qué falta entregar.
- **Repositorio:** [README técnico](00_inicio/README.md), para instalarlo y distinguir comandos disponibles de los previstos.

## Carpetas y referencia principal de cada tema

| Carpeta | Documento y función |
|---|---|
| **00_inicio** | [README técnico](00_inicio/README.md): instalación, comandos y BD. Este índice mantiene la navegación. |
| **01_consigna** | [PDF oficial](01_consigna/Proyecto_Final.pdf): requisitos del docente, sin modificar. |
| **02_planificacion** | [Plan SDD](02_planificacion/PLAN_SDD.md): alcance, tareas, dependencias y cierre. [Coordinación](02_planificacion/ORDEN_Y_COORDINACION.md): dueños de archivos, ramas, PR, comunicación y bloqueos. |
| **03_guias** | [Guía operativa](03_guias/GUIA_EQUIPO.md): preparación, commits, revisión y operación del ETL. [Guía del agente](03_guias/COMO_TRABAJAR_CON_MI_AGENTE.md): prompts y evidencia. [CLAUDE.md](03_guias/CLAUDE.md): instrucciones breves para el agente, con enlaces a las reglas completas. |
| **04_integrantes/A** | [Ficha A](04_integrantes/A/TAREAS_A.md): ejecución técnica de datos, BD y Logistic Regression. |
| **04_integrantes/B** | [Ficha B](04_integrantes/B/TAREAS_B.md): ejecución técnica de validación, módulos comunes y Random Forest. |
| **04_integrantes/Angel_Zambrano** | [Ficha C](04_integrantes/Angel_Zambrano/TAREAS_C.md): infraestructura, carga, visualización y XGBoost. [Plan personal](04_integrantes/Angel_Zambrano/PLAN_PERSONAL_ANGEL.md): recorrido gradual; no es otro catálogo de tareas. |
| **05_seguimiento** | [Avance general](05_seguimiento/avance.md): único estado vigente de entregables, incluida presentación, campus y defensa. `evidencia/` conserva la [revisión inicial histórica](05_seguimiento/evidencia/REVISION_INICIAL_CONSIGNA_ETL.md) y los [resultados del ETL](05_seguimiento/evidencia/evidencia_verificacion_etl.json); no son otro tablero. |
| **06_datos** | [Diccionario](06_datos/data_dictionary.md): columnas, disponibilidad, unidades y hechos observados. El CSV original sigue en `data/raw/`. |
| **07_especificaciones** | [Spec de datos](07_especificaciones/01-datos.md): criterios ETL y único registro de decisiones D1-D7. Aquí se agregan las otras specs cuando se elaboren y aprueben. |

El [PDF de coordinación](03_guias/pdf/Orden_y_coordinacion.pdf) es una exportación del Markdown, no un segundo documento editable. Se regenera cuando cambia su fuente.

`docs/08_entrega/` queda reservado para informe, model card y presentación cuando se creen. Los notebooks de trabajo se mantienen en `notebooks/` como parte del proyecto técnico. Ninguna ruta prevista acredita una entrega ya implementada.

## Mantener el orden

1. Guardar documentos por propósito y conservar la jerarquía al trasladarlos a Drive. Los enlaces de Drive se registrarán cuando existan; esta sesión no publicó archivos.
2. No dejar documentos en la raíz ni crear copias con sufijos de versión. Mantener el historial en Git y las exportaciones en `pdf/`.
3. Actualizar el documento principal de un tema; usar enlaces para resúmenes, prompts o recorridos personales. Los estados solo se actualizan en avance general.
4. Los comandos y rutas de código se interpretan desde la raíz del repo; los enlaces entre Markdown son relativos al documento.
5. Indicar explícitamente al agente que lea `docs/03_guias/CLAUDE.md`; no hay una copia de instrucciones en la raíz. Los archivos técnicos conservan sus ubicaciones.

La revisión de redundancias consolidó la antigua guía personal en el plan personal y la ficha C, retiró calendarios repetidos y separó el informe histórico del seguimiento. Los originales externos se conservan; la consigna y la evidencia JSON permanecen íntegras.
