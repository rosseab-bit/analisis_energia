# Plan personal de Angel Zambrano

Responsable C: 15 tareas propias y 6 conjuntas. Punto de partida revisado el **30 de octubre de 2026**.

La ficha C conserva los prompts y criterios técnicos; este plan explica el recorrido. El estado vigente de las entregas se consulta en [avance general](../../05_seguimiento/avance.md).

**Podés avanzar ahora.** No necesitás esperar a que A y B terminen sus modelos para preparar el entorno, la infraestructura, las specs o las pruebas contra contratos. Sí necesitás sus entregas y revisiones para cerrar ciertas tareas e integrar resultados válidos.

Este plan divide tus tareas en pasos pequeños. Los pasos no son nuevos issues: varios corresponden a T-00 o a una misma tarea. Se mantiene **una tarea por rama y PR**, con commits de cambios reales. El alcance y las dependencias oficiales del equipo siguen en `docs/02_planificacion/PLAN_SDD.md`; el estado común está en `docs/05_seguimiento/avance.md`.

## 1. Cómo usarlo sin abrumarte

1. Elegí un paso habilitado y trabajá en un solo resultado verificable.
2. Revisá qué necesitás, quién lo entrega y los archivos acordados antes de editar.
3. Al terminar, guardá la evidencia y marcá la casilla del paso. No cierres la tarea general si aún faltan sus otros criterios.
4. Si una dependencia se retrasa, pasá a la alternativa indicada. Preparar un borrador no equivale a integrar una tarea terminada.
5. Antes de cambiar de rama, preservá el trabajo y comprobá `git status`. El agente propone los commits; vos los revisás y ejecutás según el acuerdo actual.

No hay una fecha de entrega oficial confirmada en esta revisión. Este plan propone una secuencia por dependencias, sin inventar fechas ni prometer una duración.

## 2. Lo que hoy te puede bloquear

| Situación comprobada o pendiente | Qué bloquea | Quién lo resuelve | Qué podés hacer mientras |
|---|---|---|---|
| Entorno local preparado: `.venv` con Python 3.12.16; `python3` del sistema sigue en 3.9.6 | Usar el proyecto desde el entorno activado. | Vos. | Activar `.venv`; versión, dependencias, tests y lint registrados en la [evidencia de T-00](../../05_seguimiento/evidencia/ENTORNO_T00.md). |
| Preparación de T-00 en `docs/T-00-guia-angel`, pendiente de revisión e integración | Cambiar de tarea conservando el trabajo de esta rama. | Vos registrás y subís el trabajo. Ricky revisa tu PR. | Revisar el diff antes de cambiar de tarea y conservar el historial. |
| C: Angel (`Angelzam21`); A y propietario: Ricky (`rosseab-bit`); B: Brian, usuario pendiente. Invitaciones aceptadas según el usuario el 31 de octubre | Completar asignaciones, verificar escritura de Brian y proteger `main`. | Brian: usuario y prueba de acceso; Ricky: reglas. | CODEOWNERS incluye A/C; completar B al confirmar su usuario y escritura. |
| No hay `gh` en PATH | Publicar issues desde el generador; la prueba local sí funciona con Bash 3.2 y Python 3. | Vos, si elegís automatizar. | Validar con `DRY_RUN=1` o crear issues desde GitHub. No bloquea Git ni los commits. |
| Ruff detectó observaciones en archivos de A y B | Dejar la CI verde si reproduce esas observaciones. | A en transform; B en validate, o quien ellos acuerden. | Preparar el workflow y registrar los fallos; no ocultar la verificación ni cambiar archivos ajenos sin acuerdo. |
| T-01 y contratos pendientes de aprobación | Cerrar XG-1 y decisiones compartidas de datos/modelado. | Los tres. | Borrador de spec de XGBoost y visualización. |
| `schema.sql` existe, pero T-03 no tiene aceptación verificada | Cerrar ETL-4, VIZ-2 y XG-2 según el plan. | A entrega esquema/criterios; revisión correspondiente. | Leerlo y preparar tests contra la referencia, identificando qué sigue provisional. |
| La etiqueta usa test para algunos cálculos de train | Cerrar ETL-5 como válido y obtener resultados definitivos. | A coordina ETL-3, con acuerdo de los tres. Vos verificás integración. | Tests de carga, fixtures y diseño. No hace falta paralizar infraestructura por este problema. |
| No están los módulos comunes de modelado en esta copia | Baseline y búsqueda integrados de XGBoost. | B: preprocesador, split/CV, evaluación y runner; A: lectura/persistencia. | Spec, wrapper del modelo y tests con datos ficticios. |
| CMP-2 aún no está | Cerrar gráficos comparativos y dashboard según sus dependencias. | A, después de los runs de los tres. | Diseñar y probar gráficos/app con fixtures, sin presentar resultados ficticios como reales. |

