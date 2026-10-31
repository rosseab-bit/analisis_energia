# Guía operativa del equipo

Versión 0.3. Este documento reúne la preparación del entorno de trabajo, las convenciones de commits, el checklist del revisor y la operación del ETL. Para otros temas se enlaza su documento principal, evitando mantener instrucciones completas en varios lugares.

## 1. Preparación

### Identidad y entorno

Cada integrante usa su propia identidad de Git. Comprobala con:

```bash
git config user.name
git config user.email
```

Si falta configurarla, usá tu nombre y un correo asociado a tu cuenta de GitHub. La identidad del commit y la autenticación para hacer push son configuraciones distintas.

La instalación, requisitos y comandos disponibles se mantienen en el [README técnico](../00_inicio/README.md). No clones otra copia por cada tarea; si ya tenés el repo, trabajá sobre esa copia y preservá sus cambios.

### Agente de IA

Abrí el agente en la raíz del repositorio y pedile explícitamente que lea `docs/03_guias/CLAUDE.md`. El prompt de arranque y el método de revisión están en [Cómo trabajar con mi agente](COMO_TRABAJAR_CON_MI_AGENTE.md). No se presupone que cualquier herramienta cargue las reglas automáticamente.

## 2. Arranque y acuerdos del equipo

El repo ya existe. Angel Zambrano completa T-00/T-15; cada integrante verifica su acceso y entorno. Los pasos técnicos de infraestructura están en la [ficha C](../04_integrantes/Angel_Zambrano/TAREAS_C.md), y el orden de entregas en [coordinación](../02_planificacion/ORDEN_Y_COORDINACION.md).

En T-01, los tres deben:

1. Confirmar responsables, revisores, canal de comunicación y disponibilidad.
2. Resolver D1-D7 en la [spec de datos](../07_especificaciones/01-datos.md), con evidencia del diccionario y la revisión temporal.
3. Aprobar contratos de preprocesado, evaluación, persistencia, modelos y visualización antes del código dependiente.
4. Acordar cómo se registran decisiones y cómo se reconocen los aportes del agente en los commits, si se usa un trailer de coautoría.

Los issues deben reflejar el plan actualizado. El script de creación, sus requisitos y la prevención de duplicados se revisan dentro de T-00; autenticar Git no instala ni autentica `gh`.

## 3. Ciclo por tarea y convención de commits

