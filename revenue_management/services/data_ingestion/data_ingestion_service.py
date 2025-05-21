#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo principal para la ingesta de datos
"""

import os
import polars as pl
from pathlib import Path
from datetime import datetime
from utils.logger import setup_logger
from services.data_ingestion.excel_reader import ExcelReader
from services.data_ingestion.data_cleaner import DataCleaner
from services.data_ingestion.data_mapper import DataMapper
from db.database import db

# Configurar logger
logger = setup_logger(__name__)

class DataIngestionService:
    """
    Servicio para la ingesta de datos
    """
    
    def __init__(self):
        """
        Inicializa el servicio de ingesta de datos
        """
        self.excel_reader = ExcelReader()
    
    def ingest_bookings(self, file_path, sheet_name=None, sheet_index=0):
        """
        Ingiere datos de reservas desde un archivo Excel.
        
        Args:
            file_path (str): Ruta al archivo Excel
            sheet_name (str, optional): Nombre de la hoja a leer
            sheet_index (int, optional): Índice de la hoja a leer (por defecto 0)
            
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        try:
            logger.info(f"Iniciando ingesta de datos de reservas desde {file_path}")
            
            # Leer archivo Excel
            df = self.excel_reader.read_excel(file_path, sheet_name, sheet_index)
            
            if df is None or df.shape[0] == 0:
                return (False, "No se pudieron leer datos del archivo Excel", 0)
            
            # Procesar datos
            df = DataMapper.process_bookings(df)
            
            # Guardar en la base de datos
            rows_inserted = DataMapper.save_bookings_to_db(df)
            
            if rows_inserted == 0:
                return (False, "No se pudieron insertar datos en la base de datos", 0)
            
            # Expandir y guardar en tablas de ocupación e ingresos
            occupancy_rows, revenue_rows = DataMapper.expand_and_save_bookings(df)
            
            message = f"Se procesaron {rows_inserted} reservas. "
            message += f"Se generaron {occupancy_rows} registros de ocupación y {revenue_rows} registros de ingresos."
            
            logger.info(f"Ingesta de datos de reservas completada: {message}")
            return (True, message, rows_inserted)
            
        except Exception as e:
            error_msg = f"Error en la ingesta de datos de reservas: {e}"
            logger.error(error_msg)
            return (False, error_msg, 0)
    
    def ingest_stays(self, file_path, sheet_name=None, sheet_index=0):
        """
        Ingiere datos de estancias desde un archivo Excel.
        
        Args:
            file_path (str): Ruta al archivo Excel
            sheet_name (str, optional): Nombre de la hoja a leer
            sheet_index (int, optional): Índice de la hoja a leer (por defecto 0)
            
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        try:
            logger.info(f"Iniciando ingesta de datos de estancias desde {file_path}")
            
            # Leer archivo Excel
            df = self.excel_reader.read_excel(file_path, sheet_name, sheet_index)
            
            if df is None or df.shape[0] == 0:
                return (False, "No se pudieron leer datos del archivo Excel", 0)
            
            # Procesar datos
            df = DataMapper.process_stays(df)
            
            # Guardar en la base de datos
            rows_inserted = DataMapper.save_stays_to_db(df)
            
            if rows_inserted == 0:
                return (False, "No se pudieron insertar datos en la base de datos", 0)
            
            message = f"Se procesaron {rows_inserted} estancias."
            
            logger.info(f"Ingesta de datos de estancias completada: {message}")
            return (True, message, rows_inserted)
            
        except Exception as e:
            error_msg = f"Error en la ingesta de datos de estancias: {e}"
            logger.error(error_msg)
            return (False, error_msg, 0)
    
    def ingest_summary(self, file_path, sheet_name=None, sheet_index=0):
        """
        Ingiere datos de resumen diario desde un archivo Excel.
        
        Args:
            file_path (str): Ruta al archivo Excel
            sheet_name (str, optional): Nombre de la hoja a leer
            sheet_index (int, optional): Índice de la hoja a leer (por defecto 0)
            
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        try:
            logger.info(f"Iniciando ingesta de datos de resumen diario desde {file_path}")
            
            # Leer archivo Excel
            df = self.excel_reader.read_excel(file_path, sheet_name, sheet_index)
            
            if df is None or df.shape[0] == 0:
                return (False, "No se pudieron leer datos del archivo Excel", 0)
            
            # Procesar datos
            df = DataMapper.process_summary(df)
            
            # Guardar en la base de datos
            rows_inserted = DataMapper.save_summary_to_db(df)
            
            if rows_inserted == 0:
                return (False, "No se pudieron insertar datos en la base de datos", 0)
            
            message = f"Se procesaron {rows_inserted} registros de resumen diario."
            
            logger.info(f"Ingesta de datos de resumen diario completada: {message}")
            return (True, message, rows_inserted)
            
        except Exception as e:
            error_msg = f"Error en la ingesta de datos de resumen diario: {e}"
            logger.error(error_msg)
            return (False, error_msg, 0)
    
    def ingest_all_from_file(self, file_path):
        """
        Ingiere todos los tipos de datos desde un archivo Excel con múltiples hojas.
        
        Args:
            file_path (str): Ruta al archivo Excel
            
        Returns:
            dict: Resultados de la ingesta para cada tipo de datos
        """
        try:
            logger.info(f"Iniciando ingesta de todos los tipos de datos desde {file_path}")
            
            # Obtener nombres de las hojas
            sheet_names = self.excel_reader.get_sheet_names(file_path)
            
            if not sheet_names:
                return {
                    'success': False,
                    'message': "No se pudieron obtener las hojas del archivo Excel",
                    'details': {}
                }
            
            results = {}
            
            # Buscar hojas por nombre o patrón
            for sheet_name in sheet_names:
                sheet_lower = sheet_name.lower()
                
                # Hoja de reservas
                if 'reserva' in sheet_lower or 'booking' in sheet_lower:
                    success, message, rows = self.ingest_bookings(file_path, sheet_name)
                    results['bookings'] = {
                        'success': success,
                        'message': message,
                        'rows_processed': rows
                    }
                
                # Hoja de estancias
                elif 'estancia' in sheet_lower or 'stay' in sheet_lower or 'check' in sheet_lower:
                    success, message, rows = self.ingest_stays(file_path, sheet_name)
                    results['stays'] = {
                        'success': success,
                        'message': message,
                        'rows_processed': rows
                    }
                
                # Hoja de resumen
                elif 'resumen' in sheet_lower or 'summary' in sheet_lower or 'forecast' in sheet_lower:
                    success, message, rows = self.ingest_summary(file_path, sheet_name)
                    results['summary'] = {
                        'success': success,
                        'message': message,
                        'rows_processed': rows
                    }
            
            # Verificar si se procesó algún tipo de datos
            if not results:
                return {
                    'success': False,
                    'message': "No se encontraron hojas con nombres reconocibles en el archivo Excel",
                    'details': {}
                }
            
            # Determinar éxito general
            success = any(result['success'] for result in results.values())
            
            # Construir mensaje general
            if success:
                message = "Ingesta de datos completada con los siguientes resultados:"
                for data_type, result in results.items():
                    message += f"\n- {data_type}: {result['message']}"
            else:
                message = "La ingesta de datos falló para todos los tipos de datos"
            
            logger.info(f"Ingesta de todos los tipos de datos completada: {success}")
            
            return {
                'success': success,
                'message': message,
                'details': results
            }
            
        except Exception as e:
            error_msg = f"Error en la ingesta de todos los tipos de datos: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'details': {}
            }
    
    def reconcile_data(self):
        """
        Reconcilia los datos de reservas y estancias para generar datos consolidados.
        
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        try:
            logger.info("Iniciando reconciliación de datos")
            
            # Obtener datos de reservas
            bookings_df = self._get_bookings_from_db()
            
            if bookings_df is None or bookings_df.shape[0] == 0:
                return (False, "No hay datos de reservas para reconciliar", 0)
            
            # Obtener datos de estancias
            stays_df = self._get_stays_from_db()
            
            if stays_df is None or stays_df.shape[0] == 0:
                return (False, "No hay datos de estancias para reconciliar", 0)
            
            # Reconciliar datos
            # Priorizar valor_venta de estancias sobre tarifa_neta de reservas
            
            # Expandir estancias (una fila por noche)
            expanded_stays = DataCleaner.expand_stays(
                stays_df, 
                'fecha_checkin', 
                'fecha_checkout', 
                id_cols=['registro_num', 'cod_hab', 'tipo_habitacion'],
                rate_col='valor_venta'
            )
            
            # Expandir reservas (una fila por noche)
            expanded_bookings = DataCleaner.expand_stays(
                bookings_df, 
                'fecha_llegada', 
                'fecha_salida', 
                id_cols=['registro_num', 'cod_hab', 'tipo_habitacion'],
                rate_col='tarifa_neta'
            )
            
            # Unir datos de estancias y reservas
            # Priorizar estancias sobre reservas
            
            # Crear columna de fuente
            expanded_stays = expanded_stays.with_columns([
                pl.lit('estancia').alias('fuente')
            ])
            
            expanded_bookings = expanded_bookings.with_columns([
                pl.lit('reserva').alias('fuente')
            ])
            
            # Unir DataFrames
            combined_df = pl.concat([expanded_stays, expanded_bookings])
            
            # Agrupar por fecha, registro_num, cod_hab y priorizar estancias
            reconciled_df = combined_df.sort(['fecha', 'registro_num', 'cod_hab', 'fuente'])
            reconciled_df = reconciled_df.group_by(['fecha', 'registro_num', 'cod_hab']).agg([
                pl.first('tipo_habitacion').alias('tipo_habitacion'),
                pl.first('fuente').alias('fuente'),
                pl.when(pl.first('fuente') == 'estancia')
                  .then(pl.first('valor_venta'))
                  .otherwise(pl.first('tarifa_por_noche'))
                  .alias('ingreso')
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
            
            # Agrupar por fecha y tipo de habitación para calcular ocupación e ingresos
            daily_df = reconciled_df.group_by(['fecha', 'tipo_habitacion']).agg([
                pl.count().alias('habitaciones_ocupadas'),
                pl.sum('ingreso').alias('ingresos')
            ])
            
            # Preparar datos para las tablas
            occupancy_data = []
            revenue_data = []
            
            for row in daily_df.iter_rows(named=True):
                tipo_hab = row['tipo_habitacion'].lower()
                room_type_id = room_type_ids.get(tipo_hab)
                
                if room_type_id:
                    habitaciones_disponibles = room_counts.get(room_type_id, 0)
                    habitaciones_ocupadas = row['habitaciones_ocupadas']
                    ingresos = row['ingresos']
                    
                    # Calcular porcentaje de ocupación
                    ocupacion_porcentaje = 0
                    if habitaciones_disponibles > 0:
                        ocupacion_porcentaje = (habitaciones_ocupadas / habitaciones_disponibles) * 100
                    
                    # Calcular ADR y RevPAR
                    adr = 0
                    revpar = 0
                    if habitaciones_ocupadas > 0:
                        adr = ingresos / habitaciones_ocupadas
                    if habitaciones_disponibles > 0:
                        revpar = ingresos / habitaciones_disponibles
                    
                    occupancy_data.append((
                        row['fecha'],
                        room_type_id,
                        habitaciones_disponibles,
                        habitaciones_ocupadas,
                        ocupacion_porcentaje
                    ))
                    
                    revenue_data.append((
                        row['fecha'],
                        room_type_id,
                        ingresos,
                        adr,
                        revpar
                    ))
            
            # Limpiar tablas existentes
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM DAILY_OCCUPANCY')
                cursor.execute('DELETE FROM DAILY_REVENUE')
                conn.commit()
            
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
            
            message = f"Se reconciliaron los datos y se generaron {occupancy_rows} registros de ocupación y {revenue_rows} registros de ingresos."
            
            logger.info(f"Reconciliación de datos completada: {message}")
            return (True, message, occupancy_rows + revenue_rows)
            
        except Exception as e:
            error_msg = f"Error en la reconciliación de datos: {e}"
            logger.error(error_msg)
            return (False, error_msg, 0)
    
    def _get_bookings_from_db(self):
        """
        Obtiene los datos de reservas de la base de datos.
        
        Returns:
            pl.DataFrame: DataFrame de Polars con los datos de reservas
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RAW_BOOKINGS')
                rows = cursor.fetchall()
                
                if not rows:
                    return None
                
                # Convertir a DataFrame de pandas
                import pandas as pd
                df_pandas = pd.DataFrame([dict(row) for row in rows])
                
                # Convertir a Polars
                df = pl.from_pandas(df_pandas)
                
                return df
                
        except Exception as e:
            logger.error(f"Error al obtener datos de reservas de la base de datos: {e}")
            return None
    
    def _get_stays_from_db(self):
        """
        Obtiene los datos de estancias de la base de datos.
        
        Returns:
            pl.DataFrame: DataFrame de Polars con los datos de estancias
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RAW_STAYS')
                rows = cursor.fetchall()
                
                if not rows:
                    return None
                
                # Convertir a DataFrame de pandas
                import pandas as pd
                df_pandas = pd.DataFrame([dict(row) for row in rows])
                
                # Convertir a Polars
                df = pl.from_pandas(df_pandas)
                
                return df
                
        except Exception as e:
            logger.error(f"Error al obtener datos de estancias de la base de datos: {e}")
            return None