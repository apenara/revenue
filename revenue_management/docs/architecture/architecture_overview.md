# Arquitectura del Framework de Revenue Management

## Visión General

El Framework de Revenue Management del Hotel Playa Club es una aplicación diseñada para optimizar la gestión de ingresos del hotel mediante el análisis de datos históricos, la generación de pronósticos y la aplicación de reglas de pricing para recomendar tarifas óptimas.

La arquitectura del sistema sigue un enfoque de tres capas:

1. **Capa de Presentación**: Interfaz de usuario implementada con Streamlit
2. **Capa de Lógica de Negocio**: Módulos de análisis, forecasting y pricing
3. **Capa de Datos**: Módulos de ingesta, procesamiento y persistencia

## Diagrama de Arquitectura

```
+------------------+        +------------------+        +--------------------+
|                  |        |                  |        |                    |
|  Ingesta de      |------->|  Base de Datos   |<-------|  Análisis con      |
|  Datos (Excel)   |        |  (SQLite)        |        |  Polars (KPIs, Pat)|
|                  |        |                  |        |                    |
+------------------+        +------------------+        +--------------------+
                                    ^                             |
                                    |                             v
+------------------+        +----------------------+      +------------------+
|                  |        |                      |      |                  |
|  Interfaz de     |<-------|  Lógica de Reglas    |<-----|  Modelo de       |
|  Usuario (MVP)   |        |  (Python + Polars)   |      |  Previsión (MVP) |
|  (Streamlit)     |        |                      |      |                  |
+------------------+        +----------------------+      +------------------+
        |
        v
+------------------+
|                  |
|  Exportación     |
|  de Tarifas      |
|  (Excel p/ Zeus) |
|                  |
+------------------+
```

## Componentes Principales

### 1. Capa de Presentación

#### 1.1 Interfaz de Usuario (Streamlit)

La interfaz de usuario está implementada utilizando Streamlit, un framework de Python para crear aplicaciones web interactivas. La interfaz proporciona las siguientes funcionalidades:

- Dashboard con KPIs y visualizaciones
- Formularios para la ingesta de datos
- Visualización de pronósticos
- Configuración de reglas de pricing
- Revisión y aprobación de recomendaciones de tarifas
- Exportación de tarifas aprobadas

#### 1.2 Componentes de UI

Los componentes de UI están organizados en módulos reutilizables:

- **KPI Cards**: Tarjetas para mostrar indicadores clave de rendimiento
- **Data Tables**: Tablas para mostrar y editar datos
- **Charts**: Gráficos para visualizar datos y tendencias
- **Date Selectors**: Selectores de fechas para filtrar datos
- **File Uploaders**: Componentes para cargar archivos

### 2. Capa de Lógica de Negocio

#### 2.1 Módulo de Análisis

El módulo de análisis procesa los datos históricos para calcular KPIs y detectar patrones. Utiliza Polars para el procesamiento eficiente de datos y proporciona las siguientes funcionalidades:

- Cálculo de KPIs (RevPAR, ADR, Ocupación)
- Análisis de patrones de ocupación
- Comparaciones año contra año
- Segmentación por tipo de habitación, temporada, día de la semana, etc.

#### 2.2 Módulo de Forecasting

El módulo de forecasting utiliza modelos estadísticos para generar pronósticos de ocupación y tarifa. Utiliza Prophet como motor de previsión y proporciona las siguientes funcionalidades:

- Preparación de datos para el modelo
- Generación de pronósticos de ocupación
- Ajuste de pronósticos
- Cálculo de KPIs previstos

#### 2.3 Módulo de Pricing

El módulo de pricing aplica reglas de negocio para generar recomendaciones de tarifas. Utiliza un motor de reglas basado en Python y Polars para aplicar las siguientes reglas:

- Reglas basadas en temporada
- Reglas basadas en ocupación prevista
- Reglas basadas en canal de distribución
- Reglas basadas en día de la semana

### 3. Capa de Datos

#### 3.1 Módulo de Ingesta

El módulo de ingesta importa datos desde archivos Excel y los procesa para su almacenamiento en la base de datos. Proporciona las siguientes funcionalidades:

- Lectura de archivos Excel
- Limpieza y normalización de datos
- Mapeo de datos a modelos
- Persistencia en la base de datos

#### 3.2 Base de Datos

La base de datos utiliza SQLite como motor de almacenamiento y proporciona las siguientes funcionalidades:

- Almacenamiento de datos históricos
- Almacenamiento de pronósticos
- Almacenamiento de recomendaciones de tarifas
- Almacenamiento de configuración de reglas

#### 3.3 Módulo de Exportación

El módulo de exportación genera archivos Excel con las tarifas aprobadas para su importación en el PMS Zeus. Proporciona las siguientes funcionalidades:

- Generación de archivos Excel
- Formateo de datos según los requisitos del PMS
- Registro de exportaciones

## Flujo de Datos

El flujo de datos en el sistema sigue los siguientes pasos:

1. **Ingesta de Datos**: Los datos históricos se importan desde archivos Excel y se almacenan en la base de datos.
2. **Análisis de Datos**: Los datos históricos se procesan para calcular KPIs y detectar patrones.
3. **Generación de Pronósticos**: Se generan pronósticos de ocupación y tarifa para fechas futuras.
4. **Aplicación de Reglas**: Se aplican reglas de pricing para generar recomendaciones de tarifas.
5. **Revisión y Aprobación**: Las recomendaciones de tarifas se revisan y aprueban por el usuario.
6. **Exportación**: Las tarifas aprobadas se exportan a un archivo Excel para su importación en el PMS Zeus.

