#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para realizar copias de seguridad de la base de datos del Framework de Revenue Management.
Puede ejecutarse manualmente o programarse como tarea periódica.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import db
from config import config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(config.get("logging.file")))
    ]
)
logger = logging.getLogger("backup_db")

def create_backup(name=None):
    """
    Crea una copia de seguridad de la base de datos.
    
    Args:
        name (str, optional): Nombre personalizado para la copia de seguridad.
            Si no se proporciona, se utiliza la fecha y hora actual.
    
    Returns:
        Path: Ruta a la copia de seguridad creada.
    """
    try:
        # Crear copia de seguridad
        backup_path = db.create_backup(name)
        
        logger.info(f"Copia de seguridad creada correctamente en: {backup_path}")
        return backup_path
    
    except Exception as e:
        logger.error(f"Error al crear la copia de seguridad: {str(e)}")
        return None

def list_backups():
    """
    Lista todas las copias de seguridad disponibles.
    
    Returns:
        list: Lista de rutas a las copias de seguridad.
    """
    try:
        # Obtener lista de copias de seguridad
        backups = db.list_backups()
        
        if not backups:
            logger.info("No hay copias de seguridad disponibles.")
            return []
        
        # Mostrar información de cada copia de seguridad
        logger.info(f"Se encontraron {len(backups)} copias de seguridad:")
        for i, backup in enumerate(backups, 1):
            # Obtener información del archivo
            size_mb = backup.stat().st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"{i}. {backup.name} - Tamaño: {size_mb:.2f} MB - Fecha: {modified}")
        
        return backups
    
    except Exception as e:
        logger.error(f"Error al listar las copias de seguridad: {str(e)}")
        return []

def restore_backup(backup_path):
    """
    Restaura una copia de seguridad.
    
    Args:
        backup_path (str/Path): Ruta a la copia de seguridad a restaurar.
    
    Returns:
        bool: True si la restauración fue exitosa, False en caso contrario.
    """
    try:
        # Convertir a Path si es una cadena
        if isinstance(backup_path, str):
            backup_path = Path(backup_path)
        
        # Verificar que el archivo existe
        if not backup_path.exists():
            logger.error(f"La copia de seguridad no existe: {backup_path}")
            return False
        
        # Crear una copia de seguridad antes de restaurar
        logger.info("Creando copia de seguridad antes de restaurar...")
        pre_restore_backup = db.create_backup("pre_restore")
        
        # Restaurar copia de seguridad
        success = db.restore_backup(backup_path)
        
        if success:
            logger.info(f"Copia de seguridad restaurada correctamente: {backup_path}")
        else:
            logger.error(f"Error al restaurar la copia de seguridad: {backup_path}")
            logger.info(f"Se puede restaurar la copia de seguridad previa: {pre_restore_backup}")
        
        return success
    
    except Exception as e:
        logger.error(f"Error al restaurar la copia de seguridad: {str(e)}")
        return False

def cleanup_old_backups(max_backups=10):
    """
    Elimina copias de seguridad antiguas, manteniendo solo las más recientes.
    
    Args:
        max_backups (int, optional): Número máximo de copias de seguridad a mantener.
            Por defecto, se mantienen las 10 más recientes.
    
    Returns:
        int: Número de copias de seguridad eliminadas.
    """
    try:
        # Obtener lista de copias de seguridad
        backups = db.list_backups()
        
        if not backups:
            logger.info("No hay copias de seguridad para limpiar.")
            return 0
        
        # Ordenar por fecha de modificación (más reciente primero)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Mantener solo las más recientes
        backups_to_delete = backups[max_backups:]
        
        if not backups_to_delete:
            logger.info(f"No hay copias de seguridad antiguas para eliminar. Manteniendo {len(backups)} copias.")
            return 0
        
        # Eliminar copias antiguas
        deleted_count = 0
        for backup in backups_to_delete:
            try:
                os.remove(backup)
                deleted_count += 1
                logger.info(f"Eliminada copia de seguridad antigua: {backup}")
            except Exception as e:
                logger.error(f"Error al eliminar copia de seguridad {backup}: {str(e)}")
        
        logger.info(f"Se eliminaron {deleted_count} copias de seguridad antiguas. Manteniendo {len(backups) - deleted_count} copias.")
        return deleted_count
    
    except Exception as e:
        logger.error(f"Error al limpiar copias de seguridad antiguas: {str(e)}")
        return 0

def main():
    """
    Función principal.
    """
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Gestión de copias de seguridad de la base de datos')
    
    # Definir subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Subcomando para crear copia de seguridad
    create_parser = subparsers.add_parser('create', help='Crear una copia de seguridad')
    create_parser.add_argument('--name', help='Nombre personalizado para la copia de seguridad')
    
    # Subcomando para listar copias de seguridad
    subparsers.add_parser('list', help='Listar copias de seguridad disponibles')
    
    # Subcomando para restaurar copia de seguridad
    restore_parser = subparsers.add_parser('restore', help='Restaurar una copia de seguridad')
    restore_parser.add_argument('--path', required=True, help='Ruta a la copia de seguridad a restaurar')
    
    # Subcomando para restaurar la copia de seguridad más reciente
    subparsers.add_parser('restore-latest', help='Restaurar la copia de seguridad más reciente')
    
    # Subcomando para limpiar copias de seguridad antiguas
    cleanup_parser = subparsers.add_parser('cleanup', help='Eliminar copias de seguridad antiguas')
    cleanup_parser.add_argument('--max', type=int, default=10, help='Número máximo de copias de seguridad a mantener')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar comando correspondiente
    if args.command == 'create':
        create_backup(args.name)
    
    elif args.command == 'list':
        list_backups()
    
    elif args.command == 'restore':
        restore_backup(args.path)
    
    elif args.command == 'restore-latest':
        backups = list_backups()
        if backups:
            # Ordenar por fecha de modificación (más reciente primero)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            latest_backup = backups[0]
            logger.info(f"Restaurando la copia de seguridad más reciente: {latest_backup}")
            restore_backup(latest_backup)
        else:
            logger.error("No hay copias de seguridad disponibles para restaurar.")
    
    elif args.command == 'cleanup':
        cleanup_old_backups(args.max)
    
    else:
        # Si no se especifica un comando, mostrar ayuda
        parser.print_help()

if __name__ == "__main__":
    main()