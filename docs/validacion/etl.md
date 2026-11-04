# Validación del ETL

Resultados históricos del **30 de octubre de 2026**, obtenidos sobre el commit `96fafa6`. El detalle de la ejecución está en [etl.json](etl.json); sus rutas temporales y registros ficticios corresponden a pruebas, no a resultados de modelos entrenados.

## Comprobaciones realizadas

La ejecución utilizó Python 3.12.14, pandas 2.2.3 y NumPy 2.3.5.

- Dataset de 308 filas y 30 columnas, sin fechas duplicadas ni meses faltantes.
- Carga de 308 filas en `datos_limpios` y 3.450 en `demanda_distribuidora`.
- Repetición de la carga sin duplicar datos y con una nueva fila de auditoría.
- Conservación de resultados de modelos durante una carga sin reset.
- Rollback ante un error durante la carga y limpieza de resultados con reset.
- CLI con salida 0 para el CSV válido y salida 1 ante fechas duplicadas, conservando la base previa.

## Dependencia temporal del etiquetado

La media móvil de `src/demanda/etl/transform.py` utiliza `center=True` sobre la serie completa. Algunos scores de train incluyen demanda de test. Calcular después los percentiles solo sobre train no elimina esa dependencia.

La prueba modificó únicamente demanda y sectores de test, multiplicándolos por 50, sin cambiar ninguna fila de train. Se modificaron cinco scores de train, de febrero a junio de 2021, y tres etiquetas.

| Umbral | Original | Después de modificar solo test |
|---|---|---|
| Alta | 1,0431186752 | 1,0428623651 |
| Crítica | 1,0766404302 | 1,0755915567 |

La perturbación diagnostica una dependencia entre particiones; no es un experimento de entrenamiento. El test existente de umbrales comprueba `percentil_global`, mientras que la configuración utiliza `relativo_tendencia`.

La solución metodológica sigue pendiente en la decisión D1 de la [especificación de datos](../especificaciones/datos-etl.md). Las etiquetas del método actual son provisionales.

## Otras limitaciones observadas

La CLI muestra un traceback si falta la columna de fecha. El informe histórico también registró observaciones de lint en validación y transformación. Estos resultados describen la versión auditada; deben verificarse nuevamente cuando cambien el código, la configuración o los datos.
