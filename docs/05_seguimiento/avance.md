# Avance general del proyecto final

Última revisión: **31 de octubre de 2026**, para confirmar identidades e invitaciones y preparar la revisión de T-00. Los archivos están en `docs/T-00-guia-angel`, pendientes de revisión e integración; el fetch del 31 de octubre confirmó `main` en `96fafa6`.

**Situación actual:** dataset disponible, Git operativo y ETL funcional probado; hay una corrección temporal pendiente en la etiqueta. Todavía no están implementados los modelos, sus resultados persistidos, las visualizaciones, el dashboard o la presentación en la copia revisada.

Este es el registro general de entregables. [PLAN_SDD.md](../02_planificacion/PLAN_SDD.md) define el alcance y las dependencias; [ORDEN_Y_COORDINACION.md](../02_planificacion/ORDEN_Y_COORDINACION.md) define cómo coordinarse. Los issues y PR guardan el detalle de cada tarea.

## 1. Cómo interpretar y actualizar el estado

| Estado | Qué significa |
|---|---|
| **Pendiente** | No hay una entrega verificable en la copia revisada. No significa que se haya comprobado la ausencia de trabajo en otras ramas. |
| **Parcial** | Hay archivos o comprobaciones, pero faltan criterios de aceptación. |
| **Requiere corrección** | Se comprobó un problema que impide dar la entrega por válida. |
| **Por verificar** | Falta evidencia de un estado externo, como protección de GitHub, aprobación o subida al campus. |
| **Listo** | Cumple todos sus criterios y tiene evidencia reproducible. Si depende de código/documentación del repo, también está revisado y mergeado en `main`. |

La evidencia técnica local y el cierre formal de una tarea son distintos. En esta revisión no se marcaron tareas como Listo por la sola existencia de código de referencia. No se calcula un porcentaje de nota ni de avance sumando casillas de diferente tamaño.

## 2. Requisitos de la consigna oficial

Referencia: contenido visible de [Proyecto_Final.pdf](../01_consigna/Proyecto_Final.pdf), páginas 1 a 3. El original externo se conserva y esta copia integra el backup documental. Los compromisos adicionales del equipo se siguen en la sección 3.

