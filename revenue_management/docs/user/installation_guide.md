# Manual de Instalación y Configuración

## Requisitos Previos

Antes de instalar el Framework de Revenue Management, asegúrese de tener instalados los siguientes requisitos:

- **Python 3.9 o superior**: El framework está desarrollado en Python y requiere una versión 3.9 o superior.
- **Pip**: Gestor de paquetes de Python para instalar las dependencias.
- **Git** (opcional): Para clonar el repositorio si se utiliza control de versiones.
- **Acceso a los datos históricos del hotel**: Archivos Excel con datos de reservas, estancias y resumen diario.

## Instalación

### 1. Clonar el Repositorio (opcional)

Si el código está en un repositorio Git, puede clonarlo con el siguiente comando:

```bash
git clone https://github.com/hotelplayaclub/revenue-management.git
cd revenue-management
```

### 2. Crear y Activar un Entorno Virtual

Es recomendable utilizar un entorno virtual para aislar las dependencias del proyecto.

#### En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### En macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

Una vez activado el entorno virtual, instale las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

### 4. Inicializar la Base de Datos

Ejecute el script de inicialización de la base de datos:

```bash
python initialize_db.py
```

Este script creará la base de datos SQLite y las tablas necesarias, además de insertar datos iniciales como tipos de habitación, canales de distribución y reglas de pricing por defecto.

## Configuración

### 1. Archivo de Configuración

El archivo `config.yaml` contiene la configuración global del sistema. Puede modificarlo según sus necesidades:

```yaml
# Configuración del Framework de Revenue Management - Hotel Playa Club

# Configuración de la aplicación
app:
  name: "Revenue Management - Hotel Playa Club"
  version: "1.0.0"
  debug: true
  hotel_name: "Hotel Playa Club"
  hotel_location: "Cartagena, Colombia"
  total_rooms: 79

# Configuración de la base de datos
database:
  path: "db/revenue_management.db"
  backup_dir: "db/backups"
  backup_frequency: "daily"  # daily, weekly, monthly
  auto_backup: true
  backup_on_startup: true
  backup_on_shutdown: true

# Configuración de directorios
directories:
  data_raw: "data/raw"
  data_processed: "data/processed"
  data_exports: "data/exports"
  templates: "data/templates"

# Configuración de logging
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "logs/revenue_management.log"
  max_size_mb: 10
  backup_count: 5
  log_to_console: true

# Configuración de forecasting
forecasting:
  default_model: "prophet"
  forecast_days: 90
  seasonality_mode: "multiplicative"
  changepoint_prior_scale: 0.05
  seasonality_prior_scale: 10.0
  weekly_seasonality: true
  yearly_seasonality: true
  daily_seasonality: false

# Configuración de pricing
pricing:
  min_occupancy_threshold: 0.4
  max_occupancy_threshold: 0.8
  low_occupancy_factor: 0.9
  high_occupancy_factor: 1.15
  min_price_factor: 0.7
  max_price_factor: 1.3
  direct_channel_discount: 0.05  # 5% de descuento para canal directo

# Configuración de canales
channels:
  - name: "Directo"
    commission: 0.0
    priority: 1
    active: true
  - name: "Booking.com"
    commission: 0.15
    priority: 2
    active: true
  - name: "Expedia"
    commission: 0.18
    priority: 3
    active: true
  - name: "Hotelbeds"
    commission: 0.20
    priority: 4
    active: true
  - name: "Despegar"
    commission: 0.17
    priority: 5
    active: true

# Configuración de tipos de habitación
room_types:
  - code: "EST"
    name: "Estándar Triple"
    capacity: 3
    count: 14
  - code: "JRS"
    name: "Junior Suite"
    capacity: 5
    count: 4
  - code: "ESC"
    name: "Estándar Cuádruple"
    capacity: 4
    count: 26
  - code: "ESD"
    name: "Estándar Doble"
    capacity: 2
    count: 7
  - code: "SUI"
    name: "Suite"
    capacity: 2
    count: 1
  - code: "KSP"
    name: "King Superior"
    capacity: 2
    count: 12
  - code: "DSP"
    name: "Doble Superior"
    capacity: 2
    count: 15

# Configuración de temporadas
seasons:
  - name: "Baja"
    color: "#3498db"
    months: [4, 5, 6, 11]
    price_factor: 0.9
  - name: "Media"
    color: "#f39c12"
    months: [2, 3, 9, 10]
    price_factor: 1.0
  - name: "Alta"
    color: "#e74c3c"
    months: [1, 7, 8, 12]
    price_factor: 1.2

# Configuración de Excel
excel:
  bookings_sheet_names: ["Reservas", "Bookings", "Reservations"]
  stays_sheet_names: ["Estancias", "Stays", "Check-ins"]
  summary_sheet_names: ["Resumen", "Summary", "Forecast"]
  export_template: "templates/export_template.xlsx"
```

