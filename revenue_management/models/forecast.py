#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define el modelo para las previsiones
"""

from datetime import datetime
from models.base_model import BaseModel
from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class Forecast(BaseModel):
    """
    Modelo para las previsiones (FORECASTS)
    """
    
    def __init__(self, id=None, fecha=None, room_type_id=None, ocupacion_prevista=None, 
                 adr_previsto=None, revpar_previsto=None, created_at=None, ajustado_manualmente=False):
        """
        Inicializa una instancia de Forecast.
        
        Args:
            id (int, optional): ID del registro
            fecha (str/datetime): Fecha de la previsión
            room_type_id (int): ID del tipo de habitación
            ocupacion_prevista (float): Ocupación prevista (porcentaje)
            adr_previsto (float): ADR previsto
            revpar_previsto (float): RevPAR previsto
            created_at (str/datetime, optional): Fecha de creación del registro
            ajustado_manualmente (bool, optional): Indica si la previsión fue ajustada manualmente
        """
        self.id = id
        self.fecha = self._parse_date(fecha)
        self.room_type_id = room_type_id
        self.ocupacion_prevista = ocupacion_prevista
        self.adr_previsto = adr_previsto
        self.revpar_previsto = revpar_previsto
        self.created_at = self._parse_date(created_at) if created_at else datetime.now()
        self.ajustado_manualmente = ajustado_manualmente
    
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
    
    @classmethod
    def from_row(cls, row):
        """
        Crea una instancia de Forecast a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            Forecast: Instancia de Forecast
        """
        if not row:
            return None
        
        return cls(
            id=row['id'],
            fecha=row['fecha'],
            room_type_id=row['room_type_id'],
            ocupacion_prevista=row['ocupacion_prevista'],
            adr_previsto=row['adr_previsto'],
            revpar_previsto=row['revpar_previsto'],
            created_at=row['created_at'],
            ajustado_manualmente=bool(row['ajustado_manualmente'])
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Forecast a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del registro
            
        Returns:
            Forecast: Instancia de Forecast
        """
        return cls(
            id=data.get('id'),
            fecha=data.get('fecha'),
            room_type_id=data.get('room_type_id'),
            ocupacion_prevista=data.get('ocupacion_prevista'),
            adr_previsto=data.get('adr_previsto'),
            revpar_previsto=data.get('revpar_previsto'),
            created_at=data.get('created_at'),
            ajustado_manualmente=data.get('ajustado_manualmente', False)
        )
    
    def to_dict(self):
        """
        Convierte la instancia de Forecast a un diccionario.
        
        Returns:
            dict: Diccionario con los datos del registro
        """
        return {
            'id': self.id,
            'fecha': self._format_date(self.fecha),
            'room_type_id': self.room_type_id,
            'ocupacion_prevista': self.ocupacion_prevista,
            'adr_previsto': self.adr_previsto,
            'revpar_previsto': self.revpar_previsto,
            'created_at': self._format_date(self.created_at),
            'ajustado_manualmente': self.ajustado_manualmente
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
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.id:
                    # Actualizar registro existente
                    cursor.execute('''
                    UPDATE FORECASTS
                    SET fecha = ?, room_type_id = ?, ocupacion_prevista = ?,
                        adr_previsto = ?, revpar_previsto = ?, ajustado_manualmente = ?
                    WHERE id = ?
                    ''', (
                        self._format_date(self.fecha), self.room_type_id,
                        self.ocupacion_prevista, self.adr_previsto,
                        self.revpar_previsto, int(self.ajustado_manualmente),
                        self.id
                    ))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No se encontró el registro con ID {self.id} para actualizar")
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                    INSERT INTO FORECASTS (
                        fecha, room_type_id, ocupacion_prevista,
                        adr_previsto, revpar_previsto, ajustado_manualmente
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        self._format_date(self.fecha), self.room_type_id,
                        self.ocupacion_prevista, self.adr_previsto,
                        self.revpar_previsto, int(self.ajustado_manualmente)
                    ))
                    
                    self.id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Previsión guardada con ID {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"Error al guardar la previsión: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene un registro por su ID.
        
        Args:
            id (int): ID del registro a obtener
            
        Returns:
            Forecast: Instancia de Forecast o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM FORECASTS WHERE id = ?', (id,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la previsión con ID {id}: {e}")
            return None
    
    @classmethod
    def get_by_date_and_room_type(cls, fecha, room_type_id):
        """
        Obtiene un registro por su fecha y tipo de habitación.
        
        Args:
            fecha (str/datetime): Fecha del registro
            room_type_id (int): ID del tipo de habitación
            
        Returns:
            Forecast: Instancia de Forecast o None si no existe
        """
        try:
            # Convertir fecha a string si es datetime
            if isinstance(fecha, datetime):
                fecha = fecha.strftime('%Y-%m-%d')
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM FORECASTS 
                WHERE fecha = ? AND room_type_id = ?
                ''', (fecha, room_type_id))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener la previsión con fecha {fecha} y tipo de habitación {room_type_id}: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todos los registros.
        
        Returns:
            list: Lista de instancias de Forecast
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM FORECASTS ORDER BY fecha, room_type_id')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener todas las previsiones: {e}")
            return []
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date, room_type_id=None):
        """
        Obtiene los registros en un rango de fechas, opcionalmente filtrados por tipo de habitación.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            list: Lista de instancias de Forecast
        """
        try:
            # Convertir fechas a string si son datetime
            if isinstance(start_date, datetime):
                start_date = start_date.strftime('%Y-%m-%d')
            if isinstance(end_date, datetime):
                end_date = end_date.strftime('%Y-%m-%d')
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if room_type_id is not None:
                    cursor.execute('''
                    SELECT * FROM FORECASTS 
                    WHERE fecha BETWEEN ? AND ? AND room_type_id = ?
                    ORDER BY fecha, room_type_id
                    ''', (start_date, end_date, room_type_id))
                else:
                    cursor.execute('''
                    SELECT * FROM FORECASTS 
                    WHERE fecha BETWEEN ? AND ?
                    ORDER BY fecha, room_type_id
                    ''', (start_date, end_date))
                
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener previsiones por rango de fechas: {e}")
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
                cursor.execute('DELETE FROM FORECASTS WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar la previsión con ID {id}: {e}")
            return False
    
    @classmethod
    def bulk_insert(cls, forecasts):
        """
        Inserta múltiples registros en la base de datos.
        
        Args:
            forecasts (list): Lista de instancias de Forecast
            
        Returns:
            int: Número de registros insertados
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                values = []
                for forecast in forecasts:
                    values.append((
                        forecast._format_date(forecast.fecha), forecast.room_type_id,
                        forecast.ocupacion_prevista, forecast.adr_previsto,
                        forecast.revpar_previsto, int(forecast.ajustado_manualmente)
                    ))
                
                cursor.executemany('''
                INSERT INTO FORECASTS (
                    fecha, room_type_id, ocupacion_prevista,
                    adr_previsto, revpar_previsto, ajustado_manualmente
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ''', values)
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error al insertar múltiples previsiones: {e}")
            raise
    
    @classmethod
    def get_latest_forecasts(cls, limit=30, room_type_id=None):
        """
        Obtiene las previsiones más recientes, opcionalmente filtradas por tipo de habitación.
        
        Args:
            limit (int, optional): Número máximo de registros a obtener
            room_type_id (int, optional): ID del tipo de habitación
            
        Returns:
            list: Lista de instancias de Forecast
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if room_type_id is not None:
                    cursor.execute('''
                    SELECT * FROM FORECASTS 
                    WHERE room_type_id = ? AND fecha >= date('now')
                    ORDER BY fecha
                    LIMIT ?
                    ''', (room_type_id, limit))
                else:
                    cursor.execute('''
                    SELECT * FROM FORECASTS 
                    WHERE fecha >= date('now')
                    ORDER BY fecha, room_type_id
                    LIMIT ?
                    ''', (limit,))
                
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener las previsiones más recientes: {e}")
            return []