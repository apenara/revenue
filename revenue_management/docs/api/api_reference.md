# Referencia de la API Interna

## Visión General

Este documento proporciona una referencia detallada de las clases y funciones principales que componen la API interna del Framework de Revenue Management. La API está organizada en módulos que corresponden a las diferentes capas y componentes del sistema.

## Índice

1. [Modelos](#1-modelos)
2. [Servicios de Ingesta de Datos](#2-servicios-de-ingesta-de-datos)
3. [Servicios de Análisis](#3-servicios-de-análisis)
4. [Servicios de Previsión](#4-servicios-de-previsión)
5. [Servicios de Pricing](#5-servicios-de-pricing)
6. [Servicios de Exportación](#6-servicios-de-exportación)
7. [Componentes de UI](#7-componentes-de-ui)
8. [Utilidades](#8-utilidades)
9. [Base de Datos](#9-base-de-datos)
10. [Configuración](#10-configuración)

## 1. Modelos

Los modelos representan las entidades principales del sistema y proporcionan métodos para interactuar con la base de datos.

### 1.1 BaseModel

Clase base abstracta para todos los modelos.

```python
class BaseModel(ABC):
    """
    Clase base abstracta para todos los modelos de datos.
    Define la interfaz común que deben implementar todos los modelos.
    """
    
    @classmethod
    @abstractmethod
    def from_row(cls, row):
        """
        Crea una instancia del modelo a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            BaseModel: Instancia del modelo
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """
        Crea una instancia del modelo a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del modelo
            
        Returns:
            BaseModel: Instancia del modelo
        """
        pass
    
    @abstractmethod
    def to_dict(self):
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            dict: Diccionario con los datos del modelo
        """
        pass
    
    @abstractmethod
    def save(self):
        """
        Guarda el modelo en la base de datos.
        Si el modelo ya existe (tiene id), lo actualiza.
        Si no existe, lo crea.
        
        Returns:
            int: ID del modelo guardado
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_by_id(cls, id):
        """
        Obtiene un modelo por su ID.
        
        Args:
            id (int): ID del modelo a obtener
            
        Returns:
            BaseModel: Instancia del modelo o None si no existe
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_all(cls):
        """
        Obtiene todos los modelos.
        
        Returns:
            list: Lista de instancias del modelo
        """
        pass
    
    @classmethod
    @abstractmethod
    def delete(cls, id):
        """
        Elimina un modelo por su ID.
        
        Args:
            id (int): ID del modelo a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        pass
```

### 1.2 Room

Modelo para las habitaciones.

```python
class Room(BaseModel):
    """
    Modelo para las habitaciones (ROOM_TYPES)
    """
    
    def __init__(self, id=None, cod_hab=None, name=None, capacity=None, 
                 description=None, amenities=None, num_config=None):
        """
        Inicializa una instancia de Room.
        
        Args:
            id (int, optional): ID de la habitación
            cod_hab (str): Código de la habitación
            name (str): Nombre del tipo de habitación
            capacity (int): Capacidad de la habitación
            description (str, optional): Descripción de la habitación
            amenities (str, optional): Comodidades de la habitación
            num_config (int): Número de habitaciones de este tipo
        """
        self.id = id
        self.cod_hab = cod_hab
        self.name = name
        self.capacity = capacity
        self.description = description
        self.amenities = amenities
        self.num_config = num_config
    
    # Implementación de los métodos abstractos de BaseModel
    # ...
    
    @classmethod
    def get_by_cod_hab(cls, cod_hab):
        """
        Obtiene una habitación por su código.
        
        Args:
            cod_hab (str): Código de la habitación a obtener
            
        Returns:
            Room: Instancia de Room o None si no existe
        """
        # Implementación
        pass
    
    @classmethod
    def get_total_rooms(cls):
        """
        Obtiene el número total de habitaciones disponibles.
        
        Returns:
            int: Número total de habitaciones
        """
        # Implementación
        pass
### 1.3 DailyOccupancy

Modelo para la ocupación diaria.

```python
class DailyOccupancy(BaseModel):
    """
    Modelo para la ocupación diaria (DAILY_OCCUPANCY)
    """
    
    def __init__(self, id=None, fecha=None, room_type_id=None, 
                 habitaciones_disponibles=None, habitaciones_ocupadas=None, 
                 ocupacion_porcentaje=None, created_at=None):
        """
        Inicializa una instancia de DailyOccupancy.
        
        Args:
            id (int, optional): ID del registro
            fecha (str/datetime): Fecha
            room_type_id (int): ID del tipo de habitación
            habitaciones_disponibles (int): Número de habitaciones disponibles
            habitaciones_ocupadas (int): Número de habitaciones ocupadas
            ocupacion_porcentaje (float): Porcentaje de ocupación
            created_at (str/datetime, optional): Fecha de creación
        """
        self.id = id
        self.fecha = fecha
        self.room_type_id = room_type_id
        self.habitaciones_disponibles = habitaciones_disponibles
        self.habitaciones_ocupadas = habitaciones_ocupadas
        self.ocupacion_porcentaje = ocupacion_porcentaje
        self.created_at = created_at
    
    # Implementación de los métodos abstractos de BaseModel
    # ...
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date, room_type_id=None):
        """
        Obtiene registros de ocupación diaria por rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            list: Lista de instancias de DailyOccupancy
        """
        # Implementación
        pass
```

### 1.4 DailyRevenue

Modelo para los ingresos diarios.

```python
class DailyRevenue(BaseModel):
    """
    Modelo para los ingresos diarios (DAILY_REVENUE)
    """
    
    def __init__(self, id=None, fecha=None, room_type_id=None, 
                 ingresos=None, adr=None, revpar=None, created_at=None):
        """
        Inicializa una instancia de DailyRevenue.
        
        Args:
            id (int, optional): ID del registro
            fecha (str/datetime): Fecha
            room_type_id (int): ID del tipo de habitación
            ingresos (float): Ingresos totales
            adr (float): Average Daily Rate
            revpar (float): Revenue Per Available Room
            created_at (str/datetime, optional): Fecha de creación
        """
        self.id = id
        self.fecha = fecha
        self.room_type_id = room_type_id
        self.ingresos = ingresos
        self.adr = adr
        self.revpar = revpar
        self.created_at = created_at
    
    # Implementación de los métodos abstractos de BaseModel
    # ...
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date, room_type_id=None):
        """
        Obtiene registros de ingresos diarios por rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            list: Lista de instancias de DailyRevenue
        """
        # Implementación
        pass
```

### 1.5 Forecast

Modelo para las previsiones.

```python
class Forecast(BaseModel):
    """
    Modelo para las previsiones (FORECASTS)
    """
    
    def __init__(self, id=None, fecha=None, room_type_id=None, 
                 ocupacion_prevista=None, adr_previsto=None, revpar_previsto=None, 
                 created_at=None, ajustado_manualmente=False):
        """
        Inicializa una instancia de Forecast.
        
        Args:
            id (int, optional): ID del registro
            fecha (str/datetime): Fecha
            room_type_id (int): ID del tipo de habitación
            ocupacion_prevista (float): Ocupación prevista
            adr_previsto (float): ADR previsto
            revpar_previsto (float): RevPAR previsto
            created_at (str/datetime, optional): Fecha de creación
            ajustado_manualmente (bool, optional): Indica si fue ajustado manualmente
        """
        self.id = id
        self.fecha = fecha
        self.room_type_id = room_type_id
        self.ocupacion_prevista = ocupacion_prevista
        self.adr_previsto = adr_previsto
        self.revpar_previsto = revpar_previsto
        self.created_at = created_at
        self.ajustado_manualmente = ajustado_manualmente
    
    # Implementación de los métodos abstractos de BaseModel
    # ...
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date, room_type_id=None):
        """
        Obtiene previsiones por rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            list: Lista de instancias de Forecast
        """
        # Implementación
        pass
    
    @classmethod
    def get_by_date_and_room_type(cls, fecha, room_type_id):
        """
        Obtiene una previsión por fecha y tipo de habitación.
        
        Args:
            fecha (str/datetime): Fecha
            room_type_id (int): ID del tipo de habitación
            
        Returns:
            Forecast: Instancia de Forecast o None si no existe
        """
        # Implementación
        pass
```

## 2. Servicios de Ingesta de Datos

Los servicios de ingesta de datos se encargan de importar datos desde archivos Excel y procesarlos para su almacenamiento en la base de datos.

### 2.1 ExcelReader

Clase para leer archivos Excel.

```python
class ExcelReader:
    """
    Clase para leer archivos Excel
    """
    
    def read_excel_file(self, file_path, sheet_name=None, sheet_names=None):
        """
        Lee un archivo Excel y devuelve un DataFrame de pandas.
        
        Args:
            file_path (str/Path): Ruta al archivo Excel
            sheet_name (str, optional): Nombre de la hoja a leer
            sheet_names (list, optional): Lista de nombres de hojas a intentar leer
            
        Returns:
            pandas.DataFrame: DataFrame con los datos leídos
            
        Raises:
            ValueError: Si no se encuentra la hoja especificada
        """
        # Implementación
        pass
    
    def convert_to_polars(self, pandas_df):
        """
        Convierte un DataFrame de pandas a un DataFrame de polars.
        
        Args:
            pandas_df (pandas.DataFrame): DataFrame de pandas
            
        Returns:
            polars.DataFrame: DataFrame de polars
        """
        # Implementación
        pass
```

### 2.2 DataCleaner

Clase para limpiar y normalizar datos.

```python
class DataCleaner:
    """
    Clase para limpiar y normalizar datos
    """
    
    def clean_dates(self, df, date_column):
        """
        Limpia y normaliza fechas en un DataFrame de polars.
        
        Args:
            df (polars.DataFrame): DataFrame de polars
            date_column (str): Nombre de la columna de fecha
            
        Returns:
            polars.DataFrame: DataFrame con fechas limpias
        """
        # Implementación
        pass
    
    def clean_numeric_values(self, df, column, dtype="float"):
        """
        Limpia y normaliza valores numéricos en un DataFrame de polars.
        
        Args:
            df (polars.DataFrame): DataFrame de polars
            column (str): Nombre de la columna
            dtype (str, optional): Tipo de dato ("float" o "int")
            
        Returns:
            polars.DataFrame: DataFrame con valores numéricos limpios
        """
        # Implementación
        pass
    
    def remove_duplicates(self, df):
        """
        Elimina filas duplicadas en un DataFrame de polars.
        
        Args:
            df (polars.DataFrame): DataFrame de polars
            
        Returns:
            polars.DataFrame: DataFrame sin duplicados
        """
        # Implementación
        pass
```
### 2.3 DataMapper

Clase para mapear datos a modelos.

```python
class DataMapper:
    """
    Clase para mapear datos a modelos
    """
    
    def map_room_types(self, df, column, mapping):
        """
        Mapea códigos de habitación a nombres de tipos de habitación.
        
        Args:
            df (polars.DataFrame): DataFrame de polars
            column (str): Nombre de la columna con códigos de habitación
            mapping (dict): Diccionario de mapeo {código: nombre}
            
        Returns:
            polars.DataFrame: DataFrame con columna adicional de tipo de habitación
        """
        # Implementación
        pass
    
    def map_channels(self, df, column, mapping):
        """
        Mapea nombres de canales a tipos de canales.
        
        Args:
            df (polars.DataFrame): DataFrame de polars
            column (str): Nombre de la columna con nombres de canales
            mapping (dict): Diccionario de mapeo {nombre: tipo}
            
        Returns:
            polars.DataFrame: DataFrame con columna adicional de tipo de canal
        """
        # Implementación
        pass
```

### 2.4 DataIngestionService

Clase para coordinar el proceso de ingesta de datos.

```python
class DataIngestionService:
    """
    Clase para coordinar el proceso de ingesta de datos
    """
    
    def __init__(self):
        """
        Inicializa una instancia de DataIngestionService.
        """
        self.excel_reader = ExcelReader()
        self.data_cleaner = DataCleaner()
        self.data_mapper = DataMapper()
    
    def process_bookings(self, file_path):
        """
        Procesa un archivo Excel de reservas.
        
        Args:
            file_path (str/Path): Ruta al archivo Excel
            
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        # Implementación
        pass
    
    def process_stays(self, file_path):
        """
        Procesa un archivo Excel de estancias.
        
        Args:
            file_path (str/Path): Ruta al archivo Excel
            
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        # Implementación
        pass
    
    def calculate_daily_occupancy(self, bookings_df):
        """
        Calcula la ocupación diaria a partir de las reservas.
        
        Args:
            bookings_df (polars.DataFrame): DataFrame de reservas
            
        Returns:
            polars.DataFrame: DataFrame de ocupación diaria
        """
        # Implementación
        pass
    
    def expand_booking_to_nights(self, booking_df):
        """
        Expande las reservas a noches individuales.
        
        Args:
            booking_df (polars.DataFrame): DataFrame de reservas
            
        Returns:
            polars.DataFrame: DataFrame de noches
        """
        # Implementación
        pass
    
    def save_to_database(self, df, model_class):
        """
        Guarda un DataFrame en la base de datos.
        
        Args:
            df (polars.DataFrame): DataFrame a guardar
            model_class (class): Clase del modelo
            
        Returns:
            tuple: (éxito, filas_guardadas)
        """
        # Implementación
        pass
```

## 3. Servicios de Análisis

Los servicios de análisis se encargan de procesar los datos históricos para calcular KPIs y detectar patrones.

### 3.1 KpiCalculator

Clase para calcular KPIs.

```python
class KpiCalculator:
    """
    Clase para calcular KPIs
    """
    
    def calculate_kpis(self, start_date, end_date, room_type_id=None):
        """
        Calcula KPIs para un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            polars.DataFrame: DataFrame con KPIs calculados
        """
        # Implementación
        pass
    
    def calculate_aggregated_kpis(self, start_date, end_date, group_by="room_type_id"):
        """
        Calcula KPIs agregados para un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            group_by (str, optional): Campo por el que agrupar ("room_type_id", "fecha", "both")
            
        Returns:
            polars.DataFrame: DataFrame con KPIs agregados
        """
        # Implementación
        pass
    
    def analyze_occupancy_patterns(self, start_date, end_date, room_type_id=None):
        """
        Analiza patrones de ocupación para un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Diccionario con patrones de ocupación
        """
        # Implementación
        pass
    
    def calculate_yoy_comparison(self, start_date, end_date, room_type_id=None):
        """
        Calcula comparación año contra año para un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Diccionario con comparación año contra año
        """
        # Implementación
        pass
```

## 4. Servicios de Previsión

Los servicios de previsión se encargan de generar pronósticos de ocupación y tarifa para fechas futuras.

### 4.1 ForecastService

Clase para generar pronósticos.

```python
class ForecastService:
    """
    Clase para generar pronósticos
    """
    
    def __init__(self):
        """
        Inicializa una instancia de ForecastService.
        """
        self.forecast_config = config.get_forecasting_config()
        self.room_types = {room.id: room for room in Room.get_all()}
    
    def prepare_data(self, start_date, end_date, room_type_id=None):
        """
        Prepara los datos para el modelo de previsión.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Diccionario con DataFrames preparados por tipo de habitación
        """
        # Implementación
        pass
    
    def generate_forecast(self, start_date, end_date, forecast_days=None, room_type_id=None):
        """
        Genera pronósticos para un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio para datos históricos
            end_date (str/datetime): Fecha de fin para datos históricos
            forecast_days (int, optional): Número de días a pronosticar
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            dict: Diccionario con pronósticos por tipo de habitación
        """
        # Implementación
        pass
    
    def save_forecast_to_db(self, forecasts):
        """
        Guarda pronósticos en la base de datos.
        
        Args:
            forecasts (dict): Diccionario con pronósticos por tipo de habitación
            
        Returns:
            tuple: (éxito, mensaje, filas_guardadas)
        """
        # Implementación
        pass
    
    def load_forecast_from_db(self, start_date, end_date, room_type_id=None):
        """
        Carga pronósticos desde la base de datos.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            polars.DataFrame: DataFrame con pronósticos
        """
        # Implementación
        pass
    
    def update_forecast_kpis(self, start_date, end_date, room_type_id=None):
        """
        Actualiza KPIs de pronósticos.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            tuple: (éxito, mensaje, filas_actualizadas)
        """
        # Implementación
        pass
```