La ausencia de un módulo en esta copia no demuestra que nadie lo esté preparando en otra rama. Pedí el issue/PR y la entrega que lo habilita; no adivines su estado. La lectura de `main` remoto sigue mostrando el commit inicial en esta revisión.

## 3. Primer bloque: dejarte listo para trabajar

### Paso 0. Ordenar y revisar la documentación actual

**Qué hacemos:** revisar la reorganización y los documentos preparados, decidir el alcance del PR documental y registrar los cambios antes de iniciar otra tarea en este checkout.

**Por qué:** las reglas y rutas tienen que estar disponibles para A y B; cambiar de rama con todos estos archivos pendientes puede mezclar tareas.

**Qué necesitás:** `git status`, lectura del diff y revisión de los archivos nuevos; el agente puede explicar cada bloque. No hace falta reescribir ni borrar el commit inicial.

**Terminaste este paso cuando:** sabés qué cambió, conservaste todo y el trabajo quedó registrado para revisión. Publicar y mergear el PR es un cierre posterior con A, no algo que el agente haga sin tu indicación.

- [x] Documentación previa preservada y registrada hasta `2d9ac70`, subida a la rama documental. Revisión e integración en main pendientes.

### Paso 1. Preparar un entorno Python compatible — T-00

**Qué hacemos:** seleccionar un Python 3.11 o posterior, crear `.venv` en la raíz e instalar dependencias y el paquete. Verificar versión, configuración, tests y lint.

**Por qué:** un resultado reproducible necesita un entorno que puedas abrir de nuevo; el Python 3.9 del sistema no satisface `pyproject.toml`.

**Qué necesitás:** un ejecutable compatible disponible o instalarlo. Antes de crear el entorno, comprobar su versión; no asumir que `python3` ya apunta al correcto. Este paso no depende de A ni B.

Una vez creado y activado el entorno con ese intérprete:

```bash
python --version
python -m pip install -r requirements.txt
python -m pip install -e .
python -c "from demanda.config import load_config; print(load_config()['semilla'])"
python -m pytest -q
python -m ruff check src tests
```

**Terminaste cuando:** Python cumple la versión, la configuración imprime `42`, podés ejecutar las verificaciones y registraste su salida. Si lint o tests fallan, diferenciar problemas de entorno de defectos del código y coordinar con su dueño antes de cerrar T-00/T-15.

- [x] Entorno propio compatible y verificación inicial registrada. Ver [evidencia del 30 de octubre de 2026](../../05_seguimiento/evidencia/ENTORNO_T00.md): semilla `42`, 29 tests y 3 subcasos aprobados; dos observaciones de lint preexistentes pendientes de A/B. Este paso no cierra T-00/T-15.

### Paso 2. Confirmar personas, accesos y entregas — T-00

**Qué hacemos:** confirmar las cuentas de A/B, tu usuario real de GitHub, acceso al repo y quién tiene permisos para administrar sus reglas. Pedir a A el estado de T-03 y ETL-3; a B, el de validación y módulos comunes.

**Por qué:** ser responsable del área no garantiza tener permisos administrativos; un nombre personal tampoco reemplaza al usuario en GitHub.

**Qué necesitás:** respuestas concretas de A/B y del administrador si no sos vos. Podés preparar el resto de T-00 mientras llegan.

**Terminaste cuando:** cuentas y accesos están confirmados y cada dependencia tiene un issue/PR o un siguiente paso identificado.

- [ ] Responsables, acceso y puntos de entrega confirmados.

