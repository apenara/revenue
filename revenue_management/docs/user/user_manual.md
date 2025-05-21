# Manual de Usuario

## Introducción

Bienvenido al Manual de Usuario del Framework de Revenue Management del Hotel Playa Club. Este manual proporciona instrucciones detalladas sobre cómo utilizar todas las funcionalidades del sistema.

## Índice

1. [Inicio de Sesión](#1-inicio-de-sesión)
2. [Dashboard](#2-dashboard)
3. [Ingesta de Datos](#3-ingesta-de-datos)
4. [Análisis de KPIs](#4-análisis-de-kpis)
5. [Previsión](#5-previsión)
6. [Gestión de Tarifas](#6-gestión-de-tarifas)
7. [Exportación de Tarifas](#7-exportación-de-tarifas)
8. [Configuración](#8-configuración)

## 1. Inicio de Sesión

### 1.1 Acceder a la Aplicación

1. Abra un navegador web y acceda a la aplicación en la siguiente URL:
   ```
   http://localhost:8501
   ```

2. Se mostrará la pantalla de inicio de sesión.

### 1.2 Iniciar Sesión

1. Introduzca sus credenciales:
   - **Usuario**: Su nombre de usuario (por defecto: admin)
   - **Contraseña**: Su contraseña (por defecto: admin123)

2. Haga clic en el botón "Iniciar Sesión".

3. Si las credenciales son correctas, accederá al Dashboard. Si no, se mostrará un mensaje de error.

## 2. Dashboard

El Dashboard proporciona una visión general del rendimiento del hotel.

### 2.1 Navegación

En la barra lateral izquierda, encontrará las siguientes opciones:
- **Dashboard**: Visión general del rendimiento
- **Ingesta de Datos**: Importación de datos
- **Análisis de KPIs**: Análisis detallado de KPIs
- **Previsión**: Generación y visualización de pronósticos
- **Gestión de Tarifas**: Gestión de reglas y recomendaciones de tarifas
- **Exportación de Tarifas**: Exportación de tarifas aprobadas
- **Configuración**: Configuración del sistema

### 2.2 Selección de Fechas

1. En la parte superior del Dashboard, encontrará un selector de fechas.
2. Seleccione el rango de fechas para el que desea ver los datos.
3. Haga clic en "Aplicar" para actualizar los datos.

### 2.3 KPIs Principales

En la sección de KPIs Principales, se muestran los siguientes indicadores:
- **Ocupación**: Porcentaje de ocupación del hotel
- **ADR (Average Daily Rate)**: Tarifa media diaria
- **RevPAR (Revenue Per Available Room)**: Ingresos por habitación disponible
- **Ingresos Totales**: Ingresos totales del hotel

### 2.4 Gráficos de Tendencia

En la sección de Gráficos de Tendencia, se muestran los siguientes gráficos:
- **Tendencia de Ocupación**: Evolución de la ocupación en el tiempo
- **Tendencia de ADR**: Evolución del ADR en el tiempo
- **Tendencia de RevPAR**: Evolución del RevPAR en el tiempo
- **Tendencia de Ingresos**: Evolución de los ingresos en el tiempo

### 2.5 Análisis por Tipo de Habitación

En la sección de Análisis por Tipo de Habitación, se muestra una tabla con los siguientes datos para cada tipo de habitación:
- **Tipo de Habitación**: Nombre del tipo de habitación
- **Ocupación**: Porcentaje de ocupación
- **ADR**: Tarifa media diaria
- **RevPAR**: Ingresos por habitación disponible
- **Ingresos**: Ingresos totales

### 2.6 Análisis por Canal

En la sección de Análisis por Canal, se muestra una tabla con los siguientes datos para cada canal de distribución:
- **Canal**: Nombre del canal
- **Reservas**: Número de reservas
- **Noches**: Número de noches
- **ADR**: Tarifa media diaria
- **Ingresos**: Ingresos totales
- **Comisión**: Comisión total
- **Ingresos Netos**: Ingresos netos (después de comisiones)

## 3. Ingesta de Datos

La sección de Ingesta de Datos permite importar datos desde archivos Excel.

### 3.1 Importar Reservas

1. Seleccione la pestaña "Reservas".
2. Haga clic en "Seleccionar Archivo" y seleccione el archivo Excel con los datos de reservas.
3. Haga clic en "Importar".
4. Se mostrará una vista previa de los datos.
5. Verifique que los datos son correctos y haga clic en "Confirmar Importación".
6. Se mostrará un mensaje de éxito o error.

### 3.2 Importar Estancias

1. Seleccione la pestaña "Estancias".
2. Haga clic en "Seleccionar Archivo" y seleccione el archivo Excel con los datos de estancias.
3. Haga clic en "Importar".
4. Se mostrará una vista previa de los datos.
5. Verifique que los datos son correctos y haga clic en "Confirmar Importación".
6. Se mostrará un mensaje de éxito o error.

### 3.3 Importar Resumen Diario

1. Seleccione la pestaña "Resumen Diario".
2. Haga clic en "Seleccionar Archivo" y seleccione el archivo Excel con los datos de resumen diario.
3. Haga clic en "Importar".
4. Se mostrará una vista previa de los datos.
5. Verifique que los datos son correctos y haga clic en "Confirmar Importación".
6. Se mostrará un mensaje de éxito o error.

### 3.4 Ver Datos Importados

1. Seleccione la pestaña "Datos Importados".
2. Seleccione el tipo de datos que desea ver (Reservas, Estancias, Resumen Diario).
3. Se mostrará una tabla con los datos importados.
4. Puede filtrar los datos por fecha, tipo de habitación, canal, etc.
5. Puede exportar los datos a Excel haciendo clic en "Exportar a Excel".

## 4. Análisis de KPIs

La sección de Análisis de KPIs permite analizar en detalle los KPIs del hotel.

### 4.1 Selección de Fechas y Filtros

1. En la parte superior, seleccione el rango de fechas para el análisis.
2. Puede filtrar por tipo de habitación, canal, etc.
3. Haga clic en "Aplicar" para actualizar los datos.

### 4.2 KPIs Generales

En la sección de KPIs Generales, se muestran los siguientes indicadores:
- **Ocupación**: Porcentaje de ocupación del hotel
- **ADR**: Tarifa media diaria
- **RevPAR**: Ingresos por habitación disponible
- **Ingresos Totales**: Ingresos totales del hotel
- **Habitaciones Disponibles**: Número total de habitaciones disponibles
- **Habitaciones Ocupadas**: Número total de habitaciones ocupadas
- **Noches**: Número total de noches
- **Reservas**: Número total de reservas

### 4.3 Análisis por Día de la Semana

En la sección de Análisis por Día de la Semana, se muestra un gráfico con los siguientes datos para cada día de la semana:
- **Ocupación**: Porcentaje de ocupación
- **ADR**: Tarifa media diaria
- **RevPAR**: Ingresos por habitación disponible

### 4.4 Análisis por Mes

En la sección de Análisis por Mes, se muestra un gráfico con los siguientes datos para cada mes:
- **Ocupación**: Porcentaje de ocupación
- **ADR**: Tarifa media diaria
- **RevPAR**: Ingresos por habitación disponible

### 4.5 Análisis por Tipo de Habitación

En la sección de Análisis por Tipo de Habitación, se muestra una tabla y un gráfico con los siguientes datos para cada tipo de habitación:
- **Ocupación**: Porcentaje de ocupación
- **ADR**: Tarifa media diaria
- **RevPAR**: Ingresos por habitación disponible
- **Ingresos**: Ingresos totales
- **Habitaciones Disponibles**: Número de habitaciones disponibles
- **Habitaciones Ocupadas**: Número de habitaciones ocupadas

### 4.6 Análisis por Canal

En la sección de Análisis por Canal, se muestra una tabla y un gráfico con los siguientes datos para cada canal:
- **Reservas**: Número de reservas
- **Noches**: Número de noches
- **ADR**: Tarifa media diaria
- **Ingresos**: Ingresos totales
- **Comisión**: Comisión total
- **Ingresos Netos**: Ingresos netos (después de comisiones)

### 4.7 Comparación Año contra Año

En la sección de Comparación Año contra Año, se muestra un gráfico con la comparación de los siguientes indicadores con el año anterior:
- **Ocupación**: Porcentaje de ocupación
- **ADR**: Tarifa media diaria
- **RevPAR**: Ingresos por habitación disponible
- **Ingresos**: Ingresos totales

### 4.8 Exportar Análisis

1. Haga clic en "Exportar Análisis" en la parte inferior de la página.
2. Seleccione el formato de exportación (Excel, PDF, CSV).
3. Haga clic en "Exportar".
4. Se descargará el archivo con el análisis.

## 5. Previsión

La sección de Previsión permite generar y visualizar pronósticos de ocupación y tarifa.

### 5.1 Generar Pronósticos

1. Seleccione la pestaña "Generar Pronósticos".
2. Seleccione el rango de fechas para los datos históricos.
3. Seleccione el número de días a pronosticar.
4. Seleccione los tipos de habitación para los que desea generar pronósticos.
5. Haga clic en "Generar Pronósticos".
6. Se mostrará un mensaje de éxito o error.

### 5.2 Ver Pronósticos

1. Seleccione la pestaña "Ver Pronósticos".
2. Seleccione el rango de fechas para los pronósticos.
3. Seleccione los tipos de habitación que desea ver.
4. Se mostrará un gráfico con los pronósticos de ocupación.
5. Se mostrará una tabla con los pronósticos detallados.

### 5.3 Ajustar Pronósticos

1. Seleccione la pestaña "Ajustar Pronósticos".
2. Seleccione el rango de fechas para los pronósticos.
3. Seleccione los tipos de habitación que desea ajustar.
4. Se mostrará una tabla editable con los pronósticos.
5. Modifique los valores de ocupación prevista según sea necesario.
6. Haga clic en "Guardar Ajustes".
7. Se mostrará un mensaje de éxito o error.

### 5.4 Comparar Pronósticos con Datos Reales

1. Seleccione la pestaña "Comparar Pronósticos".
2. Seleccione el rango de fechas para la comparación.
3. Seleccione los tipos de habitación que desea comparar.
4. Se mostrará un gráfico con la comparación entre pronósticos y datos reales.
5. Se mostrará una tabla con la comparación detallada.
6. Se mostrarán métricas de precisión del pronóstico (MAPE, MAE, RMSE).

## 6. Gestión de Tarifas

La sección de Gestión de Tarifas permite configurar reglas de pricing y gestionar recomendaciones de tarifas.

### 6.1 Configurar Reglas de Pricing

1. Seleccione la pestaña "Reglas de Pricing".
2. Se mostrarán las reglas existentes.
3. Para editar una regla, haga clic en el botón "Editar" junto a la regla.
4. Para crear una nueva regla, haga clic en "Nueva Regla".
5. Complete el formulario con los detalles de la regla:
   - **Nombre**: Nombre de la regla
   - **Descripción**: Descripción de la regla
   - **Tipo**: Tipo de regla (Temporada, Ocupación, Canal, Día de la Semana)
   - **Parámetros**: Parámetros específicos según el tipo de regla
   - **Prioridad**: Prioridad de aplicación de la regla
   - **Activa**: Indica si la regla está activa
6. Haga clic en "Guardar Regla".
7. Se mostrará un mensaje de éxito o error.

### 6.2 Generar Recomendaciones de Tarifas

1. Seleccione la pestaña "Generar Recomendaciones".
2. Seleccione el rango de fechas para las recomendaciones.
3. Seleccione los tipos de habitación para los que desea generar recomendaciones.
4. Seleccione los canales para los que desea generar recomendaciones.
5. Haga clic en "Generar Recomendaciones".
6. Se mostrará un mensaje de éxito o error.

### 6.3 Revisar y Aprobar Recomendaciones

1. Seleccione la pestaña "Revisar Recomendaciones".
2. Seleccione el rango de fechas para las recomendaciones.
3. Seleccione los tipos de habitación que desea revisar.
4. Seleccione los canales que desea revisar.
5. Se mostrará una tabla con las recomendaciones de tarifas.
6. Puede filtrar las recomendaciones por fecha, tipo de habitación, canal, etc.
7. Para editar una tarifa recomendada, haga clic en el campo correspondiente y modifique el valor.
8. Para aprobar una recomendación, seleccione la casilla de verificación junto a la recomendación.
9. Para aprobar todas las recomendaciones, haga clic en "Aprobar Todas".
10. Haga clic en "Guardar Aprobaciones".
11. Se mostrará un mensaje de éxito o error.

### 6.4 Ver Historial de Tarifas

1. Seleccione la pestaña "Historial de Tarifas".
2. Seleccione el rango de fechas para el historial.
3. Seleccione los tipos de habitación que desea ver.
4. Seleccione los canales que desea ver.
5. Se mostrará una tabla con el historial de tarifas.
6. Puede filtrar el historial por fecha, tipo de habitación, canal, etc.
7. Puede exportar el historial a Excel haciendo clic en "Exportar a Excel".

## 7. Exportación de Tarifas

La sección de Exportación de Tarifas permite exportar las tarifas aprobadas a un archivo Excel para su importación en el PMS Zeus.

### 7.1 Exportar Tarifas

1. Seleccione el rango de fechas para la exportación.
2. Seleccione los tipos de habitación que desea exportar.
3. Seleccione los canales que desea exportar.
4. Haga clic en "Exportar Tarifas".
5. Se generará un archivo Excel con las tarifas.
6. Se mostrará un mensaje con la ruta al archivo generado.
7. Haga clic en "Descargar" para descargar el archivo.

### 7.2 Ver Historial de Exportaciones

1. Seleccione la pestaña "Historial de Exportaciones".
2. Se mostrará una tabla con el historial de exportaciones.
3. Para cada exportación, se mostrará:
   - **Fecha**: Fecha de la exportación
   - **Rango de Fechas**: Rango de fechas de las tarifas exportadas
   - **Tipos de Habitación**: Tipos de habitación exportados
   - **Canales**: Canales exportados
   - **Archivo**: Nombre del archivo generado
   - **Usuario**: Usuario que realizó la exportación
4. Para descargar un archivo exportado, haga clic en el enlace del archivo.

## 8. Configuración

La sección de Configuración permite configurar diversos aspectos del sistema.

### 8.1 Configuración General

1. Seleccione la pestaña "General".
2. Modifique los siguientes parámetros según sea necesario:
   - **Nombre del Hotel**: Nombre del hotel
   - **Ubicación**: Ubicación del hotel
   - **Número Total de Habitaciones**: Número total de habitaciones del hotel
   - **Modo Debug**: Habilitar/deshabilitar el modo debug
3. Haga clic en "Guardar Configuración".
4. Se mostrará un mensaje de éxito o error.

### 8.2 Configuración de Tipos de Habitación

1. Seleccione la pestaña "Tipos de Habitación".
2. Se mostrarán los tipos de habitación existentes.
3. Para editar un tipo de habitación, haga clic en el botón "Editar" junto al tipo.
4. Para crear un nuevo tipo de habitación, haga clic en "Nuevo Tipo de Habitación".
5. Complete el formulario con los detalles del tipo de habitación:
   - **Código**: Código del tipo de habitación
   - **Nombre**: Nombre del tipo de habitación
   - **Capacidad**: Capacidad máxima de personas
   - **Descripción**: Descripción del tipo de habitación
   - **Comodidades**: Comodidades disponibles
   - **Número de Habitaciones**: Número de habitaciones de este tipo
6. Haga clic en "Guardar Tipo de Habitación".
7. Se mostrará un mensaje de éxito o error.

### 8.3 Configuración de Canales

1. Seleccione la pestaña "Canales".
2. Se mostrarán los canales existentes.
3. Para editar un canal, haga clic en el botón "Editar" junto al canal.
4. Para crear un nuevo canal, haga clic en "Nuevo Canal".
5. Complete el formulario con los detalles del canal:
   - **Nombre**: Nombre del canal
   - **Comisión**: Porcentaje de comisión
   - **Prioridad**: Prioridad del canal
   - **Activo**: Indica si el canal está activo
6. Haga clic en "Guardar Canal".
7. Se mostrará un mensaje de éxito o error.

### 8.4 Configuración de Temporadas

1. Seleccione la pestaña "Temporadas".
2. Se mostrarán las temporadas existentes.
3. Para editar una temporada, haga clic en el botón "Editar" junto a la temporada.
4. Para crear una nueva temporada, haga clic en "Nueva Temporada".
5. Complete el formulario con los detalles de la temporada:
   - **Nombre**: Nombre de la temporada
   - **Color**: Color para visualización
   - **Meses**: Meses que pertenecen a esta temporada
   - **Factor de Precio**: Factor de ajuste de precio
6. Haga clic en "Guardar Temporada".
7. Se mostrará un mensaje de éxito o error.

### 8.5 Configuración de Usuarios

1. Seleccione la pestaña "Usuarios".
2. Se mostrarán los usuarios existentes.
3. Para editar un usuario, haga clic en el botón "Editar" junto al usuario.
4. Para crear un nuevo usuario, haga clic en "Nuevo Usuario".
5. Complete el formulario con los detalles del usuario:
   - **Nombre de Usuario**: Nombre de usuario para iniciar sesión
   - **Nombre Completo**: Nombre completo del usuario
   - **Email**: Email del usuario
   - **Rol**: Rol del usuario (Administrador, Usuario)
   - **Contraseña**: Contraseña para iniciar sesión
   - **Confirmar Contraseña**: Confirmación de la contraseña
6. Haga clic en "Guardar Usuario".
7. Se mostrará un mensaje de éxito o error.

### 8.6 Copias de Seguridad

1. Seleccione la pestaña "Copias de Seguridad".
2. Se mostrarán las copias de seguridad existentes.
3. Para crear una nueva copia de seguridad, haga clic en "Nueva Copia de Seguridad".
4. Introduzca un nombre para la copia de seguridad y haga clic en "Crear".
5. Se mostrará un mensaje de éxito o error.
6. Para restaurar una copia de seguridad, haga clic en el botón "Restaurar" junto a la copia.
7. Confirme la restauración haciendo clic en "Confirmar".
8. Se mostrará un mensaje de éxito o error.

### 8.7 Configuración de Logging

1. Seleccione la pestaña "Logging".
2. Modifique los siguientes parámetros según sea necesario:
   - **Nivel de Logging**: Nivel de detalle de los logs
   - **Archivo de Log**: Ruta al archivo de log
   - **Tamaño Máximo**: Tamaño máximo del archivo de log
   - **Número de Copias**: Número de copias de seguridad del archivo de log
   - **Log en Consola**: Habilitar/deshabilitar logging en consola
3. Haga clic en "Guardar Configuración".
4. Se mostrará un mensaje de éxito o error.

## Conclusión

Este manual proporciona instrucciones detalladas sobre cómo utilizar todas las funcionalidades del Framework de Revenue Management del Hotel Playa Club. Si tiene alguna pregunta o problema, consulte la sección de Solución de Problemas en el Manual de Instalación y Configuración o contacte al equipo de soporte.