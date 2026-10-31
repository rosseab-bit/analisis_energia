# Cómo trabajar con mi agente de IA

Guía práctica del equipo, revisada el 30 de octubre de 2026.

**El agente prepara cambios y muestra evidencia; vos revisás, decidís y tenés que poder explicar lo que entregás.** Según el acuerdo actual del equipo, los commits los hace cada integrante con su identidad de Git.

## 1. Qué documento usar

| Para qué | Dónde buscar |
|---|---|
| Alcance, entregables y dependencias | [PLAN_SDD.md](../02_planificacion/PLAN_SDD.md) y el issue de la tarea. |
| Dueños, archivos compartidos, revisores y bloqueos | [ORDEN_Y_COORDINACION.md](../02_planificacion/ORDEN_Y_COORDINACION.md). |
| Instalación y procedimiento general | [GUIA_EQUIPO.md](GUIA_EQUIPO.md). |
| Criterios y prompt de tu tarea | [TAREAS_A.md](../04_integrantes/A/TAREAS_A.md), [TAREAS_B.md](../04_integrantes/B/TAREAS_B.md) o [TAREAS_C.md](../04_integrantes/Angel_Zambrano/TAREAS_C.md). Esta última corresponde a Angel Zambrano. |
| Cómo pedir, revisar y continuar trabajo con el agente | Esta guía. |

El orden de tareas y las asignaciones se mantienen en el plan y las fichas. No hace falta copiarlos en cada guía.

## 2. Antes de pedir cambios

1. **Abrí el proyecto correcto.** Si ya tenés el repositorio, usá esa copia. Si empezás en otra computadora, seguí la instalación de la guía del equipo; no clones otra copia por cada tarea.
2. **Revisá `git status`.** Identificá cambios pendientes y quién los hizo. Una conversación nueva no limpia archivos, cambia de rama ni guarda el trabajo anterior.
3. **Confirmá tarea, responsable y dependencias.** Reservá los archivos en el issue según la guía de coordinación. Creá la rama desde `main` actualizado cuando tengas el árbol limpio.
4. **Pedí la lectura de las reglas explícitamente.** No supongas que cualquier agente carga `docs/03_guias/CLAUDE.md` de forma automática. Indicá los archivos y pedile que distinga los leídos de los que no pudo encontrar.
5. **Comprobá el punto de partida.** El agente debe revisar qué código existe y qué pruebas están disponibles antes de proponer una implementación nueva. Un archivo de referencia no equivale a una tarea aceptada.

La identidad del commit y la autenticación para hacer push son configuraciones distintas. Podés verificarlas sin publicar cambios; no necesitás volver a configurarlas en cada tarea si ya funcionan.

## 3. Prompt de arranque reutilizable

Completá los campos y después agregá el prompt de la ficha. Si falta un dato, dejalo identificado en lugar de inventarlo.

```text
Trabajo en la tarea <ID y título>, issue <#N o pendiente>, como <A, B o Angel Zambrano>.
La rama es <rama>. El objetivo verificable es <resultado esperado>.
Archivos acordados para editar: <lista>. Dependencias: <estado y PRs, si existen>.

Leé docs/03_guias/CLAUDE.md, la tarea en docs/02_planificacion/PLAN_SDD.md
y mi ficha en <ruta-completa-dentro-de-docs/04_integrantes/>.
Consultá docs/02_planificacion/ORDEN_Y_COORDINACION.md para dueños y revisiones, y las specs y el diccionario
que correspondan a esta tarea. Indicá qué archivos leíste y cuáles faltan.

Antes de editar, revisá git status y la implementación existente. Identificá riesgos,
criterios de aceptación y pruebas relevantes. Si falta una dependencia, distinguí
el trabajo que puede prepararse del que todavía no puede integrarse.

Seguí spec/criterio, tests cuando correspondan, implementación y documentación.
Avanzá en cambios pequeños y verificables. Resolvé los detalles rutinarios dentro
del alcance; consultá si necesitás cambiar un contrato, una decisión metodológica
no acordada o archivos de otra persona.

Preservá los cambios previos. No inventes datos, unidades, métricas ni verificaciones.
Mostrá los comandos ejecutados y sus resultados; si algo no se pudo ejecutar, decilo.
Al terminar un bloque, resumí qué cambió y proponé un mensaje tipo(ID): descripción.
No hagas commit, push ni merge: los hago yo después de revisar.
```

