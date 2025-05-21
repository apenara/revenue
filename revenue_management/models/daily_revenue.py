#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define el modelo para los ingresos diarios
"""

from datetime import datetime
from models.base_model import BaseModel
from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class DailyRevenue(BaseModel):
    """
    Modelo para los ingresos diarios (DAILY_REVENUE)
    """
    
    def __init__(self, id=None, fecha=None, room_type_id=None, ingresos=None, 
                 adr=None, revpar=None, created_at=None):
        """
        Inicializa una instancia de DailyRevenue.
        
        Args:
            id (int, optional): ID del registro
            fecha (str/datetime): Fecha del registro
            room_type_id (int): ID del tipo de habitación
            ingresos (float): Ingresos totales
            adr (float, optional): Average Daily Rate
            revpar (float, optional): Revenue Per Available Room
            created_at (str/datetime, optional): Fecha de creación del registro
        """
        self.id = id
        self.fecha = self._parse_date(fecha)
        self.room_type_id = room_type_id
        self.ingresos = ingresos
        self.adr = adr
        self.revpar = revpar
        self.created_at = self._parse_date(created_at) if created_at else datetime.now()
    
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
        Crea una instancia de DailyRevenue a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            DailyRevenue: Instancia de DailyRevenue
        """
        if not row:
            return None
        
        return cls(
            id=row['id'],
            fecha=row['fecha'],
            room_type_id=row['room_type_id'],
            ingresos=row['ingresos'],
            adr=row['adr'],
            revpar=row['revpar'],
            created_at=row['created_at']
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de DailyRevenue a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del registro
            
        Returns:
            DailyRevenue: Instancia de DailyRevenue
        """
        return cls(
            id=data.get('id'),
            fecha=data.get('fecha'),
            room_type_id=data.get('room_type_id'),
            ingresos=data.get('ingresos'),
            adr=data.get('adr'),
            revpar=data.get('revpar'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """
        Convierte la instancia de DailyRevenue a un diccionario.
        
        Returns:
            dict: Diccionario con los datos del registro
        """
        return {
            'id': self.id,
            'fecha': self._format_date(self.fecha),
            'room_type_id': self.room_type_id,
            'ingresos': self.ingresos,
            'adr': self.adr,
            'revpar': self.revpar,
            'created_at': self._format_date(self.created_at)
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
                    UPDATE DAILY_REVENUE
                    SET fecha = ?, room_type_id = ?, ingresos = ?, adr = ?, revpar = ?
                    WHERE id = ?
                    ''', (
                        self._format_date(self.fecha), self.room_type_id,
                        self.ingresos, self.adr, self.revpar, self.id
                    ))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No se encontró el registro con ID {self.id} para actualizar")
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                    INSERT INTO DAILY_REVENUE (
                        fecha, room_type_id, ingresos, adr, revpar
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        self._format_date(self.fecha), self.room_type_id,
                        self.ingresos, self.adr, self.revpar
                    ))
                    
                    self.id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Registro de ingresos diarios guardado con ID {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"Error al guardar el registro de ingresos diarios: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene un registro por su ID.
        
        Args:
            id (int): ID del registro a obtener
            
        Returns:
            DailyRevenue: Instancia de DailyRevenue o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM DAILY_REVENUE WHERE id = ?', (id,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener el registro de ingresos diarios con ID {id}: {e}")
            return None
    
    @classmethod
    def get_by_date_and_room_type(cls, fecha, room_type_id):
        """
        Obtiene un registro por su fecha y tipo de habitación.
        
        Args:
            fecha (str/datetime): Fecha del registro
            room_type_id (int): ID del tipo de habitación
            
        Returns:
            DailyRevenue: Instancia de DailyRevenue o None si no existe
        """
        try:
            # Convertir fecha a string si es datetime
            if isinstance(fecha, datetime):
                fecha = fecha.strftime('%Y-%m-%d')
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM DAILY_REVENUE 
                WHERE fecha = ? AND room_type_id = ?
                ''', (fecha, room_type_id))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener el registro de ingresos diarios con fecha {fecha} y tipo de habitación {room_type_id}: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todos los registros.
        
        Returns:
            list: Lista de instancias de DailyRevenue
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM DAILY_REVENUE ORDER BY fecha DESC, room_type_id')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener todos los registros de ingresos diarios: {e}")
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
            list: Lista de instancias de DailyRevenue
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
                    SELECT * FROM DAILY_REVENUE 
                    WHERE fecha BETWEEN ? AND ? AND room_type_id = ?
                    ORDER BY fecha, room_type_id
                    ''', (start_date, end_date, room_type_id))
                else:
                    cursor.execute('''
                    SELECT * FROM DAILY_REVENUE 
                    WHERE fecha BETWEEN ? AND ?
                    ORDER BY fecha, room_type_id
                    ''', (start_date, end_date))
                
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener registros de ingresos diarios por rango de fechas: {e}")
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
                cursor.execute('DELETE FROM DAILY_REVENUE WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar el registro de ingresos diarios con ID {id}: {e}")
            return False
    
    @classmethod
    def bulk_insert(cls, revenues):
        """
        Inserta múltiples registros en la base de datos.
        
        Args:
            revenues (list): Lista de instancias de DailyRevenue
            
        Returns:
            int: Número de registros insertados
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                values = []
                for revenue in revenues:
                    values.append((
                        revenue._format_date(revenue.fecha), revenue.room_type_id,
                        revenue.ingresos, revenue.adr, revenue.revpar
                    ))
                
                cursor.executemany('''
                INSERT INTO DAILY_REVENUE (
                    fecha, room_type_id, ingresos, adr, revpar
                )
                VALUES (?, ?, ?, ?, ?)
                ''', values)
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error al insertar múltiples registros de ingresos diarios: {e}")
            raise
    
    @classmethod
    def calculate_kpis(cls, fecha, room_type_id, habitaciones_disponibles, habitaciones_ocupadas, ingresos):
        """
        Calcula los KPIs (ADR y RevPAR) para un día y tipo de habitación específicos.
        
        Args:
            fecha (str/datetime): Fecha del registro
            room_type_id (int): ID del tipo de habitación
            habitaciones_disponibles (int): Número de habitaciones disponibles
            habitaciones_ocupadas (int): Número de habitaciones ocupadas
            ingresos (float): Ingresos totales
            
        Returns:
            DailyRevenue: Instancia de DailyRevenue con los KPIs calculados
        """
        try:
            # Calcular ADR (Average Daily Rate)
            adr = None
            if habitaciones_ocupadas and habitaciones_ocupadas > 0:
                adr = round(ingresos / habitaciones_ocupadas, 2)
            
            # Calcular RevPAR (Revenue Per Available Room)
            revpar = None
            if habitaciones_disponibles and habitaciones_disponibles > 0:
                revpar = round(ingresos / habitaciones_disponibles, 2)
            
            return cls(
                fecha=fecha,
                room_type_id=room_type_id,
                ingresos=ingresos,
                adr=adr,
                revpar=revpar
            )
        except Exception as e:
            logger.error(f"Error al calcular KPIs: {e}")
            return None