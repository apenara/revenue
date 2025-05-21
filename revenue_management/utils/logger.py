#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para configurar el sistema de logging
"""

import logging
import os
from pathlib import Path

def setup_logger(name):
    """
    Configura y retorna un logger con el nombre especificado.
    
    Args:
        name (str): Nombre del logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Crear directorio de logs si no existe
    log_dir = Path(__file__).parent.parent / "logs"
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar el logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Crear manejador de archivo
    log_file = log_dir / "app.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Crear manejador de consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Crear formato
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar manejadores al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger