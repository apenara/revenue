#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define el modelo para las habitaciones
"""

from models.base_model import BaseModel
from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class Room(BaseModel):
    """
    Modelo para las habitaciones (ROOM_TYPES)
    """
    
    def __init__(self, id=None, cod_hab=None, name=None, capacity=None, 
                 description=None, amenities=None, num_config=None):
        """
        Inicializa una instancia de Room.
        
        Args:
            id (int, optional): ID de la habitación
            cod_hab (str): Código de la habitación
            name (str): Nombre del tipo de habitación
            capacity (int): Capacidad de la habitación
            description (str, optional): Descripción de la habitación
            amenities (str, optional): Comodidades de la habitación
            num_config (int): Número de habitaciones de este tipo
        """
        self.id = id
        self.cod_hab = cod_hab
        self.name = name
        self.capacity = capacity
        self.description = description
        self.amenities = amenities
        self.num_config = num_config
    
    @classmethod
    def from_row(cls, row):
        """
        Crea una instancia de Room a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            Room: Instancia de Room
        """
        if not row:
            return None
        
        return cls(
            id=row['id'],
            cod_hab=row['cod_hab'],
            name=row['name'],
            capacity=row['capacity'],
            description=row['description'],
            amenities=row['amenities'],
            num_config=row['num_config']
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Room a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos de la habitación
            
        Returns:
            Room: Instancia de Room
        """
        return cls(
            id=data.get('id'),
            cod_hab=data.get('cod_hab'),
            name=data.get('name'),
            capacity=data.get('capacity'),
            description=data.get('description'),
            amenities=data.get('amenities'),
            num_config=data.get('num_config')
        )
    
    def to_dict(self):
        """
        Convierte la instancia de Room a un diccionario.
        
        Returns:
            dict: Diccionario con los datos de la habitación
        """
        return {
            'id': self.id,
            'cod_hab': self.cod_hab,
            'name': self.name,
            'capacity': self.capacity,
            'description': self.description,
            'amenities': self.amenities,
            'num_config': self.num_config
        }
    
    def save(self):
        """
        Guarda la habitación en la base de datos.
        Si la habitación ya existe (tiene id), la actualiza.
        Si no existe, la crea.
        
        Returns:
            int: ID de la habitación guardada
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.id:
                    # Actualizar habitación existente
                    cursor.execute('''
                    UPDATE ROOM_TYPES
                    SET cod_hab = ?, name = ?, capacity = ?, description = ?, amenities = ?, num_config = ?
                    WHERE id = ?
                    ''', (self.cod_hab, self.name, self.capacity, self.description, 
                          self.amenities, self.num_config, self.id))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No se encontró la habitación con ID {self.id} para actualizar")
                else:
                    # Crear nueva habitación
                    cursor.execute('''
                    INSERT INTO ROOM_TYPES (cod_hab, name, capacity, description, amenities, num_config)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (self.cod_hab, self.name, self.capacity, self.description, 
                          self.amenities, self.num_config))
                    
                    self.id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Habitación guardada con ID {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"Error al guardar la habitación: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene una habitación por su ID.
        
        Args:
            id (int): ID de la habitación a obtener
            
        Returns:
            Room: Instancia de Room o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ROOM_TYPES WHERE id = ?', (id,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la habitación con ID {id}: {e}")
            return None
    
    @classmethod
    def get_by_cod_hab(cls, cod_hab):
        """
        Obtiene una habitación por su código.
        
        Args:
            cod_hab (str): Código de la habitación a obtener
            
        Returns:
            Room: Instancia de Room o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ROOM_TYPES WHERE cod_hab = ?', (cod_hab,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la habitación con código {cod_hab}: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todas las habitaciones.
        
        Returns:
            list: Lista de instancias de Room
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ROOM_TYPES ORDER BY id')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener todas las habitaciones: {e}")
            return []
    
    @classmethod
    def delete(cls, id):
        """
        Elimina una habitación por su ID.
        
        Args:
            id (int): ID de la habitación a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM ROOM_TYPES WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar la habitación con ID {id}: {e}")
            return False
    
    @classmethod
    def get_total_rooms(cls):
        """
        Obtiene el número total de habitaciones disponibles.
        
        Returns:
            int: Número total de habitaciones
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(num_config) as total FROM ROOM_TYPES')
                row = cursor.fetchone()
                return row['total'] if row and row['total'] is not None else 0
        except Exception as e:
            logger.error(f"Error al obtener el número total de habitaciones: {e}")
            return 0