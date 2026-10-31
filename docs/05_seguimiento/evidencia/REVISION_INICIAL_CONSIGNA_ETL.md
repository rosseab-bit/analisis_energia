# Revisión inicial de la consigna y el ETL

Registro histórico del **30 de octubre de 2026**, sobre el commit base `96fafa6`. No contiene el estado actual ni un segundo plan de trabajo: ambos se mantienen en [avance general](../avance.md) y el [plan SDD](../../02_planificacion/PLAN_SDD.md).

## Fuente y método

Se revisaron las tres páginas visibles de [Proyecto_Final.pdf](../../01_consigna/Proyecto_Final.pdf), su texto extraído, el CSV, código, esquema y tests locales. La página 1 visible identifica la opción B como Demanda y Consumo de Energía Eléctrica. La extracción recupera además opciones anteriores que no aparecen en la página renderizada; por eso se verificó visualmente la elección.

El proyecto coincide con la temática oficial. No se volvió a descargar el recurso público: procedencia exacta y unidades requieren confirmación con la fuente. Los datos observados se describen en el [diccionario](../../06_datos/data_dictionary.md); no se reproduce aquí su tabla.

La revisión inicial detectó requisitos de presentación y acceso a la BD que después se explicitaron en F-3/F-4. Su seguimiento vigente está en avance general; el informe histórico no acredita entregas al campus ni permisos en GitHub.

## Evidencia de ejecución

El detalle inalterado está en [evidencia_verificacion_etl.json](evidencia_verificacion_etl.json). Registra versiones del entorno, huella del CSV, conteos, pruebas de carga, CLI y la prueba temporal. Las bases y registros ficticios usados para verificar carga no son resultados de modelos ni una BD final de entrega.

Las comprobaciones se ejecutaron con Python 3.12.14, pandas 2.2.3, NumPy 2.3.5, pytest 9.2.0 y Ruff 0.17.3 en un entorno temporal. El archivo conserva las rutas de esa ejecución como evidencia histórica.

## Defecto temporal reproducido

La media móvil de `src/demanda/etl/transform.py` se calcula con `center=True` sobre la serie completa. Algunos scores de train incluyen demanda de test; tomar después los percentiles solo sobre train no elimina esa dependencia.

Prueba: multiplicar por 50 demanda y sectores únicamente en test, sin cambiar ninguna fila de train. Se modificaron cinco scores de train, de febrero a junio de 2021, y tres etiquetas.

| Umbral | Original | Después de modificar solo test |
|---|---|---|
| Alta | 1,0431186752 | 1,0428623651 |
| Crítica | 1,0766404302 | 1,0755915567 |

Esta perturbación es un diagnóstico de dependencia, no un experimento de entrenamiento. El test existente de umbrales verifica `percentil_global`, mientras que la configuración utiliza `relativo_tendencia`; por eso la suite inicial no detecta el defecto.

La corrección debe acordarse en la spec de datos y su implementación corresponde a ETL-3. Este informe no selecciona un método alternativo ni modifica código o configuración. El cierre del defecto y las nuevas verificaciones se registran en avance general.

## Interpretación que debe conservar la defensa

La consigna permite clasificación; no exige pronosticar meses futuros. El equipo debe definir cuándo están disponibles las variables y cómo construye la etiqueta. Usar temperatura y potencia del mismo mes requiere explicar que se trata de información contemporánea. Los criterios de independencia, comparación de población y evaluación se mantienen en la [spec de datos](../../07_especificaciones/01-datos.md), sin duplicarlos como decisiones ya aprobadas en este registro.
