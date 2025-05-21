#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que define el modelo para el resumen diario histórico
"""

from datetime import datetime
from models.base_model import BaseModel
from db.database import db
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger(__name__)

class HistoricalSummary(BaseModel):
    """
    Modelo para el resumen diario histórico (HISTORICAL_SUMMARY)
    """
    
    def __init__(self, id=None, fecha=None, habitaciones_disponibles=None, 
                 habitaciones_ocupadas=None, ingresos_totales=None, adr=None, 
                 revpar=None, ocupacion_porcentaje=None, created_at=None):
        """
        Inicializa una instancia de HistoricalSummary.
        
        Args:
            id (int, optional): ID del resumen
            fecha (str/datetime): Fecha del resumen
            habitaciones_disponibles (int): Número de habitaciones disponibles
            habitaciones_ocupadas (int): Número de habitaciones ocupadas
            ingresos_totales (float): Ingresos totales
            adr (float, optional): Average Daily Rate
            revpar (float, optional): Revenue Per Available Room
            ocupacion_porcentaje (float, optional): Porcentaje de ocupación
            created_at (str/datetime, optional): Fecha de creación del registro
        """
        self.id = id
        self.fecha = self._parse_date(fecha)
        self.habitaciones_disponibles = habitaciones_disponibles
        self.habitaciones_ocupadas = habitaciones_ocupadas
        self.ingresos_totales = ingresos_totales
        self.adr = adr if adr is not None else self._calculate_adr()
        self.revpar = revpar if revpar is not None else self._calculate_revpar()
        self.ocupacion_porcentaje = ocupacion_porcentaje if ocupacion_porcentaje is not None else self._calculate_ocupacion()
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
    
    def _calculate_adr(self):
        """
        Calcula el ADR (Average Daily Rate).
        
        Returns:
            float: ADR calculado o None si no se puede calcular
        """
        if self.habitaciones_ocupadas and self.habitaciones_ocupadas > 0 and self.ingresos_totales is not None:
            return round(self.ingresos_totales / self.habitaciones_ocupadas, 2)
        return None
    
    def _calculate_revpar(self):
        """
        Calcula el RevPAR (Revenue Per Available Room).
        
        Returns:
            float: RevPAR calculado o None si no se puede calcular
        """
        if self.habitaciones_disponibles and self.habitaciones_disponibles > 0 and self.ingresos_totales is not None:
            return round(self.ingresos_totales / self.habitaciones_disponibles, 2)
        return None
    
    def _calculate_ocupacion(self):
        """
        Calcula el porcentaje de ocupación.
        
        Returns:
            float: Porcentaje de ocupación calculado o None si no se puede calcular
        """
        if self.habitaciones_disponibles and self.habitaciones_disponibles > 0 and self.habitaciones_ocupadas is not None:
            return round((self.habitaciones_ocupadas / self.habitaciones_disponibles) * 100, 2)
        return None
    
    @classmethod
    def from_row(cls, row):
        """
        Crea una instancia de HistoricalSummary a partir de una fila de la base de datos.
        
        Args:
            row (sqlite3.Row): Fila de la base de datos
            
        Returns:
            HistoricalSummary: Instancia de HistoricalSummary
        """
        if not row:
            return None
        
        return cls(
            id=row['id'],
            fecha=row['fecha'],
            habitaciones_disponibles=row['habitaciones_disponibles'],
            habitaciones_ocupadas=row['habitaciones_ocupadas'],
            ingresos_totales=row['ingresos_totales'],
            adr=row['adr'],
            revpar=row['revpar'],
            ocupacion_porcentaje=row['ocupacion_porcentaje'],
            created_at=row['created_at']
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de HistoricalSummary a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del resumen
            
        Returns:
            HistoricalSummary: Instancia de HistoricalSummary
        """
        return cls(
            id=data.get('id'),
            fecha=data.get('fecha'),
            habitaciones_disponibles=data.get('habitaciones_disponibles'),
            habitaciones_ocupadas=data.get('habitaciones_ocupadas'),
            ingresos_totales=data.get('ingresos_totales'),
            adr=data.get('adr'),
            revpar=data.get('revpar'),
            ocupacion_porcentaje=data.get('ocupacion_porcentaje'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """
        Convierte la instancia de HistoricalSummary a un diccionario.
        
        Returns:
            dict: Diccionario con los datos del resumen
        """
        return {
            'id': self.id,
            'fecha': self._format_date(self.fecha),
            'habitaciones_disponibles': self.habitaciones_disponibles,
            'habitaciones_ocupadas': self.habitaciones_ocupadas,
            'ingresos_totales': self.ingresos_totales,
            'adr': self.adr,
            'revpar': self.revpar,
            'ocupacion_porcentaje': self.ocupacion_porcentaje,
            'created_at': self._format_date(self.created_at)
        }
    
    def save(self):
        """
        Guarda el resumen en la base de datos.
        Si el resumen ya existe (tiene id), lo actualiza.
        Si no existe, lo crea.
        
        Returns:
            int: ID del resumen guardado
        """
        try:
            # Asegurarse de que los KPIs estén calculados
            if self.adr is None:
                self.adr = self._calculate_adr()
            if self.revpar is None:
                self.revpar = self._calculate_revpar()
            if self.ocupacion_porcentaje is None:
                self.ocupacion_porcentaje = self._calculate_ocupacion()
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.id:
                    # Actualizar resumen existente
                    cursor.execute('''
                    UPDATE HISTORICAL_SUMMARY
                    SET fecha = ?, habitaciones_disponibles = ?, habitaciones_ocupadas = ?,
                        ingresos_totales = ?, adr = ?, revpar = ?, ocupacion_porcentaje = ?
                    WHERE id = ?
                    ''', (
                        self._format_date(self.fecha), self.habitaciones_disponibles,
                        self.habitaciones_ocupadas, self.ingresos_totales,
                        self.adr, self.revpar, self.ocupacion_porcentaje,
                        self.id
                    ))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"No se encontró el resumen con ID {self.id} para actualizar")
                else:
                    # Crear nuevo resumen
                    cursor.execute('''
                    INSERT INTO HISTORICAL_SUMMARY (
                        fecha, habitaciones_disponibles, habitaciones_ocupadas,
                        ingresos_totales, adr, revpar, ocupacion_porcentaje
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self._format_date(self.fecha), self.habitaciones_disponibles,
                        self.habitaciones_ocupadas, self.ingresos_totales,
                        self.adr, self.revpar, self.ocupacion_porcentaje
                    ))
                    
                    self.id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Resumen guardado con ID {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"Error al guardar el resumen: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene un resumen por su ID.
        
        Args:
            id (int): ID del resumen a obtener
            
        Returns:
            HistoricalSummary: Instancia de HistoricalSummary o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM HISTORICAL_SUMMARY WHERE id = ?', (id,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener el resumen con ID {id}: {e}")
            return None
    
    @classmethod
    def get_by_date(cls, fecha):
        """
        Obtiene un resumen por su fecha.
        
        Args:
            fecha (str/datetime): Fecha del resumen a obtener
            
        Returns:
            HistoricalSummary: Instancia de HistoricalSummary o None si no existe
        """
        try:
            # Convertir fecha a string si es datetime
            if isinstance(fecha, datetime):
                fecha = fecha.strftime('%Y-%m-%d')
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM HISTORICAL_SUMMARY WHERE fecha = ?', (fecha,))
                row = cursor.fetchone()
                return cls.from_row(row)
        except Exception as e:
            logger.error(f"Error al obtener el resumen con fecha {fecha}: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todos los resúmenes.
        
        Returns:
            list: Lista de instancias de HistoricalSummary
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM HISTORICAL_SUMMARY ORDER BY fecha DESC')
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener todos los resúmenes: {e}")
            return []
    
    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """
        Obtiene los resúmenes en un rango de fechas.
        
        Args:
            start_date (str/datetime): Fecha de inicio
            end_date (str/datetime): Fecha de fin
            
        Returns:
            list: Lista de instancias de HistoricalSummary
        """
        try:
            # Convertir fechas a string si son datetime
            if isinstance(start_date, datetime):
                start_date = start_date.strftime('%Y-%m-%d')
            if isinstance(end_date, datetime):
                end_date = end_date.strftime('%Y-%m-%d')
                
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM HISTORICAL_SUMMARY 
                WHERE fecha BETWEEN ? AND ?
                ORDER BY fecha
                ''', (start_date, end_date))
                rows = cursor.fetchall()
                return [cls.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error al obtener resúmenes por rango de fechas: {e}")
            return []
    
    @classmethod
    def delete(cls, id):
        """
        Elimina un resumen por su ID.
        
        Args:
            id (int): ID del resumen a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM HISTORICAL_SUMMARY WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar el resumen con ID {id}: {e}")
            return False
    
    @classmethod
    def bulk_insert(cls, summaries):
        """
        Inserta múltiples resúmenes en la base de datos.
        
        Args:
            summaries (list): Lista de instancias de HistoricalSummary
            
        Returns:
            int: Número de resúmenes insertados
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                values = []
                for summary in summaries:
                    # Asegurarse de que los KPIs estén calculados
                    if summary.adr is None:
                        summary.adr = summary._calculate_adr()
                    if summary.revpar is None:
                        summary.revpar = summary._calculate_revpar()
                    if summary.ocupacion_porcentaje is None:
                        summary.ocupacion_porcentaje = summary._calculate_ocupacion()
                        
                    values.append((
                        summary._format_date(summary.fecha), summary.habitaciones_disponibles,
                        summary.habitaciones_ocupadas, summary.ingresos_totales,
                        summary.adr, summary.revpar, summary.ocupacion_porcentaje
                    ))
                
                cursor.executemany('''
                INSERT INTO HISTORICAL_SUMMARY (
                    fecha, habitaciones_disponibles, habitaciones_ocupadas,
                    ingresos_totales, adr, revpar, ocupacion_porcentaje
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', values)
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error al insertar múltiples resúmenes: {e}")
            raise