| Entregable obligatorio | Estado | Responsable y tareas | Evidencia actual / criterio para cerrarlo |
|---|---|---|---|
| Dataset propuesto y objetivo de clasificación | **Parcial** | Equipo; A en T-02 y ETL-3; T-01 conjunto. | El CSV coincide con la opción B de demanda eléctrica. Falta cerrar definición temporal del objetivo, procedencia exacta, unidades y decisiones de datos. |
| Pipeline sklearn: imputación, escalado y categóricas | **Pendiente** | B, MC-1 y MC-4; cada dueño de modelo lo integra. | No están los módulos comunes. Cierre: pipeline probado, transformaciones ajustadas solo con train y mismo criterio para los modelos. |
| Comparar al menos dos clasificadores | **Pendiente** | A: Logistic Regression; B: Random Forest; Angel Zambrano: XGBoost. | No se encontraron módulos ni resultados de entrenamiento. Cierre: modelos comparados sobre las mismas fechas, etiquetas y reglas. El plan interno compromete los tres. |
| Optimización con GridSearchCV o RandomizedSearchCV | **Pendiente** | Cada dueño, LR-4/RF-4/XG-4; B en CV compartida. | Cierre: búsquedas sobre train, parámetros, score CV y configuración registrados; test reservado para evaluación. |
| Accuracy, Precision, Recall, F1 y matriz de confusión | **Pendiente** | B en MC-3; cada dueño evalúa su modelo; CMP-2…CMP-4. | Cierre: las cuatro métricas y matrices reproducibles por modelo, con orden de clases, muestra y limitaciones documentados. |
| Tabla 1: entradas limpias y preprocesadas | **Requiere corrección** | A: ETL-1/ETL-3/T-03; B: ETL-2; Angel Zambrano: ETL-4/ETL-5. | El ETL genera 308 filas y preserva nulos esperados. La etiqueta depende de test mediante una media centrada. Corregir y verificar el método configurado antes de cerrar. |
| Tabla 2: predicciones y métricas guardadas | **Parcial** | A: DB-2; B: MC-4; cada dueño: LR-6/RF-6/XG-6. | Existen las tablas en el esquema, vacías en una carga ETL nueva. Cierre: persistencia transaccional de runs reales y consultas de verificación. |
| Gráficos y tablas claros | **Pendiente** | Angel Zambrano: VIZ-1 y CMP-3; B: análisis CMP-4. | Cierre: gráficos de datos y comparación basados en resultados reales, con unidades, títulos y limitaciones. La consigna permite varias herramientas. |
| Código organizado y control de versiones | **Parcial** | Equipo; Angel Zambrano: T-00/T-15. | Hay ETL modular, tests e identidad/conexión Git verificadas. Faltan CI y evidencias de revisiones; Ruff detectó dos observaciones. |
| Repo con script de carga, dependencias y README | **Parcial** | Angel Zambrano: T-00; equipo: F-3. | Instalación editable y configuración verificadas desde una copia nueva de GitHub; README con comandos disponibles. Faltan comprobaciones de A/B e integración de la preparación. |
| Base de datos accesible para revisión | **Pendiente** | Equipo, F-3; responsable de entrega por definir. | Las pruebas usaron bases temporales. Acordar y verificar canal de acceso/entrega al docente, versión, instrucciones y resultados reales. No basta con una BD privada en una computadora. |
| Presentación de 6 a 8 diapositivas PDF o PPTX | **Pendiente** | Equipo, F-3; consolidación por asignar. | Cierre: archivo definitivo con problema, datos, método, resultados y conclusiones, revisado por los tres. No se encontró una presentación local. |
| Presentación subida al campus | **Por verificar** | Equipo, F-3; persona encargada por asignar. | Registrar responsable, fecha y confirmación de la entrega. Crear o exportar el archivo no acredita su subida. |
| Defensa oral de 8 a 10 minutos | **Pendiente** | Equipo, F-4. | Cierre: reparto de intervención, ensayo cronometrado y los tres capaces de explicar decisiones, métricas y limitaciones. |

## 3. Compromisos internos y extras

| Compromiso | Estado | Responsable y cierre esperado |
|---|---|---|
| Tercer modelo y siete tareas por algoritmo | **Pendiente** | A: LR; B: RF; Angel Zambrano: XG. La materia pide al menos dos, pero el plan sigue comprometiendo tres hasta que el equipo acuerde modificarlo. |
| Tabla 3: configuración y parametrización | **Parcial** | A: DB-2 y cada dueño de modelo. Es extra académico; existe esquema, faltan runs con configuración real persistida. |
| Dashboard Streamlit completo | **Pendiente** | Angel Zambrano, V-1, después de CMP-3. Cierre: pestañas Datos, Modelos, Comparación, Predicciones y Calidad; filtros; lectura de BD; manejo de ausencia de datos y test de humo. |
| Ablación de features | **Pendiente** | Los tres, LR-5/RF-5/XG-5. Comparar los conjuntos acordados y controlar o explicitar las diferencias de población por disponibilidad sectorial. |
| Fixtures de BD | **Pendiente** | Angel Zambrano, VIZ-2, después de T-03. Datos ficticios identificados, con restricciones y conteos probados. |
| Ejecución completa con `run_all.py` | **Pendiente** | B, F-1. Cierre: ETL, tres modelos y persistencia desde una copia nueva, con prueba de integración. |
| CI y protección de `main` | **Pendiente / por verificar** | Angel Zambrano, T-00/T-15. No hay workflow local; verificar reglas, revisión requerida y check obligatorio en GitHub. |
| Contratos y criterios acordados | **Parcial** | Equipo, T-01/CMP-1. Hay borrador de datos; faltan contratos y criterios de comparación aprobados. |
| Informe, model card y revisión cruzada | **Pendiente** | Equipo, F-2/F-3 y tareas de cada modelo. Cierre: una sección por integrante, resultados reales y observaciones atendidas. |
| Guías de trabajo y seguimiento | **Parcial** | Equipo; Angel Zambrano coordina esta actualización. Los borradores están preparados localmente; falta revisión, commit y merge. |

