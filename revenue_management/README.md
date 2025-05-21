# Framework de Revenue Management - Hotel Playa Club

## Descripción General

El Framework de Revenue Management del Hotel Playa Club es una aplicación diseñada para optimizar la gestión de ingresos del hotel mediante el análisis de datos históricos, la generación de pronósticos y la aplicación de reglas de pricing para recomendar tarifas óptimas.

Este sistema permite:

- **Importar datos** de reservas y estancias desde archivos Excel
- **Analizar KPIs** como ocupación, ADR (Average Daily Rate) y RevPAR (Revenue Per Available Room)
- **Generar pronósticos** de ocupación y tarifa para fechas futuras
- **Aplicar reglas de pricing** para generar recomendaciones de tarifas
- **Exportar tarifas** aprobadas para su importación en el PMS Zeus

## Estructura del Proyecto

```
revenue_management/
├── data/                  # Directorio para datos
│   ├── exports/           # Tarifas exportadas
│   ├── processed/         # Datos procesados
│   └── raw/               # Datos brutos importados
├── db/                    # Módulo de base de datos
│   ├── backups/           # Copias de seguridad
│   ├── database.py        # Clase para interactuar con la base de datos
│   └── schema.py          # Esquema de la base de datos
├── docs/                  # Documentación
│   ├── api/               # Documentación de la API interna
│   ├── architecture/      # Documentación de la arquitectura
│   ├── database/          # Documentación de la base de datos
│   └── user/              # Documentación de usuario
├── logs/                  # Logs del sistema
├── models/                # Modelos de datos
│   ├── base_model.py      # Clase base para todos los modelos
│   ├── booking.py         # Modelo para reservas
│   ├── daily_occupancy.py # Modelo para ocupación diaria
│   ├── daily_revenue.py   # Modelo para ingresos diarios
│   ├── forecast.py        # Modelo para pronósticos
│   ├── recommendation.py  # Modelo para recomendaciones
│   ├── room.py            # Modelo para habitaciones
│   ├── rule.py            # Modelo para reglas de pricing
│   └── stay.py            # Modelo para estancias
├── scripts/               # Scripts de utilidad
│   ├── backup_db.py       # Script para copias de seguridad
│   ├── initialize_db.py   # Script para inicializar la base de datos
│   └── load_sample_data.py # Script para cargar datos de ejemplo
├── services/              # Servicios de negocio
│   ├── analysis/          # Servicios de análisis
│   ├── data_ingestion/    # Servicios de ingesta de datos
│   ├── data_processing/   # Servicios de procesamiento de datos
│   ├── export/            # Servicios de exportación
│   ├── forecasting/       # Servicios de previsión
│   ├── pricing/           # Servicios de pricing
│   └── revenue_orchestrator.py # Orquestador de servicios
├── tests/                 # Pruebas
│   ├── integration/       # Pruebas de integración
│   └── unit/              # Pruebas unitarias
├── ui/                    # Interfaz de usuario
│   ├── components/        # Componentes reutilizables
│   ├── pages/             # Páginas de la aplicación
│   └── utils/             # Utilidades para la UI
├── utils/                 # Utilidades generales
│   └── logger.py          # Configuración de logging
├── app.py                 # Punto de entrada de la aplicación
├── config.py              # Módulo de configuración
├── config.yaml            # Archivo de configuración
├── initialize_db.py       # Script para inicializar la base de datos
├── requirements.txt       # Dependencias del proyecto
└── run_tests.py           # Script para ejecutar pruebas
```

## Instrucciones de Instalación

### Requisitos Previos

- Python 3.9 o superior
- Pip (gestor de paquetes de Python)
- Git (opcional)

### Instalación

1. Clonar el repositorio (opcional):
   ```bash
   git clone https://github.com/hotelplayaclub/revenue-management.git
   cd revenue-management
   ```

2. Crear y activar un entorno virtual:
   ```bash
   # En Windows
   python -m venv venv
   venv\Scripts\activate

   # En macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicializar la base de datos:
   ```bash
   python initialize_db.py
   ```

Para instrucciones detalladas, consulte el [Manual de Instalación y Configuración](docs/user/installation_guide.md).

## Guía Rápida de Uso

### Iniciar la Aplicación

```bash
streamlit run app.py
```

### Acceder a la Aplicación

Abra un navegador web y acceda a la aplicación en la siguiente URL:
```
http://localhost:8501
```

### Iniciar Sesión

Inicie sesión con las credenciales por defecto:
- **Usuario**: admin
- **Contraseña**: admin123

### Flujo de Trabajo Básico

1. **Importar Datos**:
   - Vaya a la sección "Ingesta de Datos"
   - Seleccione el archivo Excel con los datos de reservas o estancias
   - Haga clic en "Importar"

2. **Analizar KPIs**:
   - Vaya a la sección "Análisis de KPIs"
   - Seleccione el rango de fechas para el análisis
   - Explore los KPIs y gráficos

3. **Generar Pronósticos**:
   - Vaya a la sección "Previsión"
   - Seleccione el rango de fechas para los datos históricos
   - Seleccione el número de días a pronosticar
   - Haga clic en "Generar Pronósticos"

4. **Gestionar Tarifas**:
   - Vaya a la sección "Gestión de Tarifas"
   - Configure las reglas de pricing
   - Genere recomendaciones de tarifas
   - Revise y apruebe las recomendaciones

5. **Exportar Tarifas**:
   - Vaya a la sección "Exportación de Tarifas"
   - Seleccione el rango de fechas para la exportación
   - Haga clic en "Exportar Tarifas"

Para instrucciones detalladas, consulte el [Manual de Usuario](docs/user/user_manual.md).

## Cargar Datos de Ejemplo

Para cargar datos de ejemplo, puede utilizar el script `load_sample_data.py`:

```bash
python scripts/load_sample_data.py
```

Este script generará datos sintéticos de reservas y estancias para pruebas y demostraciones.

## Ejecutar Pruebas

Para ejecutar las pruebas, puede utilizar el script `run_tests.py`:

```bash
# Ejecutar todas las pruebas
python run_tests.py

# Ejecutar solo pruebas unitarias
python run_tests.py --type unit

# Ejecutar solo pruebas de integración
python run_tests.py --type integration

# Ejecutar pruebas con información detallada
python run_tests.py --verbose
```

## Documentación

La documentación completa del sistema está disponible en el directorio `docs/`:

- [Arquitectura del Sistema](docs/architecture/architecture_overview.md)
- [Esquema de la Base de Datos](docs/database/database_schema.md)
- [Referencia de la API Interna](docs/api/api_reference.md)
- [Flujo de Datos](docs/user/data_flow.md)
- [Manual de Instalación y Configuración](docs/user/installation_guide.md)
- [Manual de Usuario](docs/user/user_manual.md)
- [Guía de Solución de Problemas](docs/user/troubleshooting.md)

## Información de Contacto y Soporte

Para obtener ayuda o reportar problemas, contacte al equipo de soporte:

- **Email**: soporte@hotelplayaclub.com
- **Teléfono**: +57 123 456 7890
- **Horario de atención**: Lunes a Viernes, 9:00 AM - 6:00 PM (GMT-5)

## Licencia

Este software es propiedad del Hotel Playa Club y está protegido por derechos de autor. Su uso, modificación y distribución están restringidos y requieren autorización explícita.

© 2025 Hotel Playa Club. Todos los derechos reservados.