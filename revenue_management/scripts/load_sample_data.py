#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para cargar datos de ejemplo en la base de datos del Framework de Revenue Management.
Genera datos sintéticos para pruebas y demostraciones.
"""

import polars as pl
import json
import os
import sys
import random
import argparse
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import db
from config import config
from services.data_ingestion.data_ingestion_service import DataIngestionService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(config.get("logging.file")))
    ]
)
logger = logging.getLogger("load_sample_data")

def generate_sample_bookings(start_date, end_date, num_bookings=1000):
    """
    Genera datos de reservas de ejemplo.
    
    Args:
        start_date (datetime): Fecha de inicio para las reservas.
        end_date (datetime): Fecha de fin para las reservas.
        num_bookings (int, optional): Número de reservas a generar.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos de reservas generados.
    """
    logger.info(f"Generando {num_bookings} reservas de ejemplo...")
    
    # Obtener tipos de habitación de la configuración
    room_types = config.get("room_types")
    
    # Obtener canales de la configuración
    channels = config.get("channels")
    
    # Obtener temporadas de la configuración
    seasons = config.get("seasons")
    
    # Crear diccionario de temporadas por mes
    season_by_month = {}
    for season in seasons:
        for month in season["months"]:
            season_by_month[month] = season["name"]
    
    # Generar datos de reservas
    bookings_data = []
    
    # Fecha actual para las reservas
    current_date = start_date
    
    for i in range(num_bookings):
        # Seleccionar tipo de habitación aleatorio
        room_type = random.choice(room_types)
        
        # Seleccionar canal aleatorio
        channel = random.choice(channels)
        
        # Fecha de reserva (entre start_date y end_date)
        booking_date = current_date + timedelta(days=random.randint(0, 5))
        if booking_date > end_date:
            booking_date = end_date
        
        # Fecha de llegada (entre 1 y 90 días después de la reserva)
        check_in_date = booking_date + timedelta(days=random.randint(1, 90))
        
        # Duración de la estancia (entre 1 y 7 noches)
        nights = random.randint(1, 7)
        
        # Fecha de salida
        check_out_date = check_in_date + timedelta(days=nights)
        
        # Determinar temporada según el mes de llegada
        season_name = season_by_month.get(check_in_date.month, "Media")
        
        # Determinar tarifa base según tipo de habitación y temporada
        base_rate = 100000 + room_type["capacity"] * 20000  # Tarifa base según capacidad
        
        # Ajustar tarifa según temporada
        season_factor = 0.9 if season_name == "Baja" else 1.2 if season_name == "Alta" else 1.0
        
        # Ajustar tarifa según día de la semana
        weekday = check_in_date.weekday()
        weekday_factor = 1.2 if weekday >= 5 else 1.0  # Fin de semana vs. entre semana
        
        # Calcular tarifa final
        rate_per_night = base_rate * season_factor * weekday_factor
        
        # Añadir algo de variabilidad
        rate_per_night = rate_per_night * random.uniform(0.9, 1.1)
        
        # Calcular tarifa total
        total_rate = rate_per_night * nights
        
        # Generar datos del cliente
        client_name = f"Cliente {i+1}"
        client_email = f"cliente{i+1}@example.com"
        client_phone = f"300{random.randint(1000000, 9999999)}"
        
        # Añadir a los datos
        bookings_data.append({
            'registro_num': f'R{i+1:04d}',
            'fecha_reserva': booking_date.strftime('%Y-%m-%d'),
            'fecha_llegada': check_in_date.strftime('%Y-%m-%d'),
            'fecha_salida': check_out_date.strftime('%Y-%m-%d'),
            'noches': nights,
            'cod_hab': room_type["code"],
            'tipo_habitacion': room_type["name"],
            'tarifa_neta': round(total_rate),
            'canal_distribucion': channel["name"],
            'nombre_cliente': client_name,
            'email_cliente': client_email,
            'telefono_cliente': client_phone,
            'estado_reserva': 'Confirmada',
            'observaciones': f'Reserva de ejemplo generada automáticamente'
        })
        
        # Avanzar la fecha actual
        current_date += timedelta(days=random.randint(0, 2))
        if current_date > end_date:
            current_date = start_date
    
    # Crear DataFrame
    bookings_df = pd.DataFrame(bookings_data)
    
    logger.info(f"Generados {len(bookings_df)} registros de reservas.")
    return bookings_df

def generate_sample_stays(bookings_df, current_date):
    """
    Genera datos de estancias de ejemplo a partir de las reservas.
    Solo convierte a estancias las reservas con fecha de llegada anterior a la fecha actual.
    
    Args:
        bookings_df (pandas.DataFrame): DataFrame con los datos de reservas.
        current_date (datetime): Fecha actual.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos de estancias generados.
    """
    logger.info("Generando estancias de ejemplo a partir de las reservas...")
    
    # Filtrar reservas con fecha de llegada anterior a la fecha actual
    past_bookings = bookings_df[pd.to_datetime(bookings_df['fecha_llegada']) < current_date].copy()
    
    if past_bookings.empty:
        logger.info("No hay reservas pasadas para convertir en estancias.")
        return pd.DataFrame()
    
    # Convertir a estancias
    stays_data = []
    
    for _, booking in past_bookings.iterrows():
        # Determinar si la estancia está completada o en curso
        check_out_date = datetime.strptime(booking['fecha_salida'], '%Y-%m-%d')
        status = 'Completada' if check_out_date < current_date else 'En curso'
        
        # Añadir a los datos
        stays_data.append({
            'registro_num': booking['registro_num'],
            'fecha_checkin': booking['fecha_llegada'],
            'fecha_checkout': booking['fecha_salida'],
            'noches': booking['noches'],
            'cod_hab': booking['cod_hab'],
            'tipo_habitacion': booking['tipo_habitacion'],
            'valor_venta': booking['tarifa_neta'],
            'canal_distribucion': booking['canal_distribucion'],
            'nombre_cliente': booking['nombre_cliente'],
            'email_cliente': booking['email_cliente'],
            'telefono_cliente': booking['telefono_cliente'],
            'estado_estancia': status,
            'observaciones': f'Estancia de ejemplo generada automáticamente'
        })
    
    # Crear DataFrame
    stays_df = pd.DataFrame(stays_data)
    
def generate_historical_summary(start_date, end_date, bookings_df, stays_df):
    """
    Genera datos de resumen diario histórico.
    
    Args:
        start_date (datetime): Fecha de inicio.
        end_date (datetime): Fecha de fin.
        bookings_df (pandas.DataFrame): DataFrame con los datos de reservas.
        stays_df (pandas.DataFrame): DataFrame con los datos de estancias.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos de resumen diario histórico.
    """
    logger.info("Generando resumen diario histórico...")
    
    # Obtener tipos de habitación
    room_types = config.get("room_types")
    total_rooms = sum(rt["count"] for rt in room_types)
    
    # Crear rango de fechas
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Inicializar datos de resumen
    summary_data = []
    
    # Convertir a Polars para procesamiento más eficiente
    if not stays_df.empty:
        stays_pl = pl.from_pandas(stays_df)
        stays_pl = stays_pl.with_columns([
            pl.col('fecha_checkin').str.strptime(pl.Date, '%Y-%m-%d'),
            pl.col('fecha_checkout').str.strptime(pl.Date, '%Y-%m-%d')
        ])
    else:
        stays_pl = pl.DataFrame()
    
    # Para cada fecha en el rango
    for current_date in date_range:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Calcular habitaciones ocupadas para esta fecha
        if not stays_pl.is_empty():
            # Filtrar estancias que incluyen esta fecha
            occupied_rooms = stays_pl.filter(
                (pl.col('fecha_checkin') <= current_date.date()) & 
                (pl.col('fecha_checkout') > current_date.date())
            ).height
        else:
            occupied_rooms = 0
        
        # Asegurar que no exceda el total de habitaciones
        occupied_rooms = min(occupied_rooms, total_rooms)
        
        # Calcular ingresos para esta fecha
        if not stays_pl.is_empty():
            # Filtrar estancias que incluyen esta fecha
            daily_stays = stays_pl.filter(
                (pl.col('fecha_checkin') <= current_date.date()) & 
                (pl.col('fecha_checkout') > current_date.date())
            )
            
            if not daily_stays.is_empty():
                # Calcular ingresos diarios (tarifa total dividida por noches)
                total_revenue = daily_stays.select(
                    (pl.col('valor_venta') / pl.col('noches')).sum()
                ).item()
            else:
                total_revenue = 0
        else:
            total_revenue = 0
        
        # Calcular ADR y RevPAR
        adr = total_revenue / occupied_rooms if occupied_rooms > 0 else 0
        revpar = total_revenue / total_rooms if total_rooms > 0 else 0
        occupancy_percentage = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0
        
        # Añadir a los datos de resumen
        summary_data.append({
            'fecha': date_str,
            'habitaciones_disponibles': total_rooms,
            'habitaciones_ocupadas': occupied_rooms,
            'ingresos_totales': round(total_revenue),
            'adr': round(adr),
            'revpar': round(revpar),
            'ocupacion_porcentaje': round(occupancy_percentage, 2)
        })
    
    # Crear DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    logger.info(f"Generados {len(summary_df)} registros de resumen diario histórico.")
    return summary_df

def generate_daily_occupancy(start_date, end_date, stays_df):
    """
    Genera datos de ocupación diaria por tipo de habitación.
    
    Args:
        start_date (datetime): Fecha de inicio.
        end_date (datetime): Fecha de fin.
        stays_df (pandas.DataFrame): DataFrame con los datos de estancias.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos de ocupación diaria.
    """
    logger.info("Generando datos de ocupación diaria por tipo de habitación...")
    
    # Obtener tipos de habitación
    room_types = config.get("room_types")
    
    # Crear rango de fechas
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Inicializar datos de ocupación
    occupancy_data = []
    
    # Convertir a Polars para procesamiento más eficiente
    if not stays_df.empty:
        stays_pl = pl.from_pandas(stays_df)
        stays_pl = stays_pl.with_columns([
            pl.col('fecha_checkin').str.strptime(pl.Date, '%Y-%m-%d'),
            pl.col('fecha_checkout').str.strptime(pl.Date, '%Y-%m-%d')
        ])
    else:
        stays_pl = pl.DataFrame()
    
    # Para cada fecha y tipo de habitación
    for current_date in date_range:
        date_str = current_date.strftime('%Y-%m-%d')
        
        for room_type in room_types:
            room_type_id = room_type["code"]
            available_rooms = room_type["count"]
            
            # Calcular habitaciones ocupadas para esta fecha y tipo
            if not stays_pl.is_empty():
                # Filtrar estancias que incluyen esta fecha y son de este tipo
                occupied_rooms = stays_pl.filter(
                    (pl.col('fecha_checkin') <= current_date.date()) & 
                    (pl.col('fecha_checkout') > current_date.date()) &
                    (pl.col('cod_hab') == room_type_id)
                ).height
            else:
                occupied_rooms = 0
            
            # Asegurar que no exceda el total de habitaciones disponibles
            occupied_rooms = min(occupied_rooms, available_rooms)
            
            # Calcular porcentaje de ocupación
            occupancy_percentage = (occupied_rooms / available_rooms) * 100 if available_rooms > 0 else 0
            
            # Añadir a los datos de ocupación
            occupancy_data.append({
                'fecha': date_str,
                'room_type_id': room_type_id,
                'habitaciones_disponibles': available_rooms,
                'habitaciones_ocupadas': occupied_rooms,
                'ocupacion_porcentaje': round(occupancy_percentage, 2)
            })
    
    # Crear DataFrame
    occupancy_df = pd.DataFrame(occupancy_data)
    
    logger.info(f"Generados {len(occupancy_df)} registros de ocupación diaria.")
    return occupancy_df

def generate_daily_revenue(start_date, end_date, stays_df):
    """
    Genera datos de ingresos diarios por tipo de habitación.
    
    Args:
        start_date (datetime): Fecha de inicio.
        end_date (datetime): Fecha de fin.
        stays_df (pandas.DataFrame): DataFrame con los datos de estancias.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos de ingresos diarios.
    """
    logger.info("Generando datos de ingresos diarios por tipo de habitación...")
    
    # Obtener tipos de habitación
    room_types = config.get("room_types")
    
    # Crear rango de fechas
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Inicializar datos de ingresos
    revenue_data = []
    
    # Convertir a Polars para procesamiento más eficiente
    if not stays_df.empty:
        stays_pl = pl.from_pandas(stays_df)
        stays_pl = stays_pl.with_columns([
            pl.col('fecha_checkin').str.strptime(pl.Date, '%Y-%m-%d'),
            pl.col('fecha_checkout').str.strptime(pl.Date, '%Y-%m-%d')
        ])
    else:
        stays_pl = pl.DataFrame()
    
    # Para cada fecha y tipo de habitación
    for current_date in date_range:
        date_str = current_date.strftime('%Y-%m-%d')
        
        for room_type in room_types:
            room_type_id = room_type["code"]
            available_rooms = room_type["count"]
            
            # Calcular habitaciones ocupadas e ingresos para esta fecha y tipo
            if not stays_pl.is_empty():
                # Filtrar estancias que incluyen esta fecha y son de este tipo
                daily_stays = stays_pl.filter(
                    (pl.col('fecha_checkin') <= current_date.date()) & 
                    (pl.col('fecha_checkout') > current_date.date()) &
                    (pl.col('cod_hab') == room_type_id)
                )
                
                occupied_rooms = daily_stays.height
                
                if not daily_stays.is_empty():
                    # Calcular ingresos diarios (tarifa total dividida por noches)
                    total_revenue = daily_stays.select(
                        (pl.col('valor_venta') / pl.col('noches')).sum()
                    ).item()
                else:
                    total_revenue = 0
            else:
                occupied_rooms = 0
                total_revenue = 0
            
            # Asegurar que no exceda el total de habitaciones disponibles
            occupied_rooms = min(occupied_rooms, available_rooms)
            
            # Calcular ADR y RevPAR
            adr = total_revenue / occupied_rooms if occupied_rooms > 0 else 0
            revpar = total_revenue / available_rooms if available_rooms > 0 else 0
            
            # Añadir a los datos de ingresos
            revenue_data.append({
                'fecha': date_str,
                'room_type_id': room_type_id,
                'ingresos': round(total_revenue),
                'adr': round(adr),
                'revpar': round(revpar)
            })
    
    # Crear DataFrame
    revenue_df = pd.DataFrame(revenue_data)
    
    logger.info(f"Generados {len(revenue_df)} registros de ingresos diarios.")
    return revenue_df

def generate_pricing_rules():
    """
    Genera reglas de pricing básicas.
    
    Returns:
        list: Lista de reglas de pricing.
    """
    logger.info("Generando reglas de pricing básicas...")
    
    # Definir reglas básicas
    rules = [
        {
            'nombre': 'Ocupación Alta',
            'descripcion': 'Aumentar tarifa cuando la ocupación prevista es alta',
            'parametros': {
                'ocupacion_umbral': 0.8,
                'factor_aumento': 1.15,
                'canales_aplicables': ['Booking.com', 'Expedia', 'Hotelbeds', 'Despegar']
            },
            'prioridad': 1,
            'activa': True
        },
        {
            'nombre': 'Ocupación Baja',
            'descripcion': 'Disminuir tarifa cuando la ocupación prevista es baja',
            'parametros': {
                'ocupacion_umbral': 0.4,
                'factor_reduccion': 0.9,
                'canales_aplicables': ['Booking.com', 'Expedia', 'Hotelbeds', 'Despegar', 'Directo']
            },
            'prioridad': 2,
            'activa': True
        },
        {
            'nombre': 'Temporada Alta',
            'descripcion': 'Ajuste adicional para temporada alta',
            'parametros': {
                'temporada': 'Alta',
                'factor_aumento': 1.1,
                'canales_aplicables': ['Booking.com', 'Expedia', 'Hotelbeds', 'Despegar']
            },
            'prioridad': 3,
            'activa': True
        },
        {
            'nombre': 'Canal Directo',
            'descripcion': 'Descuento para reservas directas',
            'parametros': {
                'canal': 'Directo',
                'factor_reduccion': 0.95,
                'minimo_noches': 2
            },
            'prioridad': 4,
            'activa': True
        },
        {
            'nombre': 'Fin de Semana',
            'descripcion': 'Aumento de tarifa para fines de semana',
            'parametros': {
                'dias_semana': [5, 6],  # Viernes y sábado
                'factor_aumento': 1.2,
                'canales_aplicables': ['Booking.com', 'Expedia', 'Hotelbeds', 'Despegar', 'Directo']
            },
            'prioridad': 5,
            'activa': True
        },
        {
            'nombre': 'Reserva Anticipada',
            'descripcion': 'Descuento para reservas con más de 60 días de antelación',
            'parametros': {
                'dias_antelacion': 60,
                'factor_reduccion': 0.9,
                'canales_aplicables': ['Directo']
            },
            'prioridad': 6,
            'activa': True
        }
    ]
    
    logger.info(f"Generadas {len(rules)} reglas de pricing básicas.")
    return rules
    logger.info(f"Generados {len(stays_df)} registros de estancias.")
    return stays_df

def save_sample_data_to_excel(bookings_df, stays_df, output_dir):
    """
    Guarda los datos de ejemplo en archivos Excel.
    
    Args:
        bookings_df (pandas.DataFrame): DataFrame con los datos de reservas.
        stays_df (pandas.DataFrame): DataFrame con los datos de estancias.
        output_dir (str/Path): Directorio donde guardar los archivos.
    
    Returns:
        tuple: Tupla con las rutas a los archivos generados (bookings_path, stays_path).
    """
    logger.info("Guardando datos de ejemplo en archivos Excel...")
    
    # Crear directorio si no existe
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar reservas
    bookings_path = output_dir / "sample_bookings.xlsx"
    bookings_df.to_excel(bookings_path, sheet_name='Reservas', index=False)
    logger.info(f"Datos de reservas guardados en: {bookings_path}")
    
    # Guardar estancias
    stays_path = output_dir / "sample_stays.xlsx"
    if not stays_df.empty:
        stays_df.to_excel(stays_path, sheet_name='Estancias', index=False)
        logger.info(f"Datos de estancias guardados en: {stays_path}")
    else:
        stays_path = None
        logger.info("No se generaron datos de estancias.")
    
    return bookings_path, stays_path

def load_sample_data_to_db(bookings_df, stays_df):
    """
    Carga los datos de ejemplo en la base de datos.
    
    Args:
        bookings_df (pandas.DataFrame): DataFrame con los datos de reservas.
        stays_df (pandas.DataFrame): DataFrame con los datos de estancias.
    
    Returns:
        tuple: Tupla con el número de registros cargados (bookings_count, stays_count).
    """
    logger.info("Cargando datos de ejemplo en la base de datos...")
    
    # Crear instancia del servicio de ingesta
    ingestion_service = DataIngestionService()
    
    # Cargar reservas
    bookings_count = 0
    if not bookings_df.empty:
        # Guardar DataFrame en un archivo temporal
        temp_bookings_path = Path("temp_bookings.xlsx")
        bookings_df.to_excel(temp_bookings_path, sheet_name='Reservas', index=False)
        
        # Procesar reservas
        success, message, bookings_count = ingestion_service.process_bookings(temp_bookings_path)
        
        # Eliminar archivo temporal
        if temp_bookings_path.exists():
            os.remove(temp_bookings_path)
        
        if success:
            logger.info(f"Cargados {bookings_count} registros de reservas en la base de datos.")
        else:
            logger.error(f"Error al cargar reservas: {message}")
    
    # Cargar estancias
    stays_count = 0
    if not stays_df.empty:
        # Guardar DataFrame en un archivo temporal
        temp_stays_path = Path("temp_stays.xlsx")
        stays_df.to_excel(temp_stays_path, sheet_name='Estancias', index=False)
        
        # Procesar estancias
        success, message, stays_count = ingestion_service.process_stays(temp_stays_path)
        
        # Eliminar archivo temporal
        if temp_stays_path.exists():
            os.remove(temp_stays_path)
        
        if success:
            logger.info(f"Cargados {stays_count} registros de estancias en la base de datos.")
        else:
            logger.error(f"Error al cargar estancias: {message}")
    
    return bookings_count, stays_count

def main():
    """
    Función principal.
    """
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Generación y carga de datos de ejemplo')
    
    parser.add_argument('--start-date', type=str, default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                        help='Fecha de inicio para los datos (formato YYYY-MM-DD)')
    
    parser.add_argument('--end-date', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                        help='Fecha de fin para los datos (formato YYYY-MM-DD)')
    
    parser.add_argument('--num-bookings', type=int, default=1000,
                        help='Número de reservas a generar')
    
    parser.add_argument('--output-dir', type=str, default=config.get("directories.data_raw"),
                        help='Directorio donde guardar los archivos Excel')
    
    parser.add_argument('--save-only', action='store_true',
                        help='Solo guardar los datos en archivos Excel, sin cargarlos en la base de datos')
    
    parser.add_argument('--load-only', action='store_true',
                        help='Solo cargar los datos en la base de datos, sin generar nuevos datos')
    
    parser.add_argument('--bookings-file', type=str,
                        help='Archivo Excel con datos de reservas a cargar (solo con --load-only)')
    
    parser.add_argument('--stays-file', type=str,
                        help='Archivo Excel con datos de estancias a cargar (solo con --load-only)')
                        
    parser.add_argument('--summary-file', type=str,
                        help='Archivo Excel con datos de resumen diario a cargar (solo con --load-only)')
                        
    parser.add_argument('--occupancy-file', type=str,
                        help='Archivo Excel con datos de ocupación diaria a cargar (solo con --load-only)')
                        
    parser.add_argument('--revenue-file', type=str,
                        help='Archivo Excel con datos de ingresos diarios a cargar (solo con --load-only)')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Convertir fechas a datetime
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    current_date = datetime.now()
    
    # Verificar que la fecha de inicio es anterior a la fecha de fin
    if start_date >= end_date:
        logger.error("La fecha de inicio debe ser anterior a la fecha de fin.")
        return
    
    # Crear copia de seguridad antes de cargar datos
    logger.info("Creando copia de seguridad antes de cargar datos...")
    from scripts.backup_db import create_backup
    backup_path = create_backup("pre_sample_data")
    
    if args.load_only:
        # Cargar datos desde archivos existentes
        if not any([args.bookings_file, args.stays_file, args.summary_file, args.occupancy_file, args.revenue_file]):
            logger.error("Debe especificar al menos un archivo de datos.")
            return
        
        # Cargar reservas
        bookings_df = pd.DataFrame()
        if args.bookings_file:
            bookings_path = Path(args.bookings_file)
            if bookings_path.exists():
                logger.info(f"Cargando reservas desde: {bookings_path}")
                bookings_df = pd.read_excel(bookings_path, sheet_name='Reservas')
            else:
                logger.error(f"El archivo de reservas no existe: {bookings_path}")
        
        # Cargar estancias
        stays_df = pd.DataFrame()
        if args.stays_file:
            stays_path = Path(args.stays_file)
            if stays_path.exists():
                logger.info(f"Cargando estancias desde: {stays_path}")
                stays_df = pd.read_excel(stays_path, sheet_name='Estancias')
            else:
                logger.error(f"El archivo de estancias no existe: {stays_path}")
        
        # Cargar datos de resumen diario
        summary_df = pd.DataFrame()
        if args.summary_file:
            summary_path = Path(args.summary_file)
            if summary_path.exists():
                logger.info(f"Cargando resumen diario desde: {summary_path}")
                summary_df = pd.read_excel(summary_path, sheet_name='Resumen')
            else:
                logger.error(f"El archivo de resumen diario no existe: {summary_path}")
        
        # Cargar datos de ocupación diaria
        occupancy_df = pd.DataFrame()
        if args.occupancy_file:
            occupancy_path = Path(args.occupancy_file)
            if occupancy_path.exists():
                logger.info(f"Cargando ocupación diaria desde: {occupancy_path}")
                occupancy_df = pd.read_excel(occupancy_path, sheet_name='Ocupacion')
            else:
                logger.error(f"El archivo de ocupación diaria no existe: {occupancy_path}")
        
        # Cargar datos de ingresos diarios
        revenue_df = pd.DataFrame()
        if args.revenue_file:
            revenue_path = Path(args.revenue_file)
            if revenue_path.exists():
                logger.info(f"Cargando ingresos diarios desde: {revenue_path}")
                revenue_df = pd.read_excel(revenue_path, sheet_name='Ingresos')
            else:
                logger.error(f"El archivo de ingresos diarios no existe: {revenue_path}")
        
        # Generar reglas de pricing
        rules = generate_pricing_rules()
        
        # Cargar datos en la base de datos
        if any([not df.empty for df in [bookings_df, stays_df, summary_df, occupancy_df, revenue_df]]):
            bookings_count, stays_count = load_sample_data_to_db(bookings_df, stays_df, summary_df, occupancy_df, revenue_df, rules)
            logger.info(f"Carga completada: {bookings_count} reservas, {stays_count} estancias.")
    
    else:
        # Generar datos de ejemplo
        bookings_df = generate_sample_bookings(start_date, end_date, args.num_bookings)
        stays_df = generate_sample_stays(bookings_df, current_date)
        
        # Generar datos adicionales
        summary_df = generate_historical_summary(start_date, end_date, bookings_df, stays_df)
        occupancy_df = generate_daily_occupancy(start_date, end_date, stays_df)
        revenue_df = generate_daily_revenue(start_date, end_date, stays_df)
        rules = generate_pricing_rules()
        
        # Guardar datos en archivos Excel
        file_paths = save_sample_data_to_excel(bookings_df, stays_df, summary_df, occupancy_df, revenue_df, args.output_dir)
        
        # Cargar datos en la base de datos si no se especificó --save-only
        if not args.save_only:
            # Cargar reservas y estancias
            bookings_count, stays_count = load_sample_data_to_db(bookings_df, stays_df, summary_df, occupancy_df, revenue_df, rules)
            logger.info(f"Carga completada: {bookings_count} reservas, {stays_count} estancias.")
        else:
            logger.info("Datos guardados en archivos Excel. No se cargaron en la base de datos.")
    
    logger.info("Proceso completado correctamente.")

if __name__ == "__main__":
    main()