**No pegues la ficha a ciegas.** Si pide crear algo que ya existe, partir de una suposición incorrecta o cambiar un contrato pendiente, pedile primero que señale la diferencia. El criterio aprobado y el estado real del proyecto deben guiar la implementación.

## 4. Trabajar por bloques que puedas revisar

| Bloque | Qué pedirle al agente | Qué revisás vos |
|---|---|---|
| **Criterio** | Identificar el comportamiento esperado, su spec y qué archivos necesita. | Que corresponde al issue y no incorpora decisiones ajenas al alcance. |
| **Pruebas** | Probar casos relevantes y explicar qué defecto detectan. | Si hay un defecto o comportamiento nuevo, que la prueba lo detecte antes del arreglo; si el código ya cumple, que la prueba lo verifique de forma significativa. |
| **Implementación** | Hacer el cambio mínimo necesario y explicar las decisiones. | El diff completo, claridad del código, respeto por contratos y archivos acordados. |
| **Verificación y docs** | Ejecutar las comprobaciones pertinentes y documentar uso, evidencia y límites. | Resultados observados, casos pendientes y que se pueda reproducir la entrega. |

No toda tarea necesita código o tests nuevos: una spec o un diccionario se valida por coherencia y evidencia. Tampoco un test que ya pasa es automáticamente inútil; puede verificar una funcionalidad existente. Lo importante es que detecte un fallo relevante, no forzar un resultado rojo artificial.

Durante el trabajo, ejecutá las pruebas del módulo afectado. Antes del PR de código o CI, corré la suite y el linter requeridos por el equipo. Las comprobaciones que el agente ejecute deben quedar identificadas; repetí vos las verificaciones de aceptación antes de entregar y guardá el resultado.

### Comandos para revisar lo que realmente cambió

```bash
git status --short
git diff
git diff --cached
```

`git diff` no muestra archivos nuevos sin seguimiento: abrilos y leelos también. Después de hacer tus commits y actualizar la referencia remota, podés revisar lo que llevaría el PR:

```bash
git fetch origin
git diff origin/main...HEAD
```

Esa comparación muestra cambios commiteados de la rama; no reemplaza revisar lo que todavía está sin commit.

## 5. Qué evidencia pedir y qué errores evitar

| Situación | Respuesta útil |
|---|---|
| El agente dice que los tests pasan | Pedí comando, entorno, resumen y pruebas omitidas o saltadas. Si faltan dependencias o hay un error de ejecución, no cuenta como una prueba aprobada. |
| Modifica archivos fuera de la tarea | Revisá el diff, identificá qué cambio introdujo y retiralo de forma selectiva. No uses una restauración completa que pueda borrar trabajo previo. Coordiná con el dueño si el cambio es necesario. |
| Un test pasa antes de implementar | Comprobá si la funcionalidad ya existía. Para un defecto, verificá que el caso reproduce el problema y que falla por la razón correcta; no por un import o entorno roto. |
| Usa test para entrenar, ajustar transformaciones o elegir parámetros | Corregí la fuga. Separar, inspeccionar o evaluar test no es por sí mismo una fuga: el problema es usarlo para decisiones que deben tomarse con train. |
| Cambiar test altera umbrales o etiquetas de train | Revisá toda la construcción del objetivo, no solo el cálculo final del percentil. La prueba debe cubrir el método configurado y sus pasos intermedios. |
| Propone features que reconstruyen la etiqueta | Usá los conjuntos acordados en config. Excluir demanda total, ratio de tendencia, etiqueta, split, fecha y sectores absolutos según las reglas del proyecto. |
| Presenta una mejora de métricas | Pedí valores anteriores y nuevos, comandos y configuración. Verificá mismas fechas, datos y criterio; no elegir parámetros por el resultado de test. |
| Cambia semilla, rutas o reglas sin explicarlo | Revisá configuración y contrato. No aceptar ajustes de reglas compartidas ocultos en la implementación. |
| Imputa sectores o distribuidoras en el ETL | Recordá que esos nulos representan datos inexistentes. La imputación acordada para modelos se ajusta dentro del pipeline usando train. |
| Muestra resultados casi perfectos | Reproducí y revisá el objetivo, las features, la separación temporal y la ablación. Una cifra alta no demuestra por sí sola un error ni una buena solución. |
| Usa datos ficticios o modifica el CSV para una prueba | Exigí una copia temporal o fixture identificada. No sobrescribir el dataset original ni presentar métricas ficticias como resultados reales. |

