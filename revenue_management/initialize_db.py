#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar la base de datos y crear las tablas
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from db.database import db
from db.schema import schema_manager
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

def initialize_database():
    """
    Inicializa la base de datos y crea las tablas
    """
    try:
        logger.info("Iniciando inicialización de la base de datos")
        
        # Crear tablas
        schema_manager.create_tables()
        
        # Inicializar datos básicos
        schema_manager.initialize_data()
        
        # Crear copia de seguridad inicial
        backup_path = db.create_backup("initial_backup")
        
        if backup_path:
            logger.info(f"Copia de seguridad inicial creada en: {backup_path}")
        
        logger.info("Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        return False

if __name__ == "__main__":
    success = initialize_database()
    
    if success:
        print("Base de datos inicializada correctamente")
        sys.exit(0)
    else:
        print("Error al inicializar la base de datos")
        sys.exit(1)