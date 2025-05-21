#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para gestionar las conexiones a la base de datos SQLite
"""

import os
import sqlite3
import shutil
import datetime
from pathlib import Path
from contextlib import contextmanager

from config import config
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class Database:
    """
    Clase para gestionar las conexiones a la base de datos SQLite
    """
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        self.db_path = self._get_db_path()
        self.backup_dir = self._get_backup_dir()
        self.connection = None
        
    def _get_db_path(self):
        """
        Obtiene la ruta de la base de datos desde la configuración
        y crea el directorio si no existe.
        
        Returns:
            Path: Ruta absoluta al archivo de base de datos
        """
        db_path_str = config.get("database.path", "db/revenue_management.db")
        base_dir = Path(__file__).parent.parent
        db_path = base_dir / db_path_str
        
        # Crear directorio si no existe
        db_dir = db_path.parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
            
        return db_path
    
    def _get_backup_dir(self):
        """
        Obtiene la ruta del directorio de copias de seguridad desde la configuración
        y crea el directorio si no existe.
        
        Returns:
            Path: Ruta absoluta al directorio de copias de seguridad
        """
        backup_dir_str = config.get("database.backup_dir", "db/backups")
        base_dir = Path(__file__).parent.parent
        backup_dir = base_dir / backup_dir_str
        
        # Crear directorio si no existe
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
            
        return backup_dir
    
    def connect(self):
        """
        Establece una conexión a la base de datos.
        
        Returns:
            sqlite3.Connection: Objeto de conexión a la base de datos
        """
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
            
            # Habilitar claves foráneas
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"Conexión establecida a la base de datos: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Conexión a la base de datos cerrada")
    
    @contextmanager
    def get_connection(self):
        """
        Contexto para gestionar la conexión a la base de datos.
        
        Yields:
            sqlite3.Connection: Objeto de conexión a la base de datos
        """
        conn = self.connect()
        try:
            yield conn
        finally:
            self.close()
    
    @contextmanager
    def get_cursor(self):
        """
        Contexto para gestionar el cursor de la base de datos.
        
        Yields:
            sqlite3.Cursor: Cursor para ejecutar consultas
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error en la transacción: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL y devuelve los resultados.
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple, optional): Parámetros para la consulta
            
        Returns:
            list: Lista de filas resultantes
        """
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_many(self, query, params_list):
        """
        Ejecuta una consulta SQL con múltiples conjuntos de parámetros.
        
        Args:
            query (str): Consulta SQL a ejecutar
            params_list (list): Lista de tuplas con parámetros
            
        Returns:
            int: Número de filas afectadas
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def create_backup(self, backup_name=None):
        """
        Crea una copia de seguridad de la base de datos.
        
        Args:
            backup_name (str, optional): Nombre personalizado para la copia de seguridad.
                Si no se proporciona, se utilizará la fecha y hora actual.
                
        Returns:
            Path: Ruta a la copia de seguridad creada
        """
        if not self.db_path.exists():
            logger.error("No se puede crear una copia de seguridad: la base de datos no existe")
            return None
        
        # Generar nombre de la copia de seguridad
        if not backup_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
        elif not backup_name.endswith('.db'):
            backup_name = f"{backup_name}.db"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            # Cerrar la conexión si está abierta
            if self.connection:
                self.close()
            
            # Copiar el archivo de la base de datos
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Copia de seguridad creada exitosamente: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error al crear la copia de seguridad: {e}")
            return None
    
    def restore_backup(self, backup_path):
        """
        Restaura una copia de seguridad de la base de datos.
        
        Args:
            backup_path (str): Ruta a la copia de seguridad a restaurar
            
        Returns:
            bool: True si la restauración fue exitosa, False en caso contrario
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            logger.error(f"No se puede restaurar la copia de seguridad: {backup_path} no existe")
            return False
        
        try:
            # Cerrar la conexión si está abierta
            if self.connection:
                self.close()
            
            # Crear una copia de seguridad de la base de datos actual antes de restaurar
            current_backup = self.create_backup("pre_restore_backup")
            
            # Copiar la copia de seguridad sobre la base de datos actual
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Copia de seguridad restaurada exitosamente desde: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error al restaurar la copia de seguridad: {e}")
            return False
    
    def list_backups(self):
        """
        Lista todas las copias de seguridad disponibles.
        
        Returns:
            list: Lista de rutas a las copias de seguridad
        """
        try:
            backups = list(self.backup_dir.glob("*.db"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)  # Ordenar por fecha de modificación
            return backups
        except Exception as e:
            logger.error(f"Error al listar las copias de seguridad: {e}")
            return []
    
    def create_tables(self):
        """
        Crea las tablas de la base de datos si no existen.
        Este método debe ser implementado por las subclases.
        """
        raise NotImplementedError("Este método debe ser implementado por las subclases")
    
    def initialize_database(self):
        """
        Inicializa la base de datos creando las tablas y los datos iniciales.
        Este método debe ser implementado por las subclases.
        """
        raise NotImplementedError("Este método debe ser implementado por las subclases")

# Instancia global de la base de datos
db = Database()