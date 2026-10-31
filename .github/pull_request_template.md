## Resumen

<!-- Explicar el problema, el cambio y el comportamiento resultante. -->

## Tarea, alcance y revisión

- ID de tarea:
- Closes #N <!-- Reemplazar N por el número real del issue. -->
- Spec o criterio de aceptación previo:
- Archivos/secciones acordados:
- Dependencias mergeadas en main (PR/commit) o bloqueo del borrador:
- Revisor: <!-- A revisa a Angel; Angel revisa a B; B revisa a A. Contratos: los otros dos. -->

## Validación

<!-- Indicar Python, entorno, comandos, resultado y evidencia. Registrar fallos y omisiones. -->

| Verificación | Resultado / evidencia |
|---|---|
| Tests: `python -m pytest -q` | |
| Lint: `python -m ruff check src tests` | |
| Documentación: enlaces, evidencia y coherencia | |
| CI, cuando esté configurada | |

## Definición de hecho

<!-- PLAN_SDD.md, sección 6. Mantener pendientes los criterios aún no cumplidos. -->

- [ ] Issue con ID de tarea enlazado mediante `Closes #N`.
- [ ] Spec o criterio escrito antes de implementar.
- [ ] Mínimo de tres commits propios con ID; cada uno aporta un cambio real.
- [ ] Verificaciones pertinentes aprobadas; código/CI: tests y lint local y CI; docs: enlaces, evidencia y coherencia.
- [ ] El autor puede explicar el código y sus limitaciones.
- [ ] Documentación y docstrings actualizados, según corresponda.
- [ ] Otro integrante aprobó el PR; al integrar, usar merge commit sin squash.
- [ ] Seguimiento actualizado en `docs/05_seguimiento/avance.md` al mergear.

## Checklist del revisor

<!-- GUIA_EQUIPO.md, sección 5. -->

- [ ] Cumple el issue, entregable y spec aplicable.
- [ ] Cambios acotados a los archivos acordados; commits claros con ID.
- [ ] Pruebas significativas y verificaciones aprobadas; para docs, evidencia, enlaces y coherencia revisados.
- [ ] Test no interviene en ajuste, CV, pesos ni decisiones de train; revisar también la construcción de la etiqueta.
- [ ] Features y configuración respetan las reglas acordadas, sin sectores absolutos ni variables prohibidas.
- [ ] Columnas, firmas, claves y probabilidades respetan los contratos; cambios aprobados previamente.
- [ ] Documentación actualizada; sin BD local, entorno ni credenciales en el cambio.
- [ ] El autor puede explicar la implementación y sus limitaciones.

## Pendientes y riesgos

<!-- Describir lo que impide cerrar la tarea y quién debe resolverlo. -->
