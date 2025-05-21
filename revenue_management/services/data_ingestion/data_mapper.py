#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para mapear las columnas de los archivos Excel a las tablas de la base de datos
"""

import polars as pl
from datetime import datetime
from db.database import db
from utils.logger import setup_logger
from services.data_ingestion.data_cleaner import DataCleaner

# Configurar logger
logger = setup_logger(__name__)

class DataMapper:
    """
    Clase para mapear las columnas de los archivos Excel a las tablas de la base de datos
    """
    
    # Mapeos de columnas para cada tipo de archivo
    BOOKINGS_MAPPING = {
        # Mapeo de columnas de Excel a columnas de la base de datos
        'Nº Registro': 'registro_num',
        'Fecha Reserva': 'fecha_reserva',
        'Fecha Llegada': 'fecha_llegada',
        'Fecha Salida': 'fecha_salida',
        'Noches': 'noches',
        'Tipo Hab.': 'tipo_habitacion',
        'Código Hab.': 'cod_hab',
        'Tarifa': 'tarifa_neta',
        'Canal': 'canal_distribucion',
        'Cliente': 'nombre_cliente',
        'Email': 'email_cliente',
        'Teléfono': 'telefono_cliente',
        'Estado': 'estado_reserva',
        'Observaciones': 'observaciones'
    }
    
    STAYS_MAPPING = {
        # Mapeo de columnas de Excel a columnas de la base de datos
        'Nº Registro': 'registro_num',
        'Fecha Check-in': 'fecha_checkin',
        'Fecha Check-out': 'fecha_checkout',
        'Noches': 'noches',
        'Tipo Hab.': 'tipo_habitacion',
        'Código Hab.': 'cod_hab',
        'Valor Venta': 'valor_venta',
        'Canal': 'canal_distribucion',
        'Cliente': 'nombre_cliente',
        'Email': 'email_cliente',
        'Teléfono': 'telefono_cliente',
        'Estado': 'estado_estancia',
        'Observaciones': 'observaciones'
    }
    
    SUMMARY_MAPPING = {
        # Mapeo de columnas de Excel a columnas de la base de datos
        'Fecha': 'fecha',
        'Habitaciones Disponibles': 'habitaciones_disponibles',
        'Habitaciones Ocupadas': 'habitaciones_ocupadas',
        'Ingresos Totales': 'ingresos_totales',
        'ADR': 'adr',
        'RevPAR': 'revpar',
        'Ocupación (%)': 'ocupacion_porcentaje'
    }
    
    @staticmethod
    def map_columns(df, mapping):
        """
        Mapea las columnas del DataFrame según el mapeo proporcionado.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars
            mapping (dict): Diccionario con el mapeo de columnas {columna_excel: columna_db}
            
        Returns:
            pl.DataFrame: DataFrame con las columnas mapeadas
        """
        try:
            logger.info(f"Mapeando columnas según el mapeo proporcionado")
            
            # Crear un diccionario para renombrar las columnas
            rename_dict = {}
            
            # Para cada columna en el DataFrame
            for col in df.columns:
                # Si la columna está en el mapeo
                if col in mapping:
                    # Agregar al diccionario de renombrado
                    rename_dict[col] = mapping[col]
            
            # Renombrar las columnas
            if rename_dict:
                df = df.rename(rename_dict)
                logger.info(f"Columnas renombradas: {rename_dict}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al mapear columnas: {e}")
            return df
    
    @staticmethod
    def process_bookings(df):
        """
        Procesa un DataFrame de reservas.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars con datos de reservas
            
        Returns:
            pl.DataFrame: DataFrame procesado
        """
        try:
            logger.info("Procesando DataFrame de reservas")
            
            # Mapear columnas
            df = DataMapper.map_columns(df, DataMapper.BOOKINGS_MAPPING)
            
            # Limpiar fechas
            date_columns = ['fecha_reserva', 'fecha_llegada', 'fecha_salida']
            df = DataCleaner.clean_dates(df, date_columns)
            
            # Limpiar columnas numéricas
            numeric_columns = ['noches', 'tarifa_neta']
            df = DataCleaner.clean_numeric(df, numeric_columns)
            
            # Estandarizar categorías
            category_columns = ['tipo_habitacion', 'canal_distribucion', 'estado_reserva']
            df = DataCleaner.standardize_categories(df, category_columns)
            
            # Manejar valores faltantes
            df = DataCleaner.handle_missing_values(df, strategy="fill", fill_values={
                'email_cliente': '',
                'telefono_cliente': '',
                'observaciones': ''
            })
            
            # Calcular noches si no existe la columna
            if 'noches' not in df.columns or df.filter(pl.col('noches').is_null()).shape[0] > 0:
                df = DataCleaner.calculate_nights(df, 'fecha_llegada', 'fecha_salida')
            
            # Calcular tarifa por noche
            df = DataCleaner.calculate_rate_per_night(df, 'tarifa_neta', 'noches')
            
            logger.info(f"DataFrame de reservas procesado: {df.shape[0]} filas, {df.shape[1]} columnas")
            return df
            
        except Exception as e:
            logger.error(f"Error al procesar DataFrame de reservas: {e}")
            return df
    
    @staticmethod
    def process_stays(df):
        """
        Procesa un DataFrame de estancias.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars con datos de estancias
            
        Returns:
            pl.DataFrame: DataFrame procesado
        """
        try:
            logger.info("Procesando DataFrame de estancias")
            
            # Mapear columnas
            df = DataMapper.map_columns(df, DataMapper.STAYS_MAPPING)
            
            # Limpiar fechas
            date_columns = ['fecha_checkin', 'fecha_checkout']
            df = DataCleaner.clean_dates(df, date_columns)
            
            # Limpiar columnas numéricas
            numeric_columns = ['noches', 'valor_venta']
            df = DataCleaner.clean_numeric(df, numeric_columns)
            
            # Estandarizar categorías
            category_columns = ['tipo_habitacion', 'canal_distribucion', 'estado_estancia']
            df = DataCleaner.standardize_categories(df, category_columns)
            
            # Manejar valores faltantes
            df = DataCleaner.handle_missing_values(df, strategy="fill", fill_values={
                'email_cliente': '',
                'telefono_cliente': '',
                'observaciones': ''
            })
            
            # Calcular noches si no existe la columna
            if 'noches' not in df.columns or df.filter(pl.col('noches').is_null()).shape[0] > 0:
                df = DataCleaner.calculate_nights(df, 'fecha_checkin', 'fecha_checkout')
            
            logger.info(f"DataFrame de estancias procesado: {df.shape[0]} filas, {df.shape[1]} columnas")
            return df
            
        except Exception as e:
            logger.error(f"Error al procesar DataFrame de estancias: {e}")
            return df
    
    @staticmethod
    def process_summary(df):
        """
        Procesa un DataFrame de resumen diario.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars con datos de resumen diario
            
        Returns:
            pl.DataFrame: DataFrame procesado
        """
        try:
            logger.info("Procesando DataFrame de resumen diario")
            
            # Mapear columnas
            df = DataMapper.map_columns(df, DataMapper.SUMMARY_MAPPING)
            
            # Limpiar fechas
            date_columns = ['fecha']
            df = DataCleaner.clean_dates(df, date_columns)
            
            # Limpiar columnas numéricas
            numeric_columns = ['habitaciones_disponibles', 'habitaciones_ocupadas', 
                              'ingresos_totales', 'adr', 'revpar', 'ocupacion_porcentaje']
            df = DataCleaner.clean_numeric(df, numeric_columns)
            
            # Calcular ADR si no existe la columna
            if 'adr' not in df.columns or df.filter(pl.col('adr').is_null()).shape[0] > 0:
                df = df.with_columns([
                    (pl.col('ingresos_totales') / pl.col('habitaciones_ocupadas')).alias('adr')
                ])
            
            # Calcular RevPAR si no existe la columna
            if 'revpar' not in df.columns or df.filter(pl.col('revpar').is_null()).shape[0] > 0:
                df = df.with_columns([
                    (pl.col('ingresos_totales') / pl.col('habitaciones_disponibles')).alias('revpar')
                ])
            
            # Calcular ocupación si no existe la columna
            if 'ocupacion_porcentaje' not in df.columns or df.filter(pl.col('ocupacion_porcentaje').is_null()).shape[0] > 0:
                df = df.with_columns([
                    (pl.col('habitaciones_ocupadas') / pl.col('habitaciones_disponibles') * 100).alias('ocupacion_porcentaje')
                ])
            
            logger.info(f"DataFrame de resumen diario procesado: {df.shape[0]} filas, {df.shape[1]} columnas")
            return df
            
        except Exception as e:
            logger.error(f"Error al procesar DataFrame de resumen diario: {e}")
            return df
    
    @staticmethod
    def save_bookings_to_db(df):
        """
        Guarda un DataFrame de reservas en la base de datos.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars con datos de reservas
            
        Returns:
            int: Número de filas insertadas
        """
        try:
            logger.info("Guardando DataFrame de reservas en la base de datos")
            
            # Convertir a lista de tuplas
            data = []
            for row in df.iter_rows(named=True):
                data.append((
                    row.get('registro_num'),
                    row.get('fecha_reserva'),
                    row.get('fecha_llegada'),
                    row.get('fecha_salida'),
                    row.get('noches'),
                    row.get('cod_hab'),
                    row.get('tipo_habitacion'),
                    row.get('tarifa_neta'),
                    row.get('canal_distribucion'),
                    row.get('nombre_cliente'),
                    row.get('email_cliente'),
                    row.get('telefono_cliente'),
                    row.get('estado_reserva'),
                    row.get('observaciones')
                ))
            
            # Insertar en la base de datos
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.executemany('''
                INSERT INTO RAW_BOOKINGS (
                    registro_num, fecha_reserva, fecha_llegada, fecha_salida,
                    noches, cod_hab, tipo_habitacion, tarifa_neta,
                    canal_distribucion, nombre_cliente, email_cliente,
                    telefono_cliente, estado_reserva, observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
                
                conn.commit()
                rows_inserted = cursor.rowcount
            
            logger.info(f"Se insertaron {rows_inserted} filas en la tabla RAW_BOOKINGS")
            return rows_inserted
            
        except Exception as e:
            logger.error(f"Error al guardar DataFrame de reservas en la base de datos: {e}")
            return 0
    
    @staticmethod
    def save_stays_to_db(df):
        """
        Guarda un DataFrame de estancias en la base de datos.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars con datos de estancias
            
        Returns:
            int: Número de filas insertadas
        """
        try:
            logger.info("Guardando DataFrame de estancias en la base de datos")
            
            # Convertir a lista de tuplas
            data = []
            for row in df.iter_rows(named=True):
                data.append((
                    row.get('registro_num'),
                    row.get('fecha_checkin'),
                    row.get('fecha_checkout'),
                    row.get('noches'),
                    row.get('cod_hab'),
                    row.get('tipo_habitacion'),
                    row.get('valor_venta'),
                    row.get('canal_distribucion'),
                    row.get('nombre_cliente'),
                    row.get('email_cliente'),
                    row.get('telefono_cliente'),
                    row.get('estado_estancia'),
                    row.get('observaciones')
                ))
            
            # Insertar en la base de datos
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.executemany('''
                INSERT INTO RAW_STAYS (
                    registro_num, fecha_checkin, fecha_checkout,
                    noches, cod_hab, tipo_habitacion, valor_venta,
                    canal_distribucion, nombre_cliente, email_cliente,
                    telefono_cliente, estado_estancia, observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
                
                conn.commit()
                rows_inserted = cursor.rowcount
            
            logger.info(f"Se insertaron {rows_inserted} filas en la tabla RAW_STAYS")
            return rows_inserted
            
        except Exception as e:
            logger.error(f"Error al guardar DataFrame de estancias en la base de datos: {e}")
            return 0
    
    @staticmethod
    def save_summary_to_db(df):
        """
        Guarda un DataFrame de resumen diario en la base de datos.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars con datos de resumen diario
            
        Returns:
            int: Número de filas insertadas
        """
        try:
            logger.info("Guardando DataFrame de resumen diario en la base de datos")
            
            # Convertir a lista de tuplas
            data = []
            for row in df.iter_rows(named=True):
                data.append((
                    row.get('fecha'),
                    row.get('habitaciones_disponibles'),
                    row.get('habitaciones_ocupadas'),
                    row.get('ingresos_totales'),
                    row.get('adr'),
                    row.get('revpar'),
                    row.get('ocupacion_porcentaje')
                ))
            
            # Insertar en la base de datos
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.executemany('''
                INSERT INTO HISTORICAL_SUMMARY (
                    fecha, habitaciones_disponibles, habitaciones_ocupadas,
                    ingresos_totales, adr, revpar, ocupacion_porcentaje
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', data)
                
                conn.commit()
                rows_inserted = cursor.rowcount
            
            logger.info(f"Se insertaron {rows_inserted} filas en la tabla HISTORICAL_SUMMARY")
            return rows_inserted
            
        except Exception as e:
            logger.error(f"Error al guardar DataFrame de resumen diario en la base de datos: {e}")
            return 0
    
    @staticmethod
    def expand_and_save_bookings(df):
        """
        Expande un DataFrame de reservas (una fila por noche) y lo guarda en las tablas de ocupación e ingresos diarios.
        
        Args:
            df (pl.DataFrame): DataFrame de Polars con datos de reservas
            
        Returns:
            tuple: (filas_ocupacion, filas_ingresos) - Número de filas insertadas en cada tabla
        """
        try:
            logger.info("Expandiendo y guardando DataFrame de reservas")
            
            # Expandir reservas (una fila por noche)
            expanded_df = DataCleaner.expand_stays(
                df, 
                'fecha_llegada', 
                'fecha_salida', 
                id_cols=['registro_num', 'cod_hab', 'tipo_habitacion'],
                rate_col='tarifa_neta'
            )
            
            # Agrupar por fecha y tipo de habitación para calcular ocupación
            occupancy_df = expanded_df.group_by(['fecha', 'tipo_habitacion']).agg([
                pl.count().alias('habitaciones_ocupadas')
            ])
            
            # Obtener los IDs de los tipos de habitación
            room_type_ids = {}
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name FROM ROOM_TYPES')
                for row in cursor.fetchall():
                    room_type_ids[row['name'].lower()] = row['id']
            
            # Obtener el número de habitaciones disponibles por tipo
            room_counts = {}
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, num_config FROM ROOM_TYPES')
                for row in cursor.fetchall():
                    room_counts[row['id']] = row['num_config']
            
            # Preparar datos para la tabla de ocupación
            occupancy_data = []
            for row in occupancy_df.iter_rows(named=True):
                tipo_hab = row['tipo_habitacion'].lower()
                room_type_id = room_type_ids.get(tipo_hab)
                
                if room_type_id:
                    habitaciones_disponibles = room_counts.get(room_type_id, 0)
                    habitaciones_ocupadas = row['habitaciones_ocupadas']
                    
                    # Calcular porcentaje de ocupación
                    ocupacion_porcentaje = 0
                    if habitaciones_disponibles > 0:
                        ocupacion_porcentaje = (habitaciones_ocupadas / habitaciones_disponibles) * 100
                    
                    occupancy_data.append((
                        row['fecha'],
                        room_type_id,
                        habitaciones_disponibles,
                        habitaciones_ocupadas,
                        ocupacion_porcentaje
                    ))
            
            # Agrupar por fecha y tipo de habitación para calcular ingresos
            revenue_df = expanded_df.group_by(['fecha', 'tipo_habitacion']).agg([
                pl.sum('tarifa_por_noche').alias('ingresos')
            ])
            
            # Preparar datos para la tabla de ingresos
            revenue_data = []
            for row in revenue_df.iter_rows(named=True):
                tipo_hab = row['tipo_habitacion'].lower()
                room_type_id = room_type_ids.get(tipo_hab)
                
                if room_type_id:
                    habitaciones_disponibles = room_counts.get(room_type_id, 0)
                    
                    # Obtener habitaciones ocupadas
                    habitaciones_ocupadas = 0
                    for occ_row in occupancy_data:
                        if occ_row[0] == row['fecha'] and occ_row[1] == room_type_id:
                            habitaciones_ocupadas = occ_row[3]
                            break
                    
                    # Calcular ADR y RevPAR
                    adr = 0
                    revpar = 0
                    if habitaciones_ocupadas > 0:
                        adr = row['ingresos'] / habitaciones_ocupadas
                    if habitaciones_disponibles > 0:
                        revpar = row['ingresos'] / habitaciones_disponibles
                    
                    revenue_data.append((
                        row['fecha'],
                        room_type_id,
                        row['ingresos'],
                        adr,
                        revpar
                    ))
            
            # Insertar datos de ocupación
            occupancy_rows = 0
            if occupancy_data:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.executemany('''
                    INSERT INTO DAILY_OCCUPANCY (
                        fecha, room_type_id, habitaciones_disponibles,
                        habitaciones_ocupadas, ocupacion_porcentaje
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ''', occupancy_data)
                    
                    conn.commit()
                    occupancy_rows = cursor.rowcount
            
            # Insertar datos de ingresos
            revenue_rows = 0
            if revenue_data:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.executemany('''
                    INSERT INTO DAILY_REVENUE (
                        fecha, room_type_id, ingresos, adr, revpar
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ''', revenue_data)
                    
                    conn.commit()
                    revenue_rows = cursor.rowcount
            
            logger.info(f"Se insertaron {occupancy_rows} filas en la tabla DAILY_OCCUPANCY")
            logger.info(f"Se insertaron {revenue_rows} filas en la tabla DAILY_REVENUE")
            
            return (occupancy_rows, revenue_rows)
            
        except Exception as e:
            logger.error(f"Error al expandir y guardar DataFrame de reservas: {e}")
            return (0, 0)