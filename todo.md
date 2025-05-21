Aquí tienes el `todo.md` consolidado, listo para su uso por el equipo de desarrollo.

--- START OF FILE todo.md ---

# Lista de Tareas de Implementación - Framework RM Hotel Playa Club (MVP)

Este documento lista las tareas de implementación para el Producto Mínimo Viable (MVP) del Framework de Revenue Management, basado en el PRD v1.2 (MVP Revisado) y el análisis de los archivos de datos proporcionados.

## Configuración y Entorno

*   [ ] Configurar el repositorio de código.
*   [ ] Definir la estructura inicial del proyecto (directorios para código, datos, configuración, logs, etc.).
*   [ ] Configurar el entorno virtual de Python.
*   [ ] Listar e instalar dependencias principales (`polars`, `streamlit`, `plotly`, `matplotlib`, `sqlite3`, `openpyxl`, `prophet`).
*   [ ] Configurar un sistema de gestión de configuración (ej: un archivo `.env` o `config.yaml` simple para rutas de datos, credenciales básicas, etc.).

## 1. Ingesta y Gestión de Datos (MVP)

*   [ ] **Definición de Esquema de Base de Datos SQLite:**
    *   [ ] Diseñar la tabla `HabitacionesConfig` (de `cod_hab`, `num_config`, `capacidad` de los tipos de habitación).
    *   [ ] Diseñar la tabla `ReservasBrutas` para almacenar datos de la **Imagen 1 (Bookings Detallados)**.
    *   [ ] Diseñar la tabla `EstanciasBrutas` para almacenar datos de la **Imagen 2 (Registro/Estancia)**.
    *   [ ] Diseñar la tabla `ResumenDiarioHistorico` para almacenar datos de la **Imagen 4 (Resumen Diario/Forecast)**.
    *   [ ] Diseñar tablas para datos procesados/limpios (ej: `OcupacionDiaria`, `IngresosDiarios`).
    *   [ ] Diseñar tablas para `Previsiones` y `Recomendaciones_Aprobadas`.
    *   [ ] Diseñar tabla `ParametrosReglas` para la configuración de las reglas.

*   [ ] **Implementación de Ingesta de Archivos Excel:**
    *   [ ] Desarrollar lógica para leer la hoja/archivo correspondiente a `ReservasBrutas` en un DataFrame de **Polars**.
    *   [ ] Desarrollar lógica para leer la hoja/archivo correspondiente a `EstanciasBrutas` en un DataFrame de **Polars**.
    *   [ ] Desarrollar lógica para leer la hoja/archivo correspondiente a `ResumenDiarioHistorico` en un DataFrame de **Polars**.
    *   [ ] (Opcional, para futuros TRevPAR) Desarrollar lógica para leer la hoja/archivo de `CargosServicios` (Imagen 3) en un DataFrame de **Polars**, aunque no se usará en el MVP principal de RevPAR.

*   [ ] **Preprocesamiento y Normalización de Datos (Crucial con Polars):**
    *   [ ] **Limpieza de Fechas:** Estandarizar formatos de fecha y hora, convertir a tipo `Date` (ej: `fecha_llegada`, `fecha_checkin`, `fecha`). Asegurarse de manejar el componente `00:00:00`.
    *   [ ] **Manejo de Nulos y Tipos de Datos:** Convertir columnas numéricas a tipos apropiados (`Float64`, `Int64`).
    *   [ ] **Estandarización de Categorías:** Normalizar nombres de `canal_distribucion`, `tipo_habitacion` (si es necesario).
    *   [ ] **Generación de Noches por Estancia/Reserva:** Para la tabla `ReservasBrutas`, generar una fila por cada noche de la estancia para análisis diario (desplegar la reserva). Esto es clave para calcular la ocupación y el revenue diario.
        *   Distribuir `tarifa_neta` por `días_reserva` para obtener una `tarifa_neta_por_noche`.
    *   [ ] **Conciliación de Ingresos:**
        *   Priorizar `valor_venta` de `EstanciasBrutas` para los ingresos si este representa el ingreso final de la habitación por estancia.
        *   Si no, usar `tarifa_neta` de `ReservasBrutas` (distribuida por noche).
        *   Definir claramente qué columna se usará como "ingreso por habitación" para RevPAR.
    *   [ ] **Unificación de Datos:** Diseñar y implementar la lógica de *join* entre `ReservasBrutas` y `EstanciasBrutas` en **Polars** para enriquecer los datos de reserva/estancia (ej: usar `registro_num`, nombre de cliente, fechas como heurística si no hay IDs directos). Si no, definir la prioridad de qué fuente de datos usar para cada métrica.
    *   [ ] **Consolidación Diaria:** A partir de los datos procesados de reservas/estancias, crear un DataFrame de **Polars** a nivel diario (`OcupacionDiaria`, `IngresosDiarios`) que contenga:
        *   `fecha`
        *   `habitaciones_disponibles` (de la tabla `HabitacionesConfig`)
        *   `habitaciones_ocupadas` (calculado de las reservas/estancias desplegadas)
        *   `ingresos_por_habitacion` (calculado de las reservas/estancias desplegadas)

