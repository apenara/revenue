#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar la base de datos del Framework de Revenue Management.
Crea las tablas necesarias y carga datos iniciales.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import db
from config import config
from models.room import Room
from models.rule import Rule

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(config.get("logging.file")))
    ]
)
logger = logging.getLogger("initialize_db")

def create_tables():
    """
    Crea las tablas en la base de datos.
    """
    logger.info("Creando tablas en la base de datos...")
    
    # Crear tabla de tipos de habitación
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS ROOM_TYPES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cod_hab TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        description TEXT,
        amenities TEXT,
        num_config INTEGER NOT NULL
    )
    """)
    
    # Crear tabla de temporadas
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS SEASONS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date_from TEXT NOT NULL,
        date_to TEXT NOT NULL,
        description TEXT
    )
    """)
    
    # Crear tabla de canales
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS CHANNELS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        commission_percentage REAL NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1
    )
    """)
    
    # Crear tabla de tarifas base
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS BASE_RATES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_type_id INTEGER NOT NULL,
        season_id INTEGER NOT NULL,
        rate REAL NOT NULL,
        date_from TEXT NOT NULL,
        date_to TEXT NOT NULL,
        FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id),
        FOREIGN KEY (season_id) REFERENCES SEASONS (id)
    )
    """)
    
    # Crear tabla de reservas importadas
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS RAW_BOOKINGS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registro_num TEXT,
        fecha_reserva TEXT NOT NULL,
        fecha_llegada TEXT NOT NULL,
        fecha_salida TEXT NOT NULL,
        noches INTEGER NOT NULL,
        cod_hab TEXT NOT NULL,
        tipo_habitacion TEXT,
        tarifa_neta REAL NOT NULL,
        canal_distribucion TEXT,
        nombre_cliente TEXT,
        email_cliente TEXT,
        telefono_cliente TEXT,
        estado_reserva TEXT,
        observaciones TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cod_hab) REFERENCES ROOM_TYPES (cod_hab)
    )
    """)
    
    # Crear tabla de estancias importadas
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS RAW_STAYS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registro_num TEXT,
        fecha_checkin TEXT NOT NULL,
        fecha_checkout TEXT NOT NULL,
        noches INTEGER NOT NULL,
        cod_hab TEXT NOT NULL,
        tipo_habitacion TEXT,
        valor_venta REAL NOT NULL,
        canal_distribucion TEXT,
        nombre_cliente TEXT,
        email_cliente TEXT,
        telefono_cliente TEXT,
        estado_estancia TEXT,
        observaciones TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cod_hab) REFERENCES ROOM_TYPES (cod_hab)
    )
    """)
    
    # Crear tabla de resumen histórico
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS HISTORICAL_SUMMARY (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        habitaciones_disponibles INTEGER NOT NULL,
        habitaciones_ocupadas INTEGER NOT NULL,
        ingresos_totales REAL NOT NULL,
        adr REAL NOT NULL,
        revpar REAL NOT NULL,
        ocupacion_porcentaje REAL NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Crear tabla de ocupación diaria
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS DAILY_OCCUPANCY (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        room_type_id INTEGER NOT NULL,
        habitaciones_disponibles INTEGER NOT NULL,
        habitaciones_ocupadas INTEGER NOT NULL,
        ocupacion_porcentaje REAL NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id)
    )
    """)
    
    # Crear tabla de ingresos diarios
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS DAILY_REVENUE (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        room_type_id INTEGER NOT NULL,
        ingresos REAL NOT NULL,
        adr REAL NOT NULL,
        revpar REAL NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id)
    )
    """)
    
    # Crear tabla de configuración de reglas
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS RULE_CONFIGS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        parametros TEXT NOT NULL,
        prioridad INTEGER NOT NULL,
        activa INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Crear tabla de previsiones
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS FORECASTS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        room_type_id INTEGER NOT NULL,
        ocupacion_prevista REAL NOT NULL,
        adr_previsto REAL,
        revpar_previsto REAL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ajustado_manualmente INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id)
    )
    """)
    
    # Crear tabla de recomendaciones aprobadas
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS APPROVED_RECOMMENDATIONS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        room_type_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        tarifa_base REAL NOT NULL,
        tarifa_recomendada REAL NOT NULL,
        tarifa_aprobada REAL NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        approved_at TEXT,
        estado TEXT NOT NULL DEFAULT 'Pendiente',
        exportado INTEGER NOT NULL DEFAULT 0,
        exportado_at TEXT,
        FOREIGN KEY (room_type_id) REFERENCES ROOM_TYPES (id),
        FOREIGN KEY (channel_id) REFERENCES CHANNELS (id)
    )
    """)
    
    # Crear tabla de usuarios
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS USERS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        role TEXT NOT NULL DEFAULT 'user',
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login TEXT
    )
    """)
    
    # Crear índices para mejorar el rendimiento
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_room_types_cod_hab ON ROOM_TYPES (cod_hab)")
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_raw_bookings_fechas ON RAW_BOOKINGS (fecha_llegada, fecha_salida)")
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_raw_stays_fechas ON RAW_STAYS (fecha_checkin, fecha_checkout)")
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_daily_occupancy_fecha_room ON DAILY_OCCUPANCY (fecha, room_type_id)")
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_daily_revenue_fecha_room ON DAILY_REVENUE (fecha, room_type_id)")
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_forecasts_fecha_room ON FORECASTS (fecha, room_type_id)")
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_approved_recommendations_fecha_room_channel ON APPROVED_RECOMMENDATIONS (fecha, room_type_id, channel_id)")
    
    logger.info("Tablas creadas correctamente.")

def load_initial_data():
    """
    Carga datos iniciales en la base de datos.
    """
    logger.info("Cargando datos iniciales...")
    
    # Cargar tipos de habitación
    room_types = config.get("room_types")
    for room_type in room_types:
        room = Room(
            cod_hab=room_type["code"],
            name=room_type["name"],
            capacity=room_type["capacity"],
            num_config=room_type["count"]
        )
        room.save()
    
    # Cargar canales
    channels = config.get("channels")
    for channel in channels:
        db.execute_query(
            "INSERT INTO CHANNELS (name, commission_percentage, is_active) VALUES (?, ?, ?)",
            (channel["name"], channel["commission"], channel["active"])
        )
    
    # Cargar temporadas
    seasons = config.get("seasons")
    current_year = datetime.now().year
    for season in seasons:
        # Crear temporada para el año actual
        db.execute_query(
            "INSERT INTO SEASONS (name, date_from, date_to, description) VALUES (?, ?, ?, ?)",
            (
                season["name"],
                f"{current_year}-{min(season['months']):02d}-01",
                f"{current_year}-{max(season['months']):02d}-28",
                f"Temporada {season['name']} {current_year}"
            )
        )
        
        # Crear temporada para el año siguiente
        db.execute_query(
            "INSERT INTO SEASONS (name, date_from, date_to, description) VALUES (?, ?, ?, ?)",
            (
                season["name"],
                f"{current_year+1}-{min(season['months']):02d}-01",
                f"{current_year+1}-{max(season['months']):02d}-28",
                f"Temporada {season['name']} {current_year+1}"
            )
        )
    
    # Cargar reglas de pricing por defecto
    create_default_rules()
    
    # Crear usuario administrador por defecto
    db.execute_query(
        "INSERT INTO USERS (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
        ("admin", "admin123", "Administrador", "admin@hotelplayaclub.com", "admin")
    )
    
    logger.info("Datos iniciales cargados correctamente.")

def create_default_rules():
    """
    Crea reglas de pricing por defecto.
    """
    logger.info("Creando reglas de pricing por defecto...")
    
    # Regla de temporada
    season_rule = Rule(
        nombre="Regla de Temporada",
        descripcion="Ajusta tarifas según la temporada",
        parametros={
            "tipo": "temporada",
            "factores": {
                "Baja": 0.9,
                "Media": 1.0,
                "Alta": 1.2
            }
        },
        prioridad=1,
        activa=True
    )
    season_rule.save()
    
    # Regla de ocupación
    occupancy_rule = Rule(
        nombre="Regla de Ocupación",
        descripcion="Ajusta tarifas según la ocupación prevista",
        parametros={
            "tipo": "ocupacion",
            "umbrales": {
                "bajo": config.get("pricing.min_occupancy_threshold"),
                "alto": config.get("pricing.max_occupancy_threshold")
            },
            "factores": {
                "bajo": config.get("pricing.low_occupancy_factor"),
                "medio": 1.0,
                "alto": config.get("pricing.high_occupancy_factor")
            }
        },
        prioridad=2,
        activa=True
    )
    occupancy_rule.save()
    
    # Regla de canal
    channel_factors = []
    for channel in config.get("channels"):
        factor = 1.0
        if channel["name"] != "Directo":
            # Añadir un factor para compensar la comisión
            factor = 1.0 + channel["commission"]
        
        channel_factors.append({
            "canal": channel["name"],
            "factor": factor
        })
    
    channel_rule = Rule(
        nombre="Regla de Canal",
        descripcion="Ajusta tarifas según el canal de distribución",
        parametros={
            "tipo": "canal",
            "factores": channel_factors
        },
        prioridad=3,
        activa=True
    )
    channel_rule.save()
    
    # Regla de día de semana
    weekday_rule = Rule(
        nombre="Regla de Día de Semana",
        descripcion="Ajusta tarifas según el día de la semana",
        parametros={
            "tipo": "dia_semana",
            "factores": {
                "0": 0.9,  # Lunes
                "1": 0.9,  # Martes
                "2": 0.9,  # Miércoles
                "3": 0.95, # Jueves
                "4": 1.1,  # Viernes
                "5": 1.2,  # Sábado
                "6": 1.0   # Domingo
            }
        },
        prioridad=4,
        activa=True
    )
    weekday_rule.save()
    
    logger.info("Reglas de pricing creadas correctamente.")

def create_directories():
    """
    Crea los directorios necesarios para el funcionamiento del sistema.
    """
    logger.info("Creando directorios...")
    
    # Crear directorios de datos
    os.makedirs(config.get("directories.data_raw"), exist_ok=True)
    os.makedirs(config.get("directories.data_processed"), exist_ok=True)
    os.makedirs(config.get("directories.data_exports"), exist_ok=True)
    os.makedirs(config.get("directories.templates"), exist_ok=True)
    
    # Crear directorio de copias de seguridad
    os.makedirs(config.get("database.backup_dir"), exist_ok=True)
    
    # Crear directorio de logs
    os.makedirs(os.path.dirname(config.get("logging.file")), exist_ok=True)
    
    logger.info("Directorios creados correctamente.")

def main():
    """
    Función principal.
    """
    logger.info("Iniciando inicialización de la base de datos...")
    
    # Crear directorios
    create_directories()
    
    # Crear tablas
    create_tables()
    
    # Cargar datos iniciales
    load_initial_data()
    
    # Crear copia de seguridad inicial
    if config.get("database.backup_on_startup"):
        backup_path = db.create_backup("initial_backup")
        logger.info(f"Copia de seguridad inicial creada en: {backup_path}")
    
    logger.info("Inicialización de la base de datos completada correctamente.")

if __name__ == "__main__":
    main()