**T-00: criterios de cierre pendientes y preparación disponible**

| Criterio | Evidencia / siguiente paso |
|---|---|
| Repo instalable | Clon nuevo de `2d9ac70`, venv aislado, requirements, paquete editable, `pip check`, semilla `42` y recurso SQL verificados. Falta la comprobación en los equipos de A/B. |
| Dueños | Identidades confirmadas por el usuario el 31 de octubre: A, Ricky (`rosseab-bit`); B, Brian (usuario pendiente); C, Angel (`Angelzam21`). `CODEOWNERS` incluye las áreas existentes de A/C. Confirmar usuario y acceso de Brian antes de completar las suyas. |
| Plantilla de PR | `.github/pull_request_template.md` preparada con alcance, evidencia, DoD y checklist; pendiente de revisión e integración en main. |
| Acceso y protección | Propietario: Ricky (`rosseab-bit`). Invitaciones aceptadas según el usuario el 31 de octubre; falta confirmar usuario y escritura de Brian. La consulta del 30 de octubre devolvió main sin protección y rulesets vacíos. El propietario debe configurar PR, aprobación y merge commits. |
| Issues y tablero | 50 tareas y dependencias validadas en dry-run con Bash 3.2. No hay issues/PR en la consulta; publicación y Project pendientes de cuentas confirmadas e indicación. Integrar antes la documentación y el generador en main. |
| Verificaciones | En copia nueva: 29 tests y 3 subcasos aprobados; Ruff mantiene dos observaciones de A/B. T-15 sigue pendiente. |

La [preparación de infraestructura de T-00](evidencia/INFRAESTRUCTURA_T00.md) conserva los archivos, la evidencia de GitHub y las instrucciones concretas para el propietario. T-00 permanece **Parcial** hasta verificar todos sus criterios.

## 4. Las cuatro partes de la evaluación

Cada bloque pesa **25 %** en la rúbrica; estos estados orientan el trabajo y no son una estimación de calificación.

| Bloque | Estado actual | Qué debe verse en la entrega |
|---|---|---|
| Código y Git | **Parcial** | Organización modular, calidad, funciones/clases, comentarios útiles, historial y trabajo del equipo. |
| Base de datos y visualización | **Parcial** | Entradas y resultados reales en BD, acceso para revisión y gráficos claros. |
| Modelado y resultados | **Pendiente** | Pipeline, búsqueda, evaluación, comparación y explicación metodológica. |
| Presentación oral y defensa | **Pendiente** | Material visual de 6 a 8 diapositivas, exposición de 8 a 10 minutos y dominio del tema. |

## 5. Evidencia técnica disponible y bloqueo principal

Comprobaciones ejecutadas el 30 de octubre de 2026 sobre el código de referencia actual, con Python 3.12.14, pandas 2.2.3, NumPy 2.3.5, pytest 9.2.0 y Ruff 0.17.3:

- Dataset: 308 filas, 30 columnas, sin meses faltantes ni fechas duplicadas; sin nulos en demanda total, temperatura y potencia.
- Auditoría original del ETL: **25 tests aprobados**, incluidos los del CSV real. La revisión posterior del generador añade 4 tests de publicación simulada y validación, sin acceso real a GitHub; el resultado de la suite completa se registra debajo.
- Carga: **308 filas limpias**, **3.450 de distribuidoras** y una auditoría por corrida; idempotencia y NULL comprobados.
- Pruebas adicionales: rollback con fallo durante la carga, conservación de resultados sin reset y limpieza de resultados con reset.
- CLI: CSV válido aceptado y fechas duplicadas rechazadas sin modificar la BD previa. Si falta la columna de fecha, todavía muestra traceback.
- Lint: observaciones `F401` en validate y `RUF046` en transform.
- Independencia temporal: al modificar solo demanda y sectores de test, cambiaron cinco scores y tres etiquetas de train, además de los umbrales del método por defecto.

