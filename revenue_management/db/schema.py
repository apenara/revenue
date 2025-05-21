#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para definir el esquema de la base de datos SQLite
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class SchemaManager:
    """
    Clase para gestionar el esquema de la base de datos
    """
    def __init__(self, database=None):
        """
        Inicializa el gestor de esquema.
        
        Args:
            database: Instancia de la base de datos (opcional)
        """
        self.db = database or db
    
    def create_tables(self):
        """
        Crea todas las tablas definidas en el esquema si no existen.
        """
        logger.info("Creando tablas en la base de datos...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Crear tabla ROOM_TYPES (HabitacionesConfig)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ROOM_TYPES (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cod_hab TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                description TEXT,
                amenities TEXT,
                num_config INTEGER NOT NULL
            )
            ''')
            
            # Crear tabla SEASONS
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS SEASONS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_from DATE NOT NULL,
                date_to DATE NOT NULL,
                description TEXT
            )
            ''')
            
            # Crear tabla CHANNELS
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS CHANNELS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                commission_percentage REAL NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1
            )
            ''')
            
            # Crear tabla BASE_RATES
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS BASE_RATES (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_type_id INTEGER NOT NULL,
                season_id INTEGER NOT NULL,
                rate REAL NOT NULL,
                date_from DATE NOT NULL,
                date_to DATE NOT NULL,
                FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id),
                FOREIGN KEY (season_id) REFERENCES SEASONS (id)
            )
            ''')
            
            # Crear tabla RAW_BOOKINGS (ReservasBrutas)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS RAW_BOOKINGS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registro_num TEXT,
                fecha_reserva DATE NOT NULL,
                fecha_llegada DATE NOT NULL,
                fecha_salida DATE NOT NULL,
                noches INTEGER NOT NULL,
                cod_hab TEXT NOT NULL,
                tipo_habitacion TEXT NOT NULL,
                tarifa_neta REAL NOT NULL,
                canal_distribucion TEXT NOT NULL,
                nombre_cliente TEXT,
                email_cliente TEXT,
                telefono_cliente TEXT,
                estado_reserva TEXT NOT NULL,
                observaciones TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cod_hab) REFERENCES ROOM_TYPES (cod_hab)
            )
            ''')
            
            # Crear tabla RAW_STAYS (EstanciasBrutas)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS RAW_STAYS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registro_num TEXT NOT NULL,
                fecha_checkin DATE NOT NULL,
                fecha_checkout DATE NOT NULL,
                noches INTEGER NOT NULL,
                cod_hab TEXT NOT NULL,
                tipo_habitacion TEXT NOT NULL,
                valor_venta REAL NOT NULL,
                canal_distribucion TEXT NOT NULL,
                nombre_cliente TEXT NOT NULL,
                email_cliente TEXT,
                telefono_cliente TEXT,
                estado_estancia TEXT NOT NULL,
                observaciones TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cod_hab) REFERENCES ROOM_TYPES (cod_hab)
            )
            ''')
            
            # Crear tabla HISTORICAL_SUMMARY (ResumenDiarioHistorico)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS HISTORICAL_SUMMARY (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                habitaciones_disponibles INTEGER NOT NULL,
                habitaciones_ocupadas INTEGER NOT NULL,
                ingresos_totales REAL NOT NULL,
                adr REAL,
                revpar REAL,
                ocupacion_porcentaje REAL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Crear tabla DAILY_OCCUPANCY (OcupacionDiaria)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS DAILY_OCCUPANCY (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                room_type_id INTEGER NOT NULL,
                habitaciones_disponibles INTEGER NOT NULL,
                habitaciones_ocupadas INTEGER NOT NULL,
                ocupacion_porcentaje REAL NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id)
            )
            ''')
            
            # Crear tabla DAILY_REVENUE (IngresosDiarios)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS DAILY_REVENUE (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                room_type_id INTEGER NOT NULL,
                ingresos REAL NOT NULL,
                adr REAL NOT NULL,
                revpar REAL NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id)
            )
            ''')
            
            # Crear tabla RULE_CONFIGS (ParametrosReglas)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS RULE_CONFIGS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                parametros TEXT NOT NULL,
                prioridad INTEGER NOT NULL,
                activa BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Crear tabla FORECASTS (Previsiones)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS FORECASTS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                room_type_id INTEGER NOT NULL,
                ocupacion_prevista REAL NOT NULL,
                adr_previsto REAL NOT NULL,
                revpar_previsto REAL NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ajustado_manualmente BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id)
            )
            ''')
            
            # Crear tabla APPROVED_RECOMMENDATIONS (Recomendaciones_Aprobadas)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS APPROVED_RECOMMENDATIONS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                room_type_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                tarifa_base REAL NOT NULL,
                tarifa_recomendada REAL NOT NULL,
                tarifa_aprobada REAL NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Aprobada',
                exportado BOOLEAN NOT NULL DEFAULT 0,
                exportado_at TIMESTAMP,
                FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id),
                FOREIGN KEY (channel_id) REFERENCES CHANNELS (id)
            )
            ''')
            
            conn.commit()
            logger.info("Tablas creadas exitosamente")
    
    def initialize_data(self):
        """
        Inicializa datos básicos en la base de datos.
        """
        logger.info("Inicializando datos básicos...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insertar tipos de habitación básicos
            room_types = [
                ('EST', 'Estándar Triple', 3, 'Habitación estándar con capacidad para 3 personas', 'WiFi, TV, Aire acondicionado', 14),
                ('JRS', 'Junior Suite', 5, 'Junior suite con capacidad para 5 personas', 'WiFi, TV, Aire acondicionado, Minibar, Balcón', 4),
                ('ESC', 'Estándar Cuádruple', 4, 'Habitación estándar con capacidad para 4 personas', 'WiFi, TV, Aire acondicionado', 26),
                ('ESD', 'Estándar Doble', 2, 'Habitación estándar con capacidad para 2 personas', 'WiFi, TV, Aire acondicionado', 7),
                ('SUI', 'Suite', 2, 'Suite con capacidad para 2 personas', 'WiFi, TV, Aire acondicionado, Minibar, Balcón, Jacuzzi', 1),
                ('KSP', 'King Superior', 2, 'Habitación king superior con capacidad para 2 personas', 'WiFi, TV, Aire acondicionado, Minibar', 12),
                ('DSP', 'Doble Superior', 2, 'Habitación doble superior con capacidad para 2 personas', 'WiFi, TV, Aire acondicionado, Minibar', 15)
            ]
            
            cursor.executemany('''
            INSERT OR IGNORE INTO ROOM_TYPES (cod_hab, name, capacity, description, amenities, num_config)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', room_types)
            
            # Insertar canales de distribución básicos
            channels = [
                ('Directo', 0.0, 1),
                ('Booking.com', 0.15, 1),
                ('Expedia', 0.18, 1),
                ('Hotelbeds', 0.20, 1),
                ('Despegar', 0.17, 1)
            ]
            
            cursor.executemany('''
            INSERT OR IGNORE INTO CHANNELS (name, commission_percentage, is_active)
            VALUES (?, ?, ?)
            ''', channels)
            
            # Insertar temporadas básicas
            current_year = datetime.now().year
            seasons = [
                ('Alta', f'{current_year}-12-01', f'{current_year}-01-31', 'Temporada alta de diciembre y enero'),
                ('Alta', f'{current_year}-06-15', f'{current_year}-08-31', 'Temporada alta de verano'),
                ('Media', f'{current_year}-02-01', f'{current_year}-03-31', 'Temporada media de febrero y marzo'),
                ('Media', f'{current_year}-09-01', f'{current_year}-10-31', 'Temporada media de septiembre y octubre'),
                ('Baja', f'{current_year}-04-01', f'{current_year}-06-14', 'Temporada baja de abril a mediados de junio'),
                ('Baja', f'{current_year}-11-01', f'{current_year}-11-30', 'Temporada baja de noviembre')
            ]
            
            cursor.executemany('''
            INSERT OR IGNORE INTO SEASONS (name, date_from, date_to, description)
            VALUES (?, ?, ?, ?)
            ''', seasons)
            
            # Insertar reglas básicas
            rules = [
                ('Ocupación Alta', 'Aumentar tarifa cuando la ocupación prevista es alta',
                 json.dumps({'ocupacion_umbral': 0.8, 'factor_aumento': 1.15, 'canales_aplicables': ['Booking.com', 'Expedia', 'Hotelbeds', 'Despegar']}),
                 1, 1),
                ('Ocupación Baja', 'Disminuir tarifa cuando la ocupación prevista es baja',
                 json.dumps({'ocupacion_umbral': 0.4, 'factor_reduccion': 0.9, 'canales_aplicables': ['Booking.com', 'Expedia', 'Hotelbeds', 'Despegar', 'Directo']}),
                 2, 1),
                ('Temporada Alta', 'Ajuste adicional para temporada alta',
                 json.dumps({'temporada': 'Alta', 'factor_aumento': 1.1, 'canales_aplicables': ['Booking.com', 'Expedia', 'Hotelbeds', 'Despegar']}),
                 3, 1),
                ('Canal Directo', 'Descuento para reservas directas',
                 json.dumps({'canal': 'Directo', 'factor_reduccion': 0.95, 'minimo_noches': 2}),
                 4, 1)
            ]
            
            cursor.executemany('''
            INSERT OR IGNORE INTO RULE_CONFIGS (nombre, descripcion, parametros, prioridad, activa)
            VALUES (?, ?, ?, ?, ?)
            ''', rules)
            
            conn.commit()
            logger.info("Datos básicos inicializados exitosamente")

# Instancia global del gestor de esquema
schema_manager = SchemaManager()