**Estado del ETL:** consultá [avance general](../05_seguimiento/avance.md) antes de trabajar sobre etiquetas. La asignación y corrección de un defecto no se mantienen como una segunda lista en esta guía; no pidas modificar esa regla de paso desde otra tarea.

## 6. Ejemplo para Angel Zambrano: revisar ETL-4

Usá este pedido después del prompt de arranque, cuando esté acordado el esquema de T-03 y los archivos a editar. Preparar pruebas contra una referencia antes de esa aprobación no cierra la dependencia.

```text
Tarea ETL-4. Revisá la implementación existente de src/demanda/etl/load.py contra
los criterios de carga y auditoría de docs/07_especificaciones/01-datos.md y la ficha docs/04_integrantes/Angel_Zambrano/TAREAS_C.md.

Trabajá en load.py y tests/test_load.py. Si necesitás tocar tests/test_etl.py,
indicá el motivo y coordinemos antes porque es un archivo compartido.

Primero distinguí qué comportamientos ya cumplen y qué falta probar o corregir.
Verificá con una BD temporal: carga idempotente, NULL, auditoría, rollback ante un
error durante la carga, conservación de resultados sin reset y limpieza con reset.
Usá registros ficticios identificados para probar las tablas de resultados.

No modifiques transform.py ni cambies la regla de etiqueta. Registrá como dependencia
la corrección de ETL-3. Mostrá comandos y resultados de las verificaciones y proponé
mensajes de commit solo para cambios reales. No hagas commit ni push.
```

Los mensajes reflejan el trabajo efectivamente realizado. Por ejemplo, `test(ETL-4): verifica conservación de resultados sin reset` solo corresponde si se agregó esa prueba. No inventes una implementación nueva ni cambios de documentación para completar una cantidad de commits.

## 7. Antes de entregar o continuar en otra sesión

### Checklist de entrega

- [ ] Cumple el criterio aprobado y puedo explicar el cambio.
- [ ] Revisé archivos modificados, nuevos y staged; preservé el trabajo previo.
- [ ] Las cifras y comprobaciones tienen evidencia; las limitaciones están indicadas.
- [ ] La verificación apropiada está aprobada; en código o CI, suite y linter del equipo.
- [ ] No hay contratos alterados sin acuerdo, datos originales modificados ni archivos locales que no deban subirse.
- [ ] Los commits propios tienen cambios reales y el formato acordado; se cumple el mínimo del plan.
- [ ] El PR enlaza el issue y pide revisión a la persona correcta según la guía de coordinación.

### Si cambiás de conversación o de agente

Podés abrir una sesión nueva cuando cambiás de tarea o se vuelve confuso el contexto. No es obligatorio reiniciar por cada paso. Antes de salir, pedí un resumen como este:

```text
Tarea y objetivo:
Rama y responsable:
Archivos cambiados y cambios previos que hay que preservar:
Último commit y cambios todavía sin commit:
Comandos ejecutados y resultados; verificaciones pendientes:
Decisiones aprobadas, bloqueos y dependencias:
Próximo paso concreto:
```

En la siguiente sesión, el agente debe leer ese resumen, verificar `git status` y los archivos reales, y continuar desde ahí. No asumir que el resumen prueba que algo está ejecutado, commiteado o mergeado.

Para branch, push, revisión, merge y cierre del issue, seguí [ORDEN_Y_COORDINACION.md](../02_planificacion/ORDEN_Y_COORDINACION.md). Esta guía no reemplaza las asignaciones ni los criterios del plan.
