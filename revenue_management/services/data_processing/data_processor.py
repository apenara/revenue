#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para el procesamiento de datos
"""

import polars as pl
from datetime import datetime, timedelta
from utils.logger import setup_logger
from db.database import db
from models.room import Room
from models.daily_occupancy import DailyOccupancy
from models.daily_revenue import DailyRevenue

# Configurar logger
logger = setup_logger(__name__)

class DataProcessor:
    """
    Clase para el procesamiento de datos
    """
    
    @staticmethod
    def generate_daily_data(start_date, end_date):
        """
        Genera datos diarios de ocupación e ingresos para un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        try:
            logger.info(f"Generando datos diarios para el rango {start_date} - {end_date}")
            
            # Convertir fechas a datetime si son strings
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Obtener todos los tipos de habitación
            rooms = Room.get_all()
            
            if not rooms:
                return (False, "No hay tipos de habitación definidos", 0)
            
            # Generar fechas
            dates = []
            current_date = start_date
            while current_date <= end_date:
                dates.append(current_date)
                current_date += timedelta(days=1)
            
            # Obtener datos existentes de ocupación
            existing_occupancy = {}
            occupancy_data = DailyOccupancy.get_by_date_range(start_date, end_date)
            for occ in occupancy_data:
                key = (occ.fecha.strftime('%Y-%m-%d'), occ.room_type_id)
                existing_occupancy[key] = occ
            
            # Obtener datos existentes de ingresos
            existing_revenue = {}
            revenue_data = DailyRevenue.get_by_date_range(start_date, end_date)
            for rev in revenue_data:
                key = (rev.fecha.strftime('%Y-%m-%d'), rev.room_type_id)
                existing_revenue[key] = rev
            
            # Generar datos diarios
            occupancy_count = 0
            revenue_count = 0
            
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                
                for room in rooms:
                    key = (date_str, room.id)
                    
                    # Verificar si ya existe registro de ocupación
                    if key not in existing_occupancy:
                        # Crear registro de ocupación
                        occupancy = DailyOccupancy(
                            fecha=date,
                            room_type_id=room.id,
                            habitaciones_disponibles=room.num_config,
                            habitaciones_ocupadas=0,
                            ocupacion_porcentaje=0
                        )
                        occupancy.save()
                        occupancy_count += 1
                    
                    # Verificar si ya existe registro de ingresos
                    if key not in existing_revenue:
                        # Crear registro de ingresos
                        revenue = DailyRevenue(
                            fecha=date,
                            room_type_id=room.id,
                            ingresos=0,
                            adr=0,
                            revpar=0
                        )
                        revenue.save()
                        revenue_count += 1
            
            message = f"Se generaron {occupancy_count} registros de ocupación y {revenue_count} registros de ingresos."
            
            logger.info(f"Generación de datos diarios completada: {message}")
            return (True, message, occupancy_count + revenue_count)
            
        except Exception as e:
            error_msg = f"Error en la generación de datos diarios: {e}"
            logger.error(error_msg)
            return (False, error_msg, 0)
    
    @staticmethod
    def consolidate_daily_data(date=None):
        """
        Consolida los datos diarios de ocupación e ingresos para una fecha específica o para todas las fechas.
        
        Args:
            date (str/datetime, optional): Fecha a consolidar. Si es None, consolida todas las fechas.
            
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        try:
            if date:
                logger.info(f"Consolidando datos diarios para la fecha {date}")
            else:
                logger.info("Consolidando datos diarios para todas las fechas")
            
            # Convertir fecha a string si es datetime
            date_str = None
            if date:
                if isinstance(date, datetime):
                    date_str = date.strftime('%Y-%m-%d')
                else:
                    date_str = date
            
            # Obtener datos de ocupación
            occupancy_data = []
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if date_str:
                    cursor.execute('''
                    SELECT fecha, SUM(habitaciones_disponibles) as habitaciones_disponibles,
                           SUM(habitaciones_ocupadas) as habitaciones_ocupadas
                    FROM DAILY_OCCUPANCY
                    WHERE fecha = ?
                    GROUP BY fecha
                    ''', (date_str,))
                else:
                    cursor.execute('''
                    SELECT fecha, SUM(habitaciones_disponibles) as habitaciones_disponibles,
                           SUM(habitaciones_ocupadas) as habitaciones_ocupadas
                    FROM DAILY_OCCUPANCY
                    GROUP BY fecha
                    ''')
                
                occupancy_data = cursor.fetchall()
            
            # Obtener datos de ingresos
            revenue_data = []
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if date_str:
                    cursor.execute('''
                    SELECT fecha, SUM(ingresos) as ingresos_totales
                    FROM DAILY_REVENUE
                    WHERE fecha = ?
                    GROUP BY fecha
                    ''', (date_str,))
                else:
                    cursor.execute('''
                    SELECT fecha, SUM(ingresos) as ingresos_totales
                    FROM DAILY_REVENUE
                    GROUP BY fecha
                    ''')
                
                revenue_data = cursor.fetchall()
            
            # Combinar datos
            summary_data = []
            
            # Crear diccionario de ingresos por fecha
            revenue_by_date = {}
            for row in revenue_data:
                revenue_by_date[row['fecha']] = row['ingresos_totales']
            
            # Procesar datos de ocupación y combinar con ingresos
            for row in occupancy_data:
                fecha = row['fecha']
                habitaciones_disponibles = row['habitaciones_disponibles']
                habitaciones_ocupadas = row['habitaciones_ocupadas']
                ingresos_totales = revenue_by_date.get(fecha, 0)
                
                # Calcular KPIs
                ocupacion_porcentaje = 0
                adr = 0
                revpar = 0
                
                if habitaciones_disponibles > 0:
                    ocupacion_porcentaje = (habitaciones_ocupadas / habitaciones_disponibles) * 100
                    revpar = ingresos_totales / habitaciones_disponibles
                
                if habitaciones_ocupadas > 0:
                    adr = ingresos_totales / habitaciones_ocupadas
                
                summary_data.append((
                    fecha,
                    habitaciones_disponibles,
                    habitaciones_ocupadas,
                    ingresos_totales,
                    adr,
                    revpar,
                    ocupacion_porcentaje
                ))
            
            # Eliminar registros existentes
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if date_str:
                    cursor.execute('DELETE FROM HISTORICAL_SUMMARY WHERE fecha = ?', (date_str,))
                else:
                    cursor.execute('DELETE FROM HISTORICAL_SUMMARY')
                
                conn.commit()
            
            # Insertar datos consolidados
            rows_inserted = 0
            if summary_data:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.executemany('''
                    INSERT INTO HISTORICAL_SUMMARY (
                        fecha, habitaciones_disponibles, habitaciones_ocupadas,
                        ingresos_totales, adr, revpar, ocupacion_porcentaje
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', summary_data)
                    
                    conn.commit()
                    rows_inserted = cursor.rowcount
            
            message = f"Se consolidaron {rows_inserted} registros de datos diarios."
            
            logger.info(f"Consolidación de datos diarios completada: {message}")
            return (True, message, rows_inserted)
            
        except Exception as e:
            error_msg = f"Error en la consolidación de datos diarios: {e}"
            logger.error(error_msg)
            return (False, error_msg, 0)
    
    @staticmethod
    def clean_and_normalize_data():
        """
        Limpia y normaliza los datos en la base de datos.
        
        Returns:
            tuple: (éxito, mensaje, filas_procesadas)
        """
        try:
            logger.info("Iniciando limpieza y normalización de datos")
            
            # Limpiar datos de ocupación
            occupancy_count = DataProcessor._clean_occupancy_data()
            
            # Limpiar datos de ingresos
            revenue_count = DataProcessor._clean_revenue_data()
            
            # Consolidar datos diarios
            success, _, summary_count = DataProcessor.consolidate_daily_data()
            
            if not success:
                return (False, "Error al consolidar datos diarios", 0)
            
            message = f"Se limpiaron y normalizaron {occupancy_count} registros de ocupación, "
            message += f"{revenue_count} registros de ingresos y se consolidaron {summary_count} registros."
            
            logger.info(f"Limpieza y normalización de datos completada: {message}")
            return (True, message, occupancy_count + revenue_count + summary_count)
            
        except Exception as e:
            error_msg = f"Error en la limpieza y normalización de datos: {e}"
            logger.error(error_msg)
            return (False, error_msg, 0)
    
    @staticmethod
    def _clean_occupancy_data():
        """
        Limpia y normaliza los datos de ocupación.
        
        Returns:
            int: Número de registros procesados
        """
        try:
            logger.info("Limpiando datos de ocupación")
            
            # Obtener todos los registros de ocupación
            occupancy_data = []
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM DAILY_OCCUPANCY')
                occupancy_data = cursor.fetchall()
            
            if not occupancy_data:
                return 0
            
            # Obtener tipos de habitación
            rooms = {}
            for room in Room.get_all():
                rooms[room.id] = room
            
            # Procesar cada registro
            updated_count = 0
            for row in occupancy_data:
                # Verificar si el tipo de habitación existe
                if row['room_type_id'] not in rooms:
                    continue
                
                room = rooms[row['room_type_id']]
                
                # Verificar si los datos son correctos
                habitaciones_disponibles = row['habitaciones_disponibles']
                habitaciones_ocupadas = row['habitaciones_ocupadas']
                ocupacion_porcentaje = row['ocupacion_porcentaje']
                
                # Corregir habitaciones disponibles si es necesario
                if habitaciones_disponibles != room.num_config:
                    habitaciones_disponibles = room.num_config
                
                # Corregir habitaciones ocupadas si es necesario
                if habitaciones_ocupadas > habitaciones_disponibles:
                    habitaciones_ocupadas = habitaciones_disponibles
                
                # Recalcular porcentaje de ocupación
                if habitaciones_disponibles > 0:
                    ocupacion_porcentaje = (habitaciones_ocupadas / habitaciones_disponibles) * 100
                else:
                    ocupacion_porcentaje = 0
                
                # Actualizar registro si hay cambios
                if (habitaciones_disponibles != row['habitaciones_disponibles'] or
                    habitaciones_ocupadas != row['habitaciones_ocupadas'] or
                    abs(ocupacion_porcentaje - row['ocupacion_porcentaje']) > 0.01):
                    
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                        UPDATE DAILY_OCCUPANCY
                        SET habitaciones_disponibles = ?, habitaciones_ocupadas = ?, ocupacion_porcentaje = ?
                        WHERE id = ?
                        ''', (habitaciones_disponibles, habitaciones_ocupadas, ocupacion_porcentaje, row['id']))
                        conn.commit()
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
            
            logger.info(f"Se limpiaron {updated_count} registros de ocupación")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error al limpiar datos de ocupación: {e}")
            return 0
    
    @staticmethod
    def _clean_revenue_data():
        """
        Limpia y normaliza los datos de ingresos.
        
        Returns:
            int: Número de registros procesados
        """
        try:
            logger.info("Limpiando datos de ingresos")
            
            # Obtener todos los registros de ingresos
            revenue_data = []
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM DAILY_REVENUE')
                revenue_data = cursor.fetchall()
            
            if not revenue_data:
                return 0
            
            # Obtener datos de ocupación
            occupancy_by_key = {}
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT fecha, room_type_id, habitaciones_ocupadas, habitaciones_disponibles FROM DAILY_OCCUPANCY')
                for row in cursor.fetchall():
                    key = (row['fecha'], row['room_type_id'])
                    occupancy_by_key[key] = {
                        'habitaciones_ocupadas': row['habitaciones_ocupadas'],
                        'habitaciones_disponibles': row['habitaciones_disponibles']
                    }
            
            # Procesar cada registro
            updated_count = 0
            for row in revenue_data:
                fecha = row['fecha']
                room_type_id = row['room_type_id']
                ingresos = row['ingresos']
                adr = row['adr']
                revpar = row['revpar']
                
                # Obtener datos de ocupación
                key = (fecha, room_type_id)
                if key in occupancy_by_key:
                    habitaciones_ocupadas = occupancy_by_key[key]['habitaciones_ocupadas']
                    habitaciones_disponibles = occupancy_by_key[key]['habitaciones_disponibles']
                    
                    # Recalcular ADR
                    new_adr = 0
                    if habitaciones_ocupadas > 0:
                        new_adr = ingresos / habitaciones_ocupadas
                    
                    # Recalcular RevPAR
                    new_revpar = 0
                    if habitaciones_disponibles > 0:
                        new_revpar = ingresos / habitaciones_disponibles
                    
                    # Actualizar registro si hay cambios
                    if (abs(new_adr - adr) > 0.01 or abs(new_revpar - revpar) > 0.01):
                        with db.get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                            UPDATE DAILY_REVENUE
                            SET adr = ?, revpar = ?
                            WHERE id = ?
                            ''', (new_adr, new_revpar, row['id']))
                            conn.commit()
                            
                            if cursor.rowcount > 0:
                                updated_count += 1
            
            logger.info(f"Se limpiaron {updated_count} registros de ingresos")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error al limpiar datos de ingresos: {e}")
            return 0