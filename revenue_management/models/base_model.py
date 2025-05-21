#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define la clase base para todos los modelos de datos
"""

from abc import ABC, abstractmethod
from db.database import db

class BaseModel(ABC):
    """
    Clase base abstracta para todos los modelos de datos.
    Define la interfaz común que deben implementar todos los modelos.
    """
    
    @classmethod
    @abstractmethod
    def from_row(cls, row):
        """
        Crea una instancia del modelo a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            BaseModel: Instancia del modelo
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """
        Crea una instancia del modelo a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del modelo
            
        Returns:
            BaseModel: Instancia del modelo
        """
        pass
    
    @abstractmethod
    def to_dict(self):
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            dict: Diccionario con los datos del modelo
        """
        pass
    
    @abstractmethod
    def save(self):
        """
        Guarda el modelo en la base de datos.
        Si el modelo ya existe (tiene id), lo actualiza.
        Si no existe, lo crea.
        
        Returns:
            int: ID del modelo guardado
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_by_id(cls, id):
        """
        Obtiene un modelo por su ID.
        
        Args:
            id (int): ID del modelo a obtener
            
        Returns:
            BaseModel: Instancia del modelo o None si no existe
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_all(cls):
        """
        Obtiene todos los modelos.
        
        Returns:
            list: Lista de instancias del modelo
        """
        pass
    
    @classmethod
    @abstractmethod
    def delete(cls, id):
        """
        Elimina un modelo por su ID.
        
        Args:
            id (int): ID del modelo a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        pass