*   [ ] Implementar la persistencia de los DataFrames limpios y consolidados (ej: `OcupacionDiaria`, `IngresosDiarios`) en la base de datos SQLite.
*   [ ] Implementar la interfaz de usuario (Streamlit) para subir archivos Excel y disparar el proceso de ingesta y preprocesamiento.

## 2. Análisis de Datos (MVP)

*   [ ] Implementar el cálculo de KPIs esenciales (RevPAR, ADR, Ocupación) usando **Polars** sobre el DataFrame `OcupacionDiaria` e `IngresosDiarios` (o su equivalente consolidado).
*   [ ] Implementar análisis de patrones básicos de ocupación (agrupaciones por tipo de habitación, temporada, día de la semana) usando **Polars** sobre los datos históricos procesados.
*   [ ] Implementar cálculo de comparaciones Año contra Año (YoY) para KPIs esenciales usando **Polars**.
*   [ ] Integrar los resultados de estos análisis en el dashboard de Streamlit.

## 3. Previsión de Demanda (MVP)

*   [ ] Implementar la preparación de datos de entrada para el modelo de previsión (ej: Prophet) a partir del DataFrame `ResumenDiarioHistorico` y/o `OcupacionDiaria` de **Polars**.
*   [ ] Seleccionar e integrar el modelo de previsión (Prophet o similar simple).
*   [ ] Implementar la lógica para generar previsiones de `ocupacion_prevista` futuras utilizando el modelo.
*   [ ] Implementar la segmentación de previsiones por tipo de habitación (si el modelo lo permite o si se entrena uno por tipo).
*   [ ] Implementar la visualización de las previsiones en la interfaz de usuario (Streamlit).
*   [ ] Implementar la funcionalidad en la UI para permitir ajustes manuales a las previsiones y guardar estos ajustes en la tabla `Previsiones`.

## 4. Lógica de Aplicación de Reglas para Pricing (MVP)

*   [ ] Diseñar la estructura del código Python que actuará como la "Lógica de Reglas", operando directamente sobre DataFrames de **Polars** que contendrán los datos históricos, previsiones (`ocupacion_prevista`), y tarifas base.
*   [ ] Definir una estructura de configuración simple (ej: tabla `ParametrosReglas` en SQLite, o un archivo `config.yaml` simple) para almacenar los parámetros de las reglas (umbrales de ocupación, factores de ajuste porcentuales/absolutos, tarifas base por temporada/tipo de habitación).
*   [ ] Implementar la lógica en Python (utilizando operaciones de **Polars** como `when().then().otherwise()`, `with_columns()`) para aplicar las reglas básicas:
    *   Cargar tarifas base para cada `fecha`, `tipo_habitacion`, `canal`.
    *   Aplicar ajustes basados en `ocupacion_prevista` (ej: aumento si alta, disminución si baja).
    *   Aplicar ajustes basados en `temporada`.
    *   Aplicar ajustes basados en `canal` (ej: diferencia tarifa directa vs. OTA).
    *   Establecer un orden claro de aplicación de reglas (prioridad) en el código.
*   [ ] Implementar la interfaz de usuario (Streamlit) para visualizar y modificar los parámetros configurables de estas reglas básicas (ej: slider para umbral de ocupación, input para factor de ajuste).

## 5. Recomendación de Tarifas (MVP)

*   [ ] Orquestar el flujo de procesamiento: Cargar datos procesados -> Obtener Previsión -> Cargar tarifas base -> Aplicar Lógica de Reglas (Python+Polars) para calcular la `tarifa_recomendada`.
*   [ ] La salida de este flujo debe ser un DataFrame de **Polars** con la `tarifa_recomendada` única para el período seleccionado, segmentada por `fecha`, `tipo_habitacion` y `canal`.
*   [ ] Implementar la visualización de este DataFrame de recomendación en una tabla clara en la interfaz de usuario (Streamlit).

