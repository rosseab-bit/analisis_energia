# T-00: preparación de infraestructura

Evidencia del **30 de octubre de 2026**, sobre `2d9ac70`, en
`docs/T-00-guia-angel`. Identidad de A actualizada el **31 de octubre de 2026**
por confirmación del usuario; las consultas de GitHub conservan su fecha original.
El estado vigente de la tarea se mantiene en
[avance general](../avance.md). Esta preparación cubre archivos locales,
consulta de GitHub y verificación de instalación; no acredita el cierre de T-00.

## Archivos preparados

- [CODEOWNERS](../../../CODEOWNERS): asigna a `Angelzam21` las áreas confirmadas
  de infraestructura, dependencias y carga, y a `rosseab-bit` (A) datos,
  extracción, transformación y BD. El propietario y Angel figuran como
  responsables del propio archivo. B queda pendiente de identificar.
- [Plantilla de PR](../../../.github/pull_request_template.md): incluye issue,
  criterio previo, alcance, dependencias, evidencia, definición de hecho y
  checklist de revisión del equipo.
- [README técnico](../../00_inicio/README.md): instalación y comandos disponibles.
  Las rutas de entrenamiento y dashboard siguen identificadas como previstas.

CODEOWNERS toma efecto para solicitudes de revisión cuando está en la rama base
del PR. La plantilla también debe integrarse en la rama predeterminada para su
uso habitual. Los usuarios asignados deben tener escritura; son requisitos de
[GitHub para CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).
Se sigue solicitando el revisor cruzado acordado: A revisa a Angel, Angel a B y B a A.

## Personas, acceso y dependencias

Las consultas se conservan en [github_T00.json](github_T00.json).

- Cuenta conectada: `Angelzam21`; lectura y escritura informadas por la conexión.
- Propietario y responsable A: Ricky (`rosseab-bit`), confirmado por el usuario el
  31 de octubre de 2026. A también revisa los PR de Angel.
- Responsable B: Brian, confirmado por el usuario el 31 de octubre de 2026;
  usuario de GitHub y permisos de escritura pendientes de confirmar. Sus permisos no
  se dan por confirmados a partir de una suposición.
- Invitaciones aceptadas, según confirmó el usuario el 31 de octubre de 2026.
  Esta confirmación no identifica el usuario de Brian ni acredita sus permisos de escritura.
- `main`: commit `96fafa6`, `protected: false`; la consulta de rulesets devolvió
  una lista vacía. No se encontraron issues ni PR en esta revisión.
- La consulta detallada de protección devolvió 403 por restricciones de la
  integración. La conexión informa `admin: false`, pero eso no permite deducir
  todos los privilegios reales de la cuenta al entrar desde la web.

Próximas confirmaciones del equipo:

| Persona | Entrega o confirmación necesaria | Próximo paso |
|---|---|---|
| A: Ricky, `rosseab-bit` | T-03: esquema y aceptación; ETL-3: corrección temporal y test | Compartir issue/PR o indicar la siguiente entrega. |
| B: Brian, usuario pendiente | ETL-2: validación y lint; MC-1 a MC-4: componentes comunes | Compartir issues/PR y confirmar las interfaces disponibles. |
| A y B | Instalación, semilla y resultados de verificaciones en sus equipos | Adjuntar versión de Python, `pip check`, semilla, pytest y Ruff. |
| Ricky, `rosseab-bit` | Usuario de Brian y permisos de escritura; reglas de main | Verificar permisos y aplicar la configuración siguiente. |

## Configuración para el propietario

