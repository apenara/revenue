#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de configuración global para el Framework de Revenue Management
"""

import os
import yaml
import json
from pathlib import Path
from datetime import datetime

class Config:
    """
    Clase singleton para gestionar la configuración global de la aplicación
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Carga la configuración desde el archivo config.yaml"""
        config_path = Path(__file__).parent / "config.yaml"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            
            # Crear directorios necesarios
            self.get_path("directories.data_raw", create=True)
            self.get_path("directories.data_processed", create=True)
            self.get_path("directories.data_exports", create=True)
            self.get_path("directories.templates", create=True)
            self.get_path("database.backup_dir", create=True)
            
            # Crear directorio de logs
            log_path = self.get_path("logging.file", create=False)
            if log_path:
                log_dir = log_path.parent
                if not log_dir.exists():
                    log_dir.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            print(f"Error al cargar la configuración: {e}")
            self.config = {}
    
    def get(self, key, default=None):
        """
        Obtiene un valor de configuración por clave.
        
        Args:
            key (str): Clave de configuración en formato 'seccion.subseccion.valor'
            default: Valor por defecto si la clave no existe
            
        Returns:
            El valor de configuración o el valor por defecto
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key, value):
        """
        Establece un valor de configuración por clave.
        
        Args:
            key (str): Clave de configuración en formato 'seccion.subseccion.valor'
            value: Valor a establecer
            
        Returns:
            bool: True si se estableció correctamente, False en caso contrario
        """
        keys = key.split('.')
        config = self.config
        
        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                return False
            config = config[k]
        
        # Establecer el valor en el último nivel
        config[keys[-1]] = value
        return True
    
    def save(self):
        """
        Guarda la configuración en el archivo config.yaml
        
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        config_path = Path(__file__).parent / "config.yaml"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")
            return False
    
    def get_path(self, key, create=False):
        """
        Obtiene una ruta de directorio desde la configuración y opcionalmente la crea.
        
        Args:
            key (str): Clave de configuración que contiene la ruta
            create (bool): Si es True, crea el directorio si no existe
            
        Returns:
            Path: Objeto Path con la ruta absoluta
        """
        path_str = self.get(key)
        if not path_str:
            return None
            
        # Convertir a ruta absoluta
        base_dir = Path(__file__).parent
        path = base_dir / path_str
        
        # Crear directorio si no existe y se solicita
        if create and not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            
        return path
    
    def get_room_types(self):
        """
        Obtiene la lista de tipos de habitación.
        
        Returns:
            list: Lista de diccionarios con los tipos de habitación
        """
        return self.get("room_types", [])
    
    def get_channels(self):
        """
        Obtiene la lista de canales de distribución.
        
        Returns:
            list: Lista de diccionarios con los canales de distribución
        """
        return self.get("channels", [])
    
    def get_seasons(self):
        """
        Obtiene la lista de temporadas.
        
        Returns:
            list: Lista de diccionarios con las temporadas
        """
        return self.get("seasons", [])
    
    def get_pricing_rules(self):
        """
        Obtiene las reglas de pricing.
        
        Returns:
            dict: Diccionario con las reglas de pricing
        """
        return self.get("pricing", {})
    
    def get_forecasting_config(self):
        """
        Obtiene la configuración de forecasting.
        
        Returns:
            dict: Diccionario con la configuración de forecasting
        """
        return self.get("forecasting", {})
    
    def get_hotel_info(self):
        """
        Obtiene la información del hotel.
        
        Returns:
            dict: Diccionario con la información del hotel
        """
        return {
            "name": self.get("app.hotel_name", "Hotel Playa Club"),
            "location": self.get("app.hotel_location", "Cartagena, Colombia"),
            "total_rooms": self.get("app.total_rooms", 79)
        }
    
    def get_excel_config(self):
        """
        Obtiene la configuración de Excel.
        
        Returns:
            dict: Diccionario con la configuración de Excel
        """
        return self.get("excel", {})

# Instancia global de configuración
config = Config()