**Bloqueo metodológico:** A coordina la corrección de ETL-3 y su criterio en la spec; B revisa implicaciones en split/CV y evaluación; Angel Zambrano verifica la integración. Tener 25 tests verdes no resuelve el problema: falta una prueba significativa para el método configurado.

La [evidencia detallada](evidencia/evidencia_verificacion_etl.json) se conserva aquí como backup; también se mantiene su copia externa original. Las rutas y registros ficticios de esas pruebas no representan una BD final de entrega. Después de corregir código, configuración o datos, hay que renovar la evidencia y registrar el PR/commit correspondiente.

**Revisión de consistencia documental e infraestructura:** 29 tests aprobados y 3 subcasos de dependencias inválidas comprobados. El generador lee 50 tareas desde el plan, valida IDs/dependencias y se detiene si ya existen issues. Las pruebas de publicación utilizan un `gh` simulado; no acreditan configuración remota ni crean issues reales. La corrección temporal del ETL y las dos observaciones de lint de referencia siguen pendientes.

**T-00, entorno local — 30 de octubre de 2026:** `.venv` creado con Python 3.12.16 de usuario; dependencias y paquete editable instalados. `pip check` aprobado, semilla `42`, 29 tests y 3 subcasos aprobados. Todas las bibliotecas importan; XGBoost ejecuta fit/predict con datos ficticios tras instalar OpenMP. Ruff mantiene `RUF046` en transform (A) y `F401` en validate (B). La [evidencia y las versiones exactas](evidencia/ENTORNO_T00.md) registran este paso; la instalación del resto del equipo, la infraestructura restante de T-00 y T-15 siguen pendientes.

## 6. Próximas acciones y decisiones de entrega

| Acción | Quién coordina | Evidencia esperada |
|---|---|---|
| Completar T-00/T-15 y verificar acceso/protecciones | Angel Zambrano | Instalación reproducible, workflow y reglas confirmadas. |
| Cerrar T-01 y fijar CMP-1 antes de resultados | Equipo | Specs aprobadas, decisiones y criterios registrados. |
| Corregir la independencia temporal del objetivo | A, con revisión del equipo | Spec y test del método elegido; cambios en test no alteran cálculos de train. |
| Completar módulos comunes y persistencia | B: modelado; A: BD | Pipeline común, evaluación y run real guardado. |
| Definir acceso del docente a la BD | Equipo; responsable por asignar | Canal, versión y prueba de acceso acordados. |
| Asignar consolidación y subida de presentación | Equipo | Persona responsable, ubicación del archivo, fecha de entrega y confirmación del campus cuando corresponda. |
| Acordar reparto y ensayo de defensa | Equipo | Guion por integrante y duración registrada. |

La fecha límite del campus **no fue informada ni verificada**. Las fechas del cronograma interno no se presuponen como fecha oficial de entrega.

## 7. Rutina de actualización

1. Cada integrante actualiza solo los entregables de sus tareas, con evidencia y fecha; para secciones compartidas acuerdan un autor.
2. Al mergear un PR, registrar issue/PR/commit, comando de validación y resultado. Si queda un criterio pendiente, mantener el estado parcial.
3. Para entregas externas, registrar archivo definitivo y confirmación de acceso o subida; no marcar Listo por tener un borrador.
4. En la reunión semanal, revisar esta página por entregables generales y el tablero por tareas. Resolver bloqueos y asignaciones sin duplicar toda la historia de los issues.
5. Si cambia el alcance, actualizar primero el plan y el criterio correspondiente; después este seguimiento.

Formato breve para agregar evidencia: `Fecha | Entregable | Issue/PR/commit o archivo | Verificación y resultado | Próximo paso`.