## 6. Gestión de Tarifas (MVP)

*   [ ] Implementar la interfaz de usuario (Streamlit) que muestre la tabla de recomendaciones (Tarea 5.3) en un formato editable (permitir cambios manuales en `tarifa_recomendada`).
*   [ ] Implementar la lógica para capturar las modificaciones manuales hechas por el usuario en la UI.
*   [ ] Implementar el botón y la lógica para "Aprobar Tarifas".
*   [ ] Implementar la funcionalidad para exportar el DataFrame de tarifas aprobado (con ajustes manuales) a un archivo Excel. **MUY CRÍTICO: Necesitará que se confirme el formato exacto (columnas, orden, nombre de hoja) que Zeus PMS puede importar para tarifas.**
*   [ ] Implementar la lógica para guardar el DataFrame aprobado (o sus datos esenciales) en la tabla `Recomendaciones_Aprobadas` en la base de datos SQLite como registro básico.

## 7. Visualización y Reporting (MVP)

*   [ ] Diseñar y construir el dashboard principal en Streamlit.
*   [ ] Integrar las visualizaciones de KPIs esenciales y tendencias históricas (Tarea 2.4) usando Plotly/Matplotlib y datos de **Polars**.
*   [ ] Integrar la visualización de las previsiones (Tarea 3.3).
*   [ ] Integrar la visualización de la recomendación de tarifas (Tarea 5.3).

## Requisitos No Funcionales (MVP)

*   [ ] Implementar autenticación básica (ej: usuario/contraseña simple configurado localmente).
*   [ ] Implementar registro (logging) de acciones clave (importación, aprobación de tarifas, errores) a un archivo de log.
*   [ ] Asegurar el manejo básico de errores y excepciones en todo el flujo.
*   [ ] Implementar un script simple para copia de seguridad programada de la base de datos SQLite.
*   [ ] Realizar perfilado de rendimiento para identificar y optimizar cuellos de botella, especialmente en operaciones intensivas de **Polars**.
*   [ ] Asegurar que la interfaz de usuario es razonablemente intuitiva dentro del alcance del MVP y que la navegación es clara.
*   [ ] Añadir tooltips o ayuda contextual básica donde sea necesario en la UI para las funcionalidades del MVP.

## Pruebas

*   [ ] Escribir pruebas unitarias para las funciones clave de ingesta y preprocesamiento con **Polars**.
*   [ ] Escribir pruebas unitarias para la lógica de cálculo de KPIs.
*   [ ] Escribir pruebas unitarias para el modelo de previsión.
*   [ ] Escribir pruebas unitarias para la lógica de aplicación de reglas.
*   [ ] Escribir pruebas de integración para verificar el flujo completo (ingesta -> análisis -> previsión -> reglas -> recomendación -> exportación).
*   [ ] Realizar pruebas manuales exhaustivas del proceso de importación/exportación con archivos reales de Zeus.
*   [ ] Realizar pruebas de usabilidad básica por parte del usuario final clave (Revenue Manager) con prototipos o la versión temprana.

## Documentación

*   [ ] Documentar el proceso de instalación y configuración del sistema en la máquina local.
*   [ ] Documentar los **formatos de los archivos Excel esperados para la importación** y los mapeos de columnas.
*   [ ] Documentar el **formato de exportación de tarifas para Zeus PMS**.
*   [ ] Documentar el proceso de uso del sistema (importación, visualización, generación/aprobación/exportación de tarifas) - Manual de usuario básico.
*   [ ] Añadir comentarios al código, especialmente para la lógica compleja de preprocesamiento de datos con **Polars** y la lógica de reglas.
*   [ ] Documentar el esquema final de la base de datos SQLite.

## Entrega del MVP

*   [ ] Preparar el paquete de entrega para el Hotel Playa Club (ejecutable, scripts de instalación/configuración, código fuente, dependencias).
*   [ ] Realizar la instalación en el entorno de producción (PC local del hotel).
*   [ ] Realizar la capacitación del usuario principal (Revenue Manager) en el uso del MVP.
*   [ ] Establecer un canal de soporte inicial para el MVP.

---