## Patrones de Diseño

El sistema utiliza los siguientes patrones de diseño:

### 1. Patrón Repositorio

El patrón Repositorio se utiliza para abstraer el acceso a la base de datos. Cada entidad principal tiene su propio repositorio que encapsula las operaciones CRUD.

```python
class RoomTypeRepository:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def get_all(self):
        # Lógica para obtener todos los tipos de habitación
        pass
        
    def get_by_id(self, id):
        # Lógica para obtener un tipo de habitación por ID
        pass
        
    # Otros métodos CRUD
```

### 2. Patrón Servicio

El patrón Servicio se utiliza para encapsular la lógica de negocio compleja y coordinar entre múltiples repositorios.

```python
class PricingService:
    def __init__(self, rule_repository, forecast_repository, rate_repository):
        self.rule_repository = rule_repository
        self.forecast_repository = forecast_repository
        self.rate_repository = rate_repository
        
    def generate_recommendations(self, start_date, end_date, room_types, channels):
        # Lógica para generar recomendaciones
        pass
```

### 3. Patrón Estrategia

El patrón Estrategia se utiliza para el módulo de reglas de pricing, permitiendo diferentes algoritmos de pricing que puedan ser intercambiados.

```python
class PricingStrategy(ABC):
    @abstractmethod
    def apply(self, base_rate, forecast, parameters):
        pass
        
class OccupancyBasedPricingStrategy(PricingStrategy):
    def apply(self, base_rate, forecast, parameters):
        # Lógica para ajustar precio basado en ocupación
        pass
```

### 4. Patrón Fábrica

El patrón Fábrica se utiliza para la creación de objetos complejos, como los modelos de previsión.

```python
class ForecastModelFactory:
    @staticmethod
    def create_model(model_type, **kwargs):
        if model_type == 'prophet':
            return ProphetForecastModel(**kwargs)
        elif model_type == 'simple':
            return SimpleForecastModel(**kwargs)
        else:
            raise ValueError(f"Modelo de previsión no soportado: {model_type}")
```

## Estrategia de Modularidad

Para mantener la modularidad y evitar código repetitivo, se siguen las siguientes estrategias:

### 1. Principio DRY (Don't Repeat Yourself)

- Crear funciones y clases utilitarias para operaciones comunes
- Centralizar la lógica de acceso a datos en los repositorios
- Utilizar herencia y composición para compartir funcionalidad

### 2. Inyección de Dependencias

- Utilizar inyección de dependencias para desacoplar componentes
- Pasar dependencias a través de constructores o métodos
- Facilitar las pruebas unitarias mediante mocks

### 3. Interfaces Claras

- Definir interfaces claras entre módulos
- Utilizar clases abstractas o protocolos para definir contratos
- Documentar las interfaces y contratos

## Tecnologías Utilizadas

El sistema utiliza las siguientes tecnologías:

- **Python**: Lenguaje de programación principal
- **Polars**: Biblioteca para procesamiento eficiente de datos
- **Prophet**: Biblioteca para generación de pronósticos
- **Streamlit**: Framework para la interfaz de usuario
- **Plotly/Matplotlib**: Bibliotecas para visualización de datos
- **SQLite**: Motor de base de datos
- **Pandas**: Biblioteca para manipulación de datos
- **NumPy**: Biblioteca para cálculos numéricos
- **Pytest**: Framework para pruebas unitarias y de integración

## Consideraciones de Seguridad

El sistema implementa las siguientes medidas de seguridad:

- **Autenticación**: Sistema de autenticación básico para controlar el acceso
- **Autorización**: Sistema de roles para controlar el acceso a funcionalidades
- **Validación de Datos**: Validación de datos de entrada para prevenir inyecciones SQL
- **Copias de Seguridad**: Sistema de copias de seguridad automáticas de la base de datos

## Consideraciones de Rendimiento

El sistema implementa las siguientes optimizaciones de rendimiento:

- **Procesamiento Eficiente**: Uso de Polars para procesamiento eficiente de datos
- **Caché**: Caché de resultados de cálculos costosos
- **Paginación**: Paginación de resultados para reducir el consumo de memoria
- **Consultas Optimizadas**: Optimización de consultas SQL para mejorar el rendimiento

## Extensibilidad

El sistema está diseñado para ser extensible en las siguientes áreas:

- **Nuevos Tipos de Reglas**: Facilidad para añadir nuevos tipos de reglas de pricing
- **Nuevos Modelos de Previsión**: Facilidad para añadir nuevos modelos de previsión
- **Nuevas Fuentes de Datos**: Facilidad para añadir nuevas fuentes de datos
- **Nuevas Visualizaciones**: Facilidad para añadir nuevas visualizaciones
- **Nuevas Exportaciones**: Facilidad para añadir nuevos formatos de exportación

## Conclusión

La arquitectura del Framework de Revenue Management del Hotel Playa Club está diseñada para proporcionar una solución modular, extensible y mantenible para la gestión de ingresos del hotel. La separación en capas y el uso de patrones de diseño facilitan la evolución del sistema a medida que surgen nuevos requisitos.