# Guía de Demostración del Framework de Revenue Management - Hotel Playa Club

Esta guía proporciona instrucciones paso a paso para probar el Framework de Revenue Management del Hotel Playa Club (MVP). Siga estas instrucciones para configurar el entorno, inicializar la base de datos, cargar datos de ejemplo y probar las funcionalidades principales del framework.

## Requisitos Previos

Antes de comenzar, asegúrese de tener instalado:

- Python 3.9 o superior
- Pip (gestor de paquetes de Python)
- Git (opcional)

## 1. Configuración del Entorno

### 1.1. Clonar el Repositorio (opcional)

Si aún no tiene el código fuente, puede clonarlo desde el repositorio:

```bash
git clone https://github.com/hotelplayaclub/revenue-management.git
cd revenue-management
```

### 1.2. Crear y Activar un Entorno Virtual

Es recomendable utilizar un entorno virtual para aislar las dependencias del proyecto:

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 1.3. Instalar Dependencias

Instale todas las dependencias necesarias para el proyecto:

```bash
pip install -r revenue_management/requirements.txt
```

## 2. Inicialización y Carga de Datos

Existen dos formas de inicializar la base de datos y cargar datos de ejemplo:

### 2.1. Usando el Script de Demostración (Recomendado)

El script `demo.py` automatiza todo el proceso de inicialización y carga de datos, además de mostrar cómo utilizar las principales funcionalidades del framework:

```bash
python demo.py
```

Este script realizará las siguientes acciones:
- Inicializar la base de datos
- Generar y cargar datos de ejemplo realistas para un período de 1 año
- Demostrar el análisis de KPIs
- Generar pronósticos de demanda
- Aplicar reglas de pricing para generar recomendaciones de tarifas
- Exportar tarifas aprobadas

### 2.2. Inicialización Manual

Si prefiere realizar el proceso paso a paso:

1. **Inicializar la base de datos:**
   ```bash
   python revenue_management/initialize_db.py
   ```

2. **Cargar datos de ejemplo:**
   ```bash
   python revenue_management/scripts/load_sample_data.py --num-bookings 2000
   ```

## 3. Ejecutar la Aplicación Streamlit

Una vez inicializada la base de datos y cargados los datos de ejemplo, puede ejecutar la aplicación Streamlit para interactuar con el framework a través de la interfaz de usuario:

```bash
streamlit run revenue_management/app.py
```

La aplicación se abrirá automáticamente en su navegador web predeterminado. Si no se abre automáticamente, puede acceder a ella en la siguiente URL:

```
http://localhost:8501
```

### 3.1. Iniciar Sesión

Inicie sesión con las credenciales por defecto:
- **Usuario:** admin
- **Contraseña:** admin123

## 4. Probar las Funcionalidades Principales

### 4.1. Ingesta de Datos

1. En el menú lateral, seleccione "Ingesta de Datos"
2. Utilice la opción "Cargar Reservas" para importar datos de reservas
   - Puede utilizar los archivos generados en `data/raw/sample_bookings.xlsx`
3. Utilice la opción "Cargar Estancias" para importar datos de estancias
   - Puede utilizar los archivos generados en `data/raw/sample_stays.xlsx`
4. Verifique los mensajes de confirmación para asegurarse de que los datos se han cargado correctamente

### 4.2. Análisis de KPIs

1. En el menú lateral, seleccione "Dashboard"
2. Explore los KPIs principales:
   - Ocupación
   - ADR (Average Daily Rate)
   - RevPAR (Revenue Per Available Room)
3. Utilice los selectores de fecha para analizar diferentes períodos
4. Explore los gráficos de tendencias y comparaciones año contra año

### 4.3. Previsión de Demanda

1. En el menú lateral, seleccione "Forecasting"
2. Configure los parámetros de previsión:
   - Seleccione el rango de fechas para los datos históricos
   - Especifique el número de días a pronosticar (por defecto: 90)
   - Seleccione el tipo de habitación (opcional)
3. Haga clic en "Generar Pronósticos"
4. Explore los resultados de la previsión:
   - Gráfico de ocupación prevista
   - Gráfico de ADR previsto
   - Gráfico de RevPAR previsto
5. Utilice la opción "Ajustar Pronósticos" para realizar ajustes manuales si es necesario

### 4.4. Generación de Recomendaciones de Tarifas

1. En el menú lateral, seleccione "Pricing"
2. Configure los parámetros de pricing:
   - Seleccione el rango de fechas para las recomendaciones
   - Seleccione el tipo de habitación (opcional)
   - Ajuste los parámetros de las reglas de pricing si es necesario
3. Haga clic en "Generar Recomendaciones"
4. Explore las recomendaciones generadas:
   - Tabla de tarifas recomendadas por fecha, tipo de habitación y canal
   - Comparación con tarifas base
   - Factores aplicados según las reglas

### 4.5. Aprobación y Exportación de Tarifas

1. En el menú lateral, seleccione "Gestión de Tarifas"
2. Revise las recomendaciones pendientes de aprobación
3. Realice ajustes manuales si es necesario
4. Seleccione las recomendaciones a aprobar y haga clic en "Aprobar Seleccionadas"
5. Para exportar las tarifas aprobadas:
   - Seleccione el rango de fechas para la exportación
   - Seleccione el tipo de habitación (opcional)
   - Seleccione el canal (opcional)
   - Haga clic en "Exportar Tarifas"
6. Descargue el archivo Excel generado con las tarifas aprobadas

## 5. Explorar Configuraciones Adicionales

1. En el menú lateral, seleccione "Configuración"
2. Explore y ajuste las configuraciones disponibles:
   - Parámetros de forecasting
   - Parámetros de pricing
   - Configuración de canales
   - Configuración de tipos de habitación
   - Configuración de temporadas

## 6. Cerrar la Aplicación

Para detener la aplicación Streamlit, presione `Ctrl+C` en la terminal donde se está ejecutando.

## Notas Adicionales

- Los datos de ejemplo generados son sintéticos pero realistas, basados en los patrones de ocupación y tarifas típicos del Hotel Playa Club.
- Las reglas de pricing implementadas son básicas y pueden ser ajustadas según las necesidades específicas del hotel.
- Para un uso en producción, se recomienda utilizar datos reales exportados del PMS Zeus.
- La base de datos se almacena localmente en `revenue_management/db/revenue_management.db`.
- Se realizan copias de seguridad automáticas de la base de datos en `revenue_management/db/backups/`.

## Solución de Problemas

Si encuentra algún problema durante la demostración:

1. Verifique los logs en `revenue_management/logs/revenue_management.log`
2. Asegúrese de que todas las dependencias están instaladas correctamente
3. Intente reiniciar la aplicación Streamlit
4. Si es necesario, reinicie el proceso desde el principio ejecutando:
   ```bash
   python revenue_management/initialize_db.py --force
   python demo.py
   ```

Para obtener ayuda adicional, consulte la documentación completa en `revenue_management/docs/` o contacte al equipo de soporte.