Ver la [evidencia de personas y próximos pasos](../../05_seguimiento/evidencia/INFRAESTRUCTURA_T00.md#personas-acceso-y-dependencias). La hipótesis de permisos iguales para el tercer integrante no acredita su acceso.

### Paso 3. Completar las reglas del repo — T-00

**Qué hacemos:** preparar `CODEOWNERS`, plantilla de PR, instrucciones instalables y seguimiento. Confirmar que A y B pueden instalar sus copias. Configurar PR y aprobación en `main`; el check obligatorio se añade después de ejecutar T-15.

**Por qué:** esto evita que todos editen lo mismo y establece cómo entran los cambios compartidos.

**Qué necesitás:** cuentas confirmadas y permiso del administrador para las reglas remotas. Vos preparás los archivos; A revisa tus cambios.

**Terminaste cuando:** las asignaciones son reales, la plantilla y documentación están revisadas, el equipo puede trabajar y las reglas remotas están verificadas. Sin permiso de administración, pedí esa configuración al administrador; no te bloquea preparar los archivos.

- [ ] Infraestructura de T-00 preparada y acceso del equipo validado.

Preparación local disponible: `CODEOWNERS` parcial y plantilla de PR; instalación desde copia nueva verificada. Las [instrucciones para el propietario](../../05_seguimiento/evidencia/INFRAESTRUCTURA_T00.md#configuración-para-el-propietario) permiten configurar las reglas y registrar la evidencia pendiente.

### Paso 4. Organizar issues y tablero — T-00

**Qué hacemos:** comprobar si ya hay issues, crear los faltantes y asignar responsables y dependencias. Elegir entre hacerlo desde GitHub o usar `scripts/crear_issues.sh` con sus herramientas compatibles.

**Por qué:** sin un lugar donde reservar archivos y registrar bloqueos, las guías por sí solas no coordinan el trabajo.

**Qué necesitás:** acceso al repositorio y las tareas del plan actualizado. El generador lee las tareas del plan y valida dependencias. La prueba local no requiere `gh`; la publicación sí. Si ya hay issues, el script se detiene y se completan los faltantes manualmente.

**Terminaste cuando:** podés identificar y tomar cada tarea por su issue, con dueño y dependencias. No es obligatorio instalar `gh` para crear issues manualmente.

- [ ] Issues y tablero utilizables, sin duplicados.

Dry-run verificado: 50 tareas y dependencias válidas, sin publicación. El [procedimiento de issues y tablero](../../05_seguimiento/evidencia/INFRAESTRUCTURA_T00.md#issues-y-tablero) conserva el generador único; primero se confirman las cuentas y se integra la documentación en main.

### Paso 5. Automatizar las verificaciones — T-15

**Qué hacemos:** crear el workflow de GitHub Actions con instalación, pytest y Ruff; ejecutarlo en un PR y marcar el job `test` como obligatorio cuando esté disponible.

**Por qué:** cada integración debe comprobarse en un entorno común, no depender de la computadora de quien la escribió.

**Qué necesitás:** T-00 cerrado, aprobación de A y permisos para el check obligatorio. Hay 25 tests existentes: no hace falta tolerar ausencia de tests. Coordinar con A/B los errores de lint de sus módulos.

**Terminaste cuando:** el job corre, detecta fallos reales y queda requerido en `main`. Un workflow escrito pero nunca ejecutado no cierra T-15.

- [ ] CI ejecutada y check obligatorio confirmado.

## 4. Segundo bloque: acordar antes de integrar

### Paso 6. Cerrar decisiones y criterios — T-01 y CMP-1

**Qué hacemos:** acordar objetivo y momento de clasificación, tratamiento de la fuga temporal, unidades, datos, contratos y criterios de comparación. Vos preparás la spec de visualización: qué muestra la app, filtros y comportamiento sin datos.

**Por qué:** comparar modelos necesita la misma pregunta, datos y reglas. Si cada integrante los define por separado, las métricas no son comparables.

**Qué necesitás:** A y B para aprobar T-01. CMP-1 se cierra después de T-01 y antes de ver resultados. Podés preparar tu borrador antes de la reunión, sin darlo por aprobado.

**Terminaste cuando:** las decisiones y contratos están registrados y aprobados. Pedí que la independencia temporal se pruebe para el método elegido, no solo para una alternativa.

- [ ] Acuerdos comunes y criterios de comparación aprobados.

### Paso 7. Especificar tu XGBoost — XG-1

**Qué hacemos:** explicar por qué usar boosting, definir el espacio de búsqueda y documentar etiquetas de texto, probabilidades por clase y pesos para desbalance.

**Por qué:** XGBoost debe conectarse al mismo sistema que los otros modelos; no conviene resolver sus diferencias dentro de un runner paralelo.

**Qué necesitás:** T-01 y acuerdo con B sobre interfaz y pesos calculados dentro de cada fold. Los cambios al contrato requieren revisión de los otros dos.

**Terminaste cuando:** `docs/07_especificaciones/02-modelo-xgb.md` y el contrato describen una implementación y verificaciones concretas, sin decisiones pendientes escondidas.

- [ ] Spec y contrato de XGBoost aprobados.

## 5. Tercer bloque: tu parte del ETL y una base para probar

### Paso 8. Validar la carga de SQLite — ETL-4

**Qué hacemos:** revisar el `load.py` existente y completar pruebas: repetición sin duplicados, NULL, auditoría, rollback durante la carga y conservación/limpieza de resultados según reset.

**Por qué:** una carga debe dejar todo el resultado nuevo o conservar el anterior; no puede quedar a medias. El código ya existe, así que la entrega parte de evidencia y cambios necesarios, no de reescribirlo para crear commits.

**Qué necesitás:** T-03 de A aprobado y un archivo de tests acordado. Usá BD temporal y, preferentemente, `tests/test_load.py`; coordiná antes si necesitás editar el archivo compartido `tests/test_etl.py`.

**Terminaste cuando:** las pruebas significativas pasan, podés explicar la transacción y A aprueba tu PR. La fuga de transform no impide probar la carga con datos controlados, pero sí cerrar luego el ETL completo.

- [ ] ETL-4 probado y aceptado.

### Paso 9. Crear la BD ficticia — VIZ-2

**Qué hacemos:** generar una fixture de 36 meses y tres runs identificados con `fixture_`, respetando el esquema y sus restricciones.

**Por qué:** permite desarrollar gráficos y app sin esperar los entrenamientos reales de los tres integrantes.

**Qué necesitás:** T-03 aprobado. No necesitás los modelos entrenados ni esperar a ETL-5. Es otra tarea: otra rama y PR, no un agregado al PR de carga.

**Terminaste cuando:** los tests crean la BD temporal de forma reproducible, con conteos, matrices y métricas ficticias coherentes y claramente identificadas.

- [ ] VIZ-2 disponible para el equipo.

### Paso 10. Cerrar la integración del ETL — ETL-5

**Qué hacemos:** revisar pipeline y CLI existentes, probar el CSV real y entradas inválidas, verificar ausencia de escrituras parciales y guardar la auditoría.

**Por qué:** esta entrega habilita lectura de datos, preprocesamiento y visualización para el resto del equipo.

**Qué necesitás:** ETL-1, ETL-2, ETL-3 y ETL-4 integrados y aceptados. A debe corregir la contaminación temporal antes de dar la salida por válida. Si el error del CLI depende de extracción o validación, coordiná la interfaz con sus dueños.

**Terminaste cuando:** una ejecución produce los datos esperados, la validación falla limpiamente y la prueba temporal está aprobada. Como referencia actual hay 308 filas limpias y 3.450 de distribuidoras; las cantidades por clase deben medirse de nuevo después de corregir la etiqueta. Avisá a A y B al mergear.

- [ ] ETL integrado, válido y anunciado al equipo.

## 6. Cuarto bloque: gráficos y modelo

### Paso 11. Crear gráficos de datos — VIZ-1

**Qué hacemos:** implementar las cuatro figuras acordadas en `viz/plots.py`: clases por split, demanda/temperatura, estacionalidad y serie con críticos.

**Por qué:** ayuda a entender los datos y genera piezas reutilizables en dashboard y presentación.

**Qué necesitás:** ETL-5 para aceptar el trabajo con datos reales; VIZ-2 para las pruebas con fixture. Si A no confirmó unidades, mantenerlas identificadas como pendientes en borradores, sin inventarlas para la entrega final.

**Terminaste cuando:** las funciones reciben datos y devuelven figuras, no leen la BD, y pasan los tests de humo. Los gráficos tienen títulos claros y distinción de clases que no depende solo del color.

- [ ] Gráficos base verificados.

### Paso 12. Implementar el módulo XGBoost — XG-2

**Qué hacemos:** escribir el wrapper y tests de etiquetas, clonación, parámetros, probabilidades y pesos.

**Por qué:** el resto del proyecto debe seguir viendo nombres de clases y la interfaz común, aunque el estimador use codificación interna.

**Qué necesitás:** XG-1 y T-03 aprobados. Podés usar datos ficticios en tests; no necesitás esperar el runner terminado para probar el módulo aislado.

**Terminaste cuando:** funciona con la interfaz acordada y las columnas de probabilidades corresponden a `classes_`. No asumir el orden Normal/Alta/Crítica.

- [ ] Módulo XGBoost compatible y probado.

### Pasos 13 a 17. Obtener y explicar resultados reales

Hacelos en orden, con las ramas y PR de cada tarea. Si falta un módulo común, prepará tests o documentación contra el contrato; no copies la implementación de A/B dentro de tu modelo.

| Paso | Qué hacemos y por qué | Qué necesitás / de quién dependés | Cómo sabés que terminaste |
|---|---|---|---|
| **13. XG-3: baseline** | Entrenar una primera versión reproducible para tener una referencia antes de buscar mejoras. | XG-2; MC-1/MC-2/MC-3 de B para preprocesar, separar y evaluar y DB-1 de A para lectura integrada. Si el runner falta, acordar una ejecución provisional sin crear otro runner compartido. | Parámetros, fechas, semilla y métricas documentados; comparación de pesos según el protocolo aprobado. |
| **14. XG-4: búsqueda** | Buscar parámetros con validación temporal sobre train. Evita elegir por intuición o por el resultado final. | Baseline; CV de B y pesos por fold aprobados. | Mejores parámetros, score CV y tiempo registrados, con prueba de que cada fold usa solo su entrenamiento. |
| **15. XG-5: evaluación y ablación** | Medir el modelo elegido y el efecto de participaciones y potencia. | XG-4 y MC-3 de B; datos/etiqueta definitivos. | Tabla y matrices reales por conjunto; muestras comparables o diferencias explicadas. No reutilizar como definitivos los conteos de clase previos a la corrección del ETL. |
| **16. XG-6: persistencia** | Guardar resultados y configuración para que otros los consulten sin volver a entrenar. | MC-4 de B y DB-2 de A, además de XG-5. | SQL verifica runs únicos, probabilidades por clase, métricas y configuración; mismas reglas que LR y RF. |
| **17. XG-7: explicación** | Escribir notebook y sección de model card: qué hizo el modelo, dónde falla y qué límites tiene. | XG-6 y resultados reales accesibles. | Notebook reproducible, importancia por gain, análisis de errores y conclusiones que podés defender. |

**Cuidado con test:** el baseline y la elección de parámetros usan validación temporal de train. Test queda para la evaluación final de XG-5. Esta aclaración se incorpora al plan y las fichas como criterio a revisar en T-01, antes de ejecutar los modelos.

- [ ] Paso 13: baseline aceptado.
- [ ] Paso 14: búsqueda temporal aceptada.
- [ ] Paso 15: evaluación y ablación aceptadas.
- [ ] Paso 16: runs guardados y verificados.
- [ ] Paso 17: notebook y explicación aceptados.

## 7. Quinto bloque: comparación, dashboard y entrega

### Paso 18. Dibujar la comparación — CMP-3

**Qué hacemos:** gráficos de métricas, matrices lado a lado, F1 por clase, tiempos y ablación.

**Por qué:** el equipo y el docente necesitan comparar bajo la misma escala y entender los errores, no solo ver una lista de scores.

**Qué necesitás:** CMP-2 de A, que espera los runs de los tres y CMP-1, más tus gráficos VIZ-1. Podés preparar el diseño con VIZ-2 antes; el cierre requiere datos reales y comparables.

**Terminaste cuando:** B puede usar la tabla y gráficos para CMP-4 y el equipo puede decidir en CMP-5 conforme a los criterios ya acordados.

- [ ] Comparación gráfica disponible y validada.

### Paso 19. Completar el dashboard — V-1

**Qué hacemos:** app Streamlit con Datos, Modelos, Comparación, Predicciones y Calidad; filtros y mensajes cuando falta la base o no hay runs.

**Por qué:** reúne la entrega visual y permite explorar resultados sin abrir código ni ejecutar SQL manualmente.

**Qué necesitás:** CMP-3 para cerrar la tarea. Mientras esperás, podés preparar pantallas y pruebas con fixture contra los contratos aprobados, sin marcar la app como terminada.

**Terminaste cuando:** solo lee la BD, funciona con datos reales, los filtros son coherentes y pasa el test con AppTest. No confundir que la página abra con que todo su contenido esté verificado.

- [ ] Dashboard completo y revisado.

### Paso 20. Participar en la decisión y preparar la entrega — CMP-5, F-2 y F-3

**Qué hacemos:** decidir con A/B después de CMP-4; revisar los PR de B; completar tu sección del informe y README; acordar acceso del docente a la BD y colaborar con 6 a 8 diapositivas PDF/PPTX.

**Por qué:** tu responsabilidad incluye explicar y entregar la solución. La exposición vale tanto como cada uno de los otros bloques de la rúbrica.

**Qué necesitás:** resultados y análisis final, revisión cruzada y ejecución completa F-1 de B para el cierre integrado. La consolidación de diapositivas y la subida al campus deben tener una persona asignada; no se suponen automáticamente a tu cargo. Borradores y reparto pueden prepararse mucho antes.

**Terminaste cuando:** tu parte está revisada, la BD es accesible, el archivo definitivo existe y la subida al campus está confirmada. Un archivo guardado localmente no acredita la entrega externa.

- [ ] Decisión, revisión y entregables conjuntos confirmados.

### Paso 21. Ensayar y defender — F-4

**Qué hacemos:** comprobar desde una copia nueva la instalación y ejecución, y ensayar una defensa conjunta de 8 a 10 minutos.

**Por qué:** permite detectar pasos que solo funcionan en tu computadora y preguntas que todavía no podés explicar.

**Qué necesitás:** F-3, script completo de B, BD y resultados accesibles, reparto de exposición y cronómetro.

**Terminaste cuando:** los tres pueden reproducir y explicar el proyecto; tu intervención cubre infraestructura, carga, XGBoost y gráficos con ejemplos y limitaciones reales. Registrar duración y ajustes del ensayo.

- [ ] Ejecución y defensa ensayadas.

## 8. Qué pedir a A y B

Estos son mensajes para que vos los adaptes y envíes por el canal del equipo; el agente no los publica.

**A:** confirmar estado y PR de T-03; acordar la corrección temporal de ETL-3 y el test que la acredita; confirmar contratos y próximas entregas de DB-1/DB-2. Más adelante, avisar cuándo estará CMP-2. A también revisa tus PR.

**B:** acordar `sample_weight` por fold e interfaz de modelos; confirmar estado y PR de MC-1/MC-2/MC-3 y después MC-4; coordinar la corrección de lint en validate. Vos revisás sus PR.

**Los tres:** cerrar decisiones, reservar archivos compartidos, definir quién consolida y sube diapositivas, cómo accede el docente a la BD y cuál es la fecha oficial de entrega.

## 9. Tu próxima sesión

Empezá por el **paso 0**. Si necesitás esperar la revisión de A, aprovechá para completar el entorno del **paso 1** y confirmar cuentas del **paso 2**. El siguiente objetivo es cerrar T-00, no entrenar XGBoost todavía.

Prompt breve para continuar:

```text
Soy Angel Zambrano. Vamos a realizar solo el paso <número> de mi plan personal.
Leé el plan, las reglas del agente y la ficha de la tarea correspondiente.
Verificá rama, cambios previos, dependencias y archivos antes de editar.
Explicame qué haremos y por qué; avanzá dentro del alcance acordado.
Mostrá las verificaciones y el siguiente paso habilitado. No hagas commit ni push.
```