El procedimiento de rama, actualización, PR, revisión y merge se mantiene en [coordinación, sección 4](../02_planificacion/ORDEN_Y_COORDINACION.md#4-ciclo-de-una-tarea-y-revisión). Antes de empezar, verificá responsable, dependencias, reserva de archivos y árbol de trabajo.

El orden SDD y los criterios de cierre están en el [plan, sección 6](../02_planificacion/PLAN_SDD.md#6-definición-de-hecho-dod-por-tarea). Las tareas documentales se verifican con evidencia y coherencia; no requieren tests o commits artificiales.

Formato de commit:

```text
<tipo>(<ID>): <cambio concreto, en imperativo>
```

| Tipo | Uso |
|---|---|
| `feat` | Funcionalidad nueva. |
| `fix` | Corrección de un error. |
| `test` | Pruebas. |
| `docs` | Documentación, specs o explicación de resultados. |
| `refactor` | Reorganización sin cambiar comportamiento. |
| `data` | Datos, esquema o configuración de datos. |
| `chore` | Dependencias, CI y mantenimiento. |

Ejemplos: `test(ETL-4): verifica rollback durante la carga`, `docs(T-02): documenta unidades confirmadas`. El mínimo de tres commits por tarea es el acuerdo del plan; cada commit aporta un cambio real y lo revisa su autor.

## 4. Trabajo con el agente

La [guía del agente](COMO_TRABAJAR_CON_MI_AGENTE.md) mantiene el prompt reutilizable, los bloques de trabajo, las señales de alarma y el resumen de continuación. Evitá pegar instrucciones de una ficha sin comprobar antes si el código ya existe y si sus dependencias están aprobadas.

## 5. Checklist del revisor

Este es el checklist para copiar al revisar un PR. Los dueños y revisores se consultan en [coordinación](../02_planificacion/ORDEN_Y_COORDINACION.md); las condiciones para mergear se mantienen en el plan.

- [ ] Cumple el issue, el entregable y la spec aplicable.
- [ ] Cambios acotados a archivos acordados; commits claros con ID de tarea.
- [ ] Pruebas significativas y verificaciones aprobadas; para docs, evidencia, enlaces y coherencia revisados.
- [ ] Test no interviene en ajuste, CV, pesos o decisiones que corresponden a train; se revisa también la construcción de la etiqueta.
- [ ] Features y configuración respetan las reglas acordadas; sin sectores absolutos ni variables prohibidas.
- [ ] Columnas, firmas, claves y probabilidades respetan los contratos; sus cambios tienen aprobación previa.
- [ ] Documentación actualizada; sin BD local, entorno o credenciales dentro del cambio.
- [ ] El autor puede explicar la implementación y sus limitaciones.

## 6. Operar y volver a ejecutar el ETL

Con el entorno compatible activo y desde la raíz del repositorio:

```bash
python scripts/run_etl.py
python scripts/run_etl.py --reset
```

La primera opción conserva resultados de modelos. `--reset` borra todas las tablas antes de recargar, incluidos esos resultados. Preservá las corridas que necesites antes de usarlo.

| Situación | Acción |
|---|---|
| BD nueva | Ejecutar el ETL sin reset y verificar resumen y auditoría. |
| Cambió el CSV o la etiqueta | Coordinar según el contrato, regenerar datos y reentrenar los modelos afectados. No comparar resultados obtenidos con reglas incompatibles. |
| Se necesita reiniciar la BD | Usar reset en la BD local acordada después de preservar los resultados necesarios. |
| Se rechazan datos inválidos | Leer el error y verificar que no se modificaron los datos anteriores. |
| Se necesita trazabilidad | Consultar `etl_auditoria`: archivo, SHA-256, conteos, nulos, umbrales, advertencias y configuración. |

Los criterios de aceptación se mantienen en la [spec de datos](../07_especificaciones/01-datos.md). La evidencia y los defectos abiertos están en [avance general](../05_seguimiento/avance.md); no se interpretan los tests aprobados como cierre automático del ETL.

## 7. Dependencias y trabajo en paralelo

Las dependencias por ID están en el [plan SDD](../02_planificacion/PLAN_SDD.md#5-tareas). El mapa operativo y las alternativas ante bloqueos están en [coordinación](../02_planificacion/ORDEN_Y_COORDINACION.md#3-orden-de-trabajo-avanzar-por-entregas).

Mientras falta una entrega, se pueden preparar specs, tests o fixtures contra un contrato identificado. Un stub o una BD de referencia no sustituyen la aceptación ni permiten presentar resultados provisionales como definitivos.

## 8. Seguimiento del proyecto final

El estado común se registra solo en [avance general](../05_seguimiento/avance.md): datos/ETL, modelos y métricas, BD, gráficos y dashboard, código y documentación, presentación, campus y defensa. Cada entrega tiene estado, responsable, evidencia y criterio de cierre.

En la reunión semanal se revisan los entregables de esa página y luego los issues/PR del tablero. Se asignan responsables pendientes y se registran bloqueos. La rutina diaria, los avisos y la revisión de aportes se mantienen en [coordinación, sección 5](../02_planificacion/ORDEN_Y_COORDINACION.md#5-contratos-datos-y-comunicación).

No se estima la nota contando tareas o commits; el alcance académico y la rúbrica se consultan en el plan y el seguimiento. Esta guía no mantiene una segunda copia de los estados ni de las casillas de entrega.

## 9. Dónde resolver problemas

| Problema | Referencia principal |
|---|---|
| Instalación, versión o comando no disponible | README técnico y evidencia del error completo. |
| Conflictos, cambios ajenos o contrato pendiente | Coordinación: archivos compartidos, PR y procedimiento de contratos. |
| Un cambio del agente no se entiende o no está verificado | Guía del agente: revisión por bloques y evidencia. |
| Etiquetas, datos o reglas temporales | Spec de datos, diccionario y seguimiento del defecto. |
| Wrapper, pesos o probabilidades de un modelo | Ficha del modelo y contrato aprobado; coordinar con B si afecta el runner. |

No se restauran archivos completos sin revisar el diff ni se ignoran errores de entrenamiento por clases ausentes. Los procedimientos concretos están en las referencias anteriores.

## 10. Cierre de entrega

Revisar los requisitos oficiales y compromisos internos en [avance general](../05_seguimiento/avance.md#2-requisitos-de-la-consigna-oficial). Las tareas se cierran con la [definición de hecho del plan](../02_planificacion/PLAN_SDD.md#6-definición-de-hecho-dod-por-tarea).

La entrega externa se acredita con acceso confirmado a la BD y registro de subida al campus, no con un archivo guardado localmente. No se repite aquí el checklist para evitar que dos listas indiquen estados distintos.