### 2. Configuración de Tipos de Habitación

Configure los tipos de habitación según la estructura de su hotel en la sección `room_types` del archivo `config.yaml`. Para cada tipo de habitación, especifique:

- `code`: Código del tipo de habitación (debe coincidir con el código utilizado en los archivos de datos).
- `name`: Nombre descriptivo del tipo de habitación.
- `capacity`: Capacidad máxima de personas.
- `count`: Número de habitaciones de este tipo.

### 3. Configuración de Canales de Distribución

Configure los canales de distribución en la sección `channels` del archivo `config.yaml`. Para cada canal, especifique:

- `name`: Nombre del canal (debe coincidir con el nombre utilizado en los archivos de datos).
- `commission`: Porcentaje de comisión del canal.
- `priority`: Prioridad del canal (para ordenar en la interfaz).
- `active`: Indica si el canal está activo.

### 4. Configuración de Temporadas

Configure las temporadas en la sección `seasons` del archivo `config.yaml`. Para cada temporada, especifique:

- `name`: Nombre de la temporada (Alta, Media, Baja).
- `color`: Color para visualización en la interfaz.
- `months`: Lista de meses que pertenecen a esta temporada.
- `price_factor`: Factor de ajuste de precio para esta temporada.

### 5. Configuración de Reglas de Pricing

Configure los parámetros de las reglas de pricing en la sección `pricing` del archivo `config.yaml`:

- `min_occupancy_threshold`: Umbral de ocupación mínima (0.0 - 1.0).
- `max_occupancy_threshold`: Umbral de ocupación máxima (0.0 - 1.0).
- `low_occupancy_factor`: Factor de ajuste para ocupación baja.
- `high_occupancy_factor`: Factor de ajuste para ocupación alta.
- `min_price_factor`: Factor mínimo de ajuste de precio.
- `max_price_factor`: Factor máximo de ajuste de precio.
- `direct_channel_discount`: Descuento para el canal directo.

### 6. Configuración de Forecasting

Configure los parámetros del modelo de previsión en la sección `forecasting` del archivo `config.yaml`:

- `default_model`: Modelo de previsión por defecto ("prophet").
- `forecast_days`: Número de días a pronosticar.
- `seasonality_mode`: Modo de estacionalidad ("multiplicative" o "additive").
- `changepoint_prior_scale`: Escala de prior para puntos de cambio.
- `seasonality_prior_scale`: Escala de prior para estacionalidad.
- `weekly_seasonality`: Habilitar estacionalidad semanal.
- `yearly_seasonality`: Habilitar estacionalidad anual.
- `daily_seasonality`: Habilitar estacionalidad diaria.

### 7. Configuración de Directorios

Configure las rutas de los directorios en la sección `directories` del archivo `config.yaml`:

- `data_raw`: Directorio para datos brutos importados.
- `data_processed`: Directorio para datos procesados.
- `data_exports`: Directorio para tarifas exportadas.
- `templates`: Directorio para plantillas.