En [Settings del repositorio](https://github.com/rosseab-bit/analisis_energia/settings):

1. En colaboradores, verificar las cuentas y acceso de escritura. Las invitaciones
   ya están aceptadas según la confirmación del usuario. A es Ricky (`rosseab-bit`);
   B es Brian, cuyo usuario de GitHub queda por confirmar.
2. En **General → Pull Requests**, habilitar merge commits y deshabilitar squash
   y rebase para seguir el acuerdo del equipo.
3. En **Branches**, crear una regla de protección para `main`: exigir PR y al
   menos una aprobación de otro integrante; invalidar aprobaciones al cambiar
   el contenido; mantener deshabilitados force push y borrado de la rama.
4. Aplicar las restricciones también a administradores. Mantener desactivado
   el requisito de historial lineal para permitir merge commits.
5. Mantener la aprobación general de otro integrante. Revisar la cobertura de
   CODEOWNERS y la revisión cruzada antes de exigir aprobaciones de code owners:
   las áreas cuyo único dueño sea el autor necesitan un revisor diferente.
6. Agregar el check obligatorio `test` después de implementar, ejecutar e
   integrar T-15. No se acredita CI por escribir una regla o un workflow.
7. Registrar captura o consulta verificable de la configuración y comprobar
   en un PR que se exige la aprobación y, tras T-15, el check.

Referencia de las opciones: [protección de ramas de GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
Esta sesión dejó instrucciones y evidencia de lectura; la configuración remota
requiere la intervención del propietario o de una cuenta con los permisos necesarios.

## Issues y tablero

El único generador sigue siendo `scripts/crear_issues.sh`: lee las tareas y
dependencias del plan. La prueba local se ejecuta sin cuentas ni publicación:

```bash
DRY_RUN=1 bash scripts/crear_issues.sh
```

Para publicar más adelante:

1. Integrar primero el plan, las fichas reorganizadas y el generador en `main`;
   los enlaces de los issues apuntan a esa rama.
2. Usar `GH_USER_A=rosseab-bit`, confirmar `GH_USER_B` y usar `GH_USER_C=Angelzam21`; instalar y autenticar
   `gh` si se elige ese método. Autenticar Git no autentica `gh`.
3. Revisar de nuevo todos los issues existentes. El script se detiene si encuentra
   alguno: en ese caso, completar manualmente los faltantes sin repetir el catálogo.
4. Revisar el dry-run y ejecutar la publicación una sola vez cuando se indique.
   La publicación crea labels, milestones por fase, issues, asignaciones y enlaces
   a las dependencias; no configura automáticamente un GitHub Project.
5. En un Project del repositorio, usar **Backlog**, **En progreso**, **En revisión**
   y **Hecho**, enlazar los issues y registrar bloqueos y reservas en su issue.

La creación del tablero y la publicación de issues quedan pendientes de cuentas
confirmadas y de la indicación de publicación. No se mantuvo otro catálogo de tareas.

## Verificación desde una copia nueva

El registro completo está en
[verificacion_infraestructura_T00.json](verificacion_infraestructura_T00.json).
Se clonó desde GitHub la rama documental en un directorio temporal, se creó otro
venv y se instalaron requirements con la instantánea local de versiones y el
paquete editable. La importación y configuración se comprobaron desde fuera del
checkout, sin `PYTHONPATH`, para verificar la instalación del paquete.

| Comprobación | Resultado |
|---|---|
| Clon desde GitHub | Commit `2d9ac70`, rama `docs/T-00-guia-angel`. |
| Requirements, paquete editable y `pip check` | Código 0 en cada comando. |
| Importación fuera del checkout | Paquete de la copia nueva, semilla `42`, SQL accesible y XGBoost 3.4.1. |
| `python -m pytest -q` | Código 0: **29 passed, 3 subtests passed in 2.79s**. |
| `python -m ruff check src tests` | Código 1: `RUF046` en transform y `F401` en validate, previamente registrados. |
| Bash y generador | Bash 3.2; sintaxis válida; 50 tareas en dry-run, código 0. |

La prueba utiliza el Python de usuario y su OpenMP ya instalado, descritos en
[ENTORNO_T00.md](ENTORNO_T00.md); no reproduce una Mac sin ese prerrequisito ni
sustituye las verificaciones de A/B. La copia y su venv se eliminaron al terminar.
No se generó una base de datos final ni se entrenaron modelos del proyecto.
