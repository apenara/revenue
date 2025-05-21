#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define el modelo para los parámetros de reglas
"""

import json
from datetime import datetime
from models.base_model import BaseModel
from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class Rule(BaseModel):
    """
    Modelo para los parámetros de reglas (RULE_CONFIGS)
    """
    
    def __init__(self, id=None, nombre=None, descripcion=None, parametros=None, 
                 prioridad=None, activa=True, created_at=None, updated_at=None):
        """
        Inicializa una instancia de Rule.
        
        Args:
            id (int, optional): ID del registro
            nombre (str): Nombre de la regla
            descripcion (str, optional): Descripción de la regla
            parametros (dict/str): Parámetros de la regla (como diccionario o JSON)
            prioridad (int): Prioridad de la regla
            activa (bool, optional): Indica si la regla está activa
            created_at (str/datetime, optional): Fecha de creación del registro
            updated_at (str/datetime, optional): Fecha de actualización del registro
        """
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.parametros = self._parse_parametros(parametros)
        self.prioridad = prioridad
        self.activa = activa
        self.created_at = self._parse_date(created_at) if created_at else datetime.now()
        self.updated_at = self._parse_date(updated_at) if updated_at else datetime.now()
    
    def _parse_date(self, date_value):
        """
        Convierte un valor de fecha a objeto datetime.
        
        Args:
            date_value: Valor de fecha (str, datetime, None)
            
        Returns:
            datetime: Objeto datetime o None si el valor es None
        """
        if date_value is None:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        try:
            # Intentar diferentes formatos de fecha
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
            
            # Si no se pudo convertir con ningún formato
            logger.warning(f"No se pudo convertir la fecha: {date_value}")
            return None
        except Exception as e:
            logger.error(f"Error al convertir la fecha: {e}")
            return None
    
    def _format_date(self, date_value):
        """
        Formatea un objeto datetime como string en formato YYYY-MM-DD.
        
        Args:
            date_value (datetime): Objeto datetime
            
        Returns:
            str: Fecha formateada o None si el valor es None
        """
        if date_value is None:
            return None
        
        return date_value.strftime('%Y-%m-%d')
    
    def _format_datetime(self, date_value):
        """
        Formatea un objeto datetime como string en formato YYYY-MM-DD HH:MM:SS.
        
        Args:
            date_value (datetime): Objeto datetime
            
        Returns:
            str: Fecha y hora formateadas o None si el valor es None
        """
        if date_value is None:
            return None
        
        return date_value.strftime('%Y-%m-%d %H:%M:%S')
    
    def _parse_parametros(self, parametros):
        """
        Convierte los parámetros a un diccionario.
        
        Args:
            parametros: Parámetros (dict, str, None)
            
        Returns:
            dict: Diccionario de parámetros o diccionario vacío si el valor es None
        """
        if parametros is None:
            return {}
        
        if isinstance(parametros, dict):
            return parametros
        
        try:
            return json.loads(parametros)
        except Exception as e:
            logger.error(f"Error al convertir los parámetros a diccionario: {e}")
            return {}
    
    def _format_parametros(self):
        """
        Convierte los parámetros a una cadena JSON.
        
        Returns:
            str: Cadena JSON de los parámetros
        """
        try:
            return json.dumps(self.parametros, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error al convertir los parámetros a JSON: {e}")
            return "{}"
    
    @classmethod
    def from_row(cls, row):
        """
        Crea una instancia de Rule a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            Rule: Instancia de Rule
        """
        if not row:
            return None
        
        return cls(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'],
            parametros=row['parametros'],
            prioridad=row['prioridad'],
            activa=bool(row['activa']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Rule a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del registro
            
        Returns:
            Rule: Instancia de Rule
        """
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            parametros=data.get('parametros'),
            prioridad=data.get('prioridad'),
            activa=data.get('activa', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """
        Convierte la instancia de Rule a un diccionario.
        
        Returns:
            dict: Diccionario con los datos del registro
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'parametros': self.parametros,
            'prioridad': self.prioridad,
            'activa': self.activa,
            'created_at': self._format_datetime(self.created_at),
            'updated_at': self._format_datetime(self.updated_at)
        }
    
    def save(self):
        """
        Guarda el registro en la base de datos.
        Si el registro ya existe (tiene id), lo actualiza.
        Si no existe, lo crea.
        
        Returns:
            int: ID del registro guardado
        """
        try:
            # Actualizar la fecha de actualización
            self.updated_at = datetime.now()
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.id:
                    # Actualizar registro existente
                    cursor.execute('''
                    UPDATE RULE_CONFIGS
                    SET nombre = ?, descripcion = ?, parametros = ?,
                        prioridad = ?, activa = ?, updated_at = ?
                    WHERE id = ?
                    ''', (
                        self.nombre, self.descripcion, self._format_parametros(),
                        self.prioridad, int(self.activa), self._format_datetime(self.updated_at),
                        self.id
                    ))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No se encontró el registro con ID {self.id} para actualizar")
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                    INSERT INTO RULE_CONFIGS (
                        nombre, descripcion, parametros,
                        prioridad, activa, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self.nombre, self.descripcion, self._format_parametros(),
                        self.prioridad, int(self.activa),
                        self._format_datetime(self.created_at),
                        self._format_datetime(self.updated_at)
                    ))
                    
                    self.id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Regla guardada con ID {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"Error al guardar la regla: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene un registro por su ID.
        
        Args:
            id (int): ID del registro a obtener
            
        Returns:
            Rule: Instancia de Rule o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RULE_CONFIGS WHERE id = ?', (id,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la regla con ID {id}: {e}")
            return None
    
    @classmethod
    def get_by_name(cls, nombre):
        """
        Obtiene un registro por su nombre.
        
        Args:
            nombre (str): Nombre de la regla a obtener
            
        Returns:
            Rule: Instancia de Rule o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RULE_CONFIGS WHERE nombre = ?', (nombre,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la regla con nombre {nombre}: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todos los registros.
        
        Returns:
            list: Lista de instancias de Rule
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RULE_CONFIGS ORDER BY prioridad')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener todas las reglas: {e}")
            return []
    
    @classmethod
    def get_active_rules(cls):
        """
        Obtiene todas las reglas activas.
        
        Returns:
            list: Lista de instancias de Rule
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM RULE_CONFIGS WHERE activa = 1 ORDER BY prioridad')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener las reglas activas: {e}")
            return []
    
    @classmethod
    def delete(cls, id):
        """
        Elimina un registro por su ID.
        
        Args:
            id (int): ID del registro a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM RULE_CONFIGS WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar la regla con ID {id}: {e}")
            return False
    
    def activate(self):
        """
        Activa la regla.
        
        Returns:
            bool: True si se activó correctamente, False en caso contrario
        """
        try:
            self.activa = True
            self.updated_at = datetime.now()
            self.save()
            return True
        except Exception as e:
            logger.error(f"Error al activar la regla: {e}")
            return False
    
    def deactivate(self):
        """
        Desactiva la regla.
        
        Returns:
            bool: True si se desactivó correctamente, False en caso contrario
        """
        try:
            self.activa = False
            self.updated_at = datetime.now()
            self.save()
            return True
        except Exception as e:
            logger.error(f"Error al desactivar la regla: {e}")
            return False
    
    def update_parametros(self, parametros):
        """
        Actualiza los parámetros de la regla.
        
        Args:
            parametros (dict): Nuevos parámetros
            
        Returns:
            bool: True si se actualizaron correctamente, False en caso contrario
        """
        try:
            self.parametros = parametros
            self.updated_at = datetime.now()
            self.save()
            return True
        except Exception as e:
            logger.error(f"Error al actualizar los parámetros de la regla: {e}")
            return False