### 8. Configuración de Logging

Configure los parámetros de logging en la sección `logging` del archivo `config.yaml`:

- `level`: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- `file`: Ruta al archivo de log.
- `max_size_mb`: Tamaño máximo del archivo de log en MB.
- `backup_count`: Número de copias de seguridad del archivo de log.
- `log_to_console`: Habilitar logging en consola.

## Ejecución

### 1. Iniciar la Aplicación

Para iniciar la aplicación, ejecute el siguiente comando:

```bash
streamlit run app.py
```

### 2. Acceder a la Aplicación

Abra un navegador web y acceda a la aplicación en la siguiente URL:

```
http://localhost:8501
```

### 3. Iniciar Sesión

Inicie sesión con las credenciales por defecto:

- **Usuario**: admin
- **Contraseña**: admin123

## Copias de Seguridad

### 1. Copias de Seguridad Automáticas

El sistema realiza copias de seguridad automáticas de la base de datos en los siguientes momentos:

- Al iniciar la aplicación (si `backup_on_startup` está habilitado).
- Al cerrar la aplicación (si `backup_on_shutdown` está habilitado).
- Según la frecuencia configurada en `backup_frequency` (diaria, semanal, mensual).

### 2. Copias de Seguridad Manuales

Para realizar una copia de seguridad manual, puede utilizar el siguiente script:

```python
from db.database import db

# Crear una copia de seguridad con un nombre personalizado
backup_path = db.create_backup("mi_copia_de_seguridad")
print(f"Copia de seguridad creada en: {backup_path}")
```

### 3. Restaurar Copias de Seguridad

Para restaurar una copia de seguridad, puede utilizar el siguiente script:

```python
from db.database import db

# Listar copias de seguridad disponibles
backups = db.list_backups()
for backup in backups:
    print(backup)

# Restaurar una copia de seguridad específica
success = db.restore_backup(backups[0])
if success:
    print("Copia de seguridad restaurada correctamente")
else:
    print("Error al restaurar la copia de seguridad")
```

## Solución de Problemas

### 1. Error al Iniciar la Aplicación

Si la aplicación no inicia correctamente, verifique lo siguiente:

- Asegúrese de que el entorno virtual está activado.
- Verifique que todas las dependencias están instaladas correctamente.
- Compruebe que el archivo `config.yaml` existe y tiene el formato correcto.
- Revise los logs en el directorio `logs` para obtener más información sobre el error.

### 2. Error al Importar Datos

Si hay problemas al importar datos, verifique lo siguiente:

- Asegúrese de que los archivos Excel tienen el formato correcto.
- Compruebe que los nombres de las hojas coinciden con los configurados en `excel.bookings_sheet_names`, `excel.stays_sheet_names` y `excel.summary_sheet_names`.
- Verifique que los códigos de habitación en los archivos coinciden con los configurados en `room_types`.
- Revise los logs para obtener más información sobre el error.

### 3. Error al Generar Pronósticos

Si hay problemas al generar pronósticos, verifique lo siguiente:

- Asegúrese de que hay suficientes datos históricos para entrenar el modelo.
- Compruebe que los parámetros de forecasting en `config.yaml` son adecuados.
- Revise los logs para obtener más información sobre el error.

### 4. Error al Exportar Tarifas

Si hay problemas al exportar tarifas, verifique lo siguiente:

- Asegúrese de que hay tarifas aprobadas para exportar.
- Compruebe que el directorio `data_exports` existe y tiene permisos de escritura.
- Verifique que la plantilla de exportación existe en el directorio `templates`.
- Revise los logs para obtener más información sobre el error.

## Contacto y Soporte

Para obtener ayuda adicional, contacte al equipo de soporte:

- **Email**: soporte@hotelplayaclub.com
- **Teléfono**: +57 123 456 7890
- **Horario de atención**: Lunes a Viernes, 9:00 AM - 6:00 PM (GMT-5)